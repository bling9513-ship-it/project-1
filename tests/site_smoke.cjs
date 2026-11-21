const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const path = require('node:path');
const { chromium } = require('playwright');

const pages = ['index', 'study', 'ai', 'cve', 'wargame', 'tools', 'radar', 'outfit', 'pick', 'clue', 'mission'];
const root = path.join(__dirname, '..');

async function assertCveJump(page, cid, label) {
  await page.waitForFunction((id) => {
    const el = document.getElementById('cve-' + id);
    return !!el && document.activeElement === el;
  }, cid, { timeout: 5000 });
  await page.waitForFunction((id) => {
    const el = document.getElementById('cve-' + id);
    const r = el.getBoundingClientRect();
    return r.top >= 0 && r.top < 220;
  }, cid, { timeout: 5000 });
  const state = await page.evaluate((id) => {
    const el = document.getElementById('cve-' + id);
    const active = document.querySelector('.segment-btn.active');
    return {
      activeId: document.activeElement ? document.activeElement.id : null,
      focused: el.classList.contains('is-focused'),
      term: document.getElementById('searchInput').value,
      visible: document.getElementById('visibleCount').textContent,
      cards: document.querySelectorAll('#cveList .cve-card').length,
      activeFilter: active && active.dataset ? (active.dataset.filter || null) : null,
      hash: location.hash,
    };
  }, cid);
  assert.equal(state.activeId, 'cve-' + cid, `${label}: activeElement`);
  assert.equal(state.focused, true, `${label}: focus highlight missing`);
  assert.equal(state.term, '', `${label}: search term not cleared`);
  assert.equal(state.activeFilter, 'all', `${label}: filter not reset`);
  assert.equal(state.hash, '#cve-' + encodeURIComponent(cid), `${label}: url hash not updated`);
  assert.ok(parseInt(state.visible, 10) === state.cards && state.cards > 1, `${label}: list not restored`);
}

// '이번 주 우선 조치' 행 → CVE 카드 이동 (검색·필터로 카드를 숨긴 상태에서도 동작해야 한다)
async function checkCvePriorityNav(page, width) {
  await page.locator('.priority-list a.priority-row[data-cve]').first().waitFor({ state: 'attached' });
  const target = await page.evaluate(() => {
    const row = document.querySelector('.priority-list a.priority-row[data-cve]');
    return row ? { cid: row.getAttribute('data-cve'), href: row.getAttribute('href') } : null;
  });
  assert.ok(target, 'priority row not found');
  assert.equal(target.href, '#cve-' + target.cid, 'priority row must link to its card');

  // 1) 검색어로 대상 카드를 숨긴 뒤 키보드 Tab + Enter
  await page.fill('#searchInput', 'java4shell');
  if (await page.locator('#cve-' + target.cid).count() > 0) {
    await page.fill('#searchInput', 'zzzz-no-such-cve');
  }
  await page.waitForFunction((id) => !document.getElementById('cve-' + id), target.cid, { timeout: 5000 });
  assert.equal(await page.locator('#cve-' + target.cid).count(), 0, 'target card not hidden by search');
  await page.evaluate(() => { if (document.activeElement) document.activeElement.blur(); });
  let reached = false;
  for (let i = 0; i < 80; i += 1) {
    reached = await page.evaluate(() => !!document.activeElement
      && document.activeElement.classList.contains('priority-row'));
    if (reached) break;
    await page.keyboard.press('Tab');
  }
  assert.ok(reached, 'could not reach the priority row with Tab');
  assert.equal(await page.evaluate(() => document.activeElement.getAttribute('data-cve')),
    target.cid, 'Tab focus landed on another row');
  await page.keyboard.press('Enter');
  await assertCveJump(page, target.cid, `cve ${width}px keyboard jump`);

  // 2) 필터로 대상 카드를 숨긴 뒤 마우스 클릭
  let filtered = null;
  const rows = await page.evaluate(() => {
    const items = (typeof CVE_ITEMS !== 'undefined' && Array.isArray(CVE_ITEMS)) ? CVE_ITEMS : [];
    return Array.from(document.querySelectorAll('.priority-list a.priority-row[data-cve]'))
      .slice(0, 8)
      .map((row) => {
        const cid = row.getAttribute('data-cve');
        const item = items.find((x) => x.cve_id === cid);
        return { cid, severity: item ? item.severity : null };
      });
  });
  for (const row of rows) {
    const hideFilter = row.severity === 'CRITICAL' ? 'high' : 'critical';
    await page.click(`.segment-btn[data-filter="${hideFilter}"]`);
    if (await page.locator('#cve-' + row.cid).count() === 0) {
      filtered = row;
      break;
    }
    await page.click('.segment-btn[data-filter="all"]');
  }
  assert.ok(filtered, 'could not hide any priority row target with a severity filter');
  await page.click(`.priority-row[data-cve="${filtered.cid}"]`);
  await assertCveJump(page, filtered.cid, `cve ${width}px click jump`);
  console.log(`cve priority nav ${width}px passed`);
}

async function checkPage(context, base, name, width) {
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => {
    const value = message.text();
    if (message.type() === 'error' && !value.startsWith('Failed to load resource:')) {
      errors.push(value);
    }
  });
  page.on('response', response => {
    if (response.url().startsWith(base + '/') && response.status() >= 400
        && !response.url().endsWith('/favicon.ico')) {
      errors.push(`Local resource failed: ${new URL(response.url()).pathname} (${response.status()})`);
    }
  });
  await page.addInitScript(() => {
    window.smokeCspViolations = [];
    window.addEventListener('securitypolicyviolation', event => {
      window.smokeCspViolations.push(event.effectiveDirective);
    });
  });

  try {
    const response = await page.goto(`${base}/${name}.html`, { waitUntil: 'load' });
    assert.equal(response?.status(), 200, 'Page must load');
    const theme = page.locator('#themeToggle');
    await theme.waitFor();
    const initialTheme = await page.locator('html').getAttribute('data-theme');
    await theme.click();
    assert.notEqual(await page.locator('html').getAttribute('data-theme'), initialTheme);

    const cards = { index: '#jobsContainer .job-card, #jobsContainer .list-row', ai: '#aiGrid .ai-card', cve: '#cveList .cve-card' };
    if (cards[name]) await page.locator(cards[name]).first().waitFor({ state: 'attached' });

    if (name === 'cve') await checkCvePriorityNav(page, width);

    const blocked = await page.evaluate(() => ({
      csp: window.smokeCspViolations,
      links: Array.from(document.querySelectorAll('a[href]')).filter(link => {
        const scheme = new URL(link.href, location.href).protocol;
        return !['http:', 'https:', 'mailto:', 'tel:'].includes(scheme)
          || (link.target.toLowerCase() === '_blank'
            && (!link.relList.contains('noopener') || !link.relList.contains('noreferrer')));
      }).length
    }));
    assert.deepEqual(blocked.csp, [], 'CSP violations');
    assert.equal(blocked.links, 0, 'Unsafe links in the rendered DOM');
    assert.deepEqual(errors, [], 'Browser errors');
    console.log(`${name} ${width}px passed`);
  } catch (error) {
    throw new Error(`${name} ${width}px: ${error.message}`, { cause: error });
  } finally {
    await page.close();
  }
}

async function main() {
  const server = spawn('python3', ['-u', '-m', 'http.server', '0', '--bind', '127.0.0.1'], {
    cwd: root, stdio: ['ignore', 'pipe', 'inherit']
  });
  let browser;
  try {
    const port = await new Promise((resolve, reject) => {
      server.once('error', reject);
      server.once('exit', code => reject(new Error(`Static server exited with ${code}`)));
      server.stdout.on('data', data => {
        const match = data.toString().match(/port (\d+)/);
        if (match) resolve(match[1]);
      });
    });
    browser = await chromium.launch({ executablePath: process.env.CHROMIUM_EXECUTABLE });
    for (const width of [390, 1280]) {
      const context = await browser.newContext({ viewport: { width, height: 900 } });
      for (const name of pages) await checkPage(context, `http://127.0.0.1:${port}`, name, width);
      await context.close();
    }
  } finally {
    try {
      await browser?.close();
    } finally {
      server.kill();
    }
  }
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});

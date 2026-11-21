const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const path = require('node:path');
const { chromium } = require('playwright');

const pages = ['today', 'index', 'study', 'ai', 'cve', 'wargame', 'tools', 'radar', 'outfit', 'pick', 'clue', 'mission', 'chart'];
const root = path.join(__dirname, '..');

const SHELL_HREFS = ['today.html', 'index.html', 'study.html', 'ai.html', 'cve.html', 'tools.html', 'radar.html',
  'outfit.html', 'pick.html', 'wargame.html', 'clue.html', 'mission.html', 'chart.html'];

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

// PC는 레일, 모바일은 바텀 시트에서 심각도·악용 신호 필터를 고른다.
async function setCveFilter(page, filter, width) {
  if (width >= 1024) {
    await page.click(`.segment-btn[data-filter="${filter}"]`);
    await page.waitForTimeout(80);
    return;
  }
  await page.click('#cveFilterOpenBtn');
  await page.waitForTimeout(300);
  await page.click(`.segment-btn[data-filter="${filter}"]`);
  await page.waitForTimeout(120);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);
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
    await setCveFilter(page, hideFilter, width);
    if (await page.locator('#cve-' + row.cid).count() === 0) {
      filtered = row;
      break;
    }
    await setCveFilter(page, 'all', width);
  }
  assert.ok(filtered, 'could not hide any priority row target with a severity filter');
  await page.click(`.priority-row[data-cve="${filtered.cid}"]`);
  await assertCveJump(page, filtered.cid, `cve ${width}px click jump`);
  console.log(`cve priority nav ${width}px passed`);
}

// ---- 3단서 추리: 단서 열기 → 정답 → 해결 기록 유지 · 문제 ID 공유 링크 ----
async function checkClueGame(page, base, width) {
  const tag = `clue ${width}px`;
  const readState = () => page.evaluate(() => ({
    id: typeof currentId === 'undefined' ? null : currentId,
    title: document.getElementById('pTitle').textContent.trim(),
    solved: document.getElementById('solvedStat').textContent.trim(),
    total: typeof DATA === 'undefined' ? 0 : DATA.length,
    openClues: document.querySelectorAll('#clueList .clue.open').length,
    dots: document.querySelectorAll('#pDots .dot.on').length,
    nextLabel: document.getElementById('nextClue').textContent.trim(),
    todayHidden: document.getElementById('pToday').hidden,
    share: document.getElementById('sharePreview').textContent,
    resultHidden: document.getElementById('resultBox').hidden,
    badge: document.getElementById('resultBadge').textContent.trim(),
    resultTitle: document.getElementById('resultTitle').textContent.trim(),
    correct: document.querySelectorAll('#options .opt.is-correct').length,
    answer: typeof byId === 'undefined' ? null : byId[currentId].answer,
    answerText: typeof byId === 'undefined' ? null : byId[currentId].choices[byId[currentId].answer],
  }));

  await page.waitForFunction(() => {
    const el = document.getElementById('pTitle');
    return !!el && el.textContent.trim() !== '문제를 불러오는 중입니다';
  }, null, { timeout: 5000 });

  const start = await readState();
  assert.ok(start.id, `${tag}: no puzzle loaded`);
  assert.equal(start.solved, '0 / ' + start.total, `${tag}: fresh solve record expected`);
  assert.equal(start.openClues, 1, `${tag}: only the first clue must be open on load`);
  assert.ok(start.nextLabel.includes('2/3'), `${tag}: next clue label "${start.nextLabel}"`);

  // 다음 단서 열기 → 단서 2 공개
  await page.click('#nextClue');
  await page.waitForFunction(() => document.querySelectorAll('#clueList .clue.open').length === 2,
    null, { timeout: 5000 });
  const twoClues = await readState();
  assert.equal(twoClues.dots, 2, `${tag}: clue dots not updated`);
  assert.ok(twoClues.nextLabel.includes('3/3'), `${tag}: clue button label "${twoClues.nextLabel}"`);

  // 정답 선택 → 결과 카드 · 해결 표시
  await page.click(`#options .opt[data-idx="${start.answer}"]`);
  await page.locator('#resultBox:not([hidden])').waitFor({ timeout: 5000 });
  const won = await readState();
  assert.equal(won.badge, '정답', `${tag}: result badge`);
  assert.ok(won.resultTitle.includes('해결'), `${tag}: result title "${won.resultTitle}"`);
  assert.equal(won.correct, 1, `${tag}: correct option not highlighted`);
  assert.equal(won.solved, '1 / ' + won.total, `${tag}: solved counter "${won.solved}"`);
  assert.ok(won.share.includes('/clue.html?id=' + encodeURIComponent(won.id)),
    `${tag}: share link has no puzzle id`);
  assert.ok(!won.share.includes(won.answerText), `${tag}: share text leaks the answer`);

  // 새로고침해도 localStorage 해결 기록·단서 진행이 유지된다
  await page.reload({ waitUntil: 'load' });
  await page.locator('#resultBox:not([hidden])').waitFor({ timeout: 5000 });
  const restored = await readState();
  assert.equal(restored.id, won.id, `${tag}: reload opened another puzzle`);
  assert.equal(restored.solved, '1 / ' + restored.total, `${tag}: solved record lost on reload`);
  assert.equal(restored.openClues, 2, `${tag}: clue progress lost on reload`);
  assert.equal(restored.badge, '정답', `${tag}: solved result card not restored`);

  const past = await page.evaluate(() => {
    const cards = Array.from(document.querySelectorAll('#arcGrid .arc-card'));
    const card = cards.find((item) => item.dataset.id !== currentId) || cards[0];
    return { id: card.dataset.id, title: card.querySelector('.arc-title').textContent.trim() };
  });
  assert.ok(past.id && past.id !== won.id, `${tag}: no other puzzle to deep link`);

  // #<문제 ID> 해시 링크로 지난 문제를 연다
  await page.goto(`${base}/clue.html#${encodeURIComponent(past.id)}`, { waitUntil: 'load' });
  await page.waitForFunction((id) => typeof currentId !== 'undefined' && currentId === id,
    past.id, { timeout: 5000 });
  let linked = await readState();
  assert.equal(linked.title, past.title, `${tag}: #id did not open the linked puzzle`);
  assert.equal(linked.todayHidden, true, `${tag}: linked past puzzle still tagged as today`);

  // ?id=<문제 ID> 쿼리 링크로도 같은 문제를 연다
  await page.goto(`${base}/clue.html?id=${encodeURIComponent(past.id)}`, { waitUntil: 'load' });
  await page.waitForFunction((id) => typeof currentId !== 'undefined' && currentId === id,
    past.id, { timeout: 5000 });
  linked = await readState();
  assert.equal(linked.title, past.title, `${tag}: ?id did not open the linked puzzle`);

  // 링크로 연 문제를 풀면 복사 문구 URL 도 그 문제 ID 를 가리킨다
  await page.click(`#options .opt[data-idx="${linked.answer}"]`);
  await page.locator('#resultBox:not([hidden])').waitFor({ timeout: 5000 });
  linked = await readState();
  assert.ok(linked.share.includes(`?id=${encodeURIComponent(linked.id)}`),
    `${tag}: copied link missing the linked puzzle id`);
  assert.ok(!linked.share.includes(linked.answerText), `${tag}: linked share leaks the answer`);
  assert.equal(linked.solved, '2 / ' + linked.total, `${tag}: solved counter after linked puzzle`);
  console.log(`clue game ${width}px passed (${won.id} · ${past.id} linked)`);
}

// ---- 퇴근길 미션: 방향키 · 되돌리기 · 최단 경로 클리어 ----
function missionKey(from, to) {
  const dr = to[0] - from[0];
  const dc = to[1] - from[1];
  if (dr === -1 && dc === 0) return 'ArrowUp';
  if (dr === 1 && dc === 0) return 'ArrowDown';
  if (dr === 0 && dc === -1) return 'ArrowLeft';
  if (dr === 0 && dc === 1) return 'ArrowRight';
  throw new Error(`not adjacent cells: ${from} -> ${to}`);
}

// 경유지를 모두 들른 뒤 도착하는 최단 경로(칸 목록)를 지도 데이터만 보고 BFS 로 계산한다.
function missionRoute(puzzle) {
  const { size, rows, start, goal, waypoints } = puzzle;
  const index = new Map(waypoints.map((w, i) => [`${w.r},${w.c}`, i]));
  const full = (1 << waypoints.length) - 1;
  const open = (r, c) => r >= 0 && c >= 0 && r < size && c < size && rows[r][c] !== '#' && rows[r][c] !== 'X';
  const stateKey = (pos, mask) => `${pos[0]},${pos[1]}|${mask}`;
  const seen = new Set([stateKey(start, 0)]);
  const queue = [{ pos: start, mask: 0, prev: null }];
  let found = null;
  while (queue.length && !found) {
    const state = queue.shift();
    if (state.pos[0] === goal[0] && state.pos[1] === goal[1] && state.mask === full) {
      found = state;
      break;
    }
    for (const [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
      const nr = state.pos[0] + dr;
      const nc = state.pos[1] + dc;
      if (!open(nr, nc)) continue;
      const idx = index.get(`${nr},${nc}`);
      const mask = idx === undefined ? state.mask : (state.mask | (1 << idx));
      const key = stateKey([nr, nc], mask);
      if (seen.has(key)) continue;
      seen.add(key);
      queue.push({ pos: [nr, nc], mask, prev: state });
    }
  }
  assert.ok(found, 'mission: puzzle is not solvable');
  const route = [];
  for (let node = found; node; node = node.prev) route.push(node.pos);
  return route.reverse();
}

async function readMissionPuzzle(page) {
  return page.evaluate(() => {
    const cells = Array.from(document.querySelectorAll('#board .cell'));
    const size = Math.round(Math.sqrt(cells.length));
    const rows = [];
    for (let r = 0; r < size; r += 1) {
      let line = '';
      for (let c = 0; c < size; c += 1) {
        const el = cells[r * size + c];
        line += el.classList.contains('road') || el.classList.contains('park') ? '.'
          : el.classList.contains('cons') ? 'X' : '#';
      }
      rows.push(line);
    }
    const waypoints = Array.from(document.querySelectorAll('#board .mk-wp')).map((el) => {
      const cell = el.closest('.cell');
      return { r: Number(cell.dataset.r), c: Number(cell.dataset.c) };
    });
    const startEl = document.querySelector('#board .mk-start').closest('.cell');
    const goalEl = document.querySelector('#board .mk-goal').closest('.cell');
    return {
      size, rows, waypoints,
      start: [Number(startEl.dataset.r), Number(startEl.dataset.c)],
      goal: [Number(goalEl.dataset.r), Number(goalEl.dataset.c)],
    };
  });
}

async function checkMissionGame(page, width) {
  const tag = `mission ${width}px`;
  await page.locator('#board .cell').first().waitFor({ state: 'attached' });
  const puzzle = await readMissionPuzzle(page);
  const limit = await page.evaluate(() => Number(document.getElementById('moveText').textContent.split('/')[1]));
  const route = missionRoute(puzzle);
  const shortest = route.length - 1;
  const movesNow = () => page.evaluate(() => Number(document.getElementById('moveText').textContent.trim().split('/')[0]));
  assert.ok(shortest <= limit, `${tag}: shortest route ${shortest} exceeds limit ${limit}`);
  assert.equal(await movesNow(), 0, `${tag}: mission must start at 0 moves`);

  // 방향키 한 칸 → 되돌리기 버튼
  await page.keyboard.press(missionKey(route[0], route[1]));
  assert.equal(await movesNow(), 1, `${tag}: arrow key did not move`);
  await page.click('#undoBtn');
  assert.equal(await movesNow(), 0, `${tag}: undo did not reduce the move count`);

  // 최단 경로로 경유지를 모두 들르고 도착
  for (let i = 0; i < shortest; i += 1) await page.keyboard.press(missionKey(route[i], route[i + 1]));
  await page.locator('#resultBox:not([hidden])').waitFor({ timeout: 5000 });
  const done = await page.evaluate(() => ({
    move: document.getElementById('moveText').textContent.trim(),
    title: document.getElementById('resultTitle').textContent.trim(),
    share: document.getElementById('sharePreview').textContent,
    missions: document.querySelectorAll('#missionList .mitem.is-done').length,
    statToday: document.getElementById('statToday').textContent.trim(),
  }));
  assert.ok(done.move.startsWith(`${shortest} /`), `${tag}: move meter "${done.move}" != ${shortest}`);
  assert.ok(done.title.includes('도착'), `${tag}: clear title "${done.title}"`);
  assert.equal(done.missions, puzzle.waypoints.length + 1,
    `${tag}: mission checklist ${done.missions} != ${puzzle.waypoints.length + 1}`);
  assert.ok(done.share.includes('퇴근길 미션'), `${tag}: share text missing mission title`);
  assert.ok(!done.share.includes('Arrow'), `${tag}: share text leaks the route`);
  assert.ok(done.statToday.includes('클리어'), `${tag}: today stat "${done.statToday}"`);
  console.log(`mission game ${width}px passed (${shortest}수 / 제한 ${limit}수)`);
}

// ---- 모바 미션 화면: 한 화면 배치(390×844 · 390×700) + 스와이프 이동 ----
async function checkMissionMobile(browser, base) {
  for (const [width, height] of [[390, 844], [390, 700]]) {
    const tag = `mission mobile ${width}x${height}`;
    const context = await browser.newContext({ viewport: { width, height }, hasTouch: true });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', (error) => errors.push(error.message));
    page.on('console', (message) => {
      if (message.type() === 'error' && !message.text().startsWith('Failed to load resource:')) {
        errors.push(message.text());
      }
    });
    try {
      await page.goto(`${base}/mission.html`, { waitUntil: 'load' });
      await page.locator('#board .cell').first().waitFor({ state: 'attached' });
      const layout = await page.evaluate(() => {
        const box = (sel) => {
          const b = document.querySelector(sel).getBoundingClientRect();
          return { top: b.top, bottom: b.bottom, width: b.width, height: b.height };
        };
        const chips = Array.from(document.querySelectorAll('#missionList .mitem'));
        const padBtn = document.querySelector('.pad-btn').getBoundingClientRect();
        return {
          viewport: innerHeight,
          scrollY: window.scrollY,
          overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
          list: box('#missionList'),
          board: box('#board'),
          meters: box('.meters'),
          pad: box('#pad'),
          undo: box('#undoBtn'),
          reset: box('#resetBtn'),
          chipRows: new Set(chips.map((el) => Math.round(el.getBoundingClientRect().top / 8))).size,
          padBtn: { w: padBtn.width, h: padBtn.height },
          tabbarTop: document.querySelector('.ia-tabbar').getBoundingClientRect().top,
        };
      });
      assert.equal(layout.overflow, 0, `${tag}: horizontal overflow ${layout.overflow}px`);
      assert.equal(layout.scrollY, 0, `${tag}: page scrolled on load`);
      assert.equal(layout.chipRows, 1, `${tag}: waypoint chips wrap to ${layout.chipRows} rows`);
      assert.ok(layout.list.bottom <= layout.board.top + 0.5, `${tag}: chips are not above the board`);
      assert.ok(layout.board.bottom <= layout.meters.top + 0.5, `${tag}: board is not above the meters`);
      assert.ok(layout.padBtn.w >= 44 && layout.padBtn.h >= 44,
        `${tag}: D-pad touch target ${layout.padBtn.w}x${layout.padBtn.h}`);
      for (const key of ['pad', 'undo', 'reset']) {
        assert.ok(layout[key].bottom <= layout.viewport + 0.5,
          `${tag}: ${key} below the first screen (${Math.round(layout[key].bottom)} > ${layout.viewport})`);
        assert.ok(layout[key].bottom <= layout.tabbarTop + 0.5,
          `${tag}: ${key} hidden behind the bottom tab bar (${Math.round(layout[key].bottom)} > ${Math.round(layout.tabbarTop)})`);
      }

      // 지도 스와이프로 한 칸 이동하고 페이지는 움직이지 않는다
      const puzzle = await readMissionPuzzle(page);
      const route = missionRoute(puzzle);
      const movesNow = () => page.evaluate(() => Number(document.getElementById('moveText').textContent.trim().split('/')[0]));
      const center = await page.evaluate(() => {
        const b = document.getElementById('board').getBoundingClientRect();
        return { x: b.x + b.width / 2, y: b.y + b.height / 2 };
      });
      const dr = route[1][0] - route[0][0];
      const dc = route[1][1] - route[0][1];
      const cdp = await context.newCDPSession(page);
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: center.x, y: center.y }] });
      for (const factor of [1 / 3, 2 / 3, 1]) {
        await cdp.send('Input.dispatchTouchEvent', {
          type: 'touchMove',
          touchPoints: [{ x: center.x + (dc * 60 * factor), y: center.y + (dr * 60 * factor) }],
        });
      }
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
      await page.waitForTimeout(200);
      assert.equal(await movesNow(), 1, `${tag}: swipe did not move the player once`);
      assert.equal(await page.evaluate(() => window.scrollY), 0, `${tag}: swipe scrolled the page`);

      // 이어진 칸을 탭하면 딱 한 칸만 움직인다(스와이프와 클릭이 겹치지 않는다)
      const next = await page.evaluate(([r, c]) => {
        const el = document.querySelector(`#board .cell[data-r="${r}"][data-c="${c}"]`);
        const b = el.getBoundingClientRect();
        return { x: b.x + b.width / 2, y: b.y + b.height / 2 };
      }, route[2]);
      await page.touchscreen.tap(next.x, next.y);
      await page.waitForTimeout(200);
      assert.equal(await movesNow(), 2, `${tag}: tap after swipe moved the wrong number of cells`);
      assert.deepEqual(errors, [], `${tag}: browser errors`);
      console.log(`mission mobile ${width}x${height} passed (지도·조작부 첫 화면 안 ${Math.round(layout.pad.bottom)}px)`);
    } catch (error) {
      throw new Error(`${tag}: ${error.message}`, { cause: error });
    } finally {
      await context.close();
    }
  }
}

// ---- 차트 추리실: 단서 열기 → 정답 선택 → 실제 기간·종목·출처 공개 ----
async function checkChartGame(page, base, width) {
  const tag = `chart ${width}px`;
  const readState = () => page.evaluate(() => {
    const ep = byId[currentId];
    return {
      id: currentId,
      total: DATA.length,
      solved: document.getElementById('solvedStat').textContent.trim(),
      streak: document.getElementById('statStreak').textContent.trim(),
      open: document.querySelectorAll('#clueList .clue.open').length,
      dots: document.querySelectorAll('#cDots .dot.on').length,
      nextLabel: document.getElementById('nextClue').textContent.trim(),
      futureBars: document.querySelectorAll('#chartSvg .candle-up.is-future, #chartSvg .candle-down.is-future').length,
      maLine: document.querySelectorAll('#chartSvg .ma-line').length,
      resultHidden: document.getElementById('resultBox').hidden,
      badge: document.getElementById('resultBadge').textContent.trim(),
      period: document.getElementById('revealPeriod').textContent.trim(),
      name: document.getElementById('revealName').textContent.trim(),
      future: document.getElementById('revealFuture').textContent.trim(),
      href: document.getElementById('revealSource').getAttribute('href'),
      answer: ep.quiz.answer,
      answerText: ep.quiz.choices[ep.quiz.answer],
      share: document.getElementById('sharePreview').textContent,
      todayHidden: document.getElementById('pToday').hidden,
      locked: document.querySelectorAll('#options .opt:disabled').length,
      correctMarks: document.querySelectorAll('#options .opt.is-correct').length,
      wrongMarks: document.querySelectorAll('#options .opt.is-wrong').length,
    };
  });

  await page.waitForFunction(() => typeof currentId !== 'undefined' && !!currentId, null, { timeout: 5000 });
  const start = await readState();
  assert.ok(start.total >= 14, `${tag}: fewer than 14 charts`);
  assert.equal(start.open, 0, `${tag}: clues must start closed`);
  assert.equal(start.futureBars, 0, `${tag}: hidden segment drawn before the answer`);
  assert.equal(start.maLine, 0, `${tag}: moving averages drawn before the clues`);
  assert.equal(start.resultHidden, true, `${tag}: result box visible before answering`);
  assert.equal(start.todayHidden, false, `${tag}: today's chart must open by default`);

  // 단서 1 → 이동평균선 표시
  await page.click('#nextClue');
  await page.waitForFunction(() => document.querySelectorAll('#clueList .clue.open').length === 1,
    null, { timeout: 5000 });
  const one = await readState();
  assert.equal(one.dots, 1, `${tag}: clue dots`);
  assert.equal(one.maLine, 2, `${tag}: opening a clue must reveal the moving averages`);

  await page.click('#nextClue');
  await page.click('#nextClue');
  await page.waitForFunction(() => document.querySelectorAll('#clueList .clue.open').length === 3,
    null, { timeout: 5000 });
  const three = await readState();
  assert.equal(three.nextLabel, '단서 모두 열림', `${tag}: clue button label "${three.nextLabel}"`);

  // 정답 선택 → 실제 기간·종목·출처 공개
  await page.click(`#options .opt[data-idx="${start.answer}"]`);
  await page.locator('#resultBox:not([hidden])').waitFor({ timeout: 5000 });
  const won = await readState();
  assert.equal(won.badge, '정답', `${tag}: result badge`);
  assert.ok(won.name.length > 0 && won.period.length > 0 && won.future.length > 0,
    `${tag}: revealed period/name/future missing`);
  assert.ok(won.href && won.href.startsWith('https://'), `${tag}: source link missing`);
  assert.ok(won.futureBars > 0, `${tag}: hidden bars not drawn after the answer`);
  assert.equal(won.correctMarks, 1, `${tag}: correct option not highlighted`);
  assert.equal(won.locked, 4, `${tag}: options not locked after the answer`);
  assert.equal(won.solved, `1 / ${won.total}`, `${tag}: solved counter "${won.solved}"`);
  assert.ok(won.share.includes(`/chart.html?id=${encodeURIComponent(won.id)}`),
    `${tag}: share link has no chart id`);
  assert.ok(!won.share.includes(won.answerText) && !won.share.includes(won.name),
    `${tag}: share text leaks the answer`);

  // 새로고침해도 공개 상태·기록 유지
  await page.reload({ waitUntil: 'load' });
  await page.waitForFunction(() => typeof currentId !== 'undefined' && !!currentId, null, { timeout: 5000 });
  const kept = await readState();
  assert.equal(kept.id, won.id, `${tag}: reload opened another chart`);
  assert.equal(kept.resultHidden, false, `${tag}: reveal lost on reload`);
  assert.equal(kept.open, 3, `${tag}: clue progress lost on reload`);
  assert.ok(kept.futureBars > 0, `${tag}: hidden bars lost on reload`);
  assert.equal(kept.solved, `1 / ${kept.total}`, `${tag}: solved record lost on reload`);

  // ?id= 딥링크로 다른 차트를 열고 일부러 틀린 답 선택
  const other = await page.evaluate(() => Array.from(document.querySelectorAll('#arcGrid .arc-card'))
    .map(card => card.dataset.id).find(id => id !== currentId));
  assert.ok(other, `${tag}: no other chart to deep link`);
  await page.goto(`${base}/chart.html?id=${encodeURIComponent(other)}`, { waitUntil: 'load' });
  await page.waitForFunction((id) => typeof currentId !== 'undefined' && currentId === id, other, { timeout: 5000 });
  const fresh = await readState();
  assert.equal(fresh.resultHidden, true, `${tag}: deep linked chart already revealed`);
  await page.click(`#options .opt[data-idx="${(fresh.answer + 1) % 4}"]`);
  await page.locator('#resultBox:not([hidden])').waitFor({ timeout: 5000 });
  const lost = await readState();
  assert.equal(lost.badge, '아쉬움', `${tag}: wrong answer badge "${lost.badge}"`);
  assert.equal(lost.wrongMarks, 1, `${tag}: wrong option not highlighted`);
  assert.equal(lost.correctMarks, 1, `${tag}: correct option not highlighted after a wrong pick`);
  assert.equal(lost.solved, `1 / ${lost.total}`, `${tag}: wrong answer counted as solved`);
  assert.equal(lost.streak, '0', `${tag}: streak not reset after a wrong answer`);
  assert.ok(lost.name.length > 0 && lost.futureBars > 0, `${tag}: wrong answer must still reveal the chart`);
  console.log(`chart game ${width}px passed (${won.name} · 가려진 ${won.future})`);
}

// ---- 옷차림: 오늘 추천 우선 배치 · 스타일/기온 필터 ----
function firstScreenLimit() {
  const bar = document.querySelector('.ia-tabbar');
  const shown = bar && getComputedStyle(bar).display !== 'none';
  return shown ? bar.getBoundingClientRect().top : window.innerHeight;
}

async function checkOutfit(page, width) {
  const tag = `outfit ${width}px`;
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(150);
  const read = async () => {
    const limit = await page.evaluate(firstScreenLimit);
    return page.evaluate((limit) => {
    const inFirst = (el) => {
      if (!el) return false;
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0 && r.top >= 0 && r.bottom > 0 && r.bottom <= limit + 1;
    };
    const shown = Array.from(document.querySelectorAll('.band-section')).filter(s => !s.hidden);
    const rail = document.querySelector('.of-rail');
    const main = document.querySelector('.of-main');
    const cards = Array.from(document.querySelectorAll('.band-section:not([hidden]) .outfit-card'))
      .filter(c => !c.hidden);
    const tops = cards.map(c => Math.round(c.getBoundingClientRect().top));
    const minTop = tops.length ? Math.min(...tops) : 0;
    const perRow = tops.filter(t => Math.abs(t - minTop) < 2).length;
    return {
      wxFirst: (() => {
        const el = document.getElementById('wxCard');
        const r = el.getBoundingClientRect();
        return r.height > 0 && r.top < limit && r.bottom > 0;
      })(),
      recFirst: inFirst(document.getElementById('recText')),
      styleFirst: inFirst(document.getElementById('styleChips')),
      recText: document.getElementById('recText').textContent.trim(),
      recLabel: document.getElementById('recLabel').textContent.trim(),
      styleLine: document.getElementById('recStyleLine').textContent.trim(),
      styleLineHidden: document.getElementById('recStyleLine').hidden,
      visible: document.getElementById('visibleCount').textContent.trim(),
      shownBands: shown.map(s => s.dataset.band),
      firstBand: shown.length ? shown[0].dataset.band : null,
      todayBand: (document.querySelector('.band-section.is-today') || { dataset: {} }).dataset.band || null,
      sliderInRail: !!rail && rail.contains(document.getElementById('tempSlider')),
      styleInRail: !!rail && rail.contains(document.getElementById('styleChips')),
      seasonInRail: !!rail && rail.contains(document.getElementById('seasonTabs')),
      sticky: !!rail && getComputedStyle(rail).position === 'sticky',
      railRight: rail ? rail.getBoundingClientRect().right : null,
      mainLeft: main ? main.getBoundingClientRect().left : null,
      cardRows: new Set(tops).size,
      perRow,
      cards: cards.length,
      cardStyles: Array.from(new Set(cards.map(c => c.dataset.style))),
    };
  }, limit);
  };

  const first = await read();
  assert.ok(first.recText.length > 0, `${tag}: 오늘 추천 문구 없음`);
  assert.ok(first.todayBand, `${tag}: 오늘 구간 표시가 없다`);
  assert.equal(first.firstBand, first.todayBand, `${tag}: 오늘 구간이 목록 맨 위가 아니다`);
  if (width < 1024) {
    assert.equal(first.wxFirst, true, `${tag}: 첫 화면에 오늘 날씨 카드가 없다`);
    assert.equal(first.recFirst, true, `${tag}: 첫 화면에 오늘 추천 요약이 없다`);
    assert.equal(first.styleFirst, true, `${tag}: 첫 화면에 스타일 필터가 없다`);
    assert.equal(first.shownBands.length, 1, `${tag}: 모바일 첫 화면은 오늘 구간만 (${first.shownBands.length})`);
    assert.equal(first.visible, '3', `${tag}: 코디 ${first.visible}개`);
    assert.equal(first.perRow, width < 600 ? 1 : 2, `${tag}: 한 줄에 카드 ${first.perRow}개`);
  } else {
    assert.equal(first.sticky, true, `${tag}: 레일이 sticky 가 아니다`);
    assert.equal(first.sliderInRail && first.styleInRail && first.seasonInRail, true,
      `${tag}: 기온·스타일·계절 필터가 레일 밖에 있다`);
    assert.ok(first.railRight <= first.mainLeft, `${tag}: 레일이 목록 왼쪽에 있지 않다`);
    assert.equal(first.shownBands.length, 8, `${tag}: 구간 ${first.shownBands.length}개 표시`);
    assert.equal(first.visible, '24', `${tag}: 코디 ${first.visible}개`);
    assert.ok(first.perRow >= 2, `${tag}: PC 한 줄에 카드 ${first.perRow}개`);
  }

  // 스타일 필터 → 오늘 추천 요약이 그 스타일 코디로 바뀌고 목록도 좁아진다
  await page.click('#styleChips .chip[data-style="office"]');
  await page.waitForTimeout(120);
  const styled = await read();
  assert.ok(styled.recLabel.includes('오피스'), `${tag}: 스타일 추천 라벨 "${styled.recLabel}"`);
  assert.equal(styled.styleLineHidden, false, `${tag}: 스타일 코디 상세 없음`);
  assert.ok(styled.styleLine.includes('아우터'), `${tag}: 스타일 코디 상세 "${styled.styleLine}"`);
  assert.deepEqual(styled.cardStyles, ['office'], `${tag}: 스타일 필터가 카드에 적용되지 않음`);
  assert.equal(styled.visible, width < 1024 ? '1' : '8', `${tag}: 스타일 적용 코디 ${styled.visible}개`);

  // 전체 구간 칩 → 8구간 복원
  await page.click('#tempChips .chip[data-band=""]');
  await page.waitForTimeout(120);
  const all = await read();
  assert.equal(all.shownBands.length, 8, `${tag}: 전체 칩 후 구간 ${all.shownBands.length}개`);

  // 슬라이더 25°C → 초여름(b7) 구간
  await page.click('#styleChips .chip[data-style="all"]');
  await page.evaluate(() => {
    const slider = document.getElementById('tempSlider');
    slider.value = '25';
    slider.dispatchEvent(new Event('input', { bubbles: true }));
  });
  await page.waitForTimeout(120);
  const slide = await read();
  assert.deepEqual(slide.shownBands, ['b7'], `${tag}: 슬라이더 구간 ${slide.shownBands}`);
  assert.equal(slide.visible, '3', `${tag}: 슬라이더 후 코디 ${slide.visible}개`);

  // 필터 초기화 → 오늘 구간(모바일) / 전체(PC)
  await page.click('#resetFilters');
  await page.waitForTimeout(120);
  const reset = await read();
  assert.equal(reset.visible, width < 1024 ? '3' : '24', `${tag}: 초기화 후 코디 ${reset.visible}개`);
  console.log(`outfit ${width}px passed (오늘 ${first.todayBand} · 코디 ${reset.visible}개)`);
}

// ---- 오늘 뭐 먹지: 첫 화면 룰렛 · 상황/동행/스타일 칩 · 나들이 분리 ----
async function checkPick(page, width) {
  const tag = `pick ${width}px`;
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(150);
  const read = async () => {
    const limit = await page.evaluate(firstScreenLimit);
    return page.evaluate((limit) => {
    const inFirst = (el) => {
      if (!el) return false;
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0 && r.top >= 0 && r.bottom > 0 && r.bottom <= limit + 1;
    };
    const rail = document.querySelector('.pk-rail');
    const main = document.querySelector('.pk-main');
    return {
      wxFirst: inFirst(document.getElementById('wxCard')),
      modeFirst: inFirst(document.getElementById('modeChips')),
      sitFirst: inFirst(document.getElementById('sitChips')),
      compFirst: inFirst(document.getElementById('compChips')),
      styleFirst: inFirst(document.getElementById('styleChips')),
      drawFirst: inFirst(document.getElementById('drawBtn')),
      drawInRail: !!rail && rail.contains(document.getElementById('drawBtn')),
      slotInMain: !!main && main.contains(document.getElementById('slotCard')),
      coursesInMain: !!main && main.contains(document.getElementById('outingPanel')),
      coursesBelow: main && main.contains(document.getElementById('outingPanel'))
        ? document.getElementById('outingPanel').getBoundingClientRect().top
          > document.getElementById('resultPanel').getBoundingClientRect().top : false,
      railRight: rail ? rail.getBoundingClientRect().right : null,
      mainLeft: main ? main.getBoundingClientRect().left : null,
      cand: document.getElementById('candCount').textContent.trim(),
      modeTitle: document.getElementById('modeTitle').textContent.trim(),
      pickName: document.getElementById('pickName').textContent.trim(),
      slotHidden: document.getElementById('slotBody').hidden,
      recent: document.querySelectorAll('#recentList .list-item').length,
      fav: document.getElementById('favCount').textContent.trim(),
      quickHref: (document.querySelector('.quick-link') || {}).getAttribute
        ? document.querySelector('.quick-link').getAttribute('href') : null,
    };
  }, limit);
  };

  const first = await read();
  assert.equal(first.drawInRail, true, `${tag}: 뽑기 버튼이 조건 레일에 없다`);
  assert.equal(first.slotInMain, true, `${tag}: 추천 결과가 본문에 없다`);
  assert.equal(first.coursesBelow, true, `${tag}: 나들이 코스가 추천 결과 아래에 있지 않다`);
  if (width < 1024) {
    assert.equal(first.wxFirst, true, `${tag}: 첫 화면에 오늘 날씨가 없다`);
    assert.equal(first.modeFirst, true, `${tag}: 첫 화면에 추천 모드 칩이 없다`);
    assert.equal(first.sitFirst, true, `${tag}: 첫 화면에 상황 칩이 없다`);
    assert.equal(first.drawFirst, true, `${tag}: 첫 화면에 뽑기 버튼이 없다`);
  } else {
    assert.ok(first.railRight <= first.mainLeft, `${tag}: 조건 레일이 결과 왼쪽에 있지 않다`);
  }
  assert.ok(Number(first.cand) > 0, `${tag}: 후보 ${first.cand}개`);
  assert.equal(first.quickHref, '#outingPanel', `${tag}: 나들이 바로가기 링크`);

  // 상황 칩 → 후보 수 갱신
  await page.click('#sitChips .chip[data-sit="lunch"]');
  await page.waitForTimeout(120);
  const lunch = await read();
  assert.ok(Number(lunch.cand) > 0 && Number(lunch.cand) <= Number(first.cand),
    `${tag}: 점심 후보 ${lunch.cand}개 (전체 ${first.cand}개)`);

  // 모드 칩 → 추천 모드 문구 교체
  await page.click('#modeChips .chip[data-mode="rain"]');
  await page.waitForTimeout(120);
  const rain = await read();
  assert.ok(rain.modeTitle.includes('비'), `${tag}: 비 오는 날 모드 문구 "${rain.modeTitle}"`);
  await page.click('#modeChips .chip[data-mode="auto"]');

  // 뽑기 → 결과 카드·최근 기록
  await page.click('#drawBtn');
  await page.waitForFunction(() => {
    const body = document.getElementById('slotBody');
    const name = document.getElementById('pickName');
    const btn = document.getElementById('drawBtn');
    return !!body && !body.hidden && !!name && name.textContent.trim().length > 0 && !btn.disabled;
  }, null, { timeout: 10000 });
  const drawn = await read();
  assert.ok(drawn.pickName.length > 0, `${tag}: 뽑힌 메뉴 이름 없음`);
  assert.equal(drawn.slotHidden, false, `${tag}: 결과 카드가 숨겨져 있다`);
  assert.ok(drawn.recent >= 1, `${tag}: 최근 기록 ${drawn.recent}개`);

  // 즐겨찾기 토글
  await page.click('#pickStar');
  await page.waitForTimeout(150);
  const fav = await read();
  assert.equal(fav.fav, '1', `${tag}: 즐겨찾기 ${fav.fav}개`);

  // 나들이 바로가기 → 코스 섹션으로 이동
  await page.click('.quick-link');
  await page.waitForFunction(() => {
    const panel = document.getElementById('outingPanel');
    const top = panel.getBoundingClientRect().top;
    return location.hash === '#outingPanel' && top >= -2 && top < 140;
  }, null, { timeout: 4000 }).catch(() => {});
  const anchored = await page.evaluate(() => {
    const panel = document.getElementById('outingPanel');
    const top = panel.getBoundingClientRect().top;
    return { top, hash: location.hash };
  });
  assert.equal(anchored.hash, '#outingPanel', `${tag}: 해시 ${anchored.hash}`);
  assert.ok(anchored.top >= -2 && anchored.top < 140, `${tag}: 나들이 섹션 위치 ${Math.round(anchored.top)}px`);
  console.log(`pick ${width}px passed (${drawn.pickName} · 후보 ${first.cand}개)`);
}

// ---- 공통 셸: PC 드롭다운 내비 · 모바일 하단 탭 바 ----
async function checkShellLayout(page, width, name) {
  const tag = `shell ${name} ${width}px`;
  const state = await page.evaluate(() => {
    const visible = (el) => {
      if (!el) return false;
      const cs = getComputedStyle(el);
      const box = el.getBoundingClientRect();
      return cs.display !== 'none' && cs.visibility !== 'hidden' && box.width > 0 && box.height > 0;
    };
    const items = Array.from(document.querySelectorAll(
      '.ia-header-inner > .ia-menu > .ia-menu-link, .ia-header-inner .ia-menu-group'));
    const rects = items.map((el) => el.getBoundingClientRect());
    let overlap = false;
    for (let i = 1; i < rects.length; i += 1) {
      if (rects[i - 1].right > rects[i].left + 1) overlap = true;
    }
    const actions = document.querySelector('.ia-actions');
    if (actions && rects.length && rects[rects.length - 1].right > actions.getBoundingClientRect().left + 1) {
      overlap = true;
    }
    return {
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      header: visible(document.querySelector('.ia-header')),
      menu: visible(document.querySelector('.ia-menu')),
      tabbar: visible(document.querySelector('.ia-tabbar')),
      current: document.querySelector('.ia-current') ? document.querySelector('.ia-current').textContent.trim() : '',
      headerLinks: Array.from(new Set(Array.from(document.querySelectorAll('.ia-header a[href]'))
        .map((a) => a.getAttribute('href')).filter((href) => href && href.endsWith('.html')))),
      topEntries: items.length,
      overlap,
      bottomPad: parseFloat(getComputedStyle(document.body).paddingBottom) || 0,
    };
  });
  assert.equal(state.overflow, 0, `${tag}: horizontal overflow ${state.overflow}px`);
  assert.equal(state.header, true, `${tag}: shell header missing`);
  if (width <= 768) {
    assert.equal(state.menu, false, `${tag}: desktop menu must be hidden`);
    assert.equal(state.tabbar, true, `${tag}: bottom tab bar missing`);
    assert.ok(state.current.length > 0, `${tag}: current page label missing`);
    assert.ok(state.bottomPad >= 64, `${tag}: body padding-bottom ${state.bottomPad}px is too small for the tab bar`);
  } else {
    assert.equal(state.menu, true, `${tag}: desktop menu missing`);
    assert.equal(state.tabbar, false, `${tag}: bottom tab bar must be hidden on desktop`);
    assert.equal(state.overlap, false, `${tag}: header items overlap`);
    assert.equal(state.topEntries, 5, `${tag}: desktop nav has ${state.topEntries} top-level entries`);
    for (const href of SHELL_HREFS.filter((h) => h !== 'index.html')) {
      assert.ok(state.headerLinks.includes(href), `${tag}: ${href} not reachable from the header`);
    }
  }
}

// ---- 모바일 전체 메뉴 시트: 열기/닫기(버튼·딤·Escape) · 포커스 이동·복귀 · 스크롤 잠금 ----
async function checkMobileSheet(page, width, tag) {
  const readSheet = () => page.evaluate(() => {
    const sheet = document.getElementById('iaSheet');
    const bar = document.getElementById('iaAllBtn');
    return {
      hidden: sheet.hidden,
      open: sheet.classList.contains('is-open'),
      focusInside: sheet.contains(document.activeElement),
      focusId: document.activeElement ? document.activeElement.id : null,
      locked: document.body.classList.contains('ia-sheet-open'),
      bodyOverflow: getComputedStyle(document.body).overflow,
      expanded: bar.getAttribute('aria-expanded'),
      links: Array.from(document.querySelectorAll('#iaSheet .ia-sheet-link')).map((a) => a.getAttribute('href')),
      groups: Array.from(document.querySelectorAll('#iaSheet .ia-sheet-group')).map((g) => g.textContent.trim()),
      top: Math.round(sheet.getBoundingClientRect().top),
      vh: window.innerHeight,
    };
  });

  await page.click('#iaAllBtn');
  await page.waitForTimeout(320);
  const opened = await readSheet();
  assert.equal(opened.hidden, false, `${tag}: sheet did not open`);
  assert.equal(opened.open, true, `${tag}: sheet has no open state`);
  assert.equal(opened.focusInside, true, `${tag}: focus did not move into the sheet`);
  assert.equal(opened.locked, true, `${tag}: background scroll not locked`);
  assert.equal(opened.bodyOverflow, 'hidden', `${tag}: body overflow not hidden`);
  assert.equal(opened.expanded, 'true', `${tag}: 전체 button aria-expanded`);
  assert.equal(opened.links.length, SHELL_HREFS.length, `${tag}: sheet lists ${opened.links.length} pages`);
  for (const href of SHELL_HREFS) assert.ok(opened.links.includes(href), `${tag}: sheet missing ${href}`);
  assert.deepEqual(opened.groups, ['보안·채용', '브리핑·유틸', '데일리·생활', '게임·챌린지'], `${tag}: sheet groups`);
  assert.ok(opened.top >= 0 && opened.top < opened.vh, `${tag}: sheet off-screen (top ${opened.top})`);

  await page.keyboard.press('Escape');
  await page.waitForTimeout(320);
  const closed = await readSheet();
  assert.equal(closed.hidden, true, `${tag}: Escape did not close the sheet`);
  assert.equal(closed.focusId, 'iaAllBtn', `${tag}: focus did not return to 전체`);
  assert.equal(closed.locked, false, `${tag}: scroll lock not released`);
  assert.equal(closed.expanded, 'false', `${tag}: aria-expanded not reset`);

  await page.click('#iaAllBtn');
  await page.waitForTimeout(320);
  await page.mouse.click(Math.round(width / 2), 12);
  await page.waitForTimeout(320);
  const dimClosed = await readSheet();
  assert.equal(dimClosed.hidden, true, `${tag}: backdrop click did not close the sheet`);
  assert.equal(dimClosed.focusId, 'iaAllBtn', `${tag}: focus lost after backdrop close`);

  await page.click('#iaAllBtn');
  await page.waitForTimeout(320);
  await page.click('#iaSheetClose');
  await page.waitForTimeout(320);
  const btnClosed = await readSheet();
  assert.equal(btnClosed.hidden, true, `${tag}: close button did not close the sheet`);
  assert.equal(btnClosed.focusId, 'iaAllBtn', `${tag}: focus lost after close button`);
}

// ---- 빠른 열기→닫기 회귀: 같은 틱/같은 프레임에 Escape 해도 시트가 다시 열리지 않는다 ----
async function checkSheetFastToggle(page, width, tag) {
  const read = () => page.evaluate(() => {
    const sheet = document.getElementById('iaSheet');
    return {
      hidden: sheet.hidden,
      open: sheet.classList.contains('is-open'),
      expanded: document.getElementById('iaAllBtn').getAttribute('aria-expanded'),
      locked: document.body.classList.contains('ia-sheet-open'),
    };
  });

  // 1) 연 직후 같은 틱에 Escape
  await page.evaluate(() => {
    document.getElementById('iaAllBtn').click();
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
  });
  await page.waitForTimeout(380);
  const sameTick = await read();
  assert.equal(sameTick.hidden, true, `${tag}: fast close left the sheet mounted`);
  assert.equal(sameTick.open, false, `${tag}: reserved frame re-opened the sheet (same tick)`);
  assert.equal(sameTick.expanded, 'false', `${tag}: aria-expanded not false after a fast close`);
  assert.equal(sameTick.locked, false, `${tag}: scroll lock stuck after a fast close`);

  // 2) 다음 프레임에 Escape (예약된 rAF 가 아직 실행되기 전)
  await page.evaluate(() => new Promise((resolve) => {
    document.getElementById('iaAllBtn').click();
    requestAnimationFrame(() => {
      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
      resolve();
    });
  }));
  await page.waitForTimeout(380);
  const sameFrame = await read();
  assert.equal(sameFrame.open, false, `${tag}: reserved frame re-opened the sheet (same frame)`);
  assert.equal(sameFrame.hidden, true, `${tag}: fast close left the sheet mounted (same frame)`);
  assert.equal(sameFrame.expanded, 'false', `${tag}: aria-expanded not false after a same-frame close`);

  // 3) 이후에는 정상적으로 열고 닫힌다
  await page.click('#iaAllBtn');
  await page.waitForTimeout(320);
  const reopened = await read();
  assert.equal(reopened.open, true, `${tag}: sheet broken after a fast close`);
  assert.equal(reopened.expanded, 'true', `${tag}: aria-expanded not restored`);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(320);
  const reclosed = await read();
  assert.equal(reclosed.hidden, true, `${tag}: sheet did not close normally afterwards`);
}

// ---- 채용공고: PC 필터 레일 / 모바일 필터 시트 · 배지 ----
async function checkIndexLayout(page, width, tag) {
  const count = async () => parseInt((await page.textContent('#matchCount')).trim(), 10);

  // KPI 단위('건')는 카드마다 한 번만 보인다(숫자에 '건'이 중복되지 않음).
  const kpi = await page.evaluate(() => Array.from(document.querySelectorAll('.ia-kpi')).map((card) => ({
    value: card.querySelector('.ia-kpi-value').textContent.trim(),
    text: card.textContent.replace(/\s+/g, ' ').trim(),
  })));
  assert.equal(kpi.length, 4, `${tag}: expected 4 KPI cards, found ${kpi.length}`);
  for (const card of kpi) {
    assert.ok(/^\d+$/.test(card.value), `${tag}: KPI value carries extra text (${card.value}) in "${card.text}"`);
    assert.equal((card.text.match(/건/g) || []).length, 1, `${tag}: unit 건 repeated in "${card.text}"`);
  }

  if (width >= 1024) {
    const rail = await page.evaluate(() => {
      const el = document.getElementById('filterRail');
      return {
        visible: el.getBoundingClientRect().width > 0 && getComputedStyle(el).visibility !== 'hidden',
        position: getComputedStyle(el).position,
        aside: el.tagName === 'ASIDE',
      };
    });
    assert.equal(rail.visible, true, `${tag}: filter rail missing`);
    assert.equal(rail.aside, true, `${tag}: filter rail is not an aside`);
    assert.equal(rail.position, 'sticky', `${tag}: filter rail is not a sticky side rail`);
    const before = await count();
    await page.click('.filter-pill[data-filter="platform"][data-val="원티드"]');
    assert.ok(await count() < before, `${tag}: platform filter did not narrow the feed`);
    await page.click('.filter-pill[data-filter="platform"][data-val="all"]');
    await page.fill('#searchInput', 'zzzz-no-such-job');
    await page.waitForFunction(() => document.getElementById('matchCount').textContent.trim() === '0',
      null, { timeout: 5000 });
    await page.click('[data-action="reset-filters"]');
    await page.waitForFunction(() => Number(document.getElementById('matchCount').textContent.trim()) > 0,
      null, { timeout: 5000 });
    return;
  }

  const railState = () => page.evaluate(() => {
    const rail = document.getElementById('filterRail');
    const btn = document.getElementById('filterOpenBtn');
    return {
      open: rail.classList.contains('is-open'),
      focusInside: rail.contains(document.activeElement),
      focusId: document.activeElement ? document.activeElement.id : null,
      locked: document.body.classList.contains('ia-filter-open'),
      expanded: btn.getAttribute('aria-expanded'),
      badge: document.getElementById('filterBadge').textContent.trim(),
    };
  });

  await page.click('#filterOpenBtn');
  await page.waitForTimeout(320);
  const opened = await railState();
  assert.equal(opened.open, true, `${tag}: filter sheet did not open`);
  assert.equal(opened.focusInside, true, `${tag}: focus did not move into the filter sheet`);
  assert.equal(opened.locked, true, `${tag}: filter sheet scroll lock`);
  assert.equal(opened.expanded, 'true', `${tag}: 필터 button aria-expanded`);

  const before = await count();
  await page.click('.filter-pill[data-filter="deadline"][data-val="urgent"]');
  await page.waitForTimeout(150);
  assert.ok(await count() <= before, `${tag}: deadline filter widened the feed`);
  assert.equal((await railState()).badge, '1', `${tag}: filter badge`);

  await page.keyboard.press('Escape');
  await page.waitForTimeout(320);
  const closed = await railState();
  assert.equal(closed.open, false, `${tag}: Escape did not close the filter sheet`);
  assert.equal(closed.focusId, 'filterOpenBtn', `${tag}: focus did not return to 필터`);
  assert.equal(closed.locked, false, `${tag}: filter scroll lock not released`);

  await page.selectOption('#sortSelectMobile', 'company');
  assert.equal(await page.inputValue('#sortSelect'), 'company', `${tag}: mobile sort not synced to the rail`);
}

// ---- CVE: PC 필터 레일 / 모바일 필터 시트 · 배지 · 적용 ----
async function checkCveFilters(page, width, tag) {
  const count = async () => parseInt((await page.textContent('#visibleCount')).trim(), 10);
  if (width >= 1024) {
    const rail = await page.evaluate(() => {
      const el = document.getElementById('cveRail');
      return {
        visible: el.getBoundingClientRect().width > 0 && getComputedStyle(el).visibility !== 'hidden',
        position: getComputedStyle(el).position,
        aside: el.tagName === 'ASIDE',
        searchInside: !!document.getElementById('searchInput').closest('#cveRail'),
      };
    });
    assert.equal(rail.visible, true, `${tag}: filter rail missing`);
    assert.equal(rail.aside, true, `${tag}: filter rail is not an aside`);
    assert.equal(rail.position, 'sticky', `${tag}: filter rail is not a sticky side rail`);
    assert.equal(rail.searchInside, true, `${tag}: desktop search must live in the rail`);

    const total = await count();
    await page.click('.segment-btn[data-filter="critical"]');
    await page.waitForTimeout(100);
    const critical = await count();
    assert.ok(critical > 0 && critical < total, `${tag}: severity filter did not narrow (${critical}/${total})`);
    await page.click('#sourceNav .filter-pill[data-src="cisa"]');
    await page.waitForTimeout(100);
    assert.ok(await count() <= critical, `${tag}: source filter widened the feed`);
    assert.equal((await page.textContent('#cveFilterBadge')).trim(), '2', `${tag}: filter badge`);
    await page.click('#sourceNav .filter-pill[data-src="all"]');
    await page.click('.segment-btn[data-filter="all"]');
    await page.waitForTimeout(100);
    assert.equal(await count(), total, `${tag}: filters did not reset`);
    assert.equal((await page.textContent('#cveFilterBadge')).trim(), '0', `${tag}: badge after reset`);

    await page.fill('#searchInput', 'zzzz-no-such-cve');
    await page.waitForFunction(() => document.getElementById('visibleCount').textContent.trim() === '0',
      null, { timeout: 5000 });
    await page.click('#resetFiltersMeta');
    await page.waitForFunction((t) => Number(document.getElementById('visibleCount').textContent.trim()) === t,
      total, { timeout: 5000 });
    return;
  }

  const railState = () => page.evaluate(() => {
    const rail = document.getElementById('cveRail');
    const btn = document.getElementById('cveFilterOpenBtn');
    return {
      open: rail.classList.contains('is-open'),
      focusInside: rail.contains(document.activeElement),
      focusId: document.activeElement ? document.activeElement.id : null,
      locked: document.body.classList.contains('cve-filter-open'),
      expanded: btn.getAttribute('aria-expanded'),
      badge: document.getElementById('cveFilterBadge').textContent.trim(),
      searchOutside: !!document.getElementById('searchInput').closest('.cve-mobile-controls'),
    };
  });

  assert.equal((await railState()).searchOutside, true, `${tag}: mobile search must sit above the list`);
  const total = await count();
  await page.click('#cveFilterOpenBtn');
  await page.waitForTimeout(320);
  const opened = await railState();
  assert.equal(opened.open, true, `${tag}: filter sheet did not open`);
  assert.equal(opened.focusInside, true, `${tag}: focus did not move into the filter sheet`);
  assert.equal(opened.locked, true, `${tag}: filter sheet scroll lock`);
  assert.equal(opened.expanded, 'true', `${tag}: 필터 button aria-expanded`);

  await page.click('.segment-btn[data-filter="kev"]');
  await page.waitForTimeout(120);
  assert.equal((await railState()).badge, '1', `${tag}: filter badge after a severity pick`);
  assert.ok(await count() < total, `${tag}: KEV filter did not narrow the feed`);

  await page.keyboard.press('Escape');
  await page.waitForTimeout(320);
  const closed = await railState();
  assert.equal(closed.open, false, `${tag}: Escape did not close the filter sheet`);
  assert.equal(closed.focusId, 'cveFilterOpenBtn', `${tag}: focus did not return to 필터`);
  assert.equal(closed.locked, false, `${tag}: filter scroll lock not released`);

  // 시트를 열고 바로 같은 틱에 Escape 해도 다시 열리지 않는다(예약 rAF 경합)
  await page.evaluate(() => {
    document.getElementById('cveFilterOpenBtn').click();
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
  });
  await page.waitForTimeout(320);
  const fast = await railState();
  assert.equal(fast.open, false, `${tag}: filter sheet reopened after a same-tick close`);
  assert.equal(fast.locked, false, `${tag}: scroll lock stuck after a same-tick close`);

  await page.click('#resetFiltersMeta');
  await page.waitForTimeout(120);
  assert.equal(await count(), total, `${tag}: reset did not restore the list`);
}

// ---- AI: PC 필터 레일 / 모바일 필터 시트 · 배지 ----
async function checkAiFilters(page, width, tag) {
  const count = async () => parseInt((await page.textContent('#visibleCount')).trim(), 10);
  if (width >= 1024) {
    const rail = await page.evaluate(() => {
      const el = document.getElementById('aiRail');
      return {
        visible: el.getBoundingClientRect().width > 0 && getComputedStyle(el).visibility !== 'hidden',
        position: getComputedStyle(el).position,
        aside: el.tagName === 'ASIDE',
        searchInside: !!document.getElementById('searchInput').closest('#aiRail'),
        briefOpen: document.getElementById('aiBrief').open,
      };
    });
    assert.equal(rail.visible, true, `${tag}: filter rail missing`);
    assert.equal(rail.aside, true, `${tag}: filter rail is not an aside`);
    assert.equal(rail.position, 'sticky', `${tag}: filter rail is not a sticky side rail`);
    assert.equal(rail.searchInside, true, `${tag}: desktop search must live in the rail`);
    assert.equal(rail.briefOpen, true, `${tag}: desktop briefing must start expanded`);

    const total = await count();
    await page.click('#categoryNav .segment-btn[data-cat="featured"]');
    await page.waitForTimeout(120);
    const featured = await count();
    assert.ok(featured > 0 && featured < total, `${tag}: featured filter did not narrow (${featured}/${total})`);
    assert.equal((await page.textContent('#aiFilterBadge')).trim(), '1', `${tag}: filter badge`);

    const firstSource = await page.evaluate(() => {
      const pill = Array.from(document.querySelectorAll('#sourceNav .filter-pill')).find(b => b.dataset.src !== 'all');
      return pill ? pill.dataset.src : null;
    });
    assert.ok(firstSource, `${tag}: no source pills`);
    await page.click(`#sourceNav .filter-pill[data-src="${firstSource}"]`);
    await page.waitForTimeout(120);
    assert.ok(await count() <= featured, `${tag}: source filter did not narrow`);

    await page.click('#resetFiltersMeta');
    await page.waitForTimeout(120);
    assert.equal(await count(), total, `${tag}: reset did not restore the list`);
    assert.equal((await page.textContent('#aiFilterBadge')).trim(), '0', `${tag}: badge after reset`);
    return;
  }

  const railState = () => page.evaluate(() => {
    const rail = document.getElementById('aiRail');
    const btn = document.getElementById('aiFilterOpenBtn');
    return {
      open: rail.classList.contains('is-open'),
      focusInside: rail.contains(document.activeElement),
      focusId: document.activeElement ? document.activeElement.id : null,
      locked: document.body.classList.contains('ai-filter-open'),
      expanded: btn.getAttribute('aria-expanded'),
      badge: document.getElementById('aiFilterBadge').textContent.trim(),
      searchOutside: !!document.getElementById('searchInput').closest('.ai-mobile-controls'),
      briefOpen: document.getElementById('aiBrief').open,
    };
  });

  assert.equal((await railState()).searchOutside, true, `${tag}: mobile search must sit above the list`);
  assert.equal((await railState()).briefOpen, false, `${tag}: mobile briefing must start collapsed`);
  const total = await count();
  await page.click('#aiFilterOpenBtn');
  await page.waitForTimeout(320);
  const opened = await railState();
  assert.equal(opened.open, true, `${tag}: filter sheet did not open`);
  assert.equal(opened.focusInside, true, `${tag}: focus did not move into the filter sheet`);
  assert.equal(opened.locked, true, `${tag}: filter sheet scroll lock`);

  await page.click('#categoryNav .segment-btn[data-cat="featured"]');
  await page.waitForTimeout(120);
  assert.equal((await railState()).badge, '1', `${tag}: filter badge`);
  assert.ok(await count() < total, `${tag}: featured filter did not narrow`);

  await page.keyboard.press('Escape');
  await page.waitForTimeout(320);
  const closed = await railState();
  assert.equal(closed.open, false, `${tag}: Escape did not close the filter sheet`);
  assert.equal(closed.focusId, 'aiFilterOpenBtn', `${tag}: focus did not return to 필터`);
  assert.equal(closed.locked, false, `${tag}: filter scroll lock not released`);

  await page.click('#resetFiltersMeta');
  await page.waitForTimeout(120);
  assert.equal(await count(), total, `${tag}: reset did not restore the list`);
}

// ---- 시험 공부: 좌측 탐색 레일 / 모바일 칩·드로어 · 풀이·북마크·진행률 ----
async function checkStudyHub(page, width, tag) {
  const placement = await page.evaluate(() => {
    const mode = document.getElementById('modeNavGrid');
    const subj = document.getElementById('subjPills');
    const rail = document.getElementById('studyRail');
    return {
      railAside: rail.tagName === 'ASIDE',
      railPosition: getComputedStyle(rail).position,
      modeInRail: !!mode.closest('#studyRail'),
      modeInMobile: !!mode.closest('#mobileModeSlot'),
      subjInRail: !!subj.closest('#studyRail'),
      subjInMobile: !!subj.closest('#mobileSubjSlot'),
      examInRail: !!document.getElementById('examBtnGroup').closest('#studyRail'),
    };
  });
  assert.equal(placement.railAside, true, `${tag}: learning rail is not an aside`);
  assert.equal(placement.examInRail, true, `${tag}: exam picker must live in the rail`);
  if (width >= 1024) {
    assert.equal(placement.railPosition, 'sticky', `${tag}: learning rail is not sticky`);
    assert.equal(placement.modeInRail, true, `${tag}: mode switch must live in the rail on desktop`);
    assert.equal(placement.subjInRail, true, `${tag}: subject chips must live in the rail on desktop`);
  } else {
    assert.equal(placement.modeInMobile, true, `${tag}: mode chips must sit at the top on mobile`);
    assert.equal(placement.subjInMobile, true, `${tag}: subject chips must sit at the top on mobile`);
  }

  // 문제 풀이: 선택 → 즉시 채점·해설·진행률 반영
  const before = await page.evaluate(() => ({
    solved: Number(document.getElementById('topSolved').textContent),
    total: Number(document.getElementById('topTotal').textContent),
    fill: document.getElementById('progressFill').style.width,
    explained: document.querySelectorAll('#questionsList .exp-box.show').length,
  }));
  assert.ok(before.total > 0, `${tag}: no questions rendered`);
  const target = await page.evaluate(() => {
    const row = document.querySelector('#questionsList .q-card .choice-row[data-action="select-choice"]');
    return { id: row.getAttribute('data-id'), choice: row.getAttribute('data-choice') };
  });
  await page.click(`.choice-row[data-id="${target.id}"][data-choice="${target.choice}"]`);
  await page.waitForTimeout(150);
  const after = await page.evaluate(() => ({
    solved: Number(document.getElementById('topSolved').textContent),
    explained: document.querySelectorAll('#questionsList .exp-box.show').length,
    fill: document.getElementById('progressFill').style.width,
    header: document.querySelectorAll('#questionsList .exp-header').length,
  }));
  assert.equal(after.solved, before.solved + 1, `${tag}: solved counter did not increase`);
  assert.ok(after.explained >= before.explained + 1, `${tag}: explanation not revealed after answering`);
  assert.notEqual(after.fill, before.fill, `${tag}: progress bar did not move`);

  // 북마크: 카드 표시 + localStorage 보관
  await page.click('#questionsList .q-card [data-action="toggle-bookmark"]');
  await page.waitForTimeout(120);
  const marked = await page.evaluate(() => ({
    on: document.querySelectorAll('#questionsList .q-mark.is-on').length,
    stored: Object.keys(JSON.parse(localStorage.getItem('study_bookmarks_v1') || '{}')).length,
  }));
  assert.ok(marked.on >= 1, `${tag}: bookmark state not shown on the card`);
  assert.ok(marked.stored >= 1, `${tag}: bookmark not saved`);

  if (width >= 1024) return;

  const railState = () => page.evaluate(() => {
    const rail = document.getElementById('studyRail');
    const btn = document.getElementById('studyFilterOpenBtn');
    return {
      open: rail.classList.contains('is-open'),
      locked: document.body.classList.contains('study-rail-open'),
      expanded: btn.getAttribute('aria-expanded'),
      focusInside: rail.contains(document.activeElement),
      focusId: document.activeElement ? document.activeElement.id : null,
      badge: document.getElementById('studyFilterBadge').textContent.trim(),
    };
  });

  await page.click('#studyFilterOpenBtn');
  await page.waitForTimeout(320);
  const opened = await railState();
  assert.equal(opened.open, true, `${tag}: drawer did not open`);
  assert.equal(opened.locked, true, `${tag}: drawer scroll lock`);
  assert.equal(opened.expanded, 'true', `${tag}: 탐색 button aria-expanded`);
  assert.equal(opened.focusInside, true, `${tag}: focus did not move into the drawer`);

  // 회차 선택 → 드로어가 닫히고 바로 문제가 바뀐다
  const examCount = await page.evaluate(() => document.querySelectorAll('#examBtnGroup .exam-btn').length);
  assert.ok(examCount >= 2, `${tag}: exam buttons missing`);
  await page.click('#examBtnGroup .exam-btn:nth-child(2)');
  await page.waitForTimeout(360);
  const picked = await railState();
  assert.equal(picked.open, false, `${tag}: picking an exam did not close the drawer`);
  assert.equal(picked.locked, false, `${tag}: drawer scroll lock not released`);
  assert.equal(picked.focusId, 'studyFilterOpenBtn', `${tag}: focus did not return to 탐색`);
  assert.ok(Number(picked.badge) >= 1, `${tag}: filter badge ${picked.badge}`);

  // 오답만 보기 → 배지 증가, Escape 로 닫기
  await page.click('#studyFilterOpenBtn');
  await page.waitForTimeout(320);
  await page.click('#btnWrongOnly');
  await page.waitForTimeout(120);
  assert.ok(Number((await railState()).badge) >= 2, `${tag}: wrong-only did not count on the badge`);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(320);
  const closed = await railState();
  assert.equal(closed.open, false, `${tag}: Escape did not close the drawer`);
  assert.equal(closed.focusId, 'studyFilterOpenBtn', `${tag}: focus did not return to 탐색`);
}

// ---- 하단 탭 바가 페이지 마지막 콘텐츠를 가리지 않는지 ----
async function checkBottomBar(page, width, name) {
  const tag = `bottom bar ${name} ${width}px`;
  await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
  await page.waitForTimeout(150);
  const gap = await page.evaluate(() => {
    const bar = document.querySelector('.ia-tabbar');
    const main = document.querySelector('main') || document.querySelector('.container');
    const foot = document.querySelector('footer, .footer');
    const last = foot || (main ? main.lastElementChild : null);
    return {
      barTop: bar.getBoundingClientRect().top,
      lastBottom: last ? last.getBoundingClientRect().bottom : null,
      lastTag: last ? last.tagName.toLowerCase() : null,
      pad: parseFloat(getComputedStyle(document.body).paddingBottom) || 0,
      innerHeight: window.innerHeight,
    };
  });
  assert.ok(gap.barTop > 0 && gap.barTop < gap.innerHeight, `${tag}: tab bar not fixed on screen`);
  assert.ok(gap.lastBottom !== null, `${tag}: page has no main content`);
  assert.ok(gap.lastBottom <= gap.barTop + 0.5,
    `${tag}: last <${gap.lastTag}> ends at ${Math.round(gap.lastBottom)}, under the tab bar (${Math.round(gap.barTop)})`);
  assert.ok(gap.pad >= 64, `${tag}: body padding-bottom ${gap.pad}px`);
}

// ---- prefers-reduced-motion: 전환·애니메이션 비활성 ----
async function checkReducedMotion(browser, base) {
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 }, reducedMotion: 'reduce',
  });
  const page = await context.newPage();
  try {
    await page.goto(`${base}/ai.html`, { waitUntil: 'load' });
    await page.click('#iaAllBtn');
    const state = await page.evaluate(() => {
      const ms = (value) => (value.endsWith('ms') ? parseFloat(value) : parseFloat(value) * 1000);
      const sheet = document.getElementById('iaSheet');
      const tab = document.querySelector('.ia-tab');
      const card = document.querySelector('.ai-card') || document.querySelector('button');
      return {
        hidden: sheet.hidden,
        open: sheet.classList.contains('is-open'),
        sheetMs: ms(getComputedStyle(sheet).transitionDuration.split(',')[0].trim()),
        tabMs: ms(getComputedStyle(tab).transitionDuration.split(',')[0].trim()),
        cardMs: card ? ms(getComputedStyle(card).transitionDuration.split(',')[0].trim()) : 0,
        sheetTransform: getComputedStyle(sheet).transform,
      };
    });
    assert.equal(state.hidden, false, 'reduced motion: sheet did not open');
    assert.equal(state.open, true, 'reduced motion: sheet has no open state');
    assert.ok(state.sheetMs <= 0.02, `reduced motion: sheet transition ${state.sheetMs}ms`);
    assert.ok(state.tabMs <= 0.02, `reduced motion: tab transition ${state.tabMs}ms`);
    assert.ok(state.cardMs <= 0.02, `reduced motion: card transition ${state.cardMs}ms`);
    console.log('prefers-reduced-motion passed');
  } finally {
    await context.close();
  }
}

// ---- 워게임: 한 번에 한 문제 · PC 좌측 탐색 레일 · 모바일 문제 목록 시트 · 채점 KPI ----
async function checkWargame(page, width) {
  const tag = `wargame ${width}px`;
  const readCard = () => page.evaluate(() => ({
    visible: Array.from(document.querySelectorAll('.q-card')).filter((c) => !c.hidden).length,
    active: document.querySelector('.wg-item.is-active') ? document.querySelector('.wg-item.is-active').dataset.id : null,
    shown: document.querySelector('.q-card:not([hidden])') ? document.querySelector('.q-card:not([hidden])').dataset.id : null,
    solved: document.getElementById('kpiSolved').textContent,
    focus: document.activeElement ? document.activeElement.id : null,
  }));

  let state = await readCard();
  assert.equal(state.visible, 1, `${tag}: exactly one problem must be shown`);
  assert.ok(state.shown, `${tag}: no problem selected`);
  assert.equal(state.active, state.shown, `${tag}: rail selection differs from the shown card`);

  // 정답을 고를 수 있는 문제로 이동해 채점이 KPI·레일에 반영되는지
  const choiceId = await page.evaluate(() => (DATA.find((q) => q.type === 'choice') || {}).id);
  assert.ok(choiceId, `${tag}: no choice question`);
  if (width < 1024) {
    await page.click('#wgListOpen');
    await page.waitForTimeout(320);
  }
  await page.click(`.wg-item[data-id="${choiceId}"]`);
  await page.waitForTimeout(360);
  const solved = await page.evaluate((id) => {
    const card = document.getElementById('q-' + id);
    const q = DATA.find((x) => x.id === id);
    card.querySelector('.opt[data-idx="' + q.answer + '"]').click();
    return {
      state: card.classList.contains('is-solved'),
      kpi: document.getElementById('kpiSolved').textContent,
      rail: document.querySelector('.wg-item[data-id="' + id + '"]').className,
      hash: location.hash,
    };
  }, choiceId);
  assert.equal(solved.state, true, `${tag}: answer did not solve the card`);
  assert.equal(solved.kpi, '1', `${tag}: KPI solved ${solved.kpi}`);
  assert.ok(solved.rail.includes('is-done'), `${tag}: rail item not marked solved`);
  assert.equal(solved.hash, '#q-' + choiceId, `${tag}: deep link hash not synced`);

  if (width < 1024) {
    await page.click('#wgListOpen');
    await page.waitForTimeout(340);
    let sheet = await page.evaluate(() => ({
      open: document.getElementById('wgRail').classList.contains('is-open'),
      locked: document.body.classList.contains('wg-sheet-open'),
      expanded: document.getElementById('wgListOpen').getAttribute('aria-expanded'),
      focus: document.activeElement.id,
      railTop: Math.round(document.getElementById('wgRail').getBoundingClientRect().top),
      vh: window.innerHeight,
    }));
    assert.equal(sheet.open, true, `${tag}: problem list sheet did not open`);
    assert.equal(sheet.locked, true, `${tag}: sheet did not lock scrolling`);
    assert.equal(sheet.expanded, 'true', `${tag}: aria-expanded not set`);
    assert.equal(sheet.focus, 'wgRailClose', `${tag}: focus not moved into the sheet`);
    assert.ok(sheet.railTop < sheet.vh - 40, `${tag}: sheet is off screen`);

    await page.keyboard.press('Escape');
    await page.waitForTimeout(340);
    sheet = await page.evaluate(() => ({
      open: document.getElementById('wgRail').classList.contains('is-open'),
      locked: document.body.classList.contains('wg-sheet-open'),
      focus: document.activeElement.id,
    }));
    assert.equal(sheet.open, false, `${tag}: Escape did not close the sheet`);
    assert.equal(sheet.locked, false, `${tag}: scroll lock not released`);
    assert.equal(sheet.focus, 'wgListOpen', `${tag}: focus did not return to 문제 목록`);

    // 목록에서 다른 문제를 고르면 시트가 닫힌다.
    await page.click('#wgListOpen');
    await page.waitForTimeout(340);
    const other = await page.evaluate((cur) => {
      const items = Array.from(document.querySelectorAll('.wg-item'));
      const pick = items.find((b) => b.dataset.id !== cur);
      return pick ? pick.dataset.id : null;
    }, choiceId);
    assert.ok(other, `${tag}: no second problem in the list`);
    await page.click(`.wg-item[data-id="${other}"]`);
    await page.waitForTimeout(420);
    const after = await page.evaluate(() => ({
      open: document.getElementById('wgRail').classList.contains('is-open'),
      shown: document.querySelector('.q-card:not([hidden])').dataset.id,
      locked: document.body.classList.contains('wg-sheet-open'),
    }));
    assert.equal(after.open, false, `${tag}: sheet did not close after picking a problem`);
    assert.equal(after.locked, false, `${tag}: scroll lock left on after picking`);
    assert.equal(after.shown, other, `${tag}: picked problem not shown`);
  } else {
    const geo = await page.evaluate(() => {
      const rail = document.getElementById('wgRail').getBoundingClientRect();
      const main = document.querySelector('.wg-main').getBoundingClientRect();
      return { railRight: rail.right, mainLeft: main.left, railTop: rail.top, sticky: getComputedStyle(document.getElementById('wgRail')).position };
    });
    assert.ok(geo.railRight <= geo.mainLeft + 1, `${tag}: rail is not left of the problem`);
    assert.equal(geo.sticky, 'sticky', `${tag}: rail is not sticky`);

    await page.click('.chip[data-group="status"][data-value="done"]');
    await page.waitForTimeout(150);
    const filtered = await page.evaluate(() => ({
      items: document.querySelectorAll('.wg-item').length,
      shown: document.querySelectorAll('.q-card:not([hidden])').length,
      empty: document.getElementById('emptyState').classList.contains('show'),
      active: document.querySelector('.wg-item.is-active').dataset.id,
    }));
    assert.equal(filtered.items, 1, `${tag}: solved filter shows ${filtered.items} items`);
    assert.equal(filtered.shown, 1, `${tag}: solved filter must keep one card`);
    assert.equal(filtered.active, choiceId, `${tag}: filter dropped the solved problem`);

    await page.click('.chip[data-group="status"][data-value="todo"]');
    await page.waitForTimeout(150);
    const todo = await page.evaluate(() => ({
      items: document.querySelectorAll('.wg-item').length,
      shown: document.querySelectorAll('.q-card:not([hidden])').length,
      activeDone: document.querySelector('.wg-item.is-active').classList.contains('is-done'),
    }));
    assert.equal(todo.items, 23, `${tag}: todo filter shows ${todo.items} items`);
    assert.equal(todo.shown, 1, `${tag}: todo filter must keep one card`);
    assert.equal(todo.activeDone, false, `${tag}: todo filter kept the solved problem`);

    await page.click('#resetFilters');
    await page.waitForTimeout(120);
    const reset = await page.evaluate(() => document.querySelectorAll('.wg-item').length);
    assert.equal(reset, 24, `${tag}: filters did not reset (${reset})`);
  }
  console.log(`wargame interactions ${width}px passed`);
}

// ---- 3단서 추리: PC 2단(플레이어 ↔ 아카이브 레일) · 모바일 1줄 요약 + 첫 화면 단서 ----
async function checkClueLayout(page, width) {
  const tag = `clue layout ${width}px`;
  const geo = await page.evaluate(() => {
    const player = document.getElementById('playPanel').getBoundingClientRect();
    const rail = document.querySelector('.clue-rail').getBoundingClientRect();
    const clue = document.querySelector('#clueList .clue').getBoundingClientRect();
    const next = document.getElementById('nextClue').getBoundingClientRect();
    const opt = document.querySelector('#options .opt').getBoundingClientRect();
    const kpis = document.querySelector('.clue-kpis');
    const archiveCards = document.querySelectorAll('#arcGrid .arc-card').length;
    return {
      playerLeft: player.left, playerRight: player.right, playerTop: player.top,
      railLeft: rail.left, railTop: rail.top,
      clueTop: clue.top, nextTop: next.top, optTop: opt.top, vh: window.innerHeight,
      kpiVisible: kpis && getComputedStyle(kpis).display !== 'none',
      archiveCards,
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    };
  });
  assert.equal(geo.overflow, 0, `${tag}: horizontal overflow`);
  assert.ok(geo.kpiVisible, `${tag}: streak/solved summary missing`);
  assert.ok(geo.archiveCards > 1, `${tag}: archive cards missing`);
  if (width >= 1024) {
    assert.ok(geo.railLeft >= geo.playerRight - 1, `${tag}: archive is not a right rail`);
  } else {
    assert.ok(geo.railTop > geo.playerTop, `${tag}: archive rail is not below the puzzle`);
    assert.ok(geo.clueTop < geo.vh - 40, `${tag}: first clue below the fold`);
    assert.ok(geo.optTop < geo.vh + 40, `${tag}: answer choices start below the first screen`);
  }
  console.log(`clue layout ${width}px passed`);
}

// ---- 피싱 레이더: 모바일 세그먼트 전환 · PC 2단(퀴즈·검사기 ↔ 수법·대응) ----
async function checkRadar(page, width) {
  const tag = `radar ${width}px`;
  const views = () => page.evaluate(() => ({
    quiz: !document.getElementById('rdViewQuiz').hidden,
    scan: !document.getElementById('rdViewScan').hidden,
    trends: !document.getElementById('rdViewTrends').hidden,
    segs: getComputedStyle(document.querySelector('.rd-segments')).display,
  }));

  let state = await views();
  if (width < 1024) {
    assert.equal(state.quiz, true, `${tag}: quiz view must be the default`);
    assert.equal(state.scan, false, `${tag}: scan view must start hidden`);
    assert.equal(state.trends, false, `${tag}: trends view must start hidden`);

    await page.click('.rd-seg[data-view="scan"]');
    await page.waitForTimeout(380);
    const scan = await page.evaluate(() => {
      const input = document.getElementById('scanInput').getBoundingClientRect();
      const btn = document.getElementById('scanBtn').getBoundingClientRect();
      return {
        view: !document.getElementById('rdViewScan').hidden,
        inputTop: input.top, inputBottom: input.bottom, btnTop: btn.top, btnBottom: btn.bottom,
        vh: window.innerHeight,
      };
    });
    assert.equal(scan.view, true, `${tag}: URL 검사기 segment did not switch`);
    assert.ok(scan.inputTop < scan.vh - 40, `${tag}: scan input below the fold`);
    assert.ok(scan.btnBottom < scan.vh, `${tag}: 검사 button below the first screen`);

    await page.click('#scanSamples .sample');
    await page.click('#scanBtn');
    const result = await page.evaluate(() => ({
      hidden: document.getElementById('scanResult').hidden,
      text: document.getElementById('scanResult').textContent.length,
    }));
    assert.equal(result.hidden, false, `${tag}: scan produced no result`);
    assert.ok(result.text > 20, `${tag}: scan result is empty`);

    await page.click('.rd-seg[data-view="trends"]');
    await page.waitForTimeout(320);
    const trends = await page.evaluate(() => ({
      view: !document.getElementById('rdViewTrends').hidden,
      cards: document.querySelectorAll('.trend-card').length,
      checks: document.querySelectorAll('.check-item').length,
      quiz: !document.getElementById('rdViewQuiz').hidden,
    }));
    assert.equal(trends.view, true, `${tag}: 유행 수법 segment did not switch`);
    assert.equal(trends.quiz, false, `${tag}: quiz still visible in trends view`);
    assert.ok(trends.cards >= 6, `${tag}: trend cards ${trends.cards}`);
    assert.ok(trends.checks >= 5, `${tag}: checklist items ${trends.checks}`);
    await page.click('.rd-seg[data-view="quiz"]');
    await page.waitForTimeout(320);
  } else {
    assert.equal(state.quiz && state.scan && state.trends, true, `${tag}: PC must show all three sections`);
    assert.equal(state.segs, 'none', `${tag}: segments must be hidden on PC`);
    const geo = await page.evaluate(() => {
      const main = document.querySelector('.rd-main').getBoundingClientRect();
      const rail = document.querySelector('.rd-rail').getBoundingClientRect();
      const scan = document.getElementById('rdViewScan').getBoundingClientRect();
      const quiz = document.getElementById('rdViewQuiz').getBoundingClientRect();
      return { mainRight: main.right, railLeft: rail.left, scanTop: scan.top, quizTop: quiz.top };
    });
    assert.ok(geo.railLeft >= geo.mainRight - 1, `${tag}: right rail is not beside the quiz`);
    assert.ok(geo.scanTop <= geo.quizTop, `${tag}: scanner must sit above the quiz on PC`);
  }

  const answered = await page.evaluate(() => {
    const card = document.querySelector('.qcard');
    const q = QUIZ.find((x) => x.id === card.dataset.qid);
    card.querySelector('.ans-btn[data-pick="' + q.answer + '"]').click();
    return { solved: document.getElementById('solvedNum').textContent, mobile: document.getElementById('mAnswered').textContent };
  });
  assert.equal(answered.solved, '1', `${tag}: summary did not count the answer`);
  assert.equal(answered.mobile, '1', `${tag}: mobile progress did not count the answer`);

  const checks = await page.evaluate(() => {
    document.querySelector('.check-item input').click();
    return document.getElementById('checkDone').textContent;
  });
  assert.equal(checks, '1', `${tag}: checklist not saved`);
  console.log(`radar interactions ${width}px passed`);
}

// ---- 실무 유틸: 모바일 세그먼트(실무 유틸·치트시트) · PC 좌측 도구/치트 필터 레일 ----
async function checkTools(page, width) {
  const tag = `tools ${width}px`;
  const state = await page.evaluate(() => ({
    tools: !document.getElementById('tlViewTools').hidden,
    cheat: !document.getElementById('tlViewCheat').hidden,
    segs: getComputedStyle(document.querySelector('.tl-segments')).display,
    controlsParent: document.getElementById('cheatControls').parentNode.id || '',
    tabs: document.querySelectorAll('.tool-tab').length,
  }));
  assert.equal(state.tabs, 5, `${tag}: tool tabs ${state.tabs}`);

  if (width < 1024) {
    assert.equal(state.tools, true, `${tag}: tools view must be the default`);
    assert.equal(state.cheat, false, `${tag}: cheat view must start hidden`);
    assert.equal(state.controlsParent, 'tlViewCheat', `${tag}: cheat filter must stay in the cheat view`);
    const first = await page.evaluate(() => {
      const input = document.getElementById('encInput').getBoundingClientRect();
      const btn = document.getElementById('encRun').getBoundingClientRect();
      return { inputTop: input.top, btnBottom: btn.bottom, vh: window.innerHeight };
    });
    assert.ok(first.inputTop < first.vh - 60, `${tag}: tool input below the fold`);
    assert.ok(first.btnBottom < first.vh, `${tag}: run/copy buttons below the first screen`);

    await page.click('.tl-seg[data-view="cheat"]');
    await page.waitForTimeout(380);
    const cheat = await page.evaluate(() => ({
      view: !document.getElementById('tlViewCheat').hidden,
      tools: !document.getElementById('tlViewTools').hidden,
      searchTop: document.getElementById('cheatSearch').getBoundingClientRect().top,
      rail: getComputedStyle(document.querySelector('.tl-rail')).display,
      vh: window.innerHeight,
    }));
    assert.equal(cheat.view, true, `${tag}: 치트시트 segment did not switch`);
    assert.equal(cheat.tools, false, `${tag}: tools view still visible`);
    assert.equal(cheat.rail, 'none', `${tag}: tool chips still shown in cheat view`);
    assert.ok(cheat.searchTop < cheat.vh - 40, `${tag}: cheat search below the fold`);
    await page.fill('#cheatSearch', 'tcpdump');
    await page.waitForTimeout(150);
    const filtered = await page.evaluate(() => document.querySelectorAll('.cheat-card:not(.hide)').length);
    assert.ok(filtered > 0 && filtered < 38, `${tag}: cheat search shows ${filtered}`);
    await page.click('#resetCheat');
    await page.click('.tl-seg[data-view="tools"]');
    await page.waitForTimeout(320);
  } else {
    assert.equal(state.tools && state.cheat, true, `${tag}: PC must show tools and cheat sheet`);
    assert.equal(state.segs, 'none', `${tag}: segments must be hidden on PC`);
    assert.equal(state.controlsParent, 'tlRailCheat', `${tag}: cheat filter must sit in the left rail`);
    const geo = await page.evaluate(() => {
      const rail = document.querySelector('.tl-rail').getBoundingClientRect();
      const main = document.querySelector('.tl-main').getBoundingClientRect();
      const input = document.getElementById('encInput').getBoundingClientRect();
      const out = document.getElementById('encOutput').getBoundingClientRect();
      return { railRight: rail.right, mainLeft: main.left, inRight: input.right, outLeft: out.left };
    });
    assert.ok(geo.railRight <= geo.mainLeft + 1, `${tag}: tool rail is not left of the workspace`);
    assert.ok(geo.inRight <= geo.outLeft + 1, `${tag}: encoder input/output are not 2 columns`);
  }

  const enc = await page.evaluate(() => {
    const input = document.getElementById('encInput');
    input.value = 'hello';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    return new Promise((resolve) => setTimeout(() => resolve(document.getElementById('encOutput').value), 300));
  });
  assert.equal(enc, 'aGVsbG8=', `${tag}: base64 encode failed (${enc})`);
  await page.evaluate(() => document.querySelector('.tool-tab[data-tool="jwt"]').click());
  const activePanel = await page.evaluate(() => document.querySelector('.panel.active').id);
  assert.equal(activePanel, 'panel-jwt', `${tag}: tool tab switch failed`);
  console.log(`tools interactions ${width}px passed`);
}


// ---- 채용공고: 관심 목록(상태·메모) · 보관된 관심 공고 · 저장 검색 ----
async function openIndexRail(page, width) {
  if (width >= 1024) return;
  const open = await page.evaluate(() => document.getElementById('filterRail').classList.contains('is-open'));
  if (!open) {
    await page.click('#filterOpenBtn');
    await page.waitForTimeout(320);
  }
}

async function closeIndexRail(page, width) {
  if (width >= 1024) return;
  await page.keyboard.press('Escape');
  await page.waitForTimeout(320);
}

async function checkIndexWatchlist(page, width) {
  const tag = `index watchlist ${width}px`;
  const reset = async () => {
    await page.evaluate(() => {
      localStorage.removeItem('secjobs-watchlist-v1');
      localStorage.removeItem('secjobs-saved-searches-v1');
    });
    await page.reload({ waitUntil: 'load' });
    await page.locator('#jobsContainer .job-card').first().waitFor({ state: 'attached' });
  };
  const cardState = (key) => page.evaluate((k) => {
    const card = document.querySelector('[data-key="' + k + '"]');
    if (!card) return null;
    const star = card.querySelector('[data-watch-toggle]');
    const select = card.querySelector('[data-watch-status]');
    const memo = card.querySelector('[data-watch-memo]');
    return {
      pressed: star ? star.getAttribute('aria-pressed') : null,
      status: select ? select.value : null,
      memo: memo ? memo.value : null,
      images: card.querySelectorAll('img').length,
    };
  }, key);

  await reset();
  assert.equal(await page.evaluate(() => window.__xss), undefined, `${tag}: window.__xss already set`);

  // 카드마다 관심 토글·상태 선택·한 줄 메모가 붙는다
  const controls = await page.evaluate(() => ({
    cards: document.querySelectorAll('#jobsContainer .job-card').length,
    stars: document.querySelectorAll('#jobsContainer .job-card .watch-btn').length,
    selects: document.querySelectorAll('#jobsContainer .job-card .status-select').length,
    memos: document.querySelectorAll('#jobsContainer .job-card .memo-input').length,
    uniqueKeys: new Set(JOBS.map((job) => job.job_key)).size,
    jobs: JOBS.length,
    sharedUrlBroken: (() => {
      const byUrl = {};
      JOBS.forEach((job) => { (byUrl[job.url] = byUrl[job.url] || []).push(job.job_key); });
      return Object.values(byUrl).some((keys) => new Set(keys).size !== keys.length);
    })(),
  }));
  assert.ok(controls.cards > 0, `${tag}: no cards rendered`);
  assert.equal(controls.stars, controls.cards, `${tag}: star toggle missing on some cards`);
  assert.equal(controls.selects, controls.cards, `${tag}: status select missing on some cards`);
  assert.equal(controls.memos, controls.cards, `${tag}: memo input missing on some cards`);
  assert.equal(controls.uniqueKeys, controls.jobs, `${tag}: job_key is not unique`);
  assert.equal(controls.sharedUrlBroken, false, `${tag}: two postings share one job_key`);

  // 1) 같은 통합 URL을 쓰는 서로 다른 공고는 별도 키로 분리되고, 한쪽 메모가 다른 쪽에 섞이지 않는다
  const pair = await page.evaluate(() => {
    const now = new Date().toISOString();
    const base = {
      url: 'https://example.test/shared-posting-url',
      platforms: ['사람인'], keywords: ['정보보안'], tags: [], location: '', summary: '',
      deadline: '상시채용', deadline_label: '상시채용', deadline_status: 'ALWAYS',
      last_seen_at: now, first_seen_at: now,
    };
    const a = Object.assign({}, base, { job_key: 'test:shared:aaa', company: '테스트회사', title: '동일 URL 공고 A' });
    const b = Object.assign({}, base, { job_key: 'test:shared:bbb', company: '테스트회사', title: '동일 URL 공고 B' });
    JOBS.unshift(a, b);
    jobByKey[a.job_key] = a;
    jobByKey[b.job_key] = b;
    renderFeed();
    return { a: a.job_key, b: b.job_key };
  });
  await page.locator(`[data-key="${pair.a}"] .watch-btn`).waitFor({ state: 'attached' });
  await page.selectOption(`[data-key="${pair.a}"] .status-select`, '지원예정');
  await page.fill(`[data-key="${pair.a}"] .memo-input`, 'A에만 남는 메모');
  const sameUrl = { a: await cardState(pair.a), b: await cardState(pair.b) };
  assert.equal(sameUrl.a.status, '지원예정', `${tag}: status not saved on the first posting`);
  assert.equal(sameUrl.a.memo, 'A에만 남는 메모', `${tag}: memo not saved on the first posting`);
  assert.equal(sameUrl.b.pressed, 'false', `${tag}: second posting of the same URL got watched`);
  assert.equal(sameUrl.b.memo, '', `${tag}: memo leaked to the other posting on the same URL`);
  assert.equal(await page.evaluate(() => Object.keys(JSON.parse(localStorage.getItem('secjobs-watchlist-v1'))).length), 1,
    `${tag}: one posting must create exactly one watch entry`);

  // 2) XSS 문자열은 마크업이 아니라 글자로만 남는다
  const realKey = await page.evaluate(() => JOBS.filter((job) => job.job_key.indexOf('test:') !== 0)[0].job_key);
  const payload = '<img src=x onerror="window.__xss=1">';
  await page.fill(`[data-key="${realKey}"] .memo-input`, payload);
  await page.waitForTimeout(120);
  const xss = await cardState(realKey);
  assert.equal(xss.memo, payload, `${tag}: memo text was mangled`);
  assert.equal(xss.images, 0, `${tag}: memo was rendered as markup`);
  assert.equal(await page.evaluate(() => window.__xss), undefined, `${tag}: memo script executed`);

  // 3) 새로고침해도 관심·상태·메모가 그대로 복원된다
  await page.click(`[data-key="${realKey}"] .watch-btn`);
  await page.selectOption(`[data-key="${realKey}"] .status-select`, '지원예정');
  await page.fill(`[data-key="${realKey}"] .memo-input`, '새로고침 후에도 남는 메모');
  await page.reload({ waitUntil: 'load' });
  await page.locator(`[data-key="${realKey}"] .watch-btn`).waitFor({ state: 'attached' });
  const restored = await cardState(realKey);
  assert.equal(restored.pressed, 'true', `${tag}: watch state lost on reload`);
  assert.equal(restored.status, '지원예정', `${tag}: status lost on reload`);
  assert.equal(restored.memo, '새로고침 후에도 남는 메모', `${tag}: memo lost on reload`);

  // 4) 공고가 현재 목록에서 빠져도 보관된 관심 공고에서 상태·메모를 계속 고칠 수 있다
  const removed = await page.evaluate((key) => {
    const index = JOBS.findIndex((job) => job.job_key === key);
    const job = JOBS[index];
    JOBS.splice(index, 1);
    renderFeed();
    return { company: job.company, title: job.title };
  }, realKey);
  await page.locator('#watchArchive:not([hidden])').waitFor({ timeout: 5000 });
  const archived = await page.evaluate((key) => {
    const item = document.querySelector('#watchArchiveList [data-watch-for="' + key + '"]');
    if (!item) return null;
    return {
      title: item.querySelector('.watch-arch-title').textContent,
      company: item.querySelector('.watch-arch-company').textContent,
      status: item.querySelector('.status-select').value,
      memo: item.querySelector('.memo-input').value,
      link: item.querySelector('.watch-arch-link').getAttribute('href'),
    };
  }, realKey);
  assert.ok(archived, `${tag}: archived watch item missing`);
  assert.equal(archived.title, removed.title, `${tag}: archived title mismatch`);
  assert.equal(archived.company, removed.company, `${tag}: archived company mismatch`);
  assert.equal(archived.status, '지원예정', `${tag}: archived status lost`);
  assert.equal(archived.memo, '새로고침 후에도 남는 메모', `${tag}: archived memo lost`);
  assert.ok(/^https?:/.test(archived.link), `${tag}: archived original link missing`);

  await page.selectOption(`#watchArchiveList [data-watch-for="${realKey}"] .status-select`, '면접');
  await page.fill(`#watchArchiveList [data-watch-for="${realKey}"] .memo-input`, '보관함에서 고친 메모');
  const stored = await page.evaluate((key) => JSON.parse(localStorage.getItem('secjobs-watchlist-v1'))[key], realKey);
  assert.equal(stored.status, '면접', `${tag}: archived status edit not saved`);
  assert.equal(stored.memo, '보관함에서 고친 메모', `${tag}: archived memo edit not saved`);

  // 5) 저장 검색: 저장 → 초기화(새로고침) → 칩 클릭으로 검색어·필터·정렬 복원
  await page.reload({ waitUntil: 'load' });
  await page.locator('#jobsContainer .job-card').first().waitFor({ state: 'attached' });
  await openIndexRail(page, width);
  await page.fill('#searchInput', '보안');
  await page.click('#keywordNav .segment-btn[data-kw="정보보안"]');
  await page.click('.filter-pill[data-filter="platform"][data-val="원티드"]');
  await page.selectOption(width >= 1024 ? '#sortSelect' : '#sortSelectMobile', 'company');
  await page.click('#saveSearchBtn');
  const chip = await page.evaluate(() => {
    const el = document.querySelector('#savedSearchList .saved-chip-apply');
    return el ? { label: el.textContent, count: document.querySelectorAll('#savedSearchList .saved-chip').length } : null;
  });
  assert.ok(chip && chip.label.includes('보안') && chip.label.includes('원티드'), `${tag}: saved search label "${chip && chip.label}"`);
  assert.equal(chip.count, 1, `${tag}: saved search chip missing`);

  await page.reload({ waitUntil: 'load' });
  await page.locator('#jobsContainer .job-card').first().waitFor({ state: 'attached' });
  const cleared = await page.evaluate(() => ({
    term: document.getElementById('searchInput').value,
    sort: document.getElementById('sortSelect').value,
    platform: (document.querySelector('.filter-pill[data-filter="platform"].active') || {}).getAttribute
      ? document.querySelector('.filter-pill[data-filter="platform"].active').getAttribute('data-val') : null,
  }));
  assert.equal(cleared.term, '', `${tag}: search term survived reload`);
  assert.equal(cleared.sort, 'deadline', `${tag}: sort survived reload`);

  await openIndexRail(page, width);
  await page.click('#savedSearchList .saved-chip-apply');
  await page.waitForTimeout(200);
  const restoredSearch = await page.evaluate(() => ({
    term: document.getElementById('searchInput').value,
    keyword: (document.querySelector('#keywordNav .segment-btn.active') || {}).getAttribute
      ? document.querySelector('#keywordNav .segment-btn.active').getAttribute('data-kw') : null,
    platform: (document.querySelector('.filter-pill[data-filter="platform"].active') || {}).getAttribute
      ? document.querySelector('.filter-pill[data-filter="platform"].active').getAttribute('data-val') : null,
    sort: document.getElementById('sortSelect').value,
    count: Number(document.getElementById('matchCount').textContent.trim()),
  }));
  assert.equal(restoredSearch.term, '보안', `${tag}: saved search did not restore the query`);
  assert.equal(restoredSearch.keyword, '정보보안', `${tag}: saved search did not restore the keyword`);
  assert.equal(restoredSearch.platform, '원티드', `${tag}: saved search did not restore the platform`);
  assert.equal(restoredSearch.sort, 'company', `${tag}: saved search did not restore the sort`);
  assert.ok(restoredSearch.count > 0, `${tag}: saved search restored an empty result`);

  // 저장 검색 삭제 → 칩이 사라진다
  await openIndexRail(page, width);
  await page.click('#savedSearchList .saved-chip-del');
  assert.equal(await page.evaluate(() => document.querySelectorAll('#savedSearchList .saved-chip').length), 0,
    `${tag}: saved search chip not deleted`);

  // 6) 관심만 필터로 좁히면 저장된 관심 공고만 남는다
  await page.reload({ waitUntil: 'load' });
  await page.locator('#jobsContainer .job-card').first().waitFor({ state: 'attached' });
  await openIndexRail(page, width);
  await page.click('.filter-pill[data-filter="watch"][data-val="watch"]');
  await page.waitForTimeout(150);
  const watchOnly = await page.evaluate(() => {
    const cards = Array.from(document.querySelectorAll('#jobsContainer .job-card'));
    return {
      count: cards.length,
      allWatched: cards.every((card) => card.getAttribute('data-watch-for') in JSON.parse(localStorage.getItem('secjobs-watchlist-v1'))),
      badge: document.getElementById('filterBadge').textContent.trim(),
    };
  });
  assert.equal(watchOnly.count, 1, `${tag}: watch-only filter shows ${watchOnly.count} cards`);
  assert.equal(watchOnly.allWatched, true, `${tag}: watch-only filter shows an unwatched card`);
  assert.equal(watchOnly.badge, '1', `${tag}: watch-only filter badge`);

  await closeIndexRail(page, width);
  await reset();
  console.log(`index watchlist ${width}px passed`);
}

// ---- 시험공부 복습 큐: 오답·북마크 자동 등록 · 간격 반복 갱신 · 기존 정답률 보존 · 새로고침 복원 ----
async function checkStudyReviewQueue(page, width) {
  const tag = `study review ${width}px`;
  const readQueue = () => page.evaluate(() => {
    const store = JSON.parse(localStorage.getItem('study_review_queue_v1') || 'null') || { items: {}, dismissed: {} };
    return { ids: Object.keys(store.items || {}), items: store.items || {}, dismissed: store.dismissed || {} };
  });

  await page.evaluate(() => {
    localStorage.removeItem('study_review_queue_v1');
    localStorage.removeItem('study_user_answers_v4');
    localStorage.removeItem('study_bookmarks_v1');
  });
  await page.reload({ waitUntil: 'load' });
  await page.locator('#questionsList .q-card').first().waitFor({ state: 'attached' });
  assert.equal(await page.evaluate(() => localStorage.getItem('study_review_queue_v1')), null,
    `${tag}: review queue must start empty before any wrong answer or bookmark`);

  // 1) 일반 퀴즈 1문항 오답 + 다른 1문항 북마크 → 둘 다 복습 큐에 한 번씩만 등록된다
  const pick = await page.evaluate(() => {
    const cards = Array.from(document.querySelectorAll('#questionsList .q-card'));
    const card = cards[0];
    const id = card.querySelector('[data-action="toggle-bookmark"]').getAttribute('data-id');
    const q = (window.ALL_QUESTIONS || []).find((x) => x.id === id);
    const other = cards[1].querySelector('[data-action="toggle-bookmark"]').getAttribute('data-id');
    return { id, answer: q ? q.answer : null, bookmarkId: other };
  });
  assert.ok(pick.answer, `${tag}: question data missing for the first card`);
  const wrongChoice = pick.answer === 1 ? 2 : 1;
  await page.click(`.choice-row[data-id="${pick.id}"][data-choice="${wrongChoice}"]`);
  await page.waitForTimeout(150);
  await page.click(`#questionsList [data-action="toggle-bookmark"][data-id="${pick.bookmarkId}"]`);
  await page.waitForTimeout(150);

  const queued = await readQueue();
  assert.deepEqual(queued.ids.slice().sort(), [pick.id, pick.bookmarkId].sort(),
    `${tag}: wrong and bookmarked questions must both enter the queue`);
  assert.equal(new Set(queued.ids).size, queued.ids.length, `${tag}: duplicate question in the queue`);
  assert.equal(await page.evaluate(() => document.getElementById('modeReviewCount').textContent), '2',
    `${tag}: review badge must show the due count`);

  // 이미 오답인 문항을 북마크해도 같은 문항이 두 번 들어가지 않는다
  const duplicated = await page.evaluate((id) => {
    window.toggleBookmark(id);
    const store = JSON.parse(localStorage.getItem('study_review_queue_v1'));
    const ids = Object.keys(store.items);
    return { ids: ids, unique: new Set(ids).size };
  }, pick.id);
  assert.equal(duplicated.ids.length, 2, `${tag}: bookmarking a wrong question added a second entry`);
  assert.equal(duplicated.unique, 2, `${tag}: duplicated question id in the queue`);

  // 2) 복습 모드: 정답 → 다음 간격이 늘어나고 일반 퀴즈 정답률은 그대로
  await page.click('#modeReviewBtn');
  await page.waitForTimeout(250);
  const view = await page.evaluate(() => ({
    section: getComputedStyle(document.getElementById('reviewSection')).display,
    quiz: getComputedStyle(document.getElementById('questionsList')).display,
    cards: Array.from(document.querySelectorAll('#reviewList .review-card')).map((c) => c.getAttribute('data-review-q')),
    due: document.getElementById('reviewDueCount').textContent,
    total: document.getElementById('reviewTotalCount').textContent,
  }));
  assert.notEqual(view.section, 'none', `${tag}: review view is hidden`);
  assert.equal(view.quiz, 'none', `${tag}: quiz list must hide in review mode`);
  assert.equal(view.cards.length, 2, `${tag}: review list shows ${view.cards.length} cards`);
  assert.equal(view.due, '2', `${tag}: today's due count ${view.due}`);
  assert.equal(view.total, '2', `${tag}: queue total ${view.total}`);

  const answersBefore = await page.evaluate(() => localStorage.getItem('study_user_answers_v4'));
  const solvedBefore = await page.evaluate(() => document.getElementById('topSolved').textContent);
  const firstId = view.cards[0];
  const firstAnswer = await page.evaluate((id) => {
    const q = (window.ALL_QUESTIONS || []).find((x) => x.id === id);
    return q ? q.answer : null;
  }, firstId);
  assert.ok(firstAnswer, `${tag}: answer data missing for ${firstId}`);
  await page.click(`#reviewList .review-card[data-review-q="${firstId}"] .choice-row[data-choice="${firstAnswer}"]`);
  await page.waitForTimeout(200);
  const afterCorrect = await page.evaluate((id) => {
    const item = JSON.parse(localStorage.getItem('study_review_queue_v1')).items[id];
    const card = document.querySelector('#reviewList .review-card[data-review-q="' + id + '"]');
    return {
      result: item.last_result,
      stage: item.stage,
      count: item.review_count,
      hours: (item.next_review_at - Date.now()) / 3600000,
      answers: localStorage.getItem('study_user_answers_v4'),
      solved: document.getElementById('topSolved').textContent,
      due: document.getElementById('reviewDueCount').textContent,
      explained: !!(card && card.querySelector('.exp-box.show')),
    };
  }, firstId);
  assert.equal(afterCorrect.result, 'correct', `${tag}: first review result not stored`);
  assert.equal(afterCorrect.stage, 1, `${tag}: stage after a correct review ${afterCorrect.stage}`);
  assert.equal(afterCorrect.count, 1, `${tag}: review count ${afterCorrect.count}`);
  assert.ok(afterCorrect.hours > 23 && afterCorrect.hours < 25,
    `${tag}: first correct interval ${Math.round(afterCorrect.hours * 10) / 10}h`);
  assert.equal(afterCorrect.answers, answersBefore, `${tag}: review mode must not touch study_user_answers_v4`);
  assert.equal(afterCorrect.solved, solvedBefore, `${tag}: solved KPI changed in review mode`);
  assert.equal(afterCorrect.due, '1', `${tag}: due badge after one correct review ${afterCorrect.due}`);
  assert.equal(afterCorrect.explained, true, `${tag}: explanation not shown after a review answer`);

  // 3) 복습 모드: 오답 → 짧은 간격(같은 날)으로 재예약
  const secondId = await page.evaluate(() => {
    const row = document.querySelector('#reviewList .review-card .choice-row[data-action="review-choice"]');
    return row ? row.getAttribute('data-id') : null;
  });
  assert.ok(secondId, `${tag}: no answerable card left for the wrong-answer check`);
  const secondAnswer = await page.evaluate((id) => {
    const q = (window.ALL_QUESTIONS || []).find((x) => x.id === id);
    return q ? q.answer : null;
  }, secondId);
  const secondWrong = secondAnswer === 1 ? 2 : 1;
  await page.click(`#reviewList .review-card[data-review-q="${secondId}"] .choice-row[data-choice="${secondWrong}"]`);
  await page.waitForTimeout(200);
  const afterWrong = await page.evaluate((id) => {
    const item = JSON.parse(localStorage.getItem('study_review_queue_v1')).items[id];
    return {
      result: item.last_result,
      stage: item.stage,
      hours: (item.next_review_at - Date.now()) / 3600000,
      answers: localStorage.getItem('study_user_answers_v4'),
      due: document.getElementById('reviewDueCount').textContent,
    };
  }, secondId);
  assert.equal(afterWrong.result, 'wrong', `${tag}: wrong review result not stored`);
  assert.equal(afterWrong.stage, 0, `${tag}: wrong review must reset the stage`);
  assert.ok(afterWrong.hours > 3 && afterWrong.hours < 5,
    `${tag}: wrong interval ${Math.round(afterWrong.hours * 10) / 10}h should be the same day`);
  assert.equal(afterWrong.answers, answersBefore, `${tag}: wrong review rewrote study_user_answers_v4`);
  assert.equal(afterWrong.due, '0', `${tag}: due badge after all reviews ${afterWrong.due}`);

  // 4) 새로고침 후 복습 큐·일정·진행 상태가 그대로 복원된다
  const stored = await page.evaluate(() => localStorage.getItem('study_review_queue_v1'));
  await page.reload({ waitUntil: 'load' });
  await page.waitForTimeout(300);
  const restored = await page.evaluate(() => ({
    stored: localStorage.getItem('study_review_queue_v1'),
    badge: document.getElementById('modeReviewCount').textContent,
    total: document.getElementById('reviewTotalCount').textContent,
    solved: document.getElementById('topSolved').textContent,
  }));
  assert.equal(restored.stored, stored, `${tag}: review queue not restored after reload`);
  assert.equal(restored.total, '2', `${tag}: queue total after reload ${restored.total}`);
  assert.equal(restored.badge, '0', `${tag}: due badge after reload ${restored.badge}`);
  assert.equal(restored.solved, solvedBefore, `${tag}: solved KPI changed after a review reload`);

  await page.click('#modeReviewBtn');
  await page.waitForTimeout(200);
  await page.click('#reviewAllTab');
  await page.waitForTimeout(200);
  const allTab = await page.evaluate(() => ({
    cards: document.querySelectorAll('#reviewList .review-card').length,
    stage: (document.querySelector('#reviewList .review-card .review-stage') || {}).textContent || '',
    dueLabel: document.getElementById('reviewDueTabCount').textContent,
    allLabel: document.getElementById('reviewAllTabCount').textContent,
  }));
  assert.equal(allTab.cards, 2, `${tag}: full queue shows ${allTab.cards} cards`);
  assert.ok(allTab.stage.includes('다음'), `${tag}: scheduled card lost its next review time ("${allTab.stage}")`);
  assert.equal(allTab.dueLabel, '0', `${tag}: due tab count ${allTab.dueLabel}`);
  assert.equal(allTab.allLabel, '2', `${tag}: all tab count ${allTab.allLabel}`);

  // 5) 수동 추가/제거: 퀴즈 카드의 복습 담기 → 한 번만, 다시 누르면 큐에서 빠진다
  await page.click('#modeQuizBtn');
  await page.waitForTimeout(200);
  const manualId = await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('#questionsList [data-action="toggle-review"]'))
      .find((b) => b.getAttribute('aria-pressed') === 'false');
    return btn ? btn.getAttribute('data-id') : null;
  });
  assert.ok(manualId, `${tag}: no question left to add to the queue manually`);
  await page.click(`#questionsList [data-action="toggle-review"][data-id="${manualId}"]`);
  await page.waitForTimeout(150);
  const manualAdded = await page.evaluate((id) => {
    const store = JSON.parse(localStorage.getItem('study_review_queue_v1'));
    const ids = Object.keys(store.items);
    return { has: !!store.items[id], manual: !!(store.items[id] && store.items[id].manual), count: ids.length, unique: new Set(ids).size };
  }, manualId);
  assert.equal(manualAdded.has, true, `${tag}: manual add did not reach the queue`);
  assert.equal(manualAdded.manual, true, `${tag}: manual entry not marked as manual`);
  assert.equal(manualAdded.count, 3, `${tag}: queue size after manual add ${manualAdded.count}`);
  assert.equal(manualAdded.unique, 3, `${tag}: manual add duplicated a question`);
  await page.click(`#questionsList [data-action="toggle-review"][data-id="${manualId}"]`);
  await page.waitForTimeout(150);
  const manualRemoved = await page.evaluate((id) => {
    const store = JSON.parse(localStorage.getItem('study_review_queue_v1'));
    return { has: !!store.items[id], count: Object.keys(store.items).length, dismissed: !!store.dismissed[id] };
  }, manualId);
  assert.equal(manualRemoved.has, false, `${tag}: manual remove did not leave the queue`);
  assert.equal(manualRemoved.count, 2, `${tag}: queue size after manual remove ${manualRemoved.count}`);
  assert.equal(manualRemoved.dismissed, true, `${tag}: removed question is not held out of the auto queue`);

  await page.evaluate(() => {
    localStorage.removeItem('study_review_queue_v1');
    localStorage.removeItem('study_user_answers_v4');
    localStorage.removeItem('study_bookmarks_v1');
  });
  console.log(`study review ${width}px passed`);
}

// ---- 오늘 허브: 4카드+2요약 · 상태 칩 · 각 페이지 이동 링크 ----
async function checkToday(page, width, tag) {
  await page.waitForFunction(() => document.querySelectorAll('.day-card').length === 4, null, { timeout: 5000 });
  const state = await page.evaluate(() => {
    const chip = (id) => {
      const el = document.getElementById(id);
      return el ? { state: el.getAttribute('data-state'), text: el.textContent.trim() } : null;
    };
    return {
      cards: document.querySelectorAll('.day-card').length,
      summaries: document.querySelectorAll('.summary-card').length,
      chips: ['jobsState', 'cveState', 'studyState', 'aiState', 'weatherState', 'gameState'].map(chip),
      links: Array.from(document.querySelectorAll('a[href]')).map((a) => a.getAttribute('href')),
      jobs: (document.getElementById('jobsCount') || {}).textContent,
      jobsData: typeof TODAY === 'undefined' ? null : TODAY.jobs.count,
      wx: (document.getElementById('wxTemp') || {}).textContent,
      chipsText: Array.from(document.querySelectorAll('.day-chip')).map((c) => c.textContent.trim()),
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    };
  });
  assert.equal(state.cards, 4, `${tag}: ${state.cards} core cards`);
  assert.equal(state.summaries, 2, `${tag}: ${state.summaries} summary cards`);
  for (const chip of state.chips) {
    assert.ok(chip, `${tag}: missing state chip`);
    assert.ok(chip.text.length > 0, `${tag}: empty state chip label`);
    assert.ok(['ok', 'stale', 'none', 'error'].includes(chip.state),
      `${tag}: unknown chip state "${chip.state}"`);
  }
  assert.equal(state.jobs, String(state.jobsData), `${tag}: today-closing count must come from the build data`);
  for (const href of ['index.html', 'cve.html', 'study.html', 'ai.html', 'outfit.html', 'wargame.html', 'clue.html']) {
    assert.ok(state.links.includes(href), `${tag}: ${href} not linked from the hub`);
  }
  assert.equal(state.overflow, 0, `${tag}: horizontal overflow ${state.overflow}px`);

  const weather = await page.evaluate(() => {
    const w = (typeof TODAY === 'undefined' ? null : TODAY.weather) || {};
    return {
      ok: !!w.ok,
      temp: document.getElementById('wxTemp').textContent.trim(),
      state: document.getElementById('weatherState').getAttribute('data-state'),
      label: document.getElementById('weatherState').textContent.trim(),
    };
  });
  if (weather.ok) {
    assert.notEqual(weather.temp, '-', `${tag}: build-time temperature not shown`);
  } else {
    assert.equal(weather.state, 'error', `${tag}: weather failure state not marked`);
  }
}

// ---- 오늘 허브: 브라우저 복습 큐를 실제로 읽어 오늘 복습 수를 보여 준다 ----
async function checkTodayStudyQueue(page, tag) {
  const seeded = await page.evaluate(() => {
    const now = Date.now();
    const items = {};
    for (let i = 0; i < 3; i += 1) {
      items[`smoke-due-${i}`] = { stage: 0, next_review_at: now - 3600000, review_count: 0, last_reviewed_at: 0, added_at: now - 7200000 };
    }
    items['smoke-later'] = { stage: 1, next_review_at: now + 86400000, review_count: 1, last_reviewed_at: now - 1000, added_at: now - 90000000 };
    localStorage.setItem('study_review_queue_v1', JSON.stringify({ version: 1, items, dismissed: {} }));
    localStorage.setItem('study_user_answers_v4', JSON.stringify({ a: { isCorrect: false }, b: { isCorrect: true } }));
    localStorage.setItem('study_bookmarks_v1', JSON.stringify({ c: true }));
    return { due: 3, total: 4 };
  });
  await page.reload({ waitUntil: 'load' });
  await page.waitForFunction(() => {
    const el = document.getElementById('studyCount');
    return !!el && el.textContent.trim() !== '';
  }, null, { timeout: 5000 });
  const view = await page.evaluate(() => ({
    count: document.getElementById('studyCount').textContent.trim(),
    sub: document.getElementById('studySub').textContent.trim(),
    items: document.querySelectorAll('#studyList li').length,
  }));
  assert.equal(view.count, String(seeded.due), `${tag}: due count ${view.count}`);
  assert.ok(view.sub.includes(`전체 큐 ${seeded.total}문항`), `${tag}: queue summary "${view.sub}"`);
  assert.ok(view.items > 0, `${tag}: no queue detail line`);
  await page.evaluate(() => {
    localStorage.removeItem('study_review_queue_v1');
    localStorage.removeItem('study_user_answers_v4');
    localStorage.removeItem('study_bookmarks_v1');
  });
}

// ---- 복습 정답 사전 노출 회귀: 오답 5시간 뒤 같은 탭에서 다시 열어도 이전 정답·해설이 숨겨진다 ----
async function checkStudyReviewTimeline(context, base) {
  const tag = 'study review timeline';
  const page = await context.newPage();
  try {
    await page.clock.install();
    await page.goto(`${base}/study.html`, { waitUntil: 'load' });
    await page.evaluate(() => {
      localStorage.removeItem('study_review_queue_v1');
      localStorage.removeItem('study_user_answers_v4');
      localStorage.removeItem('study_bookmarks_v1');
    });
    await page.reload({ waitUntil: 'load' });
    await page.locator('#questionsList .q-card').first().waitFor({ state: 'attached' });

    // 1) 퀴즈에서 오답 → 복습 큐 자동 등록
    const picked = await page.evaluate(() => {
      const btn = document.querySelector('#questionsList .q-card [data-action="toggle-bookmark"]');
      const id = btn.getAttribute('data-id');
      const q = (window.ALL_QUESTIONS || []).find((x) => x.id === id);
      return { id, answer: q ? q.answer : null, choices: q ? q.options.length : 0 };
    });
    assert.ok(picked.answer, `${tag}: question data missing`);
    const wrongChoice = picked.answer === 1 ? 2 : 1;
    await page.click(`.choice-row[data-id="${picked.id}"][data-choice="${wrongChoice}"]`);
    await page.waitForTimeout(200);

    // 2) 오늘 복습에서 같은 문항을 다시 틀린다 → 이때만 정답·해설이 보인다
    await page.click('#modeReviewBtn');
    await page.waitForTimeout(250);
    await page.click(`#reviewList .review-card[data-review-q="${picked.id}"] .choice-row[data-choice="${wrongChoice}"]`);
    await page.waitForTimeout(250);
    const graded = await page.evaluate((id) => {
      const card = document.querySelector(`#reviewList .review-card[data-review-q="${id}"]`);
      return {
        show: !!card.querySelector('.exp-box.show'),
        result: JSON.parse(localStorage.getItem('study_review_queue_v1')).items[id].last_result,
      };
    }, picked.id);
    assert.equal(graded.result, 'wrong', `${tag}: wrong review result not stored`);
    assert.equal(graded.show, true, `${tag}: grading result must show right after submitting`);

    // 3) 브라우저 시간을 5시간 진행 → 4시간 뒤 재복습 예약이 도래한다
    await page.clock.fastForward(5 * 60 * 60 * 1000);
    await page.waitForTimeout(100);

    // 4) 같은 탭에서 '오늘 복습'을 다시 연다 → 다시 풀 수 있는 카드는 깨끗해야 한다
    await page.click('#modeQuizBtn');
    await page.waitForTimeout(200);
    await page.click('#modeReviewBtn');
    await page.waitForTimeout(250);
    const reopened = await page.evaluate((id) => {
      const card = document.querySelector(`#reviewList .review-card[data-review-q="${id}"]`);
      if (!card) return { found: false };
      return {
        found: true,
        show: !!card.querySelector('.exp-box.show'),
        expText: (card.querySelector('.exp-box') || {}).textContent.trim(),
        answerable: card.querySelectorAll('.choice-row[data-action="review-choice"]').length,
        choices: card.querySelectorAll('.choice-row').length,
        marked: card.querySelectorAll('.choice-row.correct, .choice-row.wrong').length,
        done: card.classList.contains('is-done'),
        due: document.getElementById('reviewDueCount').textContent.trim(),
      };
    }, picked.id);
    assert.equal(reopened.found, true, `${tag}: review card missing after reopening`);
    assert.ok(parseInt(reopened.due, 10) >= 1, `${tag}: card not due after 5 hours (due ${reopened.due})`);
    assert.equal(reopened.show, false, `${tag}: previous answer/explanation leaked before answering again`);
    assert.equal(reopened.marked, 0, `${tag}: previous correct/wrong marks leaked`);
    assert.equal(reopened.done, false, `${tag}: card rendered as already done`);
    assert.equal(reopened.answerable, reopened.choices, `${tag}: choices are not answerable again`);

    // 5) 전체 복습 큐에서도 다시 풀 수 있는 카드는 이전 정답·해설을 숨긴다
    await page.click('#reviewAllTab');
    await page.waitForTimeout(250);
    const allTab = await page.evaluate((id) => {
      const card = document.querySelector(`#reviewList .review-card[data-review-q="${id}"]`);
      if (!card) return { found: false };
      return {
        found: true,
        show: !!card.querySelector('.exp-box.show'),
        answerable: card.querySelectorAll('.choice-row[data-action="review-choice"]').length,
        marked: card.querySelectorAll('.choice-row.correct, .choice-row.wrong').length,
      };
    }, picked.id);
    assert.equal(allTab.found, true, `${tag}: card missing in the full review queue`);
    assert.equal(allTab.show, false, `${tag}: full queue leaked the previous answer`);
    assert.equal(allTab.marked, 0, `${tag}: full queue leaked previous marks`);
    assert.ok(allTab.answerable > 0, `${tag}: full queue card is not answerable`);
    console.log(`${tag} passed`);
  } finally {
    await page.evaluate(() => {
      localStorage.removeItem('study_review_queue_v1');
      localStorage.removeItem('study_user_answers_v4');
      localStorage.removeItem('study_bookmarks_v1');
    }).catch(() => {});
    await page.close();
  }
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

    await checkShellLayout(page, width, name);
    if (name === 'index') await checkIndexLayout(page, width, `index ${width}px`);
    if (name === 'index' && (width === 390 || width === 1280)) await checkIndexWatchlist(page, width);
    if (name === 'ai' && width <= 768) await checkMobileSheet(page, width, `sheet ai ${width}px`);
    if (name === 'ai' && width <= 768) await checkSheetFastToggle(page, width, `sheet fast ai ${width}px`);

    const cards = { index: '#jobsContainer .job-card, #jobsContainer .list-row', ai: '#aiGrid .ai-card', cve: '#cveList .cve-card' };
    if (cards[name]) await page.locator(cards[name]).first().waitFor({ state: 'attached' });

    if (name === 'cve') await checkCvePriorityNav(page, width);
    if (name === 'cve') await checkCveFilters(page, width, `cve filter ${width}px`);
    if (name === 'ai') await checkAiFilters(page, width, `ai filter ${width}px`);
    if (name === 'study') await checkStudyHub(page, width, `study ${width}px`);
    if (name === 'study' && (width === 390 || width === 1280)) await checkStudyReviewQueue(page, width);
    if (name === 'clue') await checkClueGame(page, base, width);
    if (name === 'clue') await checkClueLayout(page, width);
    if (name === 'wargame') await checkWargame(page, width);
    if (name === 'radar') await checkRadar(page, width);
    if (name === 'tools') await checkTools(page, width);
    if (name === 'mission') await checkMissionGame(page, width);
    if (name === 'chart') await checkChartGame(page, base, width);
    if (name === 'outfit') await checkOutfit(page, width);
    if (name === 'pick') await checkPick(page, width);
    if (name === 'today') await checkToday(page, width, `today ${width}px`);
    if (name === 'today' && (width === 390 || width === 1280)) await checkTodayStudyQueue(page, `today queue ${width}px`);

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
    const base = `http://127.0.0.1:${port}`;
    for (const width of [390, 1280]) {
      const context = await browser.newContext({ viewport: { width, height: 900 } });
      for (const name of pages) await checkPage(context, base, name, width);
      await context.close();
    }
    // 320px·768px: 넘침 0, 하단 바 가림 0, 시트/필터 시트 동작(대표 페이지)
    for (const width of [320, 768]) {
      const context = await browser.newContext({ viewport: { width, height: 900 } });
      for (const name of pages) {
        const page = await context.newPage();
        try {
          const response = await page.goto(`${base}/${name}.html`, { waitUntil: 'load' });
          assert.equal(response?.status(), 200, `${name} ${width}px: page must load`);
          await checkShellLayout(page, width, name);
          await checkBottomBar(page, width, name);
          if (name === 'index') await checkIndexLayout(page, width, `index ${width}px`);
          if (name === 'ai') await checkMobileSheet(page, width, `sheet ai ${width}px`);
          if (width === 768 && name === 'ai') await checkSheetFastToggle(page, width, `sheet fast ai ${width}px`);
          if (width === 768 && name === 'cve') await checkCveFilters(page, width, `cve filter ${width}px`);
          if (width === 768 && name === 'wargame') await checkWargame(page, width);
          if (width === 768 && name === 'clue') await checkClueLayout(page, width);
          if (width === 768 && name === 'radar') await checkRadar(page, width);
          if (width === 768 && name === 'tools') await checkTools(page, width);
          if (width === 768 && name === 'outfit') await checkOutfit(page, width);
          if (width === 768 && name === 'pick') await checkPick(page, width);
        } finally {
          await page.close();
        }
        console.log(`${name} ${width}px layout passed`);
      }
      await context.close();
    }

    await checkMissionMobile(browser, base);
    await checkReducedMotion(browser, base);
    const timelineContext = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    await checkStudyReviewTimeline(timelineContext, base);
    await timelineContext.close();
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

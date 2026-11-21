const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const path = require('node:path');
const { chromium } = require('playwright');

const pages = ['index', 'study', 'ai', 'cve', 'wargame', 'tools', 'radar', 'outfit', 'pick', 'clue', 'mission', 'chart'];
const root = path.join(__dirname, '..');

const SHELL_HREFS = ['index.html', 'study.html', 'ai.html', 'cve.html', 'tools.html', 'radar.html',
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
  assert.equal(opened.links.length, 12, `${tag}: sheet lists ${opened.links.length} pages`);
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
  await page.click('#questionsList .q-card .q-mark');
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
    if (name === 'ai' && width <= 768) await checkMobileSheet(page, width, `sheet ai ${width}px`);
    if (name === 'ai' && width <= 768) await checkSheetFastToggle(page, width, `sheet fast ai ${width}px`);

    const cards = { index: '#jobsContainer .job-card, #jobsContainer .list-row', ai: '#aiGrid .ai-card', cve: '#cveList .cve-card' };
    if (cards[name]) await page.locator(cards[name]).first().waitFor({ state: 'attached' });

    if (name === 'cve') await checkCvePriorityNav(page, width);
    if (name === 'cve') await checkCveFilters(page, width, `cve filter ${width}px`);
    if (name === 'ai') await checkAiFilters(page, width, `ai filter ${width}px`);
    if (name === 'study') await checkStudyHub(page, width, `study ${width}px`);
    if (name === 'clue') await checkClueGame(page, base, width);
    if (name === 'mission') await checkMissionGame(page, width);
    if (name === 'chart') await checkChartGame(page, base, width);

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
        } finally {
          await page.close();
        }
        console.log(`${name} ${width}px layout passed`);
      }
      await context.close();
    }

    await checkMissionMobile(browser, base);
    await checkReducedMotion(browser, base);
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

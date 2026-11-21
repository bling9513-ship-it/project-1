const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const path = require('node:path');
const { chromium } = require('playwright');

const pages = ['today', 'index', 'study', 'ai', 'cve', 'wargame', 'tools', 'radar', 'outfit', 'pick', 'clue', 'mission', 'chart', 'ops', 'seat', 'load', 'arcade', 'hangul', 'cards'];
const root = path.join(__dirname, '..');

const SHELL_HREFS = ['today.html', 'index.html', 'study.html', 'ai.html', 'cve.html', 'tools.html', 'radar.html',
  'outfit.html', 'pick.html', 'wargame.html', 'clue.html', 'mission.html', 'chart.html', 'ops.html',
  'seat.html', 'load.html', 'arcade.html', 'hangul.html', 'cards.html'];

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
  //    (1단계에서 같은 카드로 이동해 hash 가 남아 있으면 클릭해도 hashchange 가 없으므로 먼저 비운다)
  await page.evaluate(() => { history.replaceState(null, '', location.pathname + location.search); });
  await setCveFilter(page, 'all', width);
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
      subs: Array.from(document.querySelectorAll('#iaSheet .ia-sheet-sub')).map((g) => g.textContent.trim()),
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
  assert.deepEqual(opened.groups, ['보안·채용', '브리핑·유틸', '데일리·생활', '게임'], `${tag}: sheet groups`);
  assert.deepEqual(opened.subs, ['챌린지', '미니게임'], `${tag}: game sub groups`);
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

    await page.goto(`${base}/seat.html`, { waitUntil: 'load' });
    await page.waitForTimeout(200);
    const demo = await page.evaluate(() => {
      const seat = document.querySelector('.sg-seat[data-demo-seat="0"]');
      const step = (n) => document.querySelector(`#seatGuideSteps .gg-step[data-step="${n}"]`);
      return {
        settled: seat ? seat.classList.contains('is-done') : false,
        checkHidden: document.querySelector('[data-demo-check]').hidden,
        freeHidden: document.querySelector('[data-demo-free]').hidden,
        onStep: document.querySelectorAll('#seatGuideSteps .gg-step.is-on').length,
        lastOn: step(3) ? step(3).classList.contains('is-on') : false,
        doneSteps: document.querySelectorAll('#seatGuideSteps .gg-step.is-done').length,
        transition: getComputedStyle(seat).transitionDuration,
      };
    });
    assert.equal(demo.settled, true, 'reduced motion: seat guide did not settle on the last frame');
    assert.equal(demo.checkHidden, false, 'reduced motion: seat guide check hidden');
    assert.equal(demo.freeHidden, true, 'reduced motion: seat guide availability label still shown');
    assert.equal(demo.onStep, 1, `reduced motion: seat guide active step ${demo.onStep}`);
    assert.equal(demo.lastOn, true, 'reduced motion: seat guide last step not active');
    assert.equal(demo.doneSteps, 2, `reduced motion: seat guide done steps ${demo.doneSteps}`);
    assert.ok(parseFloat(demo.transition) <= 0.02, `reduced motion: seat guide transition ${demo.transition}`);

    await page.goto(`${base}/load.html`, { waitUntil: 'load' });
    await page.waitForTimeout(220);
    const loadDemo = await page.evaluate(() => {
      const fill = document.querySelector('[data-demo-fill]');
      const step = (n) => document.querySelector(`#loadGuideSteps .gg-step[data-step="${n}"]`);
      return {
        crateOff: document.querySelector('[data-demo-crate]').classList.contains('is-off'),
        fillWidth: parseFloat(fill.style.width) || 0,
        shipOff: document.querySelector('[data-demo-ship]').classList.contains('is-off'),
        kg: document.querySelector('[data-demo-kg]').textContent.trim(),
        onStep: document.querySelectorAll('#loadGuideSteps .gg-step.is-on').length,
        lastOn: step(3) ? step(3).classList.contains('is-on') : false,
        deckWidth: document.querySelector('.cart-deck').getBoundingClientRect().width,
        rigTransition: getComputedStyle(document.getElementById('cartRig')).transitionDuration,
      };
    });
    assert.equal(loadDemo.crateOff, false, 'reduced motion: load guide crate hidden');
    assert.ok(loadDemo.fillWidth > 50, `reduced motion: load guide gauge not filled (${loadDemo.fillWidth})`);
    assert.equal(loadDemo.shipOff, false, 'reduced motion: load guide ship chip hidden');
    assert.ok(loadDemo.kg.includes('62'), `reduced motion: load guide weight label ${loadDemo.kg}`);
    assert.equal(loadDemo.onStep, 1, `reduced motion: load guide active step ${loadDemo.onStep}`);
    assert.equal(loadDemo.lastOn, true, 'reduced motion: load guide last step not active');
    assert.ok(loadDemo.rigTransition === '1e-05s' || parseFloat(loadDemo.rigTransition) <= 0.02,
      `reduced motion: cart tilt transition ${loadDemo.rigTransition}`);

    await page.click('#loadLeft');
    await page.waitForTimeout(120);
    const crate = await page.evaluate(() => {
      const node = document.querySelector('#stackLeft .crate');
      return node ? getComputedStyle(node).animationName : 'missing';
    });
    assert.equal(crate, 'none', `reduced motion: crate drop still animating (${crate})`);

    await page.goto(`${base}/hangul.html`, { waitUntil: 'load' });
    await page.waitForTimeout(220);
    const hangulDemo = await page.evaluate(() => ({
      tiles: Array.from(document.querySelectorAll('#guideTiles .hg-demo-tile')).map((node) => node.textContent),
      anims: document.getAnimations().length,
      open: !document.getElementById('guideBody').hidden,
      pop: getComputedStyle(document.querySelector('#guideTiles .hg-demo-tile')).animationName,
    }));
    assert.deepEqual(hangulDemo.tiles, ['가', '지', '가지'],
      `reduced motion: hangul guide not static (${hangulDemo.tiles})`);
    assert.equal(hangulDemo.anims, 0, `reduced motion: hangul guide still animating (${hangulDemo.anims})`);
    assert.equal(hangulDemo.open, true, 'reduced motion: hangul guide hidden on the first visit');
    assert.equal(hangulDemo.pop, 'none', `reduced motion: hangul demo tile animation ${hangulDemo.pop}`);
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
  // 실제 공고 중 '지금 화면에 카드가 있는' 첫 공고를 고른다(자정 직후 마감 처리된 공고는 피한다).
  const realKey = await page.evaluate(() => {
    const keys = new Set(Array.from(document.querySelectorAll('#jobsContainer .job-card')).map((card) => card.dataset.key));
    const job = JOBS.find((item) => item.job_key.indexOf('test:') !== 0 && keys.has(item.job_key));
    return job ? job.job_key : null;
  });
  assert.ok(realKey, `${tag}: no real job card to test the memo`);
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

// ---- AI·CVE 저장(북마크) · 읽음 표시 · 내 목록 필터 · 새로고침 복원 ----
async function pickCollectionChip(page, width, filterButton, kind) {
  if (width >= 1024) {
    await page.click(`#collectionNav .filter-pill[data-collection="${kind}"]`);
    await page.waitForTimeout(100);
    return;
  }
  await page.click(filterButton);
  await page.waitForTimeout(320);
  await page.click(`#collectionNav .filter-pill[data-collection="${kind}"]`);
  await page.waitForTimeout(120);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(320);
}

async function checkMarkedFeed(page, width, config) {
  const tag = `${config.name} saved ${width}px`;
  const { cardSel, keys, summaryId, badgeId, filterButton } = config;
  const visible = async () => parseInt((await page.textContent('#visibleCount')).trim(), 10);
  const readStore = (key) => page.evaluate((k) => {
    const raw = localStorage.getItem(k);
    if (!raw) return null;
    try { return JSON.parse(raw); } catch (e) { return 'invalid'; }
  }, key);
  const chipCount = (kind) => page.evaluate((sel) => document.querySelector(sel).textContent.trim(),
    `#collectionNav [data-collection="${kind}"] .count`);
  const chipPressed = (kind) => page.evaluate((sel) => document.querySelector(sel).getAttribute('aria-pressed'),
    `#collectionNav [data-collection="${kind}"]`);

  await page.evaluate((ks) => ks.forEach((k) => localStorage.removeItem(k)), Object.values(keys));
  await page.reload({ waitUntil: 'load' });
  await page.locator(`${cardSel} [data-mark="saved"]`).first().waitFor({ state: 'attached' });

  const initial = await page.evaluate((sel) => ({
    total: parseInt(document.getElementById('visibleCount').textContent.trim(), 10),
    cards: document.querySelectorAll(sel).length,
    saved: document.querySelector('#collectionNav [data-collection="saved"] .count').textContent.trim(),
    unread: document.querySelector('#collectionNav [data-collection="unread"] .count').textContent.trim(),
    pressed: Array.from(document.querySelectorAll('#collectionNav .filter-pill')).map((b) => b.getAttribute('aria-pressed')),
  }), cardSel);
  assert.equal(initial.cards, initial.total, `${tag}: card count must match the visible count`);
  assert.equal(initial.saved, '0', `${tag}: saved count must start at 0`);
  assert.equal(initial.unread, String(initial.total), `${tag}: every item must start unread`);
  assert.deepEqual(initial.pressed, ['false', 'false'], `${tag}: collection chips must start off`);
  assert.equal((await page.textContent(`#${summaryId}`)).trim(), `저장 0 · 안 읽음 ${initial.total}`,
    `${tag}: result summary`);

  // 1) 카드에서 저장 · 읽음 토글 → 저장소·버튼 상태·카드 표시가 함께 바뀐다
  const firstKey = await page.evaluate((sel) => document.querySelector(sel).getAttribute('data-key'), cardSel);
  assert.ok(firstKey, `${tag}: card has no data-key`);
  await page.locator(`${cardSel} [data-mark="saved"]`).first().click();
  await page.locator(`${cardSel} [data-mark="read"]`).first().click();
  await page.waitForTimeout(80);
  const marked = await page.evaluate((sel) => {
    const card = document.querySelector(sel);
    return {
      savedClass: card.classList.contains('is-saved'),
      readClass: card.classList.contains('is-read'),
      badge: (card.querySelector('.read-badge') || {}).textContent || '',
      savedPressed: card.querySelector('[data-mark="saved"]').getAttribute('aria-pressed'),
      readPressed: card.querySelector('[data-mark="read"]').getAttribute('aria-pressed'),
      savedLabel: card.querySelector('[data-mark="saved"]').textContent.trim(),
      readLabel: card.querySelector('[data-mark="read"]').textContent.trim(),
    };
  }, cardSel);
  assert.equal(marked.savedClass, true, `${tag}: saved card not highlighted`);
  assert.equal(marked.readClass, true, `${tag}: read card not dimmed`);
  assert.equal(marked.badge, '읽음', `${tag}: read badge missing`);
  assert.equal(marked.savedPressed, 'true', `${tag}: save button aria-pressed`);
  assert.equal(marked.readPressed, 'true', `${tag}: read button aria-pressed`);
  assert.equal(marked.savedLabel, '저장됨', `${tag}: save button label`);
  assert.equal(marked.readLabel, '읽음', `${tag}: read button label`);
  assert.equal((await readStore(keys.saved))[firstKey], 1, `${tag}: saved id not persisted with ${keys.saved}`);
  assert.equal((await readStore(keys.read))[firstKey], 1, `${tag}: read id not persisted with ${keys.read}`);
  assert.equal(await chipCount('saved'), '1', `${tag}: saved badge count`);
  assert.equal(await chipCount('unread'), String(initial.total - 1), `${tag}: unread badge count`);
  assert.equal((await page.textContent(`#${summaryId}`)).trim(), `저장 1 · 안 읽음 ${initial.total - 1}`,
    `${tag}: result summary after marking`);

  // 2) '저장한 항목만' → 저장한 한 건만 남는다 (배지·필터 표시 함께)
  await pickCollectionChip(page, width, filterButton, 'saved');
  assert.equal(await chipPressed('saved'), 'true', `${tag}: saved chip aria-pressed`);
  assert.equal(await visible(), 1, `${tag}: saved filter must leave one card`);
  assert.equal(await page.locator(cardSel).count(), 1, `${tag}: saved filter rendered extra cards`);
  assert.equal(await page.evaluate((sel) => document.querySelector(sel).getAttribute('data-key'), cardSel),
    firstKey, `${tag}: saved filter showed another card`);
  assert.equal((await page.textContent(`#${badgeId}`)).trim(), '1', `${tag}: active filter badge`);
  await pickCollectionChip(page, width, filterButton, 'saved');
  assert.equal(await chipPressed('saved'), 'false', `${tag}: saved chip did not toggle off`);
  assert.equal(await visible(), initial.total, `${tag}: saved filter did not restore the feed`);

  // 3) '안 읽은 항목만' → 읽음 처리한 카드는 빠진다
  await pickCollectionChip(page, width, filterButton, 'unread');
  assert.equal(await visible(), initial.total - 1, `${tag}: unread filter count`);
  assert.equal(await page.locator(`${cardSel}.is-read`).count(), 0, `${tag}: read card leaked into the unread filter`);
  assert.equal(await chipPressed('unread'), 'true', `${tag}: unread chip aria-pressed`);
  // 두 칩을 함께 켜면 (저장했고 + 안 읽은) 카드 = 0건 → 빈 상태 안내
  await pickCollectionChip(page, width, filterButton, 'saved');
  assert.equal(await visible(), 0, `${tag}: saved+unread must be empty`);
  assert.equal(await page.evaluate(() => document.getElementById('emptyState').classList.contains('visible')), true,
    `${tag}: empty state not shown`);

  // 4) 초기화 → 두 칩 모두 꺼지고 전체가 돌아온다
  await page.click('#resetFiltersMeta');
  await page.waitForTimeout(120);
  assert.equal(await visible(), initial.total, `${tag}: reset did not restore the feed`);
  assert.equal(await chipPressed('saved'), 'false', `${tag}: reset left the saved chip on`);
  assert.equal(await chipPressed('unread'), 'false', `${tag}: reset left the unread chip on`);

  // 5) 새로고침해도 저장·읽음 표시가 그대로 복원된다
  await page.reload({ waitUntil: 'load' });
  await page.locator(`${cardSel} [data-mark="saved"]`).first().waitFor({ state: 'attached' });
  const restored = await page.evaluate((sel) => {
    const card = document.querySelector(sel);
    return {
      saved: card.classList.contains('is-saved'),
      read: card.classList.contains('is-read'),
      label: card.querySelector('[data-mark="saved"]').textContent.trim(),
    };
  }, cardSel);
  assert.equal(restored.saved, true, `${tag}: saved state lost after reload`);
  assert.equal(restored.read, true, `${tag}: read state lost after reload`);
  assert.equal(restored.label, '저장됨', `${tag}: saved label lost after reload`);
  assert.equal(await chipCount('saved'), '1', `${tag}: saved count lost after reload`);

  // 6) 저장 데이터에 마크업이 섞여 들어와도 화면에 그려지지 않는다(텍스트 처리)
  const injected = await page.evaluate((ks) => {
    localStorage.setItem(ks.saved, JSON.stringify({ 'x"><img src=x onerror=window.__xss=1>': 1, '<script>window.__xss=2</script>': 1 }));
    localStorage.setItem(ks.read, '["not-an-object"]');
    return true;
  }, keys);
  assert.equal(injected, true, `${tag}: could not seed storage`);
  await page.reload({ waitUntil: 'load' });
  await page.locator(`${cardSel} [data-mark="saved"]`).first().waitFor({ state: 'attached' });
  const afterInjection = await page.evaluate((sel) => ({
    xss: typeof window.__xss === 'undefined' ? 0 : window.__xss,
    injectedNodes: document.querySelectorAll(`${sel} img, ${sel} script`).length,
    savedCount: document.querySelector('#collectionNav [data-collection="saved"] .count').textContent.trim(),
  }), cardSel);
  assert.equal(afterInjection.xss, 0, `${tag}: stored markup executed`);
  assert.equal(afterInjection.injectedNodes, 0, `${tag}: stored markup rendered as DOM`);
  assert.equal(afterInjection.savedCount, '0', `${tag}: unrelated stored ids must not be counted`);

  // 7) 저장 → 다시 누르면 해제된다(배지 건수도 함께 돌아온다)
  await page.locator(`${cardSel} [data-mark="saved"]`).first().click();
  await page.waitForTimeout(80);
  assert.equal(await chipCount('saved'), '1', `${tag}: save did not count`);
  await page.locator(`${cardSel} [data-mark="saved"]`).first().click();
  await page.waitForTimeout(80);
  assert.equal(await chipCount('saved'), '0', `${tag}: unsave did not clear the count`);

  await page.evaluate((ks) => ks.forEach((k) => localStorage.removeItem(k)), Object.values(keys));
  await page.reload({ waitUntil: 'load' });
  console.log(tag + ' passed');
}

// ---- ai·cve: 키보드 Enter 로 저장·읽음 토글해도 포커스가 body 로 떨어지지 않는다 ----
// (재렌더 후 같은 항목의 같은 버튼 → 필터로 카드가 사라지면 다음 카드 → 남은 카드가 없으면 필터 칩)
async function readMarkFocus(page) {
  return page.evaluate(() => {
    const el = document.activeElement;
    if (!el || el === document.body) return { body: true };
    const mark = el.closest ? el.closest('[data-mark]') : null;
    const card = el.closest ? el.closest('.ai-card, .cve-card') : null;
    const chip = el.closest ? el.closest('#collectionNav .filter-pill') : null;
    return {
      body: false,
      tag: el.tagName,
      id: el.id || null,
      mark: mark ? mark.getAttribute('data-mark') : null,
      key: card ? card.getAttribute('data-key') : null,
      chip: chip ? chip.getAttribute('data-collection') : null,
      pressed: chip ? chip.getAttribute('aria-pressed') : null,
    };
  });
}

async function checkMarkFocus(page, width, name) {
  const tag = `${name} mark focus ${width}px`;
  const cfg = name === 'ai'
    ? { card: '#aiGrid .ai-card', filterButton: '#aiFilterOpenBtn', open: 'aiFilterOpenBtn', saved: 'ai_saved_v1', read: 'ai_read_v1' }
    : { card: '#cveList .cve-card', filterButton: '#cveFilterOpenBtn', open: 'cveFilterOpenBtn', saved: 'cve_saved_v1', read: 'cve_read_v1' };
  const clear = () => page.evaluate((keys) => keys.forEach((k) => localStorage.removeItem(k)), [cfg.saved, cfg.read]);

  await clear();
  await page.reload({ waitUntil: 'load' });
  await page.locator(cfg.card).first().waitFor({ state: 'attached' });
  const keys = await page.evaluate((sel) => Array.from(document.querySelectorAll(sel))
    .map((card) => card.getAttribute('data-key')), cfg.card);
  assert.ok(keys.length >= 4, `${tag}: need at least 4 cards (${keys.length})`);

  // 1) Enter 로 저장 → 같은 카드의 저장 버튼에 포커스가 남는다
  await page.locator(`${cfg.card} [data-mark="saved"]`).first().focus();
  await page.keyboard.press('Enter');
  await page.waitForTimeout(80);
  let focus = await readMarkFocus(page);
  assert.equal(focus.body, false, `${tag}: focus fell back to body after saving with Enter`);
  assert.equal(focus.mark, 'saved', `${tag}: focus left the save button (${JSON.stringify(focus)})`);
  assert.equal(focus.key, keys[0], `${tag}: focus jumped to another card after saving`);
  assert.equal(await page.evaluate(({ k, key }) => JSON.parse(localStorage.getItem(k) || '{}')[key],
    { k: cfg.saved, key: keys[0] }), 1, `${tag}: save did not persist`);

  // 2) Enter 로 읽음 표시 → 같은 카드의 읽음 버튼에 포커스가 남는다
  await page.locator(`${cfg.card} [data-mark="read"]`).first().focus();
  await page.keyboard.press('Enter');
  await page.waitForTimeout(80);
  focus = await readMarkFocus(page);
  assert.equal(focus.body, false, `${tag}: focus fell back to body after marking read`);
  assert.equal(focus.mark, 'read', `${tag}: focus left the read button (${JSON.stringify(focus)})`);
  assert.equal(focus.key, keys[0], `${tag}: focus jumped to another card after marking read`);
  assert.equal(await page.evaluate(({ k, key }) => JSON.parse(localStorage.getItem(k) || '{}')[key],
    { k: cfg.read, key: keys[0] }), 1, `${tag}: read mark did not persist`);

  // 3) '저장한 항목만' 필터에서 해제 → 사라진 카드 대신 다음 카드의 같은 버튼으로 이동
  await page.locator(`${cfg.card} [data-mark="saved"]`).nth(1).click();
  await page.waitForTimeout(80);
  assert.equal(await page.evaluate(({ k }) => Object.keys(JSON.parse(localStorage.getItem(k) || '{}')).length,
    { k: cfg.saved }), 2, `${tag}: second card not saved`);
  await pickCollectionChip(page, width, cfg.filterButton, 'saved');
  assert.equal(await page.locator(cfg.card).count(), 2, `${tag}: saved filter must show the two saved cards`);
  await page.locator(`${cfg.card} [data-mark="saved"]`).first().focus();
  await page.keyboard.press('Enter');
  await page.waitForTimeout(100);
  assert.equal(await page.locator(cfg.card).count(), 1, `${tag}: card did not leave the saved filter`);
  focus = await readMarkFocus(page);
  assert.equal(focus.body, false, `${tag}: focus fell to body when the card left the filter`);
  assert.equal(focus.mark, 'saved', `${tag}: focus is not on a save button after the card left`);
  assert.equal(focus.key, keys[1], `${tag}: focus did not move to the next card`);

  // 4) 마지막 카드까지 해제 → 활성 필터 칩(모바일은 보이는 필터 초기화 버튼)으로 이동
  await page.keyboard.press('Enter');
  await page.waitForTimeout(100);
  assert.equal(await page.locator(cfg.card).count(), 0, `${tag}: filtered list should be empty`);
  focus = await readMarkFocus(page);
  assert.equal(focus.body, false, `${tag}: focus fell to body when the filtered list emptied`);
  assert.ok(focus.chip === 'saved' || ['resetFilters', 'resetFiltersMeta', cfg.open].includes(focus.id),
    `${tag}: focus went to ${JSON.stringify(focus)} instead of the filter chip or reset button`);

  // 5) '안 읽은 항목만' 필터에서 읽음 표시 → 다음 카드의 읽음 버튼으로 이동
  await clear();
  await page.reload({ waitUntil: 'load' });
  await page.locator(cfg.card).first().waitFor({ state: 'attached' });
  await pickCollectionChip(page, width, cfg.filterButton, 'unread');
  const unreadTotal = await page.locator(cfg.card).count();
  assert.equal(unreadTotal, keys.length, `${tag}: unread filter count ${unreadTotal}`);
  await page.locator(`${cfg.card} [data-mark="read"]`).first().focus();
  await page.keyboard.press('Enter');
  await page.waitForTimeout(100);
  assert.equal(await page.locator(cfg.card).count(), unreadTotal - 1, `${tag}: read card stayed in the unread filter`);
  focus = await readMarkFocus(page);
  assert.equal(focus.body, false, `${tag}: focus fell to body in the unread filter`);
  assert.equal(focus.mark, 'read', `${tag}: focus is not on a read button in the unread filter`);
  assert.equal(focus.key, keys[1], `${tag}: focus did not move to the next card in the unread filter`);

  await clear();
  await page.reload({ waitUntil: 'load' });
  console.log(tag + ' passed');
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

// ---- 오늘 허브: 자정을 넘겨 열면 집계 기준일과 '갱신 대기'를 카드마다 밝힌다 ----
function readTodayMidnightState(page) {
  return page.evaluate(() => {
    const chip = (id) => {
      const el = document.getElementById(id);
      return el ? { state: el.getAttribute('data-state'), text: el.textContent.trim() } : null;
    };
    const notice = document.getElementById('dayNotice');
    return {
      build: typeof TODAY === 'undefined' ? null : (TODAY.build_date_kst || TODAY.today),
      notice: notice ? { hidden: notice.hidden, text: notice.textContent.trim() } : null,
      date: document.getElementById('todayDate').textContent.trim(),
      hero: document.getElementById('heroUpdated').textContent.trim(),
      unit: document.getElementById('jobsUnit').textContent.trim(),
      jobsSub: document.getElementById('jobsSub').textContent.trim(),
      jobsCount: document.getElementById('jobsCount').textContent.trim(),
      jobsData: typeof TODAY === 'undefined' ? null : String(TODAY.jobs.count),
      jobsList: document.getElementById('jobsList').textContent,
      chips: ['jobsState', 'cveState', 'aiState', 'gameState'].map(chip),
    };
  });
}

// 기준일(build)에서 하루 뒤의 KST 날짜 라벨·짧은 라벨과 그날 00:05/23:55 UTC 시각을 만든다.
function kstDayParts(build) {
  const parts = build.split('-').map(Number);
  const next = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2] + 1));
  return {
    parts,
    short: `${parts[1]}/${parts[2]}`,
    nextLabel: `${next.getUTCMonth() + 1}월 ${next.getUTCDate()}일`,
    beforeMidnight: new Date(Date.UTC(parts[0], parts[1] - 1, parts[2], 14, 55)),
    // KST 00:05 = 같은 날짜의 UTC 15:05
    afterMidnight: new Date(Date.UTC(parts[0], parts[1] - 1, parts[2], 15, 5)),
  };
}

// ---- 오늘 허브: 탭을 열어 둔 채 새로고침 없이 자정을 넘겨도 날짜·기준일 표시가 따라온다 ----
//  trigger: 'timer'  → 자정 타이머가 스스로 다시 그린다
//           'focus'  → 잠들었던 탭이 window focus로 깨어날 때
//           'visibilitychange' → 문서가 다시 보일 때
async function checkTodayMidnightWake(browser, base, trigger) {
  const tag = `today midnight no-reload (${trigger})`;
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();
  const read = () => readTodayMidnightState(page);
  try {
    await page.goto(`${base}/today.html`, { waitUntil: 'load' });
    const build = await page.evaluate(() => (typeof TODAY === 'undefined' ? null : (TODAY.build_date_kst || TODAY.today)));
    assert.ok(/^\d{4}-\d{2}-\d{2}$/.test(String(build)), `${tag}: build date missing (${build})`);
    const day = kstDayParts(build);

    // 23:55 KST에 탭을 열어 둔 상태 (이 시점의 화면은 아직 오늘이다)
    await page.clock.install({ time: day.beforeMidnight });
    await page.goto(`${base}/today.html`, { waitUntil: 'load' });
    await page.evaluate(() => { window.__smokeNoReloadMark = 'kept'; });
    let state = await read();
    assert.ok(state.date.includes(`${day.parts[1]}월 ${day.parts[2]}일`), `${tag}: hero date not today (${state.date})`);
    assert.ok(state.notice && state.notice.hidden, `${tag}: day notice shown before midnight`);
    assert.ok(!state.hero.includes('갱신 대기'), `${tag}: hero marked waiting before midnight (${state.hero})`);
    const hadTodayDeadline = state.jobsList.includes('(오늘 마감)');

    // 새로고침 없이 시계만 00:05 KST로 진행한다
    if (trigger === 'timer') {
      await page.clock.runFor(10 * 60 * 1000);
    } else {
      // 타이머는 그대로 두고 시간만 앞으로 민 상태 — 이벤트가 없으면 화면은 아직 어제다
      await page.clock.setSystemTime(day.afterMidnight);
      const before = await read();
      assert.ok(before.date.includes(`${day.parts[1]}월 ${day.parts[2]}일`),
        `${tag}: date rolled over before the wake event (${before.date})`);
      assert.ok(before.notice && before.notice.hidden, `${tag}: day notice shown before the wake event`);
      if (trigger === 'focus') {
        await page.evaluate(() => window.dispatchEvent(new Event('focus')));
      } else {
        await page.evaluate(() => document.dispatchEvent(new Event('visibilitychange')));
      }
    }

    state = await read();
    const builtTime = await page.evaluate(() => (typeof TODAY === 'undefined' ? null
      : (TODAY.built_at_kst || (String(TODAY.built_at || '').match(/(\d{1,2}:\d{2})/) || [])[1] || null)));
    assert.ok(builtTime, `${tag}: build time is missing from the page data`);
    const mark = await page.evaluate(() => window.__smokeNoReloadMark || null);
    assert.equal(mark, 'kept', `${tag}: page was reloaded during the check`);
    assert.ok(state.date.includes(day.nextLabel) && state.date.includes('KST'),
      `${tag}: hero date did not roll over (${state.date})`);
    assert.ok(state.notice && !state.notice.hidden, `${tag}: day notice missing after midnight`);
    assert.ok(state.notice.text.includes(day.nextLabel), `${tag}: notice does not show today's date (${state.notice.text})`);
    assert.ok(state.notice.text.includes(day.short + ' 기준'), `${tag}: notice has no basis date (${state.notice.text})`);
    assert.ok(state.notice.text.includes('갱신 대기'), `${tag}: notice has no waiting label`);
    assert.ok(state.notice.text.includes(builtTime),
      `${tag}: notice does not show the real build time (${state.notice.text})`);
    assert.ok(state.notice.text.includes('다음 갱신 예정'),
      `${tag}: notice has no scheduled refresh label (${state.notice.text})`);
    assert.ok(state.jobsSub.includes(builtTime),
      `${tag}: jobs note does not show the real build time (${state.jobsSub})`);
    assert.ok(state.hero.includes(day.short + ' 기준') && state.hero.includes('갱신 대기'),
      `${tag}: hero meta not marked (${state.hero})`);
    for (const chip of state.chips) {
      assert.ok(chip, `${tag}: missing state chip`);
      assert.equal(chip.state, 'stale', `${tag}: chip not marked waiting (${chip.text})`);
      assert.ok(chip.text.includes(day.short + ' 기준'), `${tag}: chip has no basis date (${chip.text})`);
      assert.ok(chip.text.includes('갱신 대기'), `${tag}: chip has no waiting label (${chip.text})`);
    }
    assert.equal(state.jobsCount, state.jobsData, `${tag}: count changed instead of being labelled`);
    assert.ok(state.unit.includes(day.short + ' 기준'), `${tag}: jobs unit has no basis date (${state.unit})`);
    assert.ok(state.jobsSub.includes('갱신 전'), `${tag}: jobs note missing after midnight (${state.jobsSub})`);
    assert.ok(!state.jobsList.includes('(오늘 마감)'), `${tag}: yesterday's deadline still reads today`);
    if (hadTodayDeadline) {
      assert.ok(state.jobsList.includes('(' + day.short + ' 마감)'),
        `${tag}: deadline not retagged to ${day.short} (${state.jobsList})`);
    }

    // 한 번 더 깨워도 같은 글자가 같은 자리에 남아야 한다(멱등)
    await page.evaluate(() => window.dispatchEvent(new Event('focus')));
    const repeated = await read();
    assert.deepEqual(repeated, state, `${tag}: refresh is not idempotent`);

    console.log(`${tag} passed`);
  } finally {
    await page.close();
    await context.close();
  }
}


// ---- 오늘 허브: 같은 날짜에서 창 포커스·가시성 이벤트가 와도 목록을 다시 그리지 않아 키보드 포커스가 유지된다 ----
async function checkTodayFocusKeep(browser, base) {
  const tag = 'today focus keep';
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();
  try {
    await page.goto(`${base}/today.html`, { waitUntil: 'load' });
    await page.waitForSelector('#gameList a.game-link');
    const before = await page.evaluate(() => {
      const link = document.querySelector('#gameList a.game-link');
      link.setAttribute('data-smoke-mark', 'kept');
      link.focus();
      return {
        href: link.getAttribute('href'),
        count: document.querySelectorAll('#gameList li').length,
        focused: document.activeElement === link,
      };
    });
    assert.equal(before.focused, true, `${tag}: game link could not take focus`);
    assert.ok(before.count > 0, `${tag}: game list is empty`);

    await page.evaluate(() => {
      window.dispatchEvent(new Event('focus'));
      document.dispatchEvent(new Event('visibilitychange'));
      window.dispatchEvent(new Event('pageshow'));
    });
    await page.waitForTimeout(150);

    const after = await page.evaluate(() => {
      const active = document.activeElement;
      return {
        tag: active ? active.tagName : null,
        mark: active && active.getAttribute ? active.getAttribute('data-smoke-mark') : null,
        href: active && active.getAttribute ? active.getAttribute('href') : null,
        count: document.querySelectorAll('#gameList li').length,
        marked: document.querySelectorAll('#gameList a[data-smoke-mark="kept"]').length,
      };
    });
    assert.equal(after.mark, 'kept', `${tag}: focus fell to ${after.tag} on wake`);
    assert.equal(after.href, before.href, `${tag}: focused link changed`);
    assert.equal(after.marked, 1, `${tag}: game list was rebuilt on wake`);
    assert.equal(after.count, before.count, `${tag}: game list entries changed`);
    console.log(`${tag} passed`);
  } finally {
    await page.close();
    await context.close();
  }
}

async function checkTodayMidnight(browser, base) {
  const tag = 'today midnight';
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();
  const read = () => readTodayMidnightState(page);
  try {
    await page.goto(`${base}/today.html`, { waitUntil: 'load' });
    const build = await page.evaluate(() => (typeof TODAY === 'undefined' ? null : (TODAY.build_date_kst || TODAY.today)));
    assert.ok(/^\d{4}-\d{2}-\d{2}$/.test(String(build)), `${tag}: build date missing (${build})`);
    const parts = build.split('-').map(Number);
    const short = `${parts[1]}/${parts[2]}`;

    // 1) 자정 전(23:55 KST): 집계일이 오늘이므로 카운트를 그대로 보여 준다
    await page.clock.install({ time: new Date(Date.UTC(parts[0], parts[1] - 1, parts[2], 14, 55)) });
    await page.reload({ waitUntil: 'load' });
    let state = await read();
    assert.equal(state.build, build, `${tag}: build date lost on reload`);
    assert.ok(state.notice && state.notice.hidden, `${tag}: day notice shown before midnight`);
    assert.equal(state.unit, '건', `${tag}: jobs unit marked before midnight (${state.unit})`);
    assert.ok(!state.jobsSub.includes('갱신 전'), `${tag}: jobs note shown before midnight (${state.jobsSub})`);
    assert.ok(!state.hero.includes('갱신 대기'), `${tag}: hero marked waiting before midnight`);
    const hadTodayDeadline = state.jobsList.includes('(오늘 마감)');
    for (const chip of state.chips) {
      assert.ok(chip, `${tag}: missing state chip`);
      assert.ok(!chip.text.includes('갱신 대기'), `${tag}: chip marked waiting before midnight (${chip.text})`);
    }

    // 2) 자정 후(00:05 KST): 어제 집계임을 카드마다 밝히고, '오늘 마감' 표기를 기준일로 바꾼다
    await page.clock.fastForward(10 * 60 * 1000);
    await page.reload({ waitUntil: 'load' });
    state = await read();
    assert.ok(state.notice && !state.notice.hidden, `${tag}: day notice missing after midnight`);
    assert.ok(state.notice.text.includes(short + ' 기준'), `${tag}: notice has no basis date (${state.notice.text})`);
    assert.ok(state.notice.text.includes('갱신 대기'), `${tag}: notice has no waiting label`);
    const builtTimeReload = await page.evaluate(() => (typeof TODAY === 'undefined' ? null
      : (TODAY.built_at_kst || (String(TODAY.built_at || '').match(/(\d{1,2}:\d{2})/) || [])[1] || null)));
    assert.ok(builtTimeReload && state.notice.text.includes(builtTimeReload),
      `${tag}: notice does not show the real build time (${state.notice.text})`);
    assert.ok(state.notice.text.includes('다음 갱신 예정'),
      `${tag}: notice has no scheduled refresh label (${state.notice.text})`);
    assert.ok(state.hero.includes(short + ' 기준') && state.hero.includes('갱신 대기'),
      `${tag}: hero meta not marked (${state.hero})`);
    for (const chip of state.chips) {
      assert.equal(chip.state, 'stale', `${tag}: chip not marked waiting (${chip.text})`);
      assert.ok(chip.text.includes(short + ' 기준'), `${tag}: chip has no basis date (${chip.text})`);
      assert.ok(chip.text.includes('갱신 대기'), `${tag}: chip has no waiting label (${chip.text})`);
    }
    assert.equal(state.jobsCount, state.jobsData, `${tag}: count changed instead of being labelled`);
    assert.ok(state.unit.includes(short + ' 기준'), `${tag}: jobs unit has no basis date (${state.unit})`);
    assert.ok(state.jobsSub.includes('갱신 전'), `${tag}: jobs note missing after midnight (${state.jobsSub})`);
    assert.ok(!state.jobsList.includes('(오늘 마감)'), `${tag}: yesterday's deadline still reads today`);
    if (hadTodayDeadline) {
      assert.ok(state.jobsList.includes('(' + short + ' 마감)'), `${tag}: deadline not retagged to ${short}`);
    }

    console.log(`${tag} passed`);
  } finally {
    await page.close();
    await context.close();
  }

  // 3) 새로고침 없는 자정 경과: 자정 타이머·focus·visibilitychange 각각의 경로
  await checkTodayMidnightWake(browser, base, 'timer');
  await checkTodayMidnightWake(browser, base, 'focus');
  await checkTodayMidnightWake(browser, base, 'visibilitychange');
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
      const opts = (q && (q.options || q.choices)) || [];
      return { id, answer: q ? q.answer : null, choices: opts.length };
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

// ---- 60초 관제실: 첫 화면 배치(모드·타이머·인력 2명·경보 카드) · PC 좌측 레일/보드 2단 ----
async function checkOpsLayout(page, width) {
  const tag = `ops layout ${width}px`;
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(120);
  const geo = await page.evaluate(() => {
    const box = (el) => {
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { top: r.top, bottom: r.bottom, left: r.left, right: r.right, width: r.width, height: r.height };
    };
    const bar = document.querySelector('.ia-tabbar');
    const limit = bar && getComputedStyle(bar).display !== 'none'
      ? bar.getBoundingClientRect().top : window.innerHeight;
    const cards = Array.from(document.querySelectorAll('#alertBoard .ops-alert')).map(box);
    const guide = document.getElementById('opsGuideCard');
    return {
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      limit,
      mode: box(document.getElementById('modeLive')),
      clock: box(document.getElementById('clockValue')),
      people: Array.from(document.querySelectorAll('.ops-person')).map(box),
      cards,
      boardCols: cards.length > 1 && Math.abs(cards[0].top - cards[1].top) < 2 ? 2 : 1,
      rail: box(document.querySelector('.ops-rail')),
      main: box(document.querySelector('.ops-main')),
      guide: guide ? box(guide) : null,
      guideSteps: document.querySelectorAll('#opsGuideSteps .gg-step').length,
      replay: document.getElementById('opsGuideReplay') ? document.getElementById('opsGuideReplay').textContent.trim() : null,
      demo: !!document.querySelector('[data-demo-alert]') && !!document.querySelector('[data-demo-rec]'),
      count: (document.getElementById('boardCount') || {}).textContent || '',
      guideAnimation: guide ? getComputedStyle(document.querySelector('[data-demo-alert]')).animationName : 'none',
    };
  });
  assert.equal(geo.overflow, 0, `${tag}: horizontal overflow ${geo.overflow}px`);
  assert.equal(geo.cards.length, 6, `${tag}: alert cards ${geo.cards.length}`);
  assert.ok(geo.guide && geo.guide.top >= 0 && geo.guide.bottom <= geo.limit,
    `${tag}: game guide is not in the first screen`);
  assert.equal(geo.guideSteps, 3, `${tag}: guide steps ${geo.guideSteps}`);
  assert.equal(geo.replay, '다시 보기', `${tag}: replay label ${geo.replay}`);
  assert.equal(geo.demo, true, `${tag}: guide demo markup missing`);
  assert.equal(geo.guideAnimation, 'none', `${tag}: guide demo must stop (${geo.guideAnimation})`);
  assert.ok(geo.count.includes('남은') && geo.count.includes('처리'), `${tag}: remaining counter ${geo.count}`);
  assert.ok(geo.mode && geo.mode.top >= 0 && geo.mode.bottom <= geo.limit,
    `${tag}: mode switch is not in the first screen`);
  assert.ok(geo.clock && geo.clock.top >= 0 && geo.clock.bottom <= geo.limit,
    `${tag}: timer is not in the first screen`);
  assert.equal(geo.people.length, 2, `${tag}: responders ${geo.people.length}`);
  for (const person of geo.people) {
    assert.ok(person.top >= 0 && person.bottom <= geo.limit,
      `${tag}: responder card outside the first screen (${Math.round(person.bottom)} > ${Math.round(geo.limit)})`);
  }
  assert.ok(geo.cards[0].top >= 0 && geo.cards[0].bottom <= geo.limit + 1,
    `${tag}: first alert card is cut by the first screen (${Math.round(geo.cards[0].bottom)} > ${Math.round(geo.limit)})`);
  if (width >= 768) {
    assert.ok(geo.rail.right <= geo.main.left + 1, `${tag}: side rail is not left of the board`);
    assert.equal(geo.boardCols, 2, `${tag}: board is not two columns`);
  } else {
    assert.equal(geo.boardCols, width < 420 ? 1 : 2, `${tag}: board columns ${geo.boardCols}`);
  }
  console.log(`${tag} passed`);
}

// ---- 60초 관제실: 연습 배치 → 결과·기록 저장 → 다시 도전 · 실전 60초 타이머 회귀 ----
async function checkOpsGame(page, base, width) {
  const tag = `ops ${width}px`;
  const read = () => page.evaluate(() => ({
    mode: document.getElementById('modeLive').getAttribute('aria-pressed'),
    clock: document.getElementById('clockValue').textContent.trim(),
    cards: Array.from(document.querySelectorAll('#alertBoard .ops-alert')).map((card) => ({
      id: card.dataset.id, spec: card.dataset.spec, state: card.dataset.state,
    })),
    startLabel: document.getElementById('startBtn').textContent.trim(),
    startDisabled: document.getElementById('startBtn').disabled,
    resultHidden: document.getElementById('resultBox').hidden,
    score: document.getElementById('resultScore').textContent.trim(),
    completed: document.getElementById('resultCompleted').textContent.trim(),
    missed: document.getElementById('resultMissed').textContent.trim(),
    downtime: document.getElementById('resultDowntime').textContent.trim(),
    hint: document.getElementById('resultHint').textContent.trim(),
    best: document.getElementById('recBest').textContent.trim(),
    streak: document.getElementById('recStreak').textContent.trim(),
    history: document.querySelectorAll('#recHistory li:not(.is-empty)').length,
    store: JSON.parse(localStorage.getItem('ops_room_stats_v1') || 'null'),
  }));

  await page.evaluate(() => localStorage.removeItem('ops_room_stats_v1'));
  await page.reload({ waitUntil: 'load' });
  await page.locator('#alertBoard .ops-alert').first().waitFor({ state: 'attached' });

  const initial = await read();
  assert.equal(initial.cards.length, 6, `${tag}: six alerts expected`);
  assert.equal(initial.cards.filter((card) => card.spec === 'infra').length, 3, `${tag}: infra alerts`);
  assert.equal(initial.cards.filter((card) => card.spec === 'sec').length, 3, `${tag}: security alerts`);
  assert.equal(initial.mode, 'true', `${tag}: live mode must be the default`);
  assert.equal(initial.startDisabled, false, `${tag}: start button disabled on load`);
  assert.equal(initial.store, null, `${tag}: fresh storage expected`);

  // 1) 연습 모드: 6건을 전문 담당에게 배치 → 결과 카드·기록 저장
  await page.click('#modePractice');
  await page.waitForTimeout(120);
  const practice = await read();
  assert.equal(practice.mode, 'false', `${tag}: practice mode not selected`);
  assert.equal(practice.startDisabled, true, `${tag}: batch must be disabled before six placements`);
  await page.click('#person-infra');
  const firstInfra = practice.cards.find((item) => item.spec === 'infra');
  await page.click(`.ops-alert[data-id="${firstInfra.id}"]`);
  const pulse = await page.evaluate(() => ({
    rec: document.querySelectorAll('#rosterList .ops-person.is-rec').length,
    recBadge: document.querySelectorAll('#rosterList .ops-person.is-rec .ops-person-badge').length,
    suggested: document.querySelectorAll('#alertBoard .ops-alert.is-suggested').length,
    count: document.getElementById('boardCount').textContent.trim(),
    pop: document.querySelectorAll('#alertBoard .ops-alert.is-pop').length,
  }));
  assert.ok(pulse.rec >= 1, `${tag}: specialist responder was not highlighted`);
  assert.ok(pulse.recBadge >= 1, `${tag}: recommendation badge missing`);
  assert.ok(pulse.suggested >= 1, `${tag}: ready alerts of the active specialist were not suggested`);
  assert.ok(pulse.pop >= 1, `${tag}: assigned alert did not pop`);
  assert.ok(pulse.count.includes('남은') && pulse.count.includes('처리'), `${tag}: remaining counter ${pulse.count}`);
  for (const spec of ['infra', 'sec']) {
    await page.click(`#person-${spec}`);
    for (const card of practice.cards.filter((item) => item.spec === spec)) {
      await page.click(`.ops-alert[data-id="${card.id}"]`);
    }
  }
  const placed = await read();
  assert.equal(placed.startDisabled, false, `${tag}: batch not enabled after six placements`);
  assert.ok(placed.cards.every((card) => card.state === 'queued'), `${tag}: placed alerts not queued`);
  await page.click('#startBtn');
  await page.locator('#resultBox:not([hidden])').waitFor({ timeout: 5000 });
  const done = await read();
  assert.ok(Number(done.score) > 0, `${tag}: practice score ${done.score}`);
  assert.equal(done.completed, '6 / 6', `${tag}: practice completed ${done.completed}`);
  assert.equal(done.missed, '0건', `${tag}: practice missed ${done.missed}`);
  assert.ok(done.hint.includes('최적'), `${tag}: hint missing the optimum (${done.hint})`);
  assert.equal(done.best, done.score + '점', `${tag}: today's best not recorded`);
  assert.ok(Number(done.streak.replace('일', '')) >= 1, `${tag}: streak not counted`);
  assert.equal(done.history, 1, `${tag}: history entries ${done.history}`);
  const opsGap = await page.evaluate(() => ({
    text: document.getElementById('resultGapText').textContent.trim(),
    retryTop: document.getElementById('retryBtn').getBoundingClientRect().top,
    gridTop: document.getElementById('resultScore').getBoundingClientRect().top,
    label: document.getElementById('retryBtn').textContent.trim(),
  }));
  assert.ok(opsGap.text.includes('등급') || opsGap.text.includes('최적') || opsGap.text.includes('경보'),
    `${tag}: goal gap missing (${opsGap.text})`);
  assert.ok(opsGap.text.includes('!') || opsGap.text.includes('달성'), `${tag}: goal gap ending ${opsGap.text}`);
  assert.ok(opsGap.retryTop < opsGap.gridTop, `${tag}: retry is not placed first in the result`);
  assert.equal(opsGap.label, '바로 재도전', `${tag}: retry label ${opsGap.label}`);
  assert.ok(done.store && done.store.days, `${tag}: stats not saved`);
  assert.equal(done.store.days[Object.keys(done.store.days)[0]].plays, 1, `${tag}: plays not counted`);
  assert.equal(done.store.streak.count, 1, `${tag}: stored streak`);
  assert.equal(done.store.history.length, 1, `${tag}: stored history`);

  // 2) 다시 도전: 보드·결과 초기화, 기록은 유지
  await page.click('#retryBtn');
  await page.waitForTimeout(120);
  const reset = await read();
  assert.equal(reset.resultHidden, true, `${tag}: result card stayed after retry`);
  assert.ok(reset.cards.every((card) => card.state === 'ready'), `${tag}: board not reset`);
  assert.equal(reset.startDisabled, true, `${tag}: batch enabled on a fresh board`);
  assert.equal(reset.best, done.score + '점', `${tag}: today's best lost after retry`);

  // 3) 실전: 60초 타이머가 끝나면 결과·기록이 남는다
  const liveContext = await page.context().browser().newContext({ viewport: { width, height: 900 } });
  const live = await liveContext.newPage();
  const liveErrors = [];
  live.on('pageerror', (error) => liveErrors.push(error.message));
  try {
    await live.clock.install();
    await live.goto(`${base}/ops.html`, { waitUntil: 'load' });
    await live.locator('#alertBoard .ops-alert').first().waitFor({ state: 'attached' });
    await live.evaluate(() => localStorage.removeItem('ops_room_stats_v1'));
    await live.reload({ waitUntil: 'load' });
    await live.locator('#alertBoard .ops-alert').first().waitFor({ state: 'attached' });
    await live.click('#startBtn');
    await live.clock.runFor(1000);

    const assignReady = async () => {
      const ready = await live.evaluate(() => Array.from(document.querySelectorAll('#alertBoard .ops-alert'))
        .filter((card) => card.dataset.state === 'ready')
        .map((card) => ({ id: card.dataset.id, spec: card.dataset.spec })));
      for (const item of ready) {
        await live.click(`#person-${item.spec}`);
        await live.click(`.ops-alert[data-id="${item.id}"]`);
      }
      return ready.length;
    };

    const firstBatch = await assignReady();
    assert.ok(firstBatch >= 3, `${tag}: only ${firstBatch} alerts arrived in the first second`);
    await live.clock.runFor(6000);
    const secondBatch = await assignReady();
    assert.ok(firstBatch + secondBatch === 6, `${tag}: ${firstBatch + secondBatch} alerts assigned, expected 6`);

    await live.clock.runFor(53000);
    const end = await live.evaluate(() => ({
      clock: document.getElementById('clockValue').textContent.trim(),
      hidden: document.getElementById('resultBox').hidden,
      score: Number(document.getElementById('resultScore').textContent.trim()),
      completed: document.getElementById('resultCompleted').textContent.trim(),
      missed: document.getElementById('resultMissed').textContent.trim(),
      states: Array.from(document.querySelectorAll('#alertBoard .ops-alert')).map((card) => card.dataset.state),
      store: JSON.parse(localStorage.getItem('ops_room_stats_v1') || 'null'),
    }));
    assert.equal(end.hidden, false, `${tag}: result not shown when the clock ran out`);
    assert.equal(end.clock, '0.0', `${tag}: clock ${end.clock} after 60 seconds`);
    assert.equal(end.completed.split('/')[1].trim(), '6', `${tag}: summary "${end.completed}"`);
    assert.ok(end.missed.endsWith('건'), `${tag}: missed summary "${end.missed}"`);
    assert.ok(end.states.every((state) => state === 'done' || state === 'missed'),
      `${tag}: alerts left mid-run (${end.states})`);
    assert.ok(end.score > 0, `${tag}: live score ${end.score}`);
    assert.ok(end.store && end.store.history.length >= 1, `${tag}: live run not stored`);
    assert.deepEqual(liveErrors, [], `${tag}: browser errors`);
  } finally {
    await liveContext.close();
  }
  console.log(`${tag} passed`);
}


// ---- 막차 자리 배치: 같은 규칙(대기 승객 탭 → 좌석 탭 / 앉은 승객 탭 → 좌석 탭)으로 최소 이동 계획을 만든다 ----
function seatPlan(start, solution) {
  const seats = start.slice();
  const target = {};
  solution.forEach((pid, i) => { if (pid) target[pid] = i; });
  const steps = [];
  const same = () => seats.every((value, i) => value === solution[i]);
  for (let guard = 0; guard < 40 && !same(); guard += 1) {
    let moved = false;
    for (const pid of Object.keys(target)) {
      if (seats.indexOf(pid) !== -1) continue;
      const seat = target[pid];
      if (seats[seat] === null) {
        steps.push(['wait', pid]); steps.push(['seat', seat]);
        seats[seat] = pid; moved = true; break;
      }
    }
    if (moved) continue;
    for (let i = 0; i < seats.length && !moved; i += 1) {
      const pid = seats[i];
      if (!pid) continue;
      const seat = target[pid];
      if (seat !== i && seats[seat] === null) {
        steps.push(['seat', i]); steps.push(['seat', seat]);
        seats[seat] = pid; seats[i] = null; moved = true;
      }
    }
    if (moved) continue;
    for (let i = 0; i < seats.length && !moved; i += 1) {
      const pid = seats[i];
      if (!pid) continue;
      const j = target[pid];
      const other = seats[j];
      if (other && i !== j && target[other] === i) {
        steps.push(['seat', i]); steps.push(['seat', j]);
        seats[i] = other; seats[j] = pid; moved = true;
      }
    }
    if (moved) continue;
    for (let i = 0; i < seats.length && !moved; i += 1) {
      const pid = seats[i];
      if (!pid) continue;
      const j = target[pid];
      if (j !== i && seats[j] !== null) {
        steps.push(['seat', i]); steps.push(['seat', j]);
        seats[i] = seats[j]; seats[j] = pid; moved = true;
      }
    }
    if (!moved) break;
  }
  return { steps, seats };
}

// ---- 막차 자리 배치: 첫 화면(조건 요약·4×4 좌석·대기 승객) · PC 레일/보드 2단 ----
async function checkSeatLayout(page, width) {
  const tag = `seat layout ${width}px`;
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(120);

  // 게임 방법: 3단계 데모가 처음 한 번만 움직이고 마지막 장면에서 멈춘다(무한 루프 없음).
  const guide = await page.evaluate(() => ({
    exists: !!document.querySelector('#guideCard .gg-card'),
    replay: document.getElementById('seatGuideReplay') ? document.getElementById('seatGuideReplay').textContent.trim() : null,
    steps: document.querySelectorAll('#seatGuideSteps .gg-step').length,
    demo: !!document.querySelector('.sg-seat[data-demo-seat="0"]'),
    pax: !!document.querySelector('[data-demo-pax]'),
    check: !!document.querySelector('[data-demo-check]'),
    animation: getComputedStyle(document.querySelector('.sg-seat')).animationName,
    seen: !!localStorage.getItem('seat_demo_seen_v1'),
  }));
  assert.ok(guide.exists, `${tag}: game guide missing`);
  assert.equal(guide.replay, '다시 보기', `${tag}: replay label ${guide.replay}`);
  assert.equal(guide.steps, 3, `${tag}: guide steps ${guide.steps}`);
  assert.ok(guide.demo && guide.pax && guide.check, `${tag}: guide demo markup missing`);
  assert.equal(guide.animation, 'none', `${tag}: guide demo must not loop (${guide.animation})`);
  assert.equal(guide.seen, true, `${tag}: guide seen flag not stored`);

  // 데모는 1회 재생 후 3단계에서 정지한다. '다시 보기'는 1단계부터 다시 재생한다.
  await page.waitForTimeout(2300);
  const settled = await page.evaluate(() => ({
    on: Array.from(document.querySelectorAll('#seatGuideSteps .gg-step.is-on')).map((el) => el.dataset.step),
    done: document.querySelectorAll('#seatGuideSteps .gg-step.is-done').length,
    note: document.getElementById('seatGuideNote').textContent.trim(),
    seatDone: document.querySelector('.sg-seat[data-demo-seat="0"]').classList.contains('is-done'),
  }));
  assert.deepEqual(settled.on, ['3'], `${tag}: guide did not stop on the last step (${settled.on})`);
  assert.equal(settled.done, 2, `${tag}: guide completed steps ${settled.done}`);
  assert.equal(settled.seatDone, true, `${tag}: guide last frame not settled`);
  assert.ok(settled.note.includes('초록 체크'), `${tag}: last step note missing (${settled.note})`);

  await page.click('#seatGuideReplay');
  await page.waitForTimeout(120);
  const replay = await page.evaluate(() => ({
    on: Array.from(document.querySelectorAll('#seatGuideSteps .gg-step.is-on')).map((el) => el.dataset.step),
  }));
  assert.deepEqual(replay.on, ['1'], `${tag}: replay did not restart from step 1 (${replay.on})`);
  await page.waitForTimeout(2300);

  const geo = await page.evaluate(() => {
    const box = (el) => {
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { top: r.top, bottom: r.bottom, left: r.left, right: r.right, width: r.width, height: r.height };
    };
    const bar = document.querySelector('.ia-tabbar');
    const limit = bar && getComputedStyle(bar).display !== 'none'
      ? bar.getBoundingClientRect().top : window.innerHeight;
    const cells = Array.from(document.querySelectorAll('#seatGrid .seat-cell')).map(box);
    return {
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      limit,
      mode: box(document.getElementById('modeDaily')),
      hint: box(document.getElementById('seatStatus')),
      cond: box(document.getElementById('condCard')),
      cells,
      rows: new Set(cells.map((cell) => Math.round(cell.top))).size,
      gridCols: cells.length > 1 && Math.abs(cells[0].top - cells[1].top) < 2 ? 4 : 1,
      wait: box(document.getElementById('waitCard')),
      firstWait: box(Array.from(document.querySelectorAll('.wait-card')).find((card) => !card.hidden) || null),
      status: box(document.getElementById('statusCard')),
      main: box(document.querySelector('.seat-main')),
    };
  });
  assert.equal(geo.overflow, 0, `${tag}: horizontal overflow ${geo.overflow}px`);
  assert.equal(geo.cells.length, 16, `${tag}: seats ${geo.cells.length}`);
  assert.equal(geo.gridCols, 4, `${tag}: seat grid is not four columns`);
  assert.equal(geo.rows, 4, `${tag}: seat grid rows ${geo.rows}`);
  for (const cell of geo.cells) {
    assert.ok(cell.width >= 40, `${tag}: seat cell too narrow (${Math.round(cell.width)}px)`);
  }
  if (width <= 768) {
    assert.ok(geo.mode && geo.mode.top >= 0 && geo.mode.bottom <= geo.limit,
      `${tag}: mode switch is not in the first screen`);
    assert.ok(geo.hint && geo.hint.top >= 0 && geo.hint.bottom <= geo.limit,
      `${tag}: selection hint is not in the first screen`);
    assert.ok(geo.cond && geo.cond.bottom <= geo.limit, `${tag}: condition summary is cut by the first screen`);
    assert.ok(geo.cells[15].bottom <= geo.limit + 1,
      `${tag}: seat grid is cut by the first screen (${Math.round(geo.cells[15].bottom)} > ${Math.round(geo.limit)})`);
    assert.ok(geo.firstWait, `${tag}: waiting passengers are not rendered`);
    assert.ok(geo.firstWait.top < geo.limit + 90,
      `${tag}: waiting passengers are far below the first screen (${Math.round(geo.firstWait.top)} > ${Math.round(geo.limit)})`);
  } else {
    assert.ok(geo.status.right <= geo.main.left + 1, `${tag}: side rail is not left of the board`);
    assert.equal(geo.gridCols, 4, `${tag}: board is not four columns`);
  }
  console.log(`${tag} passed`);
}

// ---- 막차 자리 배치: 오늘 퍼즐을 par 수로 클리어 → 기록 저장 · 다시 하기 · 자리 교환 · 연습 스테이지 ----
async function checkSeatGame(page, width) {
  const tag = `seat game ${width}px`;
  await page.evaluate(() => localStorage.removeItem('seat_puzzle_stats_v1'));
  await page.reload({ waitUntil: 'load' });
  await page.locator('#seatGrid .seat-cell').first().waitFor({ state: 'attached' });

  const data = await page.evaluate(() => JSON.parse(document.getElementById('seatData').textContent));
  const todayKey = await page.evaluate(() => {
    const t = new Date(Date.now() + 9 * 3600000);
    const p = (n) => String(n).padStart(2, '0');
    return `${t.getUTCFullYear()}-${p(t.getUTCMonth() + 1)}-${p(t.getUTCDate())}`;
  });
  const ordinal = Math.floor(Date.parse(todayKey + 'T00:00:00Z') / 86400000);
  const puzzle = data.daily[ordinal % data.daily.length];
  const waitingCount = puzzle.start.filter((value) => !value).length > 0
    ? puzzle.passengers.filter((person) => puzzle.start.indexOf(person.id) === -1).length : 0;

  const read = () => page.evaluate(() => {
    const store = JSON.parse(localStorage.getItem('seat_puzzle_stats_v1') || 'null');
    return {
      moves: document.getElementById('moveValue').textContent.trim(),
      par: document.getElementById('parValue').textContent.trim(),
      resultHidden: document.getElementById('resultBox').hidden,
      stars: document.querySelectorAll('#resultStars .star.is-on').length,
      eff: document.getElementById('resultEff').textContent.trim(),
      recToday: document.getElementById('recToday').textContent.trim(),
      recClears: document.getElementById('recClears').textContent.trim(),
      condValue: document.getElementById('condValue').textContent.trim(),
      title: document.getElementById('boardTitle').textContent.trim(),
      practiceHidden: document.getElementById('practiceWrap').hidden,
      store,
    };
  });

  const initial = await read();
  assert.equal(initial.moves, '0', `${tag}: moves on load ${initial.moves}`);
  assert.equal(initial.par, String(puzzle.par), `${tag}: par ${initial.par} vs ${puzzle.par}`);
  assert.equal(initial.resultHidden, true, `${tag}: result shown before playing`);
  assert.equal(initial.store, null, `${tag}: fresh storage expected`);
  assert.equal(initial.practiceHidden, true, `${tag}: practice list shown in daily mode`);
  assert.ok(waitingCount >= 1, `${tag}: no waiting passenger`);

  // 보드 즉시 피드백: 승객을 고르면 앉을 수 있는 빈 좌석만 「가능」으로 켜지고, 앉은 승객은 조건 칩이 초록으로 바뀐다.
  const feedback = await page.evaluate(() => {
    const waiting = Array.from(document.querySelectorAll('.wait-card')).find((card) => !card.hidden && !card.classList.contains('is-seated'));
    if (waiting) waiting.click();
    const targets = Array.from(document.querySelectorAll('#seatGrid .seat-cell.is-target'));
    return {
      clicked: !!waiting,
      targets: targets.length,
      targetsEmpty: targets.every((cell) => !cell.classList.contains('is-occupied')),
      avail: targets.filter((cell) => !!cell.querySelector('.sc-avail')).length,
      swaps: document.querySelectorAll('#seatGrid .seat-cell.is-swap').length,
      seatedCards: document.querySelectorAll('.wait-card.is-seated').length,
      seatedChips: document.querySelectorAll('.wait-card.is-seated .chip.is-ok').length,
      seatedBadges: document.querySelectorAll('.wait-card.is-seated .wait-state:not([hidden])').length,
    };
  });
  assert.ok(feedback.clicked, `${tag}: no waiting passenger to pick`);
  assert.ok(feedback.targets > 0, `${tag}: selecting a passenger did not highlight any seat`);
  assert.equal(feedback.targetsEmpty, true, `${tag}: occupied seats were marked as available`);
  assert.equal(feedback.avail, feedback.targets, `${tag}: availability labels ${feedback.avail}/${feedback.targets}`);
  await page.waitForTimeout(220);
  const availVisible = await page.evaluate(() => Array.from(document.querySelectorAll('#seatGrid .seat-cell.is-target .sc-avail'))
    .filter((node) => parseFloat(getComputedStyle(node).opacity) > 0.9).length);
  assert.equal(availVisible, feedback.targets, `${tag}: availability labels not visible (${availVisible}/${feedback.targets})`);
  if (puzzle.start.some(Boolean)) {
    assert.ok(feedback.seatedCards > 0, `${tag}: seated passengers missing from the list`);
    assert.ok(feedback.seatedChips > 0, `${tag}: satisfied conditions not marked green`);
    assert.equal(feedback.seatedBadges, feedback.seatedCards, `${tag}: seated badges ${feedback.seatedBadges}/${feedback.seatedCards}`);
  }
  await page.evaluate(() => {
    const selected = document.querySelector('.wait-card.is-selected');
    if (selected) selected.click();
  });

  const { steps, seats } = seatPlan(puzzle.start, puzzle.solution);
  assert.deepEqual(seats, puzzle.solution, `${tag}: planner did not reach the solution`);
  assert.equal(steps.length / 2, puzzle.par, `${tag}: plan ${steps.length / 2} moves vs par ${puzzle.par}`);

  for (const [kind, value] of steps) {
    if (kind === 'wait') await page.click(`.wait-card[data-pid="${value}"]`);
    else await page.click(`.seat-cell[data-seat="${value}"]`);
  }
  await page.locator('#resultBox:not([hidden])').waitFor({ timeout: 5000 });
  const done = await read();
  assert.equal(done.moves, String(puzzle.par), `${tag}: cleared in ${done.moves} moves`);
  assert.equal(done.stars, 3, `${tag}: stars ${done.stars}`);
  assert.equal(done.eff, '100%', `${tag}: efficiency ${done.eff}`);
  assert.ok(done.store && done.store.days && done.store.days[todayKey],
    `${tag}: daily record missing`);
  assert.equal(done.store.days[todayKey].moves, puzzle.par, `${tag}: stored moves`);
  assert.equal(done.store.days[todayKey].cleared, true, `${tag}: record not marked cleared`);
  assert.equal(done.store.best[puzzle.id], puzzle.par, `${tag}: best move not stored`);
  assert.equal(done.store.totals.clears, 1, `${tag}: clears ${done.store.totals.clears}`);
  assert.equal(done.store.totals.plays, 1, `${tag}: plays ${done.store.totals.plays}`);
  assert.equal(done.store.streak.count, 1, `${tag}: streak ${done.store.streak.count}`);
  assert.equal(done.recToday, puzzle.par + '수', `${tag}: today's record ${done.recToday}`);
  const gap = await page.evaluate(() => ({
    text: document.getElementById('resultGapText').textContent.trim(),
    retryTop: document.getElementById('retryBtn').getBoundingClientRect().top,
    gridTop: document.getElementById('resultStars').getBoundingClientRect().top,
    retryLabel: document.getElementById('retryBtn').textContent.trim(),
  }));
  assert.ok(gap.text.includes('별 3개'), `${tag}: goal gap missing (${gap.text})`);
  assert.ok(gap.retryTop < gap.gridTop, `${tag}: retry is not placed before the score details`);
  assert.equal(gap.retryLabel, '다시 도전', `${tag}: retry label ${gap.retryLabel}`);

  // 조건 달성 초록 체크 · 착석 팝 · 선택 펄스 · 클리어 축하 연출이 살아 있는지
  const motion = await page.evaluate(() => {
    const probe = (cls) => {
      const cell = document.querySelector('#seatGrid .seat-cell');
      cell.classList.add(cls);
      const name = getComputedStyle(cell).animationName;
      cell.classList.remove(cls);
      return name;
    };
    return {
      pulse: probe('is-selected'),
      landing: probe('is-landing'),
      okSeats: document.querySelectorAll('#seatGrid .seat-cell.is-ok').length,
      checks: document.querySelectorAll('#seatGrid .seat-cell.is-ok .sc-check').length,
      resultNew: document.getElementById('resultBox').classList.contains('is-new'),
      coachGlow: document.querySelector('.coach').classList.contains('is-cleared'),
      starsPop: document.querySelectorAll('#resultStars .star.is-pop').length,
      condOk: document.querySelectorAll('#condList .cond-row.is-ok').length,
    };
  });
  assert.ok(motion.pulse !== 'none', `${tag}: selected pulse animation missing (${motion.pulse})`);
  assert.ok(motion.landing !== 'none', `${tag}: seat landing animation missing (${motion.landing})`);
  assert.equal(motion.okSeats, puzzle.passengers.length, `${tag}: satisfied seats ${motion.okSeats}`);
  assert.equal(motion.checks, motion.okSeats, `${tag}: seat check marks ${motion.checks}`);
  assert.equal(motion.resultNew, true, `${tag}: clear celebration not triggered`);
  assert.equal(motion.coachGlow, true, `${tag}: board glow not triggered`);
  assert.equal(motion.starsPop, 3, `${tag}: star pop ${motion.starsPop}`);
  assert.ok(motion.condOk > 0, `${tag}: no condition marked complete`);

  // 다시 하기: 보드·이동 초기화, 기록 유지
  await page.click('#retryBtn');
  await page.waitForTimeout(120);
  const reset = await read();
  assert.equal(reset.moves, '0', `${tag}: moves after retry ${reset.moves}`);
  assert.equal(reset.resultHidden, true, `${tag}: result stayed after retry`);
  assert.equal(reset.recToday, puzzle.par + '수', `${tag}: today's record lost after retry`);

  // 앉은 승객 두 명을 탭하면 1수로 자리를 바꾼다
  const pair = await page.evaluate(() => {
    const cells = Array.from(document.querySelectorAll('#seatGrid .seat-cell.is-occupied'));
    return cells.length >= 2 ? [Number(cells[0].dataset.seat), Number(cells[1].dataset.seat)] : null;
  });
  assert.ok(pair, `${tag}: not enough seated passengers for a swap`);
  const names = await page.evaluate(([a, b]) => [
    document.querySelector(`.seat-cell[data-seat="${a}"] .sc-name`).textContent,
    document.querySelector(`.seat-cell[data-seat="${b}"] .sc-name`).textContent,
  ], pair);
  await page.click(`.seat-cell[data-seat="${pair[0]}"]`);
  assert.equal(await page.evaluate(() => document.querySelectorAll('.seat-cell.is-selected').length), 1,
    `${tag}: picking a seated passenger did not select it`);
  await page.click(`.seat-cell[data-seat="${pair[1]}"]`);
  const swapped = await page.evaluate(([a, b]) => ({
    moves: document.getElementById('moveValue').textContent.trim(),
    names: [
      document.querySelector(`.seat-cell[data-seat="${a}"] .sc-name`).textContent,
      document.querySelector(`.seat-cell[data-seat="${b}"] .sc-name`).textContent,
    ],
  }), pair);
  assert.equal(swapped.moves, '1', `${tag}: swap counted ${swapped.moves} moves`);
  assert.equal(swapped.names[0], names[1], `${tag}: swap did not move the passenger`);
  assert.equal(swapped.names[1], names[0], `${tag}: swap did not exchange seats`);

  // 연습 모드: 스테이지 목록 → 다른 스테이지 로드
  await page.click('#modePractice');
  await page.locator('#practiceWrap:not([hidden])').waitFor({ timeout: 5000 });
  const practice = await page.evaluate(() => ({
    stages: document.querySelectorAll('.stage').length,
    current: document.querySelectorAll('.stage.is-current').length,
    title: document.getElementById('boardTitle').textContent.trim(),
    par: document.getElementById('parValue').textContent.trim(),
    moves: document.getElementById('moveValue').textContent.trim(),
  }));
  assert.equal(practice.stages, data.practice.length, `${tag}: practice stages ${practice.stages}`);
  assert.equal(practice.current, 1, `${tag}: current stage ${practice.current}`);
  assert.equal(practice.par, String(data.practice[0].par), `${tag}: practice par ${practice.par}`);
  assert.equal(practice.moves, '0', `${tag}: practice moves ${practice.moves}`);
  await page.click(`.stage[data-pid="${data.practice[1].id}"]`);
  await page.waitForTimeout(120);
  const switched = await page.evaluate(() => ({
    title: document.getElementById('boardTitle').textContent.trim(),
    par: document.getElementById('parValue').textContent.trim(),
  }));
  assert.equal(switched.title, data.practice[1].title, `${tag}: stage switch title ${switched.title}`);
  assert.equal(switched.par, String(data.practice[1].par), `${tag}: stage switch par ${switched.par}`);

  console.log(`${tag} passed`);
}


// ---- 한 번 더 싣기: 게임 방법 3단계 데모 · 손수레 보드 · 첫 화면 ---- 
// 각 회차에서 '표기 상한(hi)까지 실어도 안전한' 좌/우 배치를 고른다.
function loadPlan(ch) {
  return ch.batches.map((tripBoxes) => {
    let L = 0;
    let R = 0;
    const sides = [];
    for (const box of tripBoxes) {
      const options = ['left', 'right'].map((side) => {
        const nl = L + (side === 'left' ? box.hi : 0);
        const nr = R + (side === 'right' ? box.hi : 0);
        return { side, nl, nr, ok: nl + nr <= ch.limit && Math.abs(nl - nr) <= ch.tilt };
      }).filter((option) => option.ok);
      if (!options.length) break;
      options.sort((a, b) => Math.abs(a.nl - a.nr) - Math.abs(b.nl - b.nr));
      L = options[0].nl; R = options[0].nr;
      sides.push(options[0].side);
    }
    return sides;
  });
}

// 별 3개를 노리는 계획: 박스는 앞에서부터만 실을 수 있으므로 '앞 k개를 좌/우로 나눠 싣고 배송'하는
// 모든 조합 중 회차 점수(합계 × 균형 배율)가 가장 큰 것을 고른다.
function perfectLoadPlan(ch) {
  const tiers = [[0.9, 1.5], [0.78, 1.25], [0.62, 1], [0, 0.75]];
  const balance = (l, r) => {
    if (l + r <= 0) return 1;
    const ratio = 1 - Math.abs(l - r) / (l + r);
    for (const [min, mult] of tiers) if (ratio >= min) return mult;
    return 0.75;
  };
  const streakMult = (n) => Math.round((1 + Math.min(n, 5) * 0.1) * 100) / 100;
  let streak = 0;
  let total = 0;
  const plan = ch.batches.map((trip) => {
    let best = null;
    for (let k = 1; k <= trip.length; k += 1) {
      for (let mask = 0; mask < (1 << k); mask += 1) {
        let l = 0;
        let r = 0;
        let score = 0;
        let safe = true;
        const sides = [];
        trip.slice(0, k).forEach((box, i) => {
          const left = !!(mask & (1 << i));
          if (left) l += box.kg; else r += box.kg;
          score += box.score;
          sides.push(left ? 'left' : 'right');
          // 게임은 상자를 실을 때마다 한도·균형을 검사하므로 중간 상태도 안전해야 한다.
          if (l + r > ch.limit || Math.abs(l - r) > ch.tilt) safe = false;
        });
        if (!safe) continue;
        const value = score * balance(l, r);
        if (!best || value > best.value + 1e-9) best = { value, sides };
      }
    }
    if (!best) return { sides: [], gain: 0 };
    let l = 0;
    let r = 0;
    let score = 0;
    best.sides.forEach((side, i) => {
      if (side === 'left') l += trip[i].kg; else r += trip[i].kg;
      score += trip[i].score;
    });
    const gain = Math.round(score * balance(l, r) * streakMult(streak));
    streak += 1;
    total += gain;
    return { sides: best.sides, gain };
  });
  return { plan, total };
}

async function readLoadState(page) {
  return page.evaluate(() => {
    const dayBadge = document.getElementById('dayBadge');
    return {
      title: document.getElementById('boardTitle').textContent.trim(),
      trip: document.getElementById('tripValue').textContent.trim(),
      total: document.getElementById('totalValue').textContent.trim(),
      boxName: document.getElementById('boxName').textContent.trim(),
      cart: Number(document.getElementById('cartTotal').textContent),
      crates: document.querySelectorAll('.crate').length,
      preview: document.getElementById('shipPreview').textContent.trim(),
      tripScore: document.getElementById('tripScore').getAttribute('data-value'),
      tripHidden: document.getElementById('tripPanel').hidden,
      resultHidden: document.getElementById('resultBox').hidden,
      resultTotal: document.getElementById('resultTotal').getAttribute('data-value'),
      resultBadge: document.getElementById('resultBadge').textContent.trim(),
      resultToday: document.getElementById('resultToday').textContent.trim(),
      resultTodayLabel: document.getElementById('resultTodayLabel').textContent.trim(),
      dayBadge: dayBadge ? { hidden: dayBadge.hidden, text: dayBadge.textContent.trim() } : null,
      recBest: document.getElementById('recBest').textContent.trim(),
      recPlays: document.getElementById('recPlays').textContent.trim(),
      recordDate: document.getElementById('recordDate').textContent.trim(),
      practiceHidden: document.getElementById('practiceWrap').hidden,
      store: JSON.parse(localStorage.getItem('load_cart_stats_v1') || 'null'),
    };
  });
}

function pad2(n) { return String(n).padStart(2, '0'); }

async function checkLoadLayout(page, width) {
  const tag = `load layout ${width}px`;
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(150);

  const guide = await page.evaluate(() => ({
    exists: !!document.querySelector('#guideCard .gg-card'),
    replay: document.getElementById('loadGuideReplay') ? document.getElementById('loadGuideReplay').textContent.trim() : null,
    steps: document.querySelectorAll('#loadGuideSteps .gg-step').length,
    demo: !!document.querySelector('[data-demo-crate]'),
    animation: getComputedStyle(document.querySelector('[data-demo-crate]')).animationName,
    seen: !!localStorage.getItem('load_demo_seen_v1'),
  }));
  assert.ok(guide.exists, `${tag}: game guide missing`);
  assert.equal(guide.replay, '다시 보기', `${tag}: replay label ${guide.replay}`);
  assert.equal(guide.steps, 3, `${tag}: guide steps ${guide.steps}`);
  assert.ok(guide.demo, `${tag}: guide demo markup missing`);
  assert.equal(guide.animation, 'none', `${tag}: guide demo must not loop (${guide.animation})`);
  assert.equal(guide.seen, true, `${tag}: guide seen flag not stored`);

  // 1회 재생 후 3단계에서 정지하고, '다시 보기'로 1단계부터 다시 본다.
  await page.waitForTimeout(2300);
  const settled = await page.evaluate(() => ({
    on: Array.from(document.querySelectorAll('#loadGuideSteps .gg-step.is-on')).map((el) => el.dataset.step),
    shipOff: document.querySelector('[data-demo-ship]').classList.contains('is-off'),
    fill: parseFloat(document.querySelector('[data-demo-fill]').style.width) || 0,
  }));
  assert.deepEqual(settled.on, ['3'], `${tag}: guide did not stop on the last step (${settled.on})`);
  assert.equal(settled.shipOff, false, `${tag}: guide ship chip hidden on the last frame`);
  assert.ok(settled.fill > 50, `${tag}: guide gauge not filled on the last frame (${settled.fill})`);
  await page.click('#loadGuideReplay');
  await page.waitForTimeout(120);
  const replayed = await page.evaluate(() => Array.from(document.querySelectorAll('#loadGuideSteps .gg-step.is-on')).map((el) => el.dataset.step));
  assert.deepEqual(replayed, ['1'], `${tag}: replay did not restart from step 1 (${replayed})`);
  await page.waitForTimeout(2300);

  // 가이드 카드를 누르면 브라우저가 그 위치로 스크롤하므로, 첫 화면 측정 전에 맨 위로 되돌린다.
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(150);
  const geo = await page.evaluate(() => {
    const box = (sel) => {
      const el = document.querySelector(sel);
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { top: r.top, bottom: r.bottom, left: r.left, right: r.right, width: r.width };
    };
    const bar = document.querySelector('.ia-tabbar');
    const limit = bar && getComputedStyle(bar).display !== 'none'
      ? bar.getBoundingClientRect().top : window.innerHeight;
    const deck = document.querySelector('.cart-deck');
    return {
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      limit,
      mode: box('#modeDaily'),
      status: box('#statusCard'),
      cart: box('#cartCard'),
      gauge: box('.gauge'),
      box: box('#boxCard'),
      actions: box('#loadLeft'),
      ship: box('#shipBtn'),
      deck: box('.cart-deck'),
      columns: deck ? getComputedStyle(deck).gridTemplateColumns.split(' ').length : 0,
      rail: box('.load-rail'),
    };
  });
  assert.equal(geo.overflow, 0, `${tag}: horizontal overflow ${geo.overflow}px`);
  assert.equal(geo.columns, 2, `${tag}: cart deck is not two columns`);
  assert.ok(geo.deck && geo.deck.width >= 120, `${tag}: cart deck too narrow`);
  assert.ok(geo.status.top < geo.cart.top && geo.cart.top < geo.box.top, `${tag}: board order is off`);
  if (width <= 768) {
    assert.ok(geo.mode && geo.mode.top >= 0 && geo.mode.bottom <= geo.limit,
      `${tag}: mode switch is not in the first screen`);
    assert.ok(geo.gauge && geo.gauge.bottom <= geo.limit, `${tag}: weight gauge is below the first screen`);
    assert.ok(geo.actions && geo.actions.top < geo.limit, `${tag}: load buttons are not in the first screen`);
    if (width === 390) {
      assert.ok(geo.actions.bottom <= geo.limit, `${tag}: load buttons are cut by the first screen`);
      assert.ok(geo.ship && geo.ship.bottom <= geo.limit + 1, `${tag}: ship button is cut by the first screen`);
    }
    if (width === 768) {
      // 768×900 태블릿 세로에서도 적재 버튼·지금 배송 버튼이 하단 탭바 위에 온전히 들어와야 한다.
      assert.ok(geo.actions && geo.actions.bottom <= geo.limit,
        `${tag}: load buttons are cut by the tab bar (${geo.actions && geo.actions.bottom} > ${geo.limit})`);
      assert.ok(geo.ship && geo.ship.bottom <= geo.limit,
        `${tag}: ship button is cut by the tab bar (${geo.ship && geo.ship.bottom} > ${geo.limit})`);
    }
  } else {
    assert.ok(geo.rail.right <= geo.cart.left + 1, `${tag}: side rail is not left of the board`);
    assert.ok(geo.actions && geo.actions.width >= 140, `${tag}: load buttons too narrow`);
  }
  console.log(`${tag} passed`);
}

// ---- 한 번 더 싣기: 싣기 → 게이지·균형 변화 → 배송 → 과적 → 재도전·저장 ---- 
async function checkLoadGame(page, width) {
  const tag = `load game ${width}px`;
  await page.evaluate(() => localStorage.removeItem('load_cart_stats_v1'));
  await page.reload({ waitUntil: 'load' });
  await page.locator('#loadLeft').waitFor({ state: 'attached' });

  const data = await page.evaluate(() => JSON.parse(document.getElementById('loadData').textContent));
  const todayKey = await page.evaluate(() => {
    const t = new Date(Date.now() + 9 * 3600000);
    const p = (n) => String(n).padStart(2, '0');
    return `${t.getUTCFullYear()}-${p(t.getUTCMonth() + 1)}-${p(t.getUTCDate())}`;
  });
  const ordinal = Math.floor(Date.parse(todayKey + 'T00:00:00Z') / 86400000);
  const challenge = data.daily[ordinal % data.daily.length];
  const trips = challenge.batches.length;
  const limit = challenge.limit;
  const tilt = challenge.tilt;

  const read = () => page.evaluate(() => {
    const store = JSON.parse(localStorage.getItem('load_cart_stats_v1') || 'null');
    return {
      title: document.getElementById('boardTitle').textContent.trim(),
      trip: document.getElementById('tripValue').textContent.trim(),
      trips: document.getElementById('tripTotal').textContent.trim(),
      total: document.getElementById('totalValue').textContent.trim(),
      left: Number(document.getElementById('leftValue').textContent),
      right: Number(document.getElementById('rightValue').textContent),
      cart: Number(document.getElementById('cartTotal').textContent),
      gaugeWidth: parseFloat(document.getElementById('gaugeFill').style.width) || 0,
      gaugeClass: document.getElementById('gaugeFill').className,
      tiltNote: document.getElementById('tiltNote').textContent.trim(),
      preview: document.getElementById('shipPreview').textContent.trim(),
      shipDisabled: document.getElementById('shipBtn').disabled,
      boxName: document.getElementById('boxName').textContent.trim(),
      nextName: document.getElementById('nextName').textContent.trim(),
      risk: [document.getElementById('riskLeft').textContent.trim(),
        document.getElementById('riskRight').textContent.trim()],
      crates: document.querySelectorAll('.crate').length,
      boxHidden: document.getElementById('boxCard').hidden,
      tripHidden: document.getElementById('tripPanel').hidden,
      tripBadge: document.getElementById('tripBadge').textContent.trim(),
      tripScore: document.getElementById('tripScore').getAttribute('data-value'),
      streakChip: document.getElementById('streakChip').textContent.trim(),
      resultHidden: document.getElementById('resultBox').hidden,
      resultTotal: document.getElementById('resultTotal').getAttribute('data-value'),
      resultStars: document.querySelectorAll('#resultStars svg.is-on').length,
      practiceHidden: document.getElementById('practiceWrap').hidden,
      store,
    };
  });

  const initial = await read();
  assert.equal(initial.title, challenge.title, `${tag}: board title ${initial.title}`);
  assert.equal(initial.trip, '1', `${tag}: start trip ${initial.trip}`);
  assert.equal(initial.trips, String(trips), `${tag}: trip total ${initial.trips}`);
  assert.equal(initial.total, '0', `${tag}: start total ${initial.total}`);
  assert.equal(initial.shipDisabled, true, `${tag}: ship enabled with an empty cart`);
  assert.equal(initial.store, null, `${tag}: fresh storage expected`);
  assert.equal(initial.practiceHidden, true, `${tag}: practice list shown in daily mode`);
  assert.equal(initial.nextName, challenge.batches[0][1].name, `${tag}: next box preview ${initial.nextName}`);

  const first = challenge.batches[0][0];
  await page.click('#loadLeft');
  await page.waitForTimeout(450);
  const loaded = await read();
  assert.equal(loaded.left, first.kg, `${tag}: left weight ${loaded.left} vs ${first.kg}`);
  assert.equal(loaded.cart, first.kg, `${tag}: cart weight ${loaded.cart}`);
  assert.ok(loaded.gaugeWidth > 0, `${tag}: weight gauge did not move`);
  assert.equal(loaded.crates, 1, `${tag}: crates ${loaded.crates}`);
  assert.ok(/^\+[1-9]/.test(loaded.preview), `${tag}: ship preview ${loaded.preview}`);
  assert.equal(loaded.shipDisabled, false, `${tag}: ship still disabled after loading`);
  assert.ok(loaded.tiltNote.includes(String(first.kg)), `${tag}: tilt note ${loaded.tiltNote}`);
  assert.ok(['안전', '주의', '위험', '넘침'].includes(loaded.risk[0].split(' ')[0]), `${tag}: risk tag ${loaded.risk[0]}`);
  const tiltPreview = await page.evaluate(() => {
    const marks = [document.getElementById('tiltPreviewL'), document.getElementById('tiltPreviewR')];
    return {
      shown: marks.filter((mark) => mark && !mark.hidden).length,
      labels: marks.map((mark) => (mark ? mark.getAttribute('aria-label') : '')),
    };
  });
  assert.equal(tiltPreview.shown, 2, `${tag}: tilt preview markers ${tiltPreview.shown}/2`);
  for (const label of tiltPreview.labels) {
    assert.ok(label && label.includes('기울기'), `${tag}: tilt preview label ${label}`);
  }

  const motion = await page.evaluate(() => {
    const rig = document.getElementById('cartRig');
    const out = {};
    ['is-bounce', 'is-shake'].forEach((cls) => {
      rig.classList.remove(cls);
      rig.classList.add(cls);
      out[cls] = getComputedStyle(rig).animationName;
      rig.classList.remove(cls);
    });
    return out;
  });
  assert.ok(motion['is-bounce'] && motion['is-bounce'] !== 'none', `${tag}: cart bounce animation missing`);
  assert.ok(motion['is-shake'] && motion['is-shake'] !== 'none', `${tag}: cart shake animation missing`);

  const crateAnim = await page.evaluate(() => {
    const crate = document.createElement('span');
    crate.className = 'crate is-new';
    document.getElementById('stackLeft').appendChild(crate);
    const name = getComputedStyle(crate).animationName;
    crate.remove();
    return name;
  });
  assert.ok(crateAnim && crateAnim !== 'none', `${tag}: crate drop animation missing (${crateAnim})`);

  // 지금 배송: 미리보기 점수와 회차 점수가 같아야 한다.
  const preview = Number(loaded.preview.replace(/[^0-9]/g, ''));
  await page.click('#shipBtn');
  await page.waitForFunction(() => document.getElementById('tripScore').hasAttribute('data-value'));
  const shipped = await read();
  assert.equal(shipped.tripHidden, false, `${tag}: trip result not shown`);
  assert.equal(shipped.tripBadge, '배송 완료', `${tag}: trip badge ${shipped.tripBadge}`);
  assert.equal(Number(shipped.tripScore), preview, `${tag}: trip score ${shipped.tripScore} vs preview ${preview}`);
  assert.equal(shipped.total, String(preview), `${tag}: running total ${shipped.total}`);
  assert.equal(shipped.boxHidden, true, `${tag}: box card should make room for the result`);
  assert.ok(shipped.streakChip.includes('연속 1회'), `${tag}: streak chip ${shipped.streakChip}`);

  await page.click('#nextTripBtn');
  await page.waitForTimeout(180);
  const second = await read();
  assert.equal(second.trip, '2', `${tag}: trip after next ${second.trip}`);
  assert.equal(second.total, String(preview), `${tag}: total lost between trips`);
  assert.equal(second.crates, 0, `${tag}: crates left from the previous trip`);
  assert.equal(second.boxHidden, false, `${tag}: box card did not return`);

  // 전체 5회차를 '표기 상한까지도 안전한' 계획으로 완주한다.
  await page.click('#resetBtn');
  await page.waitForTimeout(180);
  assert.equal((await read()).total, '0', `${tag}: reset did not clear the score`);

  const sidesPerTrip = loadPlan(challenge);
  let expected = 0;
  for (let t = 0; t < sidesPerTrip.length; t += 1) {
    for (const side of sidesPerTrip[t]) {
      await page.click(side === 'left' ? '#loadLeft' : '#loadRight');
      await page.waitForTimeout(35);
    }
    const before = await read();
    const gained = Number(before.preview.replace(/[^0-9]/g, ''));
    await page.click('#shipBtn');
    await page.waitForFunction(() => document.getElementById('tripScore').hasAttribute('data-value'));
    const after = await read();
    assert.equal(Number(after.tripScore), gained, `${tag}: trip ${t + 1} score ${after.tripScore} vs ${gained}`);
    expected += gained;
    await page.click('#nextTripBtn');
    await page.waitForTimeout(140);
  }
  await page.waitForTimeout(700);
  const done = await read();
  assert.equal(done.resultHidden, false, `${tag}: final result not shown`);
  assert.equal(Number(done.resultTotal), expected, `${tag}: final total ${done.resultTotal} vs ${expected}`);
  assert.equal(done.total, String(expected), `${tag}: running total after finish`);
  assert.ok(done.resultStars >= 0 && done.resultStars <= 3, `${tag}: stars ${done.resultStars}`);
  const loadGap = await page.evaluate(() => ({
    text: document.getElementById('resultGapText').textContent.trim(),
    retryTop: document.getElementById('retryBtn').getBoundingClientRect().top,
    gridTop: document.getElementById('resultStars').getBoundingClientRect().top,
    label: document.getElementById('retryBtn').textContent.trim(),
  }));
  const topTarget = challenge.stars[challenge.stars.length - 1];
  assert.ok(loadGap.text.length > 0, `${tag}: goal gap missing`);
  if (done.resultStars < 3) {
    assert.ok(loadGap.text.includes('별 3개') && loadGap.text.includes(String(topTarget)),
      `${tag}: star goal gap ${loadGap.text}`);
  } else {
    assert.ok(loadGap.text.includes('연속'), `${tag}: streak goal gap ${loadGap.text}`);
  }
  assert.ok(loadGap.retryTop < loadGap.gridTop, `${tag}: retry is not placed before the score details`);
  assert.equal(loadGap.label, '바로 재도전', `${tag}: retry label ${loadGap.label}`);
  assert.ok(done.store && done.store.days && done.store.days[todayKey],
    `${tag}: daily record missing`);
  assert.equal(done.store.days[todayKey].plays, 1, `${tag}: plays ${done.store.days[todayKey].plays}`);
  assert.equal(done.store.days[todayKey].best, expected, `${tag}: daily best ${done.store.days[todayKey].best}`);
  assert.equal(done.store.best[challenge.id], expected, `${tag}: challenge best not stored`);
  assert.equal(done.store.totals.plays, 1, `${tag}: totals.plays ${done.store.totals.plays}`);
  assert.ok(done.store.streak.best >= 1, `${tag}: streak best ${done.store.streak.best}`);

  // 과적: 표기 상한을 무시하고 계속 실으면 회차가 0점으로 끝난다.
  await page.click('#retryBtn');
  await page.waitForTimeout(200);
  let busted = null;
  for (let i = 0; i < 8; i += 1) {
    const now = await read();
    if (!now.tripHidden) { busted = now; break; }
    const side = now.left <= now.right ? 'left' : 'right';
    await page.click(side === 'left' ? '#loadLeft' : '#loadRight');
    await page.waitForTimeout(140);
  }
  if (!busted) busted = await read();
  assert.equal(busted.tripHidden, false, `${tag}: loading past the limit did not end the trip`);
  assert.ok(['과적', '전복'].includes(busted.tripBadge), `${tag}: bust badge ${busted.tripBadge}`);
  assert.equal(Number(busted.tripScore), 0, `${tag}: busted trip scored ${busted.tripScore}`);
  assert.ok(busted.streakChip.includes('연속 0회'), `${tag}: streak not reset (${busted.streakChip})`);

  // 연습 모드: 스테이지 목록 → 다른 스테이지 로드
  await page.click('#modePractice');
  await page.locator('#practiceWrap:not([hidden])').waitFor({ timeout: 5000 });
  const practice = await page.evaluate(() => ({
    stages: document.querySelectorAll('.stage').length,
    current: document.querySelectorAll('.stage.is-current').length,
    title: document.getElementById('boardTitle').textContent.trim(),
    trip: document.getElementById('tripValue').textContent.trim(),
  }));
  assert.equal(practice.stages, data.practice.length, `${tag}: practice stages ${practice.stages}`);
  assert.equal(practice.current, 1, `${tag}: current stage ${practice.current}`);
  assert.equal(practice.trip, '1', `${tag}: practice trip ${practice.trip}`);
  await page.click(`.stage[data-pid="${data.practice[2].id}"]`);
  await page.waitForTimeout(160);
  const switched = await page.evaluate(() => ({
    title: document.getElementById('boardTitle').textContent.trim(),
    boxHidden: document.getElementById('boxCard').hidden,
    tripHidden: document.getElementById('tripPanel').hidden,
  }));
  assert.equal(switched.title, data.practice[2].title, `${tag}: stage switch title ${switched.title}`);
  assert.equal(switched.boxHidden, false, `${tag}: practice switch kept the result panel`);
  assert.equal(switched.tripHidden, true, `${tag}: practice switch kept the trip panel`);

  // 가이드 '다시 보기': 어느 화면에서든 1단계부터 다시 재생한다.
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.click('#loadGuideReplay');
  await page.waitForTimeout(160);
  const replay = await page.evaluate(() => ({
    on: Array.from(document.querySelectorAll('#loadGuideSteps .gg-step.is-on')).map((el) => el.dataset.step),
    shipOff: document.querySelector('[data-demo-ship]').classList.contains('is-off'),
    fill: parseFloat(document.querySelector('[data-demo-fill]').style.width) || 0,
  }));
  assert.deepEqual(replay.on, ['1'], `${tag}: guide replay did not restart (${replay.on})`);
  assert.equal(replay.shipOff, true, `${tag}: guide replay did not reset the ship chip`);
  assert.equal(replay.fill, 0, `${tag}: guide replay kept the gauge (${replay.fill})`);

  console.log(`${tag} passed`);
}

// ---- 회귀: 연습판 점수는 '오늘 기록'에 섞이지 않고 스테이지 최고 기록에만 남는다 ----
async function checkLoadPracticeRecord(browser, base) {
  const tag = 'load practice record';
  const context = await browser.newContext({ viewport: { width: 390, height: 900 } });
  const page = await context.newPage();
  try {
    await page.goto(`${base}/load.html`, { waitUntil: 'load' });
    await page.evaluate(() => localStorage.removeItem('load_cart_stats_v1'));
    await page.reload({ waitUntil: 'load' });
    await page.locator('#modePractice').waitFor({ state: 'attached' });

    const data = await page.evaluate(() => JSON.parse(document.getElementById('loadData').textContent));
    const todayKey = await page.evaluate(() => {
      const t = new Date(Date.now() + 9 * 3600000);
      const p = (n) => String(n).padStart(2, '0');
      return `${t.getUTCFullYear()}-${p(t.getUTCMonth() + 1)}-${p(t.getUTCDate())}`;
    });

    await page.click('#modePractice');
    await page.locator('#practiceWrap:not([hidden])').waitFor({ timeout: 5000 });
    const stage = data.practice[0];
    const opened = await readLoadState(page);
    assert.equal(opened.title, stage.title, `${tag}: practice stage title ${opened.title}`);

    const sides = loadPlan(stage);
    let expected = 0;
    for (let t = 0; t < sides.length; t += 1) {
      for (const side of sides[t]) {
        await page.click(side === 'left' ? '#loadLeft' : '#loadRight');
        await page.waitForTimeout(35);
      }
      const before = await readLoadState(page);
      const gained = Number(before.preview.replace(/[^0-9]/g, ''));
      await page.click('#shipBtn');
      await page.waitForFunction(() => document.getElementById('tripScore').hasAttribute('data-value'));
      const after = await readLoadState(page);
      assert.equal(Number(after.tripScore), gained, `${tag}: trip ${t + 1} score ${after.tripScore} vs ${gained}`);
      expected += gained;
      await page.click('#nextTripBtn');
      await page.waitForTimeout(140);
    }
    await page.waitForTimeout(600);
    const done = await readLoadState(page);
    assert.equal(done.resultHidden, false, `${tag}: practice result missing`);
    assert.equal(done.resultBadge, '연습 완료', `${tag}: result badge ${done.resultBadge}`);
    assert.equal(done.resultTodayLabel, '스테이지 최고', `${tag}: today stat label ${done.resultTodayLabel}`);
    assert.equal(Number(done.resultTotal), expected, `${tag}: practice total ${done.resultTotal} vs ${expected}`);
    assert.ok(done.store, `${tag}: practice run was not stored at all`);
    assert.ok(!done.store.days || !done.store.days[todayKey],
      `${tag}: practice score leaked into the daily record (${JSON.stringify(done.store.days)})`);
    assert.equal(done.store.totals.plays, 0, `${tag}: practice run counted as a daily play (${done.store.totals.plays})`);
    assert.equal(done.store.best[stage.id], expected, `${tag}: practice stage best ${done.store.best[stage.id]}`);

    // 오늘의 챌린지로 돌아오면 오늘 기록은 비어 있어야 한다.
    await page.click('#modeDaily');
    await page.waitForTimeout(220);
    const daily = await readLoadState(page);
    assert.equal(daily.practiceHidden, true, `${tag}: practice list still open in daily mode`);
    assert.equal(daily.recBest, '—', `${tag}: 오늘 최고에 연습 점수가 남음 (${daily.recBest})`);
    assert.equal(daily.recPlays, '0판', `${tag}: 오늘 완주에 연습판이 남음 (${daily.recPlays})`);
    console.log(`${tag} passed (연습 ${expected}점 · 오늘 기록 비어 있음)`);
  } finally {
    await page.close();
    await context.close();
  }
}

// ---- 회귀: 5회 연속 · 별 3개를 달성해도 '신기록까지 1회' 같은 불가능한 목표를 띄우지 않는다 ----
async function checkLoadPerfectGap(browser, base) {
  const tag = 'load perfect gap';
  const context = await browser.newContext({ viewport: { width: 390, height: 900 } });
  const page = await context.newPage();
  try {
    await page.goto(`${base}/load.html`, { waitUntil: 'load' });
    await page.evaluate(() => localStorage.removeItem('load_cart_stats_v1'));
    await page.reload({ waitUntil: 'load' });
    await page.locator('#loadLeft').waitFor({ state: 'attached' });

    const data = await page.evaluate(() => JSON.parse(document.getElementById('loadData').textContent));
    const title = await page.evaluate(() => document.getElementById('boardTitle').textContent.trim());
    const challenge = (data.daily || []).find((ch) => ch.title === title) || data.daily[0];
    assert.ok(challenge, `${tag}: 오늘의 챌린지를 찾지 못했습니다`);

    const { plan, total } = perfectLoadPlan(challenge);
    assert.ok(total >= challenge.stars[challenge.stars.length - 1],
      `${tag}: 완벽 계획이 별 3개 목표에 못 미칩니다 (${total} < ${challenge.stars[challenge.stars.length - 1]})`);

    for (let t = 0; t < plan.length; t += 1) {
      for (const side of plan[t].sides) {
        await page.click(side === 'left' ? '#loadLeft' : '#loadRight');
        await page.waitForTimeout(35);
      }
      await page.click('#shipBtn');
      await page.waitForFunction(() => document.getElementById('tripScore').hasAttribute('data-value'));
      await page.click('#nextTripBtn');
      await page.waitForTimeout(140);
    }
    await page.waitForTimeout(700);

    const done = await page.evaluate(() => ({
      gap: document.getElementById('resultGapText').textContent.trim(),
      stars: document.querySelectorAll('#resultStars svg.is-on').length,
      streak: document.getElementById('resultStreak').textContent.trim(),
      total: Number(document.getElementById('resultTotal').getAttribute('data-value')),
      store: JSON.parse(localStorage.getItem('load_cart_stats_v1') || 'null'),
    }));
    assert.equal(done.stars, 3, `${tag}: 별 3개를 못 채웠습니다 (${done.total}점 · 별 ${done.stars}개)`);
    assert.equal(done.streak, '5회', `${tag}: 최고 연속 ${done.streak}`);
    assert.ok(!/신기록까지\s*1회/.test(done.gap), `${tag}: 불가능한 목표 문구가 떴습니다 ("${done.gap}")`);
    assert.ok(!/신기록까지/.test(done.gap), `${tag}: 한 판 최대치를 넘기는 목표 문구 ("${done.gap}")`);
    assert.ok(done.gap.includes('신기록') || done.gap.includes('완벽 달성'),
      `${tag}: 달성 문구가 아닙니다 ("${done.gap}")`);
    assert.equal(done.store.streak.best, 5, `${tag}: 최고 연속 저장값 ${done.store.streak.best}`);
    console.log(`${tag} passed (${done.total}점 · 별 3개 · ${done.gap})`);
  } finally {
    await page.close();
    await context.close();
  }
}

// ---- 회귀: '다시 풀기' 연습 모드의 단서·정답 보기는 기록 저장소를 바꾸지 않는다 ----
async function checkChartPracticeStore(browser, base) {
  const tag = 'chart practice store';
  const context = await browser.newContext({ viewport: { width: 390, height: 900 } });
  const page = await context.newPage();
  try {
    await page.goto(`${base}/chart.html`, { waitUntil: 'load' });
    await page.waitForFunction(() => document.getElementById('options').querySelectorAll('.opt').length === 4,
      null, { timeout: 5000 });
    await page.click('#options .opt[data-idx="0"]');
    await page.locator('#resultBox:not([hidden])').waitFor({ timeout: 5000 });

    const saved = await page.evaluate(() => localStorage.getItem('secjobs-chart-v1'));
    assert.ok(saved, `${tag}: 기록 저장값이 없습니다`);

    await page.click('#retryBtn');
    await page.waitForTimeout(160);
    const practice = await page.evaluate(() => ({
      hidden: document.getElementById('resultBox').hidden,
      note: document.getElementById('askMsg').textContent.trim(),
      open: document.querySelectorAll('#clueList .clue.open').length,
    }));
    assert.equal(practice.hidden, true, `${tag}: 다시 풀기 후 결과가 남아 있습니다`);
    assert.ok(practice.note.includes('연습'), `${tag}: 연습 모드 안내 문구 "${practice.note}"`);
    assert.equal(practice.open, 0, `${tag}: 연습 모드 단서 ${practice.open}개가 열려 있습니다`);

    const before = await page.evaluate(() => localStorage.getItem('secjobs-chart-v1'));
    for (let i = 0; i < 3; i += 1) {
      await page.click('#nextClue');
      await page.waitForTimeout(80);
    }
    const opened = await page.evaluate(() => document.querySelectorAll('#clueList .clue.open').length);
    assert.equal(opened, 3, `${tag}: 연습 모드에서 단서가 열리지 않습니다 (${opened}/3)`);
    await page.click('#giveUp');
    await page.locator('#resultBox:not([hidden])').waitFor({ timeout: 5000 });

    const after = await page.evaluate(() => localStorage.getItem('secjobs-chart-v1'));
    assert.equal(after, before, `${tag}: 연습 모드의 단서·정답 보기가 기록(secjobs-chart-v1)을 바꿨습니다`);

    const revealed = await page.evaluate(() => ({
      answer: document.getElementById('resultAnswer').textContent.trim(),
      open: document.querySelectorAll('#clueList .clue.open').length,
      badge: document.getElementById('resultBadge').textContent.trim(),
    }));
    assert.ok(revealed.answer.length > 0, `${tag}: 정답 보기가 동작하지 않습니다`);
    assert.equal(revealed.open, 3, `${tag}: 정답 확인 후 단서 ${revealed.open}/3`);
    assert.ok(revealed.badge.length > 0, `${tag}: 결과 배지가 비어 있습니다`);

    // 기록은 실제로 그대로 남아 있어야 한다(새로고침 후에도).
    await page.reload({ waitUntil: 'load' });
    await page.waitForFunction(() => document.getElementById('options').querySelectorAll('.opt').length === 4,
      null, { timeout: 5000 });
    const reloaded = await page.evaluate(() => localStorage.getItem('secjobs-chart-v1'));
    assert.equal(reloaded, before, `${tag}: 새로고침 뒤 기록이 달라졌습니다`);
    console.log(`${tag} passed`);
  } finally {
    await page.close();
    await context.close();
  }
}

// ---- 회귀: 진행 중인 일일판은 자정을 넘겨도 시작일에 귀속해 그대로 마칠 수 있다 ----
async function checkLoadMidnightRun(browser, base) {
  const tag = 'load midnight run';
  const context = await browser.newContext({ viewport: { width: 390, height: 900 } });
  const page = await context.newPage();
  try {
    await page.goto(`${base}/load.html`, { waitUntil: 'load' });
    await page.evaluate(() => localStorage.removeItem('load_cart_stats_v1'));

    const data = await page.evaluate(() => JSON.parse(document.getElementById('loadData').textContent));
    const parts = await page.evaluate(() => {
      const t = new Date(Date.now() + 9 * 3600000);
      return [t.getUTCFullYear(), t.getUTCMonth() + 1, t.getUTCDate()];
    });
    const [y, m, d] = parts;
    const todayKey = `${y}-${pad2(m)}-${pad2(d)}`;
    const next = new Date(Date.UTC(y, m - 1, d + 1));
    const nextKey = `${next.getUTCFullYear()}-${pad2(next.getUTCMonth() + 1)}-${pad2(next.getUTCDate())}`;
    const ordinal = Math.floor(Date.UTC(y, m - 1, d) / 86400000);
    const challenge = data.daily[ordinal % data.daily.length];
    const nextChallenge = data.daily[(ordinal + 1) % data.daily.length];

    // KST 23:55에 탭을 열어 둔 상태
    await page.clock.setFixedTime(new Date(Date.UTC(y, m - 1, d, 14, 55)));
    await page.reload({ waitUntil: 'load' });
    await page.locator('#loadLeft').waitFor({ state: 'attached' });

    let state = await readLoadState(page);
    assert.equal(state.title, challenge.title, `${tag}: board ${state.title}`);
    assert.ok(state.dayBadge && state.dayBadge.hidden, `${tag}: day badge shown before midnight`);

    const sides = loadPlan(challenge);
    await page.click(sides[0][0] === 'left' ? '#loadLeft' : '#loadRight');
    await page.waitForTimeout(150);
    const loaded = await readLoadState(page);
    assert.equal(loaded.trip, '1', `${tag}: trip ${loaded.trip}`);
    assert.equal(loaded.crates, 1, `${tag}: crates ${loaded.crates}`);
    assert.ok(loaded.cart > 0, `${tag}: cart ${loaded.cart}`);

    // 새로고침 없이 시계만 KST 00:05로 넘기고 탭을 다시 보이게 한다.
    await page.clock.setFixedTime(new Date(Date.UTC(y, m - 1, d, 15, 5)));
    await page.evaluate(() => document.dispatchEvent(new Event('visibilitychange')));
    await page.waitForTimeout(200);

    const kept = await readLoadState(page);
    assert.equal(kept.title, challenge.title, `${tag}: 진행 중인 판이 자정에 초기화됨`);
    assert.equal(kept.trip, '1', `${tag}: trip reset at midnight (${kept.trip})`);
    assert.equal(kept.cart, loaded.cart, `${tag}: cart reset at midnight (${kept.cart})`);
    assert.equal(kept.crates, loaded.crates, `${tag}: crates reset at midnight (${kept.crates})`);
    assert.equal(kept.boxName, loaded.boxName, `${tag}: box card changed at midnight`);
    assert.ok(kept.dayBadge && !kept.dayBadge.hidden, `${tag}: 새 날짜 판 안내 배지가 없음`);
    assert.ok(kept.dayBadge.text.includes('새 날짜 판이 열렸습니다'), `${tag}: badge text ${kept.dayBadge.text}`);
    assert.ok(kept.recordDate.includes(`${next.getUTCMonth() + 1}/${next.getUTCDate()}`),
      `${tag}: 오늘 기록 날짜가 새 날짜가 아님 (${kept.recordDate})`);

    // 남은 회차를 마저 실어 완주한다 — 판 시작일 기록으로 저장되어야 한다.
    let expected = 0;
    for (let t = 0; t < sides.length; t += 1) {
      const rest = t === 0 ? sides[0].slice(1) : sides[t];
      for (const side of rest) {
        await page.click(side === 'left' ? '#loadLeft' : '#loadRight');
        await page.waitForTimeout(35);
      }
      const before = await readLoadState(page);
      const gained = Number(before.preview.replace(/[^0-9]/g, ''));
      await page.click('#shipBtn');
      await page.waitForFunction(() => document.getElementById('tripScore').hasAttribute('data-value'));
      const after = await readLoadState(page);
      assert.equal(Number(after.tripScore), gained, `${tag}: trip ${t + 1} score ${after.tripScore} vs ${gained}`);
      expected += gained;
      await page.click('#nextTripBtn');
      await page.waitForTimeout(140);
    }
    await page.waitForTimeout(700);
    const done = await readLoadState(page);
    assert.equal(done.resultHidden, false, `${tag}: 자정을 넘긴 판을 마치지 못함`);
    assert.equal(Number(done.resultTotal), expected, `${tag}: final total ${done.resultTotal} vs ${expected}`);
    assert.ok(done.store && done.store.days && done.store.days[todayKey],
      `${tag}: 판 시작일 기록이 없음 (${JSON.stringify(done.store && done.store.days)})`);
    assert.equal(done.store.days[todayKey].plays, 1, `${tag}: 판 시작일 완주 ${done.store.days[todayKey].plays}`);
    assert.equal(done.store.days[todayKey].best, expected, `${tag}: 판 시작일 최고 ${done.store.days[todayKey].best}`);
    assert.ok(!done.store.days[nextKey], `${tag}: 자정을 넘긴 판이 새 날짜 기록으로 저장됨`);

    // 새 날짜 판은 다음 시작(다시 하기) 때 열린다.
    await page.click('#retryBtn');
    await page.waitForTimeout(250);
    const restarted = await readLoadState(page);
    assert.equal(restarted.title, nextChallenge.title, `${tag}: 새 날짜 판 제목 ${restarted.title}`);
    assert.equal(restarted.total, '0', `${tag}: 새 판 누적 ${restarted.total}`);
    assert.ok(restarted.dayBadge && restarted.dayBadge.hidden, `${tag}: 새 판을 열었는데 배지가 남음`);
    console.log(`${tag} passed (${challenge.title} → ${nextChallenge.title} · ${expected}점)`);
  } finally {
    await page.close();
    await context.close();
  }
}

// ---- 아케이드: 첫 화면(캔버스·세그먼트·기록 카드) · PC 레일/보드 2단 · 모바일 방향키 패드 ----
async function checkArcadeLayout(page, width) {
  const tag = `arcade layout ${width}px`;
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(150);
  const geo = await page.evaluate(() => {
    const box = (sel) => {
      const el = document.querySelector(sel);
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { top: r.top, bottom: r.bottom, left: r.left, right: r.right, width: r.width, height: r.height };
    };
    const bar = document.querySelector('.ia-tabbar');
    const limit = bar && getComputedStyle(bar).display !== 'none'
      ? bar.getBoundingClientRect().top : window.innerHeight;
    const canvas = document.getElementById('gameCanvas');
    return {
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      limit,
      canvas: box('#gameCanvas'),
      rail: box('.arc-rail'),
      main: box('.arc-main'),
      brick: box('#gameBrick'),
      board: document.getElementById('stage').getAttribute('data-board'),
      cards: document.querySelectorAll('.arc-rail > section').length,
      dpad: getComputedStyle(document.getElementById('dpad')).display,
      backing: { w: canvas.width, h: canvas.height, css: canvas.getBoundingClientRect().width },
    };
  });
  assert.equal(geo.overflow, 0, `${tag}: horizontal overflow ${geo.overflow}px`);
  assert.ok(geo.canvas && geo.canvas.width > 200, `${tag}: canvas width ${geo.canvas && geo.canvas.width}`);
  assert.ok(geo.canvas.height > geo.canvas.width, `${tag}: canvas is not portrait`);
  if (width <= 390) {
    assert.ok(geo.canvas.bottom <= geo.limit + 1, `${tag}: canvas cut by the first screen`);
  } else {
    assert.ok(geo.canvas.top < geo.limit, `${tag}: canvas does not start on the first screen`);
  }
  assert.equal(geo.cards, 3, `${tag}: rail cards ${geo.cards}`);
  assert.equal(geo.board, 'brick:normal', `${tag}: initial board ${geo.board}`);
  assert.ok(geo.backing.w >= Math.round(geo.backing.css), `${tag}: canvas backing store ${geo.backing.w} < ${geo.backing.css}`);
  assert.ok(geo.brick && geo.brick.top >= 0 && geo.brick.bottom <= geo.limit, `${tag}: game segment outside the first screen`);
  if (width <= 900) {
    assert.equal(geo.dpad, 'grid', `${tag}: direction pad must be visible on mobile`);
    assert.ok(geo.rail.top >= geo.main.bottom - 1, `${tag}: rail must stack below the stage`);
  } else {
    assert.equal(geo.dpad, 'none', `${tag}: direction pad must be hidden on desktop`);
    assert.ok(geo.rail.right <= geo.main.left + 1, `${tag}: rail is not left of the stage`);
  }
  console.log(`${tag} passed`);
}

// ---- 아케이드: 두 게임 실행/점수 · 닉네임 등록(XSS 텍스트) · 티어 · 난이도별 점수판 분리 ----
async function checkArcadeGame(page, width) {
  const tag = `arcade game ${width}px`;
  await page.evaluate(() => {
    ['arcade_ranking_v1', 'arcade_last_nick', 'arcade_guide_seen_v1'].forEach((key) => localStorage.removeItem(key));
  });
  await page.reload({ waitUntil: 'load' });
  await page.locator('#gameCanvas').waitFor({ state: 'attached' });

  const data = await page.evaluate(() => JSON.parse(document.getElementById('arcadeData').textContent));
  const brickBoard = data.boards.find((board) => board.key === 'brick:normal');
  assert.ok(brickBoard && brickBoard.rivals.length >= 5 && brickBoard.rivals.length <= 8,
    `${tag}: rival records ${brickBoard ? brickBoard.rivals.length : 0}`);
  assert.equal(data.boards.length, 4, `${tag}: split boards ${data.boards.length}`);

  // 게임 방법: 3단계 데모가 한 번 움직이고 마지막 장면에서 멈춘다. 다시 보기로 재생.
  const guide = await page.evaluate(() => ({
    exists: !!document.getElementById('guideCard') && document.getElementById('guideCard').classList.contains('gg-card'),
    replay: document.getElementById('guideReplay').textContent.trim(),
    steps: document.querySelectorAll('#guideSteps .gg-step').length,
    cap: document.getElementById('guideCaption').textContent.trim(),
    canvasW: document.getElementById('guideCanvas').width,
    seen: !!localStorage.getItem('arcade_guide_seen_v1'),
    animation: getComputedStyle(document.querySelector('.arc-canvas')).animationName,
  }));
  assert.equal(guide.exists, true, `${tag}: guide card missing`);
  assert.equal(guide.replay, '다시 보기', `${tag}: replay label ${guide.replay}`);
  assert.equal(guide.steps, 3, `${tag}: guide steps ${guide.steps}`);
  assert.ok(guide.cap.length > 10, `${tag}: guide caption ${guide.cap}`);
  assert.ok(guide.canvasW > 100, `${tag}: guide preview canvas ${guide.canvasW}px`);
  assert.equal(guide.seen, true, `${tag}: guide seen flag not stored`);
  assert.equal(guide.animation, 'none', `${tag}: guide demo must not loop (${guide.animation})`);

  await page.waitForTimeout(4400);
  const settled = await page.evaluate(() => ({
    on: Array.from(document.querySelectorAll('#guideSteps .gg-step.is-on')).map((el) => el.dataset.step),
    done: document.querySelectorAll('#guideSteps .gg-step.is-done').length,
  }));
  assert.deepEqual(settled.on, ['3'], `${tag}: guide did not stop on the last step (${settled.on})`);
  assert.equal(settled.done, 2, `${tag}: guide completed steps ${settled.done}`);
  await page.click('#guideReplay');
  await page.waitForTimeout(160);
  const replayed = await page.evaluate(() => Array.from(document.querySelectorAll('#guideSteps .gg-step.is-on')).map((el) => el.dataset.step));
  assert.deepEqual(replayed, ['1'], `${tag}: replay did not restart from step 1 (${replayed})`);
  await page.waitForTimeout(4300);

  // 1) 벽돌깨기: 시작 → 점수 → 일시정지/재개 → 판 포기
  await page.click('#overlayBtn');
  await page.waitForFunction(() => Number(document.getElementById('hudScore').textContent.replace(/,/g, '')) > 0,
    null, { timeout: 20000 });
  const brickRun = await page.evaluate(() => ({
    score: Number(document.getElementById('hudScore').textContent.replace(/,/g, '')),
    phase: document.getElementById('stage').getAttribute('data-phase'),
    lives: document.getElementById('hudLives').textContent.trim(),
    aux: document.getElementById('hudAux').textContent.trim(),
    pauseDisabled: document.getElementById('pauseBtn').disabled,
  }));
  assert.ok(brickRun.score > 0, `${tag}: brick score ${brickRun.score}`);
  assert.equal(brickRun.phase, 'playing', `${tag}: brick phase ${brickRun.phase}`);
  assert.equal(brickRun.lives, '3', `${tag}: brick lives ${brickRun.lives}`);
  assert.ok(brickRun.aux.includes('스테이지'), `${tag}: brick hud ${brickRun.aux}`);
  assert.equal(brickRun.pauseDisabled, false, `${tag}: pause disabled while playing`);
  const chase = await page.evaluate(() => ({
    tier: document.getElementById('chaseTier').textContent.trim(),
    rival: document.getElementById('chaseRival').textContent.trim(),
    shown: !document.getElementById('arcChase').hidden,
  }));
  assert.ok(chase.shown, `${tag}: live chase badges missing`);
  assert.ok(chase.tier.includes('티어') && chase.tier.includes('점'), `${tag}: tier chase ${chase.tier}`);
  assert.ok(chase.rival.includes('추월'), `${tag}: rival chase ${chase.rival}`);

  await page.click('#pauseBtn');
  await page.waitForTimeout(150);
  const paused = await page.evaluate(() => ({
    phase: document.getElementById('stage').getAttribute('data-phase'),
    title: document.getElementById('overlayTitle').textContent.trim(),
    hidden: document.getElementById('overlay').hidden,
  }));
  assert.equal(paused.phase, 'paused', `${tag}: pause phase ${paused.phase}`);
  assert.equal(paused.hidden, false, `${tag}: pause overlay hidden`);
  assert.equal(paused.title, '일시정지', `${tag}: pause title ${paused.title}`);
  await page.click('#overlayBtn');
  await page.waitForTimeout(120);
  assert.equal(await page.evaluate(() => document.getElementById('stage').getAttribute('data-phase')), 'playing',
    `${tag}: resume failed`);

  const brickScore = await page.evaluate(() => Number(document.getElementById('hudScore').textContent.replace(/,/g, '')));
  await page.click('#quitBtn');
  await page.locator('#nickPanel:not([hidden])').waitFor({ timeout: 5000 });
  const ended = await page.evaluate(() => ({
    phase: document.getElementById('stage').getAttribute('data-phase'),
    title: document.getElementById('overlayTitle').textContent.trim(),
    detail: document.getElementById('overlayText').textContent.trim(),
    statsHidden: document.getElementById('overlayStats').hidden,
    nickScore: Number(document.getElementById('nickScore').textContent.replace(/,/g, '')),
    tierText: document.getElementById('tierBadge').textContent.trim(),
  }));
  assert.equal(ended.phase, 'over', `${tag}: quit phase ${ended.phase}`);
  assert.equal(ended.title, '기록 종료', `${tag}: end title ${ended.title}`);
  assert.ok(ended.detail.length > 0, `${tag}: end detail missing`);
  assert.equal(ended.statsHidden, true, `${tag}: duplicate stats shown above the nickname panel`);
  const endedExtra = await page.evaluate(() => ({
    gap: document.getElementById('overlayGap').textContent.trim(),
    gapHidden: document.getElementById('overlayGap').hidden,
    retry: document.getElementById('overlayBtn').textContent.trim(),
    retryBeforeNick: document.getElementById('overlayBtn').compareDocumentPosition(document.getElementById('nickPanel'))
      === Node.DOCUMENT_POSITION_FOLLOWING,
  }));
  assert.equal(endedExtra.gapHidden, false, `${tag}: goal gap hidden on game over`);
  assert.ok(endedExtra.gap.includes('점'), `${tag}: goal gap ${endedExtra.gap}`);
  assert.equal(endedExtra.retry, '한 판 더', `${tag}: retry label ${endedExtra.retry}`);
  assert.equal(endedExtra.retryBeforeNick, true, `${tag}: one-tap retry is not first`);
  assert.ok(ended.nickScore >= brickScore, `${tag}: nickname score ${ended.nickScore} < ${brickScore}`);

  // 티어: 현재 점수가 들어가는 구간의 등급이 배지에 보인다.
  const expectedTier = brickBoard.tiers.filter((tier) => brickScore >= tier.min).pop().name;
  assert.equal(ended.tierText, expectedTier, `${tag}: best tier ${ended.tierText} (expected ${expectedTier})`);
  const tierCard = await page.evaluate(() => ({
    badge: document.getElementById('tierBadge').textContent.trim(),
    next: document.getElementById('tierNext').textContent.trim(),
  }));
  assert.ok(tierCard.badge.length > 0, `${tag}: tier badge empty`);
  assert.ok(tierCard.next.includes('다음 등급'), `${tag}: next tier hint ${tierCard.next}`);

  // 2) 닉네임 등록: 마크업이 그대로 문자로만 렌더링된다(XSS 차단 · textContent).
  const nick = '<b>x</b>';
  await page.fill('#nickInput', nick);
  await page.click('#nickSave');
  await page.waitForFunction(() => document.querySelectorAll('#rankList .arc-rank-row').length > 0, null, { timeout: 5000 });
  const saved = await page.evaluate(() => ({
    names: Array.from(document.querySelectorAll('#rankList .arc-rank-name')).map((el) => el.textContent),
    bold: document.querySelectorAll('#rankList b, #rankList img').length,
    html: document.getElementById('rankList').innerHTML,
    note: document.getElementById('nickNote').textContent.trim(),
    saveLabel: document.getElementById('nickSave').textContent.trim(),
    store: JSON.parse(localStorage.getItem('arcade_ranking_v1') || 'null'),
  }));
  assert.equal(saved.names[0], nick, `${tag}: nickname rendered as ${JSON.stringify(saved.names[0])}`);
  assert.equal(saved.bold, 0, `${tag}: nickname markup was parsed as HTML`);
  assert.ok(saved.html.includes('&lt;b&gt;'), `${tag}: nickname not escaped in innerHTML`);
  assert.ok(saved.note.includes('검증'), `${tag}: local-only note missing (${saved.note})`);
  assert.equal(saved.saveLabel, '등록됨', `${tag}: save label ${saved.saveLabel}`);
  assert.ok(saved.store && saved.store.boards && saved.store.boards['brick:normal'],
    `${tag}: local ranking store missing`);
  const entry = saved.store.boards['brick:normal'][0];
  assert.equal(entry.name, nick, `${tag}: stored nickname ${entry.name}`);
  assert.equal(entry.verified, false, `${tag}: local record must stay unverified`);
  assert.equal(entry.tier, expectedTier, `${tag}: stored tier ${entry.tier}`);

  // 3) 기준 라이벌: 미리 세팅된 기록과 이 기기 기록을 구분해 보여 준다.
  await page.click('#rankRival');
  await page.waitForTimeout(120);
  const rivals = await page.evaluate(() => ({
    rows: document.querySelectorAll('#rankList .arc-rank-row').length,
    badges: Array.from(document.querySelectorAll('#rankList .arc-rank-badge')).map((el) => el.textContent),
    names: Array.from(document.querySelectorAll('#rankList .arc-rank-name')).map((el) => el.textContent),
    note: document.getElementById('rankNote').textContent.trim(),
  }));
  assert.equal(rivals.rows, brickBoard.rivals.length, `${tag}: rival rows ${rivals.rows}`);
  assert.ok(rivals.badges.every((badge) => badge === '기준'), `${tag}: rival badges ${rivals.badges}`);
  assert.ok(rivals.note.includes('AI 기준'), `${tag}: rival note ${rivals.note}`);
  assert.ok(!rivals.names.includes(nick), `${tag}: local record leaked into rivals`);
  await page.click('#rankLocal');
  await page.waitForTimeout(100);

  // 4) 난이도 분리: 같은 게임의 어려움 점수판은 따로 비어 있다.
  await page.click('#diffHard');
  await page.waitForTimeout(150);
  const hard = await page.evaluate(() => ({
    board: document.getElementById('stage').getAttribute('data-board'),
    label: document.getElementById('boardLabel').textContent.trim(),
    rows: document.querySelectorAll('#rankList .arc-rank-row').length,
    empty: document.querySelector('#rankList .arc-rank-empty') ? document.querySelector('#rankList .arc-rank-empty').textContent.trim() : '',
    store: JSON.parse(localStorage.getItem('arcade_ranking_v1') || 'null'),
  }));
  assert.equal(hard.board, 'brick:hard', `${tag}: hard board ${hard.board}`);
  assert.ok(hard.label.includes('어려움'), `${tag}: hard label ${hard.label}`);
  assert.equal(hard.rows, 0, `${tag}: hard board shared the normal board`);
  assert.ok(hard.empty.includes('없습니다'), `${tag}: hard empty state ${hard.empty}`);
  assert.ok(!hard.store.boards['brick:hard'], `${tag}: hard board was written by normal play`);
  await page.click('#diffNormal');
  await page.waitForTimeout(120);

  // 5) 지렁이: 시작 → 첫 먹이 점수 · 방향 전환 · 방향키 패드
  await page.click('#gameSnake');
  await page.waitForTimeout(150);
  const snakeBoard = await page.evaluate(() => ({
    board: document.getElementById('stage').getAttribute('data-board'),
    rows: document.querySelectorAll('#rankList .arc-rank-row').length,
    livesLabel: document.getElementById('hudLivesLabel').textContent.trim(),
  }));
  assert.equal(snakeBoard.board, 'snake:normal', `${tag}: snake board ${snakeBoard.board}`);
  assert.equal(snakeBoard.rows, 0, `${tag}: snake board reused brick records`);
  assert.equal(snakeBoard.livesLabel, '길이', `${tag}: snake hud label ${snakeBoard.livesLabel}`);

  await page.click('#overlayBtn');
  await page.waitForFunction(() => Number(document.getElementById('hudScore').textContent.replace(/,/g, '')) > 0,
    null, { timeout: 10000 });
  const snakeRun = await page.evaluate(() => ({
    score: Number(document.getElementById('hudScore').textContent.replace(/,/g, '')),
    length: document.getElementById('hudLives').textContent.trim(),
    phase: document.getElementById('stage').getAttribute('data-phase'),
  }));
  assert.ok(snakeRun.score > 0, `${tag}: snake score ${snakeRun.score}`);
  assert.ok(Number(snakeRun.length) >= 5, `${tag}: snake length ${snakeRun.length}`);
  assert.equal(snakeRun.phase, 'playing', `${tag}: snake phase ${snakeRun.phase}`);

  await page.keyboard.press('ArrowUp');
  await page.waitForTimeout(80);
  assert.equal(await page.evaluate(() => document.getElementById('stage').getAttribute('data-dir')), '0,-1',
    `${tag}: keyboard direction not applied`);
  if (width <= 900) {
    await page.click('.arc-dpad-btn[data-dir="left"]');
    await page.waitForTimeout(80);
    assert.equal(await page.evaluate(() => document.getElementById('stage').getAttribute('data-dir')), '-1,0',
      `${tag}: direction pad not applied`);
  }
  await page.click('#pauseBtn');
  await page.waitForTimeout(120);
  assert.equal(await page.evaluate(() => document.getElementById('stage').getAttribute('data-phase')), 'paused',
    `${tag}: snake pause failed`);
  await page.click('#overlayBtn');
  await page.waitForTimeout(100);
  assert.equal(await page.evaluate(() => document.getElementById('stage').getAttribute('data-phase')), 'playing',
    `${tag}: snake resume failed`);
  await page.click('#quitBtn');
  await page.locator('#nickPanel:not([hidden])').waitFor({ timeout: 5000 });
  await page.fill('#nickInput', '지렁이\u200b  왕');
  await page.click('#nickSave');
  await page.waitForTimeout(150);
  const snakeSaved = await page.evaluate(() => ({
    names: Array.from(document.querySelectorAll('#rankList .arc-rank-name')).map((el) => el.textContent),
    store: JSON.parse(localStorage.getItem('arcade_ranking_v1') || 'null'),
  }));
  assert.equal(snakeSaved.names[0], '지렁이 왕',
    `${tag}: snake nickname not sanitized (${JSON.stringify(snakeSaved.names[0])})`);
  assert.ok(snakeSaved.names[0].length <= 12, `${tag}: nickname length ${snakeSaved.names[0].length}`);
  assert.ok(snakeSaved.store.boards['snake:normal'], `${tag}: snake board not stored`);
  assert.equal(snakeSaved.store.boards['brick:normal'].length, 1, `${tag}: brick board count changed`);

  console.log(`${tag} passed (벽돌 ${brickScore}점 · 지렁이 ${snakeRun.score}점 · ${expectedTier})`);
}

// ---- 회귀: 단축키가 포커스된 버튼의 기본 키보드 동작(Space·Enter)을 가로채지 않는다 ----
async function checkArcadeKeyboard(browser, base, width) {
  const tag = `arcade keyboard ${width}px`;
  const context = await browser.newContext({ viewport: { width, height: 900 } });
  const page = await context.newPage();
  const read = () => page.evaluate(() => ({
    phase: document.getElementById('stage').getAttribute('data-phase'),
    game: document.getElementById('stage').getAttribute('data-game'),
    steps: Array.from(document.querySelectorAll('#guideSteps .gg-step.is-on')).map((el) => el.dataset.step),
    label: document.getElementById('guideReplay').textContent.trim(),
    focus: document.activeElement ? (document.activeElement.id || document.activeElement.tagName) : null,
  }));
  try {
    await page.goto(`${base}/arcade.html`, { waitUntil: 'load' });
    await page.evaluate(() => localStorage.removeItem('arcade_guide_seen_v1'));
    await page.reload({ waitUntil: 'load' });
    await page.locator('#guideReplay').waitFor({ state: 'attached' });

    // 1) '다시 보기' 버튼에 포커스를 두고 Space — 데모만 다시 재생되고 게임은 시작되지 않는다.
    await page.focus('#guideReplay');
    const opened = await read();
    assert.equal(opened.focus, 'guideReplay', `${tag}: focus ${opened.focus}`);
    assert.equal(opened.label, '다시 보기', `${tag}: replay label ${opened.label}`);
    await page.keyboard.press('Space');
    await page.waitForTimeout(160);
    const replayed = await read();
    assert.equal(replayed.phase, 'idle', `${tag}: Space on the guide button started the game (${replayed.phase})`);
    assert.deepEqual(replayed.steps, ['1'], `${tag}: Space did not replay the guide (${replayed.steps})`);

    // 2) Enter도 같은 규칙(버튼의 기본 클릭 동작 우선)
    await page.keyboard.press('Enter');
    await page.waitForTimeout(160);
    const replayedAgain = await read();
    assert.equal(replayedAgain.phase, 'idle', `${tag}: Enter on the guide button started the game (${replayedAgain.phase})`);
    assert.deepEqual(replayedAgain.steps, ['1'], `${tag}: Enter did not replay the guide (${replayedAgain.steps})`);

    // 3) 다른 대화형 요소(게임 전환 탭)에 포커스가 있어도 게임이 시작되지 않는다.
    await page.focus('#gameSnake');
    await page.keyboard.press('Space');
    await page.waitForTimeout(200);
    const switched = await read();
    assert.equal(switched.phase, 'idle', `${tag}: Space on the game switch started a run (${switched.phase})`);
    assert.equal(switched.game, 'snake', `${tag}: Space did not activate the focused game switch`);
    await page.focus('#gameBrick');
    await page.keyboard.press('Space');
    await page.waitForTimeout(160);

    // 4) 게임 영역(비대화형) 포커스에서는 단축키가 그대로 동작한다.
    await page.focus('#stage');
    await page.keyboard.press('Space');
    await page.waitForTimeout(300);
    const started = await read();
    assert.equal(started.phase, 'playing', `${tag}: Space in the game area did not start (${started.phase})`);
    await page.click('#quitBtn');
    console.log(`${tag} passed`);
  } finally {
    await page.close();
    await context.close();
  }
}

/* ---- 한글 한 칸 변신: 오늘 문제·연습 최단 경로 계획 ---- */
async function hangulPlan(page) {
  return page.evaluate(() => {
    const data = JSON.parse(document.getElementById('hangulData').textContent);
    const words = data.words;
    const adj = new Map();
    words.forEach((word) => adj.set(word, []));
    [0, 1].forEach((pos) => {
      const buckets = new Map();
      words.forEach((word) => {
        const key = word[pos];
        if (!buckets.has(key)) buckets.set(key, []);
        buckets.get(key).push(word);
      });
      buckets.forEach((group) => {
        for (let i = 0; i < group.length; i += 1) {
          for (let j = i + 1; j < group.length; j += 1) {
            adj.get(group[i]).push(group[j]);
            adj.get(group[j]).push(group[i]);
          }
        }
      });
    });
    const shortest = (start, goal) => {
      const previous = new Map([[start, null]]);
      const queue = [start];
      for (let head = 0; head < queue.length; head += 1) {
        const current = queue[head];
        if (current === goal) break;
        for (const next of adj.get(current)) {
          if (!previous.has(next)) {
            previous.set(next, current);
            queue.push(next);
          }
        }
      }
      if (!previous.has(goal)) return null;
      const path = [];
      for (let node = goal; node !== null; node = previous.get(node)) path.push(node);
      return path.reverse();
    };
    const toSteps = (path) => path.slice(1).map((word, index) => {
      const from = path[index];
      const pos = from[0] === word[0] ? 1 : 0;
      const code = word.charCodeAt(pos) - 0xAC00;
      return { pos, cho: data.cho[Math.floor(code / 588)], syllable: word[pos], word };
    });
    const t = new Date(Date.now() + 9 * 3600000);
    const pad = (n) => String(n).padStart(2, '0');
    const kst = `${t.getUTCFullYear()}-${pad(t.getUTCMonth() + 1)}-${pad(t.getUTCDate())}`;
    const ordinal = Math.floor(Date.parse(`${kst}T00:00:00Z`) / 86400000);
    const dailyPuzzle = data.daily[ordinal % data.daily.length];
    const practicePuzzle = data.practice[0];
    let invalid = null;
    for (const cho of Object.keys(data.syllableGroups)) {
      for (const syllable of data.syllableGroups[cho]) {
        if (syllable === dailyPuzzle.start[0]) continue;
        if (!words.includes(syllable + dailyPuzzle.start[1])) {
          invalid = { pos: 0, cho, syllable, word: syllable + dailyPuzzle.start[1] };
          break;
        }
      }
      if (invalid) break;
    }
    return {
      kst,
      ordinal,
      dailyPuzzle,
      dailySteps: toSteps(shortest(dailyPuzzle.start, dailyPuzzle.goal)),
      practicePuzzle,
      practiceSteps: toSteps(shortest(practicePuzzle.start, practicePuzzle.goal)),
      invalid,
      words: words.length,
    };
  });
}

async function hangulApply(page, step) {
  await page.click(`#wordRow .hg-syl[data-pos="${step.pos}"]`);
  await page.waitForTimeout(70);
  await page.click(`#letterChoRow .hg-cho[data-cho="${step.cho}"]`);
  await page.waitForTimeout(50);
  await page.click(`#letterGrid .hg-key[data-syllable="${step.syllable}"]`);
  await page.waitForTimeout(130);
}

function hangulRead(page) {
  return page.evaluate(() => ({
    word: document.getElementById('startWord').textContent,
    goal: document.getElementById('goalWord').textContent,
    title: document.getElementById('boardTitle').textContent,
    moves: Number(document.getElementById('moveValue').textContent),
    par: Number(document.getElementById('parValue').textContent),
    remain: document.getElementById('remainValue').textContent,
    stars: document.querySelectorAll('#starGauge .hg-star.is-on').length,
    status: document.getElementById('statusLine').textContent,
    streak: document.getElementById('streakChip').textContent,
    timer: document.getElementById('timerValue').textContent,
    resultHidden: document.getElementById('resultBox').hidden,
    padHidden: document.getElementById('pad').hidden,
    actionHidden: document.getElementById('actionRow').hidden,
    resultStars: document.querySelectorAll('#resultStars .hg-star.is-on').length,
    perfectHidden: document.getElementById('resultPerfect').hidden,
    undoDisabled: document.getElementById('undoBtn').disabled,
    practiceHidden: document.getElementById('practiceCard').hidden,
    recordBest: document.getElementById('recordBest').textContent,
    recordPlays: document.getElementById('recordPlays').textContent,
    dayBadge: { hidden: document.getElementById('dayBadge').hidden, text: document.getElementById('dayBadge').textContent },
    store: JSON.parse(localStorage.getItem('hangul_ladder_stats_v1') || 'null'),
  }));
}

async function checkHangulLayout(page, width) {
  const tag = `hangul layout ${width}px`;
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(120);

  const state = await page.evaluate(() => {
    const bar = document.querySelector('.ia-tabbar');
    const limit = bar && getComputedStyle(bar).display !== 'none'
      ? bar.getBoundingClientRect().top : window.innerHeight;
    const box = (sel) => {
      const node = document.querySelector(sel);
      if (!node) return null;
      const r = node.getBoundingClientRect();
      return { top: r.top, bottom: r.bottom, left: r.left, right: r.right, width: r.width };
    };
    return {
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      limit,
      units: document.querySelectorAll('#wordRow .hg-unit').length,
      syllables: document.querySelectorAll('#wordRow .hg-syl').length,
      parts: document.querySelectorAll('#wordRow .hg-part').length,
      jamoKeys: document.querySelectorAll('#jamoKeys .hg-key').length,
      steps: document.querySelectorAll('#guideStage .hg-demo-step').length,
      guideOpen: !document.getElementById('guideBody').hidden,
      guideLabel: document.getElementById('guideToggle').textContent.trim(),
      stars: document.querySelectorAll('#starGauge .hg-star.is-on').length,
      word: box('#wordRow'),
      pad: box('#pad'),
      actions: box('#actionRow'),
      status: box('#statusLine'),
      board: box('#board'),
      rail: box('.hg-rail'),
    };
  });
  assert.equal(state.overflow, 0, `${tag}: horizontal overflow ${state.overflow}px`);
  assert.equal(state.units, 2, `${tag}: word units ${state.units}`);
  assert.equal(state.syllables, 2, `${tag}: syllable tiles ${state.syllables}`);
  assert.equal(state.parts, 6, `${tag}: jamo cells ${state.parts}`);
  assert.equal(state.jamoKeys, 19, `${tag}: initial-consonant keys ${state.jamoKeys}`);
  assert.equal(state.steps, 3, `${tag}: guide steps ${state.steps}`);
  assert.equal(state.stars, 3, `${tag}: star gauge ${state.stars}`);
  assert.equal(state.guideOpen, true, `${tag}: guide should be open on the first visit`);
  assert.equal(state.guideLabel, '접기', `${tag}: guide toggle label ${state.guideLabel}`);
  assert.ok(state.word && state.word.bottom < state.limit,
    `${tag}: word row is below the first screen (${Math.round(state.word && state.word.bottom)}/${Math.round(state.limit)})`);
  assert.ok(state.pad && state.pad.top < state.limit, `${tag}: keypad is below the first screen`);
  assert.ok(state.actions && state.actions.bottom <= state.limit + 1,
    `${tag}: action buttons are cut by the first screen (${Math.round(state.actions && state.actions.bottom)}/${Math.round(state.limit)})`);
  if (width > 768) {
    assert.ok(state.rail.right <= state.board.left + 1, `${tag}: side rail is not left of the board`);
  }

  await page.click('#guideToggle');
  await page.waitForTimeout(160);
  const collapsed = await page.evaluate(() => ({
    hidden: document.getElementById('guideBody').hidden,
    label: document.getElementById('guideToggle').textContent.trim(),
    saved: localStorage.getItem('hangul_guide_seen_v1'),
  }));
  assert.equal(collapsed.hidden, true, `${tag}: guide did not collapse`);
  assert.equal(collapsed.label, '게임 방법', `${tag}: collapsed label ${collapsed.label}`);
  assert.equal(collapsed.saved, '1', `${tag}: guide seen flag not stored`);
  console.log(`${tag} passed`);
}

// ---- 한글 한 칸 변신: 잘못된 단어 거부 → 한 칸 이동 → 되돌리기 → 클리어 → 연습 모드 ----
async function checkHangulGame(page, width) {
  const tag = `hangul game ${width}px`;
  await page.evaluate(() => localStorage.removeItem('hangul_ladder_stats_v1'));
  await page.reload({ waitUntil: 'load' });
  await page.locator('#wordRow .hg-syl').first().waitFor({ state: 'attached' });
  const plan = await hangulPlan(page);
  assert.ok(plan.dailySteps.length === plan.dailyPuzzle.par,
    `${tag}: daily path length ${plan.dailySteps.length} vs par ${plan.dailyPuzzle.par}`);

  let state = await hangulRead(page);
  assert.equal(state.word, plan.dailyPuzzle.start, `${tag}: start ${state.word}`);
  assert.equal(state.goal, plan.dailyPuzzle.goal, `${tag}: goal ${state.goal}`);
  assert.equal(state.title, plan.dailyPuzzle.title, `${tag}: title ${state.title}`);
  assert.equal(state.par, plan.dailyPuzzle.par, `${tag}: par ${state.par}`);
  assert.equal(state.moves, 0, `${tag}: start moves ${state.moves}`);
  assert.equal(state.stars, 3, `${tag}: start stars ${state.stars}`);
  assert.equal(state.undoDisabled, true, `${tag}: undo enabled at start`);
  assert.equal(state.resultHidden, true, `${tag}: result shown at start`);
  assert.equal(state.padHidden, false, `${tag}: pad hidden at start`);
  assert.equal(state.practiceHidden, true, `${tag}: practice card shown in daily mode`);
  assert.equal(state.store, null, `${tag}: fresh storage expected`);
  assert.ok(state.remain.includes(String(plan.dailyPuzzle.par)), `${tag}: remain ${state.remain}`);

  // 사전에 없는 단어는 거부되고 이동으로 세지 않는다.
  assert.ok(plan.invalid, `${tag}: no invalid candidate`);
  await hangulApply(page, plan.invalid);
  state = await hangulRead(page);
  assert.equal(state.word, plan.dailyPuzzle.start, `${tag}: invalid word applied (${state.word})`);
  assert.equal(state.moves, 0, `${tag}: invalid word counted (${state.moves})`);
  assert.ok(state.status.includes('사전에 없는'), `${tag}: no rejection message (${state.status})`);

  // 한 칸 이동 + 되돌리기
  await hangulApply(page, plan.dailySteps[0]);
  state = await hangulRead(page);
  assert.equal(state.word, plan.dailySteps[0].word, `${tag}: first move ${state.word}`);
  assert.equal(state.moves, 1, `${tag}: moves after one step ${state.moves}`);
  assert.equal(state.undoDisabled, false, `${tag}: undo still disabled`);
  assert.ok(/^\d+:\d\d$/.test(state.timer), `${tag}: timer ${state.timer}`);

  await page.click('#undoBtn');
  await page.waitForTimeout(140);
  state = await hangulRead(page);
  assert.equal(state.word, plan.dailyPuzzle.start, `${tag}: undo word ${state.word}`);
  assert.equal(state.moves, 0, `${tag}: undo moves ${state.moves}`);
  assert.equal(state.undoDisabled, true, `${tag}: undo enabled after undo`);

  // 최소 이동으로 클리어 → 별 3개 · 스트릭 · 로컬 기록
  for (const step of plan.dailySteps) await hangulApply(page, step);
  state = await hangulRead(page);
  assert.equal(state.word, plan.dailyPuzzle.goal, `${tag}: goal word ${state.word}`);
  assert.equal(state.moves, plan.dailyPuzzle.par, `${tag}: cleared moves ${state.moves}`);
  assert.equal(state.resultHidden, false, `${tag}: result not shown`);
  assert.equal(state.padHidden, true, `${tag}: pad still shown after clear`);
  assert.equal(state.actionHidden, true, `${tag}: action row still shown after clear`);
  assert.equal(state.resultStars, 3, `${tag}: result stars ${state.resultStars}`);
  assert.equal(state.perfectHidden, false, `${tag}: perfect badge missing without hints`);
  assert.equal(state.streak, '연속 1회', `${tag}: streak ${state.streak}`);
  assert.ok(state.store && state.store.daily.days[plan.kst], `${tag}: daily record missing`);
  assert.equal(state.store.daily.days[plan.kst].clears, 1, `${tag}: daily clears ${state.store.daily.days[plan.kst].clears}`);
  assert.equal(state.store.daily.days[plan.kst].bestMoves, plan.dailyPuzzle.par, `${tag}: best moves mismatch`);
  assert.deepEqual(Object.keys(state.store.practice.puzzles), [], `${tag}: practice record written in daily mode`);
  assert.equal(state.recordBest, '3', `${tag}: record best ${state.recordBest}`);

  // 연습 모드 전환 · 힌트 사용 · 퍼펙트 배지 없음
  await page.click('#modePractice');
  await page.waitForTimeout(220);
  state = await hangulRead(page);
  assert.equal(state.practiceHidden, false, `${tag}: practice list missing`);
  assert.equal(state.word, plan.practicePuzzle.start, `${tag}: practice start ${state.word}`);
  assert.equal(state.goal, plan.practicePuzzle.goal, `${tag}: practice goal ${state.goal}`);
  assert.equal(await page.locator('#practiceList .hg-practice-btn').count(), 12, `${tag}: practice buttons`);

  await page.click('#hintBtn');
  await page.waitForTimeout(140);
  state = await hangulRead(page);
  const hintView = await page.evaluate(() => ({
    letter: !document.getElementById('letterKeys').hidden,
    chip: document.querySelector('#letterGrid .hg-key[data-hint="1"]')
      ? document.querySelector('#letterGrid .hg-key[data-hint="1"]').getAttribute('data-syllable') : null,
  }));
  assert.ok(state.status.startsWith('힌트'), `${tag}: hint message missing (${state.status})`);
  // 자모 한 칸 힌트이거나, 음절 교체 판이면 글자 모드 + 목표 음절 강조 중 하나다.
  assert.ok(/[ㄱ-ㅎ]/.test(state.status) || hintView.chip,
    `${tag}: 힌트가 자모도 목표 음절도 알려주지 않음 (${state.status})`);
  if (hintView.letter) {
    assert.ok(hintView.chip, `${tag}: 글자 모드 힌트에 목표 음절 강조가 없음`);
  }

  for (const step of plan.practiceSteps) await hangulApply(page, step);
  state = await hangulRead(page);
  assert.equal(state.resultHidden, false, `${tag}: practice clear not shown`);
  assert.equal(state.resultStars, 3, `${tag}: practice stars ${state.resultStars}`);
  assert.equal(state.perfectHidden, true, `${tag}: perfect badge shown after using a hint`);
  assert.ok(state.store.practice.puzzles[plan.practicePuzzle.id], `${tag}: practice record missing`);
  assert.equal(state.store.practice.puzzles[plan.practicePuzzle.id].clears, 1, `${tag}: practice clears`);
  assert.equal(state.store.daily.days[plan.kst].clears, 1, `${tag}: practice run leaked into the daily record`);
  assert.equal(state.recordPlays, '1판', `${tag}: practice plays ${state.recordPlays}`);
  console.log(`${tag} passed (${plan.dailyPuzzle.start}→${plan.dailyPuzzle.goal} ${plan.dailyPuzzle.par}수 · ${plan.practicePuzzle.start}→${plan.practicePuzzle.goal})`);
}

// ---- 한글 한 칸 변신: 가이드 1회 재생 후 정지 + 다시 보기 ----
async function checkHangulGuide(browser, base) {
  const tag = 'hangul guide';
  const context = await browser.newContext({ viewport: { width: 390, height: 900 } });
  const page = await context.newPage();
  try {
    await page.goto(`${base}/hangul.html`, { waitUntil: 'load' });
    await page.waitForTimeout(150);
    const start = await page.evaluate(() => ({
      tiles: Array.from(document.querySelectorAll('#guideTiles .hg-demo-tile')).map((node) => node.textContent),
      step: document.querySelector('#guideStage .hg-demo-step.is-on')
        ? document.querySelector('#guideStage .hg-demo-step.is-on').getAttribute('data-step') : null,
      open: !document.getElementById('guideBody').hidden,
    }));
    assert.equal(start.open, true, `${tag}: guide did not open automatically`);
    assert.equal(start.step, '1', `${tag}: first step ${start.step}`);
    assert.deepEqual(start.tiles, ['바', '다', '?'], `${tag}: start tiles ${start.tiles}`);

    await page.waitForTimeout(2900);
    const done = await page.evaluate(() => ({
      tiles: Array.from(document.querySelectorAll('#guideTiles .hg-demo-tile')).map((node) => node.textContent),
      step: document.querySelector('#guideStage .hg-demo-step.is-on')
        ? document.querySelector('#guideStage .hg-demo-step.is-on').getAttribute('data-step') : null,
      anims: document.getAnimations().length,
    }));
    assert.deepEqual(done.tiles, ['가', '지', '가지'], `${tag}: demo not stopped at the end (${done.tiles})`);
    assert.equal(done.step, '3', `${tag}: last step ${done.step}`);
    assert.equal(done.anims, 0, `${tag}: demo keeps moving after one play (${done.anims})`);

    await page.click('#guideReplay');
    await page.waitForTimeout(1200);
    const mid = await page.evaluate(() => Array.from(document.querySelectorAll('#guideTiles .hg-demo-tile')).map((node) => node.textContent));
    assert.deepEqual(mid, ['바', '지', '?'], `${tag}: replay did not restart (${mid})`);
    await page.waitForTimeout(1700);
    const again = await page.evaluate(() => Array.from(document.querySelectorAll('#guideTiles .hg-demo-tile')).map((node) => node.textContent));
    assert.deepEqual(again, ['가', '지', '가지'], `${tag}: replay did not settle (${again})`);
    console.log(`${tag} passed`);
  } finally {
    await context.close();
  }
}

// ---- 한글 힌트 분기: 자모 1칸으로 못 가면 글자 모드 + 목표 음절 강조 ----
async function checkHangulHintBranch(browser, base) {
  const tag = 'hangul hint branch';
  const context = await browser.newContext({ viewport: { width: 390, height: 900 } });
  const page = await context.newPage();
  try {
    await page.goto(`${base}/hangul.html`, { waitUntil: 'load' });
    await page.evaluate(() => localStorage.removeItem('hangul_ladder_stats_v1'));
    // 오늘의 일일판을 d01(의자→책상)로 고정한다: ordinal % length === 0 인 날짜로 시계를 맞춘다.
    const plan = await page.evaluate(() => {
      const t = new Date(Date.now() + 9 * 3600000);
      const pad = (n) => String(n).padStart(2, '0');
      const kst = `${t.getUTCFullYear()}-${pad(t.getUTCMonth() + 1)}-${pad(t.getUTCDate())}`;
      const ordinal = Math.floor(Date.parse(`${kst}T00:00:00Z`) / 86400000);
      const data = JSON.parse(document.getElementById('hangulData').textContent);
      const back = ordinal % data.daily.length;
      const target = new Date(Date.UTC(t.getUTCFullYear(), t.getUTCMonth(), t.getUTCDate() - back, 3));
      return { iso: target.toISOString(), puzzle: data.daily[0] };
    });
    assert.equal(plan.puzzle.id, 'd01', `${tag}: d01이 첫 일일판이 아님 (${plan.puzzle.id})`);
    assert.equal(plan.puzzle.start, '의자', `${tag}: start ${plan.puzzle.start}`);
    assert.equal(plan.puzzle.goal, '책상', `${tag}: goal ${plan.puzzle.goal}`);
    await page.clock.setFixedTime(new Date(plan.iso));
    await page.reload({ waitUntil: 'load' });
    await page.locator('#wordRow .hg-syl').first().waitFor({ state: 'attached' });
    let state = await hangulRead(page);
    assert.equal(state.word, '의자', `${tag}: board ${state.word}`);
    assert.equal(state.goal, '책상', `${tag}: goal ${state.goal}`);

    // 의자 → 사자/기자 는 초성·중성을 함께 바꿔야 한다(자모 1칸 불가) → 글자 모드 안내
    await page.click('#hintBtn');
    await page.waitForTimeout(180);
    const hinted = await page.evaluate(() => ({
      letterOpen: !document.getElementById('letterKeys').hidden,
      jamoOpen: !document.getElementById('jamoKeys').hidden,
      cho: document.querySelector('#letterChoRow .hg-cho.is-active')
        ? document.querySelector('#letterChoRow .hg-cho.is-active').getAttribute('data-cho') : null,
      chips: Array.from(document.querySelectorAll('#letterGrid .hg-key')).map((b) => b.getAttribute('data-syllable')),
      hintChip: document.querySelector('#letterGrid .hg-key[data-hint="1"]')
        ? document.querySelector('#letterGrid .hg-key[data-hint="1"]').getAttribute('data-syllable') : null,
      status: document.getElementById('statusLine').textContent,
      words: JSON.parse(document.getElementById('hangulData').textContent).words,
      chipCho: (() => {
        const chip = document.querySelector('#letterGrid .hg-key[data-hint="1"]');
        if (!chip) return null;
        const data = JSON.parse(document.getElementById('hangulData').textContent);
        const code = chip.getAttribute('data-syllable').charCodeAt(0) - 0xAC00;
        return data.cho[Math.floor(code / 588)];
      })(),
    }));
    assert.equal(hinted.letterOpen, true, `${tag}: 글자 모드로 전환되지 않음`);
    assert.equal(hinted.jamoOpen, false, `${tag}: 자모 팔레트가 남아 있음`);
    assert.ok(hinted.hintChip, `${tag}: 목표 음절 강조가 없음`);
    assert.ok(hinted.chips.includes(hinted.hintChip), `${tag}: 강조한 칩이 현재 초성 후보에 없음`);
    assert.equal(hinted.cho, hinted.chipCho, `${tag}: 강조 칩과 초성 필터가 어긋남 (${hinted.cho}/${hinted.chipCho})`);
    assert.ok(hinted.status.includes('강조'), `${tag}: 안내 문구 ${hinted.status}`);
    assert.ok(!hinted.status.includes('초성 →'), `${tag}: 자모 1칸이 안 되는 판에 자모 힌트를 줌 (${hinted.status})`);
    assert.ok(hinted.words.includes(hinted.hintChip + '자'), `${tag}: 힌트 음절이 실제 단어를 만들지 못함`);

    // 강조된 칩을 바로 누르면 실제 유효 이동이 된다 (긔자 같은 사전에 없는 단어가 나오지 않는다)
    await page.click('#letterGrid .hg-key[data-hint="1"]');
    await page.waitForTimeout(160);
    state = await hangulRead(page);
    assert.equal(state.word, hinted.hintChip + '자', `${tag}: 이동 결과 ${state.word}`);
    assert.equal(state.moves, 1, `${tag}: 이동 수 ${state.moves}`);
    assert.ok(!state.status.includes('사전에 없는'), `${tag}: 힌트가 사전에 없는 단어로 안내함 (${state.status})`);

    // 사자로 되돌려, 받침 한 칸만 다른 경우는 자모(받침) 힌트로 안내되는지 확인
    if (state.word !== '사자') {
      await page.click('#wordRow .hg-syl[data-pos="0"]');
      await page.waitForTimeout(90);
      await page.click('#letterChoRow .hg-cho[data-cho="ㅅ"]');
      await page.waitForTimeout(90);
      await page.click('#letterGrid .hg-key[data-syllable="사"]');
      await page.waitForTimeout(140);
    }
    state = await hangulRead(page);
    assert.equal(state.word, '사자', `${tag}: 되돌리기 실패 (${state.word})`);
    await page.click('#hintBtn');
    await page.waitForTimeout(180);
    const jamo = await page.evaluate(() => ({
      letterOpen: !document.getElementById('letterKeys').hidden,
      jamoOpen: !document.getElementById('jamoKeys').hidden,
      part: (() => {
        const cell = document.querySelector('#wordRow .hg-part.is-active');
        return cell ? cell.getAttribute('data-part') : null;
      })(),
      status: document.getElementById('statusLine').textContent,
    }));
    assert.equal(jamo.jamoOpen, true, `${tag}: 자모 힌트가 열리지 않음`);
    assert.equal(jamo.letterOpen, false, `${tag}: 한 칸 이동인데 글자 모드로 안내함`);
    assert.equal(jamo.part, 'jong', `${tag}: 선택 칸 ${jamo.part}`);
    assert.ok(/받침|종성/.test(jamo.status), `${tag}: 자모 힌트 문구 ${jamo.status}`);
    console.log(`${tag} passed (의자→사자 글자 모드 · 사자→사장 받침 힌트)`);
  } finally {
    await context.close();
  }
}

// ---- 한글 초성 팔레트: Enter/Space로 골라도 포커스가 body로 떨어지지 않는다 ----
async function checkHangulChoFocus(browser, base) {
  const tag = 'hangul cho focus';
  const context = await browser.newContext({ viewport: { width: 390, height: 900 } });
  const page = await context.newPage();
  try {
    await page.goto(`${base}/hangul.html`, { waitUntil: 'load' });
    await page.locator('#wordRow .hg-syl').first().waitFor({ state: 'attached' });
    await page.click('#wordRow .hg-syl[data-pos="1"]');
    await page.waitForTimeout(120);
    await page.evaluate(() => document.querySelector('#letterChoRow .hg-cho[data-cho="ㄴ"]').focus());
    assert.equal(await page.evaluate(() => document.activeElement.getAttribute('data-cho')), 'ㄴ',
      `${tag}: 초성 버튼에 포커스를 못 줌`);

    await page.keyboard.press('Enter');
    await page.waitForTimeout(140);
    let state = await page.evaluate(() => ({
      tag: document.activeElement ? document.activeElement.tagName : null,
      cho: document.activeElement ? document.activeElement.getAttribute('data-cho') : null,
      active: document.querySelector('#letterChoRow .hg-cho.is-active')
        ? document.querySelector('#letterChoRow .hg-cho.is-active').getAttribute('data-cho') : null,
      chips: document.querySelectorAll('#letterGrid .hg-key').length,
    }));
    assert.equal(state.tag, 'BUTTON', `${tag}: Enter 뒤 포커스가 ${state.tag}로 떨어짐`);
    assert.equal(state.cho, 'ㄴ', `${tag}: Enter 뒤 포커스 초성 ${state.cho}`);
    assert.equal(state.active, 'ㄴ', `${tag}: Enter로 초성 선택이 안 됨 (${state.active})`);
    assert.ok(state.chips > 0, `${tag}: 초성 ㄴ 후보가 비었음`);

    await page.keyboard.press('Space');
    await page.waitForTimeout(140);
    state = await page.evaluate(() => ({
      tag: document.activeElement ? document.activeElement.tagName : null,
      cho: document.activeElement ? document.activeElement.getAttribute('data-cho') : null,
      active: document.querySelector('#letterChoRow .hg-cho.is-active')
        ? document.querySelector('#letterChoRow .hg-cho.is-active').getAttribute('data-cho') : null,
    }));
    assert.equal(state.cho, 'ㄴ', `${tag}: Space 뒤 포커스 초성 ${state.cho}`);
    assert.equal(state.active, 'ㄴ', `${tag}: Space 뒤 초성 선택 ${state.active}`);

    // 키보드로 다른 초성까지 이동해도 재렌더 후 포커스가 유지된다
    await page.focus('#letterGrid .hg-key');
    assert.equal(await page.evaluate(() => document.activeElement.getAttribute('data-syllable') !== null), true,
      `${tag}: 음절 후보로 포커스 이동 실패`);
    console.log(`${tag} passed (Enter·Space 후 포커스 유지)`);
  } finally {
    await context.close();
  }
}

// ---- 한글 한 칸 변신: 자정을 넘긴 일일판은 시작일 기록으로 남는다 ----
async function checkHangulMidnight(browser, base) {
  const tag = 'hangul midnight';
  const context = await browser.newContext({ viewport: { width: 390, height: 900 } });
  const page = await context.newPage();
  try {
    await page.goto(`${base}/hangul.html`, { waitUntil: 'load' });
    await page.evaluate(() => localStorage.removeItem('hangul_ladder_stats_v1'));
    const plan = await hangulPlan(page);
    const [year, month, day] = plan.kst.split('-').map(Number);
    const next = new Date(Date.UTC(year, month - 1, day + 1));
    const pad = (n) => String(n).padStart(2, '0');
    const nextKey = `${next.getUTCFullYear()}-${pad(next.getUTCMonth() + 1)}-${pad(next.getUTCDate())}`;
    const nextPuzzle = plan.dailyPuzzle;
    const nextDaily = await page.evaluate((ordinal) => {
      const data = JSON.parse(document.getElementById('hangulData').textContent);
      return data.daily[(ordinal + 1) % data.daily.length];
    }, plan.ordinal);

    // KST 23:55에 탭을 열어 두고 한 수 진행
    await page.clock.setFixedTime(new Date(Date.UTC(year, month - 1, day, 14, 55)));
    await page.reload({ waitUntil: 'load' });
    await page.locator('#wordRow .hg-syl').first().waitFor({ state: 'attached' });
    let state = await hangulRead(page);
    assert.equal(state.title, nextPuzzle.title, `${tag}: board ${state.title}`);
    assert.equal(state.dayBadge.hidden, true, `${tag}: day badge shown before midnight`);

    await hangulApply(page, plan.dailySteps[0]);
    const progressed = await hangulRead(page);
    assert.equal(progressed.word, plan.dailySteps[0].word, `${tag}: first move ${progressed.word}`);
    assert.equal(progressed.moves, 1, `${tag}: moves ${progressed.moves}`);

    // 새로고침 없이 시계만 KST 00:05로 넘기고 탭을 다시 보이게 한다.
    await page.clock.setFixedTime(new Date(Date.UTC(year, month - 1, day, 15, 5)));
    await page.evaluate(() => document.dispatchEvent(new Event('visibilitychange')));
    await page.waitForTimeout(220);
    const kept = await hangulRead(page);
    assert.equal(kept.title, nextPuzzle.title, `${tag}: 진행 중인 판이 자정에 초기화됨`);
    assert.equal(kept.word, progressed.word, `${tag}: word reset at midnight (${kept.word})`);
    assert.equal(kept.moves, 1, `${tag}: moves reset at midnight (${kept.moves})`);
    assert.equal(kept.dayBadge.hidden, false, `${tag}: 새 날짜 안내 배지가 없음`);
    assert.ok(kept.dayBadge.text.includes('새 날짜 문제'), `${tag}: badge text ${kept.dayBadge.text}`);

    // 남은 수를 마저 두어 완주 — 판 시작일 기록으로 저장된다.
    for (const step of plan.dailySteps.slice(1)) await hangulApply(page, step);
    const done = await hangulRead(page);
    assert.equal(done.resultHidden, false, `${tag}: 자정을 넘긴 판을 마치지 못함`);
    assert.equal(done.moves, plan.dailyPuzzle.par, `${tag}: final moves ${done.moves}`);
    assert.ok(done.store && done.store.daily.days[plan.kst], `${tag}: 판 시작일 기록이 없음`);
    assert.equal(done.store.daily.days[plan.kst].clears, 1, `${tag}: 판 시작일 완주 ${done.store.daily.days[plan.kst].clears}`);
    assert.ok(!done.store.daily.days[nextKey], `${tag}: 자정을 넘긴 판이 새 날짜 기록으로 저장됨`);

    // '다시 하기'는 새 날짜 문제를 연다.
    await page.click('#retryBtn');
    await page.waitForTimeout(260);
    const restarted = await hangulRead(page);
    assert.equal(restarted.title, nextDaily.title, `${tag}: 새 날짜 문제 제목 ${restarted.title}`);
    assert.equal(restarted.moves, 0, `${tag}: 새 판 이동 ${restarted.moves}`);
    assert.equal(restarted.dayBadge.hidden, true, `${tag}: 새 판을 열었는데 배지가 남음`);
    console.log(`${tag} passed (${nextPuzzle.title} → ${nextDaily.title})`);
  } finally {
    await context.close();
  }
}

// ---- 오늘의 카드: 첫 화면(덱 전환·그림·핵심 한 줄·이전/다음) · 입력 필드 0 ----
async function checkCardsLayout(page, width) {
  const tag = `cards ${width}px`;
  const state = await page.evaluate(() => {
    const r = (sel) => {
      const el = document.querySelector(sel);
      if (!el) return null;
      const b = el.getBoundingClientRect();
      return { top: b.top, bottom: b.bottom, left: b.left, right: b.right, height: b.height };
    };
    const bar = document.querySelector('.ia-tabbar');
    return {
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      decks: r('.cd-decks'),
      art: r('#cdArt'),
      headline: r('#cdHeadline'),
      prev: r('#cdPrev'),
      next: r('#cdNext'),
      tabTop: bar ? bar.getBoundingClientRect().top : 0,
      viewport: window.innerHeight,
      dots: document.querySelectorAll('.cd-dot').length,
      hasArt: !!document.querySelector('#cdArt svg'),
      index: document.getElementById('cdIndex').textContent.trim(),
      theme: document.getElementById('cdTheme').textContent.trim(),
      source: document.getElementById('cdSource').textContent.trim(),
      action: document.getElementById('cdActionText').textContent.trim(),
      fields: document.querySelectorAll('input, textarea, select').length,
    };
  });
  assert.equal(state.overflow, 0, `${tag}: horizontal overflow ${state.overflow}px`);
  assert.ok(state.decks && state.decks.height >= 30, `${tag}: deck switch missing`);
  assert.equal(state.hasArt, true, `${tag}: card art missing`);
  assert.equal(state.dots, 3, `${tag}: expected 3 progress dots, got ${state.dots}`);
  assert.equal(state.index, '1 / 3', `${tag}: progress label ${state.index}`);
  assert.ok(state.theme.indexOf('오늘의 테마') === 0, `${tag}: theme label ${state.theme}`);
  assert.ok(state.source.length >= 10, `${tag}: health source line missing`);
  assert.ok(state.action.length >= 3, `${tag}: today action missing`);
  assert.equal(state.fields, 0, `${tag}: input fields are not allowed on this page`);

  const limit = width <= 768 ? state.tabTop - 2 : state.viewport;
  for (const key of ['decks', 'art', 'headline', 'prev', 'next']) {
    const box = state[key];
    assert.ok(box, `${tag}: ${key} missing`);
    assert.ok(box.top >= 0, `${tag}: ${key} starts above the viewport (${Math.round(box.top)})`);
    assert.ok(box.bottom <= limit, `${tag}: ${key} ends at ${Math.round(box.bottom)}, below ${Math.round(limit)}`);
  }
}

// ---- 오늘의 카드: 넘기기(버튼·키보드·스와이프) · 저장/저장한 카드 · 실천 체크 · 저장소 화이트리스트 ----
async function checkCardsFlow(page, width) {
  const tag = `cards flow ${width}px`;
  const read = () => page.evaluate(() => ({
    theme: document.getElementById('cdTheme').textContent.trim(),
    index: document.getElementById('cdIndex').textContent.trim(),
    headline: document.getElementById('cdHeadline').textContent.trim(),
    savedCount: document.getElementById('cdSavedCount').textContent.trim(),
    activeDeck: document.querySelector('.cd-deck.is-active').getAttribute('data-deck'),
    savedView: !document.getElementById('cdSavedList').hidden,
    cardHidden: document.getElementById('cdCard').hidden,
    savePressed: document.getElementById('cdSaveBtn').getAttribute('aria-pressed'),
    donePressed: document.getElementById('cdDoneBtn').getAttribute('aria-pressed'),
    doneMeter: document.getElementById('cdDoneMeter').textContent.trim(),
    rows: document.querySelectorAll('.cd-savedrow').length,
    emptyText: document.querySelector('.cd-empty strong') ? document.querySelector('.cd-empty strong').textContent.trim() : '',
    firstRow: document.querySelector('.cd-savedrow h3') ? document.querySelector('.cd-savedrow h3').textContent.trim() : '',
    allView: !document.getElementById('cdAllList').hidden,
    allRows: document.querySelectorAll('.cd-allrow').length,
    allGroups: document.querySelectorAll('.cd-allgroup').length,
  }));

  const first = await read();
  assert.equal(first.activeDeck, 'condition', `${tag}: default deck must be condition`);
  assert.equal(first.index, '1 / 3', `${tag}: initial progress ${first.index}`);
  assert.equal(first.savePressed, 'false', `${tag}: card must start unsaved`);

  await page.click('#cdNext');
  let state = await read();
  assert.equal(state.index, '2 / 3', `${tag}: next button did not advance`);
  assert.notEqual(state.headline, first.headline, `${tag}: headline did not change`);

  await page.keyboard.press('ArrowRight');
  assert.equal((await read()).index, '3 / 3', `${tag}: ArrowRight did not advance`);
  await page.keyboard.press('ArrowRight');
  assert.equal((await read()).index, '1 / 3', `${tag}: ArrowRight must wrap to the first card`);
  await page.keyboard.press('ArrowLeft');
  assert.equal((await read()).index, '3 / 3', `${tag}: ArrowLeft did not wrap backwards`);

  const art = await page.locator('#cdArt').boundingBox();
  assert.ok(art, `${tag}: art box missing for swipe`);
  await page.mouse.move(art.x + art.width * 0.82, art.y + art.height / 2);
  await page.mouse.down();
  await page.mouse.move(art.x + art.width * 0.18, art.y + art.height / 2, { steps: 8 });
  await page.mouse.up();
  await page.waitForTimeout(160);
  state = await read();
  assert.equal(state.index, '1 / 3', `${tag}: swipe left did not advance to the first card`);
  assert.equal(state.headline, first.headline, `${tag}: swiped card is not the first card`);

  await page.click('.cd-dot:nth-child(2)');
  const target = await read();
  assert.equal(target.index, '2 / 3', `${tag}: dot navigation failed`);

  await page.click('#cdSaveBtn');
  state = await read();
  assert.equal(state.savePressed, 'true', `${tag}: save state not set`);
  assert.equal(state.savedCount, '1', `${tag}: saved badge ${state.savedCount}`);
  const stored = await page.evaluate(() => JSON.parse(localStorage.getItem('daily_cards_saved_v1') || '[]'));
  assert.equal(stored.length, 1, `${tag}: saved id not written`);

  await page.click('#cdDeckSaved');
  state = await read();
  assert.equal(state.savedView, true, `${tag}: saved tab did not open`);
  assert.equal(state.cardHidden, true, `${tag}: card stage still visible in saved tab`);
  assert.equal(state.rows, 1, `${tag}: saved list rows ${state.rows}`);
  assert.equal(state.firstRow, target.headline, `${tag}: saved row headline mismatch`);

  await page.click('.cd-saved-remove');
  state = await read();
  assert.equal(state.rows, 0, `${tag}: saved row was not removed`);
  assert.ok(state.emptyText.indexOf('아직 저장한 카드가 없어요') === 0, `${tag}: empty state missing`);
  assert.equal(state.savedCount, '0', `${tag}: saved badge not reset`);

  await page.click('#cdDeckCondition');
  await page.click('#cdDoneBtn');
  state = await read();
  assert.equal(state.donePressed, 'true', `${tag}: done state not set`);
  assert.ok(state.doneMeter.indexOf('1/3') >= 0, `${tag}: today meter ${state.doneMeter}`);
  const done = await page.evaluate(() => JSON.parse(localStorage.getItem('daily_cards_done_v1') || '{}'));
  assert.equal(done.ids.length, 1, `${tag}: done id not written`);
  assert.match(done.date, /^\d{4}-\d{2}-\d{2}$/, `${tag}: done date ${done.date}`);

  await page.reload({ waitUntil: 'load' });
  assert.equal(await page.getAttribute('#cdDoneBtn', 'aria-pressed'), 'true', `${tag}: done state lost on reload`);

  await page.evaluate(() => {
    localStorage.setItem('daily_cards_saved_v1', JSON.stringify(['bogus-id', '<img src=x>', 12]));
    localStorage.setItem('daily_cards_done_v1', JSON.stringify({ date: '1999-01-01', ids: ['cond-sleep-1'] }));
  });
  await page.reload({ waitUntil: 'load' });
  assert.equal((await read()).savedCount, '0', `${tag}: unknown saved ids were not filtered`);
  assert.equal(await page.getAttribute('#cdDoneBtn', 'aria-pressed'), 'false', `${tag}: stale done date was not ignored`);
  assert.equal(await page.locator('.cd-savedrow').count(), 0, `${tag}: bogus saved row rendered`);

  await page.click('#cdDeckDigital');
  state = await read();
  assert.equal(state.activeDeck, 'digital', `${tag}: digital deck not active`);
  assert.equal(state.index, '1 / 3', `${tag}: deck switch must start at the first card`);
  assert.notEqual(state.headline, first.headline, `${tag}: digital deck shows the same headline`);
  assert.ok(state.theme.indexOf('2단계 인증') >= 0 || state.theme.indexOf('알림') >= 0 || state.theme.indexOf('와이파이') >= 0 || state.theme.indexOf('앱 권한') >= 0, `${tag}: digital theme ${state.theme}`);

  // 덱 전진 칩 4개(컨디션 · 디지털 · 전체 · 저장)와 칩 글자 넘침 없음
  const chips = await page.evaluate(() => Array.from(document.querySelectorAll('.cd-deck')).map((b) => b.getAttribute('data-deck')));
  assert.deepEqual(chips, ['condition', 'digital', 'all', 'saved'], `${tag}: deck chips ${chips.join(',')}`);
  const chipFit = await page.evaluate(() => Array.from(document.querySelectorAll('.cd-deck')).map((b) => b.scrollWidth - b.clientWidth));
  assert.ok(Math.max(...chipFit) <= 1, `${tag}: chip label clipped (${chipFit.join(',')})`);

  // 출처 원문 링크: https·새 창·noopener
  const sourceLink = await page.evaluate(() => {
    const a = document.querySelector('#cdSource a.cd-source-link');
    return a ? { href: a.getAttribute('href'), target: a.getAttribute('target'), rel: a.getAttribute('rel'), text: a.textContent.trim() } : null;
  });
  assert.ok(sourceLink, `${tag}: source original link missing`);
  assert.ok(sourceLink.href.startsWith('https://'), `${tag}: source href ${sourceLink.href}`);
  assert.equal(sourceLink.target, '_blank', `${tag}: source target ${sourceLink.target}`);
  assert.match(sourceLink.rel, /noopener/, `${tag}: source rel ${sourceLink.rel}`);
  assert.match(sourceLink.rel, /noreferrer/, `${tag}: source rel ${sourceLink.rel}`);

  // 전체 카드: 날짜와 상관없이 24장·8테마 + 테마별 목록에서 다른 테마 카드 열기
  await page.click('#cdDeckAll');
  await page.waitForTimeout(150);
  const allView = await page.evaluate(() => ({
    open: !document.getElementById('cdAllList').hidden,
    cardHidden: document.getElementById('cdCard').hidden,
    controlsHidden: document.getElementById('cdControls').hidden,
    rows: document.querySelectorAll('.cd-allrow').length,
    groups: document.querySelectorAll('.cd-allgroup').length,
    themes: Array.from(document.querySelectorAll('.cd-allgroup')).map((g) => g.getAttribute('data-theme')),
    links: document.querySelectorAll('.cd-allrow a.cd-source-link').length,
    hrefs: Array.from(document.querySelectorAll('.cd-allrow a.cd-source-link')).map((a) => a.getAttribute('href')),
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  }));
  assert.equal(allView.open, true, `${tag}: all-cards view did not open`);
  assert.equal(allView.cardHidden, true, `${tag}: card stage still visible in all-cards view`);
  assert.equal(allView.controlsHidden, true, `${tag}: prev/next still visible in all-cards view`);
  assert.equal(allView.rows, 24, `${tag}: all-cards rows ${allView.rows}`);
  assert.equal(allView.groups, 8, `${tag}: all-cards theme groups ${allView.groups}`);
  assert.equal(new Set(allView.themes).size, 8, `${tag}: theme groups ${allView.themes.join(',')}`);
  assert.ok(allView.links >= 21, `${tag}: all-cards source links ${allView.links}`);
  assert.ok(allView.hrefs.every((href) => href && href.startsWith('https://')), `${tag}: non-https source link in all-cards view`);
  assert.equal(allView.overflow, 0, `${tag}: all-cards view horizontal overflow ${allView.overflow}`);

  const pastRow = await page.evaluate(() => {
    const rotation = (typeof CD_DATA !== 'undefined') ? CD_DATA.rotation : {};
    const row = Array.from(document.querySelectorAll('.cd-allrow'))
      .find((r) => r.getAttribute('data-theme') !== rotation[r.getAttribute('data-deck')]);
    return row ? { id: row.getAttribute('data-card'), deck: row.getAttribute('data-deck'),
      theme: row.getAttribute('data-theme'), headline: row.getAttribute('data-headline') } : null;
  });
  assert.ok(pastRow, `${tag}: no card from a past theme in all-cards view`);
  await page.click(`.cd-allrow[data-card="${pastRow.id}"] .cd-allrow-open`);
  await page.waitForTimeout(150);
  const opened = await page.evaluate(() => ({
    cardHidden: document.getElementById('cdCard').hidden,
    allHidden: document.getElementById('cdAllList').hidden,
    headline: document.getElementById('cdHeadline').textContent.trim(),
    theme: document.getElementById('cdTheme').textContent.trim(),
    index: document.getElementById('cdIndex').textContent.trim(),
    activeDeck: document.querySelector('.cd-deck.is-active').getAttribute('data-deck'),
    source: document.getElementById('cdSource').textContent.trim(),
  }));
  assert.equal(opened.cardHidden, false, `${tag}: past-theme card did not open`);
  assert.equal(opened.allHidden, true, `${tag}: all-cards list still visible after opening a card`);
  assert.equal(opened.headline, pastRow.headline, `${tag}: opened "${opened.headline}" instead of "${pastRow.headline}"`);
  assert.equal(opened.activeDeck, pastRow.deck, `${tag}: active deck ${opened.activeDeck}`);
  assert.ok(opened.theme.startsWith('테마'), `${tag}: past-theme label ${opened.theme}`);
  assert.ok(opened.index.endsWith('/ 3'), `${tag}: past-theme progress ${opened.index}`);
  assert.ok(opened.source.length >= 10, `${tag}: past-theme source line ${opened.source}`);

  const pastTheme = opened.theme;
  await page.click('#cdNext');
  await page.waitForTimeout(120);
  assert.equal(await page.evaluate(() => document.getElementById('cdTheme').textContent.trim()), pastTheme,
    `${tag}: paging left the opened theme`);

  await page.click(pastRow.deck === 'condition' ? '#cdDeckCondition' : '#cdDeckDigital');
  await page.waitForTimeout(120);
  const backToToday = await page.evaluate(() => ({
    theme: document.getElementById('cdTheme').textContent.trim(),
    index: document.getElementById('cdIndex').textContent.trim(),
  }));
  assert.ok(backToToday.theme.startsWith('오늘의 테마'), `${tag}: deck chip did not return to today's theme (${backToToday.theme})`);
  assert.equal(backToToday.index, '1 / 3', `${tag}: today's theme progress ${backToToday.index}`);

  const pageErrors = await page.evaluate(() => window.smokeCspViolations || []);
  assert.deepEqual(pageErrors, [], `${tag}: CSP violations`);
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
    if (name === 'cve' && (width === 390 || width === 1280)) {
      await checkMarkedFeed(page, width, {
        name: 'cve', cardSel: '#cveList .cve-card', filterButton: '#cveFilterOpenBtn',
        summaryId: 'cveCollectionSummary', badgeId: 'cveFilterBadge',
        keys: { saved: 'cve_saved_v1', read: 'cve_read_v1' },
      });
    }
    if (name === 'ai') await checkAiFilters(page, width, `ai filter ${width}px`);
    if (name === 'ai' && (width === 390 || width === 1280)) {
      await checkMarkedFeed(page, width, {
        name: 'ai', cardSel: '#aiGrid .ai-card', filterButton: '#aiFilterOpenBtn',
        summaryId: 'aiCollectionSummary', badgeId: 'aiFilterBadge',
        keys: { saved: 'ai_saved_v1', read: 'ai_read_v1' },
      });
    }
    if ((name === 'ai' || name === 'cve') && (width === 390 || width === 1280)) {
      await checkMarkFocus(page, width, name);
    }
    if (name === 'study') await checkStudyHub(page, width, `study ${width}px`);
    if (name === 'study' && (width === 390 || width === 1280)) await checkStudyReviewQueue(page, width);
    if (name === 'clue') await checkClueGame(page, base, width);
    if (name === 'clue') await checkClueLayout(page, width);
    if (name === 'wargame') await checkWargame(page, width);
    if (name === 'radar') await checkRadar(page, width);
    if (name === 'tools') await checkTools(page, width);
    if (name === 'mission') await checkMissionGame(page, width);
    if (name === 'chart') await checkChartGame(page, base, width);
    if (name === 'ops') await checkOpsLayout(page, width);
    if (name === 'ops') await checkOpsGame(page, base, width);
    if (name === 'seat') await checkSeatLayout(page, width);
    if (name === 'seat') await checkSeatGame(page, width);
    if (name === 'load') await checkLoadLayout(page, width);
    if (name === 'load') await checkLoadGame(page, width);
    if (name === 'arcade') await checkArcadeLayout(page, width);
    if (name === 'arcade') await checkArcadeGame(page, width);
    if (name === 'hangul') await checkHangulLayout(page, width);
    if (name === 'hangul' && (width === 390 || width === 1280)) await checkHangulGame(page, width);
    if (name === 'cards') await checkCardsLayout(page, width);
    if (name === 'cards' && (width === 390 || width === 1280)) await checkCardsFlow(page, width);
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

// ---- 60초 관제실: 탭 스로틀링으로 65초를 한 번에 건너뛰어도 즉시 0.0초 종료·결과 카드 ----
async function checkOpsClockJump(browser, base) {
  const tag = 'ops clock jump';
  const context = await browser.newContext({ viewport: { width: 390, height: 900 } });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  try {
    await page.clock.install();
    await page.goto(`${base}/ops.html`, { waitUntil: 'load' });
    await page.locator('#alertBoard .ops-alert').first().waitFor({ state: 'attached' });
    await page.evaluate(() => localStorage.removeItem('ops_room_stats_v1'));
    await page.reload({ waitUntil: 'load' });
    await page.locator('#alertBoard .ops-alert').first().waitFor({ state: 'attached' });
    await page.click('#startBtn');
    await page.clock.runFor(1000);
    const ready = await page.evaluate(() => Array.from(document.querySelectorAll('#alertBoard .ops-alert'))
      .filter((card) => card.dataset.state === 'ready')
      .map((card) => ({ id: card.dataset.id, spec: card.dataset.spec })));
    assert.ok(ready.length >= 3, `${tag}: ${ready.length} alerts arrived in the first second`);
    for (const item of ready) {
      await page.click(`#person-${item.spec}`);
      await page.click(`.ops-alert[data-id="${item.id}"]`);
    }
    const running = await page.evaluate(() => ({
      hidden: document.getElementById('resultBox').hidden,
      clock: document.getElementById('clockValue').textContent.trim(),
    }));
    assert.equal(running.hidden, true, `${tag}: result shown before the jump`);
    // 탭이 백그라운드에서 스로틀되어 0.2초 콜백이 한 번만 돌아온 상황을 만든다.
    await page.clock.fastForward(65000);
    const end = await page.evaluate(() => ({
      clock: document.getElementById('clockValue').textContent.trim(),
      hidden: document.getElementById('resultBox').hidden,
      score: Number((document.getElementById('resultScore').textContent || '').replace(/[^0-9]/g, '')),
      completed: document.getElementById('resultCompleted').textContent.trim(),
      states: Array.from(document.querySelectorAll('#alertBoard .ops-alert')).map((card) => card.dataset.state),
      store: JSON.parse(localStorage.getItem('ops_room_stats_v1') || 'null'),
    }));
    assert.equal(end.hidden, false, `${tag}: result card missing after the 65s jump`);
    assert.equal(end.clock, '0.0', `${tag}: clock ${end.clock} after the 65s jump`);
    assert.ok(end.states.every((state) => state === 'done' || state === 'missed'),
      `${tag}: alerts left mid-run (${end.states})`);
    assert.ok(end.score >= 0, `${tag}: score ${end.score}`);
    assert.ok(end.completed.startsWith(String(ready.length)), `${tag}: completed summary ${end.completed}`);
    assert.ok(end.states.some((state) => state === 'missed'), `${tag}: jump skipped the misses (${end.states})`);
    assert.ok(end.store && end.store.history.length >= 1, `${tag}: jump run not stored`);
    assert.deepEqual(errors, [], `${tag}: browser errors`);
    console.log(`${tag} passed (${end.score}점 · ${end.completed})`);
  } finally {
    await context.close();
  }
}

// ---- 모바일 하단 '게임' 탭: 이동하지 않고 전체 시트의 게임 목록으로 스크롤·포커스 ----
async function checkGameTabSheet(browser, base, width) {
  const tag = `game tab sheet ${width}px`;
  const context = await browser.newContext({ viewport: { width, height: 900 } });
  const page = await context.newPage();
  try {
    await page.goto(`${base}/index.html`, { waitUntil: 'load' });
    await page.click('#iaGameBtn');
    await page.waitForFunction(() => !document.getElementById('iaSheet').hidden);
    await page.waitForTimeout(320);
    const state = await page.evaluate(() => {
      const sheet = document.getElementById('iaSheet');
      const group = document.getElementById('iaSheetGroupGame');
      const sr = sheet.getBoundingClientRect();
      const gr = group.getBoundingClientRect();
      const links = Array.from(document.querySelectorAll('.ia-sheet-link')).map((anchor) => anchor.getAttribute('href'));
      return {
        path: location.pathname,
        hidden: sheet.hidden,
        open: sheet.classList.contains('is-open'),
        focus: document.activeElement ? document.activeElement.id : null,
        scrollTop: sheet.scrollTop,
        groupTop: gr.top - sr.top,
        groupBottom: gr.bottom - sr.top,
        sheetHeight: sr.height,
        lastGameBottom: (() => {
          const hrefs = ['wargame.html', 'clue.html', 'mission.html', 'chart.html', 'arcade.html', 'ops.html', 'seat.html', 'load.html', 'hangul.html'];
          const nodes = Array.from(document.querySelectorAll('.ia-sheet-link'))
            .filter((anchor) => hrefs.includes(anchor.getAttribute('href')));
          return nodes.length ? nodes[nodes.length - 1].getBoundingClientRect().bottom - sr.top : -1;
        })(),
        groupText: group.textContent.trim(),
        arcade: links.includes('arcade.html'),
        hangul: links.includes('hangul.html'),
        subs: Array.from(document.querySelectorAll('.ia-sheet-sub')).map((el) => el.textContent.trim()),
        gameLinks: Array.from(document.querySelectorAll('.ia-sheet-link'))
          .filter((anchor) => ['wargame.html', 'clue.html', 'mission.html', 'chart.html', 'arcade.html', 'ops.html', 'seat.html', 'load.html', 'hangul.html']
            .includes(anchor.getAttribute('href'))).length,
      };
    });
    assert.equal(state.path, '/index.html', `${tag}: game tab navigated to ${state.path}`);
    assert.equal(state.hidden, false, `${tag}: sheet did not open`);
    assert.equal(state.open, true, `${tag}: sheet has no open state`);
    assert.equal(state.focus, 'iaSheetGroupGame', `${tag}: focus ${state.focus}`);
    assert.equal(state.groupText, '게임', `${tag}: group title ${state.groupText}`);
    assert.ok(state.scrollTop > 0, `${tag}: sheet did not scroll (${state.scrollTop})`);
    assert.ok(state.groupTop >= 0 && state.groupBottom <= state.sheetHeight + 1,
      `${tag}: game title outside the sheet viewport (${Math.round(state.groupTop)}~${Math.round(state.groupBottom)}/${Math.round(state.sheetHeight)})`);
    assert.ok(state.lastGameBottom > 0 && state.lastGameBottom <= state.sheetHeight + 1,
      `${tag}: last game link cut by the sheet (${Math.round(state.lastGameBottom)}/${Math.round(state.sheetHeight)})`);
    assert.ok(state.arcade, `${tag}: arcade.html missing from the game group`);
    assert.ok(state.subs.includes('미니게임'), `${tag}: mini games sub group missing`);
    assert.equal(state.gameLinks, 9, `${tag}: game links ${state.gameLinks}`);
    assert.ok(state.hangul, `${tag}: hangul.html missing from the game group`);
    await page.keyboard.press('Escape');
    await page.waitForFunction(() => document.getElementById('iaSheet').hidden);
    const focusBack = await page.evaluate(() => (document.activeElement ? document.activeElement.id : null));
    assert.equal(focusBack, 'iaGameBtn', `${tag}: focus did not return (${focusBack})`);
    console.log(`${tag} passed`);
  } finally {
    await context.close();
  }
}

// ---- 게임 고도화 1차: 워게임·추리·미션·차트 공통(1회 가이드·보드 강조·결과 격차) ----
async function checkGamePolish(browser, base) {
  const errors = [];
  const open = async (name, height) => {
    const context = await browser.newContext({ viewport: { width: 390, height: height || 900 } });
    const page = await context.newPage();
    page.on('pageerror', (error) => errors.push(`${name}: ${error.message}`));
    await page.goto(`${base}/${name}.html`, { waitUntil: 'load' });
    await page.evaluate(() => localStorage.clear());
    await page.reload({ waitUntil: 'load' });
    return { context, page };
  };

  // ---------- 워게임 ----------
  {
    const tag = 'wargame polish';
    const { context, page } = await open('wargame');
    try {
      await page.locator('#wgGuideStage .gg-step').first().waitFor({ state: 'attached' });
      await page.waitForTimeout(2300);
      const guide = await page.evaluate(() => ({
        steps: document.querySelectorAll('#wgGuideStage .gg-step').length,
        on: document.querySelector('#wgGuideStage .gg-step.is-on')
          ? document.querySelector('#wgGuideStage .gg-step.is-on').getAttribute('data-step') : null,
        verdict: document.querySelector('[data-demo-verdict]').hidden,
        seen: localStorage.getItem('wargame_demo_seen_v1'),
        replay: !!document.getElementById('wgGuideReplay'),
      }));
      assert.equal(guide.steps, 3, `${tag}: guide steps ${guide.steps}`);
      assert.equal(guide.on, '3', `${tag}: guide did not settle on the last step (${guide.on})`);
      assert.equal(guide.verdict, false, `${tag}: verdict chip missing at the end`);
      assert.equal(guide.seen, '1', `${tag}: guide autoplay not remembered`);
      assert.equal(guide.replay, true, `${tag}: 다시 보기 button missing`);

      await page.click('#wgGuideReplay');
      await page.waitForTimeout(120);
      const replay = await page.evaluate(() => document.querySelector('#wgGuideStage .gg-step.is-on')
        ? document.querySelector('#wgGuideStage .gg-step.is-on').getAttribute('data-step') : null);
      assert.equal(replay, '1', `${tag}: replay did not restart (${replay})`);

      const id = await page.evaluate(() => (DATA.find((q) => q.type === 'choice' && q.cat === 'web') || DATA.find((q) => q.type === 'choice')).id);
      await page.evaluate((qid) => { location.hash = '#q-' + qid; }, id);
      await page.reload({ waitUntil: 'load' });
      await page.waitForTimeout(250);
      const answered = await page.evaluate((qid) => {
        const card = document.getElementById('q-' + qid);
        const q = DATA.find((x) => x.id === qid);
        card.querySelector('.opt[data-idx="' + q.answer + '"]').click();
        return {
          lit: card.querySelectorAll('.code-block.is-lit').length,
          keyLines: card.querySelectorAll('.cl.is-key').length,
          badge: card.querySelector('.code-badge') ? card.querySelector('.code-badge').textContent : null,
          resultHidden: card.querySelector('.q-result').hidden,
          gap: card.querySelector('.q-result-text').textContent,
        };
      }, id);
      assert.ok(answered.lit > 0, `${tag}: 판단 근거 줄이 강조되지 않음`);
      assert.ok(answered.keyLines > 0, `${tag}: 근거 줄 span 없음`);
      assert.equal(answered.badge, '정답 근거', `${tag}: code badge "${answered.badge}"`);
      assert.equal(answered.resultHidden, false, `${tag}: 결과 영역이 숨어 있음`);
      assert.ok(answered.gap.includes('다음 티어'), `${tag}: 목표 격차 문구 "${answered.gap}"`);
      assert.ok(answered.gap.includes('퍼펙트'), `${tag}: 퍼펙트 격차 문구 "${answered.gap}"`);

      const retried = await page.evaluate((qid) => {
        const card = document.getElementById('q-' + qid);
        card.querySelector('.q-result-retry').click();
        return {
          resultHidden: card.querySelector('.q-result').hidden,
          lit: card.querySelectorAll('.code-block.is-lit').length,
          enabled: Array.from(card.querySelectorAll('.opt')).filter((o) => !o.disabled).length,
        };
      }, id);
      assert.equal(retried.resultHidden, true, `${tag}: 재도전 후 결과 영역이 남아 있음`);
      assert.equal(retried.lit, 0, `${tag}: 재도전 후 근거 강조가 남아 있음`);
      assert.ok(retried.enabled >= 3, `${tag}: 재도전 후 보기가 다시 열리지 않음 (${retried.enabled})`);
      console.log(`${tag} passed`);
    } finally {
      await context.close();
    }
  }

  // ---------- 3단서 추리 ----------
  {
    const tag = 'clue polish';
    const { context, page } = await open('clue');
    try {
      await page.waitForFunction(() => typeof currentId !== 'undefined' && !!currentId, null, { timeout: 5000 });
      await page.waitForTimeout(2300);
      const guide = await page.evaluate(() => ({
        steps: document.querySelectorAll('#clueGuideStage .gg-step').length,
        on: document.querySelector('#clueGuideStage .gg-step.is-on')
          ? document.querySelector('#clueGuideStage .gg-step.is-on').getAttribute('data-step') : null,
        pick: document.querySelector('[data-demo-pick]').hidden,
      }));
      assert.equal(guide.steps, 3, `${tag}: guide steps ${guide.steps}`);
      assert.equal(guide.on, '3', `${tag}: guide end step ${guide.on}`);
      assert.equal(guide.pick, false, `${tag}: demo verdict missing`);

      await page.click('#nextClue');
      await page.waitForTimeout(150);
      const two = await page.evaluate(() => ({
        dots: document.querySelectorAll('#pDots .dot.on').length,
        onSteps: document.querySelectorAll('#pDots .track-step.is-on').length,
        pop: document.querySelectorAll('#pDots .track-step.is-pop').length,
        fresh: document.querySelectorAll('#clueList .clue.is-fresh').length,
      }));
      assert.equal(two.dots, 2, `${tag}: clue dots ${two.dots}`);
      assert.equal(two.onSteps, 2, `${tag}: timeline steps ${two.onSteps}`);
      assert.equal(two.pop, 1, `${tag}: 방금 연 단서 단계가 움직이지 않음`);
      assert.equal(two.fresh, 1, `${tag}: 새로 열린 단서 카드 강조 없음`);

      const wrong = await page.evaluate(() => {
        const p = byId[currentId];
        return p.choices.map((_, i) => i).find((i) => i !== p.answer);
      });
      await page.click(`#options .opt[data-idx="${wrong}"]`);
      await page.waitForTimeout(150);
      const flash = await page.evaluate(() => ({
        hidden: document.getElementById('clueFlash').hidden,
        cls: document.getElementById('clueFlash').className,
      }));
      assert.equal(flash.hidden, false, `${tag}: 오답 피드백이 카드 위에 없음`);
      assert.ok(flash.cls.includes('no'), `${tag}: 오답 피드백 색상 ${flash.cls}`);

      const answer = await page.evaluate(() => byId[currentId].answer);
      await page.click(`#options .opt[data-idx="${answer}"]`);
      await page.waitForTimeout(250);
      const won = await page.evaluate(() => ({
        hidden: document.getElementById('resultBox').hidden,
        gap: document.getElementById('resultGapText').textContent,
        record: JSON.parse(localStorage.getItem('secjobs-clue-v1') || '{}')[currentId],
        flash: document.getElementById('clueFlash').className,
      }));
      assert.equal(won.hidden, false, `${tag}: 결과 박스가 열리지 않음`);
      assert.ok(won.gap.includes('연속'), `${tag}: 결과 격차 문구 "${won.gap}"`);
      assert.ok(won.gap.includes('최소 단서'), `${tag}: 단서 격차 문구 "${won.gap}"`);
      assert.ok(won.flash.includes('ok'), `${tag}: 정답 피드백 ${won.flash}`);
      assert.ok(won.record && won.record.solved, `${tag}: 해결 기록이 저장되지 않음`);

      await page.click('#retryBtn');
      await page.waitForTimeout(250);
      const practice = await page.evaluate(() => ({
        hidden: document.getElementById('resultBox').hidden,
        open: document.querySelectorAll('#clueList .clue.open').length,
        record: JSON.parse(localStorage.getItem('secjobs-clue-v1') || '{}')[currentId],
        enabled: Array.from(document.querySelectorAll('#options .opt')).filter((o) => !o.disabled).length,
      }));
      assert.equal(practice.hidden, true, `${tag}: 한 판 더 후 결과 박스가 남아 있음`);
      assert.equal(practice.open, 1, `${tag}: 연습 모드 단서 수 ${practice.open}`);
      assert.ok(practice.enabled === 4, `${tag}: 연습 모드 보기 ${practice.enabled}`);
      assert.ok(practice.record.solved, `${tag}: 연습 모드가 기록을 지움`);
      console.log(`${tag} passed`);
    } finally {
      await context.close();
    }
  }

  // ---------- 퇴근길 미션 ----------
  {
    const tag = 'mission polish';
    const { context, page } = await open('mission', 844);
    try {
      await page.locator('#board .cell').first().waitFor({ state: 'attached' });
      await page.waitForTimeout(2300);
      const guide = await page.evaluate(() => ({
        steps: document.querySelectorAll('#mgGuide .gg-step').length,
        on: document.querySelector('#mgGuide .gg-step.is-on')
          ? document.querySelector('#mgGuide .gg-step.is-on').getAttribute('data-step') : null,
        ghost: !!document.querySelector('.ghost-dot'),
        remain: document.getElementById('remainLabel').textContent.trim(),
        next: document.querySelectorAll('#board .cell.next').length,
      }));
      assert.equal(guide.steps, 3, `${tag}: guide steps ${guide.steps}`);
      assert.equal(guide.on, '3', `${tag}: guide end step ${guide.on}`);
      assert.equal(guide.ghost, true, `${tag}: 보드 위 가이드 점이 없음`);
      assert.ok(/최소까지 \d+수 남음|도착!/.test(guide.remain), `${tag}: 남은 수 문구 "${guide.remain}"`);
      assert.equal(guide.next, 1, `${tag}: 다음 이동 칸 강조 ${guide.next}`);

      const before = await page.evaluate(() => Number(document.getElementById('remainLabel').textContent.replace(/[^0-9]/g, '')));
      const nextCell = await page.evaluate(() => {
        const cell = document.querySelector('#board .cell.next');
        return { r: Number(cell.dataset.r), c: Number(cell.dataset.c) };
      });
      const pos = await page.evaluate(() => {
        const cur = document.querySelector('#board .cell.current');
        return { r: Number(cur.dataset.r), c: Number(cur.dataset.c) };
      });
      const key = missionKey([pos.r, pos.c], [nextCell.r, nextCell.c]);
      await page.keyboard.press(key);
      await page.waitForTimeout(220);
      const after = await page.evaluate(() => ({
        remain: document.getElementById('remainLabel').textContent.trim(),
        next: document.querySelectorAll('#board .cell.next').length,
      }));
      assert.equal(after.next, 1, `${tag}: 이동 후 다음 칸 강조 ${after.next}`);
      assert.equal(Number(after.remain.replace(/[^0-9]/g, '')), before - 1,
        `${tag}: 남은 수가 줄지 않음 (${before} → ${after.remain})`);
      assert.equal(await page.locator('#retryBtn').count(), 1, `${tag}: 결과 다시 도전 버튼 없음`);
      console.log(`${tag} passed`);
    } finally {
      await context.close();
    }
  }

  // ---------- 차트 추리실 ----------
  {
    const tag = 'chart polish';
    const { context, page } = await open('chart');
    try {
      await page.waitForFunction(() => typeof currentId !== 'undefined' && !!currentId, null, { timeout: 5000 });
      await page.waitForTimeout(2300);
      const guide = await page.evaluate(() => ({
        steps: document.querySelectorAll('#chartGuideStage .gg-step').length,
        on: document.querySelector('#chartGuideStage .gg-step.is-on')
          ? document.querySelector('#chartGuideStage .gg-step.is-on').getAttribute('data-step') : null,
        picked: !document.querySelector('[data-demo-chip="pick"]').classList.contains('is-pick') ? false : true,
      }));
      assert.equal(guide.steps, 3, `${tag}: guide steps ${guide.steps}`);
      assert.equal(guide.on, '3', `${tag}: guide end step ${guide.on}`);
      assert.equal(guide.picked, true, `${tag}: 예측 칩이 마지막 단계에 켜지지 않음`);

      const box = await page.evaluate(() => {
        const r = document.querySelector('#chartSvg').getBoundingClientRect();
        return { x: r.x, y: r.y, w: r.width, h: r.height };
      });
      await page.mouse.move(box.x + box.w * 0.45, box.y + box.h * 0.4);
      await page.waitForTimeout(220);
      const hover = await page.evaluate(() => ({
        hidden: document.getElementById('chartTip').hidden,
        text: document.getElementById('chartTip').textContent,
        hot: document.querySelectorAll('#chartSvg .is-hot').length,
        band: document.getElementById('hoverBand') ? document.getElementById('hoverBand').style.display : null,
      }));
      assert.equal(hover.hidden, false, `${tag}: 봉 툴팁이 뜨지 않음`);
      assert.ok(hover.text.includes('거래량'), `${tag}: 툴팁에 거래량 없음 (${hover.text})`);
      assert.ok(hover.text.includes('시가'), `${tag}: 툴팁에 시가 없음 (${hover.text})`);
      assert.ok(hover.hot > 0, `${tag}: 짚은 봉 하이라이트 없음`);
      assert.notEqual(hover.band, 'none', `${tag}: 봉 하이라이트 밴드가 숨겨져 있음`);

      const answer = await page.evaluate(() => byId[currentId].quiz.answer);
      await page.click(`#options .opt[data-idx="${answer}"]`);
      await page.waitForTimeout(260);
      const won = await page.evaluate(() => ({
        badgeHidden: document.getElementById('pickBadge').hidden,
        badge: document.getElementById('pickBadge').textContent,
        cls: document.getElementById('pickBadge').className,
        gap: document.getElementById('resultGapText').textContent,
      }));
      assert.equal(won.badgeHidden, false, `${tag}: 내 예측 배지가 없음`);
      assert.ok(won.badge.includes('내 예측'), `${tag}: 배지 문구 "${won.badge}"`);
      assert.ok(won.cls.includes('is-ok'), `${tag}: 정답 예측 배지 색 ${won.cls}`);
      assert.ok(won.gap.includes('연속 정답'), `${tag}: 결과 격차 문구 "${won.gap}"`);
      assert.ok(won.gap.includes('등급'), `${tag}: 등급 격차 문구 "${won.gap}"`);

      await page.click('#retryBtn');
      await page.waitForTimeout(260);
      const practice = await page.evaluate(() => ({
        hidden: document.getElementById('resultBox').hidden,
        badgeHidden: document.getElementById('pickBadge').hidden,
        open: document.querySelectorAll('#clueList .clue.open').length,
        solved: document.getElementById('solvedStat').textContent.trim(),
      }));
      assert.equal(practice.hidden, true, `${tag}: 다시 풀기 후 결과가 남아 있음`);
      assert.equal(practice.badgeHidden, true, `${tag}: 다시 풀기 후 예측 배지가 남아 있음`);
      assert.equal(practice.open, 0, `${tag}: 다시 풀기 단서 ${practice.open}`);
      assert.ok(practice.solved.startsWith('1 /'), `${tag}: 다시 풀기가 기록을 바꿈 (${practice.solved})`);
      console.log(`${tag} passed`);
    } finally {
      await context.close();
    }
  }

  assert.deepEqual(errors, [], `game polish: browser errors ${errors.join(' | ')}`);
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
          if (name === 'ops') await checkOpsLayout(page, width);
          if (name === 'seat') await checkSeatLayout(page, width);
          if (name === 'load') await checkLoadLayout(page, width);
          if (name === 'arcade') await checkArcadeLayout(page, width);
          if (name === 'hangul') await checkHangulLayout(page, width);
          if (name === 'cards') await checkCardsLayout(page, width);
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
    await checkTodayMidnight(browser, base);
    await checkTodayFocusKeep(browser, base);
    await checkOpsClockJump(browser, base);
    await checkHangulGuide(browser, base);
    await checkHangulHintBranch(browser, base);
    await checkHangulChoFocus(browser, base);
    await checkGamePolish(browser, base);
    await checkLoadPracticeRecord(browser, base);
    await checkLoadPerfectGap(browser, base);
    await checkChartPracticeStore(browser, base);
    await checkLoadMidnightRun(browser, base);
    await checkHangulMidnight(browser, base);
    await checkArcadeKeyboard(browser, base, 390);
    await checkArcadeKeyboard(browser, base, 1280);
    await checkGameTabSheet(browser, base, 320);
    await checkGameTabSheet(browser, base, 390);
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

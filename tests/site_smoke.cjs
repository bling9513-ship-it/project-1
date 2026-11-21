const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const path = require('node:path');
const { chromium } = require('playwright');

const pages = ['index', 'study', 'ai', 'cve', 'wargame', 'tools', 'radar', 'outfit', 'pick', 'clue', 'mission', 'chart'];
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
    await checkMissionMobile(browser, base);
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

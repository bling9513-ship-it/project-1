# -*- coding: utf-8 -*-
"""게임 4종(워게임·3단서 추리·퇴근길 미션·차트 추리실) 공통 '게임 방법' 데모 가이드.

원칙
- 이모지·그라데이션 없이 SVG 아이콘과 짧은 라벨만 쓴다.
- 처음 방문에 한 번만 자동 재생되고 마지막 장면에서 멈춘다. '다시 보기'로 언제든 재생.
- prefers-reduced-motion 이면 애니메이션 없이 마지막 장면을 바로 보여 준다.
- 건너뛰기 버튼은 없다. 데모는 실제 플레이 영역을 가리지 않으므로 바로 플레이할 수 있다.
- 390px 첫 화면에서 목표 1줄 + 데모 + 첫 조작이 함께 보이도록 높이를 150px 안쪽으로 묶는다.
"""

GUIDE_CSS = r"""
    /* ----- 게임 방법: 한 번만 움직이는 데모 (4종 공통) ----- */
    .gg-card {
      background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 12px; padding: 11px 12px 10px; margin: 0 0 10px;
      box-shadow: var(--card-shadow);
    }
    .gg-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .gg-head-actions { display: inline-flex; align-items: center; gap: 6px; }
    .gg-head h2 {
      display: inline-flex; align-items: center; gap: 5px;
      font-size: 12px; font-weight: 700; letter-spacing: -0.02em; color: var(--text-primary);
    }
    .gg-head h2 svg { color: var(--accent-primary); flex-shrink: 0; }
    .gg-auto { font-size: 9.5px; font-weight: 600; color: var(--text-muted); white-space: nowrap; }
    .gg-demo {
      position: relative; margin-top: 8px; padding: 9px 9px 8px;
      border: 1px solid var(--border-subtle); border-radius: 10px; background: var(--bg-page);
      overflow: hidden;
    }
    .gg-steps { display: flex; align-items: center; justify-content: center; gap: 5px; margin-top: 8px; }
    .gg-step {
      display: inline-flex; align-items: center; gap: 3px;
      font-size: 9px; font-weight: 600; line-height: 1.2; white-space: nowrap;
      color: var(--text-muted); padding: 2px 5px; border-radius: 999px;
      border: 1px solid transparent; transition: color 140ms ease, background-color 140ms ease, border-color 140ms ease;
    }
    .gg-step.is-done { color: var(--text-secondary); }
    .gg-step.is-on { color: var(--accent-primary); background: var(--accent-subtle); border-color: var(--border-default); }
    .gg-note { margin-top: 7px; font-size: 10px; line-height: 1.5; color: var(--text-muted); min-height: 15px; }
    .gg-replay {
      width: auto; border: 1px solid var(--border-default); border-radius: 7px;
      background: var(--bg-surface); color: var(--accent-primary);
      font-family: inherit; font-size: 10.5px; font-weight: 700; padding: 3px 8px;
      cursor: pointer; white-space: nowrap;
    }
    .gg-replay:hover { background: var(--bg-subtle); border-color: var(--border-strong); }
    .gg-replay:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    @media (max-width: 420px) {
      .gg-card { padding: 8px 10px 7px; }
      .gg-demo { margin-top: 6px; padding: 7px 8px 6px; }
      .gg-steps { margin-top: 6px; }
      .gg-note { margin-top: 5px; min-height: 13px; }
      .gg-replay { padding: 2px 6px; font-size: 10px; }
      .gg-step { font-size: 8.6px; padding: 2px 4px; }
    }
    @media (prefers-reduced-motion: reduce) {
      .gg-step { transition: none !important; }
    }
"""

_GUIDE_ICON = (
    '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<circle cx="12" cy="12" r="9"></circle><path d="M12 8v.01"></path><path d="M11 12h1v4h1"></path>'
    '</svg>'
)


def guide_html(prefix, stage_html, steps, note):
    """게임 방법 카드 마크업. stage_html 은 페이지별 미니 보드, steps 는 짧은 라벨 목록."""
    chips = "".join(
        '<span class="gg-step" data-step="%d">%s</span>' % (i + 1, label)
        for i, label in enumerate(steps)
    )
    return (
        '<section class="gg-card" id="%(p)sCard" aria-labelledby="%(p)sTitle">'
        '<div class="gg-head">'
        '<h2 id="%(p)sTitle">%(icon)s 게임 방법</h2>'
        '<div class="gg-head-actions">'
        '<span class="gg-auto">자동 1회</span>'
        '<button type="button" class="gg-replay" id="%(p)sReplay">다시 보기</button>'
        '</div>'
        '</div>'
        '<div class="gg-demo" id="%(p)sStage" aria-hidden="true">%(stage)s'
        '<div class="gg-steps" id="%(p)sSteps">%(chips)s</div>'
        '</div>'
        '<p class="gg-note" id="%(p)sNote">%(note)s</p>'
        '</section>'
    ) % {"p": prefix, "icon": _GUIDE_ICON, "stage": stage_html, "chips": chips, "note": note}


GUIDE_JS = r"""
  /* ---------------------------------------------------------- 게임 방법 데모
     처음 방문에 한 번만 자동 재생하고 마지막 장면에서 멈춘다. '다시 보기'로 재생.
     prefers-reduced-motion 이면 애니메이션 없이 마지막 장면만 보여 준다. */
  var GameGuide = (function () {
    var reduce = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
    var TIMING = [900, 1900];

    function create(opts) {
      var timers = [];
      var last = opts.notes.length;

      function clear() {
        timers.forEach(function (t) { window.clearTimeout(t); });
        timers = [];
      }

      function paintSteps(n) {
        var chips = opts.steps ? opts.steps.querySelectorAll('.gg-step') : [];
        for (var i = 0; i < chips.length; i += 1) {
          var step = Number(chips[i].getAttribute('data-step'));
          chips[i].classList.toggle('is-on', step === n);
          chips[i].classList.toggle('is-done', step < n);
        }
      }

      function apply(n) {
        paintSteps(n);
        if (opts.note) opts.note.textContent = opts.notes[n - 1];
        if (opts.step) opts.step(n);
      }

      function settle() {
        clear();
        if (opts.reset) opts.reset();
        apply(last);
      }

      function play() {
        clear();
        if (opts.reset) opts.reset();
        apply(1);
        if (reduce) { settle(); return; }
        TIMING.forEach(function (delay, index) {
          timers.push(window.setTimeout(function () { apply(index + 2); }, delay));
        });
      }

      var seen = null;
      try { seen = localStorage.getItem(opts.key); } catch (e) { seen = null; }
      if (seen || reduce) {
        settle();
        try { localStorage.setItem(opts.key, '1'); } catch (e) {}
      } else {
        try { localStorage.setItem(opts.key, '1'); } catch (e) {}
        play();
      }
      if (opts.replay) opts.replay.addEventListener('click', function () { play(); });

      return { play: play, settle: settle };
    }

    return { create: create, reduce: reduce };
  })();
"""

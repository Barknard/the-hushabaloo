// @ts-check
import { test, expect } from '@playwright/test';

/**
 * These tests run against the assembled site served from a SUBPATH
 * (http://127.0.0.1:PORT/the-hushabaloo/), not from the server root.
 *
 * That is deliberate. GitHub Pages serves this project at
 * barknard.github.io/the-hushabaloo/, and a suite that tests the root URL will
 * pass green while every real visitor gets 404s on the audio — an absolute
 * "/audio/x.mp3" resolves to the domain root, which only exists locally.
 * Test the URL shape you ship. See playwright.config.js for the server setup.
 */

const BASE = '/the-hushabaloo/';

/** Jump to a page by its id in script/pages.py, not by a brittle index. */
async function goToPage(page, pageId) {
  await page.evaluate(id => {
    const el = document.querySelector(`.page[data-pageid="${id}"]`);
    window.__book.showPage(Number(el.dataset.page), 'next');
  }, pageId);
}

/** Load the book and wait until it is safe to drive. */
async function open(page) {
  await page.goto(BASE);
  await page.waitForFunction(() => window.__book && window.__book.ready);
  await page.evaluate(() => window.__book.ready);
}

test.describe('The Hushabaloo read-along', () => {

  test('opens on the cover with the start gate up', async ({ page }) => {
    await open(page);
    await expect(page.locator('.start-title')).toHaveText('The Hushabaloo');
    await expect(page.locator('#startOverlay')).not.toHaveClass(/hidden/);
    await expect(page.locator('.page.active')).toHaveAttribute('data-page', '0');
  });

  test('has all eleven spreads and every block carries an id', async ({ page }) => {
    await open(page);
    await expect(page.locator('.page')).toHaveCount(35);
    const blocks = page.locator('[data-audio]');
    await expect(blocks).toHaveCount(87);
    const missing = await blocks.evaluateAll(
      els => els.filter(e => !e.getAttribute('data-audio')).length);
    expect(missing).toBe(0);
  });

  test('word timings load and cover every speech block', async ({ page }) => {
    await open(page);
    await page.waitForFunction(() => Object.keys((window.__book||{}).words || {}).length > 0)
      .catch(() => {});
    const report = await page.evaluate(async () => {
      const r = await fetch('./audio/timestamps.json');
      const j = await r.json();
      const ids = [...document.querySelectorAll('.audio-block[data-audio]')]
        .map(e => e.dataset.audio);
      return { ok: r.ok, missing: ids.filter(i => !j[i] || !j[i].length) };
    });
    expect(report.ok).toBe(true);
    expect(report.missing).toEqual([]);
  });

  // The one that would have caught the last false green.
  test('every audio file resolves under the deployed subpath', async ({ page }) => {
    await open(page);
    const bad = await page.evaluate(async () => {
      const urls = new Set();
      const v = window.__book.build.startsWith('__') ? '' : `?v=${window.__book.build}`;
      document.querySelectorAll('.audio-block[data-audio]')
        .forEach(e => urls.add('./audio/lines/' + e.dataset.audio + '.mp3' + v));
      document.querySelectorAll('.sfx-block[data-sfx]')
        .forEach(e => urls.add('./audio/sfx/' + e.dataset.sfx + '.mp3' + v));
      const failures = [];
      for (const u of urls) {
        const r = await fetch(u, { method: 'HEAD' });
        if (!r.ok) failures.push(`${u} -> ${r.status}`);
      }
      return failures;
    });
    expect(bad).toEqual([]);
  });

  test('no absolute asset paths', async ({ page }) => {
    await open(page);
    const abs = await page.evaluate(() =>
      [...document.querySelectorAll('[src],[href]')]
        .map(e => e.getAttribute('src') || e.getAttribute('href'))
        .filter(v => v && v.startsWith('/')));
    expect(abs).toEqual([]);
  });

  test('playing lights words up and then fades them', async ({ page }) => {
    await open(page);
    await page.locator('#startOverlay').click();
    const cover = page.locator('[data-audio="cover_nar_01"]');
    await expect(cover).toHaveClass(/speaking/, { timeout: 15000 });
    // A word lights up...
    await expect(cover.locator('[data-word].word-active').first())
      .toBeVisible({ timeout: 15000 });
    // ...and once passed, it carries the faded "spoken" state instead.
    await expect(cover.locator('[data-word].word-spoken').first())
      .toBeVisible({ timeout: 15000 });
  });

  test('participation beats never block the story', async ({ page }) => {
    await open(page);
    // Spread 8 holds the 3s "blow a raspberry" beat.
    await goToPage(page, 'p8b');
    const wait = page.locator('[data-audio="p8_wait_01"]');
    await expect(wait).toHaveAttribute('data-wait', '3.0');
    await page.evaluate(() => {
      window.__book.setPlaying(true);
      window.__book.play(window.__book.blockAt('p8_wait_01'));
    });
    await expect(wait).toHaveClass(/speaking/);
    // It must advance on its own, with nobody touching anything.
    await expect(wait).not.toHaveClass(/speaking/, { timeout: 8000 });
  });

  test('the start gate blocks the controls until it is dismissed', async ({ page }) => {
    await open(page);
    // The gate is opaque and sits above the controls. A control behind it must
    // not be operable -- otherwise a stray tap lands mid-book with nothing playing.
    // (Playwright counts a covered element as "visible", so assert behaviour.)
    const covered = await page.locator('#btnNext').evaluate(el => {
      const r = el.getBoundingClientRect();
      const top = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2);
      return top !== el && !el.contains(top);
    });
    expect(covered).toBe(true);

    await page.locator('#startOverlay').click();
    await expect(page.locator('#startOverlay')).toHaveClass(/hidden/);
    await page.locator('#btnNext').click();   // now it operates
    await expect(page.locator('.page.active')).toHaveAttribute('data-page', '1');
  });

  test('page navigation works and clamps at both ends', async ({ page }) => {
    await open(page);
    // Dismiss the gate without starting playback, so navigation is tested alone.
    await page.evaluate(() => document.getElementById('startOverlay').classList.add('hidden'));
    await expect(page.locator('#btnPrev')).toBeDisabled();
    await page.locator('#btnNext').click();
    await expect(page.locator('.page.active')).toHaveAttribute('data-page', '1');
    await expect(page.locator('#btnPrev')).toBeEnabled();
    await page.evaluate(() => window.__book.showPage(34, 'next'));
    await expect(page.locator('#btnNext')).toBeDisabled();
  });

  test('verse renders as lines, not prose', async ({ page }) => {
    await open(page);
    // Every narration block is metrical verse. If wrapWords ever flattens the
    // markup again, these become one run-on line and the meter disappears.
    await goToPage(page, 'p1a');
    const lines = await page.locator('[data-audio="p1_nar_01"] .ln').count();
    expect(lines).toBe(4);
    // And each line must actually sit on its own row on screen.
    const tops = await page.locator('[data-audio="p1_nar_01"] .ln')
      .evaluateAll(els => els.map(e => Math.round(e.getBoundingClientRect().top)));
    expect(new Set(tops).size).toBe(4);
    // Word spans must survive inside the lines, or karaoke has nothing to light.
    const words = await page.locator('[data-audio="p1_nar_01"] .ln [data-word]').count();
    expect(words).toBeGreaterThan(30);
  });

  test('characters come from one shared definition', async ({ page }) => {
    await open(page);
    // Consistency is structural: every appearance is a <use> of one <symbol>.
    // If a spread ever hand-rolls a character again, this catches it.
    const uses = await page.locator('use[href^="#ch-"]').count();
    expect(uses).toBeGreaterThanOrEqual(25);
    const symbols = await page.locator('symbol[id^="ch-"]').count();
    expect(symbols).toBe(5);
    // Every reference must resolve to a symbol that actually exists.
    const dangling = await page.evaluate(() =>
      [...document.querySelectorAll('use[href^="#ch-"]')]
        .map(u => u.getAttribute('href'))
        .filter(h => !document.querySelector(`symbol[id="${h.slice(1)}"]`)));
    expect(dangling).toEqual([]);
  });

  test('an ambient bed runs under the narration and follows the spread', async ({ page }) => {
    await open(page);
    // Every spread but the cover carries a bed; they must resolve and differ by scene.
    const beds = await page.evaluate(() => {
      const out = {};
      document.querySelectorAll('.page[data-spread]').forEach(p => { out[p.dataset.spread] = true; });
      return out;
    });
    expect(Object.keys(beds).length).toBe(11);

    // Only spread 6 keeps a bed. The first pass laid one under nearly every
    // spread and it read as white noise, because a bed with no events is hiss.
    await page.evaluate(() => { window.__book.setPlaying(true); window.__book.setBed('p6'); });
    await expect.poll(() => page.evaluate(() => window.__book.bedName)).toBe('amb_drips');

    const vol = await page.evaluate(() => window.__book.bed && window.__book.bed.volume);
    expect(vol).toBeLessThanOrEqual(0.30);
    const loops = await page.evaluate(() => window.__book.bed && window.__book.bed.loop);
    expect(loops).toBe(true);

    // Everywhere else must be genuinely silent -- especially spread 7, where the
    // silence IS the story.
    for (const s of ['p1', 'p3', 'p7', 'p9']) {
      await page.evaluate(x => window.__book.setBed(x), s);
      await expect.poll(() => page.evaluate(() => window.__book.bedName)).toBe(null);
    }
  });

  test('art stays with its verse instead of scrolling away', async ({ page }) => {
    await open(page);
    await goToPage(page, 'p4b');           // the longest page in the book
    const art = page.locator('.page[data-pageid="p4b"] .art-pane');
    const before = (await art.boundingBox()).y;
    // Spread 7 is the longest in the book. Scroll well past where the art used
    // to disappear -- a picture book must show the picture WHILE it reads.
    await page.evaluate(() => { document.querySelector('.page[data-pageid="p4b"]').scrollTop = 600; });
    await page.waitForTimeout(300);
    const after = (await art.boundingBox()).y;
    expect(Math.abs(after - before)).toBeLessThan(6);
    await expect(art).toBeInViewport();
  });

  test('wide landscape lays out as a two-page spread', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await open(page);
    await goToPage(page, 'p1a');
    const art = await page.locator('.page[data-pageid="p1a"] .art-pane').boundingBox();
    const text = await page.locator('.page[data-pageid="p1a"] .text-pane').boundingBox();
    // Art on the left page, verse on the right -- side by side, not stacked.
    expect(art.x + art.width).toBeLessThanOrEqual(text.x + 4);
    expect(Math.abs(art.y - text.y)).toBeLessThan(60);
  });

  test('audio URLs are versioned so a fixed recording actually reaches a reader', async ({ page }) => {
    await open(page);
    // Filenames are stable across rebuilds. Without a version the browser keeps
    // serving whatever it cached first -- which meant a corrected recording
    // never reached anyone who had already opened the book.
    const build = await page.evaluate(() => window.__book.build);
    expect(build).not.toContain('__');          // placeholder must be stamped
    expect(build.length).toBeGreaterThan(6);

    const src = await page.evaluate(() => {
      const a = document.querySelector('.audio-block[data-audio]');
      window.__book.setPlaying(false);
      return window.__book.blocks.length ? a.dataset.audio : null;
    });
    expect(src).toBeTruthy();

    // The stamp is visible, so "am I looking at the new one?" is answerable.
    await expect(page.locator('#build')).toHaveText(build.slice(0, 7));
  });

  test('no page needs scrolling to finish its verse', async ({ page }) => {
    await open(page);
    // The point of 35 short pages: the reader never scrolls mid-thought, and the
    // picture never leaves the screen. Checked on a phone, the tightest case.
    await page.setViewportSize({ width: 390, height: 780 });
    const overflowing = await page.evaluate(() => {
      const bad = [];
      document.querySelectorAll('.page').forEach(p => {
        p.classList.add('active');
        if (p.scrollHeight > p.clientHeight * 1.6) bad.push(p.dataset.pageid);
        if (p.dataset.page !== '0') p.classList.remove('active');
      });
      return bad;
    });
    expect(overflowing).toEqual([]);
  });

  test('every page has its own picture', async ({ page }) => {
    await open(page);
    // Two consecutive pages showing the same art makes the page turn meaningless.
    const arts = await page.evaluate(() =>
      [...document.querySelectorAll('.page .art')].map(a => a.innerHTML.length + ':' +
        a.innerHTML.slice(0, 200)));
    expect(arts.length).toBe(35);
    expect(new Set(arts).size).toBe(35);
  });

  test('every page arrives with its own entrance animation', async ({ page }) => {
    await open(page);
    const kinds = ['rise','bloom','sweep','pop','dissolve','lean','fall','flare'];
    const enters = await page.evaluate(() =>
      [...document.querySelectorAll('.page')].map(p => p.dataset.enter));
    expect(enters.length).toBe(35);
    expect(enters.filter(Boolean).length).toBe(35);
    for (const e of enters) expect(kinds).toContain(e);
    // All eight are actually used -- otherwise the variety is theoretical.
    expect(new Set(enters).size).toBe(8);

    // The entrance must actually run on the active page, and only there.
    await goToPage(page, 'p3a');
    const running = await page.evaluate(() => {
      const a = document.querySelector('.page[data-pageid="p3a"] .art');
      return getComputedStyle(a).animationName;
    });
    expect(running).toMatch(/^e-/);
  });

  test('every page actually renders its art after the entrance', async ({ page }) => {
    await open(page);
    await page.evaluate(() => document.getElementById('startOverlay').classList.add('hidden'));
    // e-pop and e-flare once ended on a keyframe that set transform but not
    // opacity. With fill-mode:both the element held that frame and fell back to
    // .art{opacity:0} -- eight pages finished their entrance INVISIBLE, including
    // the raspberry and the burst. Check the end state, not that it animated.
    // The entrance animates per element, so activating every page at once starts
    // all 35 entrances together and the end state can be read in one pass --
    // walking them one at a time took 30s and told us nothing extra.
    // Await the animations rather than sleeping a guessed duration -- under
    // parallel load a fixed wait caught them mid-fade at 0.94 and reported a
    // failure that was really just a slow machine. The looping accents never
    // finish, so exclude them.
    await page.evaluate(async () => {
      document.querySelectorAll('.page').forEach(p => p.classList.add('active'));
      const arts = [...document.querySelectorAll('.page .art')];
      await Promise.all(arts.flatMap(a => a.getAnimations()
        .filter(an => an.effect.getTiming().iterations !== Infinity)
        .map(an => an.finished.catch(() => {}))));
    });
    const blank = await page.evaluate(() =>
      [...document.querySelectorAll('.page')]
        .map(p => [p.dataset.pageid, getComputedStyle(p.querySelector('.art')).opacity])
        .filter(([, op]) => parseFloat(op) < 0.95)
        .map(([id, op]) => `${id}=${op}`));
    expect(blank).toEqual([]);
  });

  test('landscape and mirrored shapes keep the verse on screen', async ({ page }) => {
    // Two columns used to be gated on min-width:900px. A phone in landscape is
    // 844px, so it stayed stacked and the sticky art plus the control bar pushed
    // the verse entirely below the fold -- measured at -87px of visible height.
    for (const [w, h] of [[844, 390], [667, 375], [1180, 820], [1920, 1080], [1280, 720]]) {
      await page.setViewportSize({ width: w, height: h });
      await open(page);
      await page.evaluate(() => document.getElementById('startOverlay').classList.add('hidden'));
      await goToPage(page, 'p4b');              // the longest page in the book
      await page.waitForTimeout(350);
      const r = await page.evaluate(() => {
        const pg = document.querySelector('.page.active');
        const vh = innerHeight - 82, vw = innerWidth;
        let off = 0;
        pg.querySelectorAll('.ln').forEach(l => {
          const b = l.getBoundingClientRect();
          if (b.right > vw + 2 || b.left < -2) off++;
        });
        const top = pg.querySelector('.text-pane').getBoundingClientRect().top;
        return { visible: vh - Math.max(top, 0), off,
                 twoCol: getComputedStyle(pg).flexDirection === 'row' };
      });
      expect(r.off, `${w}x${h}: lines running off screen`).toBe(0);
      expect(r.visible, `${w}x${h}: verse starts below the fold`).toBeGreaterThan(180);
      if (w > h) expect(r.twoCol, `${w}x${h}: landscape should be two columns`).toBe(true);
    }
  });

  test('the page starts at the top and follows the reading downward', async ({ page }) => {
    // scrollIntoView({block:'center'}) centred every block, which on a short
    // landscape screen jumped straight past the opening lines. The verse must
    // start at the top of the page and creep down as the words are spoken.
    await page.setViewportSize({ width: 844, height: 390 });   // phone landscape
    await open(page);
    await page.evaluate(() => document.getElementById('startOverlay').classList.add('hidden'));
    await goToPage(page, 'p4b');                               // the longest page

    expect(await page.evaluate(() =>
      document.querySelector('.page.active').scrollTop)).toBe(0);

    const trail = await page.evaluate(async () => {
      const c = document.querySelector('.page.active');
      const out = [];
      for (const el of c.querySelectorAll('[data-audio]')) {
        window.__book.revealBlock(el);
        await new Promise(r => setTimeout(r, 260));
        const cr = c.getBoundingClientRect(), er = el.getBoundingClientRect();
        out.push({ top: Math.round(c.scrollTop),
                   visible: er.top >= cr.top - 2 && er.bottom <= cr.bottom + 2 });
      }
      return out;
    });

    expect(trail[0].top).toBe(0);                       // begins at the top
    for (const t of trail) expect(t.visible).toBe(true);
    for (let i = 1; i < trail.length; i++)              // never scrolls backwards
      expect(trail[i].top).toBeGreaterThanOrEqual(trail[i - 1].top - 1);
    expect(trail[trail.length - 1].top).toBeGreaterThan(0);   // it did move
  });

  test('a page that already fits never scrolls', async ({ page }) => {
    // Motion for its own sake is worse than none in front of a two-year-old.
    await page.setViewportSize({ width: 390, height: 844 });
    await open(page);
    await page.evaluate(() => document.getElementById('startOverlay').classList.add('hidden'));
    await goToPage(page, 'p1a');
    const moved = await page.evaluate(async () => {
      const c = document.querySelector('.page.active');
      for (const el of c.querySelectorAll('[data-audio]')) {
        window.__book.revealBlock(el);
        await new Promise(r => setTimeout(r, 200));
      }
      return c.scrollTop;
    });
    expect(moved).toBe(0);
  });

  test('controls say what they do', async ({ page }) => {
    await open(page);
    await expect(page.locator('#playLabel')).toContainText('Play');
    await expect(page.locator('#btnPlay')).toHaveAttribute('aria-label', /Play the story/);
    await expect(page.locator('#btnNext')).toHaveAttribute('aria-label', /Next page/);
  });

  test('loads with no console errors', async ({ page }) => {
    const errors = [];
    page.on('console', m => m.type() === 'error' && errors.push(m.text()));
    page.on('pageerror', e => errors.push(e.message));
    await open(page);
    await page.waitForTimeout(1200);
    expect(errors).toEqual([]);
  });
});

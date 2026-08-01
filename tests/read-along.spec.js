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
    await expect(page.locator('.page')).toHaveCount(11);
    const blocks = page.locator('[data-audio]');
    await expect(blocks).toHaveCount(85);
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
      document.querySelectorAll('.audio-block[data-audio]')
        .forEach(e => urls.add('./audio/lines/' + e.dataset.audio + '.mp3'));
      document.querySelectorAll('.sfx-block[data-sfx]')
        .forEach(e => urls.add('./audio/sfx/' + e.dataset.sfx + '.mp3'));
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
    await page.evaluate(() => window.__book.showPage(8, 'next'));
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
    await page.evaluate(() => window.__book.showPage(10, 'next'));
    await expect(page.locator('#btnNext')).toBeDisabled();
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

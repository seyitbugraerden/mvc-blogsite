// Optional browser checks: PLAYWRIGHT_MODULE and BROWSER_EXECUTABLE may point to local installations.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const net = require('net');
(async () => {
    const socket = net.createServer();
    await new Promise(resolve => socket.listen(0, '127.0.0.1', resolve));
    const base = `http://127.0.0.1:${socket.address().port}`;
    await new Promise(resolve => socket.close(resolve));
    const root = path.resolve(__dirname, '../Voku.Web');
    const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'voku-blog-browser-'));
    const server = spawn('dotnet', [path.join(root, 'bin/Debug/net10.0/Voku.Web.dll')], {
        cwd: root, env: { ...process.env, ASPNETCORE_ENVIRONMENT: 'Development', ASPNETCORE_URLS: base,
            Admin__RequireAuthentication: 'false', ConnectionStrings__Default: `Data Source=${temp}/test.db` }, stdio: 'ignore'
    });
    let browser;
    try {
        for (let i = 0; i < 150; i++) {
            try { if ((await fetch(base)).ok) break; } catch {}
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        browser = await chromium.launch({ headless: true, ...(process.env.BROWSER_EXECUTABLE ? { executablePath: process.env.BROWSER_EXECUTABLE } : {}) });
        const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
        const errors = [];
        page.on('pageerror', error => errors.push(error.message));
        await page.goto(base + '/admin/posts/new');
        await page.locator('#Title').fill('Tarayıcı testi yazısı');
        await page.locator('#Slug').fill('tarayici-testi');
        await page.locator('#Description').fill('Dinamik kart özeti');
        await page.locator('#CoverImageUrl').fill('/images/img-7.jpg');
        await page.locator('#Category').fill('Gezi');
        await page.locator('#Author').fill('Test yazarı');
        await page.locator('#PublishedAtUtc').fill('2040-01-02T12:00');
        await page.locator('#Published').check();
        const paragraph = page.locator('#visual-fields textarea').first();
        await paragraph.fill('Görsel editörden kaydedilen yazı gövdesi.');
        await page.locator('button.primary').click();
        await page.waitForURL('**/admin/posts/tarayici-testi/edit');
        for (const route of ['/', '/blog']) {
            await page.goto(base + route);
            const card = page.locator('[data-post-slug="tarayici-testi"]');
            if (!await card.isVisible()) throw Error('New card missing on ' + route);
            if (!await card.getByText('Dinamik kart özeti').isVisible()) throw Error('Excerpt missing');
            await card.locator('img').scrollIntoViewIfNeeded();
            await page.waitForFunction(() => document.querySelector('[data-post-slug="tarayici-testi"] img').naturalWidth > 0);
        }
        await page.locator('.blog-filters').getByRole('link', { name: 'Gezi', exact: true }).click();
        if (await page.locator('.blog-card').count() !== 1) throw Error('Category filter failed');
        await page.locator('.blog-card h3 a').click();
        await page.waitForURL('**/blog/tarayici-testi');
        if ((await page.locator('h1').textContent()).trim() !== 'Tarayıcı testi yazısı') throw Error('Detail title mismatch');
        if (!await page.getByText('Görsel editörden kaydedilen yazı gövdesi.').isVisible()) throw Error('Article body missing');
        await page.goto(base + '/admin/posts/tarayici-testi/edit');
        await page.locator('#Title').fill('Güncel yazı');
        await page.locator('#Slug').fill('guncel-yazi');
        await page.locator('button.primary').click();
        await page.waitForURL('**/admin/posts/guncel-yazi/edit');
        await page.goto(base + '/');
        await page.locator('[data-post-slug="guncel-yazi"] h3 a').click();
        await page.waitForURL('**/blog/guncel-yazi');
        if ((await page.locator('h1').textContent()).trim() !== 'Güncel yazı') throw Error('Edited title mismatch');
        const screenshotDir = process.env.SCREENSHOT_DIR || temp;
        fs.mkdirSync(screenshotDir, { recursive: true });
        for (const route of ['/', '/blog', '/blog/guncel-yazi']) {
            await page.setViewportSize({ width: 1440, height: 1000 });
            await page.goto(base + route);
            const name = route === '/' ? 'home' : route.replaceAll('/', '-');
            await page.screenshot({ path: path.join(screenshotDir, name + '-desktop.png'), fullPage: true });
            await page.setViewportSize({ width: 390, height: 844 });
            await page.screenshot({ path: path.join(screenshotDir, name + '-mobile.png'), fullPage: true });
            if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 2)) throw Error('Mobile overflow: ' + route);
        }
        if (errors.length) throw Error(errors.join('\n'));
        console.log('PASS: browser creation, metadata, visual editor, categories, slug/title updates and desktop/mobile layouts.');
    } finally {
        if (browser) await browser.close();
        const closed = new Promise(resolve => server.once('exit', resolve));
        server.kill();
        if (server.exitCode === null) await closed;
        fs.rmSync(temp, { recursive: true, force: true });
    }
})().catch(error => { console.error(error); process.exitCode = 1; });

// Optional PDF renderer: install Playwright separately and set PLAYWRIGHT_MODULE if needed.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const path = require('path');
const { pathToFileURL } = require('url');
(async () => {
    const options = { headless: true };
    if (process.env.BROWSER_EXECUTABLE) options.executablePath = process.env.BROWSER_EXECUTABLE;
    const browser = await chromium.launch(options);
    try {
        const page = await browser.newPage();
        await page.goto(pathToFileURL(path.join(__dirname, 'Voku-CMS-Egitim-Rehberi.html')).href);
        await page.emulateMedia({ media: 'print' });
        await page.pdf({
            path: path.join(__dirname, 'Voku-CMS-Egitim-Rehberi.pdf'),
            format: 'A4', printBackground: true, preferCSSPageSize: true,
            displayHeaderFooter: true, headerTemplate: '<div></div>',
            footerTemplate: '<div style="width:100%;font-size:8px;color:#65776c;padding:0 17mm;display:flex;justify-content:space-between"><span>VOKU CMS · PROJE VE MİMARİ EĞİTİM REHBERİ</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
            tagged: true, outline: true
        });
        console.log('PDF created; chapters:', await page.locator('.chapter').count());
    } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });

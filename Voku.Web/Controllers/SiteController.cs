using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Voku.Web.Data;
using Voku.Web.Models;
namespace Voku.Web.Controllers;
public class SiteController(SiteDbContext db) : Controller
{
    private const int PageSize = 6;
    [HttpGet("/")]
    public Task<IActionResult> Home() => Render("home", false, null, 1);
    [HttpGet("/{slug}")]
    public Task<IActionResult> Page(string slug, [FromQuery] string? category, [FromQuery(Name = "page")] int number = 1)
        => Render(slug, false, category, number);
    [HttpGet("/blog/{slug}")]
    public Task<IActionResult> Detail(string slug) => Render(slug, true, null, 1);
    [Route("/server-error")]
    public IActionResult ServerError() => Problem("İşlem tamamlanamadı. Lütfen tekrar deneyin.");

    private async Task<IActionResult> Render(string slug, bool detail, string? category, int number)
    {
        var page = await db.Pages.AsNoTracking().SingleOrDefaultAsync(p => p.Slug == slug && p.IsDetail == detail && p.Published);
        if (page == null)
        {
            Response.StatusCode = 404;
            page = await db.Pages.AsNoTracking().SingleOrDefaultAsync(p => p.Slug == "error" && !p.IsDetail && p.Published);
            if (page == null) return NotFound();
        }
        if (!page.IsDetail && page.Slug is "home" or "blog")
        {
            var query = db.Pages.AsNoTracking().Where(p => p.IsDetail && p.Published);
            var categories = await query.Where(p => p.Category != null && p.Category != "")
                .Select(p => p.Category!).Distinct().OrderBy(c => c).ToListAsync();
            category = page.Slug == "blog" ? category?.Trim() : null;
            if (!string.IsNullOrEmpty(category)) query = query.Where(p => p.Category == category);
            var count = await query.CountAsync();
            var totalPages = (int)Math.Ceiling(count / (double)PageSize);
            number = Math.Clamp(number, 1, Math.Max(1, totalPages));
            var posts = await query.OrderByDescending(p => p.PublishedAtUtc).ThenByDescending(p => p.Id)
                .Skip((number - 1) * PageSize).Take(PageSize).ToListAsync();
            return View("Page", new SitePageViewModel { Page = page, Posts = posts, Categories = categories,
                Category = category, PageNumber = number, TotalPages = totalPages, TotalPosts = count });
        }
        if (page.IsDetail)
        {
            var home = await db.Pages.AsNoTracking().SingleOrDefaultAsync(p => p.Slug == "home" && !p.IsDetail);
            return View("Page", new SitePageViewModel { Page = page,
                HeaderHtml = BlogMarkup.Chrome(home?.BodyHtml ?? page.BodyHtml, "header"),
                FooterHtml = BlogMarkup.Chrome(home?.BodyHtml ?? page.BodyHtml, "footer") });
        }
        return View("Page", new SitePageViewModel { Page = page });
    }
}

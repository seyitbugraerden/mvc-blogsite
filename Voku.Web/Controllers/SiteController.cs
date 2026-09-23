using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Voku.Web.Data;
namespace Voku.Web.Controllers;
public class SiteController(SiteDbContext db) : Controller
{
    [HttpGet("/")]
    public Task<IActionResult> Home() => Render("home", false);
    [HttpGet("/{slug}")]
    public Task<IActionResult> Page(string slug) => Render(slug, false);
    [HttpGet("/blog/{slug}")]
    public Task<IActionResult> Detail(string slug) => Render(slug, true);
    [Route("/server-error")]
    public IActionResult ServerError() => Problem("İşlem tamamlanamadı. Lütfen tekrar deneyin.");
    private async Task<IActionResult> Render(string slug, bool detail)
    {
        var page = await db.Pages.AsNoTracking().SingleOrDefaultAsync(p => p.Slug == slug && p.IsDetail == detail && p.Published);
        if (page == null)
        {
            Response.StatusCode = 404;
            page = await db.Pages.AsNoTracking().SingleOrDefaultAsync(p => p.Slug == "error" && !p.IsDetail && p.Published);
            if (page == null) return NotFound();
        }
        ViewBag.Posts = await db.Pages.AsNoTracking().Where(p => p.IsDetail && p.Published).OrderByDescending(p => p.UpdatedUtc).ToListAsync();
        return View("Page", page);
    }
}

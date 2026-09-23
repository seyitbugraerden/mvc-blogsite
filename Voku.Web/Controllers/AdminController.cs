using System.Security.Claims;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.EntityFrameworkCore;
using Voku.Web.Data;
using Voku.Web.Models;
namespace Voku.Web.Controllers;
[Authorize, Route("admin")]
public class AdminController(SiteDbContext db) : Controller
{
    [AllowAnonymous, HttpGet("login")]
    public IActionResult Login() => View(new LoginModel());
    [AllowAnonymous, HttpPost("login"), EnableRateLimiting("login")]
    public async Task<IActionResult> Login(LoginModel input)
    {
        if (!ModelState.IsValid) return View(input);
        var user = await db.AdminUsers.SingleOrDefaultAsync(u => u.Username == input.Username);
        if (user == null || new PasswordHasher<AdminUser>().VerifyHashedPassword(user, user.PasswordHash, input.Password) == PasswordVerificationResult.Failed)
        { ModelState.AddModelError("", "Kullanıcı adı veya şifre hatalı."); return View(input); }
        await HttpContext.SignInAsync(CookieAuthenticationDefaults.AuthenticationScheme, new ClaimsPrincipal(new ClaimsIdentity(new[] { new Claim(ClaimTypes.Name, user.Username) }, CookieAuthenticationDefaults.AuthenticationScheme)));
        return RedirectToAction(nameof(Index));
    }
    [HttpPost("logout")]
    public async Task<IActionResult> Logout() { await HttpContext.SignOutAsync(); return RedirectToAction(nameof(Login)); }
    [HttpGet("")]
    public async Task<IActionResult> Index() => View(await db.Pages.AsNoTracking().OrderBy(p => p.IsDetail).ThenBy(p => p.Title).ToListAsync());
    [HttpGet("pages/{slug}/edit")]
    public Task<IActionResult> EditPage(string slug) => Editor(slug, false);
    [HttpGet("posts/{slug}/edit")]
    public Task<IActionResult> EditPost(string slug) => Editor(slug, true);
    private async Task<IActionResult> Editor(string slug, bool detail)
    {
        var page = await db.Pages.AsNoTracking().SingleOrDefaultAsync(p => p.Slug == slug && p.IsDetail == detail);
        return page == null ? NotFound() : View("Edit", page);
    }
    [HttpGet("posts/new")]
    public async Task<IActionResult> New()
    {
        var template = await db.Pages.AsNoTracking().FirstOrDefaultAsync(p => p.IsDetail);
        return View("Edit", new ContentPage { IsDetail=true, Published=false, BodyHtml=template?.BodyHtml ?? "<main class=\"container\"><h1>Yeni yazı</h1><p>İçerik</p></main>" });
    }
    [HttpPost("pages/{slug}/edit")]
    public Task<IActionResult> SavePage([FromRoute] string slug, ContentPage input) => Save(slug, false, input);
    [HttpPost("posts/{slug}/edit")]
    public Task<IActionResult> SavePost([FromRoute] string slug, ContentPage input) => Save(slug, true, input);
    [HttpPost("posts/new")]
    public Task<IActionResult> Create(ContentPage input) => Save(null, true, input);
    private async Task<IActionResult> Save(string? oldSlug, bool detail, ContentPage input)
    {
        input.IsDetail = detail;
        var page = oldSlug == null ? new ContentPage { IsDetail=true } : await db.Pages.SingleOrDefaultAsync(p => p.Slug == oldSlug && p.IsDetail == detail);
        if (page == null) return NotFound();
        input.Id = page.Id;
        if (!detail && oldSlug != input.Slug) ModelState.AddModelError("Slug", "Sabit sayfaların route'u değiştirilemez.");
        if (await db.Pages.AnyAsync(p => p.IsDetail == detail && p.Slug == input.Slug && p.Id != page.Id)) ModelState.AddModelError("Slug", "Bu slug zaten kullanılıyor.");
        if (!ModelState.IsValid) return View("Edit", input);
        var oldUrl = page.Url;
        page.Title=input.Title; page.Slug=input.Slug; page.Description=input.Description ?? "";
        page.BodyHtml=input.BodyHtml; page.Published=input.Published; page.UpdatedUtc=DateTime.UtcNow;
        if (oldSlug == null) db.Pages.Add(page);
        else if (detail && oldSlug != page.Slug)
        {
            // Existing template links follow the new detail slug.
            foreach (var linked in await db.Pages.Where(p => p.BodyHtml.Contains(oldUrl)).ToListAsync())
                linked.BodyHtml = linked.BodyHtml.Replace("\"" + oldUrl + "\"", "\"" + page.Url + "\"").Replace("'" + oldUrl + "'", "'" + page.Url + "'");
        }
        try { await db.SaveChangesAsync(); }
        catch (DbUpdateException) { ModelState.AddModelError("", "Kayıt tamamlanamadı. Slug başka bir kayıtta kullanılıyor olabilir."); return View("Edit", input); }
        TempData["Success"] = "İçerik kaydedildi.";
        return Redirect(detail ? $"/admin/posts/{page.Slug}/edit" : $"/admin/pages/{page.Slug}/edit");
    }
}

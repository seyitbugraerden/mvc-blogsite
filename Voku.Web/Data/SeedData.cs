using System.Text.RegularExpressions;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Voku.Web.Models;
namespace Voku.Web.Data;
public static class SeedData
{
    public static async Task InitializeAsync(IServiceProvider services, IWebHostEnvironment env, IConfiguration config)
    {
        using var scope = services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<SiteDbContext>();
        await db.Database.MigrateAsync();
        if (!await db.AdminUsers.AnyAsync())
        {
            var password = config["Admin:Password"];
            if (string.IsNullOrWhiteSpace(password) || password.Length < 12)
                throw new InvalidOperationException("İlk çalıştırma için Admin__Password değişkenini en az 12 karakter olarak ayarlayın.");
            var user = new AdminUser { Username = config["Admin:Username"] ?? "admin" };
            user.PasswordHash = new PasswordHasher<AdminUser>().HashPassword(user, password);
            db.AdminUsers.Add(user);
        }
        if (!await db.Pages.AnyAsync())
        {
            var titles = new Dictionary<string, string> { ["index"]="Ana sayfa", ["about"]="Hakkımızda", ["skills"]="Yetenekler", ["blog"]="Blog", ["blog-post"]="Heyecanlı bir yolculuk", ["contact"]="İletişim", ["coming-soon"]="Yakında", ["site-offline"]="Bakım", ["error"]="Sayfa bulunamadı", ["typography"]="Tipografi" };
            foreach (var file in Directory.GetFiles(Path.Combine(env.ContentRootPath, "Content"), "*.html"))
            {
                var name = Path.GetFileNameWithoutExtension(file);
                var html = await File.ReadAllTextAsync(file);
                html = Regex.Match(html, @"<body[^>]*>([\s\S]*?)</body>", RegexOptions.IgnoreCase).Groups[1].Value;
                html = Regex.Replace(html, @"<script\b[^>]*>[\s\S]*?</script>", "", RegexOptions.IgnoreCase);
                html = Regex.Replace(html, @"(?<=[""'(])images/", "/images/");
                foreach (var key in titles.Keys)
                    html = html.Replace(key + ".html", key == "index" ? "/" : key == "blog-post" ? "/blog/heyecanli-bir-yolculuk" : "/" + key);
                html = html.Replace("<div id=\"map\"></div>", "<div id=\"map\" style=\"display:grid;place-items:center;background:#eee\">Konum bilgisi yakında</div>");
                if (name == "contact")
                    html += "<section class=\"container margin-top-50 margin-bottom-50\"><h2>İletişim</h2><p>Form şu an gönderime kapalıdır.</p><form><label>Adınız <input name=\"name\" class=\"form-control\" required></label><label>E-posta <input name=\"email\" type=\"email\" class=\"form-control\" required></label><label>Mesajınız <textarea name=\"message\" class=\"form-control\" required></textarea></label><button type=\"submit\" class=\"btn\">Gönder</button></form></section>";
                db.Pages.Add(new ContentPage { Title=titles[name], Slug=name == "index" ? "home" : name == "blog-post" ? "heyecanli-bir-yolculuk" : name, IsDetail=name == "blog-post", BodyHtml=html });
            }
        }
        await db.SaveChangesAsync();
    }
}

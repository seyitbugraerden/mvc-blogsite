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
        if (config.GetValue("Admin:RequireAuthentication", true) && !await db.AdminUsers.AnyAsync())
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
            var posts = new Dictionary<string, string> {
                ["full review of my house"] = "full-review-of-my-house",
                ["we did it! story of an exciting journey"] = "heyecanli-bir-yolculuk",
                ["true story about Tim Finch"] = "true-story-about-tim-finch",
                ["Paris. the first day — adventure begins"] = "paris-the-first-day"
            };
            foreach (var file in Directory.GetFiles(Path.Combine(env.ContentRootPath, "Content"), "*.html"))
            {
                var name = Path.GetFileNameWithoutExtension(file);
                var html = await File.ReadAllTextAsync(file);
                html = Regex.Match(html, @"<body[^>]*>([\s\S]*?)</body>", RegexOptions.IgnoreCase).Groups[1].Value;
                html = Regex.Replace(html, @"<script\b[^>]*>[\s\S]*?</script>", "", RegexOptions.IgnoreCase);
                html = Regex.Replace(html, @"(?<=[""'(])images/", "/images/");
                foreach (var key in titles.Keys)
                    html = html.Replace(key + ".html", key == "index" ? "/" : key == "blog-post" ? "/blog/heyecanli-bir-yolculuk" : "/" + key);
                foreach (var post in posts)
                    html = html.Replace($"<a href=\"#.\" class=\"tittle-post\">{post.Key}</a>", $"<a href=\"/blog/{post.Value}\" class=\"tittle-post\">{post.Key}</a>");
                foreach (var link in new Dictionary<string, string> { ["about me"]="about", ["skills"]="skills", ["blog"]="blog", ["Contact"]="contact" })
                    html = html.Replace($"<a href=\"#.\">{link.Key}</a>", $"<a href=\"/{link.Value}\">{link.Key}</a>");
                html = html.Replace("<a href=\"#.\" class=\"load-more\">", "<a href=\"/blog\" class=\"load-more\">");
                html = html.Replace("<div id=\"map\"></div>", "<div id=\"map\" style=\"display:grid;place-items:center;background:#eee\">Konum bilgisi yakında</div>");
                if (name == "contact")
                    html = html.Replace("<!-- FOOTER -->", "<section class=\"container margin-top-50 margin-bottom-50\"><h2>İletişim</h2><p>Form şu an gönderime kapalıdır.</p><form><label>Adınız <input name=\"name\" class=\"form-control\" required></label><label>E-posta <input name=\"email\" type=\"email\" class=\"form-control\" required></label><label>Mesajınız <textarea name=\"message\" class=\"form-control\" required></textarea></label><button type=\"submit\" class=\"btn\">Gönder</button></form></section><!-- FOOTER -->");
                db.Pages.Add(new ContentPage { Title=titles[name], Slug=name == "index" ? "home" : name == "blog-post" ? "heyecanli-bir-yolculuk" : name, IsDetail=name == "blog-post", BodyHtml=html });
            }
            var detailTemplate = db.Pages.Local.Single(p => p.IsDetail);
            foreach (var post in posts.Where(p => p.Value != detailTemplate.Slug))
                db.Pages.Add(new ContentPage {
                    Title = post.Key, Slug = post.Value, IsDetail = true,
                    BodyHtml = new Regex(@"<h2>[\s\S]*?</h2>").Replace(detailTemplate.BodyHtml, $"<h2><span>{post.Key}</span></h2>", 1)
                });
        }
        await db.SaveChangesAsync();
    }
}

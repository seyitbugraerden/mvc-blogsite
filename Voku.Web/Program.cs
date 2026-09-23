using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Threading.RateLimiting;
using Voku.Web.Data;
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllersWithViews(o => o.Filters.Add(new AutoValidateAntiforgeryTokenAttribute()));
Directory.CreateDirectory(Path.Combine(builder.Environment.ContentRootPath, "App_Data"));
builder.Services.AddDbContext<SiteDbContext>(o => o.UseSqlite(builder.Configuration.GetConnectionString("Default") ?? $"Data Source={Path.Combine(builder.Environment.ContentRootPath, "App_Data", "voku.db")}"));
builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme).AddCookie(o => {
    o.LoginPath = "/admin/login"; o.AccessDeniedPath = "/admin/login";
    o.Cookie.Name = "Voku.Admin"; o.Cookie.HttpOnly = true;
    o.ExpireTimeSpan = TimeSpan.FromHours(4);
});
builder.Services.AddAuthorization(options =>
    options.AddPolicy("AdminAccess", policy => policy.RequireAssertion(context =>
        !builder.Configuration.GetValue("Admin:RequireAuthentication", true)
        || context.User.Identity?.IsAuthenticated == true)));
builder.Services.AddRateLimiter(o => {
    o.RejectionStatusCode = 429;
    o.AddPolicy("login", context => RateLimitPartition.GetFixedWindowLimiter(context.Connection.RemoteIpAddress?.ToString() ?? "unknown", _ => new FixedWindowRateLimiterOptions { PermitLimit=10, Window=TimeSpan.FromMinutes(1), QueueLimit=0 }));
});
var app = builder.Build();
if (!app.Environment.IsDevelopment()) { app.UseExceptionHandler("/server-error"); app.UseHsts(); app.UseHttpsRedirection(); }
app.Use(async (context, next) => {
    context.Response.Headers["X-Content-Type-Options"] = "nosniff";
    context.Response.Headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' https: data:; connect-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'";
    await next();
});
app.UseStaticFiles();
app.UseRouting();
app.UseRateLimiter();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
await SeedData.InitializeAsync(app.Services, app.Environment, app.Configuration);
app.Run();

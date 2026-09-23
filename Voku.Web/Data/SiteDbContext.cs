using Microsoft.EntityFrameworkCore;
using Voku.Web.Models;
namespace Voku.Web.Data;
public class SiteDbContext(DbContextOptions<SiteDbContext> options) : DbContext(options)
{
    public DbSet<ContentPage> Pages => Set<ContentPage>();
    public DbSet<AdminUser> AdminUsers => Set<AdminUser>();
    protected override void OnModelCreating(ModelBuilder model)
    {
        model.Entity<ContentPage>().HasIndex(p => new { p.IsDetail, p.Slug }).IsUnique();
        model.Entity<ContentPage>().Ignore(p => p.Url);
        model.Entity<AdminUser>().HasIndex(p => p.Username).IsUnique();
    }
}

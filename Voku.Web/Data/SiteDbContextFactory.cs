using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;
namespace Voku.Web.Data;
// Migration tooling does not start the web host or require an admin password.
public class SiteDbContextFactory : IDesignTimeDbContextFactory<SiteDbContext>
{
    public SiteDbContext CreateDbContext(string[] args)
    {
        Directory.CreateDirectory("App_Data");
        var options = new DbContextOptionsBuilder<SiteDbContext>()
            .UseSqlite(Environment.GetEnvironmentVariable("ConnectionStrings__Default") ?? "Data Source=App_Data/voku.db").Options;
        return new SiteDbContext(options);
    }
}

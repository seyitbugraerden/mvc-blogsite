using System.ComponentModel.DataAnnotations;
namespace Voku.Web.Models;
public class ContentPage
{
    public int Id { get; set; }
    [Required, StringLength(160)] public string Title { get; set; } = "";
    [Required, StringLength(120), RegularExpression(@"^[a-z0-9]+(?:-[a-z0-9]+)*$", ErrorMessage = "Slug küçük harf, rakam ve tire içerebilir.")]
    public string Slug { get; set; } = "";
    public bool IsDetail { get; set; }
    [Required] public string BodyHtml { get; set; } = "";
    [StringLength(300)] public string? Description { get; set; } = "";
    [StringLength(500), RegularExpression(@"^(?:/(?!/)|https://)[^\s""'<>\\]+$", ErrorMessage = "Görsel yolu /images/... veya https://... biçiminde olmalı.")]
    public string? CoverImageUrl { get; set; }
    [StringLength(80)] public string? Category { get; set; }
    [StringLength(100)] public string? Author { get; set; }
    public DateTime PublishedAtUtc { get; set; } = DateTime.UtcNow;
    public bool Published { get; set; } = true;
    public DateTime UpdatedUtc { get; set; } = DateTime.UtcNow;
    public string Url => IsDetail ? $"/blog/{Slug}" : Slug == "home" ? "/" : $"/{Slug}";
}
public class AdminUser
{
    public int Id { get; set; }
    public string Username { get; set; } = "admin";
    public string PasswordHash { get; set; } = "";
}
public class LoginModel
{
    [Required] public string Username { get; set; } = "";
    [Required, DataType(DataType.Password)] public string Password { get; set; } = "";
}

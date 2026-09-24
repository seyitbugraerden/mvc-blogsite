namespace Voku.Web.Models;

public class SitePageViewModel
{
    public required ContentPage Page { get; init; }
    public IReadOnlyList<ContentPage> Posts { get; init; } = [];
    public IReadOnlyList<string> Categories { get; init; } = [];
    public string? Category { get; init; }
    public int PageNumber { get; init; } = 1;
    public int TotalPages { get; init; }
    public int TotalPosts { get; init; }
    public string HeaderHtml { get; init; } = "";
    public string FooterHtml { get; init; } = "";
    public string ListingUrl(int number, string? category) =>
        $"/blog?page={number}" + (string.IsNullOrEmpty(category) ? "" : $"&category={Uri.EscapeDataString(category)}");
}

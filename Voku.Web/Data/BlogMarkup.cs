using System.Text.RegularExpressions;

namespace Voku.Web.Data;

// Adapt only the known Voku container elements; never rewrite stored article text on startup.
public static class BlogMarkup
{
    public static string PublicHtml(string html) => Regex.Replace(html,
        @"<li>\s*<a\s+href=[""']/blog/[^""']+[""']>\s*Blog Post\s*</a>\s*</li>", "", RegexOptions.IgnoreCase);

    public const string ListMarker = "<!-- BLOG_LIST -->";

    private static (int Start, int Length, int InnerStart, int InnerLength)? Element(string html, string tag, string attribute, string value)
    {
        foreach (Match start in Regex.Matches(html, $@"<{tag}\b[^>]*>", RegexOptions.IgnoreCase))
        {
            var attr = Regex.Match(start.Value, $@"\b{attribute}\s*=\s*([""'])(.*?)\1", RegexOptions.IgnoreCase);
            if (!attr.Success || !attr.Groups[2].Value.Split(' ', StringSplitOptions.RemoveEmptyEntries).Contains(value)) continue;
            return Bounds(html, tag, start);
        }
        return null;
    }

    private static (int Start, int Length, int InnerStart, int InnerLength)? Bounds(string html, string tag, Match start)
    {
        var depth = 1;
        var innerStart = start.Index + start.Length;
        foreach (Match token in Regex.Matches(html[innerStart..], $@"</?{tag}\b[^>]*>", RegexOptions.IgnoreCase))
        {
            depth += token.Value.StartsWith("</") ? -1 : 1;
            if (depth == 0) return (start.Index, innerStart + token.Index + token.Length - start.Index, innerStart, token.Index);
        }
        return null;
    }

    private static string Remove(string html, string tag, string attribute, string value)
    {
        var bounds = Element(html, tag, attribute, value);
        return bounds is { } b ? html.Remove(b.Start, b.Length) : html;
    }

    public static string ListingTemplate(string html)
    {
        html = PublicHtml(html);
        if (html.Contains(ListMarker)) return html;
        var section = Element(html, "section", "class", "post-content");
        if (section is { } b) return html.Remove(b.Start, b.Length).Insert(b.Start, ListMarker);
        var footer = html.IndexOf("<!-- FOOTER -->", StringComparison.Ordinal);
        return footer >= 0 ? html.Insert(footer, ListMarker) : html + ListMarker;
    }

    public static string ArticleBody(string html)
    {
        var content = Element(html, "div", "id", "content");
        if (content is not { } b) return html; // An authored article fragment is already the body.
        var body = html.Substring(b.InnerStart, b.InnerLength);
        body = Remove(body, "div", "class", "tabs-link");
        body = Remove(body, "div", "class", "comments");
        return body;
    }

    public static string Chrome(string html, string tag)
    {
        var start = Regex.Match(html, $@"<{tag}\b[^>]*>", RegexOptions.IgnoreCase);
        if (!start.Success) return "";
        var bounds = Bounds(html, tag, start);
        return bounds is { } b ? PublicHtml(html.Substring(b.Start, b.Length)) : "";
    }
}

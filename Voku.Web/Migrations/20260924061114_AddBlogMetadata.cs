using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Voku.Web.Migrations
{
    /// <inheritdoc />
    public partial class AddBlogMetadata : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "Author",
                table: "Pages",
                type: "TEXT",
                maxLength: 100,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Category",
                table: "Pages",
                type: "TEXT",
                maxLength: 80,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "CoverImageUrl",
                table: "Pages",
                type: "TEXT",
                maxLength: 500,
                nullable: true);

            migrationBuilder.AddColumn<DateTime>(
                name: "PublishedAtUtc",
                table: "Pages",
                type: "TEXT",
                nullable: false,
                defaultValue: new DateTime(1, 1, 1, 0, 0, 0, 0, DateTimeKind.Unspecified));
            // Backfill metadata without modifying existing titles or article HTML.
            migrationBuilder.Sql("UPDATE Pages SET PublishedAtUtc = UpdatedUtc;");
            migrationBuilder.Sql("""
                UPDATE Pages SET Category = 'Genel', CoverImageUrl = CASE Slug
                    WHEN 'full-review-of-my-house' THEN '/images/img-1.jpg'
                    WHEN 'true-story-about-tim-finch' THEN '/images/img-4.jpg'
                    WHEN 'paris-the-first-day' THEN '/images/img-7.jpg'
                    WHEN 'heyecanli-bir-yolculuk' THEN '/images/img-2.jpg'
                    ELSE '/images/blog-post-bg.jpg' END
                WHERE IsDetail = 1;
                """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "Author",
                table: "Pages");

            migrationBuilder.DropColumn(
                name: "Category",
                table: "Pages");

            migrationBuilder.DropColumn(
                name: "CoverImageUrl",
                table: "Pages");

            migrationBuilder.DropColumn(
                name: "PublishedAtUtc",
                table: "Pages");
        }
    }
}

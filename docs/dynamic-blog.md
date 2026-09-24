# Tamamen dinamik blog alanları

Önceki eğitim PDF'i `2688cd4` sürümünü anlatır. Bu değişiklikten sonra ana sayfa ve blog kartları HTML'deki örnek yazılardan değil, yayınlanmış `ContentPage` kayıtlarından üretilir.

## Tek yazı kaydı, üç görünüm

`/admin/posts/new` → `AdminController.Create` → `Save` → `Pages` tablosu.

- `Title`: kart başlığı, detay ana başlığı ve tarayıcı başlığı.
- `Description`: kart özeti, detay giriş açıklaması ve SEO açıklaması.
- `CoverImageUrl`: kart görseli ve detay kapak görseli. Boşsa ortak Voku görseli kullanılır; yerel `/...` veya HTTPS adresi kabul edilir.
- `Category`: kart/detay kategori bağlantısı ve blog filtresi.
- `Author`: kart ve detay yazar metni.
- `PublishedAtUtc`: gösterim ve sıralama tarihi; otomatik zamanlanmış yayın yapmaz.
- `BodyHtml`: yazının asıl gövdesi.
- `Published`: tüm ziyaretçi listeleri ve detay erişimi için aynı yayın koşulu.
- `Slug`: kart bağlantısı ve detay route'u.

Başlığı veya slug'ı değiştirmek için ana sayfayı ayrıca düzenlemek gerekmez. Yayından kaldırmak yazıyı kartlardan çıkarır ve detay adresini 404 yapar.

## Controller → view akışı

`SiteController.Home` veya `Page` → yayınlanmış detay sorgusu → kategori filtresi → kayıt sayısı → sıralama → Skip/Take → `SitePageViewModel` → `Views/Site/Page.cshtml` → `_BlogListing.cshtml`.

Ana sayfada son 6 yazı ve tüm yazılara bağlantı vardır. Blogda her sayfa 6 yazıdır; kategori değişince ilk sayfaya dönülür. Aynı yayın tarihinde Id azalan sıralaması kararlı sonuç sağlar. Kategori, URL oluşturulurken encode edilir. Boş sonuçlarda bilgi mesajı gösterilir. Sınır dışı sayfa numarası geçerli aralığa alınır.

Detayda aynı entity ile başlık/kapak/meta alanları çizilir. `BlogMarkup.ArticleBody` eski Voku gövdesinden içerik bölümünü alır; örnek kategori şeridi ve örnek yorumları çıkarır. Yeni yazılarda zaten yalnızca makale gövdesi vardır. Dinamik üst bilgi ile gövde başlığını tekrar tekrar düzenlemek gerekmez.

## Eski veriler nasıl korunuyor?

`AddBlogMetadata` alan ekleyen bir EF migrationıdır. Mevcut `BodyHtml`, `Title`, `Slug` ve yayın durumu değiştirilmez. Tarih `UpdatedUtc` ile doldurulur. Örnek yazılara ilgili Voku kapak yolları, diğer yazılara ortak kapak atanır; kategori başlangıçta Genel olur.

Ana sayfa ve blogda bilinen Voku `section.post-content` alanı görüntüleme sırasında dinamik liste konumuna dönüştürülür. Yönetici bu sayfayı açıp kaydettiğinde HTML'de `<!-- BLOG_LIST -->` işareti tutulur. Üst/alt alanlar ve bölüm dışındaki içerikler korunur. İşaret ve eski Voku bölümü yoksa liste footer işaretinden önce, o da yoksa gövde sonunda gösterilir.

Bu yardımcı, bilinen Voku HTML yapısına uyarlama yapar; genel amaçlı bir HTML sanitizer değildir. Eski alanların içindeki sosyal bloklar, sabit alıntılar ve sahte sayaçlar yerine veriye bağlı yazı kartları çizilir. Yönetici makale gövdesine elle sabit bir bağlantı yazarsa bu hâlâ editoryal içeriktir; otomatik liste değildir.

## Testler

`tests/smoke.py`: ana sayfa/blog kartlarının kayıtlardan oluşması, metadata, geçersiz görsel URL, taslak görünürlüğü, slug değişimi, kategori, çok sayfalı sonuçlar, boş durum, eski şemadan migration ve orijinal HTML'nin veritabanında korunması.

`tests/blog-browser.cjs`: gerçek tarayıcıda yazı oluşturma, görsel editör, kategoriye tıklama, başlık/slug güncelleme ve masaüstü/mobil görünüm. Her iki test gerçek kullanıcı veritabanından ayrı geçici SQLite dosyaları kullanır.

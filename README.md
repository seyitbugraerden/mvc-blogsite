# Voku CMS

.NET 10 MVC, Entity Framework Core 10 ve SQLite ile Voku tasarımını kullanan içerik yönetim uygulaması.

## Çalıştırma

.NET 10 SDK gereklidir. Şimdilik giriş kontrolü kapalıdır; `/admin` doğrudan açılır.

```bash
dotnet run --project /Users/macuser/Desktop/dotnet-blogpage/Voku.Web/Voku.Web.csproj --launch-profile http
```

Site: http://localhost:5080 · Yönetim: http://localhost:5080/admin

`Admin:RequireAuthentication` ayarı `appsettings.json` içinde `false`. Bu ayarda admin işlemleri herkese açıktır ve ilk açılışta şifre istenmez. Tekrar giriş istemek için ayarı `true` yapın veya `Admin__RequireAuthentication=true` tanımlayın. Henüz hesap yoksa `Admin__Password` ile en az 12 karakterlik ilk şifreyi belirtin. Mevcut hesap varsa eski şifresi korunur.

Varsayılan kullanıcı adı `admin`; ilk kurulumda `Admin__Username` ile değiştirilebilir. Şifre PBKDF2 tabanlı ASP.NET Core PasswordHasher ile hashlenir. İlk kurulumdan sonra bu değişkenler mevcut kullanıcıyı değiştirmez. Şifre kaynak koduna veya Git'e eklenmez.

SQLite dosyası `Voku.Web/App_Data/voku.db` altında oluşturulur. Migration ve başlangıç içerikleri ilk açılışta uygulanır; yeniden başlatmak düzenlenen içerikleri sıfırlamaz. Veritabanı Git'e dahil edilmez. `ConnectionStrings__Default` ile bağlantı adresi değiştirilebilir.

## Sayfalar ve yönetim

| Ziyaretçi adresi | Düzenleme adresi |
| --- | --- |
| `/` | `/admin/pages/home/edit` |
| `/about` | `/admin/pages/about/edit` |
| `/skills` | `/admin/pages/skills/edit` |
| `/blog` | `/admin/pages/blog/edit` |
| `/contact` | `/admin/pages/contact/edit` |
| `/coming-soon` | `/admin/pages/coming-soon/edit` |
| `/site-offline` | `/admin/pages/site-offline/edit` |
| `/typography` | `/admin/pages/typography/edit` |
| `/error` | `/admin/pages/error/edit` |
| `/blog/{slug}` | `/admin/posts/{slug}/edit` |

`/admin/posts/new` üzerinden boş yazı gövdesiyle yeni blog yazısı oluşturulur. Slug küçük harf, rakam ve tire kullanır; aynı türde benzersizdir. Slug değiştirildiğinde mevcut içeriklerdeki tam eşleşen bağlantılar güncellenir. Eski slug adresi 404 döner. Sabit sayfaların route'ları değiştirilemez. Yayından kaldırılan sayfalar 404 döner. Ana sayfa son 6 yayınlanmış yazıyı gösterir. `/blog` aynı kayıtlardan 6 yazılık sayfalar oluşturur; kategori filtreleri gerçek yayınlanmış yazılardan gelir. Sıralama yazı tarihi, eşit tarihte kayıt kimliği azalan biçimdedir. Tarih gösterim/sıralama içindir; zamanlanmış yayın yoktur.

Editörde metin, bağlantı ve görseller için alanlar bulunur. İç içe HTML içeren metinler, bölüm düzeni, arka plan görselleri ve diğer gelişmiş değişiklikler HTML alanından yapılır. Blog başlığı, özet, kapak görseli, kategori, yazar ve tarih admin formundan yönetilir; hem kartlarda hem detay sayfasında aynı kayıt kullanılır. Yazı gövdesini ayrıca düzenleyin. Sabit sayfaların HTML içindeki başlıkları yine gövdeden düzenlenir. Görsel yolları `/images/...` biçimindedir; bu sürümde dosya yükleme bulunmaz.

Ana sayfa ve blogdaki bütün yazı kartları veritabanından oluşturulur. Yeni yayınlanan yazılar otomatik görünür; taslaklar görünmez. Sahte yorum ve fotoğraf sayaçları gösterilmez. Kategori filtresi: `/blog?category=Gezi`; sayfalama: `/blog?page=2`.

Sayfa gövdeleri veritabanında saklanır. Ana sayfa/blog HTML içindeki `<!-- BLOG_LIST -->` işareti dinamik liste yerini belirler. Eski veritabanlarında Voku `post-content` bölümü görüntüleme sırasında bu işaretle uyarlanır; migration eski HTML içeriklerini silmez. Blog detayları ana sayfanın üst/alt alanlarını paylaşır; ana başlık ve kapak Razor tarafından güncel kayıtla çizilir. Eski detayların örnek kategori ve yorum alanları gösterim sırasında kaldırılır. `Voku-HTML-Package` orijinal referanstır; `Voku.Web/Content` başlangıç içerikleridir. İlk kurulumdan sonra değişiklikleri admin panelinden yapın.

Formlar e-posta göndermez ve veri kaydetmez; gönderim denemesinde kullanıcıya bilgi verilir. PHP ve SMTP entegrasyonu yoktur. Şablondaki Google Maps anahtarı kullanılmaz. Şablonun örnek metinleri ve sosyal bağlantıları yönetim panelinden özelleştirilebilir.

## Migration ve yayınlama

```bash
dotnet tool restore
dotnet ef migrations add MigrationAdi --project Voku.Web
dotnet ef database update --project Voku.Web
dotnet publish Voku.Web -c Release -o ./publish
```

Yayın ortamında HTTPS sağlayın; `App_Data` dizinini kalıcı ve yazılabilir tutun. Birden fazla uygulama örneği kullanmadan önce migration uygulamasını dağıtım adımına taşıyın. Giriş kontrolü etkinleştirildiğinde admin girişine hız sınırı ve cookie kimlik doğrulaması uygulanır. Yazma işlemlerindeki CSRF koruması her iki modda da etkindir. HTML düzenleyicisi güvenilir yöneticiler içindir; inline script çalıştırılmaz.

## Doğrulama ve Git akışı

```bash
dotnet build Voku.slnx
python3 tests/smoke.py
```

Smoke testi ayrı geçici SQLite dosyası ve uygulama süreci kullanır; gerçek içerikleri değiştirmez.

Anlamlı aşamalar Conventional Commits (`feat`, `fix`, `test`, `docs`, `chore`) ile kaydedilir ve `origin/main` dalına gönderilir.

EF Core SQLite/migration referansı: https://learn.microsoft.com/en-us/ef/core/get-started/netcore/new-db-sqlite

## Ayrıntılı eğitim rehberi

[PDF: Voku CMS Eğitim Rehberi](docs/Voku-CMS-Egitim-Rehberi.pdf) — Kuruluş, kullanılan diller, MVC veri akışı, controller/view/model ilişkileri, EF Core, migrations, admin formları, slug yönetimi ve testleri 28 bölümde anlatır.

[Tarayıcıda okunabilir HTML](docs/Voku-CMS-Egitim-Rehberi.html). Kaynak belge `docs/build_guide.py` ile üretilir. Rehber uygulamanın `2688cd4` sürümünü temel alır; örnek geliştirmeler mevcut özelliklerden ayrı belirtilmiştir.

### Dinamik blog geçişi

`AddBlogMetadata` migrationı uygulama yeniden başlatıldığında otomatik uygulanır. Yeni alanlar eklenir, mevcut yazı tarihleri `UpdatedUtc` değerinden alınır; eski başlık ve HTML içerikleri korunur. [Güncel dinamik blog mimarisi](docs/dynamic-blog.md), önceki PDF'in blog listeleme bölümlerinden sonra yapılan değişiklikleri açıklar.

İsteğe bağlı tarayıcı testi: `tests/blog-browser.cjs` (Playwright ve bir Chromium tarayıcısı gerekir). `PLAYWRIGHT_MODULE` ve `BROWSER_EXECUTABLE` ile kurulum yolları, `SCREENSHOT_DIR` ile ekran görüntüsü dizini belirtilebilir. Test geçici veritabanı kullanır.

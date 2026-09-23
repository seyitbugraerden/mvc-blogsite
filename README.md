# Voku CMS

.NET 10 MVC, Entity Framework Core 10 ve SQLite ile Voku tasarımını kullanan içerik yönetim uygulaması.

## Çalıştırma

.NET 10 SDK gereklidir. İlk çalıştırmadan önce yönetici şifresi belirleyin:

```bash
# zsh: şifreyi terminal geçmişine yazmadan alır
read -s 'Admin__Password?Yönetici şifresi (en az 12 karakter): '
export Admin__Password
dotnet restore
dotnet run --project Voku.Web --launch-profile http
```

Site: http://localhost:5080 · Yönetim: http://localhost:5080/admin

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

`/admin/posts/new` üzerinden Voku detay şablonuyla yeni yazı oluşturulur. Slug küçük harf, rakam ve tire kullanır; aynı türde benzersizdir. Slug değiştirildiğinde mevcut içeriklerdeki tam eşleşen bağlantılar güncellenir. Eski slug adresi 404 döner. Sabit sayfaların route'ları değiştirilemez. Yayından kaldırılan sayfalar 404 döner. `/blog` sayfasının altındaki dinamik liste yayınlanmış tüm detayları gösterir.

Editörde metin, bağlantı ve görseller için alanlar bulunur. İç içe HTML içeren metinler, bölüm düzeni, arka plan görselleri ve diğer gelişmiş değişiklikler HTML alanından yapılır. Sayfa başlığı tarayıcı/liste başlığıdır; içerikteki görünür başlık ayrıca düzenlenir. Yeni detaylar mevcut detayın tasarımını kopyalar; içeriğini düzenleyip yayınlayın. Görsel yolları `/images/...` biçimindedir; bu sürümde dosya yükleme bulunmaz.

Ana sayfa ve blogdaki dört örnek yazı kartı ayrı slug adreslerine bağlanır.

Şablonun tüm sayfa gövdeleri veritabanında saklanır; üst/alt alanlar her sayfa için ayrı düzenlenir. `Voku-HTML-Package` orijinal referanstır; `Voku.Web/Content` başlangıç içerikleridir. İlk kurulumdan sonra değişiklikleri admin panelinden yapın.

Formlar e-posta göndermez ve veri kaydetmez; gönderim denemesinde kullanıcıya bilgi verilir. PHP ve SMTP entegrasyonu yoktur. Şablondaki Google Maps anahtarı kullanılmaz. Şablonun örnek metinleri ve sosyal bağlantıları yönetim panelinden özelleştirilebilir.

## Migration ve yayınlama

```bash
dotnet tool restore
dotnet ef migrations add MigrationAdi --project Voku.Web
dotnet ef database update --project Voku.Web
dotnet publish Voku.Web -c Release -o ./publish
```

Yayın ortamında HTTPS sağlayın; `App_Data` dizinini kalıcı ve yazılabilir tutun. Birden fazla uygulama örneği kullanmadan önce migration uygulamasını dağıtım adımına taşıyın. Admin girişine hız sınırı, cookie kimlik doğrulaması ve yazma işlemlerine CSRF koruması uygulanır. HTML düzenleyicisi güvenilir yöneticiler içindir; inline script çalıştırılmaz.

## Doğrulama ve Git akışı

```bash
dotnet build Voku.slnx
python3 tests/smoke.py
```

Smoke testi ayrı geçici SQLite dosyası ve uygulama süreci kullanır; gerçek içerikleri değiştirmez.

Anlamlı aşamalar Conventional Commits (`feat`, `fix`, `test`, `docs`, `chore`) ile kaydedilir ve `origin/main` dalına gönderilir.

EF Core SQLite/migration referansı: https://learn.microsoft.com/en-us/ef/core/get-started/netcore/new-db-sqlite

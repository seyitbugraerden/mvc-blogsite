"""Build a beginner's lesson focused on the current SiteController source."""
from pathlib import Path
from html import escape, unescape
import re

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'Voku.Web/Controllers/SiteController.cs').read_text()
lines = source.splitlines()
parts = []
def p(s): return '<p>'+s+'</p>'
def code(s): return '<pre><code>'+escape(s.strip())+'</code></pre>'
def note(s): return '<aside>'+s+'</aside>'
def table(head, rows):
 return '<table><thead><tr>'+''.join('<th>'+x+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(unescape(x))+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table>'
def steps(items): return '<ol>'+''.join('<li>'+x+'</li>' for x in items)+'</ol>'
def excerpt(start,end): return code('\n'.join(f'{i:02}  {lines[i-1]}' for i in range(start,end+1)))
def section(title,goal,body):
 n=len(parts)+1
 parts.append((title,f'<section class="chapter" id="lesson-{n}"><div class="eyebrow">DERS 01 · BÖLÜM {n:02}</div><h1>{title}</h1><p class="goal">{goal}</p>{body}</section>'))

section('Önce büyük resmi görelim','Bu dosyanın görevi ne, neyi yapmıyor?',
p('Bir ziyaretçi /about, /blog veya /blog/ilk-yazim adresini açtığında, hangi içeriğin bulunacağını ve ekrana hangi verilerin gönderileceğini <b>SiteController</b> belirler. Bu dosya ziyaretçinin okuma tarafıdır; güncellenen ders view ve model bağlantılarını da izler. Admin formundan kaydetme işlemi burada yapılmaz.')+
code('Tarayıcı URL ister\n    ↓\nRoute uygun action’ı seçer\n    ↓\nSiteController veritabanından gerekli kayıtları ister\n    ↓\nSitePageViewModel ekran verilerini bir araya getirir\n    ↓\nViews/Site/Page.cshtml HTML üretir\n    ↓\nTarayıcı bu HTML’yi gösterir')+
p('Bu PDF yalnızca <code>Voku.Web/Controllers/SiteController.cs</code> dosyasını öğretir. Başka dosyalara, bu dosyanın bir satırını anlayabilmek için gerektiği kadar bakacağız. Sonraki dersin konusunu siz belirleyebilirsiniz. Anlatım <b>4c8cf8c</b> sürümündeki mevcut koda dayanır.')+
table(['İsim','Aklınızda nasıl tutabilirsiniz?'],[
['Controller','İsteği karşılayan ve yapılacak işi seçen sınıf.'],
['Action','Bir URL/HTTP yöntemiyle dışarıdan çağrılan controller metodu.'],
['Entity','Veritabanındaki kaydın C# nesnesi; burada ContentPage.'],
['View model','Ekrana birlikte gönderilecek verilerin paketi; SitePageViewModel.'],
['View','Bu paketi kullanıp HTML oluşturan Razor dosyası.']])+
note('Controller HTML sayfasının kendisi değildir. “Şu view’ı, şu verilerle oluştur” kararını verir. Veritabanına erişebilmesi de bütün kayıtları her seferinde getirdiği anlamına gelmez.')+
p('<b>Nasıl çalışın?</b> PDF ile SiteController.cs dosyasını yan yana açın. Her bölümde örnek URL’yi takip edin. Önce satırın sonucunu kendi cümlenizle söyleyin, sonra açıklamayla karşılaştırın. Kod kutularındaki satır numaraları öğretim içindir; kopyalarken numaraları dahil etmeyin.'))

section('using, namespace ve sınıf','Dosyanın ilk sekiz satırını okuyalım.',excerpt(1,8)+
table(['Kod','Anlamı / neden var?'],[
['using Microsoft.AspNetCore.Mvc','Controller, IActionResult ve HttpGet gibi MVC adlarını kısa yazabilmek için.'],
['using Microsoft.EntityFrameworkCore','AsNoTracking, ToListAsync gibi EF uzantı metotlarına erişmek için.'],
['using Voku.Web.Data','SiteDbContext ve BlogMarkup bu namespace altında.'],
['using Voku.Web.Models','SitePageViewModel gibi modelleri kullanmak için.'],
['namespace Voku.Web.Controllers;','Sınıfın kod içindeki ad alanı. Tek başına URL tanımlamaz.'],
['public class SiteController','Dışarıdan erişilebilen SiteController adlı sınıfın tanımı.'],
[': Controller','MVC Controller sınıfından miras alır; View, NotFound, Problem gibi metotları kullanır.'],
['private const int PageSize = 6','Bu sınıfa özel, değişmeyen tam sayı: bir listede en fazla 6 yazı.']])+
p('<code>using</code> burada kod adlarını erişilebilir hale getirir; veritabanı sorgusu başlatmaz. Paket yüklemekle aynı işlem değildir. Paket bağımlılıkları csproj içinde tanımlanır.')+
p('<code>class</code> bir sınıf tanımlar. Süslü parantezler sınıfın veya metodun sınırını gösterir. Noktalı virgül bir ifadenin sonunu belirtir. <code>const</code> değerinin uygulama çalışırken değişmesini önler. PageSize’ı 9 yapıp yeniden derlerseniz hem ana sayfa limiti hem blog sayfa büyüklüğü değişir.')+
note('Bu bölümün sorusu: Controller dosyasına using ekledim; veritabanı okunmuş olur mu? Hayır. Sadece ilgili tür/metot isimlerini kullanabilirim.'))

section('SiteDbContext db nasıl geliyor?','db veritabanının kendisi değil, erişim nesnesidir.',code('public class SiteController(SiteDbContext db) : Controller')+
p('Parantez içi bu sınıfın <b>primary constructor</b> tanımıdır. “SiteController oluşturulurken bana SiteDbContext türünde bir nesne ver” der. Nesneye sınıf içinde <code>db</code> adıyla erişiriz. db özel bir C# kelimesi değildir; context adını da verebilirdik.')+
p('Bu nesneyi ASP.NET Core’un dependency injection sistemi sağlar. Program.cs’de <code>AddDbContext&lt;SiteDbContext&gt;(...UseSqlite...)</code> kaydı, context’in nasıl oluşturulacağını tarif eder. Controller içinde bağlantı yolunu tekrar yazmamız gerekmez.')+
code('''// Aynı fikrin klasik constructor ile gösterimi:
public class SiteController : Controller
{
    private readonly SiteDbContext db;

    public SiteController(SiteDbContext db)
    {
        this.db = db;
    }
}''')+
p('Bu örnekte <code>this.db</code> sınıf alanıdır; sağdaki db constructor parametresidir. Mevcut dosya daha kısa primary constructor yazımını kullanıyor. İki örneği aynı dosyaya birlikte eklemeyin; bu yalnızca anlamı göstermek için alternatif bir yazımdır.')+
table(['İfade','Ne anlatır?'],[
['db','İstek sırasında kullanılan SiteDbContext nesnesi.'],
['db.Pages','ContentPage kayıtları için EF sorgu/işlem giriş noktası.'],
['SQLite dosyası','Gerçek kalıcı veri; varsayılan olarak App_Data/voku.db.'],
['db.Pages.Where(...)','Hangi kayıtların isteneceğini tarif eden sorgu.']])+
note('Bu satır veritabanına erişimi mümkün kılar; kendi başına SQL çalıştırmaz. Gerçek veri okuma SingleOrDefaultAsync, CountAsync ve ToListAsync gibi sorguyu yürüten işlemlerde olur.'))

section('URL hangi metoda gidiyor?','Action, route ve parametre kavramlarını üç URL ile öğrenelim.',excerpt(9,17)+
table(['İstek','Çalışan action','Render’a gönderilen değerler'],[
['GET /','Home()','"home", false, null, 1'],
['GET /about','Page(...)','"about", false, null, 1'],
['GET /blog?category=Gezi&amp;page=2','Page(...)','"blog", false, "Gezi", 2'],
['GET /blog/ilk-yazim','Detail(...)','"ilk-yazim", true, null, 1']])+
p('<code>[HttpGet("/{slug}")]</code> içindeki süslü parantez URL’den alınacak değişkeni belirtir. /about için slug=about, /blog için slug=blog olur. /blog/ilk-yazim iki parçalı olduğundan /blog/{slug} route’u ile Detail action’ına gider.')+
p('<code>[FromQuery]</code>, değerin URL’de ? işaretinden sonraki sorgu parametrelerinden alınacağını belirtir. category=Gezi → category değişkeni. <code>[FromQuery(Name="page")] int number=1</code> ise URL’de adı page olan değeri C# tarafında number değişkenine bağlar. Parametre verilmezse başlangıç değeri 1 olur.')+
p('<code>string?</code> ifadesi null olabilen string demektir; ziyaretçi kategori seçmemiş olabilir. <code>=&gt;</code> burada kısa metot gövdesidir: metot sağdaki ifadenin sonucunu döndürür. “Parametreleri hazırla ve Render’a aktar” işini kısa yazar.')+
p('ServerError, Problem(...) ile hata yanıtı üretir; Page.cshtml’i açmaz. Program.cs’de Development dışındaki exception handler bu adrese yönlendirilmiştir. Normal içerik route’larından farklı bir hata işleme yoludur.')+
note('Buradaki public action’lar giriş kapılarıdır. Render private bir yardımcı metottur; /Render diye bir endpoint oluşturulmaz.'))

section('Render neden ortak bir metot?','Aynı işlemleri üç farklı action’da tekrar yazmamak için.',code('private async Task<IActionResult> Render(\n    string slug, bool detail, string? category, int number)')+
table(['Parça','Bu metottaki anlamı'],[
['private','Yalnızca bu sınıf içinden çağrılan yardımcı metot.'],
['async','Metot içinde await kullanılabilmesini sağlar.'],
['Task&lt;IActionResult&gt;','Tamamlandığında bir MVC sonucu üreten asenkron işlem.'],
['IActionResult','View, NotFound veya benzeri HTTP yanıtı sonucunun ortak türü.'],
['slug','Bulunacak içeriğin adres parçası.'],
['detail','false: sabit sayfa; true: blog detayı.'],
['category','Blog listesine uygulanabilecek kategori filtresi.'],
['number','İstenen liste sayfasının numarası.']])+
p('Home, Page ve Detail farklı adreslerden aynı işe başlar: içeriği bul, yayın durumunu kontrol et, ekrana uygun verileri hazırla. Ortak kısmın Render içinde olması aynı sorgu/hata kodunun üç kez yazılmasını önler.')+
code('''// Action işi doğrudan döndürüyor:
public Task<IActionResult> Home()
    => Render("home", false, null, 1);

// Render içinde sorgunun sonucu kullanılacağı için await var:
var count = await query.CountAsync();''')+
p('Home, Task’ı doğrudan döndürdüğü için kendi içinde await kullanmıyor. Bu, işin unutulup arka planda bırakıldığı anlamına gelmez; ASP.NET Core dönen işlemin tamamlanmasını bekler. Render ise count gibi sonuçları sonraki satırlarda kullandığı için await eder.')+
p('await, sonucu hazır olduğunda metodun devam etmesini sağlar. Sorguları otomatik paralelleştirmez ve SQL’in mutlaka daha hızlı çalışmasını sağlamaz. Burada önemli olan, sonuç isteyen satırların doğru sırada tamamlanmasıdır.')+
note('Akılda tutun: Controller’daki Render adı geliştiricinin seçtiği bir isimdir. HTML’yi doğrudan bu metot çizmez; sonunda dönen View sonucu Razor ekranını oluşturur.'))

section('İlk kayıt sorgusunu parçalayalım','Tek sayfa kaydı nasıl seçiliyor?',code('''var page = await db.Pages.AsNoTracking()
    .SingleOrDefaultAsync(p =>
        p.Slug == slug &&
        p.IsDetail == detail &&
        p.Published);''')+
steps(['db.Pages: Pages tablosundaki ContentPage kayıtlarını sorgula.', 'AsNoTracking(): Bu nesneyi EF değişiklik takibine alma. Bu controller yalnızca okuyup gösteriyor.', 'p =&gt; ...: Her kaydın sağlaması gereken koşulu tarif eden lambda. p adı pageRecord da olabilirdi.', 'p.Slug == slug: Kaydın slug alanı, metodun slug parametresine eşit olsun.', 'p.IsDetail == detail: Kayıt türü gelen detail parametresine eşit olsun; her zaman true demiyoruz.', 'p.Published: bool özellik doğrudan koşulda kullanılmış; p.Published == true anlamına gelir.', 'SingleOrDefaultAsync: Tek eşleşme varsa kaydı, yoksa null getir. Birden fazla eşleşme varsa hata ver.', 'await: Sorgu sonucunu alıp page değişkenine ata.'])+
table(['Örnek çağrı','Aranan kayıt'],[
['Render("about", false, null, 1)','Slug=about, IsDetail=false, Published=true'],
['Render("ilk-yazim", true, null, 1)','Slug=ilk-yazim, IsDetail=true, Published=true']])+
p('<code>var</code> “türsüz değişken” demek değildir; C# türü sağdaki ifadeden çıkarır. Buradaki page tek bir ContentPage nesnesi veya null olabilir. List&lt;ContentPage&gt; değildir. <code>&amp;&amp;</code> bütün koşulların birlikte doğru olmasını ister.')+
p('AsNoTracking veritabanını salt okunur yapmaz; context’in bu sorgudan gelen nesneyi takip etmemesini sağlar. Okuma ekranı için uygundur. (IsDetail, Slug) birleşik benzersiz indeksi normal koşullarda aynı türde birden çok slug kaydı oluşmasını önler.')+
note('Kavramsal SQL: SELECT ... FROM Pages WHERE Slug=@slug AND IsDetail=@detail AND Published=1. Bu öğretici bir özet; EF’nin ürettiği SQL’in birebir kopyası değildir.'))

section('Kayıt bulunamazsa ne olur?','null kontrolü, 404 ve erken return.',excerpt(22,27)+
p('Önceki sorguda kayıt yoksa page=null olur. Bu hem gerçekten olmayan bir slug için hem de mevcut ama Published=false olan bir yazı için geçerlidir. Ziyaretçi tarafında taslak yazı da bulunamamış gibi davranır.')+
steps(['Response.StatusCode=404: HTTP yanıtının bulunamadı durumunu ayarla.', 'İkinci sorguda Slug=error, IsDetail=false, Published=true kaydını ara.', 'Varsa page değişkenine bu hata sayfasını koy ve aşağıdaki normal view akışına devam et.', 'Bu kayıt da yoksa return NotFound(): metottan hemen çık ve 404 sonucu ver.'])+
p('<code>page</code> değişkeninin değeri değişebilir: önce aranan sayfa null’dı; sonra hata sayfası kaydı atanabilir. Ama Response.StatusCode 404 kalır. Böylece kullanıcı tasarlanmış hata ekranını görürken istemciye doğru HTTP durum kodu gider.')+
table(['İstek / durum','Sonuç'],[
['/olmayan-sayfa, error kaydı yayında','Error içeriği + HTTP 404'],
['/olmayan-sayfa, error kaydı da yok','NotFound sonucu + HTTP 404'],
['/blog/taslak-yazi','Ziyaretçi açısından bulunamadı; 404'],
['/error doğrudan açılırsa ve kayıt yayındaysa','Normal sayfa kaydı bulunur; genellikle HTTP 200']])+
note('return, yalnızca bir değer söylemez; o metodun çalışmasını o noktada bitirir. Bu nedenle NotFound döndükten sonra aşağıdaki listeleme kodu çalışmaz.')+
p('<b>Mini kontrol:</b> Kayıt bulunamadığında neden hemen her zaman NotFound dönmüyoruz? Çünkü veritabanından yönetilebilen error sayfasının tasarımını göstermek istiyoruz. Ama hata sayfası bulunmasa bile 404 üretebilen bir yedek yolumuz var.'))

section('Hangi ekran türündeyiz?','Ana sayfa, blog listesi, detay ve diğer sayfalar ayrılıyor.',code('''if (!page.IsDetail && page.Slug is "home" or "blog")
{
    // Listeleme verileri hazırlanır ve view döndürülür.
}
if (page.IsDetail)
{
    // Detay sayfası verileri hazırlanır ve view döndürülür.
}
return View("Page", new SitePageViewModel { Page = page });''')+
p('<code>!page.IsDetail</code> ifadesi IsDetail false olsun demektir. Başındaki ünlem mantıksal “değil” operatörüdür. <code>page.Slug is "home" or "blog"</code> C# örüntü eşleştirmesiyle slug bu iki değerden biri mi diye sorar.')+
code('''// Aynı koşulun daha açık yazımı:
if (!page.IsDetail &&
    (page.Slug == "home" || page.Slug == "blog"))''')+
table(['Kayıt','Seçilen dal'],[
['home + IsDetail=false','Son yazıların listesi'],
['blog + IsDetail=false','Kategori ve sayfalama içeren blog listesi'],
['ilk-yazim + IsDetail=true','Blog detay ekranı'],
['about + IsDetail=false','En alttaki genel sayfa sonucu'],
['error + IsDetail=false','En alttaki genel sayfa sonucu; hata akışındaysa 404 korunur']])+
p('Kod if / else if yerine iki if ve sondaki return ile yazılmış. İlk dalın içinde return olduğu için o dal çalışınca ikinci if’e geçilmez. Detay dalı çalışınca da alttaki genel return’e ulaşılmaz. Bu “erken dönüş” yaklaşımı fazla iç içe kod yazmayı azaltır.')+
p('Üç dal da aynı Page adlı Razor view’ını kullanır; fakat view modelin doldurulan alanları farklıdır. Liste ekranında Posts ve Categories gerekir, detayda HeaderHtml/FooterHtml gerekir, normal sayfada çoğunlukla Page yeterlidir.')+
note('Karıştırmayın: page.Slug == "blog" bir blog yazısı değil, blog yazılarını listeleyen sabit sayfadır. Gerçek blog yazılarının IsDetail değeri true olur.'))

section('query ve kategori listesi','Where, Select, Distinct, OrderBy ve ToListAsync birlikte nasıl çalışıyor?',excerpt(30,32)+
p('İlk satır query adlı temel sorguyu kurar: yalnızca yayınlanmış blog detayları. Bu noktada henüz sonuç listesi alınmaz. Sonraki satırlar bu temel sorgudan kategori isimlerini çıkaran ayrı bir sorgu oluşturur.')+
table(['Yazı başlığı','Category','Published'],[
['İstanbul gezisi','Gezi','true'],['EF Core başlangıcı','Yazılım','true'],['Ankara gezisi','Gezi','true'],['İsimsiz kategori','null','true'],['Taslak haber','Haber','false']])+
code('''query
// Yayınlanmış dört yazıyı hedefler; taslak haber yok.
.Where(p => p.Category != null && p.Category != "")
// Kategorisiz kaydı eler.
.Select(p => p.Category!)
// Artık yazı nesneleri değil: "Gezi", "Yazılım", "Gezi"
.Distinct()
// Tekrarsız: "Gezi", "Yazılım"
.OrderBy(c => c)
// Kategori değerine göre artan sıra.
.ToListAsync()
// Sorguyu çalıştır; await ile List<string> al.''')+
p('<code>Select</code> hangi alanı alacağını seçer; kayıt silmez. <code>Distinct</code> sonuçtaki tekrarları kaldırır; veritabanındaki aynı kategorili yazılar aynen kalır. <code>OrderBy(c =&gt; c)</code> içindeki c artık ContentPage değil string kategori adıdır. Sıralamanın ayrıntısı veritabanının metin karşılaştırma kurallarına bağlıdır.')+
p('<code>Category!</code> sonundaki ünlem, derleyiciye “burada null olmadığını kabul et” der; çalışma anında null kontrolü yapmaz. Önceki Where null değerleri elemiştir. Bu ünlem, önceki bölümdeki <code>!page.IsDetail</code> ile aynı görevde değildir.')+
note('Neden kategoriler seçili filtre uygulanmadan önce alınıyor? Gezi seçtiğinizde filtre menüsünde Yazılım da kalabilsin diye. Aksi halde kullanıcı sadece seçili kategoriyi görebilirdi.'))

section('Kategori filtresi nasıl uygulanıyor?','Kategorileri listelemek ile yazıları kategoriye göre filtrelemek farklı işlerdir.',excerpt(33,34)+
p('İlk satır üçlü koşul operatörü kullanır. Yapısı <code>koşul ? doğruysa : yanlışsa</code> biçimindedir. Blog sabit sayfasındaysak gelen kategori değerini temizler; ana sayfadaysak category=null yapar. Böylece ana sayfa her zaman genel son yazıları gösterir.')+
code('''// category = "  Gezi  " ise:
category?.Trim()  // "Gezi"

// category = null ise:
category?.Trim()  // null; Trim çağrılmaz.''')+
p('<code>?.</code> null koşullu erişimdir. Değer varsa metodu çağırır, yoksa null verir. Trim baştaki/sondaki boşlukları kaldırır; kategori adının içindeki boşlukları kaldırmaz. <code>string.IsNullOrEmpty</code>, null veya boş string mi diye kontrol eder. Önündeki ! nedeniyle “boş değilse filtre uygula” diyoruz.')+
p('<code>query = query.Where(...)</code>, temel sorguya ek şart koyar. Böylece hem IsDetail/Published koşulları hem Category koşulu geçerli olur. Bu bir veritabanı UPDATE işlemi değildir; sadece çalıştırılacak SELECT sorgusunun kapsamı daralır.')+
table(['URL','Yazı sorgusunda kategori koşulu'],[
['/blog','Yok; tüm yayınlanmış detaylar'],
['/blog?category=Gezi','Category == "Gezi"'],
['/blog?category=','Yok; temizlenmiş değer boş'],
['/blog?category=Olmayan','Eşleşme yok; boş liste'],
['/?category=Gezi','Home action bu filtreyi kullanmaz']])+
note('categories çoğul: filtre menüsünün seçenekleri. category tekil: kullanıcının seçtiği değer. query: seçime göre yazıları getirecek sorgu. Bu üç değişken aynı şey değildir.')+
p('<b>Düşünme sorusu:</b> Bir yazıyı taslağa çekersek tek başına onun kullandığı kategori menüde kalır mı? Hayır; categories sorgusu da yalnızca Published=true yazılar üzerinden kuruluyor.'))

section('Kaç kayıt, kaç sayfa?', 'CountAsync, Ceiling, Max ve Clamp için sayısal örnekler.',excerpt(35,37)+
p('<code>CountAsync()</code> filtreye uyan toplam yazı sayısını getirir. Altı kayıtlık görünen sayfanın sayısı değildir. Örneğin seçili kategoride 14 yayınlanmış yazı varsa count=14 olur.')+
code('''PageSize = 6
count = 14

14 / (double)6 = 2.333...
Math.Ceiling(2.333...) = 3
(int)3 = 3

totalPages = 3''')+
p('<code>(double)</code>, bölmeyi ondalıklı yapar. İki int doğrudan bölünseydi kesir atılır, 14/6 sonucu 2 olurdu. Ceiling yukarı yuvarlar; son iki yazı için üçüncü sayfanın gerektiğini hesaplar. <code>(int)</code> sonucu tam sayıya çevirir.')+
table(['count','totalPages','Sayfalardaki kayıt sayıları'],[
['0','0','Hiç kayıt yok'],['1','1','1'],['6','1','6'],['7','2','6 + 1'],['14','3','6 + 6 + 2']])+
p('<code>Math.Clamp(number, 1, Math.Max(1, totalPages))</code> istenen sayfayı geçerli aralığa çeker. Clamp, alt sınırın altındaki değeri alt sınıra; üst sınırın üstündekini üst sınıra getirir. Max(1,totalPages), hiç kayıt yokken bile üst sınırın en az 1 olmasını sağlar.')+
table(['İstek','totalPages=3 iken number'],[
['page=2','2'],['page=0 veya page=-8','1'],['page=99','3']])+
note('Hiç yazı yoksa TotalPages=0 ama PageNumber=1 olur. Çelişki değil: veri için sıfır sayfa var; Skip hesabına geçerli bir başlangıç değeri veriyoruz. View bu durumda boş liste mesajı gösterir.'))

section('Sıralama, Skip ve Take','Tüm yazıları belleğe almadan istenen sayfayı getiriyoruz.',excerpt(38,39)+
steps(['OrderByDescending(PublishedAtUtc): Tarihi yeni olan yazı önce gelsin.', 'ThenByDescending(Id): Tarihler aynıysa büyük Id önce gelsin.', 'Skip((number - 1) * PageSize): Önceki sayfalardaki kayıtları atla.', 'Take(PageSize): En fazla 6 kayıt al.', 'ToListAsync + await: Sorguyu çalıştır ve sonuçları posts listesine ata.'])+
table(['number','Skip hesabı','Alınan sıralı kayıtlar'],[
['1','(1−1)×6 = 0','1–6'],['2','(2−1)×6 = 6','7–12'],['3','(3−1)×6 = 12','13–18; yalnızca 14 varsa 13–14']])+
p('ThenByDescending ikinci bir OrderBy yerine kullanılır. Amaç ilk tarih sırasını koruyup eşit tarihler içinde Id ile sıralamaktır. İkinci bir OrderBy yazmak ilk sıralamayı değiştirebilir. Id ile eşitliği çözmek sayfa sınırlarındaki sonucu daha belirli hale getirir.')+
p('Filtreleme, sıralama ve Skip/Take, ToListAsync öncesinde EF sorgusunun parçalarıdır; amaç veritabanından yalnızca gereken alt kümeyi almaktır. Önce ToListAsync yapıp ardından Where/Skip uygulasaydık artık bellekteki listeyi işliyor olurduk ve gereksiz kayıtlar getirebilirdik.')+
p('Sıralama alanı PublishedAtUtc’dir; UpdatedUtc değildir. Yazının gövdesini düzenlemek onu otomatik en üste taşımaz. Yazı tarihini değiştirmek ise sıralamayı etkiler. Gelecekteki tarih için ayrıca bir “tarih geldi mi?” koşulu olmadığı için Published=true olan gelecek tarihli yazı da görünür.')+
note('ToListAsync sonucu List&lt;ContentPage&gt; olur. Ancak kategori sorgusunda Select ile string’e dönüştürdüğümüz için aynı ToListAsync orada List&lt;string&gt; üretmişti. Sonucun türünü sorgunun son eleman türü belirler.'))

section('View’a tam olarak ne gönderiliyor?','View adı ile view modelin alanlarını birbirinden ayıralım.',excerpt(40,41)+
p('<code>View("Page", ...)</code> ifadesindeki "Page" bir view adıdır. SiteController için ilgili dosya <b>Views/Site/Page.cshtml</b> olur. İkinci parametre o view’a gönderilen veri nesnesidir.')+
p('<code>new SitePageViewModel { ... }</code> yeni bir ekran modeli oluşturur. Süslü parantez içindeki atamalar bu nesnenin alanlarını doldurur. <code>Page = page</code> ifadesinde soldaki Page model özelliği, sağdaki page ise veritabanından aldığımız yerel değişkendir.')+
table(['View model alanı','Gönderilen değer','Ekrandaki amacı'],[
['Page','home/blog sabit sayfa kaydı','Başlık, açıklama ve sayfa HTML düzeni'],
['Posts','O sayfaya ait en fazla 6 detay','Yazı kartları'],
['Categories','Tekrarsız kategori isimleri','Kategori filtre bağlantıları'],
['Category','Seçili kategori veya null','Seçili filtre ve sayfalama linkleri'],
['PageNumber','Düzeltilmiş sayfa numarası','“Sayfa 2 / 3” bilgisi'],
['TotalPages','Toplam sayfa sayısı','Önceki/sonraki kontrolleri'],
['TotalPosts','Filtreye uyan toplam kayıt','“14 yazı” bilgisi']])+
code('''// Razor tarafında kavramsal kullanım:
@model SitePageViewModel

@foreach (var post in Model.Posts)
{
    <a href="@post.Url">@post.Title</a>
}''')+
p('Mevcut Page.cshtml, listeleme ekranında bu modeli _BlogListing.cshtml partial view’ına aktarır. Kartların foreach döngüsü oradadır. Controller bu kartların HTML’sini tek tek üretmez; onları oluşturacak veri listesini sağlar.')+
note('Bu üç “page” farklıdır: URL’de page=2 sayfalama parametresidir; C# page değişkeni ContentPage kaydıdır; View("Page") ise Razor dosyasının adıdır. Büyük/küçük harf ve bulunduğu bağlam anlamı değiştirir.'))

section('Blog detayında header nereden geliyor?','About Us örneğini gerçek kodla takip edelim.',excerpt(43,49)+
p('IsDetail=true ise listeleme dalı atlanır ve bu blok çalışır. Detay yazısı ilk sorguda zaten page değişkenine alınmıştır. Burada ikinci kez ana sayfa kaydı bulunur; amaç detayın header ve footer alanlarını ana sayfayla paylaşmaktır.')+
code('home?.BodyHtml ?? page.BodyHtml')+
steps(['home varsa home.BodyHtml değerini al.', 'home null ise ?. nedeniyle sonuç null olur.', '??, sol taraf null ise sağdaki page.BodyHtml değerini kullanır.', 'BlogMarkup.Chrome(..., "header") seçilen HTML içinden header bölümünü çıkarır.', 'Aynı işlem footer için yapılır; iki string view modeline konur.'])+
p('<b>Chrome burada Google Chrome tarayıcısı değildir.</b> Projede yazılmış yardımcı metodun adıdır; sayfanın üst/alt kabuk HTML’sini bulur. Bir web isteği atmaz ve yeni veritabanı sorgusu yapmaz. Kendisine verilen metin üzerinde çalışır.')+
p('Ana sayfanın BodyHtml alanında <code>&lt;a href="/about"&gt;2About Us&lt;/a&gt;</code> varsa detay header’ında da aynı metin görünür. Çünkü veri doğrudan veritabanındaki ana sayfa HTML’sinden gelir. Admin’de ana sayfa menü metnini değiştirmek hem ana sayfaya hem blog detayına yansır.')+
p('Diğer sabit sayfalar bu dala girmediği için kendi BodyHtml içindeki header’ı kullanır. Bu yüzden onlar About Us gösterirken detay 2About Us gösterebilmişti. Bu bir CSS veya tarayıcı cache farkı olmak zorunda değildir; veri kaynağı farkıdır.')+
note('İki ince ayrıntı: Ana sayfa sorgusunda Published filtresi yok; burada ana sayfa chrome kaynağı olarak okunuyor. Ayrıca ?? yalnızca null durumunda fallback yapar. home mevcut ama HTML içinde header yoksa Chrome boş string döndürür; otomatik olarak detayın header’ına ikinci kez dönülmez.'))

section('Diğer sayfalar ve tam istek örnekleri','Aynı controller’ın üç farklı isteğe nasıl yanıt verdiğini tekrar izleyelim.',code('return View("Page", new SitePageViewModel { Page = page });')+
p('En alttaki satır Hakkımızda, Yetenekler, İletişim veya hata sayfası gibi genel içerikler içindir. Page alanı doldurulur. Posts ve Categories gibi alanlar SitePageViewModel’de başlangıçta boş listelerdir; bu sayfalar için blog listesi sorgusu çalıştırılmaz.')+
table(['Adım','/about','/blog?category=Gezi&amp;page=2','/blog/ilk-yazim'],[
['Action','Page','Page','Detail'],
['İlk Render değerleri','about, false, null, 1','blog, false, Gezi, 2','ilk-yazim, true, null, 1'],
['İlk kayıt','about sabit sayfası','blog sabit sayfası','ilk-yazim detayı'],
['Ek sorgular','Yok','Kategoriler + count + posts','Ana sayfa header/footer kaynağı'],
['View modeli','Page','Page + listeler + sayfalama','Page + HeaderHtml + FooterHtml'],
['Görünüm','Genel BodyHtml','Dinamik yazı kartları','Dinamik detay başlığı ve yazı gövdesi']])+
p('Başarılı normal /about isteğinde bir içerik sorgusu vardır. Başarılı listeleme isteğinde ilk sayfa sorgusu, kategori sorgusu, count sorgusu ve posts sorgusu olmak üzere dört içerik sorgusu yürütülür. Başarılı detay isteğinde detay kaydı ve ana sayfa kaydı için iki sorgu vardır. Bunlar bu controller’ın normal yollarıdır; başlangıç migration/seed işlemleri bu sayıya dahil değildir.')+
p('Kod yukarıdan aşağıya okunur ama her istek bütün satırları çalıştırmaz. Koşullar ve return ifadeleri izlenecek yolu belirler. Bu nedenle hata ayıklarken önce hangi URL’nin hangi parametrelerle geldiğini belirlemek, sonra o dalı izlemek önemlidir.')+
note('Controller’ın hiçbir dalında Add, Remove veya SaveChangesAsync yok. Bu dosya veriyi okur ve yanıt hazırlar. Admin’den değişen veriyi bir sonraki ziyaretçi isteğinde yeniden okuduğu için içerik güncel görünür.'))

section('Kendi başınıza deneyin','Küçük alıştırmalar; önce tahmin edin, sonra koddan kontrol edin.',
table(['Soru','Cevap ve gerekçe'],[
['detail=false ise IsDetail=true kayıt gelir mi?','Hayır. p.IsDetail == detail eşitlik koşulu vardır.'],
['Published false kayda doğrudan URL ile gidilir mi?','Bu controller onu ilk sorguda dışlar ve 404 yoluna girer.'],
['Select kaldırılırsa categories ne olur?','String listesi yerine entity sorgusu kalır; devamdaki OrderBy(c =&gt; c) kategori sıralaması olmaktan çıkar.'],
['Distinct kaldırılırsa?','Aynı kategori her yazı için tekrarlanabilir.'],
['13 yazı ve PageSize=6 ise kaç sayfa?','Ceiling(13/6.0)=3; 6+6+1 kayıt.'],
['2. sayfa kaç kayıt atlar?','(2−1)×6=6.'],
['Özet değişince neden kart güncellenir?','Controller güncel entity’yi Posts listesinde view’a yollar.'],
['Başlık değiştiğinde bu dosyada SQL yazmalı mıyız?','Hayır. Okuma sorgusu güncel Title değerini zaten getirir.'],
['Header niçin diğer sayfadan farklı olabilir?','Detay home.BodyHtml kaynağını, diğer sabit sayfa kendi BodyHtml kaynağını kullanır.'],
['Query oluşturmak kayıtları değiştirmek midir?','Hayır. Sorgu tanımıdır; burada veri yazma işlemi yok.']])+
p('<b>Breakpoint alıştırması:</b> İlk kayıt sorgusuna breakpoint koyun. /about açın; slug=about ve detail=false değerlerini görün. Sonra /blog?category=Gezi&amp;page=2 açıp category ve number değerlerini izleyin. Count sonrasında count ve totalPages’i, posts sorgusundan sonra listenin elemanlarını inceleyin.')+
p('<b>Boş kategori alıştırması:</b> /blog?category=OlmayanBirKategori açın. Ana blog sayfası kaydı yine bulunduğu için HTTP 404 beklemeyin. count=0 ve posts boş olur; view boş liste mesajı gösterir. “Sayfanın bulunamaması” ile “listenin boş olması” farklı durumlardır.')+
p('<b>Kendi cümlenizle tamamlayın:</b> “Bu istek ... action’ına gider. İlk sorgu ... kaydını bulur. ... koşulu nedeniyle ... dalı çalışır. ... verileri SitePageViewModel’e konur. ... view’ı bu verileri HTML olarak gösterir.”')+
note('Bir sonraki dosyaya geçmeden önce bu paragrafı /about, /blog ve /blog/ilk-yazim için üç kez doldurabilmeniz yeterlidir.'))

section('SitePageViewModel neden ayrı?', 'Tek entity, ekranın bütün ihtiyaçlarını karşılamıyor.',
code('public required ContentPage Page { get; init; }\npublic IReadOnlyList<ContentPage> Posts { get; init; } = [];\npublic IReadOnlyList<string> Categories { get; init; } = [];\npublic string? Category { get; init; }\npublic int PageNumber { get; init; } = 1;')+
p('ContentPage tek bir kalıcı içerik kaydıdır. Blog ekranında ise hem blog sabit sayfasının düzeni hem yazı listesi hem kategoriler hem de sayfalama bilgisi gerekir. SitePageViewModel, farklı kaynaklardan gelen bu verileri tek türü belli paket içinde taşır. Ayrı bir veritabanı tablosu değildir.')+
table(['Yazım','Amaç / sınır'],[['required Page','Nesne oluşturulurken Page atamasını derleyici düzeyinde ister; SQL NOT NULL veya MVC Required doğrulaması değildir.'],['get; init;','Nesne kurulurken atanır; sonradan normal property atamasını sınırlar. İçindeki entity’yi derinlemesine değişmez yapmaz.'],['IReadOnlyList<ContentPage>','View’a okuma odaklı liste arayüzü sunar. Alttaki tüm nesneleri immutable hale getirmez.'],['= []','Boş liste başlangıcı; view’ın null kontrolü yerine Count/foreach kullanmasını kolaylaştırır.'],['string? Category','Filtre seçilmemişse null geçerli bir durumdur.']])+
p('Posts listesi entity’ler içerir; kartlar Title, Description ve Url gibi mevcut alanları doğrudan okur. Ayrı BlogCardViewModel kullanmak gelecekte kartın ihtiyaç duyduğu alanları sınırlandırabilir; şu an böyle bir sınıf yoktur. Ekran modeli veritabanı modelinden ayrılmış olsa da içindeki her öğenin ayrı ekran modeline dönüştürülmesi zorunlu değildir.')+
note('Neden ViewBag yerine bu sınıf? Alan adlarını ve türlerini derleme sırasında kontrol edebilmek için. Model.Posts yanlış yazılırsa hata daha erken anlaşılır. Mevcut ziyaretçi controller’ı ViewBag.Posts kullanmıyor.'))

section('Page.cshtml: modelden ekran seçmek','Controller’ın gönderdiği paket Razor’da nasıl açılıyor?',
code('@model SitePageViewModel\n@{\n    Layout = null;\n    var entry = Model.Page;\n    var isListing = !entry.IsDetail &&\n        (entry.Slug == "home" || entry.Slug == "blog");\n}')+
p('Model bütün ekran paketidir; entry bu paketin içindeki ContentPage kaydıdır. Model.Title yazmak yanlış olur çünkü Title SitePageViewModel’de değil, Model.Page üzerinde tanımlıdır. entry.Title bu uzun yolu kısaltır. Bu atama yeni veritabanı sorgusu yapmaz.')+
steps(['entry.IsDetail ise dinamik kapak, ana başlık, kategori/yazar/tarih ve makale gövdesi çizilir.', 'Ana sayfa veya blog listesi ise HTML içindeki BLOG_LIST işareti bulunur; öncesi çizilir, _BlogListing partial’ı eklenir, sonrası çizilir.', 'Diğer sabit sayfalarda kayıt gövdesi gösterilir.'])+
code('@Html.Raw(Model.HeaderHtml)\n<h1>@entry.Title</h1>\n@Html.Raw(BlogMarkup.ArticleBody(entry.BodyHtml))\n\n<partial name="_BlogListing" model="Model" />')+
p('Bu satırlar farklı dallardan alınmış örneklerdir. Partial’a model="Model" verilmesi, controller’dan alınmış paketin aynısını alt view’a taşır. Yeni controller isteği veya SQL sorgusu başlatmaz. Partial yalnızca sayfanın tekrar kullanılabilir HTML parçasıdır.')+
p('Layout=null nedeniyle bu view html/head/body kabuğunu kendisi kurar. Admin ekranında ise ortak _AdminLayout vardır. Html.Raw HTML string’ini markup olarak gösterir; @entry.Title normal metin kodlamasıyla gösterilir. Raw bir temizleyici değildir; gövdenin güven modeli ayrı değerlendirilir.')+
note('Sabit sayfanın BodyHtml içindeki h1 metni ile Title metadata’sı ayrı olabilir. Blog detayının ana h1’i ise @entry.Title ile doğrudan modelden gelir. Aynı isimli “başlık” alanları her görünümde aynı yoldan çizilmiyor.'))

section('_BlogListing: kart, filtre ve sayfalama','Hangi görünür öğe modelin hangi alanından geliyor?',
table(['View ifadesi','Veri kaynağı','Ekrandaki karşılığı'],[['Model.Posts','Controller’ın filtrelenmiş, sayfalanmış listesi','foreach ile kartlar'],['post.Title / post.Url','Listedeki ContentPage','Başlık ve detay bağlantısı'],['post.CoverImageUrl ?? varsayılan','Yazı kaydı / null durumunda fallback','Kart görseli'],['Model.Categories','Tüm yayınlanmış yazılardan tekil kategori adları','Filtre bağlantıları'],['Model.Category == category','Seçili filtre','selected CSS sınıfı'],['Model.TotalPosts','Filtreye uyan toplam kayıt','Yazı sayısı'],['PageNumber / TotalPages','Controller hesaplaması','Önceki/sonraki bağlantıları']])+
code('@foreach (var post in Model.Posts)\n{\n    <h3><a href="@post.Url">@post.Title</a></h3>\n    <p>@post.Description</p>\n}\n@if (Model.Posts.Count == 0)\n{\n    <p>Henüz yayınlanmış yazı yok.</p>\n}')+
p('Sadeleştirilmiş örnek: foreach veritabanını tekrar taramaz; hazır listeyi dolaşır. Kart sayısı kadar SQL sorgusu yapılmaz. Model.ListingUrl(number, category), sayfalama URL’sini üretir; kategori değerini Uri.EscapeDataString ile URL’ye uygun kodlar. Bir sonraki sayfaya tıklamak ise yeni HTTP isteği başlatır.')+
p('Ana sayfada “Tüm yazıları gör” linki /blog’a gider. Blog listesinde sayfalama, kategori parametresini korur; kategori seçmek sayfa numarasını 1’e döndürür. Aksi halde önceki kategorideki yüksek sayfa numarası yeni filtre için anlamsız olabilir.')+
note('Başlık linkinin rengi CSS işidir. Hangi başlığın ve URL’nin geldiği model/controller işidir. Renk değiştirmek için migration gerekmez; kartta yeni kalıcı veri göstermek için veri yolunun tamamını düşünmek gerekir.'))

section('Bir alanın admin’den ziyaretçiye yolculuğu','View değişikliğinin sınırlarını somut örnekle görelim.',
steps(['Admin/Edit.cshtml içindeki input asp-for="Author" kullanıcıya yazar adını düzenletir.', 'POST model binding, Author form değerini ContentPage input.Author’a bağlar.', 'AdminController.Save, doğrulamadan sonra input.Author değerini gerçek page.Author’a kopyalar.', 'SaveChangesAsync yeni değeri Pages tablosuna yazar.', 'Ziyaretçi /blog istediğinde SiteController güncel kayıtları Posts listesine alır.', '_BlogListing.cshtml @post.Author ile yeni metni gösterir.'])+
p('Bu akış için SiteController’a yeni sorgu yazmak gerekmez; Author entity üzerinde zaten vardır ve mevcut sorgu entity’yi getirir. Öte yandan alan hiç yoksa yalnızca Razor’a @post.ReadingMinutes yazmak yetmez; model ve kalıcılık tasarımı gerekir.')+
table(['İstenen değişiklik','Gereken çalışma'],[['Label “Yazar” yerine “Yazıyı hazırlayan” olsun','Label metni; asp-for aynı kalır.'],['Yazar adı italik gösterilsin','Ziyaretçi view’ı/CSS.'],['Yeni bir okuma süresi verisi saklansın','Entity alanı, migration, admin input, Save ataması, view gösterimi, test.'],['Bir alan ekranda farklı adla taşınsın','Ayrı view model eşlemesi; DB değişmiyorsa migration yok.']])+
p('Admin controller rehberi bu kayıt zincirini ayrıntılı ele alır. SiteController’ın sorumluluğu kaydetmek değil, verinin sonraki istekte doğru filtre ve ekran modeliyle tekrar okunmasıdır.')+
note('Öğrenme kontrolü: “Formda görünen değer” ile “DB’de kayıtlı değer” her zaman aynı olmayabilir. Hatalı POST, kullanıcının girdilerini view’da koruyabilir ama kaydetmez. Başarılı kayıt sonrası ziyaretçi sorgusu kalıcı değeri getirir.'))

section('Kodun tamamı · ilk bölüm','Açıklamalardan sonra gerçek dosyayı bir bütün olarak okuyun.',excerpt(1,27)+p('İlk bölüm: bağımlılıklar, route’lar, ortak Render metodu, kayıt seçimi ve bulunamama davranışı. Buradaki satır numaraları hazırlama anındaki gerçek dosyayla eşleşir.'))
section('Kodun tamamı · ikinci bölüm','Listeleme, detay ve genel ekran dönüşleri.',excerpt(28,len(lines))+p('Kod referansı: <a href="https://github.com/seyitbugraerden/mvc-blogsite/blob/4c8cf8c/Voku.Web/Controllers/SiteController.cs">SiteController.cs · 4c8cf8c</a>. Yardımcı model: <a href="https://github.com/seyitbugraerden/mvc-blogsite/blob/4c8cf8c/Voku.Web/Models/SitePageViewModel.cs">SitePageViewModel.cs</a>. Bu ders, uygulama kodunda değişiklik yapmaz.'))

base=(ROOT/'docs/Voku-CMS-Egitim-Rehberi.html').read_text()
css=re.search(r'<style>([\s\S]*?)</style>',base).group(1)
css+='\npre{font-size:8.5pt;line-height:1.4} .cover h1{font-size:42pt} .toc a{padding:2mm 0} .chapter:last-child pre{font-size:8pt}\n'
cover='''<div class="cover"><div><div class="tag">C# VE MVC · DOSYA DOSYA EĞİTİM</div><h1>SiteController.cs<br>Adım adım</h1><p>Ne işe yarıyor?<br>Neden böyle yazıldı?<br>Hangi veri, hangi ekrana gidiyor?</p></div><div><p>Ders 01 · Başlangıç seviyesi<br>Gerçek proje kodu, örnek URL’ler ve cevaplı alıştırmalar.</p><div class="meta">Voku CMS · 24 Eylül 2026<br>Kod sürümü: 4c8cf8c<br>Kapsam: Yalnızca SiteController.cs</div></div></div>'''
toc=''
for start in range(0,len(parts),11):
 toc+='<section class="toc"><div class="eyebrow">DERS PLANI</div><h1>İçindekiler'+(' · devam' if start else '')+'</h1>'
 toc+=''.join(f'<a href="#lesson-{i+1}"><b>{i+1:02}</b> &nbsp; {parts[i][0]}</a>' for i in range(start,min(start+11,len(parts))))
 toc+='<small>Başlıklara tıklayarak ilgili bölüme geçebilirsiniz. İlk okumada bölümleri sırayla takip edin; son iki bölüm dosyanın tam kodunu içerir.</small></section>'
html='<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>SiteController.cs — Adım Adım Eğitim</title><style>'+css+'</style></head><body>'+cover+toc+''.join(x[1] for x in parts)+'</body></html>'
(ROOT/'docs/SiteController-Egitimi.html').write_text(html)
print(f'{len(parts)} sections, {len(lines)} source lines.')

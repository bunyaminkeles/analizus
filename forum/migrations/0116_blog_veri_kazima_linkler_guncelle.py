from django.db import migrations

def guncelle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')

    content = """<h2>Literatür Taramasında Veri Kazıma (Scraping) Nedir?</h2>
<p>Tez veya makale yazarken araştırmacıların en çok vaktini ve enerjisini alan aşama şüphesiz literatür taramasıdır. Belirli bir konuda yazılmış yüzlerce makaleyi veya tezi tek tek aramak, başlıklarını kopyalamak, özetlerini okumak ve bu verileri bir Excel dosyasına elle işlemek haftalar hatta aylar sürebilir. <strong>Veri kazıma (web scraping)</strong> teknolojileri sayesinde bu manuel süreci dakikalara indirmek mümkündür. Analizus.com, araştırmacılar için özel olarak geliştirdiği araçlarla Türkiye'nin ve dünyanın en büyük akademik veri tabanlarından otomatik ve sistematik veri çekilmesini sağlar.</p>

<h2><a href="/yoktez/">YÖK Tez Kazıma Aracı →</a></h2>
<p>Türkiye'de yazılmış lisansüstü tezlerin tek resmi kaynağı olan YÖK Ulusal Tez Merkezi, çok zengin bir bilimsel havuzdur. Bibliyometrik analizler yapmak veya spesifik bir alandaki trendleri görmek isteyenler için buradaki veriler çok kıymetlidir. Ancak sistem, toplu veri indirmeye izin vermez. <a href="/yoktez/">Analizus'un YÖK Tez Kazıma aracı</a> ile bu engeli aşabilirsiniz:</p>
<ul>
  <li>Belirlediğiniz anahtar kelimelere göre binlerce tezin künyesini (Yazar, Danışman, Yıl, Üniversite, Enstitü, Konu, Tür vb.) tek bir tıklamayla sistemden çekebilirsiniz.</li>
  <li>Tez özetlerini (Abstract) Türkçe ve İngilizce dillerinde toplu halde elde edebilirsiniz.</li>
  <li>Elde ettiğiniz bu geniş veri setini saniyeler içinde <code>.xlsx</code> veya <code>.csv</code> formatında dışa aktararak SPSS veya R gibi analiz programlarına doğrudan yükleyebilirsiniz.</li>
</ul>
<p><a href="/yoktez/" class="btn btn-sm btn-outline-success">YÖK Tez Kazıma Aracını Kullan →</a></p>

<h2><a href="/trdizin/">TR Dizin Veri Çekme Aracı →</a></h2>
<p>TÜBİTAK ULAKBİM tarafından yönetilen TR Dizin, Türkiye merkezli ulusal hakemli dergilerin en önemli indeksidir. Doçentlik başvuruları ve yerel literatür analizi için kritik olan TR Dizin'den veri toplamak bazen hantal bir sürece dönüşebilir. <a href="/trdizin/">Analizus'un TR Dizin modülü</a> sayesinde:</p>
<ul>
  <li>Ulusal dergilerdeki makalelerin başlık, özet, yazar, bağlı olunan kurum ve dergi bilgilerini kolayca listeleyip çekebilirsiniz.</li>
  <li>Belirli bir araştırma konusunun Türkiye'de yıllara göre nasıl bir gelişim gösterdiğini analiz etmek (trend ve frekans analizleri) için ham verinizi hatasız bir şekilde hızla oluşturabilirsiniz.</li>
</ul>
<p><a href="/trdizin/" class="btn btn-sm btn-outline-primary">TR Dizin Kazıma Aracını Kullan →</a></p>

<h2><a href="/openalex/">OpenAlex ile Global Literatür Analizi →</a></h2>
<p>250 milyondan fazla akademik eseri barındıran ve tamamen açık kaynaklı devasa bir bibliyografik veri tabanı olan <strong>OpenAlex</strong>, günümüzde Web of Science (WoS) ve Scopus'un en büyük ücretsiz alternatifidir. <a href="/openalex/">Analizus'un OpenAlex entegrasyonu</a> size küresel literatürün kapılarını açar:</p>
<ul>
  <li>Uluslararası makale, kitap, preprint ve konferans bildirilerinin meta verilerini gelişmiş filtrelerle (yıl, ülke, yazar, dergi) çekebilirsiniz.</li>
  <li>İlgili literatürdeki yazarların h-indeksi, kurumların genel yayın performansları ve kaynakların atıf verileri gibi kritik metrikleri süzebilirsiniz.</li>
  <li>VOSviewer veya CiteSpace gibi haritalama programlarına aktarmak üzere <em>ağ analizi (network analysis)</em> ve <em>ortak yazar (co-authorship)</em> çalışmaları için hazır ham veri setini saniyeler içinde indirebilirsiniz.</li>
</ul>
<p><a href="/openalex/" class="btn btn-sm btn-outline-info">OpenAlex Kazıma Aracını Kullan →</a></p>

<h2>Tezde Nasıl Yazılır (APA Formatı)</h2>
<p>Bibliyometrik bir tez veya sistematik derleme (systematic review) makalesi yazıyorsanız, veriyi nasıl elde ettiğinizi metodoloji bölümünde şeffafça bildirmelisiniz.</p>
<p><em>"Bu araştırmanın veri seti, [Tarih] tarihinde Analizus veri kazıma (web scraping) araçları kullanılarak oluşturulmuştur. Belirlenen anahtar kelimeler çerçevesinde YÖK Ulusal Tez Merkezi ve OpenAlex veri tabanlarından ilgili eserlerin meta verileri (başlık, yazar, yıl, özet ve kurum bilgileri) otomatik olarak çekilmiş ve analiz programlarına aktarılmak üzere .csv formatında dışa aktarılmıştır."</em></p>

<hr>
<small>
<strong>Kaynakça:</strong><br>
Priem, J., Piwowar, H., &amp; Orr, R. (2022). OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. arXiv preprint arXiv:2205.01205.<br>
TÜBİTAK ULAKBİM. (2023). TR Dizin Veri Tabanı.<br>
Yükseköğretim Kurulu (YÖK). Ulusal Tez Merkezi İstatistikleri.
</small>"""

    BlogPost.objects.filter(
        slug='analizus-veri-kazima-yok-tez-tr-dizin-openalex'
    ).update(content=content)

class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0115_blog_analizus_veri_kazima_yok_trdizin_openalex'),
    ]

    operations = [
        migrations.RunPython(guncelle, migrations.RunPython.noop),
    ]

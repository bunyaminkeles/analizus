# Dosya Adı: forum/migrations/0091_blog_survival_analizi_101.py

from django.db import migrations

def ekle(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')
    User = apps.get_model('auth', 'User')

    author = User.objects.filter(is_superuser=True).first() or User.objects.first()

    category, _ = BlogCategory.objects.get_or_create(
        slug='saglik-istatistigi',
        defaults={'name': 'Sağlık İstatistiği'}
    )

    content = """<h2>Survival (Sağkalım) Analizi Nedir?</h2>
<p>Klinik araştırmalarda araştırmacılar genellikle sadece "Tedavi edilen hasta iyileşti mi?" veya "Vefat etti mi?" sorularıyla ilgilenmezler. En az bunlar kadar kritik olan diğer soru şudur: <strong>"Bu olay ne kadar süre sonra gerçekleşti?"</strong>. İşte belirli bir olayın (ölüm, hastalığın nüksetmesi, cihazın bozulması vb.) gerçekleşmesine kadar geçen süreyi inceleyen istatistiksel yöntemlere <strong>Survival (Sağkalım) Analizi</strong> denir.</p>

<h2>Sansürlü Veri (Censored Data) Kavramı</h2>
<p>Survival analizini klasik istatistikten (örneğin T-testi veya doğrusal regresyon) ayıran en büyük fark <strong>sansürlü verilerle</strong> başa çıkabilmesidir. Araştırma süresi boyunca şu durumlarla karşılaşabilirsiniz:</p>
<ul>
  <li>Hasta araştırmadan kendi isteğiyle ayrılabilir.</li>
  <li>Hasta başka bir sebeple (örneğin trafik kazası) vefat edebilir.</li>
  <li>Araştırma süresi (örneğin 5 yıl) bittiğinde hasta hala hayatta olabilir.</li>
</ul>
<p>Bu durumlarda olayın ne zaman gerçekleşeceğini kesin olarak bilemeyiz, sadece o ana kadar olay olmadığını biliriz. İstatistiksel olarak bu durum <em>sağdan sansürlü (right-censored) veri</em> olarak adlandırılır ve veriyi çöpe atmadan analize dahil etmenin tek yolu survival analizidir.</p>

<h2>Kaplan-Meier Eğrisi ve Log-Rank Testi</h2>
<p>Sağkalım analizi yaparken başvurulan ilk yöntem <strong>Kaplan-Meier Sağkalım Eğrisi</strong>'dir. Bu analiz, olayın (örneğin ölüm) zamana bağlı olarak gerçekleşme olasılığını görselleştirir. Eğri, her bir olayın gerçekleştiği zaman noktasında aşağı doğru bir basamak oluşturur.</p>
<p>İki farklı grubu (örneğin İlaç A alanlar vs. İlaç B alanlar) karşılaştırmak istediğimizde ise <strong>Log-Rank Testi</strong> devreye girer. Log-rank testi, bu iki grubun sağkalım eğrileri arasında istatistiksel olarak anlamlı bir fark olup olmadığını (p &lt; 0.05) gösterir.</p>

<h2>Cox Orantılı Riskler Regresyonu (Cox Proportional Hazards)</h2>
<p>Kaplan-Meier sadece kategorik bir değişkenin (tedavi türü, cinsiyet vb.) etkisine bakabilir. Eğer hastanın yaşı, tansiyonu, kan değerleri gibi çok sayıda sürekli ve kategorik değişkenin sağkalım süresi üzerindeki etkisini <em>aynı anda</em> modellemek istiyorsak <strong>Cox Regresyonu</strong> kullanırız.</p>
<p>Cox modelinin en önemli çıktısı <strong>Tehlike Oranıdır (Hazard Ratio - HR)</strong>:</p>
<ol>
  <li><strong>HR = 1:</strong> Değişkenin riske etkisi yoktur.</li>
  <li><strong>HR &gt; 1:</strong> Değişken, olayın gerçekleşme (tehlike) riskini artırır. (Örn: Sigara içenlerde ölüm riskinin HR=2.5 olması, sigara içmeyenlere göre 2.5 kat daha fazla riske sahip olduklarını gösterir).</li>
  <li><strong>HR &lt; 1:</strong> Değişken koruyucudur, riski azaltır. (Örn: Yeni ilacın HR=0.6 olması, ölüm riskini %40 oranında azalttığını ifade eder).</li>
</ol>
<hr>
<small>
<strong>Kaynakça:</strong><br>
Bland, J. M., &amp; Altman, D. G. (1998). Survival probabilities (the Kaplan-Meier method). BMJ, 317(7172), 1572.<br>
Cox, D. R. (1972). Regression models and life-tables. Journal of the Royal Statistical Society: Series B (Methodological), 34(2), 187-202.<br>
Hosmer Jr, D. W., Lemeshow, S., &amp; May, S. (2011). Applied survival analysis: regression modeling of time-to-event data. John Wiley &amp; Sons.
</small>"""

    BlogPost.objects.get_or_create(
        slug='survival-analizi-101-kaplan-meier-cox-regresyon-ve-tedavi-etkili-mi',
        defaults={
            'title': 'Survival Analizi 101: Kaplan-Meier, Cox Regresyon ve "Tedavi Etkili mi?" Sorusunun İstatistikle Cevabı',
            'excerpt': 'Klinik araştırmaların belkemiği olan Survival (Sağkalım) Analizi nedir? Sansürlü veri, Kaplan-Meier eğrisi, Log-Rank testi ve Cox Regresyonu hakkında giriş niteliğinde biyoistatistik rehberi.',
            'content': content,
            'category': category,
            'author': author,
            'status': 'published'
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0090_blog_saglikta_veri_krizi'),
    ]

    operations = [
        migrations.RunPython(ekle, migrations.RunPython.noop),
    ]
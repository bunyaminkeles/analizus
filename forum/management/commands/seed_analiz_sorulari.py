"""
Analiz senaryolu İstatistik Arena soruları.
Cronbach, normallik, korelasyon, t-testi, ANOVA, betimsel çıktı okuma soruları.
Kullanım: python manage.py seed_analiz_sorulari [--clear]
"""
from django.core.management.base import BaseCommand
from forum.models import QuizQuestion

SORULAR = [
    # ── Cronbach Alpha ─────────────────────────────────────────────────────
    {
        'question': (
            'Bir Cronbach Alpha analizi çıktısında α = .873 değeri görülüyor. '
            'Bu değerin doğru yorumu hangisidir?'
        ),
        'option_a': 'Kabul edilemez düzeyde güvenilir (α < .50)',
        'option_b': 'Düşük güvenilirlik (.50 ≤ α < .60)',
        'option_c': 'Yüksek güvenilirlik (.80 ≤ α < .90)',
        'option_d': 'Mükemmel güvenilirlik (α ≥ .90)',
        'correct_answer': 'C',
        'category': 'cronbach',
        'difficulty': 'easy',
        'explanation': (
            'α = .873, 0.80 ile 0.90 arasındadır; bu da "yüksek/çok iyi güvenilirlik" anlamına gelir. '
            'Nunnally (1978) ölçütüne göre α ≥ .70 kabul edilebilir, α ≥ .80 iyi, α ≥ .90 mükemmeldir.'
        ),
    },
    {
        'question': (
            'Madde istatistikleri tablosunda "Silinince Alpha" sütununda, '
            '4. madde için değer .891 görünüyor ve genel α = .843. '
            'Bu madde için ne yapılmalıdır?'
        ),
        'option_a': 'Madde kesinlikle ölçekten çıkarılmalıdır',
        'option_b': 'Madde çıkarılırsa güvenilirlik artacağından çıkarılması değerlendirilmelidir',
        'option_c': 'Madde çıkarılırsa güvenilirlik düşeceğinden tutulmalıdır',
        'option_d': 'Bu bilgiden madde hakkında karar verilemez',
        'correct_answer': 'B',
        'category': 'cronbach',
        'difficulty': 'medium',
        'explanation': (
            '"Silinince Alpha" değeri (.891) genel alpha değerinden (.843) yüksekse, '
            'bu maddeyi silmek ölçeğin güvenilirliğini artıracak demektir. '
            'Araştırmacı bu maddeyi teorik olarak da değerlendirip karar vermelidir.'
        ),
    },
    {
        'question': (
            'Düzeltilmiş madde-toplam korelasyonu (corrected item-total correlation) '
            'negatif çıkan bir madde için ne yapılmalıdır?'
        ),
        'option_a': 'Madde olduğu gibi kullanılabilir, negatif korelasyon normaldir',
        'option_b': 'Madde ters kodlanmış olabilir; kontrol edilip gerekirse tersine çevrilmeli',
        'option_c': 'Madde analizden otomatik çıkarılır',
        'option_d': 'Örneklem büyütülerek tekrar analiz edilmelidir',
        'correct_answer': 'B',
        'category': 'cronbach',
        'difficulty': 'medium',
        'explanation': (
            'Negatif madde-toplam korelasyonu, maddenin ters yönde puanlandığına işaret edebilir. '
            'Örneğin "Hiç endişelenmem" maddesi diğer kaygı maddeleriyle ters yönde ilişkilidir. '
            'Madde ters kodlanarak yeniden analiz edilmelidir.'
        ),
    },

    # ── Normallik Testi ────────────────────────────────────────────────────
    {
        'question': (
            'Shapiro-Wilk testi sonucunda W = .962, p = .043 bulunuyor (n = 45). '
            'Bu sonucun doğru yorumu hangisidir?'
        ),
        'option_a': 'Dağılım normal; parametrik test kullanılabilir (p > .05)',
        'option_b': 'Dağılım normal değil; p < .05 olduğundan normallik reddedilir',
        'option_c': 'W değeri 1\'e yakın olduğundan dağılım normaldir',
        'option_d': 'Örneklem küçük olduğundan test geçersizdir',
        'correct_answer': 'B',
        'category': 'normallik',
        'difficulty': 'easy',
        'explanation': (
            'Shapiro-Wilk testinde p < .05 ise normallik hipotezi reddedilir; '
            'dağılımın normal olmadığı söylenir. '
            'Bu durumda non-parametrik testler tercih edilmelidir.'
        ),
    },
    {
        'question': (
            'Çarpıklık (skewness) değeri +2.31 olan bir değişken için ne söylenebilir?'
        ),
        'option_a': 'Sola çarpık; çoğu değer sağda yoğunlaşmış',
        'option_b': 'Sağa çarpık; dağılımın kuyruğu sağda uzuyor, aykırı değer olabilir',
        'option_c': 'Normal dağılım; ±1.96 sınırı içinde',
        'option_d': 'Basık bir dağılım söz konusu',
        'correct_answer': 'B',
        'category': 'normallik',
        'difficulty': 'medium',
        'explanation': (
            'Pozitif çarpıklık değeri sağa çarpıklık anlamına gelir; dağılımın kuyruğu sağa uzar. '
            '|çarpıklık| > 2 genellikle ciddi bir normallikten sapma olarak yorumlanır. '
            'Sola çarpıklık negatif değerle gösterilir.'
        ),
    },
    {
        'question': (
            'Normallik testinde p = .210 ve Q-Q plot\'ta noktalar doğruya yakın görünüyor. '
            'n = 120 olan bu örneklemde ne yapılmalıdır?'
        ),
        'option_a': 'p > .05 olduğundan ve görsel desteklediğinden parametrik test uygundur',
        'option_b': 'n > 30 olduğundan Shapiro-Wilk geçersiz, Kolmogorov-Smirnov kullanılmalı',
        'option_c': 'p değerine bakılmaksızın her zaman non-parametrik test tercih edilmeli',
        'option_d': 'n > 100 için normallik testi gerekli değil, direkt t-testi yapılmalı',
        'correct_answer': 'A',
        'category': 'normallik',
        'difficulty': 'medium',
        'explanation': (
            'p = .210 > .05 normallik hipotezinin reddedilemediğini, Q-Q plot da normal dağılımla '
            'uyumlu olduğunu gösteriyor. Her iki kanıt parametrik testin uygun olduğunu destekler.'
        ),
    },

    # ── Korelasyon ─────────────────────────────────────────────────────────
    {
        'question': (
            'İki değişken arasında Pearson r = .67, p = .002 bulunuyor. '
            'Bu sonuç ne anlama gelir?'
        ),
        'option_a': 'Zayıf ve anlamsız bir ilişki',
        'option_b': 'Orta-güçlü ve istatistiksel olarak anlamlı pozitif ilişki',
        'option_c': 'Negatif yönlü anlamlı ilişki',
        'option_d': 'Korelasyon anlamlı ama etki büyüklüğü ihmal edilebilir',
        'correct_answer': 'B',
        'category': 'korelasyon',
        'difficulty': 'easy',
        'explanation': (
            'r = .67, Cohen (1988) sınıflandırmasına göre güçlü ilişkiyi (.50+) gösterir. '
            'p = .002 < .05 olduğundan ilişki istatistiksel olarak anlamlıdır. '
            'Pozitif değer, bir değişken artarken diğerinin de arttığına işaret eder.'
        ),
    },
    {
        'question': (
            'Korelasyon matrisinde "Motivasyon – Başarı" için r = .54, p = .001; '
            '"Motivasyon – Kaygı" için r = -.38, p = .023 bulunuyor. '
            'Bu sonuçlar nasıl yorumlanmalıdır?'
        ),
        'option_a': 'Her iki korelasyon da anlamsız, ikinci değer negatif olduğundan hatalı',
        'option_b': 'Motivasyon başarıyla pozitif, kaygıyla negatif anlamlı ilişki içinde',
        'option_c': 'Sadece başarı ile ilişki anlamlı; kaygı korelasyonu yeterince güçlü değil',
        'option_d': 'Matris verisi çelişkili, yeniden analiz edilmeli',
        'correct_answer': 'B',
        'category': 'korelasyon',
        'difficulty': 'easy',
        'explanation': (
            'r = .54 (p < .05): motivasyon artarken başarı da artıyor (pozitif yön). '
            'r = -.38 (p < .05): motivasyon artarken kaygı azalıyor (negatif yön). '
            'Her iki ilişki de istatistiksel olarak anlamlıdır.'
        ),
    },
    {
        'question': (
            'Spearman korelasyonu Pearson korelasyonuna tercih edilmesi gereken durum hangisidir?'
        ),
        'option_a': 'Her iki değişken de normal dağılımlı ve sürekli ölçümse',
        'option_b': 'Büyük örneklem (n > 500) çalışmalarında her zaman',
        'option_c': 'Değişkenler sıralı (ordinal) ölçekteyse veya normallik sağlanmıyorsa',
        'option_d': 'İki değişken arasında doğrusal olmayan bir ilişki olduğunda',
        'correct_answer': 'C',
        'category': 'korelasyon',
        'difficulty': 'medium',
        'explanation': (
            'Spearman sıra korelasyonu, verilerin sıralamaya dönüştürülerek hesaplanır. '
            'Ordinal ölçekli veriler veya normal dağılım varsayımının karşılanmadığı durumlarda '
            'Pearson yerine Spearman kullanılmalıdır.'
        ),
    },

    # ── t-Testi ────────────────────────────────────────────────────────────
    {
        'question': (
            'Bağımsız örneklem t-testi çıktısında: '
            't(58) = −2.34, p = .023, d = −.60. '
            'Bu sonuç ne anlama gelir?'
        ),
        'option_a': 'Gruplar arasında anlamlı fark yok; p > .01',
        'option_b': 'Gruplar arasında anlamlı fark var, orta büyüklükte etki',
        'option_c': 'Negatif t değeri hesaplama hatasına işaret eder',
        'option_d': 'Sadece bir yönlü testte anlamlı; çift yönlü için geçersiz',
        'correct_answer': 'B',
        'category': 'ttesti',
        'difficulty': 'easy',
        'explanation': (
            'p = .023 < .05 → gruplar arasında istatistiksel olarak anlamlı fark var. '
            '|d| = .60 Cohen\'s d için orta büyüklükte etkiye karşılık gelir (.50–.80 arası). '
            'Negatif t değeri yalnızca grup 1\'in ortalamасının grup 2\'den düşük olduğunu gösterir.'
        ),
    },
    {
        'question': (
            'Levene testi sonucu F = 8.21, p = .006 çıktı. '
            'Bağımsız t-testi için ne yapılmalıdır?'
        ),
        'option_a': 'Standart t-testi uygulanabilir; Levene sonucu dikkate alınmaz',
        'option_b': 'Varyanslar homojen olmadığından Welch t-testi (eşit varyans varsayılmaksızın) tercih edilmeli',
        'option_c': 'Levene p < .05 olduğundan t-testi hiç uygulanamaz',
        'option_d': 'Örneklem büyütülerek test tekrarlanmalıdır',
        'correct_answer': 'B',
        'category': 'ttesti',
        'difficulty': 'medium',
        'explanation': (
            'Levene testi p < .05 → varyanslar homojen değil. '
            'Bu durumda "equal variances not assumed" satırı yani Welch t-testi kullanılmalıdır. '
            'Welch t-testi varyans homojenliği varsayımını gerektirmez.'
        ),
    },
    {
        'question': (
            'Bağımlı örneklem t-testi (öntest–sontest) sonucunda t(29) = 3.87, p = .001 bulundu. '
            'Bu araştırmada en doğru yorum hangisidir?'
        ),
        'option_a': 'Öntest ve sontest ortalamaları arasında anlamlı fark var; müdahale etkili görünüyor',
        'option_b': 'Gruplar arası bir fark tespit edildi',
        'option_c': 'p < .01 olduğundan etki büyük; d hesaplamaya gerek yok',
        'option_d': 'Serbestlik derecesi 29 olduğundan örneklem yeterince büyük değil',
        'correct_answer': 'A',
        'category': 'ttesti',
        'difficulty': 'easy',
        'explanation': (
            'Bağımlı t-testinde öntest ve sontest aynı bireylerden ölçülür. '
            'p = .001 < .05 anlamlı bir değişimi gösterir. '
            'Serbestlik derecesi df = n − 1 = 29 → n = 30 kişi; bu makul bir örneklemdir.'
        ),
    },

    # ── ANOVA ──────────────────────────────────────────────────────────────
    {
        'question': (
            'Tek yönlü ANOVA sonucunda F(3, 76) = 5.23, p = .002, η² = .17. '
            'Bu değerler nasıl yorumlanır?'
        ),
        'option_a': 'Anlamlı fark yok; F değeri çok küçük',
        'option_b': 'Gruplar arasında anlamlı fark var; büyük etki büyüklüğü',
        'option_c': 'Anlamlı fark var; ancak etki büyüklüğü küçük (η² < .06)',
        'option_d': 'p < .01 olduğundan post-hoc test gerekmiyor',
        'correct_answer': 'B',
        'category': 'anova',
        'difficulty': 'medium',
        'explanation': (
            'p = .002 < .05 → gruplar arasında anlamlı fark var. '
            'η² = .17 > .14 büyük etki büyüklüğüne karşılık gelir (Cohen, 1988). '
            'p < .05 olduğunda hangi gruplar arasında fark olduğunu belirlemek için post-hoc test yapılmalıdır.'
        ),
    },
    {
        'question': (
            'ANOVA sonrası Tukey HSD post-hoc testinde A–B karşılaştırması için '
            'p (düzeltilmiş) = .034, A–C için p = .421, B–C için p = .012 bulundu. '
            'Hangi gruplar arasında anlamlı fark var?'
        ),
        'option_a': 'Sadece A ile B arasında',
        'option_b': 'A-B ve B-C arasında (ikisi de p < .05)',
        'option_c': 'Hiçbiri; Bonferroni düzeltmesi gerekir',
        'option_d': 'Tüm çiftler arasında',
        'correct_answer': 'B',
        'category': 'anova',
        'difficulty': 'medium',
        'explanation': (
            'p < .05 olan çiftler: A–B (.034) ve B–C (.012). A–C (.421 > .05) anlamlı değil. '
            'Tukey HSD zaten çoklu karşılaştırma düzeltmesi içerdiğinden ek düzeltme gerekmez.'
        ),
    },
    {
        'question': (
            'ANOVA öncesi Levene testi p = .002 çıktı. '
            'Araştırmacı ne yapmalıdır?'
        ),
        'option_a': 'ANOVA uygulamaya devam edilebilir; Levene sadece bilgi amaçlıdır',
        'option_b': 'Varyans homojenliği sağlanamadığından Welch ANOVA veya Kruskal-Wallis tercih edilmeli',
        'option_c': 'ANOVA iptal edilmeli, t-testi yapılmalıdır',
        'option_d': 'Örneklem yeterince büyükse (n > 30/grup) bu sorun yok sayılabilir',
        'correct_answer': 'B',
        'category': 'anova',
        'difficulty': 'hard',
        'explanation': (
            'Levene testi p < .05 → varyans homojenliği varsayımı ihlal edilmiş. '
            'Bu durumda Welch ANOVA (varyans eşitsizliğine dayanıklı) veya '
            'non-parametrik Kruskal-Wallis testi tercih edilmelidir.'
        ),
    },

    # ── Betimleyici İstatistik ─────────────────────────────────────────────
    {
        'question': (
            'Bir değişkenin medyanı 45, ortalaması 67. '
            'Bu durum ne anlama gelir?'
        ),
        'option_a': 'Dağılım sola çarpık; birkaç düşük değer ortalamayı aşağı çekiyor',
        'option_b': 'Dağılım sağa çarpık; birkaç yüksek değer ortalamayı yukarı itiyor',
        'option_c': 'Normal dağılım; medyan ve ortalama yakın olduğunda bu normaldir',
        'option_d': 'Standart sapma hesaplanamaz',
        'correct_answer': 'B',
        'category': 'betimsel',
        'difficulty': 'easy',
        'explanation': (
            'Ortalama (67) > Medyan (45) durumunda dağılım sağa çarpıktır. '
            'Yüksek aykırı değerler ortalamayı yukarı iter; medyan bu aykırı değerlerden daha az etkilenir. '
            'Gelir verileri bu durumun klasik örneğidir.'
        ),
    },
    {
        'question': (
            'Betimsel istatistik çıktısında 5\'li Likert ölçeği verisinde '
            'Ortalama = 3.82, SS = 0.43, Min = 1, Maks = 5 görünüyor. '
            'Bu bulgu nasıl raporlanmalıdır?'
        ),
        'option_a': 'Katılımcılar ortalama 3.82 ± 0.43 puan vermiş (1–5 aralığı); dağılım geniş değil',
        'option_b': 'Min=1 ve Maks=5 olduğundan SS anlamlı değil',
        'option_c': 'Ortalama 4\'e yakın olduğundan madde analizden çıkarılmalı',
        'option_d': 'SS = 0.43 çok yüksek; veri temizlenmeli',
        'correct_answer': 'A',
        'category': 'betimsel',
        'difficulty': 'easy',
        'explanation': (
            'APA formatında betimsel istatistikler: M ± SS biçiminde raporlanır. '
            'SS = .43 düşük bir değişkenlik gösterir; katılımcılar ortalamaya yakın yanıt vermiş. '
            'Min ve Maks puanlar tüm aralığı kapsıyor olsa da bu SS değerini etkilemez.'
        ),
    },
    {
        'question': (
            'Bir araştırmada n = 250 katılımcının yaş ortalaması 28.4 (SS = 6.2). '
            'Standart hata (Standard Error of Mean) yaklaşık ne kadardır?'
        ),
        'option_a': '6.2',
        'option_b': '0.39',
        'option_c': '2.48',
        'option_d': '0.025',
        'correct_answer': 'B',
        'category': 'betimsel',
        'difficulty': 'hard',
        'explanation': (
            'SEM = SS / √n = 6.2 / √250 = 6.2 / 15.81 ≈ 0.39. '
            'Standart hata, örneklem ortalamasının standart sapmasıdır ve n büyüdükçe küçülür. '
            'SS ile SEM\'i karıştırmamak önemlidir; SS bireysel değişkenliği, SEM ortalama kesinliğini ölçer.'
        ),
    },

    # ── Genel Metodoloji ───────────────────────────────────────────────────
    {
        'question': (
            '1000 katılımcılı büyük örneklemde p = .003, d = .08 bulundu. '
            'Bu sonuç nasıl değerlendirilmelidir?'
        ),
        'option_a': 'Hem istatistiksel hem pratik açıdan anlamlı güçlü bir etki',
        'option_b': 'İstatistiksel olarak anlamlı ancak pratik etki büyüklüğü ihmal edilebilir',
        'option_c': 'p < .05 olduğundan bulgular mutlaka önemlidir',
        'option_d': 'Büyük örneklemde t-testi yerine ANOVA kullanılmalıydı',
        'correct_answer': 'B',
        'category': 'methodology',
        'difficulty': 'hard',
        'explanation': (
            'Büyük örneklemlerde çok küçük farklar bile istatistiksel anlamlılık kazanabilir. '
            'd = .08 ihmal edilebilir bir etki büyüklüğüdür (Cohen: küçük = .20). '
            'Bu nedenle p değeriyle birlikte etki büyüklüğü her zaman raporlanmalıdır.'
        ),
    },
    {
        'question': (
            'Hangi durum Tip I Hata (α hatası) olarak tanımlanır?'
        ),
        'option_a': 'Gerçekten var olan bir etkiyi tespit edememek',
        'option_b': 'Aslında olmayan bir etkiyi istatistiksel olarak anlamlı bulmak',
        'option_c': 'Yanlış bir ölçek kullanmak',
        'option_d': 'Örneklem seçiminde sistematik hata yapmak',
        'correct_answer': 'B',
        'category': 'methodology',
        'difficulty': 'easy',
        'explanation': (
            'Tip I Hata (α): Boş hipotez doğruyken onu reddetmek → sahte pozitif. '
            'Tip II Hata (β): Boş hipotez yanlışken onu reddetmemek → sahte negatif. '
            'α genellikle .05 olarak belirlenir; yani 100 testten 5\'inde yanlış pozitif bulgu çıkmasına izin verilir.'
        ),
    },
]


class Command(BaseCommand):
    help = 'Analiz senaryolu İstatistik Arena soruları ekler'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true',
                            help='Analiz kategorilerindeki mevcut soruları sil')

    def handle(self, *args, **options):
        analiz_cats = {'cronbach', 'normallik', 'korelasyon', 'ttesti', 'anova',
                       'betimsel', 'output_reading', 'methodology'}

        if options['clear']:
            deleted, _ = QuizQuestion.objects.filter(category__in=analiz_cats).delete()
            self.stdout.write(self.style.WARNING(f'{deleted} soru silindi.'))

        created = 0
        skipped = 0
        for s in SORULAR:
            _, c = QuizQuestion.objects.get_or_create(
                question=s['question'],
                defaults={
                    'option_a': s['option_a'],
                    'option_b': s['option_b'],
                    'option_c': s['option_c'],
                    'option_d': s['option_d'],
                    'correct_answer': s['correct_answer'],
                    'category': s['category'],
                    'difficulty': s['difficulty'],
                    'explanation': s.get('explanation', ''),
                    'is_active': True,
                }
            )
            if c:
                created += 1
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'{created} soru eklendi, {skipped} zaten mevcut. '
            f'Toplam: {QuizQuestion.objects.count()} soru.'
        ))

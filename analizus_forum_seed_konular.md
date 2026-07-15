# ANALIZUS — FORUM SEED KONULARI (Faz 12 editoryal içerik)
> Kullanım: `reseed_forum_topics` komutuna ya da admin'den elle girişe kaynak.
> Her konu üç testi geçer: (1) birinci ağızdan, (2) gerçek kısıt/veri içerir,
> (3) doğrulanmış uzman cevabı AI cevabından görünür biçimde iyidir.
> "Huni" satırı hangi hizmete lead ürettiğini gösterir — cevabı o alandaki
> doğrulanmış uzman yazmalı; cevap vitrindir.

---

## AKADEMİK SÜREÇ

**1. Hakem 2 tüm analizimi SEM ile tekrarlamamı istiyor — zorunda mıyım?**
Kategori: Akademik Danışmanlık · Huni: analiz hizmeti + danışmanlık
> Q1 bir dergiye gönderdiğim makalede hiyerarşik regresyon kullandım. Hakem 2
> "ilişkiler yapısal eşitlik modeliyle test edilmeli" diyor, Hakem 1'in itirazı yok.
> Örneklemim 214 kişi — SEM için sınırda. Revizyon mektubunda direnmek mi,
> dönüştürmek mi daha akıllıca? Direneceksem nasıl gerekçelendiririm?

**2. Etik kurul, retrospektif kurum verisi için de bireysel onam istedi — süreç böyle mi işliyor?**
Kategori: Etik Kurul · Huni: tez danışmanlığı / süreç danışmanlığı
> Tezimde hastane kayıtlarından anonimleştirilmiş 2019-2023 verisi kullanacağım.
> Etik kurul her hastadan onam alınmasını istedi ama hastaların çoğuna ulaşmak
> imkânsız. Muadil çalışmalarda "onam muafiyeti" görüyorum — muafiyet başvurusu
> nasıl yazılır, hangi gerekçe kabul görüyor?

**3. YÖK Tez yüklemesinde benzerlik raporu %18 çıktı — yöntem bölümü şişiriyor, ne yapmalıyım?**
Kategori: YÖK Tez / Tez Süreci · Huni: metin editörlüğü
> Turnitin raporumda benzerliğin çoğu yöntem bölümünden geliyor (ölçek tanımları,
> standart prosedür cümleleri). Üniversitem üst sınırı %20 ama danışmanım %15 altı
> istiyor. Yöntem bölümünde herkesin aynı şeyi yazdığı yerler nasıl düşürülür —
> alıntılama mı, yeniden yazım mı?

**4. Danışmanım SPSS istiyor ama verim panel veri — R'da yapıp SPSS diliyle raporlamak sorun olur mu?**
Kategori: Danışman-Yöntem Uyuşmazlığı · Huni: analiz hizmeti (R/SPSS)
> Verim 5 yıllık panel (86 firma × 5 yıl). SPSS'te panel regresyon desteği fiilen
> yok, R'da plm ile kurdum. Danışmanım SPSS dışında yazılım bilmiyor ve çıktıları
> SPSS formatında görmek istiyor. Jüride "neden R" sorusu gelirse nasıl savunurum,
> yoksa analizi SPSS'in yapabildiği bir modele mi indirgemeliyim?

**5. Tez önerimde G*Power ile 128 kişi hesapladım, jüri 300 istedi — nasıl savunurum?**
Kategori: Tez Önerisi · Huni: tez danışmanlığı + güç analizi hizmeti
> Öneri savunmasında güç analizimi (f²=.15, güç .95) sundum, jüri üyesi "sosyal
> bilimlerde 300 altı örneklem olmaz" dedi. Hocanın dediği mi, hesabın dediği mi?
> Revize öneride güç analizini nasıl sunmalıyım ki hem bilimsel hem ikna edici olsun?

**6. ChatGPT'ye yazdırdığım analiz yorumlarını jüri fark eder mi — doğrulatmak istiyorum**
Kategori: AI Doğrulama · Huni: doğrulama hizmeti (source=verification hunisinin forum ayağı)
> İtiraf: bulgular bölümümdeki tablo yorumlarını büyük ölçüde ChatGPT yazdı.
> Şimdi savunma yaklaşıyor ve iki korkum var: yorumlarda fark etmediğim istatistik
> hatası olması ve jürinin metinden şüphelenmesi. Birine kontrol ettirmek istiyorum —
> neye baktırmalıyım, sadece dil mi, sayıların tutarlılığı mı?

## VERİ ANALİZİ & BI

**7. Excel 80 bin satırda yavaşladı — Power Query yeter mi, Power BI'a mı geçmeliyim?**
Kategori: Excel / Power BI · Huni: kurumsal BI hizmeti
> Aylık satış raporunu 6 şubeden gelen CSV'leri birleştirerek elle yapıyorum,
> dosya 80 bin satırı geçti ve her ay 2 günümü alıyor. VLOOKUP'lar çöküyor.
> Power Query ile mevcut Excel'de mi kalmalıyım, yoksa bu iş artık Power BI işi mi?
> Geçiş maliyeti (öğrenme + lisans) küçük bir ekip için mantıklı mı?

**8. Tableau dashboard'um var ama yönetim hâlâ haftalık Excel istiyor — otomatik besleme kurulur mu?**
Kategori: Tableau · Huni: BI otomasyon hizmeti
> Satış verisini Tableau'da gayet iyi görselleştirdim ama genel müdür "bana Excel
> gönder" diyor. Her hafta dashboard'dan elle export alıyorum. Tableau'dan
> zamanlanmış Excel/PDF çıktısı almanın ya da bu döngüyü tamamen otomatikleştirmenin
> yolu nedir? Tableau Server yok, sadece Desktop var.

**9. Anket verimde ters kodlu maddeleri işlemeden ölçek puanı hesaplamışım — analizleri baştan mı alacağım?**
Kategori: İstatistik / Veri Temizliği · Huni: analiz kontrol hizmeti
> 40 maddelik ölçekte 8 ters madde varmış, farkında olmadan ham haliyle toplam
> puan aldım ve güvenirlik ile korelasyonları raporladım. Cronbach alfa .58 çıkmıştı
> — şimdi sebebini anladım. Hangi sonuçlar kurtarılabilir, hangileri kesin yeniden
> hesaplanmalı? Benzer hata yapıp yakalanan var mı?

## AI / ML / AGENTIC

**10. 12 bin Türkçe müşteri yorumum var — duygu analizi için hazır model mi, fine-tune mu?**
Kategori: NLP · Huni: NLP proje hizmeti
> E-ticaret sitemizin ~12 bin ürün yorumunu olumlu/olumsuz/nötr sınıflamak
> istiyorum. Türkçe hazır modeller (BERTurk tabanlı) yeterli olur mu, yoksa kendi
> verimle fine-tune mu etmeliyim? Etiketli verim yok — etiketleme maliyetine
> girmeden başlamanın yolu var mı? Bütçe sınırlı, GPU yok.

**11. Üretim hattı sensör verisinden arıza tahmini — 3 yılda sadece 41 arıza kaydım var, ML mümkün mü?**
Kategori: ML / Endüstri · Huni: kurumsal ML danışmanlığı
> Fabrikada 12 sensörden dakikalık veri topluyoruz (3 yıl birikti) ama toplam arıza
> sayısı 41. Bu kadar dengesiz sınıfla arıza tahmini modeli kurulur mu, yoksa
> anomali tespiti gibi başka bir çerçeve mi düşünmeliyim? Yönetime "AI yapalım"
> demeden önce neyin gerçekçi olduğunu bilmek istiyorum.

**12. Muhasebede her ay tekrarlayan mutabakat işleri — agentic AI ile otomasyona nereden başlanır?**
Kategori: Agentic AI · Huni: agentic otomasyon hizmeti (AI Çözümler)
> KOBİ'de ön muhasebe tarafında her ay aynı döngü: banka ekstrelerini indir,
> cari hesaplarla eşleştir, uyuşmayanları listele, mail at. "AI agent'larla
> otomatikleşir" deniyor ama nereden başlanacağını bilmiyorum. Bu süreç agentic
> otomasyon için uygun bir ilk aday mı, yoksa klasik RPA/script işi mi? Riskleri ne?

---

## YAYINLAMA KURALLARI (önemli — güven mimarisini korur)

1. **Kademeli yayın:** 12 konu aynı gün açılmaz — haftada 2-3 konu, birkaç haftaya
   yayılır. Aynı anda açılan 12 konu seed olduğunu bağırır.
2. **Cevap vitrindir:** Her konuya en geç birkaç gün içinde o alandaki DOĞRULANMIŞ
   uzman hesabından özenli, somut bir cevap yazılır. Cevapsız seed, boş raftan kötüdür.
   Cevap, ilgili hizmete zorlamadan köprü kurabilir ("bu iş şu kapsamda yaptırılabilir"
   düzeyinde — satış diliyle değil).
3. **Sahte metrik yok:** Görüntülenme/beğeni şişirilmez (Faz 12 zaten temizliyor).
   Gerçek sayı küçükse hiç gösterilmez.
4. **Gerçek hesaplar:** Konular gerçek ekip/uzman hesaplarından açılır; hayalet
   hesap ordusu kurulmaz. Bir hesabın art arda 5 konu açması yerine farklı gerçek
   hesaplara dağıtılır.
5. **Konu → hizmet eşlemesi canlı tutulur:** Bir seed konu gerçek trafik/cevap
   çekmeye başlarsa, o alanda yeni (gerçek) sorular teşvik edilir — seed'in amacı
   pompayı çalıştırmak, kalıcı içerik olmak değil.

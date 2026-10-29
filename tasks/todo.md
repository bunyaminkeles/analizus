# Çok Dilli Yayın (EN/DE) — YAYINDA

**Durum (29 Ekim 2026 gece):** Bibliometri Grup A (A1-A9) tamamen bitti,
`main`'de canlı (Hetzner). Grup B (bibliometrix/VOSviewer yol haritası):
**B1 (veri kalitesi) ve B2 (bilim haritalama) TAMAMEN BİTTİ — 8/8**
(B1-1 OpenAlex zenginleştirme, B1-2 tekilleştirme, B1-3 yazar birleştirme,
B1-4 anahtar kelime normalizasyonu; B2-1 Bradford Kanunu, B2-2 Louvain
kümeleri + tablo, B2-3 Tematik Harita, B2-4 Tematik Evrim, B2-5 Üç Alan
Grafiği, B2-6 SCP/MCP, B2-7 Bibliyografik Eşleşme + Yerel/Küresel Atıf,
B2-8 Konu Modelleme NMF). B1+B2 (B1-1..B2-8 tamamı) kullanıcı isteğiyle
`--no-ff` ile `main`'e merge edilip push edildi (Hetzner deploy tetiklendi,
merge öncesi production'da aktif kullanıcı kontrolü yapıldı). İstatistik
araç sayısı 17→26. **B3 (Çıktılar) başladı: B3-1 (Temiz Veri Seti İndirme
XLSX/CSV) + B3-2 (VOSviewer map+network export) + Topic Map/Bradford Kanunu
görsel bug düzeltmeleri TAMAMLANDI — 29 Ekim 2026 `--no-ff` ile `main`'e
merge edilip push edildi (merge commit `19bdefd`, GitHub Actions ile Hetzner
deploy tetiklendi, migration `0008`/`0009` uygulandığı ve site 200 döndüğü
doğrulandı; merge öncesi production'da 2 aktif kullanıcı vardı,
kullanıcı kararıyla yine de devam edildi).** **Yeni oturum buradan devam
etsin: sıradaki B3-3 (hazır Yöntem metni + PRISMA diyagramı), sonra B3-4,
sonra B4** (B3-2b — Biblioshiny WoS-plaintext export — R/bibliometrix ile
test edilebildiğinde ayrı ele alınacak; bkz. madde 2 altındaki detaylı
liste ve `bibliometri_durum_ve_gelistirme_prompt.md` §4).
Ayrıca aşağıdaki 1 ayrı
açık iş hâlâ bekliyor (bu Grup B turunda ele alınmadı, kullanıcı kararı):

1. **DE/EN tarama araçlarının otomatik özet paragrafı Türkçe kalıyor** —
   kaynağı bulunamadı (`claude_service.generate_summary` değil, semanticscholar
   job_runner/views'ta `generate_summary` çağrısı yok). Detay: aşağıdaki
   "AÇIK İŞLER" listesinde 29 Ekim 2026 maddesi.
2. **Grup B** (bibliometrix/VOSviewer kalitesinde yol haritası — B1 veri
   kalitesi → B2 bilim haritalama → B3 çıktılar → B4 ürün/huni), plan
   dosyası: `bibliometri_durum_ve_gelistirme_prompt.md` §4.
   - [x] **B1-1 TAMAMLANDI (29 Ekim 2026, dev'de, push edildi):**
     DOI ile OpenAlex zenginleştirme. `bibliometrics/services/enrichment.py`
     (yeni) + `openalex/services/scraper.py.fetch_works_by_dois()` (yeni,
     mevcut arama koduna dokunulmadı) + `SiteSettings.
     bibliometri_openalex_zenginlestirme_max_kayit` (default 2000, migration
     `forum/0192`) + `job_runner.py`/`report_notes.py` entegrasyonu. 6 yeni
     pytest + gerçek DOI ile manuel doğrulama. `forum+bibliometrics` 124/124.
     Detay: `analizus.md` §27 (29 Ekim B1-1 maddesi).
   - [x] **B1-2 TAMAMLANDI (29 Ekim 2026, dev'de, push edildi):** Tekilleştirme
     iyileştirmesi. `parser.py._deduplicate_and_filter`: DOI yoksa artık
     normalize edilmiş başlık (noktalama yok sayılır) + yayın yılı ile eşleşir
     (yıl ikisinde de biliniyorsa farklı yıllar ayrı kayıt sayılır — ör. aynı
     "Editöryal" başlığı farklı yıllarda yanlışlıkla birleşmez; yıl taraflardan
     birinde eksikse eski davranış gibi yalnız başlığa güvenilir). 5 yeni
     pytest. Rapor metni (`report_notes.py` "Uygulanan kurallar") EN/DE
     güncellendi. Migration yok. `forum+bibliometrics` 129/129.
   - [x] **B1-3 KISMEN TAMAMLANDI (29 Ekim 2026, dev'de, push edildi):**
     Yazar adı birleştirme — yalnız "Soyad + baş harf" normalizasyonu kısmı
     (aksan/büyük-küçük harf yok sayılır). `analyzer.py`'ye `canonical_author_key()`
     + `_group_authors()` eklendi; `top_authors`/`lotka_law`/`author_collaboration`
     artık isim varyantlarını ("Smith, J." / "John Smith") tek kişi sayıyor.
     **"OpenAlex author ID varsa onu kullan" kısmı BİLİNÇLİ OLARAK ERTELENDİ:**
     CSV/BibTeX yazar listesi ile OpenAlex authorship listesi arasında konumsal
     eşleme güvenilir değil (sıra/sayı farklı olabilir) — isim benzerliğiyle
     eşleme gerekir, bu da Faz B2'nin ("yazar ID ile homonym çözümü") işi;
     orada düzgün yapılacak. 7 yeni pytest (`canonical_author_key`,
     `_group_authors`, 3 fonksiyonun varyant birleştirmesi). Rapor "Kısıtlar"
     metni güncellendi (EN/DE). Migration yok. `forum+bibliometrics` 136/136.
   - [x] **B1-4 TAMAMLANDI (29 Ekim 2026, dev'de, push edildi) — B1 (Veri
     kalitesi) TAMAMEN BİTTİ:** Anahtar kelime normalizasyonu. `normalize_keywords`:
     tire ile boşluk artık eşdeğer sayılıyor ("COVID-19" ~ "COVID 19"); TR
     lemmatization kelimeyi değiştirmediyse (muhtemelen yabancı kelime) basit
     bir çoğul→tekil kuralı devreye giriyor (`_simple_depluralize`: cats→cat,
     boxes→box, studies→study). **Yan bulgu (düzeltilmedi, kapsam dışı):** lokal
     dev ortamında zeyrek'in TR lemmatization'ı NLTK `punkt_tab` kaynağı eksik
     olduğu için sessizce başarısız oluyor (`except Exception: pass` ile orijinal
     kelimeyi döndürüyor) — prod'da durum doğrulanmadı, ayrı bir inceleme
     gerektirir. 4 yeni pytest, rapor "Uygulanan kurallar" metni EN/DE
     güncellendi, migration yok. `forum+bibliometrics` 139/139.
   - [x] **B2-1 TAMAMLANDI (29 Ekim 2026, dev'de, push edildi):** Bradford
     Kanunu. `analyzer.py`'ye `bradford_zones()` (saf hesap, test edilebilir)
     + `bradford_law()` (tablo+grafik, citation_analysis'teki iki panel
     kalıbı) eklendi; `run_all_analyses`'a 18. analiz olarak kaydedildi
     (istatistik araç sayısı 17→18). Tablo sabit ~2.6" yükseklikte üstte
     sabitlendi (Topic Map'teki "devasa boş alan" sorunuyla aynı kalıba
     düşülmedi — küçük/büyük veri setiyle görsel olarak doğrulandı). Tüm
     "17 Analiz" referansları (2 şablon, e-posta metni, admin/SiteSettings
     help_text) 18'e güncellendi. 5 yeni pytest, rapor "kurallar" metnine
     yöntem cümlesi eklendi, EN/DE çevrildi. Migration yok.
     `forum+bibliometrics` 143/143.
   - [x] **B2-2 TAMAMLANDI (29 Ekim 2026, dev'de, push edildi):** Anahtar
     kelime eş-oluşum ağı + Louvain kümeleri. `analyzer.py`'de mevcut
     `greedy_modularity_communities` yerine sabit seed'li `louvain_communities`
     kullanılacak şekilde değiştirildi (VOSviewer/bibliometrix eşitliği,
     tekrarlanabilir kümeler); hesap `keyword_clusters()` (saf, test edilebilir)
     fonksiyonuna ayrıldı. Grafik iki panelli hale getirildi (Bradford/
     citation_analysis kalıbı): sol = ağ grafiği, sağ = **küme başına ilk
     kelimeler tablosu** (eksik olan asıl madde) + toplam kelime/bağlantı/küme
     özeti. Tablo metni taşmayacak şekilde kırpıldı, görsel olarak doğrulandı
     (3 ayrık konu grubuyla sentetik veri → 3 doğru küme). 5 yeni pytest
     (kümelerin doğru ayrıldığı + sabit seed'le determinizm dahil). Rapor
     "kurallar" metnine Louvain açıklaması eklendi, EN/DE çevrildi. Yeni paket
     yok (`networkx` zaten `requirements.txt`'te, `louvain_communities`
     3.6.1'de mevcut). Migration yok. `forum+bibliometrics` 147/147.
   - [x] **B2-3 TAMAMLANDI (29 Ekim 2026, dev'de, push edildi):** Tematik
     Harita (Callon merkeziyet × yoğunluk). `analyzer.py`'ye `thematic_map_themes()`
     (saf hesap: her Louvain kümesinin dışa bağlantı gücü = merkeziyet, iç
     bağlantı gücü/büyüklük = yoğunluk) + `thematic_map()` (4 kadranlı balon
     grafiği — Motor/Niş/Temel/Gelişen-Azalan Temalar, kadran sınırı = ortalama
     değerler) eklendi, 19. analiz olarak kaydedildi (istatistik araç sayısı
     18→19, tüm "N Analiz" referansları güncellendi). `keyword_clusters()`
     (B2-2) üzerine inşa edildi — ayrı community detection YOK. Senkronize
     test verisiyle (3 konu, biri izole) doğru davranış görsel + test ile
     doğrulandı: izole küme merkeziyet=0, köprü kelimesi paylaşan iki küme
     yüksek merkeziyet alıyor. 4 yeni pytest, rapor "kurallar" metni EN/DE
     güncellendi. Yeni paket/migration yok. `forum+bibliometrics` 150/150.
     **Not (B2-4+ için tekrarlayan bakım yükü):** her yeni analiz "N Analiz"
     sayısını 7+ dosyada (2 şablon, e-posta, admin/SiteSettings help_text,
     pdf_builder yorumu) elle güncellemeyi gerektiriyor — ileride tek bir
     `len(analyses)` kaynağına taşınabilir (ayrı refactor, şimdi yapılmadı).
   - [x] **B2-4 TAMAMLANDI (29 Ekim 2026, dev'de, commit edildi):** Tematik
     Evrim (dönemler arası tema akışı). `analyzer.py`'ye `thematic_evolution_periods()`
     (yayın yılına göre otomatik dönemlendirme — kullanıcı kesim yılı girmiyor,
     veri yeterliyse 3 değilse 2 dönem) + `thematic_evolution_themes()` (her
     dönem `keyword_clusters()` (B2-2) ile BAĞIMSIZ kümelenir, ardışık
     dönemler arası paylaşılan anahtar kelime sayısı akış ağırlığı) +
     `thematic_evolution()` (el yapımı alüvyal/Sankey diyagramı — matplotlib
     `PathPatch` + Bezier eğrili şeritler, `networkx`/plotly gerekmedi)
     eklendi, 20. analiz olarak kaydedildi (istatistik araç sayısı 19→20,
     tüm "N Analiz" referansları — 2 şablon, e-posta, admin/SiteSettings
     help_text, pdf_builder yorumu — güncellendi). Tema büyüklüğü kasıtlı
     olarak kelime kümesinin eleman SAYISI (frekans ağırlığı değil) seçildi:
     iki dönemin kümeleri birbirinden bağımsız birer bölüntü olduğundan, bu
     seçim akış şeritlerinin kutu yüksekliğini hiçbir zaman aşmamasını
     matematiksel olarak garanti ediyor. Senkronize test verisiyle (köprü
     tema + yalnız bir dönemde var olan temalar) görsel + pytest ile
     doğrulandı. 5 yeni pytest, rapor "kurallar" metni EN/DE çevrildi. Yeni
     paket/migration yok. `forum+bibliometrics` 155/155.
     **Ders (tekrar düşülmesin):** `makemessages` çalıştırılırken yanlışlıkla
     `--no-location` flag'i kullanıldı (önceki S3 turunda da aynı hata
     yapılmıştı, bkz. ilgili not) — hemen fark edilip `git checkout` ile geri
     alındı, flag'siz tekrar çalıştırıldı.
   - [x] **B2-5 TAMAMLANDI (29 Ekim 2026, dev'de, commit edildi):** Üç Alan
     Grafiği (bibliometrix 'Three Fields Plot' eşdeğeri, Yazar ↔ Anahtar
     Kelime ↔ Dergi). `analyzer.py`'ye `three_field_plot_data()` (saf hesap:
     yazar/dergi kutu büyüklüğü yalnız gösterilen top-N anahtar kelimelerle
     birlikte geçme toplamı; anahtar kelime kutu büyüklüğü TÜM veri setindeki
     toplam frekans — B2-4'teki "akış kutuyu asla aşamaz" ispatıyla aynı
     mantık) + `three_field_plot()` (3 sütunlu alüvyal/Sankey diyagramı,
     B2-4'teki `_sankey_ribbon()` yeniden kullanıldı ama çizim döngüsü
     KASITLI OLARAK AYRI fonksiyon — test edilmiş `thematic_evolution()`'a
     dokunulmadı) eklendi, 21. analiz olarak kaydedildi (istatistik araç
     sayısı 20→21, tüm "N Analiz" referansları güncellendi). **Görsel
     doğrulamada bulunup düzeltilen gerçek bug:** 8+ öğeli sütunlarda
     (yazar/dergi, B2-4'teki 2-4 dönemden farklı olarak çok daha fazla öğe
     olabiliyor) öğeler arası boşlukların toplamı `max_total`'ı aşıp en alttaki
     kutuyu grafik alanının dışına itiyordu — sütun yüksekliği hesabı
     `canvas_height = max(toplam + (öğe_sayısı-1)×boşluk)` olarak düzeltildi
     (yalnız bu fonksiyonda; `thematic_evolution` dokunulmadı, orada henüz
     tetiklenmemiş gizli/latent aynı risk var — ileride öğe sayısı artarsa
     akılda tutulmalı). Sentetik + rastgele (8 yazar × 9 kelime × 5 dergi)
     veriyle görsel doğrulandı. 3 yeni pytest, rapor "kurallar" metni EN/DE
     çevrildi. Yeni paket/migration yok. `forum+bibliometrics` 158/158.
   - [x] **B2-6 TAMAMLANDI (29 Ekim 2026, dev'de, commit edildi):** Ülke
     İşbirliği SCP/MCP (bibliometrix 'Corresponding Author's Country'
     eşdeğeri). **Durum tespiti:** "Ülke İşbirliği Ağı" (network grafiği)
     zaten mevcuttu (`country_collaboration()`, analiz #15) — eksik olan
     asıl parça SCP/MCP yığılmış çubuktu. `analyzer.py`'ye `scp_mcp_counts()`
     (saf hesap: her kayıt `_record_countries()` ile sınıflandırılır — 1
     ülke → o ülke için SCP, 2+ ülke → listedeki HER ülke için MCP, mevcut
     "tam sayım" kuralıyla tutarlı) + `scp_mcp_chart()` (top-10 ülke, yatay
     yığılmış çubuk — `top_journals()`/`top_cited()` ile aynı görsel dil)
     eklendi, 22. analiz olarak kaydedildi (istatistik araç sayısı 21→22,
     tüm "N Analiz" referansları güncellendi). **Dünya haritası (plan
     dosyasında zaten "opsiyonel" işaretliydi) kullanıcı kararıyla kapsam
     dışı bırakıldı** — GeoJSON + matplotlib poligon ek karmaşıklık. Sentetik
     veriyle (12 ülke, ağırlıklı rastgele SCP/MCP dağılımı) görsel doğrulandı
     — bibliometrix'in gerçek SCP/MCP grafiğiyle aynı kalıp. 3 yeni pytest,
     rapor "kurallar" metni EN/DE çevrildi. Yeni paket/migration yok.
     `forum+bibliometrics` 161/161.
   - [x] **B2-7 TAMAMLANDI (29 Ekim 2026, dev'de, push edilmedi):** Atıf
     ağları. **Veri durumu netleştirildi (AskUserQuestion ile kullanıcıya
     soruldu):** `referenced_works` yalnız DOI'li ve B1-1 OpenAlex
     zenginleştirmesinden geçen kayıtlarda dolu; her kaydın KENDİ OpenAlex
     ID'si hiçbir yerde saklanmıyordu — klasik "co-citation" (harici atıf
     edilen eserler arası ağ) için düğümler yalnız ham ID ile etiketlenebilir
     (başlık için yüzlerce ek API çağrısı gerekir) — kullanıcı bu nedenle en
     dar/en değerli kapsamı seçti: **Bibliyografik Eşleşme (Bibliographic
     Coupling) + Yerel/Küresel Atıf**, harici co-citation ağı YAPILMADI.
     `enrichment.py`'ye `rec['openalex_id']` eklendi (B1-1 akışında, `work.
     get('id')`) + `parser.py` `EMPTY_RECORD`'a `'openalex_id': ''` eklendi.
     `analyzer.py`'ye `bibliographic_coupling()` (iki yayın aynı esere atıf
     yapıyorsa bağlanır, kenar ağırlığı paylaşılan referans sayısı —
     `country_collaboration()`/`author_collaboration()` ile aynı ağ çizim
     kalıbı, Counter + fallback) + `local_citation_counts()`/
     `local_global_citations()` (saf hesap + çizim ayrımı, `scp_mcp_counts`/
     `scp_mcp_chart` kalıbıyla tutarlı — "yerel atıf" = bu veri setindeki
     diğer kayıtlardan kaç tanesinin referenced_works'ünde bu kaydın
     openalex_id'si geçtiği) eklendi, 23. ve 24. analiz olarak kaydedildi
     (istatistik araç sayısı 22→24, tüm "N Analiz" referansları 7 dosyada
     güncellendi). **Görsel doğrulamada bulunup düzeltilen gerçek tasarım
     sorunu:** ilk tasarımda yerel/küresel atıf aynı eksende çift çubuk
     olarak çiziliyordu — küresel atıf (tüm literatür) yerel atıftan
     (küçük veri setindeki iç atıf) yapısal olarak çok büyük olduğundan
     (gerçek veride de hep böyle olacak) yerel çubuk görünmez kalıyordu;
     tasarım tek çubuğa (yerel atıf, sıralama ölçütü) + her çubuğun yanına
     "{yerel} yerel · {küresel} küresel atıf" metin etiketine çevrildi —
     ikisi de ölçek farkından bağımsız okunabilir. `local_global_citations`
     bu nedenle `has_citations=False` (PubMed) kaynaklarda da atlanan
     `citation_based` kümesine eklendi (küresel atıf her zaman 0 olurdu).
     Sentetik veriyle (25 yayın × paylaşılan referans havuzu; 12 iç-atıflı
     kayıt) görsel doğrulandı. 8 yeni pytest (ağ düğüm sayısı + yerel atıf
     sıralaması + eşik altı/üstü durumlar), rapor "kurallar" metni (2 yeni
     cümle) EN/DE çevrildi. Yeni paket yok, migration yok (openalex_id
     kayıt içi bir alan, model değil). `forum+bibliometrics` 167/167.
   - [x] **B2-8 TAMAMLANDI (29 Ekim 2026, dev'de, push edilmedi):** Konu
     Modelleme. **İki tasarım kararı AskUserQuestion ile netleştirildi:**
     (1) NMF + TF-IDF (determinist, nndsvd init + sabit seed — LDA'nın
     küçük veri setlerinde daha fazla ayar gerektiren olasılıksal
     yaklaşımına tercih edildi), (2) `research_gap()`'e DOKUNULMADI —
     B2-8 tamamen bağımsız 2 yeni analiz olarak eklendi (plan dosyasındaki
     "Research Gap'i bununla destekle" notu ileride ayrı görev olabilir).
     `analyzer.py`'ye `topic_modeling_data()` (özetler `normalize_abstract_words()`
     ile TR stopword filtreli/lemmatize edilip TF-IDF matrisine dönüştürülür +
     sklearn'ün İngilizce stopword listesi, NMF ile gizli konulara ayrıştırılır,
     her kayıt en baskın konusuna atanır — `topic_map()`'ten [anahtar kelime
     eş-oluşum ağı] TAMAMEN FARKLI yöntem, özet METNİNİ kullanır) +
     `topic_modeling_words_chart()` (konu başına panel, en belirleyici
     kelimeler) + `topic_modeling_trend()` (konulara göre yıllık yayın payı,
     yığılmış çubuk, zaman serisi) eklendi, 25. ve 26. analiz olarak
     kaydedildi (istatistik araç sayısı 24→26, tüm "N Analiz" referansları
     7 dosyada güncellendi). **İki ayrı analiz aynı pahalı NMF hesabını
     paylaştığından** `run_all_analyses()`'te bir kez hesaplanıp iki
     fonksiyona da geçiriliyor (gereksiz 2x fit önlendi). **Görsel
     doğrulamada bulunup düzeltilen gerçek kalite sorunu:** istenen konu
     sayısı (varsayılan 6) gerçek ayrışmadan fazla olduğunda, hiçbir
     kaydın BASKIN konusu olmayan "gürültü" konuları (ortak akademik
     kelimelerin — study/result/research vb. — kendi bileşeni) panelde
     "(0 kayıt)" ile boş/anlamsız gösteriliyordu — `topic_modeling_data()`
     artık 0 kayıtlı konuları çıkarıp kalanları yeniden numaralandırıyor.
     Sentetik veriyle (4 net ayrışan konu kümesi + ortak gürültü kelimeleri,
     60 kayıt) görsel doğrulandı. 6 yeni pytest (iki net kelime kümesinin
     karışmadan ayrışması + yetersiz özet/yıl durumları), rapor "kurallar"
     metni (1 yeni cümle) EN/DE çevrildi. Yeni paket yok (scikit-learn zaten
     requirements'ta), migration yok. `forum+bibliometrics` 173/173.
     **Grup B'nin B1+B2 bölümü artık TAMAMEN BİTTİ (8/8); main'e merge
     henüz yapılmadı (kullanıcı istemedi).**
   - [x] **B3-1 TAMAMLANDI (29 Ekim 2026, dev'de):** Temiz Veri Seti İndirme
     (XLSX+CSV, herkese ücretsiz — kullanıcı kararı). Yeni
     `bibliometrics/services/export_builder.py`; `BibliometricJob.
     clean_data_xlsx_url`/`clean_data_csv_url` (migration `0008`);
     `job_runner.py` her iki worker'a `_upload_clean_data()` eklendi (hata
     toleranslı); `cleanup_expired_bibliometrics_s3_files()` yeni prefix;
     `job_status` JSON + `landing.html` 3. kart + `order.html` blok. 5 yeni
     pytest + gerçek job ile uçtan uca S3 doğrulaması (test nesneleri
     sonra silindi). EN/DE çevrildi (polib ile 2 fuzzy düzeltildi).
     `forum+bibliometrics` 178/178. Detay: `analizus.md` §27 (29 Ekim B3-1).
   - [x] **B3-2 TAMAMLANDI (29 Ekim 2026, dev'de):** VOSviewer Uyumlu Dışa
     Aktarım. Format resmi VOSviewer dokümanından doğrulandı (WebFetch);
     x/y/cluster bilinçli olarak gönderilmiyor (VOSviewer kendi yerleşim/
     kümelemesini çalıştırsın). 4 ağ (anahtar kelime eş-oluşumu, yazar
     işbirliği, ülke işbirliği, bibliyografik eşleşme) — veri yoksa o ağ
     atlanır. Refactor: `author_collaboration()`/`country_collaboration()`/
     `bibliographic_coupling()` artık `_*_graph()` yardımcılarını çağırıyor
     (davranış aynı, G dışa açıldı). **Refactor sırasında gerçek regresyon
     bulundu+düzeltildi:** 2 fonksiyonda `import networkx as nx` yanlışlıkla
     eksik kalmıştı (`NameError`) — `country_collaboration()`'ın hiç testi
     olmadığı için yalnız `bibliographic_coupling` testi yakaladı. Yeni
     `bibliometrics/services/vosviewer_export.py` (stdlib `zipfile`);
     `BibliometricJob.vosviewer_export_url` (migration `0009`);
     `_upload_vosviewer_export()` (B3-1 deseniyle aynı, hata toleranslı);
     B3-1'in 3. kartına üçüncü buton. 9 yeni pytest + gerçek job uçtan uca
     S3 doğrulaması. EN/DE çevrildi. `forum+bibliometrics` 187/187. **Kullanıcı
     kararı: Biblioshiny (bibliometrix) WoS-plaintext export bu turda
     YAPILMADI** (R/bibliometrix burada kurulu değil, gerçek yazılımla
     doğrulanamıyor) — ayrı B3-2b olarak bekliyor. Detay: `analizus.md` §27
     (29 Ekim B3-2).
   - [ ] B3-2b (Biblioshiny/bibliometrix WoS-plaintext export) — R ile test
     edilebildiğinde ele alınacak, ayrı onay/tur.
   - [ ] B3-3 (hazır Yöntem metni TR/EN/DE + PRISMA akış diyagramı)
   - [ ] B3-4 (grafik başına otomatik yorum cümlesi, kural tabanlı)
   - [ ] B4 (ürün/huni) — bkz. plan dosyası §4
   - [x] **Topic Map görsel kalite sorunu DÜZELTİLDİ (29 Ekim 2026, dev'de)**
     (Grup B dışı, ayrı açık işti). Kök neden sentetik veriyle render edilip
     doğrulandı: `topic_map()`'te sabit `figsize=(14,8)` (en/boy 1.75, geniş)
     dikey A4 sayfa içeriğiyle (en/boy ~0.79) uyuşmuyordu — `pdf_builder.
     _draw_figure_page()`'in en-boy-koruyan `drawImage` ölçeklemesi az küme/
     satırda (ör. 1 satır) görüntünün dikey ~%55'ini boş bırakıyordu
     (matematiksel olarak doğrulandı); ayrıca sabit fontsize=7.5 + kırpılmamış
     uzun anahtar kelime öbekleri balon sınırlarını taşıyordu. Düzeltme:
     `cols`/`rows`'a göre dinamik `figsize` (bradford_law()'daki dinamik
     yükseklik deseniyle tutarlı) + `cols` artık `sqrt`'e dayalı (2-3 kümede
     bile "tek geniş satır" yerine kareye yakın/dikey istiflenmiş düzen,
     ≤2 kümede dikey tek sütun) + anahtar kelime etiketleri 11 karaktere
     kırpılıp (`…` ile) küçültülmüş fontta (6.5) gösteriliyor. 1, 2, 3, 4,
     5, 8 küme senaryolarıyla PNG render edilip görsel olarak doğrulandı
     (hiçbiri taşmıyor, boşluk makul). 3 yeni pytest (en/boy oranı sınırı,
     figsize artık sabit değil regresyonu, 8-küme senaryosu hâlâ çalışıyor).
     `forum+bibliometrics` 190/190. Ayrı bir refactor/kaldırma gerekmedi —
     sorun tamamen çözülebildi.
   - [x] **Bradford Kanunu grafiği aynı sınıftan (ters yönde) bug DÜZELTİLDİ
     (29 Ekim 2026, dev'de)** — kullanıcı canlı PDF'ten ekran görüntüsü
     paylaştı ("Bradford's Law — Core Journal Zones" sayfası ekranın
     ortasında okunamaz dar/ince bir şerit). Kök neden: `fig_height =
     max(8, len(shown) * 0.45)` üst sınırsızdı — Bölge 1+2'de çok sayıda
     dergi olan büyük veri setlerinde (sentetik olarak 1670 kayıt/305 dergi
     ile yeniden üretildi, Bölge 1+2'de 72 dergi) `figsize=(13, 32.4)` gibi
     aşırı dar/uzun bir görüntü üretip PDF'e sığdırılınca genişliğin
     ~%49'u boş kalıyordu (hesapla doğrulandı — ekran görüntüsüyle birebir
     eşleşti). Düzeltme: diğer analizlerdeki "top N" kırpma kalıbıyla
     tutarlı şekilde en fazla **40 dergi** gösteriliyor (kırpılırsa başlığa
     not eklenir), sağ paneldeki özet tablo kırpmadan bağımsız tam sayıları
     gösterir. Aynı sentetik veriyle yeniden render edilip (13x32.4→13x18)
     görsel doğrulandı. 1 yeni pytest + 4 mevcut test regresyon olmadan
     geçti. EN/DE çevrildi (ayrıca ilgisiz bir fuzzy çeviri de fark edilip
     düzeltildi). `forum+bibliometrics` 191/191.

Ayrıca not: Hetzner'de yalnız **2 CPU** var — deploy/collectstatic yavaş
sürebilir (~10 dk'ya kadar), bir dahaki "donmuş gibi görünen" deploy'da
hemen paralel teşhis komutu çalıştırıp CPU'yu bölmeden önce birkaç dakika
daha beklenmeli (29 Ekim 2026 dersi).

## DEVAM NOKTASI (bir sonraki oturum buradan başlasın)

### AÇIK İŞLER — TEK LİSTE (24 Eylül 2026 sonu; 25 Eylül buradan başla)
Kullanıcı kuralı: **bütün eksiklikler mutlaka bu listede olmalı.** Yeni
bulgu çıktığında buraya ekle; bitince [x] yap. Ayrıntılar alttaki ilgili
maddelerde.

- [ ] **(29 Ekim 2026) Bibliometri Grup B / B1-4 sırasında çıkan yan bulgu:
  zeyrek'in Türkçe lemmatization'ı lokal dev ortamında sessizce başarısız
  oluyor — araştırılmadı.** `bibliometrics/services/analyzer.py`
  `lemmatize_word()` içindeki `analyzer.lemmatize(word)` çağrısı NLTK
  `punkt_tab` (tokenizers/punkt_tab/turkish/) kaynağı eksik olduğu için
  `LookupError` fırlatıyor; fonksiyon bunu `except Exception: pass` ile
  yutup kelimeyi değiştirmeden döndürüyor — yani lokal'de anahtar kelime
  kök indirgemesi (TR için) hiç çalışmıyor olabilir (ör. "kediler" "kedi"ye
  inmiyor). Production'da (Hetzner) bu NLTK verisinin mevcut olup olmadığı
  DOĞRULANMADI — eğer orada da eksikse canlı raporlardaki Türkçe anahtar
  kelime/kelime bulutu analizleri sessizce beklenenden daha az "akıllı"
  çalışıyor demektir (çoğul/tekil TR kelimeler ayrı sayılabilir). Sıradaki
  adım: Hetzner'de `docker compose exec web python -c "import nltk;
  nltk.data.find('tokenizers/punkt_tab/turkish/')"` ile kontrol, eksikse
  Dockerfile/deploy.sh'a `nltk.download('punkt_tab')` eklenmesi.
- [ ] **(29 Ekim 2026) Tarama araçlarının AI özet paragrafı DE/EN'de Türkçe
  kalıyor — araştırılmadı, sıraya alındı.** Kullanıcı Semantic Scholar
  aracında (muhtemelen diğer tarama araçlarında da) hem DE hem EN arayüzde
  sonuç listesinin üstündeki otomatik özet paragrafının Türkçe çıktığını
  gördü (ör. "Sorgu sonucunda toplam 0 kayıt bildirilmesine karşın..."). Kısa
  araştırma: bu metin `forum/services/claude_service.py`
  `generate_summary(lang=...)`'ten GELMİYOR — o fonksiyon doğru çalışıyor
  (system_prompt'ta "Yanıtının tamamını {dil} dilinde yaz" var, openalex
  job_runner'da `lang=translation.get_language()` ile doğru çağrılıyor).
  `semanticscholar/services/job_runner.py` ve `views.py`'de `generate_summary`
  çağrısı YOK — yani bu paragraf farklı bir mekanizmadan geliyor (muhtemelen
  `forum/services/ai_service.py` — GroqService — ya da tarama araçları
  arası paylaşımlı başka bir özet fonksiyonu, henüz bulunamadı). Sıradaki
  adım: paragrafın tam kaynağını (hangi fonksiyon/şablon) bulup `lang`
  parametresinin oraya doğru geçip geçmediğini kontrol etmek.

- [x] **(28 Ekim 2026) TAMAMLANDI — Site genelinde çok satırlı Django `{# #}`
  yorumu site kullanıcılarına düz metin olarak sızıyordu.** Kullanıcı
  Render'da bibliometri sayfasında soluk/düşük kontrastlı bir metin fark
  etti ("renk uyumu sorunu" sandı), tarayıcı çeviri eklentisiyle seçince
  gerçek içerik ortaya çıktı: `{# Ortak S3 saklama süresi uyarısı... #}`
  — Django'nun `{# #}` yorum etiketi **TEK SATIR** için tasarlanmış (CLAUDE.md
  kuralı), çok satıra yayılınca yorum olarak PARSE EDİLMİYOR, ham metin
  olarak render ediliyor. İki dosyada bulundu ve düzeltildi
  (`{% comment %}...{% endcomment %}`'a çevrildi):
  - `templates/partials/_s3_retention_notice.html` — 30+ araç sayfasında
    kullanılıyor (tüm istatistik araçları + tarama araçları + bibliometri)
  - `templates/partials/order_payment.html` — 5 **sipariş/ödeme sayfasında**
    kullanılıyor (openalex, bibliometrics, trdizin, oaipmh, semanticscholar
    — gerçek müşteri IBAN ödeme sayfaları, daha yüksek risk)
  Tüm template'lerde aynı hata kalıbı taranıp (regex ile) başka yer
  bulunmadığı doğrulandı. `render_to_string()` ile içerik sızıntısı kalmadığı
  test edildi, `forum+bibliometrics` 117/117 geçti.

- [x] **(28 Ekim 2026) TAMAMLANDI — `EMAIL_TIMEOUT` ayarı eklendi (Render'da
  admin aksiyonu donup worker öldürüldü).** Kullanıcı admin panelinden
  "Onayla ve Tam Rapor Emailini Gönder" aksiyonunu çalıştırdı, istek donup
  kaldı; Render logu kanıtladı: ASGI worker "took too long to shut down and
  was killed", ardından `[Errno 110] Connection timed out` (SMTP'ye
  ulaşılamıyor). Kök neden: `EMAIL_BACKEND` SMTP, Django'nun varsayılan
  `EMAIL_TIMEOUT` değeri `None` (sonsuz bekler) — `bibliometrics/services/
  job_runner.py`'deki 3 e-posta gönderim yeri de (`send_order_results_email`
  dahil) ham `EmailMessage().send()` kullanıyor, `EmailService.is_configured()`
  koruması yok. Çözüm: `analizdestek/settings.py`'ye `EMAIL_TIMEOUT = 15`
  eklendi — tek satır, proje genelindeki TÜM `.send()` çağrılarını kapsar,
  sonsuz donma yerine ~15 saniyede hata fırlatır (mevcut try/except'ler
  zaten yakalıyor). Kullanıcı kararıyla bu kadarı yeterli görüldü (SMTP'nin
  Render'da neden ulaşılamaz olduğu ayrıca araştırılmadı — muhtemelen
  env var eksik/yanlış, dev/staging ortamı). `forum+bibliometrics` 117/117 geçti.

- [x] **(28 Ekim 2026) TAMAMLANDI — Bibliometri "Geçmiş Analizlerim" tablosu
  analiz tamamlanınca sayfa yenilenmeden güncellenmiyordu.** Kullanıcı
  gözlemi: canlı sonuç paneli işin bittiğini gösteriyor ama alttaki geçmiş
  tablosu (sunucu tarafında sayfa yüklenirken render ediliyor) sayfa
  yenilenene kadar yeni işi listelemiyor. `bibliometrics_job_status` view'ı
  `original_filename` + `created_at` alanlarını da döndürecek şekilde
  genişletildi; `showResults()` JS'i artık tamamlanan işi `#recentJobsBody`
  tablosunun en üstüne canlı olarak ekliyor (aksiyon hücresi zaten
  TR/EN'e göre doğru yapılandırılmış `orderBtn`'in klonu). Aynı taşımada:
  demo PDF indirme linki (`downloadDemoBtn`, `data.demo_pdf_url`) de
  bağlandı — daha önce `job.demo_pdf_url` backend'de vardı ama hiçbir
  template'te kullanılmıyordu, "Demo Emaile Gönder" dışında indirme yolu
  yoktu (diğer araçlarda — openalex, istatistik — olduğu gibi doğrudan
  indirme linki eksikti). Django test client ile `job_status` endpoint'inin
  yeni alanları döndürdüğü doğrulandı, `forum+bibliometrics` 117/117 geçti.

- [x] **(28 Ekim 2026) TAMAMLANDI — E-posta doğrulama middleware'i (`EmailVerificationMiddleware`)
  aşırı engelleme hatası.** Kullanıcı raporu: `/verification-pending/`'e düşen
  doğrulanmamış kullanıcı hiçbir sayfaya gidemiyor, dil bile değiştiremiyordu.
  Kök neden: `forum/middleware.py` ALLOWED_URLS whitelist'i ilk eklendiğinden
  beri güncellenmemiş, zamanla eklenen blog/hizmetler/eğitim/istatistik
  araçları/dil seçici (`set_language`)/şifre sıfırlama gibi herkese-açık
  sayfalar listeye hiç girmemişti. Düzeltme: whitelist tamamlandı (mimari
  aynı kaldı) + 3 ek tutarsızlık giderildi — `topic_detail`/`new_topic`
  POST kollarına ve `api_ai_chat`/`ai_suggest_answer`'a view-içi
  `email_verified` kontrolü eklendi (AI widget artık `/api/` önek
  muafiyetini bypass edemiyor). `forum/tests.py` 104/104 geçti, Django test
  Client ile atomic-rollback senaryosuyla manuel doğrulandı. Plan:
  `/home/bunyamin/.claude/plans/swift-yawning-perlis.md`.
  - [ ] **Ertelendi — ayrı görev:** `topic_detail` view'ında `login_required`
    yok; teorik olarak anonim kullanıcı yorum POST edebilir (`created_by`
    `AnonymousUser` olursa FK hatasıyla 500 riski). Bu turun kapsamı dışında
    bırakıldı, ayrı onayla ele alınmalı.

- [ ] **(28 Ekim 2026) Admin Dashboard — rakamların tutarlılığı ve metinlerle
  örtüşmesi kontrol edilmeli.** Kullanıcı ekran görüntüsünde `/admin/`
  "Site yönetimi" dashboard'unu paylaştı (PLATFORM SAĞLIĞI 60/İyi, Toplam
  Kullanıcı 140, Toplam Konu 124, Toplam Gönderi 247, Toplam Görüntülenme
  93802, HİZMET PAZARI 0 açık ilan/0 bekleyen teklif/5 devam eden/23 bu ay
  bitti/toplam 31 iş, GELİR ÖZETİ bağış/vitrin/bibliometrik/OpenAlex
  ay/toplam tutarları, AKADEMİK SERVİSLER 4/24 OpenAlex, 8/65 YÖK Tez,
  2/9 Bibliometrik, 0/0 Dizin Tezleri, İSTATİSTİK ARAÇLARI 49/129 toplam,
  10/29 Cronbach α, 7/16 Normallik, 16/32 Betimleyici) ve her bir sayının
  (ay/toplam ayrımı, kart başlığı, yüzde/renk eşiği gibi) hesaplandığı
  sorguyla ve yanındaki etiket/metinle gerçekten örtüştüğünü doğrulamamızı
  istedi — henüz incelenmedi. Kontrol edilecekler: hangi view/queryset
  hangi kartı besliyor (muhtemelen admin dashboard view'ı, bkz.
  [[project_admin_analitik_turu]]), "ay" filtresinin tarih aralığı doğru mu
  (bu ay mı, son 30 gün mü), "toplam" gerçekten tüm zamanları mı kapsıyor,
  PLATFORM SAĞLIĞI skorunun bileşenleri ("Büyüme + içerik + kuyruk")
  etiketle tutarlı mı, HİZMET PAZARI "Bu Ay Bitti" ile "Toplam
  tamamlandı" sayılarının tutarlılığı, N+1 sorgu riski olup olmadığı.
  Kullanıcı kararı: önce bu TEK LİSTE'ye not edilsin, inceleme ayrı
  görev olarak ele alınacak.

- [ ] **(28 Ekim 2026) OpenAlex sayfalama (pagination) 401 Unauthorized hatası
  — araştırılmadı, bibliometri işinden bağımsız.** Render (dev/staging)
  loglarında görüldü: bir arama job'ı (`d0855985-...`) cursor ile sayfalama
  yaparken OpenAlex API'den 3 deneme boyunca 401 aldı ("OpenAlex pagination
  hatası: 401"), bu yüzden toplam 2890 bulunan kayıttan yalnızca ilk sayfa
  (200) çekilebildi; kullanıcı 1000 kayıt istemişti, 200/1000 ile kaldı
  (parser sonrası net 199). İlk sayfa isteği başarılı olduğuna göre
  `OPENALEX_API_KEY`/`mailto` muhtemelen yalnızca cursor'lu (sayfalanmış)
  isteklerde eksik/düşüyor — `openalex/services/scraper.py` `build_api_params`
  ve `_fetch_page` cursor akışı incelenmeli. Kullanıcı kararı: şimdilik not,
  araştırma ayrı görev olarak sorulacak.

- [ ] **(28 Ekim 2026) Bibliometri — Grup A hata düzeltmeleri (plan onaylandı,
  henüz uygulanmadı).** Kaynak: `bibliometri_durum_ve_gelistirme_prompt.md`
  (gerçek vaka: d4yu/user 777, kayıt→doğrulama→onboarding huninde `next`
  kayboldu, EN kullanıcı Türkçe demo rapor aldı). Sıra (her adım ayrı onayla,
  plan dosyası: `/home/bunyamin/.claude/plans/functional-crunching-raven.md`):
  - [x] A1 TAMAMLANDI (28 Ekim 2026): `forum/templates/forum/home_intl.html:551`
    sabit `/analiz/?from=hero` → `{% url "analiz_home" %}?from=hero`; reverse()
    tr/en/de doğrulandı (`/analiz/`, `/en/analiz/`, `/de/analiz/`), web+nginx
    restart edildi. NOT: aynı fonksiyonda satır 543 `fetch('/analiz/hero-upload/'...)`
    de öneksiz — A2 taramasına dahil edilecek, bu adımda dokunulmadı.
  - [x] A2 TAMAMLANDI (28 Ekim 2026, rapor): 13 bulgu bulundu, düzeltmeler ayrı
    onay bekliyor.
    - [x] **TAMAMLANDI (28 Ekim 2026)** `forum/templates/forum/home.html:1280,1288`
      — A1 ile BİREBİR AYNI hatanın düzeltmesi uygulandı (flag değerinden
      bağımsız güvenli: TR için no-op, EN/DE için düzeltme). `fetch(...)` →
      `{% url "hero_upload" %}`, redirect → `{% url "analiz_home" %}?from=hero`.
      Aynı anda `home_intl.html:543`'teki fetch satırı da aynı deseple
      düzeltildi (A1'in yan etkisiydi). reverse() tr/en/de doğrulandı
      (`/analiz/hero-upload/`, `/en/analiz/hero-upload/`, `/de/analiz/hero-upload/`),
      web+nginx restart edildi. Prod `feature_intl_consulting_home` flag
      değeri hâlâ teyit edilmedi (kullanıcı vakit bulunca komutu çalıştıracak)
      — ama artık hangi değerde olursa olsun hero akışı doğru çalışıyor.
    - [x] TAMAMLANDI: `home.html:774,782` + `home_intl.html:370,374` — "OpenAlex
      Tarama" kartı `{% url 'openalex:landing' %}` ile düzeltildi (data-card-url + href)
    - [x] TAMAMLANDI (A1 ile birlikte): `home_intl.html:543` fetch satırı düzeltildi
    - [x] TAMAMLANDI: `studyroom_detail.html` — `PROFILE_URL_TEMPLATE` sentinel
      sabiti eklendi (`{% url "profile_detail" "__USERNAME__" %}` + JS `.replace()`,
      STATUS_TEMPLATE pattern'iyle aynı yöntem), `appendRoomPost` + `renderMentions` düzeltildi
    - [x] TAMAMLANDI: `send_message.html` — aynı `PROFILE_URL_TEMPLATE` deseni, `renderMentions` düzeltildi
    - [x] TAMAMLANDI: `liderboard.html:53,80` — `{% url 'profile_detail' ... %}` ile düzeltildi (yanlış "profil" path'i de düzelmiş oldu)
    - [x] TAMAMLANDI: `analiz_console_base.html:194` — `{% url "analiz_clear_session" %}` ile düzeltildi
    - [x] TAMAMLANDI: `profile_private.html:21` — `{% url "home" %}` ile düzeltildi
    - [x] TAMAMLANDI: `trdizin/services/job_runner.py:153` — `reverse('proje_talebi')` ile düzeltildi (içerik Türkçe kalıyor, TR Dizin zaten TR'ye özgü — i18n gerekmiyor)
    - [x] TAMAMLANDI: `egitim.html:199,230` — `{% url 'analiz_home' %}` / `{% url 'tarama_hub' %}`
      ile düzeltildi (F9). Not: lokal DB'de `feature_training` flag'i False — sayfa
      404 veriyor ama bu düzeltmeyle ilgisizdir, `get_template()` parse testi + reverse()
      doğrulaması yeterli görüldü.
    - Tüm düzeltmeler reverse() (tr/en/de) + `get_template()` parse testi + canlı curl ile doğrulandı, web+nginx restart edildi
    - Temiz: e-posta şablonları, `base.html`/`partials/`, `static/js/*.js` (yalnız `/api/`), market şablonları, `HttpResponseRedirect('/...')` kalıbı yok
  - [x] A3 TAMAMLANDI (28 Ekim 2026): Gerçek kök neden session değil —
    `templates/base.html`'deki SİTE GENELİ Giriş/Kayıt Ol linkleri (navbar,
    mobil menü, AI asistan banner'ı — 6 yer) hiç `?next=` eklemiyordu (yalnız
    `service_promo.html`'deki özel CTA ekliyordu). d4yu muhtemelen navbar'ı
    kullandı, next hiç oluşmadı. Düzeltme: (1) `base.html` 6 yere
    `?next={{ request.path }}` eklendi; (2) `next`, SESSION'a değil
    **doğrulama e-postasının linkine gömülüyor** (`email_service.py`
    `send_verification_email(next_url=...)`) — cihazdan bağımsız çalışır;
    (3) `register()` next doğrulamasını e-posta göndermeden önceye aldı;
    (4) `verify_email()` next'i `onboarding`'e `?next=` ile aktarıyor;
    (5) `onboarding()`'deki 3 koşulsuz `redirect('home')` → doğrulanmış
    `next` (form action'sız olduğu için GET→POST arası otomatik korunuyor).
    Her adımda `url_has_allowed_host_and_scheme` ile açık yönlendirme
    koruması. **Uçtan uca canlı test edildi** (register→verify-email
    [taze/cihazdan bağımsız cookie ile]→onboarding→hedef sayfa; next'siz
    eski akış bozulmadı; dış domain next 3 noktada da reddedildi).
    `pytest forum/tests.py` 104/104 geçti.
  - [x] A5 TAMAMLANDI (28 Ekim 2026): `bibliometrics/services/analyzer.py`'ye
    paylaşımlı `_set_integer_year_ticks()` helper'ı eklendi (lotka_law
    pattern'i), `publication_trend`/`annual_citation_trend`/
    `publication_growth_rate` kullanıyor. 3 ve 20 yıllık sentetik veriyle
    görsel + `get_xticks()` testiyle doğrulandı. `bibliometrics/tests.py`
    eklendi (ilk kez — 5 test, hepsi geçti).
  - [x] A6 TAMAMLANDI (28 Ekim 2026, eşik N=5 kullanıcı onayıyla): Zaman
    serisi 3-4 tam yıl ise (`publication_growth_rate`'in kendi 3 yıl
    minimumuyla tutarlı) hem büyüme oranı grafiğindeki CAGR kutusuna hem
    de rapor "Veri, Yöntem ve Kısıtlar" bölümüne "Veri N yıldan kısa bir
    dönemi kapsıyor; büyüme oranları küçük taban etkisine açıktır." notu
    eklendi. Yeni `SHORT_SERIES_YEARS=5` sabiti `analyzer.py`'de, eşik
    `report_notes.py`'den `analyzer.SHORT_SERIES_YEARS` ile tek yerden
    okunuyor (duplicate yok). EN/DE çevirisi eklendi (`makemessages`
    **flag'siz** çalıştırıldı — `--no-location` tekrar denenip devasa
    gereksiz diff ürettiği görülüp geri alındı, ders tekrar doğrulandı).
    3/6 yıllık sentetik veri + EN/DE `translation.override` ile canlı
    test edildi, 2 yeni pytest eklendi (toplam bibliometrics 7 test).
    `pytest forum/tests.py bibliometrics/tests.py` 111/111 geçti.
  - [x] **TAMAMLANDI (28 Ekim 2026) Demo grafik sayısı 3→10.**
    `SiteSettings.bibliometri_demo_grafik_sayisi` (PositiveIntegerField,
    default=10, migration `0191`) eklendi — admin → Limitler'den
    değiştirilebilir. `bibliometrics/services/job_runner.py`'deki 2
    `figures[:3]` → `figures[:demo_n]` (SiteSettings'ten okunuyor).
    **Bulgu:** `pdf_builder.py` `build_demo_pdf()` içinde de AYRICA sabit
    `figures[:3]` vardı (çağıranın kırptığı listeyi tekrar 3'e indiriyordu,
    gerçek fix burasıydı) — kaldırıldı, artık çağıranın kırptığı listeye
    güveniyor. 300 kayıtlık zengin sentetik veriyle (15 grafik üretildi)
    uçtan uca test edildi: 10 grafik demo PDF'e doğru girdi (1MB PDF
    sorunsuz üretildi). `pytest forum/tests.py bibliometrics/tests.py`
    111/111 geçti. Migration dosyası container'da root sahipli oluştu,
    `chown 1000:1000` ile düzeltildi (bilinen ders, §26).
  - [ ] **ERTELENDİ — AI yorumlama (28 Ekim 2026, kullanıcı "atla" dedi, şimdilik
    yapılmayacak).** Tartışılan tasarım (ileride gerekirse buradan devam):
    proje talebi hangi job'a ait olduğunu bilsin diye CTA linki `?job=<uuid>`
    taşısın (projede zaten kullanılan "iş-spesifik ?job= link" deseni),
    `ProjectRequest`'e yeni FK alanı (`BibliometricJob`, migration); her
    grafik için ayrı Claude çağrısı (`claude_summary_service` + `AIUsageLog`
    + `feature_ai_summary` deseni — `openalex/services/job_runner.py`
    `_build_ai_prompt`/`_ai_comment_for_job` örnek alınacak), üretilince
    "taslak" etiketiyle ADMIN ONAYI bekleyecek, otomatik gönderilmeyecek
    (karar 28 Ekim 2026). `project_claude_ai_yorumu.md` hafıza notundaki
    "Faz D — Bibliometrics, en karmaşık" ile aynı iş.
  - [x] A7 KISMEN TAMAMLANDI (28 Ekim 2026) — kullanıcının verdiği örnek
    dosya aslında openalex.org web CSV'si değil, **bizim OpenAlex aracımızın
    ürettiği TXT çıktısıydı** (`openalex_txt` formatı, zaten desteklenen).
    Ama test ederken **gerçek, ciddi bir hata bulundu ve düzeltildi**:
    - **Kök neden:** `openalex/services/job_runner.py:25`'teki üretici
      etiket hizasını dinamik hesaplıyor (`w = max(len(v) for v in L.values())`,
      "Anahtar Kelimeler" eklendiğinden beri w=17), ama
      `bibliometrics/services/parser.py` `parse_openalex_txt()` **sabit
      14 karakterlik** önek bekliyordu (`'Başlık       :'` gibi, ayrıca
      "Anahtar Kel." kısaltmasıyla) — üretici ile ayrıştırıcı birbirinden
      kopmuştu. Sonuç: gerçek bir OpenAlex TXT dosyası yeniden yüklenince
      TÜM kayıtlar sessizce "başlıksız" diye eleniyordu (0 kayıt çıkıyordu).
    - **Düzeltme:** sabit genişlik string eşleştirmesi yerine esnek
      boşluklu regex (`_val(label)` → `re.match(label + r'\s*:\s*(.*)$')`)
      — dil/etiket uzunluğu ne olursa olsun çalışır, bu hata sınıfını
      kalıcı olarak ortadan kaldırır. `parse_pubmed_txt`'e de AYNI düzeltme
      uygulandı (şu an Türkçe'de tesadüfen doğru çalışıyordu ama aynı
      kırılmaya karşı savunmasızdı — EN/DE'de etiket uzunluğu değişince
      kırılırdı, önleyici olarak düzeltildi).
    - **İkinci bulgu:** `parse_openalex_txt`'in anahtar kelime ayrıştırması
      da bozuktu — `_split_keywords()` `;`/`|` ile ayırıyor ama üretici
      `, ` ile birleştiriyor (bu TAM OLARAK `parse_pubmed_txt`'te zaten
      fark edilip düzeltilmiş olan aynı hataydı, kod yorumunda duruyordu
      ama openalex'e hiç uygulanmamıştı) — aynı düzeltme uygulandı.
    - Gerçek dosya + üretici→ayrıştırıcı uçtan uca testle (4 yeni pytest)
      doğrulandı, `forum+bibliometrics` 113/113 geçti.
    - **Hâlâ eksik (A7'nin orijinal kapsamı):** openalex.org web sitesinin
      kendi "Export → CSV" özelliğiyle indirilen gerçek CSV formatı hâlâ
      desteklenmiyor (`csv_auto`'ya düşüyor) — bunun için openalex.org'dan
      gerçekten indirilmiş bir CSV örneği hâlâ gerekiyor, bu TXT dosyası
      onun yerini tutmuyor.
  - [x] A8+A9 TAMAMLANDI (28 Ekim 2026):
    - **A8:** `bibliometrics/services/pdf_builder.py`'ye `_demo_cta_text()`
      eklendi — TR'de mevcut "sipariş oluşturunuz" metni korunuyor, EN/DE'de
      `reverse('proje_talebi')` ile dil önekli proje talebi linkine
      yönlendiriyor ("analizus.com/en/proje-talebi/" vb., sorgu parametreleri
      okunurluk için PDF düz metnine eklenmedi). `_fit_text` ile taşma
      koruması eklendi, kapak PNG'ye render edilip görsel doğrulandı.
    - **A9:** `promo_title` paylaşımlı "Bibliometrik Analiz" msgid'ini
      kullanıyordu (navbar/mobil menü/ana sayfa/onboarding'de de aynı
      çeviri) — doğrudan retranslate etmek o yerleri de bozardı. `pgettext('seo_title', ...)`
      ile bağlamlı çeviriye geçirildi (TR çıktısı aynı kalıyor, context-free
      kullanım yerleri etkilenmedi — ayrıca doğrulandı), EN/DE SEO'ya
      güçlendirildi ("Bibliometric Analysis from Scopus, WoS & OpenAlex
      Data – Automated Report").
    - **Yan bulgu (A8/A9 sırasında, demo sayısı 3→10 işinin devamı):**
      `bibliometrics/views.py`, `bibliometrics/templates/bibliometrics/landing.html`,
      `openalex/templates/openalex/landing.html` (2 yer) ve `pubmed/views.py`
      + `pubmed/templates/pubmed/landing.html`'de TOPLAM 6 yerde daha sabit
      "(3 grafik)" referansı bulundu (demo sayısı değişince stale kalmışlar).
      bibliometrics'teki 3 yer `SiteSettings.bibliometri_demo_grafik_sayisi`'nden
      dinamik okuyor artık (`{% blocktrans with n=... %}`); openalex/pubmed'deki
      3 yer basitçe "10" olarak güncellendi (bu ikisi bibliometri'nin
      SiteSettings'ine bağlı değil, ayrı app'ler — sabit metin olarak
      bırakıldı, ileride admin 10'u değiştirirse bu 3 yer elle güncellenmeli).
    - 2 yeni pytest (`_demo_cta_text` tr/en/de), `forum+bibliometrics`
      113/113 geçti. EN/DE çevirileri eklendi, `compilemessages` hatasız.
  - [x] A4 TAMAMLANDI (28 Ekim 2026, kullanıcı kararı: ayrı alan/migration
    ile). `BibliometricJob.report_language` eklendi (boş = arayüz dili ile
    aynı — mevcut davranış korunur; tr/en/de seçilebilir, migration `0006`).
    Kapsam yalnız dosya yükleme formu (`BibliometricUploadForm` + `landing.html`
    — `{{ form.report_language }}`, JS'e dokunulmadı, `FormData(form)` zaten
    alıyor); OpenAlex/PubMed köprüsünden gelen job'lar bu formu kullanmadığı
    için etkilenmedi, arayüz diliyle devam ediyor (A4'ün orijinal kapsamı).
    `job_runner.py` `_in_user_language()`: `report_language` doluysa
    `translation.override()` ile zorlanıyor (PDF+e-posta dahil TÜM iş o
    dilde), boşsa eski davranış (profil dili). `tezanaliz/admin.py`'deki
    `BibliometricJobProxyAdmin`'e `report_language` list_display/list_filter
    olarak eklendi. Canlı test: register→email doğrula→bibliometri sayfası
    → form alanı 4 seçenekle (Aynı/TR/EN/DE) doğru render oluyor (ekran
    görüntüsü yerine HTML'den doğrulandı). 2 yeni pytest (`report_language`
    doluyken zorluyor, boşken profil diline düşüyor), `forum+bibliometrics`
    117/117 geçti. EN/DE çevirileri (`Rapor Dili`/`Arayüz dili ile aynı`)
    eklendi. **Grup A TAMAMEN BİTTİ.**
  - [ ] Grup B (bibliometrix/VOSviewer kalitesinde yol haritası — veri kalitesi,
    bilim haritalama, çıktılar, ürün/huni) — **kullanıcı kararı (28 Ekim 2026):
    ERTELENDİ, yarına/sonraki oturuma bırakıldı.** Özet sunuldu (B1 veri
    kalitesi → B2 bilim haritalama (en karmaşık: tematik harita, ortak atıf
    ağları, konu modelleme) → B3 çıktılar (VOSviewer export, hazır yöntem
    metni, PRISMA) → B4 ürün/huni). Ayrı planlama turu gerekiyor.
  - [ ] **A7 tamamlanmamış kısım — gerçek openalex.org web CSV'si elde edildi
    (28 Ekim 2026), henüz parser desteği yazılmadı.** Kullanıcı gerçek bir
    "Export CSV" dosyası verdi (`works-2026-10-28T22-05-18.csv`, ~150 kayıt).
    Analiz edildi: sütunlar `Title,Author,Year,Citation count,Open access,
    Abstract` — yazar `|` ile ayrılmış (bazı kayıtlarda tutarsız, virgülle).
    **Kritik eksiklik:** bu formatta dergi/DOI/kurum/ülke/anahtar kelime/
    yayın türü HİÇ YOK — openalex.org'un web export'u yalnız bu 6 sütunu
    veriyor. Yani bu formatla top_journals/top_institutions/country_
    collaboration/keyword_cooccurrence/keyword_trend/publication_types
    analizleri hep `skipped` düşecek; yalnız keyword_cloud (abstract
    metninden) ve atıf/yazar/yıl bazlı analizler çalışır. DOI olmadığı için
    tekilleştirme başlığa düşüyor (zaten desteklenen yol). Dosyada gerçek
    tekrar eden kayıtlar da var (iyi test senaryosu). Plan: `detect_format`'a
    yeni dal (`'citation count' in lower and 'open access' in lower` gibi
    ayırt edici imza) + yeni `_parse_openalex_csv()` fonksiyonu (csv.DictReader,
    scopus parser'ın pattern'i). Kullanıcıya bu kısıtlama bildirilecek,
    onay sonrası uygulanacak.

- [ ] **(27 Ekim 2026) GSC "Page indexing → Not found (404)" raporu — kök
  neden bulundu, henüz düzeltilmedi.** Kullanıcı Search Console'da iki URL
  kalıbı gördü: `/hizmetler/<slug>/` (EN/DE, ör. `nitel-analiz`,
  `akademik-danismanlik`) ve `/en/market/job/<id>/`. Araştırma: ikisi de
  view seviyesinde HAKLI olarak 404 dönüyor (`nitel-analiz`/`akademik-
  danismanlik`'in `ServicePageTranslation` kaydı yok — yalnız `nicel-analiz`
  pilot çevrildi, migration `0182`; `feature_market_intl` varsayılanı
  `False` olduğu için EN/DE ilan sayfaları tamamen kapalı). Asıl sorun:
  `forum/context_processors.py:115-141` `hreflang_alternates`, hedefte
  çeviri/flag uygunluğu kontrol etmeden `translate_url()` ile körü körüne
  tr/en/de `<link rel="alternate" hreflang>` üretiyor (`templates/
  base.html:273-276`) — Google bu sahte linkleri takip edip var olmayan
  sayfaları crawl ediyor. Sitemap tarafı doğru filtrelenmiş, sorun kaynağı
  değil. **Öneri (uygulanmadı):** `hreflang_alternates`'e sayfa bazlı "hedef
  gerçekten var mı" kontrolü eklenmeli. Kullanıcı onayı bekliyor.

- [x] **(27 Ekim 2026 TAMAMLANDI) Ana sayfa/eğitim/urls.py'deki sabit araç
  sayısı genel ifadeye çevrildi, main'de canlı.** Yukarıdaki GSC araştırması
  sırasında `home.html`/`home_intl.html` hero bölümünde bulunan sabit "18
  aracın tümü →" ifadesi (önceki oturumdan uncommitted) zaten genel "Analiz
  araçlarının tümü →" ifadesine çevrilmişti; bu oturumda aynı mantıkla
  `egitim.html`'deki ("Eğitmen/Ekip" + "Neden Analizus" bölümleri, 2 yer) ve
  `urls.py:47` yorumundaki sabit "24 istatistik aracı" ifadeleri de
  "istatistik araçları" olarak genelleştirildi (gerçek sayı şu an 25,
  `istatistik/views.py` `TOOL_CATEGORIES`). EN/DE çevirileri eklendi
  (`makemessages --no-wrap` yanlışlıkla tüm dosyayı yeniden sardı, fark
  edilip `git checkout` ile geri alınıp doğru şekilde elle düzeltildi —
  ders: `--no-wrap`/`--no-location` bayraklarına dikkat). `dev`→`main`
  `--no-ff` merge + push edildi, GitHub Actions otomatik Hetzner deploy'u
  tetikledi; merge öncesi production online-kullanıcı kontrolünde `fijital`
  (muhtemelen kullanıcının kendi hesabı) aktif görüldü, kullanıcı onayıyla
  devam edildi. Canlıda doğrulandı (`/egitim/` 200, hero "Analiz araçlarının
  tümü →" gösteriyor). **Yan not:** lokal Docker ortamında `/egitim/`
  TR/EN/DE üçünde de 404 görünmüştü — kod bug'ı değil, `forum/views.py:2438`
  `@feature_required('training')` decorator'ının lokal `SiteSettings`
  kaydında kapalı olması (production'da açık); yanlışlıkla "pre-existing
  bug" diye raporlanmıştı, sonradan düzeltildi. **Ayrıca düzeltildi:** aynı
  taramada `svm`/`mediation`/`moderation` job_queue whitelist düzeltmesinin
  (bkz. aşağıdaki 26 Ekim maddesi) "henüz merge edilmedi" notu bayat
  çıktı — `git show origin/main:analizdestek/job_queue.py` ile zaten
  production'da olduğu doğrulanıp not güncellendi.

- [ ] **(25 Ekim 2026) EN/DE Ödeme Sistemleri Altında Adres Değişikliği** —
  kullanıcı talebi: EN ve DE sayfalarında ödeme sistemleri bölümünde yer alan
  adres güncellenmeli. Detay/hangi adres henüz belirtilmedi — sonraki
  oturumda kullanıcıdan netleştirilecek, sonra uygulanacak.

- [x] **(26 Ekim 2026 TAMAMLANDI, KRİTİK — Kümeleme aracı geliştirmesi
  sırasında bulundu) `svm`, `mediation`, `moderation` araçlarının arka plan
  işi hiç çalışmıyormuş.** `analizdestek/job_queue.py:147`'deki async iş
  kuyruğu dispatch whitelist'i yalnız `('cronbach', 'normallik', 'betimsel',
  'korelasyon', 'ttesti', 'anova', 'mann_whitney', 'kruskal_wallis',
  'ki_kare', 'lineer_regresyon', 'lojistik_regresyon', 'afa', 'wilcoxon',
  'friedman', 'tekrarli_anova', 'karar_agaci')` içeriyordu — **svm,
  mediation, moderation eksikti**. Bu üç aracın "Analizi Başlat" butonuna
  basan kullanıcı job'ı oluşturuyor ama `[job_queue] Bilinmeyen job_type`
  log'uyla iş hiç işlenmiyordu, kullanıcı sonsuza kadar "yükleniyor"
  ekranında kalıyordu (moderation 26 Ekim, mediation 26 Ekim, svm 15
  Ekim'de main'e alınmıştı; GET ile sayfa 200 dönmesi deploy'u doğrulamış
  ama POST→analiz akışı hiç test edilmemiş görünüyordu). **Düzeltme:**
  whitelist tuple'ına `svm`, `mediation`, `moderation` (ve `kumeleme`)
  eklendi. Docker'da gerçek async kuyruk (mock yok, `transaction.atomic()`
  DIŞINDA — worker thread'in commit edilmiş veriyi görmesi gerekiyor)
  üzerinden moderation job'ı oluşturulup `run_job()` çağrıldı, ~1sn içinde
  `status='completed'` + gerçek `pdf_url` ile tamamlandığı doğrulandı (daha
  önce sonsuza `pending` kalırdı); test job'ı silindi. 104/104 pytest yeşil,
  `docker compose restart web` yapıldı. **Güncelleme (27 Ekim 2026):** bu
  düzeltme (commit `930263f`) sonraki `dev`→`main` merge'lerine (MANOVA/
  Sağkalım/ROC/Path Analizi turları) dahil olarak zaten production'a ulaşmış
  — `git show origin/main:analizdestek/job_queue.py` ile doğrulandı, ayrı bir
  merge beklemiyor.

- [x] **(25 Ekim 2026 TAMAMLANDI) S3 Dosya Saklama Süresi — Kullanıcı Bildirimi Eksik
  (S3 cron denetimi sırasında bulundu, bkz. sohbet). 9/10 araçta kullanıcı
  dosyasının ne zaman silineceğini hiç bilmiyor, 3 aracın e-postası yanlış
  süre söylüyor, gizlilik politikası 4 aracı hiç kapsamıyor. Ayrı onay
  gereken 3 iş (KIRMIZI ÇİZGİ ilkesi — tek tek uygulanacak):**
  1. [x] **(25 Ekim 2026 düzeltildi) Metin hatası düzeltmesi:**
     `bibliometrics/services/job_runner.py:366,424`, `makaleanaliz/services/
     job_runner.py:166`, `tezanaliz/services/job_runner.py:175` e-postalarındaki
     "indirme linki 3 gün geçerlidir" metni "7 gün" olarak düzeltildi (kod
     gerçekte `cleanup_expired_*_s3_files(days=7)` ile 7 gün saklıyor).
     bibliometrics/makaleanaliz `gettext()` ile sarılıydı — EN/DE `locale/*/
     LC_MESSAGES/django.po` msgid+msgstr güncellendi, `compilemessages`
     hatasız derlendi (`docker compose exec web`). tezanaliz dosyasında bu
     e-posta hiç `gettext` kullanmıyor (dosyada başka hiçbir yerde de yok) —
     bu maddenin kapsamı dışında bırakıldı, yalnız sayı düzeltildi.
  2. [x] **(25 Ekim 2026 düzeltildi) Eksik UI/e-posta uyarısı.** Ortak
     `templates/partials/_s3_retention_notice.html` (ax-alert--info, `{%
     blocktrans %}` ile "7 gün" metni) oluşturuldu; 9 ana araç (trdizin,
     openalex, oaipmh, pubmed, semanticscholar, bibliometrics — 2 yer,
     makaleanaliz, tezanaliz — 2 yer) sonuç/indirme paneline eklendi.
     istatistik'in 17 aracına (afa, anova, betimsel, cronbach, friedman,
     karar_agaci, ki_kare, korelasyon, kruskal_wallis, lineer_regresyon,
     lojistik_regresyon, mann_whitney, normallik, svm, tekrarli_anova,
     ttesti, wilcoxon) PDF panelinin yanına aynı include eklendi —
     `analiz_console_base.html` ortak bir sonuç paneli tanımlamadığı için
     (her araç kendi şablonunda ayrı panel) tek tek yapıldı; flex buton
     satırının (`d-flex gap-2 flex-wrap`) İÇİNE değil hemen dışına
     yerleştirilmesine dikkat edildi (ilk denemede pubmed.html'de bu hata
     yapılıp fark edilip düzeltildi). `orneklem.html` (S3 kullanmıyor, salt
     hesap makinesi), `analiz_hub.html`, `analiz_console_base.html` kapsam
     dışı bırakıldı. E-posta tarafında trdizin/oaipmh/openalex/
     semanticscholar'ın sipariş/sonuç e-postalarına "Not: İndirme linki/
     bağlantısı 7 gün geçerlidir." eklendi (openalex/semanticscholar zaten
     `gettext` kullanıyordu, mevcut msgid'i tekrar kullandı; trdizin/oaipmh
     hiç i18n kullanmıyordu — kapsam dışı, madde 1'deki tezanaliz
     emsaliyle tutarlı düz metin bırakıldı); pubmed'de dosya e-postayla
     gitmiyor, ek yapılmadı (yalnız "proje talebi" linki var).
     `makemessages` ile yeni msgid toplanıp EN/DE çevirileri girildi,
     `compilemessages` hatasız derlendi. **Dikkat (ders):** ilk
     `makemessages` denemesinde yanlışlıkla `--no-location` kullanılıp
     ardından `git checkout` ile geri alınırken madde 1'in .po
     düzeltmeleri de kazayla silinmiş, hemen fark edilip yeniden
     uygulandı. Tüm 17+9 şablon `get_template()` ile sözdizimi
     doğrulandı, 104/104 pytest yeşil, `docker compose restart web`
     yapıldı.
  3. [x] **(25 Ekim 2026 düzeltildi) Gizlilik politikası güncellemesi.**
     `forum/templates/forum/gizlilik_politikasi.html` §4 "Veri Saklama
     Süreleri" (satır 93) ve §7 GDPR madde listesindeki "Saklama süreleri"
     bendine (satır 135) bibliometrics/makaleanaliz/tezanaliz/istatistik
     eklendi. **Ek bulgu:** aynı cümlede Semantic Scholar da hiç
     geçmiyormuş — todo'nun "zaten kapsanıyor" notu yanlıştı, o da aynı
     düzeltmeyle eklendi. Yeni liste: OpenAlex, TR Dizin, OAI-PMH, PubMed,
     Semantic Scholar, Bibliometrik Analiz, Makale Analizi, Tez Analizi,
     İstatistik Araçları → 7 gün; YÖK Tez → 3 gün (değişmedi). EN/DE
     çevirileri güncellendi (`makemessages` ile fuzzy eşleşme çıktı,
     elle düzeltilip fuzzy işareti kaldırıldı), `compilemessages` hatasız
     derlendi, "Son güncelleme" tarihi 25.10.2026 yapıldı. Şablon
     `get_template()` ile doğrulandı, 104/104 pytest yeşil, `docker
     compose restart web` yapıldı.

**→ S3 Dosya Saklama Süresi görevinin 3 maddesi de tamamlandı.**

- [ ] **(25 Ekim 2026) Çalışma Odaları — Kötüye Kullanım Tespiti + KVKK Uyumu
  (kullanıcı talebi: kötü niyetli yazışmaların tespiti, adli makamlara
  verilebilmesi; "admin görünmeden girsin mi" soruldu → KARAR: hayır, ayrıntı
  için bkz. sohbet notu). Henüz başlanmadı, faz faz (her faz önce onay bekler,
  KIRMIZI ÇİZGİ ilkesi):**
  1. [x] **(25 Ekim 2026 TAMAMLANDI) Faz 1 — Otomatik işaretleme (flagged):**
     `StudyRoomPost.flagged` alanı eklendi (`forum/models.py`,
     migration `0186_studyroompost_flagged`) — gerçek desen `FreelanceJob`'da
     değil `ReferralUse.flagged`'da bulundu, aynı mantık uygulandı. Telefon,
     e-posta, WhatsApp/Telegram/Instagram/Signal geçen metin, IBAN, kripto
     cüzdan adresi (0x.../bc1...) ve kısa bir tehdit-kelime listesi regex ile
     `save()` içinde taranıyor; `_studyroom_post_abuse_signal()` yardımcı
     fonksiyonu. **Dikkat (ders):** mesaj düzenleme view'ı (`api_edit_room_post`)
     `save(update_fields=['message','edited_at'])` kullanıyor — `flagged`
     update_fields listesine dahil edilmezse DB'ye yazılmaz; `save()` override
     bunu otomatik `update_fields`'e ekliyor. `forum/admin.py`'ye
     `StudyRoomPostAdmin` (list_filter=flagged) eklendi, Unfold sidebar'a
     "Oda Mesajları (İşaretli)" girdisi eklendi (üç yerde birlikte kuralı).
     Canlı engelleme yok, yalnız sonradan admin filtresi. Docker'da
     transaction.atomic()+rollback ile telefon/whatsapp/IBAN/tehdit kelimesi/
     normal mesaj senaryoları ve update_fields ile düzenleme testi yapıldı,
     104/104 pytest yeşil, `manage.py check` temiz, `docker compose restart web`
     yapıldı.
  2. [x] **(26 Ekim 2026 düzeltildi) Faz 2 — Kullanıcı "bildir" özelliği.**
     `StudyRoomPostReport` modeli (post, reporter, reason — önceden tanımlı
     5 seçenek: Taciz/Hakaret, Spam/Reklam, Platform Dışına Yönlendirme,
     Uygunsuz İçerik, Diğer — kullanıcı kararı: `unique_together` YOK, aynı
     mesaj tekrar tekrar bildirilebilir), migration `0187_studyroompostreport`.
     `studyroom_detail.html`'de başkasının mesajına (`rm-karsi`) hover'da
     görünen "Bildir" butonu + sebep seçim paneli (mevcut `rm-edit-area`
     deseniyle tutarlı inline panel), hem server-render hem polling ile
     eklenen (`appendRoomPost`) mesajlarda çalışıyor. `api_report_room_post`
     view'ı: giriş+POST zorunlu, geçersiz sebep ve kendi mesajını bildirme
     reddediliyor. Admin: `StudyRoomPostReportAdmin` (reason filtresi) +
     sidebar'a "Oda Bildirimleri" girdisi. **Not:** `forum/urls.py`
     `i18n_patterns` DIŞINDA (çalışma odaları TR-only kapsam) — bu yüzden
     şablonda `{% trans %}` kullanılmadı, dosyadaki mevcut (çevrilmemiş)
     Türkçe metin deseniyle tutarlı bırakıldı, EN/DE çeviri adımı atlandı.
     Docker'da: iki farklı kullanıcıyla rapor/tekrar-rapor/geçersiz-sebep/
     kendi-mesajını-bildirme senaryoları `Client` ile uçtan uca test edildi,
     104/104 pytest yeşil, `docker compose restart web` + `restart nginx`
     yapıldı.
  3. [x] **(26 Ekim 2026 TAMAMLANDI) Faz 3 — Saklama süresi + "legal hold".**
     Kullanıcı kararları: N=6 ay (180 gün), kapsam yalnız mesajlar (oda kaydı
     kalır), tetikleme günlük cron/management komut deseni (mevcut
     `CRON_SECRET_KEY` korumalı `/api/cron/...` deseni). `StudyRoom.archived_at`
     eklendi (migration `0188_studyroom_archived_at`), `auto_archive_if_expired()`
     bu alanı da set ediyor. Yeni `cron_cleanup_archived_room_posts`
     (`forum/api_views.py`, route `/api/cron/cleanup-archived-room-posts/`):
     `archived_at` 180 günden eski odalardaki mesajları siler (önce varsa ekli
     dosya S3'ten temizlenir); `flagged=True` veya en az bir
     `StudyRoomPostReport`'u olan mesajlar muaf (legal hold). **Not:** bu yeni
     URL'in dış cron servisine (cron-job.org vb., diğer `/api/cron/...`
     uçlarıyla aynı yerde) eklenmesi kullanıcının kendisi tarafından
     yapılmalı — kod yalnız endpoint'i oluşturur, dış tetikleyiciye erişimim
     yok. Docker'da `transaction.atomic()+rollback` ile 5 senaryo
     (eski/temiz mesaj silindi; flagged/bildirilen/180 günden yeni
     arşiv/aktif oda mesajları korundu; yanlış secret 403) doğrulandı,
     104/104 pytest yeşil, `docker compose restart web` yapıldı.
  4. [x] **(26 Ekim 2026 TAMAMLANDI) Faz 4 — Adli makam talebi / export audit
     log.** Kullanıcı kararları: format PDF, kapsam seçilen odanın TÜM
     mesajları, yetki yalnızca superuser. `RoomExportAuditLog` modeli
     (room, exported_by, exported_at, message_count — migration
     `0189_roomexportauditlog`, admin'de değiştirilemez/silinemez salt
     okunur). `forum/services/room_export.py` — ReportLab/Platypus ile PDF
     (oda başlığı, dışa aktaran admin + zaman PDF üzerinde de yazılı, tüm
     mesajlar tarih/yazar/içerik tablosu; `istatistik.services.pdf_fonts.
     register_fonts()` ile Türkçe karakter desteği; mesaj içeriği
     `xml.sax.saxutils.escape()` ile kaçışlı — bibliometrics/pdf_builder.py
     ile aynı desen). `StudyRoomAdmin.export_room_messages` aksiyonu
     (`TrainingRequestAdmin.generate_certificate` deseniyle aynı): staff
     ama superuser olmayan reddedilir, birden fazla oda seçilirse reddedilir,
     başarılı olursa PDF indirilir + audit log kaydı oluşur. Sidebar'a
     "Oda Export Kayıtları" girdisi. Docker'da: staff/superuser/çoklu-seçim
     senaryoları + üretilen PDF'in boyutu ve özel karakter (`<b>`, `&`)
     içeren mesajın bozmadığı `transaction.atomic()+rollback` ile doğrulandı,
     104/104 pytest yeşil, `docker compose restart web` yapıldı.
     **Ek bulgu (26 Ekim 2026, merge sonrası production kontrolünde):**
     Faz 3 deploy edildiğinde production'da zaten `archived` durumda olan
     8 oda `archived_at=NULL` kaldığı için retention cron'una hiç girmiyordu.
     Kullanıcı kararı: backfill yapılsın — migration
     `0190_backfill_studyroom_archived_at` ile bu odalara `ends_at` proxy
     olarak `archived_at`'a yazıldı (`RunPython`, `models.F('ends_at')`).
     Docker'da izole bir senaryo (`transaction.atomic()+rollback`) ile
     backfill mantığı doğrulandı, 104/104 pytest yeşil, `docker compose
     restart web` yapıldı. Henüz yalnız `dev`'de, production'a migration
     deploy ile gidecek.
  - [x] **(26 Ekim 2026 TAMAMLANDI) Admin sidebar grupla.** 4 ayrı sidebar
    girdisi (Çalışma Odaları, Oda Mesajları (İşaretli), Oda Bildirimleri,
    Oda Export Kayıtları) kullanıcı isteğiyle tek "Çalışma Odaları" girdisine
    indirildi — mevcut `GroupTabsMixin` deseni (`analizdestek/admin_nav.py`,
    16 Ekim'de Arama & Analiz Servisleri için kurulmuştu) `STUDYROOM_TABS`
    ile tekrar kullanıldı; 4 admin sınıfına (`StudyRoomAdmin`,
    `StudyRoomPostAdmin`, `StudyRoomPostReportAdmin`,
    `RoomExportAuditLogAdmin`) mixin eklendi, her sayfanın üstünde sekme
    çubuğuyla geçiş yapılıyor. Docker'da 4 sayfanın da 200 döndüğü ve sekme
    çubuğunun göründüğü doğrulandı, 104/104 pytest yeşil, `docker compose
    restart web` yapıldı.

  5. [ ] **Faz 5 — Aydınlatma metni güncellemesi (BEKLEMEDE — avukat/KVKK
     danışmanı onayı gerekiyor, Claude tek başına yazıp yayınlayamaz).**
     Gizlilik Politikası/Kullanım Şartları'na "mesajlarınız kötüye
     kullanımın önlenmesi ve yasal yükümlülükler çerçevesinde saklanır,
     gerektiğinde yetkili makamlarla paylaşılabilir" açıklaması eklenir.
     Kullanıcı onaylı metni getirdiğinde uygulanacak.
  6. [ ] **Faz 6 — Admin erişim logu (26 Ekim 2026, plan onaylanmadan
     ertelendi — kullanıcı "geç" dedi).** Plan taslağı: `RoomAccessAuditLog`
     modeli (room, viewed_by, viewed_at) + `StudyRoomPostAdmin.
     changelist_view()` override edilip `room__id__exact` filtresiyle
     görüntülemede otomatik log. Bir admin bir odanın mesaj dökümünü
     panelden görüntülediğinde bunun loglanması (kim, hangi oda, ne zaman) —
     "görünmeden girme" yerine şeffaf ama izlenebilir erişim hedefi.
  - **Reddedilen fikir:** Admin'in canlı odaya görünmeden/stealth presence
    ile girmesi — gereksiz (mesajlar zaten DB'de, admin paneli yeterli) ve
    KVKK şeffaflık ilkesi + kullanıcı güveni açısından riskli; uygulanmayacak.

- [ ] **(25 Ekim 2026) Yeni Ücretsiz İstatistik Araçları Fikirleri — öncelik
  sırasıyla:**
  1. [x] **(26 Ekim 2026 TAMAMLANDI) Aracılık/Düzenleyici Değişken Analizi
     (Mediation/Moderation)** — SPSS Process/Hayes'e karşılık; TR sosyal
     bilimler/işletme tezlerinde en çok talep edilen, bizde hiç karşılığı
     yoktu. **Kullanıcı kararıyla v1 kapsamı yalnız basit (tek aracı
     değişkenli) Mediation** — Moderation ayrı, sonraki bir tur (KIRMIZI
     ÇİZGİ "tek seferde tek görev" ilkesi). Yeni `istatistik/services/
     mediation.py`: üç statsmodels OLS modeli (c: Y~X toplam etki, a: M~X,
     b+c': Y~X+M direkt etki), dolaylı etki (a×b) **bootstrap %95 GA**
     (5000 yeniden örnekleme, kullanıcı kararı — Hayes/Process ile eşleşir)
     + **Sobel testi** (ek/klasik) ile raporlanıyor; tam/kısmi/aracılık yok
     sınıflandırması c' anlamlılığına göre otomatik. Mevcut 18 araçla
     birebir aynı iskelet: `TOOL_CHOICES` + migration `0012_add_mediation_
     tool`, `job_runner.py` dispatch dalı, `views.py` (`TOOL_CATEGORIES`
     "Regresyon Analizleri" grubuna 3. satır, `mediation_landing` view,
     `_handle_group_tool_post`/`_SLUG_MAP` genişletmesi), `urls.py`,
     yeni `istatistik/templates/istatistik/mediation.html` (lineer_regresyon.
     html'in X/M/Y üç değişkenli uyarlaması, `_s3_retention_notice.html`
     dahil), `seo_content.py` (intro/when_to_use/assumptions/
     how_to_interpret/apa_example/2 faq/related_tools), `forum/sitemaps.py`
     `IstatistikSitemap`. 75 yeni msgid EN/DE'ye çevrildi (`makemessages`
     ilk denemede bazı stringleri eski alakasız çevirilerle fuzzy eşleşti —
     tek tek doğru çeviriyle düzeltilip fuzzy bayrağı temizlendi, ayrıca
     `{% trans %}` içindeki "%95" kendiliğinden "%%95"e kaçtığı için o
     girdi ayrı düzeltildi), `compilemessages` hatasız derlendi. Docker'da:
     tam/kısmi/aracılık-yok/kategorik-X/yetersiz-n/sayısal-olmayan-M
     senaryoları `analyze()`+`build_pdf()` ile, tam job pipeline'ı
     `transaction.atomic()+rollback` ile (`_upload_pdf` mock'lanarak
     gerçek S3'e yazılmadan — CLAUDE.md'deki "lokal/prod aynı S3 bucket"
     uyarısı gereği) doğrulandı; TR/EN/DE üç dilde hem anonim (promo) hem
     girişli (konsol) sayfa render edildi, sitemap üç dilde de URL'i
     içeriyor, 104/104 pytest yeşil, `docker compose restart web` + nginx
     yapıldı. Kullanıcı onayıyla (yedek alındı) `dev`→`main` merge + push
     edildi, GitHub Actions otomatik Hetzner deploy'u tetikledi, migration
     production'da uygulandı, canlı doğrulandı (`https://www.analizus.com/
     analiz/mediation/` 200).
  1b. [x] **(26 Ekim 2026 TAMAMLANDI) Moderation (Düzenleyici Değişken
     Analizi) — mediation'ın ikinci yarısı, ayrı tur.** Yeni `istatistik/
     services/moderation.py`: Y~Xc+Wc+Xc*Wc modeli (statsmodels OLS,
     Aiken & West 1991 merkezleme standardı), etkileşim katsayısı **b3**'ün
     p değeri düzenleme etkisinin anlamlılığını belirliyor, **ΔR²**
     (etkileşim teriminin ek açıklayıcılığı) raporlanıyor, **basit eğimler
     (simple slopes)** W'nin düşük/orta/yüksek (sürekliyse Ort.±1SS, 2
     kategoriliyse W=0/W=1) düzeylerinde X'in koşullu etkisini (model
     `cov_params()`'tan SE/t/p ile) gösteriyor — Hayes/Process Model 1'in
     temel yorumlama katmanı. Ek olarak matplotlib ile **etkileşim grafiği**
     (X-Y ilişkisi W düzeylerine göre, base64 PNG — AFA'daki scree plot
     deseniyle aynı, `job_runner.py` `_AI_PROMPT_EXCLUDE_KEYS`'e
     `interaction_plot_b64` eklendi). Mediation ile birebir aynı iskelet:
     `TOOL_CHOICES` + migration `0013_add_moderation_tool`, `job_runner.py`
     dispatch dalı, `views.py` (`TOOL_CATEGORIES` 4. satır, `moderation_
     landing` view, `_handle_group_tool_post`/`_SLUG_MAP`), `urls.py`, yeni
     `istatistik/templates/istatistik/moderation.html` (X/W/Y üç değişkenli,
     etkileşim grafiği `<img>` + basit eğimler tablosu), `seo_content.py`
     (moderation girdisi + mediation'ın `related_tools`'una çapraz link
     eklendi), `forum/sitemaps.py`. 64 yeni msgid EN/DE'ye çevrildi (yine
     bazı stringler fuzzy eşleşti, tek tek düzeltilip bayrak temizlendi),
     `compilemessages` hatasız derlendi. Docker'da: anlamlı/anlamsız
     etkileşim, kategorik W (dummy), sürekli W (basit eğimler), yetersiz n,
     sayısal olmayan X senaryoları `analyze()`+`build_pdf()` ile (gerçek PNG
     üretimi dahil), tam job pipeline `_upload_pdf` mock'lanarak
     `transaction.atomic()+rollback` ile doğrulandı; TR/EN/DE üç dilde
     anonim+girişli sayfa render edildi, sitemap üç dilde URL'i içeriyor,
     104/104 pytest yeşil, `docker compose restart web` + nginx yapıldı.
     Kullanıcı onayıyla `dev`→`main` merge + push edildi, GitHub Actions
     otomatik Hetzner deploy'u tetikledi, migration production'da
     uygulandı, canlı doğrulandı (`https://www.analizus.com/analiz/
     moderation/` 200). `dev` de origin'e push edildi (Render staging).
  2. [x] **(26 Ekim 2026 TAMAMLANDI) Kümeleme Analizi (K-means / Hiyerarşik
     Cluster)** — kullanıcı kararıyla tek araç, "Yöntem" dropdown'u
     (K-means / Hiyerarşik-Ward); küme sayısı (k) boş bırakılırsa k=2..10
     arası silhouette skoruna göre otomatik seçilir (en iyi k), kullanıcı
     elle de girebilir. Yeni `istatistik/services/kumeleme.py`: seçilen
     sayısal değişkenler `StandardScaler` ile ölçekleniyor (n>3000 satırda
     3000'e örnekleniyor — hiyerarşik yöntemin O(n²) bellek sınırı için);
     K-means `sklearn.cluster.KMeans` + `inertia_`, Hiyerarşik
     `scipy.cluster.hierarchy.linkage(method='ward')` tek sefer hesaplanıp
     her k adayı için `fcluster` ile kesiliyor (performans — her k'de ağacı
     yeniden kurmuyor). Silhouette skoru Kaufman & Rousseeuw (1990)
     eşikleriyle yorumlanıyor; diyagnostik grafik K-means'te elbow(WCSS)+
     silhouette çift eksen, Hiyerarşik'te dendrogram; dağılım grafiği 2
     değişkende direkt, fazlasında PCA ile 2B. Mevcut 20 araçla birebir aynı
     iskelet: `TOOL_CHOICES` + migration `0014_add_kumeleme_tool`,
     `job_runner.py` dispatch dalı, `views.py` ("Makine Öğrenmesi" grubuna
     3. satır, `kumeleme_landing`, `_handle_group_tool_post` options dalı,
     `_SLUG_MAP`), `urls.py`, yeni `istatistik/templates/istatistik/
     kumeleme.html` (afa.html'in ax- tasarım sistemi deseniyle — moderation/
     mediation'ın henüz ax-'e taşınmamış eski Bootstrap kartları DEĞİL,
     CLAUDE.md "ax- sistemi" kuralı gereği), `seo_content.py`, `forum/
     sitemaps.py`. **Ek bulgu (kapsam içi, düzeltildi):** `analizdestek/
     job_queue.py`'deki async iş kuyruğu dispatch whitelist'inde (satır 147)
     `svm`, `mediation`, `moderation` hiç yoktu — yani bu üç canlı aracın
     arka plan işi hiçbir zaman çalışmıyor, kullanıcı sonsuza kadar
     "yükleniyor" ekranında kalıyor olmalı (uçtan uca test sırasında
     `[job_queue] Bilinmeyen job_type` logu ile bulundu). `kumeleme`
     whitelist'e eklendi (kendi kapsamım için zorunlu); **svm/mediation/
     moderation'ın eksikliği kullanıcıya ayrıca bildirildi, kullanıcı onayı
     ile aynı oturumda ayrı adım olarak düzeltildi (bkz. birkaç madde
     yukarıdaki kritik bulgu kaydı).**
     75 yeni msgid EN/DE'ye çevrildi (bazıları yine fuzzy yanlış eşleşti —
     örn. "Dendrogram"→"Program", tek tek düzeltilip `previous_msgid` alanı
     polib ile temizlendi), `compilemessages` hatasız derlendi. Docker'da:
     `analyze()` doğrudan (kmeans/hierarchical × otomatik/elle k × 2 ve 3+
     değişken × büyük n örnekleme × geçersiz girdi senaryoları) ve tam uçtan
     uca akış (preview→run→job kuyruğu→analiz→PDF, `transaction.atomic()+
     rollback` ile, `_upload_pdf`/`upload_bytes_to_s3` mock'lanarak) test
     edildi; TR/EN/DE anonim (promo) sayfa 200, sitemap üç dilde URL'i
     içeriyor, 104/104 pytest yeşil, `docker compose restart web` + nginx
     yapıldı. Kullanıcı onayıyla `dev`→`main` merge + push edildi, GitHub
     Actions otomatik Hetzner deploy'u tetikledi (24 sn), migration
     production'da uygulandı, canlı doğrulandı (`https://www.analizus.com/
     analiz/kumeleme/` TR/EN/DE 200). Aynı deploy'la svm/mediation/moderation
     job_queue düzeltmesi de canlıya alındı.
  3. [x] **(26 Ekim 2026 TAMAMLANDI) MANOVA (Çok Değişkenli Varyans Analizi)**
     — kullanıcı kararıyla: (1) MANOVA anlamlıysa Bonferroni düzeltmeli
     (α/değişken sayısı) takip ANOVA'ları eklendi, (2) Box's M testi
     (kovaryans matrisi homojenliği) eklendi. Yeni `istatistik/services/
     manova.py`: `statsmodels.multivariate.manova.MANOVA` ile SPSS'in
     "Multivariate Tests" tablosuyla birebir aynı dört istatistik (Wilks'
     Lambda, Pillai's Trace, Hotelling-Lawley Trace, Roy's Largest Root);
     birincil anlamlılık Wilks' Lambda'ya göre, kısmi η² Cohen'in 1 − Λ^(1/s)
     yaklaşımıyla hesaplanıyor. Box's M testi elle implemente edildi (Box,
     1949 — pooled/grup kovaryans matrisleri, log-determinant, ki-kare
     yaklaşımı; tekil/singular matriste `None` dönüp PDF'te "hesaplanamadı"
     notu gösteriyor). MANOVA anlamlıysa her bağımlı değişken için mevcut
     `anova.py`'nin `analyze()` fonksiyonu yeniden kullanılarak (Welch/Levene/
     eta-kare/post-hoc dahil) takip ANOVA'ları + α/m düzeltmeli anlamlılık
     eşiği hesaplanıyor. Profil grafiği (grup ortalamaları × bağımlı
     değişkenler, SPSS MANOVA raporlamasındaki standart görsel) matplotlib
     ile üretiliyor. Mevcut 21 araçla aynı iskelet: `TOOL_CHOICES` + migration
     `0015_add_manova_tool`, `job_runner.py` dispatch dalı +
     `_AI_PROMPT_EXCLUDE_KEYS`, `views.py` ("Fark Analizleri" grubuna 7.
     satır, `manova_landing`, `_handle_group_tool_post` options dalı,
     `_SLUG_MAP`), `urls.py`, `job_queue.py` whitelist, yeni `istatistik/
     templates/istatistik/manova.html` (kumeleme.html'in ax- deseniyle; grup
     değişkeni dropdown + bağımlı değişkenler checkbox-listesi — anova.html'in
     grup+tek bağımlı değişken desenine MANOVA'nın çoklu bağımlı değişken
     ihtiyacı için afa/kumeleme'nin checkbox-list deseni eklendi), `seo_content.py`,
     `forum/sitemaps.py`. 71 yeni msgid EN/DE'ye çevrildi (**ders:** şablonda
     `{% trans "...Wilks\' Λ..." %}` içinde gereksiz ters eğik çizgi kaçışı
     (`\'`) kullanmak Django trans tag'inde literal karakter olarak kalıp
     farklı/kopuk bir msgid üretiyor — `apaSig`/`apaNs`/`etaText` JS
     sabitlerinde bulunup düzeltildi, `makemessages` tekrar çalıştırılıp
     doğrulandı). Docker'da: `analyze()` doğrudan (anlamlı/anlamsız × 2-3
     grup × 2-3 bağımlı değişken × geçersiz girdi — tek değişken/eksik sütun/
     grup içi çakışma/yetersiz gözlem/çok fazla grup senaryoları) ve tam
     uçtan uca akış (preview→run→job kuyruğu→analiz→PDF, gerçek async
     `enqueue` senkron çalıştırılarak, `upload_bytes_to_s3` mock'lanarak) test
     edildi; TR/EN/DE anonim (promo) sayfa 200, sitemap üç dilde URL'i
     içeriyor, 104/104 pytest yeşil, `docker compose restart web` + nginx
     yapıldı. Kullanıcı onayıyla (önce yedek alındı) `dev`→`main` merge + push
     edildi, GitHub Actions otomatik Hetzner deploy'u tetikledi, migration
     production'da uygulandı, canlı doğrulandı (`https://www.analizus.com/
     analiz/manova/` TR/EN/DE 200).
  4. [x] **(27 Ekim 2026 TAMAMLANDI) Sağkalım Analizi (Kaplan-Meier / Cox
     Regresyon)** — kullanıcı kararıyla: tek araç (Yöntem dropdown: Kaplan-Meier
     / Cox Regresyon, kümeleme ile aynı desen) + Cox'ta oransal tehlikeler
     (proportional hazards) varsayım testi eklendi. **Bağımlılık notu:**
     `lifelines` paketi denendi ama `pandas<3.0` gerektirdiği için projenin
     `pandas==3.1.0` sabitlemesiyle çakıştı (Docker build `ResolutionImpossible`
     hatası verdi) — pandas'ı düşürmek yerine **statsmodels'in kendi
     `duration` modülü** (zaten kurulu, `statsmodels==0.15.0`) kullanıldı:
     `SurvfuncRight` (Kaplan-Meier, Greenwood SE, medyan), `survdiff`
     (log-rank, 2+ grup genellemeli) ve `PHReg` (Cox, Efron tie-breaking).
     Yeni `istatistik/services/sagkalim.py`: olay değişkeni lojistik_regresyon
     ile birebir aynı 2-kategori→0/1 kodlama deseni (`event_category` ile
     hedef kategori seçimi, `views.py`'deki `category_values` önizleme
     mekanizması `lojistik_regresyon`'dan `sagkalim`'e de genişletildi).
     Cox'ta: hazard oranı + %95 GA (log ölçekten `exp()` ile dönüştürüldü),
     Harrell's C-index (elle, O(n²) ama n≤birkaç bin için hızlı), oransal
     tehlikeler testi (Grambsch & Therneau 1994 yaklaşımı — ölçeklenmiş
     Schoenfeld rezidülerinin olay zamanı sırasıyla Pearson korelasyonu;
     `statsmodels`'te hazır fonksiyon yok, elle implemente edildi).
     Değişken başına minimum 10 olay (EPV kuralı) hard validation olarak
     uygulandı. Mevcut 22 araçla aynı iskelet: `TOOL_CHOICES` + migration
     `0016_add_sagkalim_tool`, `job_runner.py` dispatch dalı +
     `_AI_PROMPT_EXCLUDE_KEYS` (km_plot_b64 + curves — uzun zaman/olasılık
     dizileri), `views.py` ("Regresyon Analizleri" grubuna 5. satır,
     `sagkalim_landing`, `_handle_group_tool_post` options dalı,
     `_SLUG_MAP`), `urls.py`, `job_queue.py` whitelist, yeni `istatistik/
     templates/istatistik/sagkalim.html` (grup değişkeni YA DA kovaryat
     checkbox-listesi yönteme göre dinamik gösterilip gizleniyor), `seo_content.py`,
     `forum/sitemaps.py`. **Bulunan 2 hata, düzeltildi:** (1) Kaplan-Meier
     eğrisinin standart hata dizisinde (Greenwood formülü, risk seti
     küçüldüğünde) `NaN` oluşabiliyordu — Postgres JSONField NaN kabul
     etmediği için job tamamlanırken patlıyordu (CLAUDE.md'de zaten
     belgelenmiş "result_data kaydetmeden önce inf/nan temizle" tuzağı);
     `_safe_round()` yardımcısıyla NaN/inf → `None` çevrildi. (2) Şablonda
     `{% trans %}` içinde "%95" kullanmak (manova turundaki `\'` kaçış dersine
     benzer ama farklı bir tuzak) Django'nun extraction aşamasında "%%95"e
     dönüştürülüyor, Python tarafındaki (`sagkalim.py`) "%95" msgid'inden
     FARKLI bir kayıt oluşturuyor — ikisi ayrı ayrı çevrildi, izole
     `Template()` render testiyle (hem EN hem DE) tek `%` olarak doğru
     render edildiği doğrulandı. 107 yeni msgid EN/DE'ye çevrildi. Docker'da:
     `analyze()` doğrudan (KM gruplu/gruplu-anlamsız/grupsuz × Cox × string
     olay etiketi + event_category × 6 geçersiz girdi senaryosu) ve tam
     uçtan uca akış (her iki yöntem için ayrı ayrı preview→run→job
     kuyruğu→analiz→PDF) test edildi; TR/EN/DE anonim sayfa 200, sitemap üç
     dilde URL'i içeriyor, 104/104 pytest yeşil, `docker compose restart web`
     + nginx yapıldı. Kullanıcı onayıyla (önce yedek alındı) `dev`→`main`
     merge + push edildi, GitHub Actions otomatik Hetzner deploy'u
     tetikledi, migration production'da uygulandı, canlı doğrulandı
     (`https://www.analizus.com/analiz/sagkalim/` TR/EN/DE 200).
  5. [x] **(27 Ekim 2026 TAMAMLANDI) ROC Eğrisi / Tanısal Tarama Analizi**
     — lojistik regresyon FAQ'ı zaten AUC-ROC'tan bahsediyordu ama hesaplayan
     araç yoktu. Kullanıcı kararıyla: (1) AUC güven aralığı Hanley-McNeil
     (1982) kapalı-form formülüyle, (2) kapsam genişletilip iki testi aynı
     örneklemde karşılaştıran DeLong testi (DeLong, DeLong & Clarke-Pearson,
     1988) de eklendi. Yeni `istatistik/services/roc.py`: tek test modunda
     `sklearn.metrics.roc_curve`/`auc` ile ROC eğrisi, AUC negatifse (ters
     yönlü test — düşük değer = pozitif) otomatik yön düzeltmesi (test
     senaryosuyla doğrulandı: ters yönlü veri orijinaliyle BİREBİR aynı AUC/
     duyarlılık/özgüllük sonucunu veriyor), Youden J indeksine göre optimal
     kesim noktası + o noktada duyarlılık/özgüllük/PPV/NPV/LR+/LR- tablosu.
     İki test karşılaştırma modunda DeLong testi elle implemente edildi
     (statsmodels/sklearn'de hazır fonksiyon yok — DeLong yerleşim
     (placement) değerleri üzerinden kovaryans matrisi, z-testi). Olay/
     referans değişkeni kodlaması `lojistik_regresyon.py`/`sagkalim.py` ile
     birebir aynı 2-kategori→0/1 deseni (`positive_category` ile hedef
     kategori seçimi, `views.py`'deki `category_values` önizleme mekanizması
     `roc`'a da genişletildi). Mevcut 23 araçla aynı iskelet: `TOOL_CHOICES`
     + migration `0017_add_roc_tool`, `job_runner.py` dispatch dalı +
     `_AI_PROMPT_EXCLUDE_KEYS`, `views.py` ("Regresyon Analizleri" grubuna
     6. satır, `roc_landing`, `_handle_group_tool_post` options dalı,
     `_SLUG_MAP`), `urls.py`, `job_queue.py` whitelist, yeni `istatistik/
     templates/istatistik/roc.html` (tek test/iki test karşılaştırma moduna
     göre dinamik form + sonuç paneli), `seo_content.py`, `forum/
     sitemaps.py`. **Ders (manova/sagkalim turlarındaki aynı tuzak tekrar
     bulundu):** şablonda `{% trans "AUC (%95 GA)" %}` kullanımı yine
     extraction'da `%%95`e kaçtı — Python tarafındaki msgid'den ayrı tutulup
     her ikisi de çevrildi, izole `Template()` render testiyle tek `%`
     olarak doğru render edildiği doğrulandı. 83 yeni msgid EN/DE'ye
     çevrildi. Docker'da: `analyze()` doğrudan (güçlü/ters yönlü/ayırt
     edicilik yok × string etiket + positive_category × iki test
     karşılaştırma (anlamlı/anlamsız fark) × 4 geçersiz girdi senaryosu —
     confusion matrix sanity check'leriyle) ve tam uçtan uca akış (tek test
     ve karşılaştırma modları ayrı ayrı preview→run→job kuyruğu→analiz→PDF)
     test edildi; TR/EN/DE anonim sayfa 200, sitemap üç dilde URL'i
     içeriyor, 104/104 pytest yeşil, `docker compose restart web` + nginx
     yapıldı. **Ayrıca kullanıcı bulgusu (aynı oturumda düzeltildi):** ana
     sayfa hero/meta açıklaması + `egitim.html` + `teleprompter.html` +
     `analizdestek/urls.py` yorumundaki sabit "18" araç sayısı artık yanlıştı
     (kümeleme/MANOVA/sağkalım/ROC eklenince 18→24 oldu) — `TOOL_CATEGORIES`
     gerçek toplamı (24) ile güncellendi, ilgili 2 EN/DE çevirisi yeniden
     girildi; `analizus.md`/`tasks/todo.md` içindeki TARİHLİ geçmiş kayıtlara
     (o tarihte gerçekten 18'di) kasıtlı dokunulmadı. Kullanıcı onayıyla
     `dev`→`main` merge + push edildi, GitHub Actions otomatik Hetzner
     deploy'u tetikledi (19 sn), migration production'da uygulandı, canlı
     doğrulandı (`https://www.analizus.com/analiz/roc/` TR/EN/DE 200; ana
     sayfa artık "24 ücretsiz istatistik aracı" gösteriyor).
  6. [x] **(27 Ekim 2026) Basit Path Analizi (Çoklu Paralel Aracı Değişken) —
     TAMAMLANDI.** Kapsam kararı kullanıcı onayıyla netleşti: mediation.py'nin
     çoklu-aracı uzantısı (Hayes PROCESS Model 4'ün çoklu aracı versiyonu) —
     flexible genel path modeli veya `semopy` ile tam SEM DEĞİL. Yeni bağımlılık
     gerekmedi, mevcut `statsmodels` OLS zinciri + bootstrap (5000 iterasyon,
     percentile %95 GA) yeterli oldu (`lifelines`/pandas 3.1.0 çakışması emsali
     burada devreye girmedi). X (sayısal veya 2 kategorili, dummy'lenir) →
     2-5 paralel aracı M1..Mk (birbirinden bağımsız, aynı anda modellenir) →
     Y; her aracı için a (X→M) / b (M→Y, diğer aracılar kontrollü) yolları,
     dolaylı etki (a×b) ve bootstrap %95 GA; toplam dolaylı etki (Σ a×b) ve
     c/c' (toplam/direkt etki) üzerinden tam/kısmi/yok aracılık sınıflandırması.
     `istatistik/services/path_analizi.py` (yeni), model `TOOL_CHOICES` +
     migration `0018`, `views.py` (TOOL_CATEGORIES, POST options, landing view,
     `_SLUG_MAP`), `job_runner.py` dispatch, `urls.py`/`urls_analiz.py`,
     `job_queue.py` whitelist, `forum/sitemaps.py`, `seo_content.py` (FAQ'de
     Path Analizi vs Mediation farkı + seri/serial mediation sınırlaması
     açıklandı) — hepsi tek seferde entegre edildi. Şablon
     `path_analizi.html` manova.html'in checkbox-list deseniyle yazıldı (X/Y
     select + M için dinamik 2-5 checkbox listesi, X/Y seçilince otomatik
     filtrelenir). **Bulunan/düzeltilen 2 hata:** (1) `makemessages
     --no-location` yanlışlıkla kullanıldı, location yorumlarını silip ~15 bin
     satırlık gereksiz diff yarattı — fark edilip `git checkout` ile geri
     alındı, doğru komutla (`-l en -l de`, location'lı) yeniden çalıştırıldı;
     (2) JS'teki `rowCPrime` sabitinde `{% trans "c\' ..." %}` şeklinde
     gereksiz backslash-escape kullanılmıştı (manova.html'de daha önce
     yakalanan aynı tuzak) — yanlış/duplicate msgid üretiyordu, backslash
     kaldırılarak düzeltildi. Docker'da gerçek (mocklanmamış) e2e test:
     preview → run → async job (senkron patch ile) → sonuç → PDF (S3'e
     gerçek upload + HEAD isteğiyle 200/application/pdf doğrulandı) — n=200
     sentetik veri, 2 aracı anlamlı (kısmi aracılık) + 1 aracı anlamsız örneği
     ile uçtan uca test edildi. Anonim promo sayfası TR/EN/DE 200, auth
     konsol sayfası 200, `/analiz/` hub sayfasında kart görünüyor, sitemap
     200. 39 yeni msgid EN/DE çevrildi (`%%95` çift-yüzdeleme tuzağına dikkat
     edildi — template-side msgid'de `%%`, msgstr'de de `%%` olmalı; render
     testiyle tek `%`'ye doğru çözüldüğü doğrulandı), `compilemessages`
     hatasız. `pytest forum/tests.py` 104/104 yeşil. `dev`→`main` merge +
     push edildi (27 Ekim 2026), GitHub Actions otomatik Hetzner deploy'u
     tetikledi (18 sn), migration `0018` production'da uygulandı, canlı
     doğrulandı (`/analiz/path-analizi/` TR/EN 200).
  7. [x] **(27 Ekim 2026) Güç Analizi (Post-hoc Power) — TAMAMLANDI.** Kapsam
     kararı kullanıcı onayıyla netleşti: yeni ayrı bir araç DEĞİL, mevcut
     `orneklem` hesaplayıcısına "Örneklem Hesapla (A Priori)" / "Güç Hesapla
     (Post-hoc)" mod geçişi eklendi. Yeni kütüphane gerekmedi —
     `orneklem.py`'deki `_ttest_power`/`_anova_power`/`_correlation_power`
     fonksiyonları zaten n verildiğinde gücü hesaplıyordu (a priori mod
     bunları binary search içinde hedef güce ulaşan n'i ararken kullanıyordu);
     yeni `calculate_post_hoc()` aynı fonksiyonları n sabitken DOĞRUDAN
     çağırıyor, binary search'e gerek yok. Round-trip doğrulandı: a priori
     modda d=0.5/α=0.05/güç=0.80 için bulunan n=63, post-hoc moda aynen
     verilince achieved_power=0.8013 ile tam örtüştü. 4 test tipi (bağımsız/
     bağımlı t-testi, ANOVA, korelasyon) + hata durumları (n<2, r≥1) test
     edildi. Yeni `_interpret_power()` yorumu 4 kademeli (çok düşük/düşük/
     yeterli/çok yüksek güç, Tip II hata riski vurgusu). `views.py`'de
     `_handle_orneklem_calc` artık `mode` POST parametresine göre
     `calculate`/`calculate_post_hoc` arasında dallanıyor (mode gönderilmezse
     a_priori — geriye dönük uyumlu, eski davranış değişmedi).
     `orneklem.html` şablonunda mod seçimi butonları eklendi; post-hoc modda
     "İstatistiksel Güç" input'u gizlenip yerine "Elde Edilmiş Örneklem
     Büyüklüğü (n)" input'u çıkıyor, sonuç panelindeki ana kutu (öncesi:
     toplam örneklem) post-hoc modda elde edilen güce dönüşüyor, yorum kutusu
     "Yorum"/öneri yerine "Güç Yorumu" gösteriyor, APA cümlesi moda göre iki
     ayrı şablondan (`T.apa`/`T.apaPostHoc`) üretiliyor — mevcut Bootstrap
     tasarımı korundu (bu dosya henüz ax- migrasyonuna dahil değil, kapsam
     dışına çıkılmadı). Docker'da view endpoint'i her iki mod + hata senaryosu
     (eksik n → 400) ile doğrudan test edildi, `/analiz/orneklem/` TR/EN/DE
     200. 15 yeni msgid EN/DE çevrildi (`gettext()` + `{% trans %}` render
     testiyle doğrulandı), `compilemessages` hatasız, `pytest forum/tests.py`
     104/104 yeşil. Henüz push/merge edilmedi — kullanıcının "push et"/
     "merge et" onayı bekleniyor.
  - Düşük öncelik / sonra değerlendirilebilir: diskriminant analizi, ordinal/
    multinomial lojistik regresyon.

- [ ] **(25 Ekim 2026) İstatistik Araçları Denetimi — 18 aracın tamamı (hesaplama +
  rapor kalitesi) 7 paralel subagent ile salt-okunur incelendi. Hiçbir dosya
  değiştirilmedi. Bulgular şiddete göre (en kritik üstte):**

  **YÜKSEK — bilimsel doğruluk/güven kırıcı:**
  1. [x] **(25 Ekim 2026 düzeltildi)** `istatistik/services/normallik.py` —
     n>5000 olduğunda kod aslında `scipy.stats.normaltest` (D'Agostino K²)
     çalıştırıyor ama sonucu `shapiro_stat`/`shapiro_p` adıyla saklıyor; hem
     PDF hem ekran APA metni koşulsuz "Shapiro-Wilk testi ile incelenmiştir"
     diyor. Ayrıca sayfa başlığı/meta "Kolmogorov-Smirnov" testini vaat
     ediyor ama kodda KS testi hiç yok. Üstüne üstlük şablonda normallik
     eşiği için üç farklı yerde üç farklı sayı var (n<50 / n<2000 / kodda
     n<=5000), hiçbiri tutmuyor. **Düzeltme:** `test_name`/`test_stat_label`
     alanları eklendi (n≤5000 → Shapiro-Wilk/W, n>5000 → D'Agostino K²/K²),
     PDF tablosu+APA metni ve ekran JS'i artık gerçek test adını dinamik
     gösteriyor; title/meta/metodoloji/SSS'ten KS iddiası kaldırılıp D'Agostino
     K² ile değiştirildi, üç farklı eşik n≤5000/n>5000'e birleştirildi;
     `seo_content.py` aynı şekilde düzeltildi. EN/DE çevirileri eklenip
     `compilemessages` hatasız derlendi; Docker'da küçük (Shapiro) + büyük
     (D'Agostino) örneklem senaryoları ve EN/DE aktivasyonu test edildi.
  2. [x] **(25 Ekim 2026 düzeltildi)** `istatistik/templates/istatistik/betimsel.html:177-196`
     — "Hesaplanan İstatistikler" listesi Mod, Varyans, Çarpıklık (Skewness),
     Basıklık (Kurtosis) hesaplandığını iddia ediyor + yorum eşik tablosu
     gösteriyor; ama `betimsel.py` bunların hiçbirini hesaplamıyor (sadece
     n/mean/std/min/max/median/q1/q3). Kullanıcı ekranda/PDF'te bu değerleri
     bulamaz. **Düzeltme:** `betimsel.py`'ye Mod/Varyans/Çarpıklık/Basıklık
     gerçekten eklendi (mod, tüm değerler tekilse `None` döner), PDF'e
     "Dağılım Şekli ve Ek Ölçüler" tablosu eklendi (A4'e uyan genişlik);
     `betimsel.html`'e dokunulmadı çünkü ekranda zaten detaylı tablo yok,
     metodoloji metni artık doğru. Docker'da tekil/tekrarlı veri senaryoları
     test edildi, PDF başarıyla üretildi.
  3. [x] **(25 Ekim 2026 düzeltildi)** `istatistik/templates/istatistik/ttesti.html`
     + SEO metni — "Tek Örneklem t-Testi" üçüncü bir özellik olarak
     tanıtılıyordu (başlık, "Nedir?" kartı) ama `ttesti.py` yalnızca bağımsız/
     bağımlı örneklemi destekliyordu; arayüzde de seçenek yoktu. **Düzeltme
     (kullanıcı kararı: metinden çıkarma değil, gerçekten eklendi):**
     `ttesti.py`'ye `_one_sample()` dalı (scipy `ttest_1samp`, Cohen's d,
     %95 GA) + `_conclusion_one_sample()` eklendi; `analyze()` dispatcher ve
     `build_pdf()` (grup tablosu + APA metni) üç test tipini de kapsıyor;
     `ttesti.html`'e "Tek Örneklem" toggle butonu + değişken/test değeri
     seçimi + istemci tarafı doğrulama eklendi; `views.py`/`job_runner.py`
     `test_value` parametresini taşıyor. EN/DE çevirileri eklenip
     `compilemessages` hatasız derlendi. Docker'da: bağımsız/bağımlı
     regresyon testi (bozulmadı), tek örneklem hata senaryoları (değer yok/
     sayısal değil/sütun yok), TR/EN/DE APA çıktısı ve gerçek `IstatistikJob`
     üzerinden uçtan uca job_runner akışı test edildi.
  4. [x] **(25 Ekim 2026 düzeltildi)** `istatistik/services/tekrarli_anova.py`
     — Küresellik (Mauchly) testi hiç uygulanmıyor; kod bunu `sphericity_note`
     ile PDF'e yazıyordu ama ekran şablonunda bu not hiçbir yerde render
     edilmiyordu. PDF indirmeyen kullanıcı bu kritik varsayımın (Tip-I hata
     riski) test edilmediğinden habersiz kalıyordu. **Karar (kullanıcı,
     25 Ekim 2026):** gerçek Mauchly testi eklenmedi (kapsam büyük) — mevcut
     `sphericity_note` ekrana da taşındı (`ax-alert-warning` kutusu).
     Aynı şablondaki post-hoc tablosunda bulunan ek bir XSS noktası
     (`ph.col1`/`ph.col2`) da `_esc()` ile düzeltildi.
  5. [x] **(25 Ekim 2026 düzeltildi)** `istatistik/templates/istatistik/cronbach.html:186-191`
     vs `cronbach.py:78-88` — Ekrandaki statik "Yorum Eşikleri" tablosu
     (.50-.70 = "Düşük") ile gerçek hesaplanan `interpretation` (.60-.70 =
     "Kabul Edilebilir") farklı eşik/etiket kullanıyor; α=0.65 çıkan kullanıcı
     aynı sayfada çelişen iki yorum görüyor. **Düzeltme:** Tablo koddaki 6
     banda (<.50/.50-.60/.60-.70/.70-.80/.80-.90/≥.90) birebir uyacak şekilde
     güncellendi, EN/DE çevirileri eklendi.
  6. [x] **(25 Ekim 2026, ayrıca yapıldı — kullanıcı talebi)** AI Yorumu artık
     17 aracın tamamının PDF raporuna da ekleniyor (önceden yalnız ekranda
     görünüyordu) — ayrıntı §12 ve bu dosyanın ilerisindeki ilgili madde.
  6. [x] **(25 Ekim 2026 düzeltildi)** `istatistik/services/afa.py` —
     `eigen_table` (özdeğer tablosu) hesaplanıp hiç kullanılmıyordu; SSS
     içeriği kullanıcıya "scree plot kırılma noktası" kriterini öneriyordu
     ama araç scree plot/özdeğer tablosu hiç sunmuyordu. Ayrıca faktör yük
     matrisi + varyans tablosu PDF'e yazılıyordu ama ekranda yalnız 5 özet
     sayı vardı. **Düzeltme:** `afa.py`'ye matplotlib ile scree plot (Kaiser
     kriteri çizgili, base64 PNG) eklendi, PDF'e özdeğer tablosu + scree plot
     eklendi; `afa.html` ekranına scree plot görseli + faktör yük matrisi
     tablosu + açıklanan varyans tablosu eklendi (`_esc()` ile kaçışlı, ek
     bir XSS noktası — checkbox listesi — de aynı dosyada düzeltildi).
     `job_runner.py`'nin AI prompt hariç tutma listesine `scree_plot_b64`
     eklendi. EN/DE çevirileri eklendi, `compilemessages` hatasız derlendi;
     TR/EN/DE üç dilde `analyze()`+`build_pdf()` test edildi.
  7. [x] **(25 Ekim 2026 düzeltildi)** `istatistik/services/korelasyon.py:105`
     — Isı haritası hücre metin rengi mantığı TERS: `'black' if
     0.3<=|r|<=0.7 else 'white'`. RdYlGn skalasında en sık görülen zayıf
     korelasyonlar (|r|<0.3) açık/krem renkte ama bunlara beyaz metin
     atanıyor → sayılar neredeyse görünmez (gerçek render ile doğrulanmış).
     **Düzeltme:** Sabit eşik yerine o hücrenin matplotlib colormap'ten
     gelen gerçek renk parlaklığı (luminance) hesaplanıp kontrast rengi ona
     göre seçiliyor; val=0 (en sık durum) artık siyah metinle okunaklı,
     val=±1 uçları beyaz metinle kalıyor. Docker'da luminance/renk eşlemesi
     ve gerçek ısı haritası + PDF üretimi test edildi.
  8. [x] **(25 Ekim 2026 düzeltildi)** `istatistik/services/ki_kare.py:216-217`
     (build_pdf, çapraz tablo) — Sabit sütun genişliği (`[3cm]+[2cm]*(n_cols-1)`),
     A4'te kullanılabilir alan 17cm. 2. değişkenin kategori sayısı 7'yi
     aşınca (şehir/bölüm/fakülte gibi sık rastlanan değişkenler) fazla
     sütunlar ve "Toplam" sütunu sayfadan taşıp PDF'te TAMAMEN KAYBOLUYOR
     (hata vermeden, gerçek render ile doğrulandı) — sessiz veri kaybı.
     **Düzeltme:** Sütun genişliği + font boyutu kategori sayısına göre
     dinamik hesaplanıyor (taban 0.9cm, toplam ≤17cm garantili); ayrıca aynı
     dosyadaki özet tablo da (18.2cm → 16.5cm) taşma sınırından çıkarıldı.
     Docker'da 12+ kategorili senaryoda (eski yöntemle 29cm çıkacak tablo)
     PDF'in artık 17cm sınırını aşmadığı doğrulandı.
  9. [x] **(25 Ekim 2026 düzeltildi)** `istatistik/services/ki_kare.py:30` —
     `chi2_contingency(ct)` parametresiz çağrılıyor → scipy varsayılanı 2×2
     tabloda Yates süreklilik düzeltmesini otomatik uyguluyor, ama ne
     ekranda ne PDF'te ne APA cümlesinde bu düzeltmenin uygulandığı
     belirtiliyordu. **Düzeltme:** `yates_applied` alanı eklendi (yalnızca
     2×2 tabloda True); APA cümlesine ve ekran JS'ine "2×2 tablo olduğu için
     Yates düzeltmesi uygulanmıştır" notu koşullu olarak ekleniyor. EN/DE
     çevirileri eklendi.
  9b. [x] **(25 Ekim 2026, denetim sırasında ek bulgu — kullanıcı onayıyla
      düzeltildi)** `lineer_regresyon.html`, `lojistik_regresyon.html` +
      `ki_kare.html` — kullanıcı dosyasından gelen sütun/kategori adları
      (`c.name`, `cl.cat0/cat1`, çapraz tablo satır/sütun başlıkları)
      escape'siz `innerHTML`'e yazılıyordu (self-XSS riski, CLAUDE.md
      güvenlik kuralına aykırı). **Düzeltme:** Projede zaten var olan
      `_esc()` deseni (openalex/tezanaliz/trdizin vb. landing şablonlarında
      kullanılan) bu üç şablona da eklendi, tüm ilgili interpolasyonlar
      kaçışlandı.
  10. [x] **(25 Ekim 2026 düzeltildi)** `karar_agaci.html` + `svm.html` —
      Sayfa açıklaması "confusion matrix"/"ağaç yapısı" gösterileceğini vaat
      ediyordu ama ekran JS'i (`showResults()`) bunları hiç render etmiyordu,
      yalnızca PDF'te vardı. Ayrıca `istatistik/seo_content.py`'deki örnek
      APA cümleleri ("AUC = .88/.91") bu iki aracın hiç hesaplamadığı bir
      metriğe atıf yapıyordu (ne karar_agaci ne svm AUC/ROC hesaplıyor;
      lojistik_regresyon'un FAQ'ındaki AUC-ROC referansı da aynı şekilde
      yanlıştı). **Düzeltme:** Her iki şablonun ekranına confusion matrix
      tablosu eklendi (karar_agaci'ye ayrıca ağaç yapısı metni, PDF ile aynı
      ilk-5-seviye/ilk-40-satır sınırıyla); aynı dosyalarda bulunan ek
      XSS noktaları (`f.name`, `r.classes.join`) `_esc()` ile düzeltildi;
      `seo_content.py`'deki 4 yanlış AUC referansı gerçekte hesaplanan
      metriklerle (precision/recall/accuracy/F1) değiştirildi. EN/DE
      çevirileri eklendi, Docker'da gerçek sayfa render + JS sözdizimi
      (node --check) + 104 testlik pytest paketiyle doğrulandı.

  **ORTA — doğruluk nüansı / tutarsızlık:**
  11. [x] **(25 Ekim 2026 düzeltildi — bkz. madde 9b)** `lineer_regresyon.html`
      + `lojistik_regresyon.html` — kullanıcı dosyasından gelen sütun/kategori
      adları (`c.name`, `cl.cat0/cat1`) escape'siz `innerHTML`'e yazılıyor
      → CLAUDE.md güvenlik kuralına aykırı
      self-XSS riski (kötü niyetli sütun adıyla `<img onerror=...>` vb.).
  12. [x] **(25 Ekim 2026 düzeltildi)** `normallik.py` — çoklu sütun seçiminde
      satır-bazlı (listwise) `dropna()` kullanılıyordu; bir sütundaki eksik
      veri diğer dolu sütunların satırlarını da siliyordu (betimsel.py'deki
      sütun-bazlı yaklaşımla tutarsız), N'i gereksiz düşürüyordu.
      **Düzeltme:** `analyze()`'daki listwise `df_num.dropna()` satırı
      kaldırıldı; döngü içindeki sütun-bazlı `df_num[col].dropna()` zaten
      yeterli ve doğru.
  13. [x] **(25 Ekim 2026 düzeltildi)** `normallik.py` — skewness/kurtosis
      için ±1.96 eşiği ham değere uygulanıyordu; bu z-kritik değeridir, ham
      çarpıklık/basıklığa değil SE'ye bölünmüş z-skoruna uygulanması
      gerekirdi — iki farklı yöntem karışmıştı. **Düzeltme:** standart hata
      (SES/SEK) hesaplanıp `skew/SES`, `kurt/SEK` z-skorları ±1.96 ile
      karşılaştırılıyor (`views.py:149`'daki açıklamayla tutarlı); n≤3'te
      SEK tanımsız olduğu için kurtosis kontrolü o durumda atlanıyor.
  14. [x] **(25 Ekim 2026 düzeltildi)** `orneklem.py` — korelasyon testi için
      r≥1 girilirse `math.atanh` "math domain error" ile çöküyordu, kullanıcıya
      ham Python hata metni gösteriliyordu; ayrıca t-testi gücü noncentral-t
      yerine normal yaklaşımla (Laubscher) hesaplanıyor ama sayfa "G*Power
      alternatifi" vaat ediyordu, bu yaklaşıklık belirtilmiyordu. **Düzeltme:**
      `calculate()`'e `test_type == 'correlation' and effect_size >= 1`
      kontrolü eklendi (net Türkçe `ValueError`, view zaten 400 ile yakalıyor);
      `orneklem.html` Metodoloji bölümüne t-testi gücünün normal yaklaşımla
      (Laubscher) hesaplandığını ve G*Power ile pratikte uyumlu olduğunu
      belirten bir not eklendi.
  15. [x] **(25 Ekim 2026 düzeltildi)** `anova.py` — Levene testi hesaplanıp
      gösteriliyordu ama (ttesti.py'nin aksine) varyans homojen değilse Welch
      düzeltmesine otomatik geçiş yoktu (oysa `seo_content.py` "ihlal
      durumunda Welch ANOVA kullanılır" diye zaten vaat ediyordu); ayrıca
      "Tukey" post-hoc'u aslında Bonferroni ile aynı formülü kullanıyor
      (kodda dürüstçe "Tukey (Bonferroni yaklaşımı)" etiketli ve sonuç
      ekranında bu şekilde görünüyor — TEMİZ), ama analiz ÖNCESİ sayfa
      metni/buton/SEO açıklaması gerçek Tukey HSD izlenimi veriyordu.
      **Düzeltme:** `_welch_anova()` eklendi — Levene p<0.05 olunca gerçek
      Welch F/p/df hesabı devreye giriyor, post-hoc ikili karşılaştırmalar da
      `equal_var=not used_welch` ile tutarlı hale getirildi; `test_label`'a
      "(Welch)" eki PDF başlığı + ekran etiketine yansıtıldı (ttesti.py
      pattern'i). `anova.html` title/meta + post-hoc buton altına "Tukey
      etiketi Bonferroni yaklaşımıdır" notu eklendi; `seo_content.py`'deki
      "Tukey daha güçlüdür" SSS cevabı, iki seçeneğin aslında aynı formülü
      kullandığını ve Welch'e otomatik geçişi doğru anlatacak şekilde
      düzeltildi. Docker'da homojen/heterojen varyans senaryoları + r≥1
      (madde 14) + template render + 104/104 pytest doğrulandı.
  16. [x] **(25 Ekim 2026 düzeltildi)** `anova.html:220` — "Tukey HSD"/
      "Bonferroni"/"Games-Howell" terimleri ayrı `{% trans %}` parçalarına
      bölünmüştü — CLAUDE.md'nin "parça birleştirme yok, tam cümle msgid"
      i18n kuralına aykırıydı. **Düzeltme:** tek cümle `{% blocktrans %}`
      bloğuna birleştirildi (`<strong>` etiketleri gömülü — projede zaten
      var olan `analiz_console_base.html:114` deseniyle aynı); render testiyle
      HTML'in kaçışsız ve tam cümle olarak çıktığı doğrulandı.
  17. [x] **(25 Ekim 2026 düzeltildi)** `kruskal_wallis.py:21` — Grup
      etiketleri `sorted(..., key=str)` ile STRING olarak sıralanıyordu
      (1,10,2,20 gibi görünebiliyordu); post-hoc gerçek Dunn testi değildi,
      Bonferroni+ikili Mann-Whitney hesaplanıyordu — oysa hem kod yorumu hem
      `seo_content.py` (intro/how_to_interpret/apa_example/FAQ) zaten "Dunn
      post-hoc testi uygulanır" diye vaat ediyordu. **Düzeltme:** sayısal
      etiketler için `key=float` denenip olmazsa `key=str`'ye düşülüyor;
      post-hoc artık gerçek Dunn testi (pooled sıra varyansı + bağlı değer
      düzeltmeli z-istatistiği) + Bonferroni — `seo_content.py`'ye hiç
      dokunmaya gerek kalmadı, zaten doğruydu. `kruskal_wallis.py` PDF'i ve
      `kruskal_wallis.html` ekranı `u_stat`/"U" yerine `z_stat`/"z" ve
      "Dunn + Bonferroni" etiketini gösteriyor. EN/DE çevirisi eklendi,
      Docker'da ters sayısal sıra + bağlı (tied) değer senaryoları test
      edildi, 104/104 pytest yeşil. **Not (ayrı, çözülmedi — todo'ya
      eklendi):** `anova.py`/`lojistik_regresyon.py` aynı `key=str` sıralama
      desenini taşıyor ama bu maddenin kapsamı dışında bırakıldı.
  17b. [x] **(25 Ekim 2026 düzeltildi)** `anova.py:18` ve
      `lojistik_regresyon.py:36` — `kruskal_wallis.py`'de düzeltilen aynı
      `sorted(..., key=str)` grup/kategori etiketi sıralama sorunu (numerik
      etiketler 1,10,2,20 gibi yanlış sıralanıyordu) bu iki dosyada da
      vardı. **Düzeltme:** aynı `key=float` dene, olmazsa `key=str`'ye düş
      deseni uygulandı (`lojistik_regresyon.py`'de binary kategori
      sıralaması — varsayılan referans/hedef ataması — için). Docker'da
      ters sayısal sıralı grup/kategori senaryoları (1,10,2 → 1,2,10;
      2,10 → 2,10) test edildi, 104/104 pytest yeşil.
  18. [x] **(25 Ekim 2026 düzeltildi)** `mann_whitney.html` + `kruskal_wallis.html`
      — `views.py` `active_job_id`'yi context'e koyuyordu ama şablonlar
      wilcoxon.html/friedman.html'deki gibi bunu okuyup `startPolling()`
      çağırmıyordu; analiz sürerken sayfa yenilenirse job takibi kopuyordu.
      **Düzeltme:** her iki şablonun script sonuna `{% if active_job_id %}`
      bloğu eklendi (`showPanel('loading')` + `startPolling('{{ active_job_id }}')`
      — bu iki araçta `startPolling(jobId)` parametre alıyor, wilcoxon'daki
      gibi ayrı bir `currentJobId` değişkenine gerek yok). **Ayrıca madde
      17'den kalan iki unutulan metin de düzeltildi:** `views.py:534`
      (kruskal-wallis promo "Post-Hoc" özelliği) ve `kruskal_wallis.html:89`
      hâlâ "Mann-Whitney + Bonferroni" diyordu, "Dunn + Bonferroni" ile
      güncellendi. EN/DE çevirileri eklendi, Docker'da template render +
      104/104 pytest doğrulandı. **Not (ayrı, çözülmedi — todo'ya eklendi):**
      `anova.html` ve `ttesti.html` de aynı `active_job_id` okumama sorununu
      taşıyor.
  18b. [x] **(25 Ekim 2026 düzeltildi)** `anova.html` ve `ttesti.html` —
      `views.py` bu iki araç için de `active_job_id`'yi context'e
      koyuyordu ama şablonlar bunu okuyup sayfa yenilenince
      `startPolling()`'i devam ettirmiyordu (madde 18'deki ile aynı sorun).
      **Düzeltme:** `anova.html`'e `showPanel('loading'); startPolling('{{
      active_job_id }}');` eklendi (jobId parametre alıyor); `ttesti.html`
      zaten var olan `currentJobId` değişkenini kullanıyor (wilcoxon.html
      deseniyle aynı). Docker'da her iki şablonun render testiyle
      doğrulandı, 104/104 pytest yeşil.
  19. [x] **(25 Ekim 2026 düzeltildi)** `lojistik_regresyon.py` — VIF/çoklu
      bağlantı kontrolü hiç yoktu ama SEO metni ve "Nedir?" kartı VIF'den
      bahsediyordu; hedef kategori (y=1) otomatik alfabetik sıralamayla
      seçiliyordu, kullanıcı seçemiyordu — Exp(B) yönü beklenenin tersi
      okunabiliyordu. **Düzeltme (kullanıcı kararı: tam özellik):**
      `lojistik_regresyon.py`'ye `lineer_regresyon.py` ile aynı desende VIF
      hesabı eklendi (ekran tablosu + PDF + footnote); `analyze()`'a opsiyonel
      `target_category` parametresi eklendi (boşsa eski davranış — sıralı
      2. değer — korunuyor). UI: preview adımı artık 2-kategorili sütunların
      değerlerini (`category_values`) döndürüyor, `lojistik_regresyon.html`'de
      bağımlı değişken seçilince "Hedef Kategori (Y=1)" seçici beliriyor
      (varsayılan seçili değer mevcut davranışla aynı); `views.py` options +
      `job_runner.py` parametreyi uçtan uca taşıyor. EN/DE çevirileri
      eklendi, Docker'da varsayılan/ters hedef kategori senaryoları
      (`B` katsayısının işareti doğru tersine dönüyor) + gerçek job pipeline
      (preview→run→job_runner→PDF/S3) uçtan uca test edildi, 104/104 pytest
      yeşil.
  20. [x] **(25 Ekim 2026 düzeltildi)** `lineer_regresyon.html`/
      `lojistik_regresyon.html` — ekranda Bootstrap'ın varsayılan mavisi
      kullanılıyordu, PDF'te ise marka rengi (navy/teal) — ekran/PDF renk
      tutarsızlığı. **İnceleme:** `lojistik_regresyon.html` zaten PDF'teki
      teal (`#065f46`) ailesinden hex renkler kullanıyordu (sorun yoktu);
      asıl sorun yalnız `lineer_regresyon.html`'deydi — tüm `btn-primary`/
      `text-primary` (Bootstrap varsayılan mavisi `#0d6efd`) kullanımları,
      PDF'in navy'siyle (`#1e3a5f`) aynı aileden renklerle değiştirildi:
      dolgu butonlarda tam navy (`#1e3a5f`, üstünde beyaz metin), ikon/metin
      vurgularında koyu arka plan üzerinde okunaklı açık mavi tonu
      (`#60a5fa`) — diğer araçlardaki "koyu buton + açık ikon" deseniyle
      tutarlı (ör. kruskal-wallis teal `#065f46`/`#34d399`). Docker'da
      render doğrulandı (2 buton + 7 ikon/metin), 104/104 pytest yeşil.
  21. [x] **(25 Ekim 2026 düzeltildi)** `static/css/analiz_console.css`
      (254, 273, 318 satırları) — `var(--ax-primary)` token'ı projede HİÇ
      tanımlanmamıştı (CLAUDE.md'deki bilinen `--ax-color-primary`
      hatasından farklı, ayrı bir eksik token); SSS accordion oku, "İlgili
      Araçlar" çip rengi, APA kutusu kenarlığı tarayıcıda varsayılana
      düşüyordu. **Düzeltme:** üç kullanım da `base.css`'de zaten tanımlı
      olan doğru değişken `var(--ax-accent-primary)` ile değiştirildi (proje
      genelinde `.ax-link`/`.ax-badge--primary` vb. için kullanılan standart
      token). **Not (ayrı, çözülmedi — todo'ya eklendi):**
      `static/css/profiles.css:690`'da da aynı tanımsız `--ax-primary`
      kullanımı var, bu maddenin kapsamı dışında bırakıldı.
  21b. [x] **(25 Ekim 2026 düzeltildi)** `static/css/profiles.css:690` —
      madde 21'de düzeltilen aynı tanımsız `var(--ax-primary)` token'ı
      burada da kullanılıyordu (portfolyo kartı hover kenarlığı; hemen
      yanındaki `box-shadow` zaten `rgba(99,102,241,...)` — `--ax-accent-
      primary`'nin hex karşılığı — kullanıyordu, bu da doğru tokenı
      doğruladı). **Düzeltme:** `var(--ax-accent-primary)` ile değiştirildi.
      Proje genelinde artık hiçbir yerde tanımsız `--ax-primary` kalmadı.
  22. [x] **(25 Ekim 2026 düzeltildi)** `svm.py:34-36` — n>5000'de beklenen
      stratified örnekleme aslında düz rastgele idi (`sample()`'da `stratify`
      yok); ayrıca hem karar_agaci hem svm'de class imbalance uyarısı hiç
      yoktu. **Düzeltme:** `svm.py`'de n>5000 durumunda artık
      `train_test_split(..., stratify=...)` ile sınıf oranlarını koruyan
      örnekleme yapılıyor (nadir sınıf stratified'ı imkansız kılarsa düz
      rastgele örneklemeye düşülüyor, `try/except`); örnekleme sonrası sınıf
      sayısı yeniden hesaplanıyor. Her iki dosyaya da (`svm.py`,
      `karar_agaci.py`) sınıf dengesizliği oranı (en büyük/en küçük sınıf)
      hesabı eklendi; oran ≥3 olunca ekranda (`alert-warning`) ve PDF'te
      turuncu uyarı metni gösteriliyor — "Doğruluk tek başına yanıltıcı
      olabilir, precision/recall/F1'e de bakın." EN/DE çevirileri eklendi,
      Docker'da stratified örnekleme oran koruması + dengeli/dengesiz veri
      senaryoları + PDF üretimi test edildi, 104/104 pytest yeşil.
  23. [x] **(25 Ekim 2026 düzeltildi)** `cronbach.py:58` — 2 maddelik
      ölçekte "madde silinince alfa" hesabı ZeroDivisionError ile
      çöküyordu (k2=1 olunca Spearman-Brown düzeltme katsayısı
      `k2/(k2-1)` = `1/0`; genel except belirsiz hata mesajı veriyordu).
      **Düzeltme:** `k2 < 2` (2 maddelik ölçekte kaçınılmaz) veya `tv2 <= 0`
      durumunda `alpha_if_deleted` artık `None` dönüyor (önceki `float('nan')`
      sentinel'i JSON'da geçersiz `NaN` token'ı üretip polling response'unu
      sessizce bozabilirdi — bu potansiyel ikinci hata da önlendi); PDF
      tablosu `None` için `'—'` gösteriyor. Ekranda bu alan zaten
      gösterilmiyor (yalnız PDF'te var), JS değişikliği gerekmedi. Docker'da
      2 maddelik (çökme yok, `None` + JSON serialize + PDF OK) ve 4 maddelik
      (regresyon yok) senaryolar test edildi, 104/104 pytest yeşil.
  24. [x] **(25 Ekim 2026 düzeltildi)** `ki_kare.py` — Beklenen frekans
      düşük 2×2 durumlarda bile ana sonuç/APA cümlesi her zaman ki-kare
      p-değerine dayanıyordu, Fisher sonucu ayrıca gösterilse de
      öncelenmiyordu — oysa `seo_content.py` (intro + FAQ) zaten "küçük
      örneklemlerde Fisher's Exact Test otomatik devreye girer... Analizus
      bunu otomatik kontrol eder" diye vaat ediyordu. **Düzeltme:** 2×2 +
      en az 1 hücrede beklenen frekans <5 olunca `fisher_is_primary=True`
      hesaplanıyor; `is_significant`, `conclusion` (PDF) ve APA cümlesi
      (hem PDF hem ekran JS, ortak msgid) artık bu durumda ki-kare yerine
      Fisher p-değerine dayanıyor — ham ki-kare/Fisher değerleri tabloda
      hâlâ ayrı ayrı görünüyor, yalnızca "nihai karar" değişti. Gerçek bir
      ayrışma senaryosuyla (`[[0,2],[6,0]]`: ki-kare p=.059 "anlamsız" vs
      Fisher p=.036 "anlamlı") doğrulandı — düzeltme öncesi bu durumda
      yanlış sonuç raporlanıyordu. EN/DE çevirileri eklendi, Docker'da
      düşük/normal frekans senaryoları + PDF üretimi + render test edildi,
      104/104 pytest yeşil.
  25. [x] **(25 Ekim 2026 düzeltildi)** `requirements.txt` — `scipy` sürümü
      sabitlenmemişti; mann_whitney/kruskal_wallis/wilcoxon/friedman
      doğrudan `scipy.stats`'a bağlı (CLAUDE.md kuralı: API'ye doğrudan
      bağlı paketler sabitlenmeli). **Düzeltme:** çalışan Docker imajındaki
      mevcut/test edilmiş sürüme (`scipy==1.17.1`) sabitlendi, kısa açıklama
      yorumu eklendi (`bibtexparser==1.4.4`/`anthropic==1.13.0` ile aynı
      desen). **DEPLOY NOTU:** bu `requirements.txt` değişikliği `main`'e
      push sonrası otomatik akışa yansımaz, Hetzner'de elle `--build`
      gerekir. **Not (ayrı, çözülmedi — todo'ya eklendi):** `numpy`/
      `pandas`/`scikit-learn`/`statsmodels` de istatistik araçlarının
      birçoğunda doğrudan kullanılıyor ama bu maddenin kapsamı (yalnız
      scipy) dışında bırakıldı, sabitlenmedi.
  25b. [x] **(25 Ekim 2026 düzeltildi)** `requirements.txt` — `numpy`,
      `pandas`, `scikit-learn`, `statsmodels` de madde 25'teki scipy ile
      aynı gerekçeyle (istatistik araçlarının API'sine doğrudan bağlı)
      sabitlenmemişti. **Düzeltme:** çalışan Docker imajındaki test
      edilmiş sürümlere sabitlendi: `numpy==2.4.6`, `pandas==3.1.0`,
      `scikit-learn==1.9.1`, `statsmodels==0.15.0` — her birine hangi
      araçların bağlı olduğunu belirten kısa yorum eklendi. **DEPLOY
      NOTU:** madde 25 gibi, `main`'e push sonrası otomatik akışa
      yansımaz, Hetzner'de elle `--build` gerekir. 104/104 pytest yeşil.

---

**İstatistik Araçları Denetimi (25 Ekim 2026) — TAMAMLANDI.** 25 ana
madde + 4 ek bulgu (17b/18b/21b/25b) hepsi düzeltildi, `dev`'e commit+push
edildi. Geriye yalnız ayrı/büyük kapsamlı notlar kaldı: "DÜŞÜK" toplu not
(küçük tutarsızlıklar) ve "TASARIM (ax- sistemi)" — bkz. aşağıdaki ilgili
başlıklar (Bootstrap Kaldırma Migrasyonu'na bağlı, ayrı iş).

  **DÜŞÜK — TAMAMLANDI (26 Ekim 2026).** Hepsi düzeltildi, EN/DE çevirileri
  eklendi, Docker'da test edildi, 104/104 pytest yeşil:
  - [x] `ttesti.py` — bağımsız örneklem CI formülü (`se_diff`) her zaman
    unpooled (Welch) varyans kullanıyordu, pooled t-istatistiğiyle tutarsızdı
    → artık `used_welch`'e göre pooled/unpooled SE seçiliyor; `diff/t_stat`
    ile `(CI genişliği/2)/implied_SE` oranının t-kritik değerine eşit çıktığı
    doğrulandı.
  - [x] `anova.py` — anlamsız sonuçta F değerini "—" yazıyordu (hesaplı
    olmasına rağmen) → `_conclusion()`'a gerçek `f_stat` geçiriliyor.
  - [x] `afa.py` — eğik (promax/oblimin) rotasyonda varyans tablosu
    ortogonal mantığıyla raporlanıyordu, hiç uyarı yoktu → `oblique_variance_note`
    eklendi (ekran + PDF, yalnız promax/oblimin'de görünüyor). KMO terimi
    tutarsızlığı (`afa.html` tablosu "Zayıf" diyordu, kod `_interpret_kmo()`
    "Düşük" döndürüyordu) → tabloya `_interpret_kmo()` ile birebir aynı
    "Düşük" yazıldı.
  - [x] `korelasyon.html` — Kendall açıklaması iki yerde farklı (ve biri
    istatistiksel olarak anlamsız: "çok sayıda eşik") terim kullanıyordu →
    doğru terim "bağlı (eşit) gözlem" (tied observations) ile her iki yerde
    de tutarlı hale getirildi.
  - [x] `kruskal_wallis` — 2 grupla da çalışmaya izin veriyordu, Mann-Whitney'e
    yönlendirme yoktu → `two_group_note` eklendi (k=2 olunca ekran+PDF'te
    Mann-Whitney önerisi gösteriliyor, analiz engellenmiyor).
  - [x] `karar_agaci.py` — `export_text(max_depth=5)` hardcoded idi, kullanıcı
    daha derin bir ağaç seçse bile görüntü sessizce 5 seviyede kesiliyordu →
    gerçek `max_depth` parametresi kullanılıyor (zaten var olan ayrı 40 satır
    sınırı güvenlik ağı olarak kalıyor); max_depth=10 ile tree_text'in artık
    daha fazla satır ürettiği doğrulandı.
  - [x] `seo_content.py` — "Essensiyal" yazım hatası → "Esansiyel" (EN/DE
    çevirileri zaten doğruydu, yalnız TR kaynak metin hatalıydı).

  **TASARIM (ax- sistemi) — geniş çaplı, bilinen Bootstrap Kaldırma
  Migrasyonu Faz 3 borcu, yeni/izole hata değil ama envantere eklendi.**
  **(26 Ekim 2026 DÜZELTME — bu envanter 25 Ekim'de hatalıydı, kullanıcı
  sorusu üzerine gerçek dosyalar `class="..."` token bazında kontrol
  edildi, raw substring arama `ax-btn` gibi isimlerde yanlış pozitif/
  negatif veriyordu):**
  - **ax- sistemine HİÇ geçmemiş (gerçekten doğrulandı, 8 dosya):**
    `orneklem.html`, `ki_kare.html`, `mann_whitney.html`,
    `kruskal_wallis.html`, `lineer_regresyon.html`, `lojistik_regresyon.html`,
    `karar_agaci.html`, `svm.html` — her birinde yalnızca ~8 `ax-` sınıfına
    karşılık 59-79 ham Bootstrap bileşen sınıfı (`btn` 7-11, `card` 2,
    `badge` 0-1, `alert` 1-5, `form-select` 1-3, `table-dark` 1-3,
    `text-white`/`text-white-50` 8-29) + hardcode hex/rgba renkler.
  - **Önceki envanterde "hiç geçmemiş" denilen ama ASLINDA ZATEN GEÇMİŞ
    olduğu doğrulanan 3 dosya (düzeltme):** `ttesti.html` (118 ax- sınıfı),
    `anova.html` (135 ax- sınıfı), `tekrarli_anova.html` (139 ax- sınıfı)
    — bunlarda kalan Bootstrap sınıfları yalnızca izin verilen grid/utility
    türünden (`d-flex`, `d-none`, `row`, `container` — CLAUDE.md'nin
    "Bootstrap yalnızca grid" kuralına uygun), UI bileşenleri (`btn`/`card`/
    `badge`/`alert`) zaten `ax-` prefix'li. Bu üçü migrasyon kapsamından
    çıkarılabilir.
  - **Büyük ölçüde ax-'e geçmiş (doğrulandı, 5 dosya):** `korelasyon.html`
    (141 ax-), `cronbach.html` (124 ax-), `afa.html` (155 ax-),
    `wilcoxon.html` (123 ax-), `friedman.html` (137 ax-) — kalan Bootstrap
    sınıfları da yalnızca grid/utility türünden (~23-29 adet, `d-flex`/
    `d-none`/`row`/`container`), gerçek migrasyon sorunu yok.
  - **Sonuç: gerçek migrasyon işi yalnız 8 dosyada kalmış** (önceki
    envanterdeki 11 değil), bu 8'i Bootstrap Kaldırma Migrasyonu Faz 3'ün
    güncel hedef listesi olarak kullan. **Çapraz kontrol:** aşağıdaki
    "Bootstrap Kaldırma — Kademeli Migration Planı" başlığının "Güncel
    envanter (11 Ekim 2026 taraması)" bölümü bu 8 dosyayı zaten doğru
    şekilde "Orta (10-20 class)" grubunda listeliyor — bugünkü bağımsız
    doğrulama o envanterle birebir örtüşüyor, 25 Ekim denetiminin kendi
    notu (bu bölümün başı) ise hatalıydı.

  **Düzeltme sırası kullanıcı onayına bağlı** — CLAUDE.md kırmızı çizgisi
  gereği hiçbir madde otomatik uygulanmadı; kullanıcı hangilerini
  önceliklendireceğini seçtikten sonra değişecek dosyalar listelenip onay
  alınacak, sonra tek tek uygulanacak.

- [ ] **(22 Ekim 2026) `onboarding.html` ax- tasarım sistemine aykırı:**
  Bootstrap UI bileşenleri (`card`, `btn btn-primary/outline-secondary/
  success/link`, `text-muted`, `text-danger`) doğrudan kullanılıyor
  (olması gereken `ax-` prefix'li sınıflar) + CSS bloğunda hardcode hex
  renkler (`#f0f0ff`, `#6366f1`, `#eef2ff`, `#4f46e5`, `#1e293b`,
  `var(--text-main, #e2e8f0)` fallback'i) `var(--ax-*)` değişkeni yerine
  yazılmış. Düzeltme: dosyayı ax sistemine taşımadan önce mevcut `ax-`
  sınıf/değişken karşılıklarını (`bundle.css`) kontrol et, JS'teki
  `.segment-card`/`.selected` davranışını bozma.

- [ ] **(22 Ekim 2026) Güvenlik taraması — bulgular (CVE-2026-109618/109619
  PHP duyurusu vesilesiyle istendi; proje PHP değil, Django — sunucuda PHP
  olmadığı SSH ile teyit edildi, bu iki CVE geçersiz).** pip-audit +
  `manage.py check --deploy` + trivy (base imajlar + uygulama imajı) +
  OWASP kod taraması (subagent) yapıldı. Bulgular şiddet sırasına göre:
  1) **[x] Docker imajına sızan gizli dosyalar — DÜZELTİLDİ:**
     `.dockerignore` eksikti, `COPY . .` ile production imajına
     `cookies.txt` (450KB, hosting paneli gerçek oturum çerezi +
     scraping araçları çerezleri), `frontend/` (git'te izlenmeyen/yerel
     Next.js denemesi, `node_modules` içinde Next.js 16.1.5 — kimlik
     doğrulamasız RCE CVE-2026-75604 CRITICAL) ve
     `nginx/local-ssl/selfsigned.key` (private key) giriyordu.
     `.dockerignore`'a `frontend/`, `cookies.txt`, `youtube_cookies.txt`,
     `nginx/local-ssl/` eklendi, imaj yeniden build edildi.
     **Kullanıcı tarafı TAMAMLANDI (22 Ekim 2026):** hosting paneli ve
     Gmail şifreleri değiştirildi; EBSCO hesabı zaten kullanılmıyor,
     gerek görülmedi.
  2) **[x] Stored XSS — blog yazıları — DÜZELTİLDİ (22 Ekim 2026):**
     (`forum/templatetags/markdown_extras.py`) `markdown` filtresi artık
     `md.markdown()` çıktısını `bleach.clean()` ile (izinli etiket/öznitelik
     listesi, yalnız http/https/mailto link şeması, `strip=True`) temizledikten
     sonra `mark_safe()` yapıyor. `bleach` requirements.txt'e eklendi.
     Test: `<script>`/`onerror` payload'ı temizlendi, başlık/kalın/italik/
     liste/kod bloğu (codehilite)/tablo/link normal render oldu; 103/103
     pytest yeşil. **Deploy notu:** requirements.txt değişti, deploy
     öncesi `--build` gerekir (otomatik akışa yansımaz).
  3) **[x] IDOR — istatistik analiz sonuçları — DÜZELTİLDİ (22 Ekim 2026):**
     (`istatistik/views.py`, `job_status` + iki job-oluşturma noktası)
     anonim (demo) job'lar artık `request.session['demo_job_ids']`
     listesiyle eşleştiriliyor (migration gerekmedi — mevcut DB-backed
     session kullanıldı); giriş yapmış kullanıcı job'ları `user_id`
     eşleşmesiyle korunuyor, eşleşmeyen her durumda `Http404`. Shell
     testiyle doğrulandı: sahip (anonim + girişli) erişebiliyor, yabancı
     anonim oturum ve başka kullanıcı 404 alıyor; 103/103 pytest yeşil.
  4) **[x] Orta — DM/çalışma odası eki MIME doğrulaması client-controlled
     — DÜZELTİLDİ (22 Ekim 2026):** `AWS_S3_CUSTOM_DOMAIN` teyit edildi:
     `analizus-files.s3.eu-north-1.amazonaws.com` — analizus.com alt alan
     adı DEĞİL, cross-origin, yani CSRF token çalınması senaryosu zaten
     geçersizdi (şiddet Orta'da kaldı, yükselmedi). Gerçek içerik
     doğrulaması (`python-magic`) yeni sistem kütüphanesi + Dockerfile
     değişikliği gerektirdiği için orantısız bulundu; bunun yerine
     `forum/storage.py`'ye `get_attachment_storage()` eklendi
     (`PrivateMessage.attachment`, `StudyRoomPost.file` — yalnız bu iki
     alan, avatar/diğer dosyalar etkilenmedi) — S3'te
     `ContentDisposition: attachment` zorlanıyor, tarayıcı içerik tipi
     ne olursa olsun (sahte olsa dahi) inline render etmiyor, yalnızca
     indiriyor. Migration `0185` (state-only `AlterField`, DB şeması
     değişmedi) uygulandı. Doğrulama: `override_settings` ile storage
     nesnesinin `object_parameters` değeri kontrol edildi (gerçek S3'e
     dosya yazmadan — prod/dev S3 bucket paylaşımlı, test verisi
     bulaştırılmadı), 103/103 pytest yeşil.
  5) **[x] `pillow` 12.3.0 → 13.0.0 — DÜZELTİLDİ** (CVE-2026-112393,
     trivy'den; bleach ile aynı `--build` sırasında requirements.txt'teki
     sürümsüz `Pillow` zaten güncel sürümü çekti, production'da canlı).
  6) **[x] Düşük — `api_submit_quiz_answer` gerekçesiz `@csrf_exempt` —
     DÜZELTİLDİ (22 Ekim 2026):** Decorator kaldırıldı (`forum/views.py`);
     frontend (`templates/base.html`) zaten `X-CSRFToken` header'ı
     gönderiyordu, JS değişikliği gerekmedi. Yeni regresyon testi
     eklendi (`test_quiz_answer_requires_csrf_token`, `forum/tests.py`):
     token'sız POST 403, doğru token'lı POST 200 — 104/104 pytest yeşil.
  7) **[x] Düşük — `oaipmh` scraper'da `verify=False` — İNCELENDİ,
     KASITLI OLARAK BIRAKILDI (22 Ekim 2026):** git geçmişi (`91186f1`,
     19 Şubat 2026) bunun gözden kaçma değil, bilinçli bir düzeltme
     olduğunu gösterdi — Ordu Üniversitesi gibi bozuk SSL sertifikalı
     üniversitelerin OAI-PMH bağlantısı bu olmadan başarısız oluyordu.
     Düz `verify=True`'ya çevirmek o zaman çözülen sorunu geri getirir.
     Risk zaten düşük/düşük-güvenilirlik (4/10) olarak işaretliydi —
     kullanıcı kararıyla olduğu gibi bırakıldı. "Doğru" çözüm
     (üniversite bazlı opt-out: yeni model alanı + migration + admin +
     hangi üniversitelerin gerçekten sorunlu olduğunu tespit etmek)
     orantısız bulundu, istenirse ayrı görev.
  SQL injection, SSRF, command injection, insecure deserialization,
  kullanıcı tetikleyebileceği XXE, diğer IDOR'lar (DM, oda, 6 tarama
  aracı, pazar, profil), hardcoded secret — temiz, sağlam sahiplik
  kontrolleri doğrulandı. **22 Ekim 2026 güvenlik turu TAMAMLANDI** —
  7 bulgunun 6'sı düzeltildi ve production'da canlı, 1'i (oaipmh SSL)
  bilinçli olarak mevcut haliyle bırakıldı.

- [ ] **(21 Ekim 2026) Bootstrap Kaldırma Migrasyonu — bu TEK LİSTE'de hiç
  yoktu, eklendi (kullanıcı talebiyle).** Bugünkü ana sayfa CLS/performans
  turunda Lighthouse "`bootstrap.min.css`'in %92'si kullanılmıyor (30,5 KiB)"
  bulgusu çıktı; CDN'den tam Bootstrap yerine yalnızca grid içeren bir
  sürüme geçmek cazip göründü ama site geneli tarama bunun **güvenli
  olmadığını** doğruladı — `btn` 464, `card` 184, `badge` 150, `accordion`
  146, `form-control` 49 kez gerçek (ax- önekisiz) Bootstrap bileşen
  class'ı olarak hâlâ kullanılıyor (migrasyon henüz tamamlanmadığı için).
  Dolayısıyla bugün dokunulmadı. Ayrıntılı envanter + faz planı aşağıda
  "Bootstrap Kaldırma — Kademeli Migration Planı" başlığında (12 Ekim 2026
  durumu: Faz 1-2 tamam, Faz 3 sürüyor, 55 dosyada ~760 component class
  kaldı) — bu maddenin amacı yalnızca onu TEK LİSTE'ye bağlamak, plan
  kendi başlığında devam ediyor.

- [x] **(19 Ekim 2026) EN/DE için ayrı pazaryeri — TR'den tamamen ayrı
  havuz, kriter yok, haftalık 1 ücretsiz + bağışla yükselen limit —
  UYGULANDI (dev'de), henüz canlıya alınmadı.** Üç paralel araştırma +
  bir tasarım ajanıyla kod tabanı taranıp plan onaylandı (plan dosyası:
  `quizzical-crunching-eagle.md`), sonra sırayla uygulandı. Kararlar:
  EN+DE tek ortak "intl" havuzda birleşiyor (ayrı iki pazar değil);
  fazladan ilan hakkı mevcut bağış→Premium mekanizmasıyla otomatik
  işliyor (yeni mekanizma icat edilmedi, yalnız yeni limit sayıları
  eklendi); teklif vermek (bidding) intl ilanlarda yalnız `is_staff`
  kullanıcılara açık (kullanıcı kararı: "kim görüp teklif verecek...
  sadece admin yetkisine sahip olanlara açık olsun"). **Değişiklik
  özeti:** `FreelanceJob.language` alanı (migration `0183`, varsayılan
  `tr`, mevcut kayıtlar etkilenmez) + `FreelanceJob.in_market_scope()`;
  `SiteSettings.feature_market_intl` + `job_weekly_limit_intl_free/
  premium` (varsayılan 1/3, admin'den değiştirilebilir); `Profile.
  get_weekly_job_limit/get_weekly_job_count/can_post_job_now` artık
  `scope='tr'|'intl'` parametresi alıyor (referans bonusu yalnız TR'de);
  `JobProposal.can_propose_for_job()` intl ilanlarda `is_staff` kontrolü
  yapıyor; `forum/views.py`'de `market_scope()`/`get_job_or_404_for_scope()`
  helper'ları tüm pk'li market view'larını (job_list, post_job,
  job_detail, toggle_like/bookmark, close/edit/accept_proposal,
  admin_manage_proposal, add_job_review) kapsam bazlı 404'e bağlıyor —
  normal kullanıcı pk tahminiyle bile karşı kapsama (TR↔intl) giremiyor,
  staff/superuser her ikisini de görebiliyor; `my_jobs`/`promote_job`/
  `mark_payment_transferred` bilinçli olarak dokunulmadı (zaten
  `owner=request.user` filtreli, sızıntı riski yok). Navbar/footer/
  `proje_talebi.html` linkleri TR→`features.market`, EN/DE→
  `features.market_intl` ikili yapıya ayrıldı; `home_intl.html`'e yeni
  pazaryeri CTA'sı eklendi. **Gerçek bug bulundu ve düzeltildi:**
  `job_list.html`'deki "Uzmanlarla Tanış" → `uzman_dizini` linki
  (bu URL hiç çevrilmedi, i18n_patterns dışında) EN/DE'de de
  render ediliyordu, kırık link veriyordu — artık TR-only.
  `job_detail.html`'deki "Nasıl Yetki Kazanılır? (1000+ puan kazan...)"
  ipucu kutusu intl ilanlarda yanlış/alakasız olduğu için TR-only yapıldı.
  Admin: `FreelanceJobAdmin`/`JobProposalAdmin`'e `language` filtresi,
  `SiteSettingsAdmin`'e yeni flag+limit alanları (3 nokta kuralı
  uygulandı: model + `feature_flags()` context processor + fieldsets).
  SEO: `JobSitemap` artık yalnız `language='tr'` filtreli (önceden
  filtresizdi, şans eseri sorun çıkmamıştı), yeni `JobIntlSitemap`
  eklendi (`ServicePageTranslatedSitemap` deseniyle); `robots.txt`'te
  değişiklik gerekmedi (EN/DE action-endpoint disallow'ları zaten vardı).
  **13 yeni pytest testi** eklendi (`forum/tests.py`), toplam 103/103
  yeşil (`docker compose exec web python -m pytest forum/tests.py`).
  Manuel doğrulama (gerçek request/response ile): ortak havuz görünürlüğü,
  çapraz kapsam 404'ü (iki yönde), staff bypass, teklif formu gizleme —
  hepsi beklenen gibi çalıştı. **Henüz yapılmayanlar / canlıya almadan
  önce:** (1) yeni EN/DE metinleri (`gettext`/`{% trans %}` ile
  işaretlendi ama) `locale/en|de/LC_MESSAGES/django.po`'ya henüz
  çevrilmedi — `makemessages`+çeviri+`compilemessages` ayrı bir tur
  gerekir; (2) `job_weekly_limit_intl_premium` varsayılanı (3) kullanıcı
  tarafından teyit edilmedi, admin'den değiştirilebilir; (3) bütçe alanı
  hâlâ yalnızca TL (₺ sembolü şablonlarda sabit) — mevcut tasarımda
  bilinçli olarak korundu, istenirse ayrı görev; (4) **"Go-live" adımı
  kullanıcıya ait**: admin panelinden `feature_market_intl`'i açmak —
  henüz açılmadı, hiçbir EN/DE kullanıcısına görünmüyor. Migration
  yalnızca lokalde uygulandı; `main`'e push öncesi `scripts/
  yedek_indir.sh --simdi` (kullanıcının kendi bilgisayarında) istenmeli.

- [x] **(18 Ekim 2026) Admin dashboard — İlan Onayı tek-tık onay/red.**
  Şikayet: bildirimdeki "Onayla / Reddet →" linki Django'nun standart
  değiştirme formuna gidiyordu, orada buton olmadığı için kullanıcı tekrar
  İş İlanları listesine dönüp checkbox + action seçmek zorunda kalıyordu
  (3 adım). Çözüm: `JobPaymentAdmin`'deki mevcut tek-tık onay deseni
  (`get_urls()` + özel view + `confirm()` dialoglu link) `FreelanceJobAdmin`'e
  de uygulandı — `forum/admin.py` `quick_approve_view`/`quick_reject_view`
  (3 ret sebebi: service_ad/incomplete/rules), `templates/admin/index.html`
  İlan Onayı satırı artık "Onayla →" + 3 ayrı "Reddet: ..." linki + nadir
  durumlar için "Detaylı →" (changeform) içeriyor. Test client ile
  onay/red/geçersiz-sebep-guard'ı doğrulandı, `forum/tests.py` 90/90 yeşil.
  Migration yok. **Henüz push edilmedi**, kullanıcı onayı bekleniyor.
- [x] **(18 Ekim 2026) EN/DE pazaryeri sızıntısı — kalıntı link düzeltmesi
  UYGULANDI, doğrulanmadı + 2 açık karar kaldı.** Kaynak: bir admin "Navigasyon
  Grafiği" kaydında EN'de login olan bir kullanıcının onboarding sonrası
  `/en/market/` ve `/en/market/job/191/`'i ziyaret ettiği görüldü (16 Ekim
  turunda navbar/footer/home'dan kaldırılmıştı ama URL hâlâ tamamen açık).
  Kod incelemesi: `job_list`/`job_detail` view/URL seviyesinde hiçbir dil
  kısıtlaması yok (yalnız navigasyon gizlenmiş); `PageView` referrer/UTM
  tutmadığı için kullanıcının oraya nasıl geldiği (URL'i elle yazdı mı,
  daha önce TR'de görüp dil değiştirip path korundu mu) kesin tespit
  edilemedi. **Bulunup düzeltilen (bu oturumda, onaylandı):**
  `openalex/templates/openalex/landing.html:31` ("Premium üyelik" →
  `job_list` linki, dil koşulsuzdu) ve `forum/templates/forum/
  profile_detail.html` 3 nokta (satır ~378 portföy kartı, ~445 "İlanlar",
  ~498 "Verdiğim Teklifler" — `job_detail` linkleri dil koşulsuzdu) artık
  EN/DE'de ya tıklanamaz (`href`siz) ya da düz `<div>`. **Doğrulandı (18
  Ekim 2026):** `docker compose restart web`+`nginx` sonrası `curl` ile
  openalex landing'de TR'de "Premium üyelik" var/EN-DE'de `job_list`
  referansı yok; `profile_detail.html`'de geçici test ilanı (`FreelanceJob`,
  sonra silindi) ile TR'de `job_detail` href=1, EN/DE'de href=0 doğrulandı;
  portföy kartı mantığı izole template render testiyle (EN+in_progress→
  `<div>`, TR+in_progress→`<a href>`) doğrulandı, syntax hatası yok, her
  dilde sayfa 200 dönüyor. **Bilinen kozmetik
  tutarsızlık (kullanıcı kararıyla ERTELENDİ):** "İlanlar"/"Verdiğim
  Teklifler" satırlarında `.ax-profile-job-item:hover` CSS kuralı `href`
  olmasa da hâlâ tetikleniyor (kenarlık/arka plan rengi değişiyor) —
  tıklanamaz olduğu halde tıklanabilir görünüyor; düzeltilmedi, kullanıcı
  "kalsın" dedi. **Karar (18 Ekim 2026, kullanıcı):** `/market/` ve
  `/market/job/<id>/` URL'lerine EN/DE'de route seviyesinde dokunulmayacak
  — "sadece navigasyondan gizli" mevcut durum yeterli kabul edildi, kod
  değişikliği yapılmadı (dil değiştiricinin aynı path'i koruyarak
  `/en/market/...`'e taşıması da bu kararın kapsamında — ayrı bir kod yolu
  değil, zaten açık olan URL'e farklı bir giriş; tutarlılık için ayrıca
  engellenmedi). **TAMAMLANDI (18 Ekim 2026):** `PageView`'a `referrer`
  alanı eklendi (`analytics/models.py`, migration
  `0003_pageview_referrer`, `analytics/middleware.py`'de `HTTP_REFERER`
  yakalanıyor, `analytics/admin.py` changelist'te görünür). Yerelde
  migration uygulandı, referrer yakalama canlı test client ile doğrulandı,
  `forum/tests.py` 90/90 yeşil. **Migration dosyası container'da root
  sahipli oluştu, `docker compose exec -u root` ile `chown 1000:1000`
  yapılarak düzeltildi** (bilinen §26 sorunu). **Henüz yapılmadı: `dev`'e
  commit + push ve production'a (`main`) migration'lı deploy** — kullanıcı
  push isteğinde bulunmadı, bekleniyor. Push öncesi `scripts/yedek_indir.sh
  --simdi` hatırlatması geçerli (migration içeriyor).
- [ ] **(16 Ekim 2026) EN/DE Ana Sayfa — Danışmanlık Dönüşümü: 11 adımlı plan
  hazır, henüz hiçbir adıma başlanmadı.** Kaynak: proje kökündeki
  `en_de_danismanlik_donusumu_prompt.md` (ayrı bir dosya, tasks/todo.md'de
  değil — buraya yalnız özet + doğrulama notu). Plan: Adım 1 pazaryeri/forum
  sızıntılarını (`forum/home.html` "Uzman Vitrini" + "Gündemdeki Tartışmalar"
  + sayaç şeridi kalemleri) EN/DE'de gizle (karar zaten §28.7'de var, onay
  gerekmiyor) → Adım 2 geçici msgstr düzeltmeleri (yanlış vaatler: "dakikalar
  içinde", "%100 gizlilik", "doğrulanmış uzman" vb.) → Adım 3 renk/kontrast
  (TR'yi de etkiler) → Adım 4 SEO title/description + SSS H2→H3 → Adım 5
  Premium/bağış bloğunu EN/DE'de gizleme kararı (K8) → **Adım 6 (asıl iş,
  migration'lı): yeni `home_intl.html` + `feature_intl_consulting_home`
  flag'i ile danışmanlık odaklı EN/DE ana sayfası** → Adım 7 EN/DE navigasyon
  → Adım 8 Impressum (DE) → Adım 9 EN/DE hizmet sayfaları (yalnız tasarım
  dokümanı, kod yok) → Adım 10 proje talebi formuna ön görüşme alanları
  (migration) → Adım 11 ölçüm sorgusu. Adım 6 öncesi 9 açık kullanıcı kararı
  var (K1–K9, plan dosyası §3): kim/hangi dilde danışmanlık verecek, Impressum
  bilgileri, fiyat modeli, yanıt süresi taahhüdü, veri işleme/KVKK, eğitimler,
  dropzone'un kalkıp kalkmayacağı, Premium'un gizlenip gizlenmeyeceği, sayaç
  kalemlerinden hangisinin kalacağı.
  **Doğrulama turu (16 Ekim) sonucu — plan teknik olarak sağlam, tek gerçek
  eksiklik bulundu:** S3 (sayaç şeridi) tablosu yalnız 5 kalemden bahsediyor
  (Aktif Üye, Akademik Konu, Forum Mesajı, Tamamlanan Proje, Tamamlanan
  Analiz); ama `forum/home.html:581-636`'daki şerit aslında **8 kalemli** —
  eksik 3 kalem: **"Açık İlan"** (`open_jobs_count`, linkli — pazaryerine
  gidiyor olabilir), **"Bu Hafta Yeni Üye"**, **"Şu An Çevrimiçi Uzman"**.
  K9 kararı yalnız "Tamamlanan proje/analiz" için soruluyor; bu üç kalem
  hiç karara bağlanmamış — özellikle "Açık İlan" EN/DE'de pazaryeri kapalı
  kararıyla doğrudan çelişebilir. Adım 1'in genel sızıntı tarama maddesi
  (madde 4) bunu muhtemelen yakalar ama plan metninde açık kör nokta,
  Adım 1'e başlarken ayrıca kontrol edilmeli. Diğer doğrulanan noktalar:
  `--ax-color-primary` gerçekten tanımsız token (`home.html:45,48`, `base.css`
  karşılığı `--ax-accent-primary-light` = `#a5b4fc`); `ProjectRequest.
  SOURCE_CHOICES`'da `home_market`/`home_steps`/`home_faq`/`nav` zaten mevcut
  (plan zaten "önce kontrol et" diyor, sorun değil); feature flag üç-yer
  deseni örnekle doğrulandı.

  **K1–K9 KARARLARI NETLEŞTİ (16 Ekim 2026, kullanıcı):**
  - K1: Analizus admin TR/EN/DE danışmanlığın tamamını verecek.
  - K2: Impressum sayfası (DE) + Legal Notice (EN) hazırlanır ama şirket/kişi
    bilgileri (adres, vergi no vb.) netleşene kadar **footer/nav'a
    linklenmez** — boş/placeholder bilgiyle yayına alınmaz (Almanya'da
    yasal risk).
  - K3: Fiyat sitede/SSS'de gösterilmez; proje talebi sonrası verilecek
    cevapta belirtilir. SSS "Was kostet eine Analyse?" cevabı buna göre
    yazılmalı (sabit rakam yok).
  - K4: Yanıt süresi taahhüdü VAR — "proje büyüklüğüne göre 5-7 gün içinde"
    (gerçek, yazılabilir). Adım 2'deki sahte "24 Stunden" ifadelerinin
    yerine bu geçecek (Premium'un kendi "24 saat" vaadi hariç, o ayrı konu).
  - K5: S3 bucket `eu-north-1` (Stockholm/AB) — koddan doğrulandı
    (`.env: AWS_S3_REGION_NAME=eu-north-1`). Yazılabilir: "Daten werden in
    der EU verarbeitet" / "processed within the EU". **"in Deutschland"
    YAZILAMAZ** — yanlış olur. Hetzner sunucusunun datacenter konumu ayrıca
    doğrulanmadı, "Deutschland" iddiası için bu da teyit gerektirir.
  - K6: Eğitimler yalnız **EN**'de veriliyor, DE'de yok — Adım 7 navigasyonda
    "Training" linki yalnız EN menüsünde, DE menüsünde olmayacak.
  - K7: Hero dropzone (dosya yükle, hemen analiz et) EN/DE'de **kalır**,
    kaldırılmayacak.
  - K8: Premium/bağış bloğu EN/DE'de **gizlenmeyecek** (S7 tespitinin aksine
    kaldırılmıyor); fiyatlar TL yerine **EUR'a çevrilir**, ödeme için
    **ayrı bir EUR IBAN** eklenir. Mevcut TL/IBAN akışının neresinde dil
    bazlı ayrım yapılacağı (muhtemelen `templates/base.html` premium modalı)
    Adım 5'te araştırılmalı; bu artık "gizleme" değil "yerelleştirme" görevi.
  - K9: Sayaç şeridinden **"Açık İlan"**, **"Bu Hafta Yeni Üye"**,
    **"Şu An Çevrimiçi Uzman"** kalemleri EN/DE'de **tamamen kaldırılır**;
    yalnız "Tamamlanan Proje" ve "Tamamlanan Analiz" kalır (`total_users`,
    `total_topics`, `total_posts` zaten S3/Adım 1 kapsamında kaldırılıyordu).

  Not: K8 kararı plan dosyasındaki Adım 5'in varsayımını ("Premium gizlensin
  mi?") değiştiriyor — Adım 5 artık "EUR fiyat + ayrı IBAN" görevine
  dönüşüyor, plan dosyası bu haliyle güncel değil, uygulama sırasında bu
  fark gözetilmeli.

  **ADIM 1 TAMAMLANDI (16 Ekim 2026) — forum/forum/home.html'de EN/DE
  pazaryeri/forum sızıntıları kapatıldı, henüz push edilmedi (dev'de commit
  yok, yalnız working tree'de).** Tek dosya değişti:
  `forum/templates/forum/home.html`, 9 nokta (5 ayrı değişiklik bloğu):
  (1) hero kişiselleştirme "uzman" segment dalına `and LANGUAGE_CODE == 'tr'`
  eklendi (akademisyen dalıyla tutarlı); (2) "Uzman Arayan Projeler" (gerçek
  S1 kaynağı — plan dosyasının işaret ettiği "FAZ 3: UZMAN VİTRİNİ" DEĞİL,
  ondan ayrı, ₺ fiyatlı ilan kartları gösteren bölüm) `and LANGUAGE_CODE ==
  'tr'` ile sarıldı; (3) "Gündemdeki Tartışmalar" (S2) aynı şekilde; (4)
  sayaç şeridinde (S3) 6 kalem (`total_users`, `total_topics`, `total_posts`,
  `open_jobs_count`, `weekly_new_users`, `online_experts`) `and
  LANGUAGE_CODE == 'tr'` ile sarıldı, `completed_jobs`/`completed_analyses`
  dokunulmadan kaldı (K9). "FAZ 3: UZMAN VİTRİNİ" (uzman profil kartları,
  fiyat/ilan içermiyor) ve zaten 16 Ekim akşam düzeltilmiş `home_market`
  kartları kullanıcı kararıyla **değiştirilmedi** (EN/DE'de görünmeye devam
  ediyor).
  **Doğrulama:** `transaction.atomic()` içinde açık bir `FreelanceJob`
  (status='open', approved_at dolu — yeniden yayın tetiklemeden) + bir forum
  `Topic`/`Post` oluşturulup Test Client ile `/`, `/en/`, `/de/` render
  edildi, rollback yapıldı (nesneler DB'de kalmadı, doğrulandı). Sonuç: TR'de
  beklenen içerik (pazaryeri/forum linkleri, "Gündemdeki", "Uzman Arayan
  Projeler") aynen duruyor; **EN ve DE'de sıfır sızıntı** (`/market/`,
  `/forum/`, `/topic/`, "Gündemdeki", "Uzman Arayan Projeler" aramalarının
  hepsi 0). `docker compose exec web python -m pytest forum/tests.py` →
  **90/90 yeşil**, regresyon yok.
  **Deploy etkisi:** migration yok, collectstatic gerekmez, `--build` yok;
  yalnız `docker compose restart web` (zaten yapıldı, lokalde doğrulandı).
  **ADIM 1 commit + push edildi** (`70e363d`, `dev`'e gitti, Render'a
  otomatik deploy tetiklendi).

  **ADIM 2 TAMAMLANDI (16 Ekim 2026) — EN/DE yanlış vaat ifadeleri msgstr
  düzeyinde düzeltildi, henüz commit edilmedi.** İki dosya:
  `locale/de/LC_MESSAGES/django.po`, `locale/en/LC_MESSAGES/django.po`
  (+derlenmiş `.mo`'lar), ayrıca `forum/templates/forum/home.html`'de
  1 ek satır (plan dışı, doğrulama sırasında bulunan gerçek bug). TR hiçbir
  msgid'de değişmedi (yalnız msgstr). 10 msgid düzeltildi: hero H1 ("du"
  → "Sie", "jemanden der es tut" → "von Fachleuten erledigen"), aynı ifadenin
  og/twitter paylaşım başlığı (ek bulgu, plan tablosunda yoktu), hero CTA
  butonu, hero açıklama cümlesi ("in Minuten/verifizierten Experten" →
  "wir finden die passende Fachperson", "100% Vertraulichkeit" → "Vertraulicher
  Umgang... kostenlose Erstbewertung"), "Alanında doğrulanmış uzmanlar" →
  "Fachleute mit Erfahrung", "Şeffaf fiyatlandırma" → "Unverbindliches
  Angebot vor Arbeitsbeginn", AI doğrulama bandındaki "24 Stunden/hours"
  kaldırıldı, hero alt başlığı + footer tagline'daki "verifizierte
  Experten/verified experts" → "Fachleute/specialists".
  **Doğrulama sırasında bulunan gerçek bug:** `home.html:772`'de
  `AI {% trans "Asistan" %}` — "AI" kelimesi şablonda SABİT yazılmış,
  yalnız "Asistan" çevriliyordu → DE'de "AI Assistent" (karışık dil)
  çıkıyordu. `{% trans "AI Asistan" %}` olarak düzeltildi (zaten doğru
  çevrilen mevcut msgid'i kullanıyor, TR'de görünüm value'su aynı kaldı).
  **Dokunulmadan bırakılan (plan kapsamı dışı, Adım 6'ya ait):**
  "So arbeiten wir" (Nasıl Çalışıyoruz) adımlarındaki "Verifizierte
  Analysten unterbreiten Methodik- und Preisangebote" (S4) — bu bölüm
  Adım 6'da baştan yazılacak süreç adımlarıyla değişecek.
  **Doğrulama:** `docker compose exec web python manage.py compilemessages`
  container'da msgfmt bulunamadığı için host'ta `msgfmt -c -o ...` ile
  derlendi (hata yok, yalnız bilinen header uyarıları). `docker compose
  restart web` sonrası canlı (lokal) `/`, `/en/`, `/de/` curl ile kontrol
  edildi: DE/EN'de hedeflenen ifadelerin (in Minuten/in minutes,
  verifizierte Experten/verified experts, Expert/innen, findest du,
  AI Assistent) **hepsi 0**; "24 Stunden"/"24 hours" **tam olarak 2**
  (yalnız Premium, beklenen); TR'de "Analizini yap.", "Yapamıyorsan, yapan
  burada.", "24 saatte", "AI Asistan" **hiç değişmedi**. `pytest
  forum/tests.py` → **90/90 yeşil** (home.html'e ikinci dokunuştan sonra
  tekrar çalıştırıldı).
  **Deploy etkisi:** migration yok, collectstatic gerekmez. `docker-compose.
  yml`'de `.:/app` bind-mount var (`Dockerfile` yalnız build anında `COPY . .`
  yapıyor) — yani `git pull` + `restart web` host dosyalarını (dolayısıyla
  `.mo`'ları) doğrudan container'a yansıtır, tıpkı şablon değişikliğinde
  olduğu gibi; `--build` gerekmiyor. GitHub Actions zaten `main`'e push'ta
  bu akışı otomatik çalıştırıyor.
  **ADIM 2 commit + push edildi** (`3a0c108`, `dev`'e gitti).

  **ADIM 3 TAMAMLANDI (16 Ekim 2026) — renk/kontrast düzeltmeleri, henüz
  commit edilmedi.** TR'yi de etkileyen tek adım (dile göre ayrılmamış CSS
  kuralları). 3 dosya, 11 nokta: `forum/templates/forum/home.html` (inline
  kritik CSS, 4 satır), `static/css/hero.css` (5 satır), `static/css/
  home_sections.css` (2 satır).
  (1) Tanımsız `--ax-color-primary` token'ı (`home.html:45,48` +
  `hero.css` aynı kuralların tam kopyası) → `--ax-accent-primary-light`
  (#a5b4fc, gerçek değer hesaplandı: 9.61:1/8.90:1 — plan dosyasının
  tahmin ettiği #818cf8/6.42:1'den bile iyi).
  (2) Koyu zeminde düşük kontrastlı linkler ("Alle 18 Tools →",
  "Ya da bu işi bir uzmana bırak" hover) → aynı token, 4.29/3.97:1'den
  9.61/8.90:1'e çıktı.
  (3) "oder analysieren Sie selbst:" (`.ax-hero__or`, yalnız `hero.css`'te
  tek kopya) `--ax-text-muted` → `--ax-text-secondary` (4.02→7.47:1).
  (4) **Ek bulgu (plan metninde yoktu):** "oder machen Sie es selbst →" ve
  yanındaki Cronbach/Normallik/Betimsel/Hangi Test linkleri
  (`.ax-market-diy__label/__link`, `home_sections.css:206-215`) token bile
  kullanmıyordu, hardcode `rgba(148,163,184,0.5/0.7)` idi — ölçülen gerçek
  kontrast **2.68:1 ve 4.04:1** (plandaki tahminden kötü) → `var(--ax-
  text-secondary)` solid yapıldı, **6.92:1**'e çıktı.
  **Test edildi, değişiklik GEREKMEDİ:** `.ax-market-visual` kırpılması —
  Playwright ile 1024/1280/1440px ölçüldü (ilk ölçümde yanlış elementi
  seçmişim — sayfada aynı class'tan iki tane var, demand+supply kartları;
  düzeltip doğru elemanı ölçtüm), üç genişlikte de tutarlı ~15px
  (CSS'teki `right:-16px` tasarım değeriyle birebir), ekran görüntüsü
  temiz — sorun yok.
  **Yalnız listelendi, uygulanmadı (ayrı onay gerekir):** `#fbbf24`
  (artık TR'ye özel "Uzman Arayan Projeler" başlığı), `#f97316`
  (`trend_topics.css`, forum başlığı, artık TR'ye özel), `#a855f7`,
  `#818cf8` ×3 (decoratif SVG/gradient) — `#818cf8` tam olarak
  `--ax-accent-primary-hover`'a eşit (tokenize edilebilir), diğerlerine
  (amber/turuncu/mor) base.css'te karşılık gelen bir token yok, yeni
  token eklemeden dokunulmadı.
  **Kapsam dışı (ayrı not):** global `.ax-btn--primary` beyaz-üzeri-indigo
  kontrastı (4.47:1, sınırda) — tüm siteyi etkiler, bu turun dışında.
  **Doğrulama:** `docker compose restart web`; Playwright ile TR/EN/DE ×
  1280px render edilen `getComputedStyle().color` değerleri doğrulandı
  (hepsi beklenen yeni token rengine döndü, üç dilde birebir aynı); TR/DE
  hero ekran görüntüsü karşılaştırıldı (TR değişmemiş, DE okunaklı ve
  tutarlı "Sie" hitabı). `pytest forum/tests.py` → **90/90 yeşil**.
  **Deploy etkisi:** migration yok; CSS dosyaları (`hero.css`,
  `home_sections.css`) değişti — `collectstatic` ileride hash'li adla
  yeniden üretecek ama bind-mount sayesinde `restart web` yeterli (Adım
  2'deki gibi), `--build` gerekmiyor.
  **ADIM 3 commit + push edildi** (`4519fa4`, `dev`'e gitti).

  **ADIM 4 TAMAMLANDI (16 Ekim 2026) — SEO title/description + SSS H2→H3
  + KRİTİK EK BULGU düzeltmesi, henüz commit edilmedi.**
  (1) `home.html`'in `{% block title %}`/`{% block meta_description %}`
  msgid'leri bulundu (tek kullanım, satır 6-7). Planın önerdiği DE/EN
  metinleri kendi belirlediği sınırı (title ≤60-65, desc ≤155-160) aşıyordu
  (73-75/182-189 karakter) — kısaltılıp kullanıcıya gösterildi, onaylandı:
  DE title "Statistikberatung für Forschung & Unternehmen \| Analizus" (56),
  EN title "Statistics Consulting for Research & Business \| Analizus" (56),
  DE/EN description sırasıyla 135/148 karakter. TR değişmedi.
  (2) SSS'deki 5 soru `<h2 class="accordion-header">` → `<h3>` (satır
  982-1044 aralığı, yalnız bu 5 çift, bölüm başlığı "Sıkça Sorulan Sorular"
  H2 olarak kaldı) — TR dahil tüm diller etkilendi, JSON-LD FAQPage ayrı
  script bloğu olduğu için etkilenmedi.
  (3) **KRİTİK EK BULGU (doğrulama sırasında bulundu, plan dosyasında
  YOKTU):** SSS bölümünün tamamı (5 soru + JSON-LD FAQPage) hiç dil
  koşuluna bağlı değildi — DE/EN'de TR pazaryeri içeriğiyle birebir
  render ediliyordu. Örnek, canlıda DE: "Die Experten auf der Plattform
  prüfen den Umfang Ihres Projekts und machen Ihnen ihr eigenes
  Preisangebot" (platformdaki uzmanlar teklif verir) — K3 kararıyla
  (fiyat sitede gösterilmez) ve "pazaryeri kapalı" pozisyonuyla doğrudan
  çelişiyordu. Adım 1'in URL/link bazlı sızıntı taraması bunu yakalamamıştı
  (düz metin, link içermiyor). Kullanıcı onayıyla hemen düzeltildi: SSS
  başlığı+alt başlığı+5 soru (`home.html:969-1055`)
  `{% if LANGUAGE_CODE == 'tr' %}` ile sarıldı; altındaki mevcut
  `{% if LANGUAGE_CODE != 'tr' %}` CTA'sı ("Noch Fragen? Beschreiben Sie
  Ihr Projekt…", zaten `source=home_faq` ile vardı) dokunulmadan kaldı —
  EN/DE artık SSS yerine doğrudan bu CTA'yı görüyor. Adım 6'da gerçek
  danışmanlık SSS'si gelince bu geçici gizleme kaldırılacak.
  **Ders (lessons.md'ye de eklenebilir):** EN/DE sızıntı taraması yalnız
  URL/link pattern'i değil, düz metin açıklamalarını da (özellikle
  "uzman teklif verir/eşleşme" gibi pazaryeri mekaniği anlatan cümleleri)
  kapsamalı.
  **Doğrulama:** `docker compose restart web`; curl ile DE/EN/TR `<title>`,
  meta description, SSS h2/h3 sayımı, FAQPage JSON-LD varlığı (TR'de var,
  DE/EN'de artık hiç yok — beklenen) kontrol edildi; DE'de CTA metninin
  ("Noch Fragen?...") gerçekten göründüğü doğrulandı. `pytest
  forum/tests.py` → **90/90 yeşil**.
  **Deploy etkisi:** migration yok; `.po`/`.mo` + `home.html` değişti,
  bind-mount sayesinde `restart web` yeterli.
  **ADIM 4 commit + push edildi** (`4e4e8b1`, `dev`'e gitti).

  **ADIM 6 TAMAMLANDI (16 Ekim 2026) — yeni danışmanlık odaklı EN/DE ana
  sayfası (`home_intl.html`) + flag, henüz commit edilmedi. Kullanıcı
  "6'yı yap" diyerek Adım 5'i atlayıp doğrudan Adım 6'ya geçti — Adım 5
  (Premium/bağış EUR+IBAN) hâlâ açık, sırada.**

  **Mimari (9 dosya):** `forum/models.py` (+`feature_intl_consulting_home`
  alanı + `ProjectRequest.SOURCE_CHOICES`'a `home_academic`),
  `forum/migrations/0179_...py` (migration, root sahipli — chown izni yok
  ama git/okuma sorunsuz çalışıyor, bilinen kısıt), `forum/
  context_processors.py` (+`intl_consulting_home` flag'i), `forum/admin.py`
  (fieldsets'e eklendi), `forum/views.py` (`home()` sonunda flag+dil
  kontrolüyle şablon seçimi, `SiteSettings.load()` tek sorguya indirildi),
  **yeni** `forum/templates/forum/home_intl.html` (~300 satır), 2× `.po`
  + `.mo`.

  **İçerik:** Hero (tek CTA + K7 dropzone aynen) → Güven şeridi (yalnız AB
  içi veri + TR/EN/DE dil, K1/K5) → Akademik/Kurumsal kart (ikincisi
  `ai_cozumler`'e de link) → Teslimatlar (bir revizyon turu dahil, onaylı)
  → 4 adım süreç ("teklif" dendi, "sabit fiyat" DENMEDİ — K3 netleşmemişti)
  → Sınırlarımız → AI doğrulama bandı (Adım 2'den temiz, agentic/training
  kartları çıkarıldı — kurumsal kartla çakışmasın diye, training zaten
  `LANGUAGE_CODE == 'en'` ile sınırlı olurdu K6 gereği) → Araştırma
  Konsolu (mevcut, birebir, zaten EN/DE filtreli) → 6 soruluk SSS (H3,
  kendi FAQPage JSON-LD'si, K3/K4/K5/K1 kararlarına dayalı cevaplar).

  **Doğrulama turunda 2 EK SIZINTI bulundu ve kapatıldı (planın kendi S4/S5
  bulguları, hiç uygulanmamıştı):**
  1. "Nasıl Çalışıyoruz?" 4 adımlı bölüm (`home.html:535`) — "İlan Aç",
     "Teklif Al (doğrulamadan geçmiş analistler...)" pazaryeri adımları
     dil koşulsuzdu → başlık+4 kart `{% if LANGUAGE_CODE == 'tr' %}` ile
     sarıldı, altındaki mevcut `home_steps` CTA'sı dokunulmadı.
  2. "GEMINI GÖREV 6: GÜVEN UNSURLARI (Platform Güvencesi)" bölümü
     (`home.html:648`) — "Güvenli Ödeme", "Uzman Doğrulama" (analistler
     doğrulamadan geçer), "Şeffaf Değerlendirme" (5 yıldız) — hiçbiri
     EN/DE için gerçek değildi (ödeme kararı blokajda, doğrulanmış uzman
     ağı yok), hiç dil koşulu yoktu → tüm bölüm TR'ye özel yapıldı.
  **Ders:** Bu oturumda toplam 5 kez (Adım1: S1/S3, Adım4: FAQ, Adım6: S4/S5)
  aynı kalıp tekrarladı — plan dosyası S1-S5'i tanımlamış ama yalnız S1-S3'ü
  gerçekten kapatmıştı. `analizus.md`/`tasks/lessons.md`'ye not: **EN/DE
  sızıntı denetimi yalnız URL/link grep'i değil, "ilan", "teklif",
  "doğrulanmış uzman", "güvenli ödeme" gibi pazaryeri sözcüklerini de
  taramalı; bir plan dosyasının "bulundu" demesi "düzeltildi" anlamına
  gelmez, uygulanmadan önce kodda fiilen kontrol et.**

  **Çeviri süreci notu (gelecek oturumlar için önemli):** `makemessages`
  sonrası yeni msgid'lerin bir kısmı (11/76) metince BENZER eski
  msgid'lere `#, fuzzy` olarak otomatik eşleşti ve YANLIŞ/eski çeviriyi
  miras aldı — boş `msgstr ""` taraması bunları YAKALAMAZ (zaten dolu
  görünürler). Fark edilmesi `node`/curl değil **Playwright ekran
  görüntüsü** sayesinde oldu (hero CTA'sı ve kurumsal kart başlığı hâlâ
  Türkçe çıkıyordu). Düzeltme: şablondaki tüm `{% trans %}` msgid'lerini
  programatik çıkarıp her birini po'da `fuzzy`/`boş`/`eksik` olarak
  tarayan bir script yazıldı (76/76 temiz çıktı). **Kural:** yeni şablon +
  toplu çeviri turlarında, "boş msgstr" taraması YETMEZ — fuzzy taraması
  da şart, en güvenilir doğrulama görsel (Playwright) kontrolüdür.

  **Doğrulama:** `transaction.atomic()` içinde flag açılıp TR/EN/DE
  render edildi, rollback yapıldı — TR değişmedi (sayı bile aynı), EN/DE
  `home_intl.html`'i kullandı, sıfır pazaryeri/forum sızıntısı, FAQPage
  JSON-LD (`json.loads`) geçerli. Flag kapalıyken EN/DE'nin hâlâ
  `home.html`'i kullandığı ayrıca doğrulandı. Playwright ile EN/DE ×
  375/1280px tam sayfa ekran görüntüsü — ilk turda 2 metin hâlâ Türkçe
  çıktı (yukarıdaki fuzzy sorunu), düzeltilip tekrar çekildi, temiz.
  İki inline JS bloğu `node --check` ile sözdizimi doğrulandı. `pytest
  forum/tests.py` → **90/90 yeşil** (üç ayrı turda tekrar tekrar
  çalıştırıldı, hepsi yeşil).

  **Deploy etkisi:** **MIGRATION VAR** (`0179_...py`, no-data — yalnız
  yeni `BooleanField` + `choices` değişikliği, mevcut satırları etkilemez)
  → `main`'e push öncesi kullanıcıdan `scripts/yedek_indir.sh --simdi`
  (kendi bilgisayarında) istenmeli. Flag canlıda **kapalı** gelecek;
  kullanıcı admin'den `SiteSettings` → Feature Flags → "EN/DE Danışmanlık
  Ana Sayfası" ile açacak.
  **ADIM 6 commit + push edildi** (`8d3284e`, `dev`'e gitti).

  **CANLI BUG BULUNDU VE DÜZELTİLDİ (16 Ekim 2026, kullanıcı Render dev
  ortamında ekran görüntüsüyle bildirdi):** `home.html`'de "Nasıl
  Çalışıyoruz?" bölümünü (Adım 6 doğrulama turunda) TR'ye özel yaparken,
  altındaki `{% if LANGUAGE_CODE != 'tr' %}` CTA'sını ("Ücretsiz Proje
  Talebi Gönder") bilerek dokunmadan bırakmıştım (FAQ'daki desenle aynı).
  Ama bu CTA'nın hiç bağlamı yoktu (FAQ'daki "Hâlâ sorunuz mu var?" gibi
  açıklayıcı metni yok) — EN/DE'de "I Want an Analysis Done" kartının
  hemen altında, boşlukta duran İKİNCİ bir "Send a Free Project Request"
  butonu olarak görünüyordu, görsel olarak bozuk/tekrarlı duruyordu.
  **Düzeltme:** Tüm `ax-steps-section` (başlık+4 kart+yetim CTA dahil
  `<section>` etiketiyle birlikte) `{% if LANGUAGE_CODE == 'tr' %}` ile
  sarıldı, yetim CTA tamamen kaldırıldı (FAQ'daki gibi bağlamlı bir CTA
  değil, saf tekrar olduğu için silinmesi doğru karardı).
  **Ders:** Bir bölümü gizlerken altındaki "kalsın" denen CTA'nın GERÇEKTEN
  bağlamsız kalıp kalmadığını kontrol et — FAQ'da CTA'nın kendi açıklayıcı
  metni vardı (çalıştı), Steps'te yoktu (bozdu). Sadece kod tarafı
  doğrulaması (curl/pytest) bunu yakalamadı, kullanıcının gerçek tarayıcı
  ekran görüntüsü yakaladı — **büyük sızıntı kapatma turlarından sonra
  kullanıcıya da canlı/dev ortamı gözden geçirmesi hatırlatılmalı.**
  **Doğrulama:** Playwright ile EN sayfası tam ekran görüntüsü — tek CTA
  kart içinde, ikincisi yalnız sayfa sonundaki FAQ'da (bağlamlı). `pytest
  forum/tests.py` → **90/90 yeşil**. **Commit + push edildi** (`7b155da`,
  `dev`'e gitti).

  **Sıradaki adım sırası — kullanıcı kararı (16 Ekim 2026):** Adım 5
  (Premium/bağış EUR+IBAN) hâlâ bekliyor (atlandı); kalan adımlar için
  sıra **10 → 7 → 9 → 8 → 11** olarak belirlendi.

  **ADIM 10 TAMAMLANDI (16 Ekim 2026) — proje talebi formuna "aşama" +
  "hedef teslim tarihi" + isteğe bağlı randevu linki eklendi, henüz
  commit edilmedi. MIGRATION VAR (0180).**
  **Mimari (7 dosya):** `forum/models.py` (+`ProjectRequest.STAGE_CHOICES`
  ve `stage`/`deadline` alanları; +`SiteSettings.meeting_booking_url`),
  `forum/migrations/0180_...py`, `forum/admin.py` (ikisi de fieldsets/
  list_display/list_filter'a eklendi), `forum/views.py` (`proje_talebi()`
  — `stage` zorunlu doğrulamaya eklendi, `deadline` isteğe bağlı parse
  edilir, admin bildirim e-postasına ikisi de eklendi), `forum/templates/
  forum/proje_talebi.html` (yeni form satırı: Aşama [zorunlu select] +
  Hedef Teslim Tarihi [isteğe bağlı date input]; "Randevu Planla" linki
  yalnız `meeting_booking_url` doluysa görünür), 2× `.po`+`.mo`.
  **Kullanıcı kararları:** bütçe aralığı alanı EKLENMEDİ (fiyat/para
  birimi belirsizliği nedeniyle); aşama zorunlu, tarih isteğe bağlı;
  randevu linki şimdilik boş (admin daha sonra dolduracak, kod değişikliği
  gerekmeyecek).
  **Ek bulgu — kullanıcı onayıyla hemen düzeltildi:** proje_talebi
  sayfasındaki "Neden Analizus?" kutusunda "Python, R, SQL, Tableau
  uzmanlarından oluşan doğrulanmış analist ağı" ifadesi K1 kararıyla
  (admin kendisi/ekibi TR/EN/DE danışmanlık veriyor, ağ/pazaryeri modeli
  değil) çelişiyordu — yalnız bu msgid'in DE/EN msgstr'ı "Direkte
  Betreuung durch unser Team..."/"Direct support from our team..." olarak
  değiştirildi (tek kullanım yeri, başka sayfayı etkilemedi).
  **AÇIK BULGU — kullanıcı karar vermeden oturum kapandı, bir sonraki
  oturumda sorulmalı:** Aynı sayfanın H1/alt başlığı da aynı sorunu
  taşıyor: "Tell Us About Your Project, We'll Find the Right Expert" /
  "...we'll match you with expert analysts and offer a free initial
  assessment." — "uzman bulma/eşleştirme" vaadi K1 ile çelişiyor ama
  kapsamı daha geniş (H1 + alt başlık + muhtemelen "Finans, perakende,
  sağlık ve üretim sektörlerinde kanıtlanmış proje deneyimi" gibi
  doğrulanmamış iddialar da var) — **dokunulmadı, ayrı onay gerekir.**
  **Doğrulama:** `transaction.atomic()` içinde TR/EN/DE × GET (form
  alanları render) + POST (stage+deadline ile başarılı kayıt, stage boşken
  reddedilme) test edildi, rollback temiz. Playwright ile EN form ekran
  görüntüsü — yeni alanlar doğru yerleşmiş, "Randevu Planla" linki doğru
  şekilde gizli (link boş olduğu için). `pytest forum/tests.py` →
  **90/90 yeşil**.
  **Deploy etkisi:** **MIGRATION VAR** (`0180_...py`, no-data — iki yeni
  alan, mevcut satırlar etkilenmez) → `main`'e push öncesi
  `scripts/yedek_indir.sh --simdi` (kullanıcının kendi bilgisayarında)
  gerekiyor.
  **Sıradaki:** Adım 7 (EN/DE navigasyon), sonra 9 (hizmet sayfaları
  tasarım dokümanı), 8 (Impressum), 11 (ölçüm) — bu oturumda başlanmadı,
  bir sonraki oturumda devam edilecek. Yukarıdaki açık bulgu (proje_talebi
  H1/alt başlık) da bir sonraki oturumun başında kullanıcıya sorulmalı.

  **ADIM 7 TAMAMLANDI (18 Ekim 2026) — EN/DE navigasyon.** 4 dosya: `templates/base.html` (masaüstü + mobil drawer),
  `templates/partials/footer.html`, `forum/templates/forum/home_intl.html`,
  `locale/{en,de}/LC_MESSAGES/django.po`+`.mo`.
  **Kapsam (kullanıcı kararıyla daraltıldı — tam yeniden tasarım değil):**
  (1) K6 düzeltmesi: "Eğitim" linki (`features.training` koşuluna ek
  `LANGUAGE_CODE != 'de'`) artık TR+EN'de görünür, DE'de gizli — önceden
  dil şartsızdı (flag açıkken DE'de de görünüyordu, K6'ya aykırıydı).
  (2) Yeni "Hizmetlerimiz" (`#leistungen`) ve "Nasıl Çalışıyoruz?"
  (`#ablauf`) nav linkleri — yalnız `features.intl_consulting_home` flag'i
  açık **ve** `LANGUAGE_CODE != 'tr'` iken görünür; `home_intl.html`'deki
  ilgili iki bölüme (`İki İş Kolu`, `Nasıl Çalışıyoruz?`) id eklendi.
  Flag kapalıyken (şu an canlı durum) hiçbir görünür değişiklik yok — ölü
  link riski yok (linkler zaten flag'e bağlı render oluyor).
  **Yapılmayan (plandaki tam öneri, kullanıcı kararıyla ertelendi):**
  Leistungen/Services ▾ ve Ablauf/Process ▾ dropdown'ları, "Free tools ▾"
  yeniden gruplama — mevcut Analizler/Akademik Tarama/Kurumsal yapısı
  EN/DE için zaten pazaryeri/forum sızdırmıyor, yeniden tasarım flag
  açıldıktan sonra ayrı bir turda değerlendirilebilir.
  **Doğrulama:** `transaction.atomic()` içinde iki flag (training,
  intl_consulting_home) açılıp TR/EN/DE × flag-açık/kapalı render edildi
  (`override_settings(ALLOWED_HOSTS=['*'])` ile Test Client), rollback
  yapıldı: Eğitim href sayısı TR=4, EN=4, DE=0 (beklenen); Leistungen/
  Ablauf linkleri yalnız flag açıkken EN/DE'de, flag kapalıyken hiçbir
  dilde yok. `pytest forum/tests.py` → **90/90 yeşil**.
  **Deploy etkisi:** migration yok, `--build` yok; `docker compose restart
  web` lokalde yapıldı ve doğrulandı.

  **ADIM 9 — TASARIM DOKÜMANI (18 Ekim 2026, kod YOK, kullanıcı kararı
  bekliyor).** Araştırma bulguları ve plan:
  **Mevcut durum (doğrulandı):**
  - `ServicePage`/`ServicePageSection`/`ServicePageFAQ` (`forum/models.py:
    936-987`) dil alanı yok, TR-only (model docstring'inde zaten yazıyor).
  - 4 aktif TR sayfası (DB'den doğrulandı): `nicel-analiz`,
    `akademik-danismanlik`, `nitel-analiz`, `veri-ve-yapay-zeka`.
  - `/hizmetler/` ve `/hizmetler/<slug>/` (`forum/urls.py:16-17`)
    `i18n_patterns` BLOĞUNUN DIŞINDA (`analizdestek/urls.py:127`) — dil
    prefix'i almıyor, EN/DE'den hiç erişilemiyor.
  - `feature_hizmet_sayfalari` flag'inin kendi help_text'i zaten "Pilot:
    önce yalnız Nicel Analiz sayfasını açın" diyor — EN/DE pilotu da aynı
    sayfayla (`nicel-analiz`) başlamalı.
  - `hreflang_alternates` (`forum/context_processors.py:95-124`)
    `translate_url()` ile yalnız dil PREFİX'ini değiştirir, slug'ı
    çevirmez; path tüm dillerde aynı değilse (bugün zaten öyle, sayfa
    i18n_patterns dışında) hreflang hiç üretilmiyor (sessizce atlanıyor).
    Sayfa i18n_patterns içine alınır ve EN/DE'de FARKLI slug kullanılırsa
    (`quantitative-analysis` gibi) bu mekanizma kırılır → 404.
  - `set_language` view'ı (`forum/views.py:4342-4360`) TR-only bir sayfada
    dil değiştirmeyi karşılık bulamadığı için ana sayfaya düşürüyor —
    hizmet sayfası i18n'e taşınırsa bu sarmalayıcının da güncellenmesi
    gerekir (karşılık path varsa oraya, yoksa ana sayfaya).
  - `ai_cozumler` (`forum/urls_i18n.py:29`) zaten i18n_patterns içinde ve
    EN/DE'de çalışıyor AMA tamamen farklı bir model: statik şablon +
    gettext çevirisi, DB içerik yok. ServicePage'in admin-düzenlenebilir
    içerik modeliyle doğrudan karşılaştırılamaz, emsal değil.
  - Projede DB satırı bazlı çok dilli içerik modeli (`language` alanlı,
    çeviri taşıyan) hiç yok — tüm EN/DE içerik ya gettext/.po (şablon
    metni) ya da `home_intl.html` gibi ayrı şablon. ServicePage içeriği
    (admin'in serbest yazdığı `intro`/`process_text`/bölümler) gettext'e
    uygun değil (msgid sistemi statik metin içindir).
  **İki tasarım kararı — kod yazmadan önce kullanıcı onayı gerekir:**
  1. **URL/slug stratejisi** — Öneri (A, daha düşük riskli): sayfayı
     `i18n_patterns` içine taşı, SLUG'I TÜM DİLLERDE AYNI tut, yalnız
     `path()` önekini `gettext_lazy` ile çevir (`/en/services/nicel-analiz/`,
     `/de/leistungen/nicel-analiz/`, `/hizmetler/nicel-analiz/` TR) →
     mevcut `hreflang_alternates`/`translate_url` hiçbir özel kod
     gerektirmeden doğru çalışır. Alternatif (B, plandaki orijinal öneri):
     dile göre FARKLI slug + grup anahtarı — daha "doğal" EN/DE URL'leri
     verir ama hreflang'i context processor'da özel eşlemeyle bypass etmek
     ve `set_language`'ı override etmek gerekir (yeni, test edilmemiş
     kod yolu). **A önerilir** (YALIN ilkesiyle tutarlı, mevcut i18n
     altyapısını bozmadan kullanır).
  2. **İçerik modeli** — Öneri: yeni `ServicePageTranslation` modeli
     (FK → `ServicePage`, `language` seçimi `en`/`de`, çevrilen alanlar:
     `title`, `meta_title`, `meta_description`, `intro`, `process_text`,
     `ethics_text`); `ServicePageSection`/`ServicePageFAQ` için de benzer
     küçük çeviri modelleri (veya tek JSON alanı — ikisi arasında seçim
     kullanıcıya sorulmalı). Admin'de TR sayfasının altında inline EN/DE
     çeviri formu (`StackedInline`) öner. **Pilot kapsamı:** yalnız
     `nicel-analiz` çevrilir, diğer 3 sayfa TR-only kalmaya devam eder
     (flag zaten bunu öngörüyor).
  **Migration etkisi (kod yazılırsa):** yeni model(ler) + varsa URL/view
  değişikliği — no-data migration, mevcut TR kayıtlarını etkilemez.
  **KARAR 1 ve 2 ONAYLANDI (18 Ekim 2026, kullanıcı):**
  - Karar 1 (URL/slug): **Öneri A** — slug tüm dillerde aynı kalır, yalnız
    URL öneki `gettext_lazy` ile çevrilir (`/en/services/nicel-analiz/`,
    `/de/leistungen/nicel-analiz/`, TR `/hizmetler/nicel-analiz/`); mevcut
    `hreflang_alternates`/`translate_url` değişmeden çalışır.
  - Karar 2 (içerik modeli): ayrı `ServicePageTranslation` tablosu (JSON
    alanı değil), pilot kapsamı yalnız `nicel-analiz`.
  **İkisi de onaylandı, AYNI OTURUMDA KOD YAZILDI (18 Ekim 2026):** yeni
  `ServicePageTranslation`/`ServicePageSectionTranslation`/
  `ServicePageFAQTranslation` modelleri (migration 0181), `/hizmetler/`
  URL'leri `i18n_patterns`'e taşındı (`forum/urls_i18n.py`), admin'e
  çeviri inline'ı + 2 ayrı admin kaydı + sidebar girdileri eklendi.
  **Ek bulgu (kod yazarken ortaya çıktı, kullanıcı onayıyla kapsam
  genişletildi):** `service_list.html`/`service_detail.html` şablonları
  ve `nicel-analiz` pilot içeriği (intro/süreç/etik/FAQ) pazaryeri
  modeline göre yazılmıştı ("İlan Aç", "Pazaryerine Git", "Uzmanları Gör",
  bölüm başına uzman eşleştirme kartları) — K1'e aykırıydı. Şablonlardaki
  tüm pazaryeri CTA/kart/breadcrumb'ları EN/DE'de `proje_talebi` CTA'sına
  çevrildi, uzman eşleştirme EN/DE'de hiç hesaplanmıyor. `nicel-analiz`
  için EN/DE intro/süreç/etik/FAQ K1/K3/K4 kararlarına göre YENİDEN
  YAZILDI (birebir çevrilmedi); 7 metodoloji bölümü (pazaryeri ifadesi
  içermiyordu) doğrudan çevrildi (migration 0182, korumalı/idempotent).
  Çevirisi olmayan sayfa (diğer 3 TR sayfası) EN/DE'de 404 döner — TR ham
  içerik fallback olarak gösterilmez.
  **Doğrulama:** `override_settings(ALLOWED_HOSTS=['*'])` ile Test Client,
  nicel-analiz TR/EN/DE render edildi (TR: pazaryeri CTA var; EN/DE:
  proje_talebi CTA var, pazaryeri sıfır), akademik-danismanlik EN/DE'de
  404 (TR'de 200), hreflang etiketleri doğru 4 dil/URL üretti (`translate_
  url` slug'a dokunmadan çalıştı), SSS/bölüm başlıkları doğru dilde
  geldi. `pytest forum/tests.py` → **90/90 yeşil**.
  **Deploy etkisi: MIGRATION VAR (0181 yapısal, 0182 veri/korumalı)** —
  main'e push öncesi `scripts/yedek_indir.sh --simdi` gerekir.
  **COMMIT + PUSH EDİLDİ (`20942ac`, `dev`'e gitti, Adım 7 ile birlikte
  tek commit'te).**
  **Not:** Yeni `/hizmetler/` sayfası henüz hiçbir EN/DE nav/footer'a
  linklenmedi (Adım 7'de bilinçli olarak kapsam dışı bırakılmıştı) —
  yalnız doğrudan URL veya `service_page_list` üzerinden erişilebilir.

  **ADIM 11 TAMAMLANDI (18 Ekim 2026) — başlangıç ölçümü alındı, kullanıcı
  komutu production'da (Hetzner) çalıştırdı.** Sonuç: `[{'language': '',
  'source': 'direct', 'n': 3}]` — toplam 3 `ProjectRequest` kaydı, hepsi
  eski (dil/kaynak alanı boş), EN/DE'den hiç talep yok. `analizus.md`
  §28.7'ye işlendi. **Tekrar tarihi: ~15 Kasım 2026** (Adım 6/7/9 canlıya
  çıkışından 4 hafta sonra).

  **Kullanıcı ayrıca production'da canlı ekran görüntüsüyle doğruladı
  (18 Ekim 2026):** flag'ler (`feature_intl_consulting_home`,
  `feature_training`) production admin'den ayrıca açıldı (dev'den
  bağımsız, ayrı DB); yeni nav (Leistungen/So arbeiten wir, EN'de Training
  DE'de yok) canlıda doğru çalışıyor. **Ek bulgu (kullanıcı gözlemi,
  aynı gün düzeltildi):** `home_intl.html` hero'sunda CTA sonrası 3 ayrı
  metin satırı (güven cümlesi + araç listesi + AI sloganı) fazla kalabalık
  duruyordu → tek kısa cümleye indirildi ("Ücretsiz, kayıt gerekmeden APA
  formatında rapor alın. 18 aracın tümü →"), AI sloganı kaldırıldı (aşağıda
  zaten tekrar ediyordu). Yeni 1 msgid (`locale/{en,de}`), `pytest` 90/90
  yeşil. **Commit + push + merge edildi** (`8f26686`, main'e alındı).

  **Ek bulgu (kullanıcı canlı DE/EN karşılaştırmasında fark etti, aynı gün
  düzeltildi):** DE hero başlığı TR kaynağın uzun/açıklayıcı birebir
  çevirisiydi, EN için ise ayrı kısa bir slogan yazılmıştı (Adım 6'dan
  kalma bilinçli tercih, ama iki dil arasında tutarsız tondu). DE msgstr
  "Statistikberatung, die standhält." olarak EN ile aynı tona getirildi
  (TR msgid/EN değişmedi). **Commit + push + merge edildi** (`67c04df`).

  **Ek bulgu (kullanıcının "GSC'de yapacak bir şey var mı?" sorusu
  üzerine bulundu, aynı gün düzeltildi):** `forum/sitemaps.py`'deki
  `ServicePageSitemap` yalnız TR URL üretiyordu, `service_page_list` de
  TR-only `StaticViewSitemap`'teydi — Adım 9'da `/hizmetler/`
  `i18n_patterns`'e taşındığı halde sitemap güncellenmemiş, yeni EN/DE
  sayfaları Google'a hiç bildirilmiyordu. `service_page_list` →
  `StaticI18nSitemap`'e taşındı (TR+EN+DE); yeni
  `ServicePageTranslatedSitemap` eklendi — yalnız gerçekten çevirisi olan
  (sayfa, dil) çiftlerini listeler (404 riski yok). Doğrulama:
  `/sitemap.xml`'de beklenen 9 URL tam çıktı, `pytest` 90/90 yeşil.
  **Commit + push + merge edildi** (`b840490`).

  **KULLANICIYA KALAN GSC ADIMLARI (sitemap düzeltmesi main'e gittikten
  sonra, Hetzner deploy olunca):**
  1. Google Search Console'da `sitemap.xml`'i yeniden gönder.
  2. `/en/` ve `/de/` ana sayfa için URL denetimi + "Dizine Ekleme İste"
     (içerik önemli ölçüde değişti).
  3. `/en/hizmetler/nicel-analiz/` ve `/de/hizmetler/nicel-analiz/` için
     aynısı (yeni sayfalar).
  4. hreflang'in canlı HTML'de doğru çıktığını sayfa kaynağından kontrol
     et (GSC'de ayrı hreflang raporu yok).

  **11 ADIMLIK PLANIN TAMAMI TAMAMLANDI, main'e alındı** (Adım 5 —
  Premium/bağış EUR+IBAN — kullanıcı kararıyla atlandı/ertelendi; Adım 8
  — Impressum — şirket bilgisi gelene kadar beklemede).

  **KARAR (kullanıcı sordu, 18 Ekim 2026): `/hizmetler/` sayfasına EN/DE'de
  BİLİNÇLİ OLARAK hiçbir nav/footer linki eklenmeyecek.** Kullanıcı
  "dokunma, böyle kalsın" dedi — sayfa yalnız Google/dış arama trafiği
  için var (TR'deki "market'e yeni şerit eklenmez" ilkesine benzer),
  footer'daki "Hizmetler" linki hâlâ `LANGUAGE_CODE == 'tr'` şartına bağlı
  kalacak. EN/DE'de sayfaya ulaşmanın tek yolu doğrudan URL veya Google
  sonucu — bu bir bug/eksiklik DEĞİL, bilerek bırakıldı. İleride tekrar
  gündeme gelirse bu karar hatırlanmalı.

- [x] **(16 Ekim 2026, kullanıcı bulgusu → aynı gün düzeltildi) EDU doğrulama
  DM'i admin'in kişisel hesabından gönderiliyordu, sistem/bot hesabından değil.**
  `forum/views.py:1361` (`_handle_edu_user`) artık diğer otomatik DM'lerle aynı
  deseni kullanıyor: önce `User.objects.get(username='AnalizBot')`, `AnalizBot`
  yoksa (ör. dev DB'de seed edilmemişse) fallback olarak ilk superuser.

- [ ] **(16 Ekim 2026, kullanıcı bulgusu — kullanıcı tarafında yapılacak, Render
  dashboard erişimi gerektiriyor) Render (`analizus-dev`) saatlik "memory limit
  exceeded" ile restart oluyordu.** Kök neden: `istatistik/services/job_runner.py`
  `_session_datasets` dict'i (istatistik araçlarına yüklenen dosya içeriğini
  RAM'de session_key'e göre tutuyor) yalnızca saatlik harici cron
  (`api/cron/cleanup-session-datasets/?secret=...`) ile temizleniyor; Hetzner
  crontab'ı salt-okunur incelendi (kullanıcı onayıyla) — bu cron yalnızca
  `https://www.analizus.com`'u hedefliyor, Render'a (`analizus-dev.onrender.com`)
  hiç gitmiyor. Dict sınırsız birikip OOM'a yol açıyordu. **Kod tarafı aynı gün
  düzeltildi:** `save_session_dataset()` artık her yeni kayıtta süresi geçmiş
  girdileri de fırsatçı temizliyor (`job_runner.py:27-30`, `dev`'e push edildi) —
  bu tek başına da yeterli bir güvence. **Kullanıcının yapması gereken (opsiyonel
  ek güvence):** Render dashboard'da `CRON_SECRET_KEY` tanımlı olduğunu
  doğrulayıp, saatlik `GET https://analizus-dev.onrender.com/api/cron/cleanup-session-datasets/?secret=<Render'daki CRON_SECRET_KEY>`
  çağrısı yapan bir cron (Render Cron Job veya cron-job.org) kurmak — Hetzner'in
  production secret'ı Render için kullanılmamalı, ayrı ortam.

- [ ] **(15 Ekim 2026, ÜRÜN KARARI BEKLİYOR)** YÖK Tez'de (muhtemelen diğer tarama
  araçlarında da) kullanıcılar "Başlık"/"Özet" alanına virgülle ayrılmış birden
  fazla kelime giriyor (ör. "islam, tefsir, hadis, tasavvuf, Kur'an, fıkıh,
  sünnet"), OR aranacağını bekleyerek — ama kod bunu desteklemiyor.
  `yoktez/services/scraper.py:86-100` (`_determine_query`) `tez_ad` değerini
  OLDUĞU GİBİ (virgülleri ayırmadan) YÖK'ün arama formuna tek "keyword" olarak
  gönderiyor → YÖK bunu muhtemelen tam ifade/alt-metin olarak arıyor, gerçek tez
  başlıkları bu kadar uzun virgüllü bir ifadeyi içermediği için 0 sonuç dönüyor.
  Admin dashboard'da görülen "79firuze" kullanıcısının 2 başarısız araması bu
  örüntüyle örtüşüyor — muhtemelen 0-sonuç aramaların önemli bir kısmının kök
  nedeni. İki seçenek, karar kullanıcıda: **(A)** düşük efor — form'a/placeholder'a
  "bu alan tam ifade arar, virgülle ayrılmış kelimeleri OR olarak aramaz" tarzı
  netleştirici metin eklemek; **(B)** daha değerli ama daha büyük iş — virgülle
  ayrılmış terimleri gerçekten OR mantığıyla aramak (her terim için ayrı YÖK
  isteği + sonuçları birleştirme/tekilleştirme — mevcut rate-limit/insan-gecikmesi
  mimarisiyle dikkatli entegre edilmeli). Diğer 5 aracın (OpenAlex/TrDizin/
  SemanticScholar/PubMed/OAI-PMH) `query_parts` tabanlı title/abstract alanlarının
  aynı sorunu yaşayıp yaşamadığı ayrıca kontrol edilmeli — onlar gerçek API'lere
  gittiği için YÖK'ten farklı davranabilirler, doğrulanmadı.
- [ ] **(15 Ekim 2026, 2. planda — ertelendi)** Render `dev` ortamında
  (`/admin/analytics/pageview/grafik/` — "Kullanıcı Navigasyon Analizi")
  3 widget de "Kayıt yok" gösteriyor. Teşhis: `chart_view()` varsayılan
  görünümde `is_staff=True` kullanıcıları hariç tutuyor
  (`analytics/admin.py:182-186, 224-227`); dev'e girenler ya staff/test
  hesabıyla geziniyor (filtrelerle eleniyor) ya da hiç login olmadan bakıyor
  (`PageViewMiddleware` `is_authenticated` şartına takılıp hiç yazmıyor,
  `analytics/middleware.py:22`). Ayrıca middleware hatayı sessizce yutuyor
  (`except Exception: pass`, satır 35-36) — migration eksikse bile görünmez.
  Kesinleştirmek için `/admin/analytics/pageview/` ham listesine bakılmalı
  (o tarih aralığında satır var mı, varsa kullanıcılar staff mı). Kod
  değişikliği YAPILMADI — kullanıcı isteyince ele alınacak.
- [ ] **(15 Ekim 2026, admin dashboard kelime grafiği sırasında bulundu)**
  `forum/services/dashboard_service.py:160` → `from oaipmh.models import
  OAISearchJob` yanlış import, gerçek model adı `OAIPMHSearchJob`. `except
  Exception` ile sessizce yutuluyor; admin dashboard'daki "Dizin Tezleri"
  (oaipmh) bu ay/toplam sayaçları (`oaipmh_month`/`oaipmh_total`) bu yüzden
  her zaman 0 görünüyor. Kapsam dışı tutuldu (ayrı görev olarak düzeltilmeli).
- [ ] **(15 Ekim 2026)** `semanticscholar/admin.py` diğer 5 tarama aracından
  farklı olarak Unfold değil düz Django `ModelAdmin` kullanıyor, ayrıca
  `get_query_summary` sütunu yok (sadece ham `status/total_results/created_at`
  görünüyor) — görsel/işlevsel tutarsızlık, ayrı görev olarak ele alınmalı.
- [x] **TAMAMLANDI (16 Ekim 2026) — OAI-PMH "0 sonuç" yanlış sınıflandırma düzeltmesi +
  44 yeni üniversite + admin sidebar sadeleştirmesi, `main`'de canlı (3 ayrı merge).**
  `oaipmh/services/scraper.py`'deki `browse_university()` bağlantı/sunucu hatalarını
  (connection refused, SSL, HTTP 5xx) gerçek "0 sonuç" (`noRecordsMatch`) ile aynı şekilde
  yutup sessizce işaretliyordu — artık `last_result_count=-1` ("🔌 Bağlantı Hatası") ile ayrı
  gösteriliyor (admin e-postası + admin panel listesi). hipo-labs TR üniversite domain
  listesi + kalıp taramasıyla 44 yeni çalışan OAI-PMH endpoint'i bulunup eklendi (migration
  0010), hepsi gerçek canlı testten geçirildi — 4'ü (Marmara/Erzurum Teknik/Osmaniye/Rumeli)
  + eski 19'dan 3'ü (Çukurova/Uşak/Uludağ) flagged, admin kararı bekliyor. Admin sidebar'daki
  "Arama & Analiz" bölümü 10 satırdan 2'ye indi (Unfold `list_before_template` hook'u ile
  paylaşımlı sekme çubuğu, `analizdestek/admin_nav.py`), üst başlık kaldırıldı. Detaylı
  anlatım: `analizus.md` §27 "Geçmiş Turlar" en üstteki madde.
- [x] **TAMAMLANDI (15 Ekim 2026) — Admin dashboard analitik turu: arama kelime
  grafiği + 0-sonuç ikazı + YÖK Tez/OAI-PMH üniversite canlı tespiti, `main`'de
  canlı (production'da uçtan uca doğrulandı — İTÜ + Dokuz Eylül Ü. gerçekten
  flagged oldu, admin e-postası geldi).** Detaylı anlatım: `analizus.md` §27
  "Geçmiş Turlar" en üstteki madde. Yukarıdaki 4 açık madde bu turda bulundu,
  henüz çözülmedi.
- [x] **TAMAMLANDI (13 Ekim 2026) — Claude AI Yorumu Faz C: OpenAlex ve PubMed
  tarama sonuçlarına AI yorumu eklendi, `main`'de canlı.** Faz A/B (istatistik
  araçları) ile aynı desen: `AlexSearchJob`/`PubMedSearchJob`'a `ai_comment`
  TextField eklendi (migration `openalex/0004`, `pubmed/0002` — somut alanlı
  modeller olduğu için JSONField'a gömülemedi, Faz B'den farklı olarak gerçek
  migration gerekti). `job_runner.py`'lerde `mark_completed`'dan önce
  `_ai_comment_for_job`/`_build_ai_prompt` çağrılıyor (flag+kota kontrolünden
  geçerse); prompt'a tam `abstract` gönderilmiyor, yalnız başlık/yıl/dergi/tür
  + OpenAlex'te atıf sayısı, PubMed'de MeSH terimleri (token/maliyet kontrolü).
  `job_status` uçları ve template'ler (openalex: mevcut Bootstrap deseniyle
  tutarlı; pubmed: zaten geçmiş olduğu `ax-`/`pm-` sistemiyle tutarlı) AI
  kutusunu gösteriyor. Dil: her iki job_runner da zaten `recipient_language
  (user)` içinde çalıştığından ekstra mekanizma gerekmedi (istatistik'teki
  `_pending_job_languages` deseninden farklı, ama fonksiyonel olarak yeterli).
  `feature_ai_summary`/`feature_pubmed` geçici açılıp gerçek Claude API
  çağrısıyla her iki araç için de doğru yorum üretildiği, `AIUsageLog`'a
  kaydedildiği, sayfaların yeni kutuyu render ettiği doğrulandı — tüm test
  verisi `transaction.atomic()` + rollback ile temizlendi, flag'ler eski
  haline (kapalı) döndü. Migration dosyaları container'da `makemigrations`
  ile üretilip root sahipliğinden host kullanıcısına geçirildi (bilinen
  kısıt, §26). 90/90 pytest yeşil. `dev`'de commit edilip (ece-benzeri hash)
  kullanıcı isteğiyle `main`'e merge + push edildi, Hetzner'e otomatik deploy
  tetiklendi. **Sırada Faz D:** Bibliometrics (migration + `analyzer.py` ham
  veri yakalama — en karmaşık faz, ayrıca bkz. aşağıdaki "Claude AI Yorumu"
  maddesi).

- [x] **TAMAMLANDI (13 Ekim 2026) — Ana sayfa "Uzman Olarak Katılmak
  İstiyorum" kartı zenginleştirildi, `main`'de canlı.** Kullanıcı bulgusu:
  talep tarafındaki kart ("Analiz Yaptırmak İstiyorum") zaten kategori
  rozetleri + 2. buton + "veya kendin yap" satırı içerirken arz tarafı
  yalnızca 1 paragraf + 3 madde + 1 buton — dengesizdi. Önce bir Explore
  turuyla uzman tarafına gerçekten sunulan özellikler koddan doğrulandı
  (abartı yasağı): "sıfır komisyon" gerçek (platform proje ücretine hiç
  dokunmuyor, `JobPayment` yalnız ilan vitrin ücreti), "1000 puan →
  Doğrulanmış Uzman & teklif verme hakkı" gerçek (`Profile.can_propose()`),
  "güvenli ödeme" / "Premium ile dizinde öne çık" gibi asılsız iddialar
  plana hiç alınmadı. İki somut tasarım seçeneği bir Canvas'ta (Design
  artifact) görsel olarak mockup'landı, kullanıcı inceleyip **Seçenek B
  (Zengin — talep kartıyla simetrik)**'i seçti. `forum/templates/forum/
  home.html` satır 464-481 (yalnız TR dalı) değiştirildi: 4. madde eklendi,
  kategori rozetleri (`ax-market-cats`, demand kartıyla birebir aynı
  desen/davranış — filtresiz `job_list` linki), canlı açık-proje sayacı
  (`ax-market-diy`, mevcut `open_jobs_count >= stat_min_display` korumalı
  context değişkenleri — view değişikliği gerekmedi), güçlendirilmiş arena
  linki, 2. buton ("Nasıl Uzman Olunur?" → `/uzmanlar/`). Hiç yeni CSS
  yazılmadı. `makemessages`/`compilemessages` çalıştırıldı (container'a
  geçici `gettext` kurulup iş bitince kaldırıldı); EN/DE msgstr boş
  bırakıldı (bu kart zaten yalnız TR'de render ediliyor). Eşik korumalı
  sayaç satırı hem normal (gizli, lokalde 0 açık ilan/25 eşik) hem geçici
  eşik düşürülmüş (görünür) durumda doğrulandı, 90/90 pytest yeşil. `dev`'de
  commit edilip kullanıcı isteğiyle `main`'e merge + push edildi.

- [x] **DÜZELTİLDİ (12 Ekim 2026) — Çalışma odası "Tartışma" bloğu yüksekliği
  sınırsızdı, sayfa aşağı doğru çok uzuyordu.**
  `forum/templates/forum/studyroom_detail.html` `#posts-container` viewport'a
  göre `calc(100vh - 420px)` ile sabitlenmişti; üstteki bilgi kartı 420px'den
  uzun olunca kutu aşırı büyüyüp sayfayı uzatıyordu. DM/mesajlaşma ekranındaki
  (`send_message.html` `#chat-history`) kalıpla aynı hale getirildi:
  `min-height:300px; max-height:450px; overflow-y:auto` — artık sabit boyutlu,
  kendi içinde kaydırılıyor. Lokalde template cache temizlenip (`docker
  compose restart web`) doğrulandı. `dev`'den `main`'e merge edilip push
  edildi, Hetzner'e otomatik deploy tetiklendi (12 Ekim 2026).

- [x] **TAMAMLANDI (25 Ekim 2026, kullanıcı onayı) — Çalışma odası admin onayı
  bildirim olarak hiçbir yerde görünmüyor.** Kullanıcı yeni oda açtığında
  "Admin onayı bekleniyor" mesajı gösteriliyor ama admin tarafında (navbar
  bildirim zili / dashboard "BİLDİRİMLER" paneli — İlan Onayı, Ödemeler,
  Hikayeler, Değerlendirmeler, Mesajlar, Bağışlar sekmeleri) bekleyen oda
  onayı için hiç sekme/sayım yok, admin fark etmiyor. İstenen: (1) admin
  onayı bekleyen her türlü aksiyon (oda onayı dahil) dashboard'daki bu
  bildirim panelinde görünmeli; (2) ayrıca admin kullanıcılarına site-içi DM
  (oda/mesajlaşma sistemi — bkz. `analizus.md` §13-15) ile anlık bildirim
  gitmeli. Kapsam: hangi admin onay akışlarının (yalnız oda onayı mı, yoksa
  ileride başka bekleyen aksiyonlar mı) bu panele dahil edileceği ve DM
  gönderiminin tüm admin kullanıcılarına mı yoksa belirli bir role mi
  gideceği kullanıcı kararı gerektirir — uygulamaya başlamadan önce sorulmalı.

- [x] **DÜZELTİLDİ (12 Ekim 2026) — Hero doğrulama turu (`hero_dogrulama_prompt.md`)
  bulguları uygulandı, `dev`'den `main`'e merge + push edildi, Hetzner'e otomatik
  deploy oldu.**
  (1) "Kayıt gerekmez" → "Yüklemek için kayıt gerekmez" (TR/EN/DE) — 17/18 araç
  hâlâ `service_promo.html` giriş duvarına çarpıyor, yalnız yükleme adımı
  serbest; metin gerçeğe uyduruldu (araçları açmak yerine). (2) "24 saatte
  uzmana bırak" → "bir uzmana bırak" (TR/EN/DE) — `proje_talebi` view'ının
  kendi mesajı "en kısa sürede" diyordu, garanti edilmeyen rakam kaldırıldı.
  (3) `register()`/`custom_login()` sonrası Django `cycle_key()` session_key'i
  değiştirdiğinden RAM'deki hero-upload dosyası yetim kalıyordu —
  `move_session_dataset()` eklendi, **lokalde doğrulandı** (giriş sonrası
  dosya artık kayboluyor). (4) `tasks/todo.md` Faz 13'teki yanlış "misafir
  analiz çalıştırabiliyor" notu düzeltildi.
  **Render staging ve production'da kullanıcı tarafından doğrulandı (12 Ekim
  2026).**
- [ ] **DÜŞÜK ÖNCELİK (12 Ekim 2026, hero turu) — `analizus.md`'de hero
  template'i "home.html" diye anılıyor, gerçek yol
  `forum/templates/forum/home.html`.** Küçük dokümantasyon netliği, işlevsel
  etkisi yok.
- [ ] **DÜŞÜK ÖNCELİK (12 Ekim 2026, hero turu) — hero alt başlığındaki "18
  ücretsiz istatistik aracı" sayısı hardcoded**, `TOOL_CATEGORIES`'ten
  hesaplanmıyor (şu an doğru: 18). Araç eklenir/çıkarılırsa elle senkronize
  edilmeli; dinamik hesaplamaya çevirmek kozmetik bir sağlamlaştırma.
- [ ] **AÇIK SORU (12 Ekim 2026, hero turu) — "24 saat" ifadesi hero dışında
  da geçiyor** (AI Doğrulama bandı: "uzmanımız 24 saat içinde incelesin";
  bağış/Premium aktivasyonu: "24 saat içinde aktif edilir"). Bunlar hero'dan
  bağımsız farklı süreçler, kod bunların gerçekten tutturulduğunu garanti
  etmiyor — operasyonel olarak bu sürelerin fiilen karşılandığının
  doğrulanması kullanıcı/iş kararı, kod değişikliği değil.

- [x] **DÜZELTİLDİ (12 Ekim 2026, anasayfa_ux_kontrol_prompt.md turu) — Ana
  sayfa UX kontrolü bulguları (U2, U3, U4, U5, U6) uygulandı, local'de
  canlı doğrulandı (ikon, SSS metni, TR çapraz link, EN'de görünmediği,
  kontrast token'ı, kart z-index'i); henüz commit/push edilmedi, kullanıcı
  onayı bekliyor. U1b (24 saat vaadi, kapsam dışı) ve U2c (ProjectRequest
  veri sorgusu) hâlâ açık — ayrıntı aşağıda.
  **Ek bulgu (uygulama sırasında fark edildi):** `.ax-hero__personal-badge`
  ve `.ax-hero__personal-link:hover` (`home.html` satır 45,48) tanımsız
  `--ax-color-primary` token'ını kullanıyor (yalnız `hangi_test.html`'de
  sayfa-özel tanımlı, ana sayfada yok) — muhtemelen rengi görünmüyor/miras
  rengine düşüyor. Bu tur kapsamında DEĞİŞTİRİLMEDİ (U3 kapsamı dışı),
  ayrı görev olarak not edildi.
  Aşağıdaki orijinal bulgu metni (geçmiş referans için):
  (1) **U4, yüksek öncelik** — kapı kartlarında görsel çakışma CANLIDA
  DOĞRULANDI: `.ax-market-visual` absolute konumlu ama kart başlığı
  (`.ax-market-header`/`.ax-market-title`) hiç `position`/`z-index` almamış,
  bu yüzden 1024/1280/1632px'de dekoratif ikon başlığın üstüne biniyor; sol
  kartta illüstrasyon da kenar kesiliyor (`static/css/home_sections.css`
  satır 71-79, 233-238, 1323-1339). <768px'de görsel zaten gizli, sorun yok.
  Tek dosya değişir, deploy: yalnız `collectstatic`.
  (2) **U2, yüksek öncelik** — pazaryeri ↔ proje talebi çapraz yönlendirme
  tek yönlü: `job_list.html:52` proje talebine link veriyor, `proje_talebi.html`
  pazaryerine hiç geri link vermiyor. Ayrıca `ProjectRequest.source` dağılımı
  ve son 90 günün `FreelanceJob` sayısı kullanıcı tarafından shell'den
  kontrol edilip (komut hazır, ajan raporunda) ayrım metni/kapı sayısı kararı
  buna göre verilmeli.
  (3) **U3, orta öncelik** — hero altı 3 mikro-metinden 2'si (`--ax-text-muted`
  token; "t-testi·ANOVA" satırı VE gelir getiren "bir uzmana bırak" linki
  dahil) ölçülen kontrast ~3.4-4.0:1 — WCAG AA (4.5:1) FAIL. Kural iki yerde
  kopya halinde duruyor (`home.html` inline kritik CSS + `hero.css`), ikisi
  birlikte senkron değişmeli yoksa biri unutulur.
  (4) **U5, orta öncelik** — "Sıfır komisyon" iddiası doğru (yalnız isteğe
  bağlı vitrin ücreti var) ama ana sayfadaki SSS yalnız müşteri tarafını
  açıklıyor, uzman tarafına ("siz nasıl kazanıyorsunuz") hiç değinmiyor; SSS'e
  1-2 cümle eklenmesi gerekiyor (çeviri + `compilemessages` gerektirir).
  (5) **U6, düşük öncelik** — "Analiz Yaptırmak İstiyorum" kartındaki büyüteç
  SVG ikonu "ara" anlamında, "yaptır" değil; sitenin geri kalanı Bootstrap
  Icons (`bi-*`) kullanıyor — `bi-send`/`bi-clipboard-check` ile
  değiştirilmesi önerildi.
  (6) **Kapsam dışı not** — SSS akordeonu hâlâ `data-bs-toggle="collapse"`
  (Bootstrap JS) kullanıyor, CLAUDE.md kuralı ve devam eden Bootstrap
  Kaldırma Faz 3 ile çelişiyor; ayrı görev olarak işaretlendi.
  Ekran görüntüleri `tmp/ux_kontrol/` altında (14 dosya, `.gitignore`'da
  DEĞİL — commit edilmemesine dikkat). Önerilen uygulama sırası: U4 → U2 →
  U3 → U5 → U6, her biri ayrı onayla.

- [ ] **BULGU (12 Ekim 2026, "Render-blocking bundle.css" düzeltmesi sırasında
  Lighthouse'ta görüldü) — `#ax-cookie` çerez onay banner'ı CLS'e sebep
  oluyor** (Lighthouse `layout-shifts` audit'inde en büyük katkı, skor
  ~0.17/0.215). Bu PR'dan bağımsız, önceden var olan ayrı bir sorun —
  banner'ın sayfaya giriş animasyonu/konumlanması muhtemelen `position`
  geçişi veya geç render nedeniyle layout shift üretiyor. Kapsam dışı
  bırakıldı (ayrı görev); detay: bu dosyanın "PageSpeed" bölümündeki
  "Render-blocking bundle.css" maddesi.
- [x] **DÜZELTİLDİ (12 Ekim 2026) BUG — `bibliometrics/services/parser.py` `detect_format()`
  PubMed TXT'sini OpenAlex TXT sanıyordu.** PubMed'in indirilen TXT'si (`pubmed/services/
  job_runner.py` `_generate_pubmed_results_txt`) OpenAlex'inkiyle (`_generate_alex_results_txt`)
  BİREBİR AYNI "--- Yayın #" başlığını ve aynı dolgu genişliğini (w=17, ikisinde de en uzun
  etiket "Anahtar Kelimeler") kullanıyordu — "Başlık" satırları birebir aynı çıkıyordu, eski
  kontrol ikisini ayıramıyordu. **Düzeltme:** `detect_format()`'a OpenAlex kontrolünden ÖNCE,
  gettext'siz/dilden bağımsız sabit "PMID" satırına bakan bir `pubmed_txt` dalı eklendi; yeni
  `parse_pubmed_txt()` fonksiyonu (OpenAlex'inkine benzer ama PMID'i atlayan, anahtar kelime
  boşsa MeSH Terimleri'ne düşen) `parse_file()`'a bağlandı. Docker içinde gerçek
  `_generate_pubmed_results_txt`/`_generate_alex_results_txt` çıktısıyla uçtan uca doğrulandı:
  `detect_format` artık ikisini doğru ayırıyor, alanlar (başlık/yazar/yıl/DOI/tür/kurum/anahtar
  kelime/MeSH yedeği/özet) doğru parse ediliyor; `test_wos_parser.py` regresyonsuz geçti.
  Migration yok (yalnız `bibliometrics/services/parser.py`). **Ayrıca sorulan soru (hâlâ kullanıcı
  kararı bekliyor, kapsam dışı bırakıldı):** bibliometri sayfasındaki "OpenAlex'te tarama mı
  yaptın? ... OpenAlex Taramasına Git" köprü bandına PubMed de eklensin mi? PubMed'in zaten
  kendi sonuç sayfasında doğrudan köprü API'sine (`/bibliometrics/from-pubmed/<id>/`) giden
  "Bibliometrik Analiz İstiyorum" butonu var — bu banner yalnız "önceden indirilmiş dosyayı
  manuel tekrar yükleme" senaryosu için, PubMed'de gerçek talep henüz ölçülmedi.
- [x] **DÜZELTİLDİ (12 Ekim 2026) BUG — `forum/templates/forum/blog/blog_list.html` kart/sidebar
  arka planları tamamen şeffaftı.** İnline `<style>` bloğu + arama butonunun inline `style=`
  attribute'u (satır 30) `var(--ax-surface)`, `var(--ax-border)`, `var(--ax-text)`,
  `var(--ax-muted)`, `var(--ax-primary)` kullanıyordu — `static/css/base.css`'te hiç tanımlı
  olmayan terk edilmiş bir isim şeması. **Düzeltme:** dosyadaki toplam 33 kullanım gerçek
  token'lara eşlendi (`--ax-surface`→`--ax-bg-tertiary`, `--ax-border`→`--ax-border-default`,
  `--ax-text`→`--ax-text-primary`, `--ax-muted`→`--ax-text-secondary`, `--ax-primary`→
  `--ax-accent-primary`) — yalnız bu dosya, başka hiçbir blok değişmedi. `analizus.md` §10'daki
  ilgili not da "düzeltme bekliyor" durumundan "düzeltildi"ye güncellendi. Migration yok.
  **Not — taranmadı:** başka dosyalarda aynı eski kısa isimler kullanılmış mı kontrol edilmedi,
  istenirse ayrı görev.

- [x] **(11 Ekim 2026 → TAMAMLANDI, henüz push edilmedi) Profil "İlanlar" sekmesi: sahip kendi "Devam Eden Projeler"ini göremiyor.**
  Kullanıcı ekran görüntüsüyle bildirdi: `joseph` kendi profiline (`/profile/joseph/`)
  bakınca "İlanlar" sekmesinde sadece "Verdiğim Teklifler" (Kabul Edildi/Kabul
  Edilmedi) görüyor; aynı sekmede başka bir kullanıcı (örn. `bunyamin`) joseph'in
  profiline baktığında "Tamamlanan ve Devam Eden Projeler" (Devam Ediyor/
  Tamamlandı + yıldız) grubunu görüyor — sahip kendi "Devam Ediyor" durumundaki
  projelerini bu sekmede hiç göremiyor.
  - Kök neden (doğrulandı, `forum/views.py:1830` `profile_detail` +
    `forum/templates/forum/profile_detail.html` "İLANLAR SEKMESİ" bloğu):
    satır 471 `{% if is_owner %}` → `given_proposals` render ediliyor, satır
    501 `{% else %}` → `completed_projects` render ediliyor. Bu bir if/else —
    sahip olduğunda `completed_projects` (Devam Eden Projeler) hiç gösterilmiyor.
    `completed_projects` zaten view'de `is_owner` koşulu olmadan (satır
    1887-1889, `status='accepted'` filtresiyle) herkes için hesaplanıyor ve
    context'e konuyor (satır 1928) — veri hazır, sadece template'te sahibe
    gösterilmiyor. (Not: aynı veri "Portföy" sekmesinde sahibe dahil zaten
    gösteriliyor — satır 363-400 civarı, `is_owner` koşulsuz.)
  - **Düzeltme:** "İlanlar" sekmesinde sahip için `completed_projects`
    (Devam Eden Projeler) bloğunu da göster — ya `given_proposals`'ın yanına
    ek blok olarak ekle, ya da if/else'i kaldırıp ikisini birden sahibe göster.
    Kapsam tek şablon dosyası (`profile_detail.html`) + gerekirse context
    sırası; KIRMIZI ÇİZGİ kuralı gereği başka hiçbir bloğa dokunma.
  - **İkinci şikayet — reddedilen tekliflerin 3. şahıslara görünmesi —
    kodda ARAŞTIRILDI, sızıntı YOK:** `completed_projects` sorgusu
    `status='accepted'` filtresi taşıyor (`views.py:1888`) — reddedilen/
    bekleyen bir `JobProposal` bu queryset'e hiç giremiyor. `given_proposals`
    (reddedilenleri içeren tek değişken) yalnızca `is_owner=True` iken DB'den
    çekiliyor (`views.py:1884`), değilse `None` — template'e hiç ulaşmıyor.
    Ayrı bir API/AJAX endpoint bu veriyi tekrar expose etmiyor (grep ile
    doğrulandı). Bu bilinçli bir tasarım kararı (analizus.md'de Haziran 2026
    kaydı: 3. şahıslara fiyat+red durumu gizlenir, anonim "son tamamlanan
    proje" gösterilir). **Aksiyon gerekmedi**, sadece kayıt amaçlı not.
  - **Uygulanan değişiklik:** `forum/templates/forum/profile_detail.html`
    "İlanlar" sekmesindeki if/else kaldırıldı — `{% if is_owner %}...{% endif %}`
    (Verdiğim Teklifler) artık bağımsız bir blok, hemen ardından `{% if
    completed_projects %}...{% endif %}` (Tamamlanan ve Devam Eden Projeler)
    herkese (sahip dahil) gösteriliyor. Başka hiçbir dosya/blok değişmedi.
    `docker compose restart web` + `nginx` sonrası Django test client ile
    doğrulandı: owner görünümünde her iki başlık da (Verdiğim Teklifler +
    Tamamlanan ve Devam Eden Projeler) render ediliyor; başka kullanıcı
    görünümünde yalnız "Tamamlanan ve Devam Eden Projeler" görünüyor,
    "Verdiğim Teklifler" hiç yok (reddedilen teklif sızıntısı yok, eskisiyle
    aynı). `dev`'de commit edildi (1f689e7), kullanıcı isteğiyle `main`'e
    merge + push edildi (ece4ffd) — Hetzner'de otomatik deploy oldu, sunucuda
    `git log` ile doğrulandı.
  - **Round 2 (11 Ekim 2026, aynı gün) — kullanıcı canlıda test edince yeni
    sorun bildirdi:** "Tamamlanan ve Devam Eden Projeler" bloğu sahip için
    eklendi ama "Verdiğim Teklifler" listesinin ALTINA düştü; bu liste zaman
    içinde (her teklif kabul/ret) uzadıkça yeni blok ekranın iyice altında
    kalıp görünmez hale geliyor. Kullanıcı net talep etti: devam eden/
    tamamlanan projeler EN ÜSTTE ayrı bir kutuda (boşsa "yok" yazsın),
    "Verdiğim Teklifler" ise yalnız son 5 kayıt + altında "Diğerlerini gör"
    açılır buton.
    - `forum/templates/forum/profile_detail.html` İlanlar sekmesi yeniden
      sıralandı: "Tamamlanan ve Devam Eden Projeler" artık ilk blok (herkese,
      boşsa "Devam eden veya tamamlanmış proje bulunmuyor." mesajı), ardından
      sahibe özel "Verdiğim Teklifler". "Verdiğim Teklifler" listesinde
      5'ten sonraki satırlara `ax-profile-proposal-extra d-none` class'ı
      eklendi, `given_proposals|length > 5` ise altına "Diğer N teklifi
      göster" butonu ekleniyor.
    - JS: mevcut sayfa-altı `<script>` IIFE'sine (tab switching ile aynı
      blok) vanilla `addEventListener` ile buton tıklamasında `.ax-profile-
      proposal-extra` elemanlarından `d-none` kaldırılıyor + buton kendini
      siliyor — `forum/templates/forum/inbox.html`'deki mevcut "Diğer N
      konuşmayı göster" deseniyle birebir aynı yaklaşım (tutarlılık için),
      `data-bs-toggle` kullanılmadı.
    - CSS: `static/css/profiles.css`'e `.ax-profile-more-btn` eklendi
      (`.ax-inbox-more-btn` ile aynı görünüm, `var(--ax-*)` token'ları
      kullanıyor, hardcode renk/pixel yok).
    - Doğrulama: Docker'da `transaction.atomic()` içinde 7 geçici teklif
      (test verisi) oluşturup Django test client ile owner görünümü render
      edildi, sonra `raise` ile rollback edilip **hiçbir veri kalıcı
      yazılmadı**. Sonuç: İlanlar sekmesinde "Tamamlanan ve Devam Eden
      Projeler" artık "Verdiğim Teklifler"den ÖNCE geliyor (pozisyon
      doğrulandı), 7 teklifin ilk 5'i görünür + "Diğer 2 teklifi göster"
      butonu doğru sayıyla render edildi, boş durumda yeni mesaj metni
      çalışıyor. `docker compose restart web` + `nginx` sonrası test edildi.
    - **TAMAMLANDI — kullanıcı onayladı, `dev`'de commit edildi (66e8e3e).**
- [x] **DÜZELTİLDİ/EKLENDİ (12 Ekim 2026, henüz push edilmedi) PWA (Progressive Web App) — temel kurulum.**
  Kullanıcı mobil app ihtiyacını sordu — native (React Native/Flutter) için
  önce Django'nun üstüne ince bir JSON API katmanı (DRF) + ayrı bir app
  kod tabanı gerekir; bu aşamada önerilmedi. Bunun yerine **önce PWA**
  önerildi, kullanıcı onayladı ve plan modunda (`~/.claude/plans/
  keen-strolling-kernighan.md`) detaylandırılıp uygulandı:
  - `static/manifest.json` + `static/img/icons/` (icon-192/512/512-maskable/
    apple-touch-icon — kaynak repo kökündeki `analizus-logo-001.png`
    1024×1024, tek seferlik Pillow script'iyle üretildi, kalıcı koda
    eklenmedi) + `static/js/service-worker.js` (yalnız `/static/` altını
    stale-while-revalidate ile önbellekler, sayfa/API/WebSocket'e dokunmaz)
    + `static/js/pwa-register.js` (register) + `templates/base.html`'e
    `<link rel="manifest">`/`apple-touch-icon` + register script tag.
  - `nginx/conf.d/default.conf`'a yalnız `/static/js/service-worker.js`
    için `no-cache` override eklendi (genel `/static/` 1 yıllık immutable
    cache'in SW güncellemelerini geciktirmemesi için — ayrıntı/gerekçe
    `analizus.md` §10 "PWA" alt notunda).
  - Docker'da uçtan uca doğrulandı: `/`, `/en/`, `/de/` üçünde de manifest
    linki + register script render ediliyor, manifest.json ve 3 ikon 200
    dönüyor, SW dosyası erişilebilir; `nginx -t` (ayrı test container'ında)
    yalnız eksik gerçek SSL sertifikasında hata verdi — syntax sorunsuz.
    `docker compose exec web python -m pytest forum/tests.py -q` → 90/90
    yeşil (regresyon yok).
  - Android (Chrome): gerçek "Ana ekrana ekle/Yükle" istemi çıkar; Play
    Store listelemesi istenirse "Trusted Web Activity" ayrı/opsiyonel adım.
  - iOS (Safari): manuel "Paylaş → Ana Ekrana Ekle" gerekir.
  - **Kapsam dışı bırakıldı (bilinçli, ayrı iş):** Web Push (VAPID) — yeni
    model/migration/`pywebpush` kütüphanesi gerektirir; offline sayfa/
    navigasyon önbellekleme (dinamik/kimlik doğrulamalı site için riskli);
    Play Store/App Store native paketleme (somut talep görülürse).
  - **Deploy:** migration yok, kullanıcı "push et"/"merge et" demeden
    `main`'e gitmeyecek (nginx config değişikliği olduğu için `main`'e
    alınınca Hetzner'de `docker compose restart nginx` da gerekecek —
    GitHub Actions akışı yalnız `web`'i restart ediyor, ayrıca elle
    yapılmalı, bkz. not aşağıda).
  - [ ] **YENİ BULGU (12 Ekim 2026, PWA doğrulaması sırasında, karar
    gerektirmiyor ama araştırılmalı):** Lokal Docker'da (`DEBUG=True`)
    `django.contrib.staticfiles.storage.staticfiles_storage.url(...)`
    TÜM dosyalar için (yalnız yeni eklenenler değil, mevcut `css/bundle.css`
    dahil) hash'siz plain path döndürüyor — `{% static 'css/bundle.css' %}`
    render'da `/static/css/bundle.css` çıkıyor, oysa container içindeki
    gerçek `/app/staticfiles/staticfiles.json` manifest dosyası doğru
    hash'li adları içeriyor (`css/bundle.95b4f3ddbf19.css`). Yani whitenoise
    `CompressedManifestStaticFilesStorage`'ın hash'leme/manifest-okuma
    kısmı collectstatic'te çalışıyor ama `{% static %}` tag'i bunu
    kullanmıyor — sebep araştırılmadı (DEBUG=True'da farklı bir storage
    code path'i mi devreye giriyor, `ConfiguredStorage` lazy-wrapper'ında
    bir sorun mu var?). **Pratik etki şu an sınırlı** çünkü proje zaten her
    CSS/JS linkine elle `?v=XXXX` ekliyor (bu yüzden fark edilmemiş) — ama
    settings.py'deki 27 Eylül 2026 "whitenoise manifest-hash artık doğru
    çalışıyor" notu en azından DEBUG=True'da **yanlış/eksik** olabilir;
    production'da (DEBUG=False) farklı davranıp davranmadığı
    doğrulanmadı. PWA'nın manifest.json linkine de bu yüzden ayrıca
    `?v=0001` eklendi (hash'e güvenmek yerine).
- [ ] **(11 Ekim 2026 → Faz A tamamlandı, dev'de commit `6dd984b`, PUSH EDİLMEDİ) Claude AI Yorumu —
  tarama/analiz sonuçlarına ücretsiz AI özeti.** Amaç: Claude Startups $1000 API kredisini yeni müşteri
  kazanma + mevcut analist/kullanıcı elde tutma için aktif kullanmak. Plan: `~/.claude/plans/
  modular-bouncing-pebble.md`. Pilot kapsam: İstatistik araçları (17 test + örneklem), Bibliometrik Analiz,
  OpenAlex, PubMed. Model: Haiku 5.5. Kota: yalnız kayıtlı kullanıcı, günlük sınırlı (admin'den ayarlanır).
  **Faz A (tamamlandı, uçtan uca test edildi — gerçek API çağrısı başarılı):** `anthropic==1.13.0`
  (`requirements.txt`), `ANTHROPIC_API_KEY` env var, `forum/services/claude_service.py`
  (`ClaudeSummaryService`, hata durumunda job'u düşürmez), `SiteSettings` yeni alanlar
  (`feature_ai_summary` kapalı, `ai_summary_daily_limit_free/premium` 5/15), yeni `AIUsageLog` modeli
  (kota + token/maliyet takibi, admin'de salt-okunur liste + sidebar girdisi), migration `forum/migrations/
  0177_...`. Lokal `.env`'e anahtar eklendi, image `--build` ile yeniden oluşturuldu, 90/90 test yeşil.
  **Faz B (tamamlandı, uçtan uca gerçek API çağrısıyla test edildi — henüz commit edilmedi):**
  `istatistik/services/job_runner.py`'a `_ai_comment_for_job`/`_build_ai_prompt` eklendi — `mark_completed`'dan
  önce, flag+kota kontrolünden geçerse tek genel (tool-spesifik olmayan) prompt'la Claude çağrılıyor,
  `result_data['ai_comment']`'e yazılıyor; hata `try/except` ile job'u düşürmüyor (migration yok, `result_data`
  zaten serbest JSONField). 17 test aracının template'ine (cronbach…svm — `TOOL_CHOICES`'taki hepsi) aynı
  "AI Yorumu" kutusu (`static/css/analiz_console.css`'e eklenen 2 ortak kural, `ax-rounded-md p-3
  ax-ai-comment-box`) + aynı JS toggle deseni eklendi. **Kapsam dışı bırakıldı:** `orneklem.html` — tamamen
  senkron akış, `IstatistikJob`/`result_data`'ya hiç girmiyor, ayrı tasarım ister. EN/DE çevirisi girildi
  (`locale/en,de/LC_MESSAGES/django.po` + `.mo`); bu arada `makemessages` önceki (henüz main'e push edilmemiş)
  profil "İlanlar" turundan kalma 2 çevrilmemiş/fuzzy string'i de yakaladı (`"Devam eden veya tamamlanmış
  proje bulunmuyor."`, `"Diğer %(count)s teklifi göster"`) — bunlar da bu arada EN/DE'ye çevrildi (ayrı konu
  ama aynı dosyalarda surfaced oldu). Gerçek dosyayla uçtan uca doğrulandı (ttesti, bağımsız örneklem
  t-testi): doğru akademik TR yorum üretildi, `AIUsageLog` kaydı oluştu, test verisi/kullanıcı temizlendi.
  90/90 pytest yeşil. `feature_ai_summary` lokalde de **kapalı bırakıldı** (yalnız test sırasında geçici açılıp
  kapatıldı). **Revizyon (aynı gün):** kullanıcı gerçek ekran görüntüsüyle AI Yorumu'nun APA kutusundan kopuk
  durduğunu bildirdi, `MAX_TOKENS=1024`'e çıkarıldı (önceki 512 cümle ortasında kesiyordu) — ardından kullanıcı
  AI yorumunun APA kutusuyla **tek kutuda birleşmesini** istedi (ayrı ikon/renk/uyarı metni olmadan, APA
  cümlesinin altına ince bir ayraçla eklensin). 17 dosyanın hepsinde uygulandı: ayrı `.ax-ai-comment-box` kartı
  kaldırıldı, `ai-yorum-box`/`ai-yorum-text` artık APA kutusunun (`res-apa`/`<tool>-apa-display`) içinde, tek
  "Kopyala" butonu artık APA cümlesi + AI yorumunu birlikte panoya kopyalıyor (`copyApa` fonksiyonları
  güncellendi). 90/90 test + `manage.py check` tekrar doğrulandı.
  **Bulgu (karar bekliyor):** Test çıktısında AI yorumu 608 karakterde cümle ortasında kesildi —
  `forum/services/claude_service.py` `MAX_TOKENS=512` (Faz A) — **düzeltildi, 1024'e çıkarıldı** (kullanıcı
  onayladı), artık cümle ortasında kesilmiyor.
  **UI revizyonu (11 Ekim 2026, kullanıcı isteği):** AI Yorumu ayrı/renkli bir kutu olmaktan çıkarıldı — 17
  dosyanın hepsinde APA Formatında Raporlama kutusunun İÇİNE, APA cümlesinin altına ince bir ayraçla
  yerleştirildi; tek "Kopyala" butonu artık APA cümlesi + AI yorumunu birlikte panoya kopyalıyor.
  **Production deploy (11 Ekim 2026) — main'e merge+push edildi, Hetzner'de 3 eksik tek tek giderildi ve
  gerçek API çağrısıyla doğrulandı:** (1) `ANTHROPIC_API_KEY` production `.env`'de hiç yoktu → eklendi; (2)
  `anthropic` paketi container'da kurulu değildi (GitHub Actions deploy'u yalnız `git pull+restart` yapıyor,
  image rebuild etmiyor) → `docker compose up -d --build web` ile giderildi; (3) `feature_ai_summary` production
  admin'den açıldı. **Render (dev/staging) henüz yapılmadı** — tamamen ayrı bir ortam, `.env` dosyası okumuyor,
  `ANTHROPIC_API_KEY` Render dashboard'undan ayrıca girilmeli + orada da (muhtemelen ayrı DB) flag açılmalı;
  kullanıcı isterse ayrı görev.
  - [x] **(11 Ekim 2026 açıldı → 25 Ekim 2026 tamamlandı) AI Yorumu artık PDF raporuna da ekleniyor.**
    `istatistik/services/pdf_fonts.py`'ye ortak `append_ai_comment(story, result, style, bg_hex, box_color)`
    yardımcı fonksiyonu eklendi (APA kutusunun hemen altına, ekrandaki gibi ayrı kutu/ikon olmadan ince bir üst
    çizgiyle, aracın kendi marka rengiyle — bkz. §12 "UI" notu). 17 `istatistik/services/<tool>.py` dosyasının
    her birinin `build_pdf()`'ine 2 satır eklendi (import + çağrı, `apa_tbl` eklendikten hemen sonra). Docker
    içinde 17 aracın tamamı sentetik veriyle `analyze()`+`build_pdf()` çalıştırılıp hem `ai_comment` YOK hem VAR
    senaryosu doğrulandı (hata yok, PDF boyutu arttı) — `orneklem` kapsam dışı kaldı (zaten AI yorumu çalışmıyor).
  **Faz C tamamlandı (13 Ekim 2026) — yukarıdaki "AÇIK İŞLER" listesinin başında ayrıntılı kayıt var,
  `main`'de canlı. Sırada Faz D:** Bibliometrics (migration + `analyzer.py` ham veri yakalama — en karmaşık faz).
- [x] **(9 Ekim 2026 → tamamlandı, main'de canlı) `/hakkimizda/` sayfası sadeleştirildi.** Tek blok olduğu
  ortaya çıktı (başlık "Platformdaki Uzmanlardan Örnekler" + TeamMember kartları, admin adı "Ekip Üyeleri" aynı
  şeydi) — `forum/templates/forum/about.html` satır 276-392 kaldırıldı, yerine kısa metin + "Uzman Dizinini
  İncele" butonu (`/uzmanlar/`) eklendi. Kullanıcı kararı: `TeamMember` modeli/admin/5 kayıt **silinmedi**, yalnız
  sayfadan kaldırıldı (başka yerde kullanılmıyordu zaten, ileride lazım olursa durur). "yüzlerce uzman" ibaresi
  abartılı vaat olduğu için kullanıcı talebiyle kaldırıldı. Migration yok. Commit `be80061` (dev) → main merge
  commit `080308e`, origin/main'e push edildi (9 Ekim 2026), Hetzner GitHub Actions ile otomatik deploy tetiklendi.
- [x] **(8 Ekim 2026 → büyük ölçüde tamamlandı, commit `f320e14` dev'de, PUSH EDİLMEDİ) YÖK Tez tarama
  (`/yoktez/`) kapsamlı çalışması.** Yapılanlar: canlı YÖK sitesi incelenip "Detaylı Arama"nın (üniversite/enstitü/
  anabilim dalı) yeni arayüzün opak `kod` değeriyle çalışmadığı, eski/sayısal bir ID beklediği keşfedildi (canlı
  testle doğrulandı) — 67 üniversitelik ID haritası (`yoktez/services/yok_universities.py`) çıkarılıp forma/scraper'a
  eklendi (ID 81-260 arası taranamadı, YÖK art arda istekte bağlantıyı kesti — ileride daha yavaş bir devam taraması
  gerekebilir). Arama tamamlanınca/başarısız olunca artık otomatik e-posta + in-app `Notification` gönderiliyor
  (önceden tamamen manuel "E-posta gönder" butonuna bağlıydı — bu buton tekrar-gönder işlevi olarak duruyor).
  Sonuç gösterim penceresi 24 saatten 3 güne çıkarıldı, kullanıcıya UI'da ve e-postada bildiriliyor. `yoktez/demo/`
  S3 dosyaları için 3 günlük otomatik temizlik eklendi, günlük `cleanup-s3` cron'una bağlandı; ilk çalıştırmada
  (test sırasında, lokal/prod S3 bucket'ı paylaşıldığı ortaya çıktığı için gerçekten) Mart 2026'dan beri birikmiş
  97 eski dosya da silindi. KVKK sayfasındaki yanlış beyan ("YÖK Tez 7 günde silinir" — hiç olmuyordu) düzeltildi,
  eksik olan PubMed eklendi, YÖK Tez 3 gün olarak doğru yazıldı. Promo metnindeki "yazar/danışmana göre arama"
  iddiası (form'da hiç yoktu) gerçek kapsamla uyumlu hale getirildi. 90/90 test yeşil.
  **Kalan/ertelenen:** (1) GA4 huni analizi hâlâ yapılmadı (event tracking yok); (2) içerik derinliği/SSS/iç
  linkleme maddeleri bu oturumda ele alınmadı; (3) "Danışman" alanı forma eklenmedi (backend destekliyor ama
  kullanıcı "gerek yok" dedi); (4) yarım kalan 81-260 ID taraması; (5) deploy — kullanıcı "push et" demeden main'e
  gitmeyecek.
- [x] **(9 Ekim 2026 → tamamlandı, main'de canlı) S3 saklama süresi — tüm araçlarda tutarlı, tek merkezi
  temizlik.** Kök neden teşhisi değişti: Hetzner log'u (`/var/log/cron_cleanup_s3.log` + `docker compose logs`)
  okunduğunda trdizin'de hiç hata izi yoktu — gerçek sebep `settings.py` `LOGGING['root']['level']='WARNING'`
  idi; `trdizin`/`openalex`/`pubmed`/`bibliometrics`/`semanticscholar`/`makaleanaliz`/`tezanaliz` loggerları
  kayıtlı olmadığı için INFO logları (hem başarı hem potansiyel hata-altı bilgi) hiçbir yere yazılmıyordu.
  S3 konsolünden ölçüldü: `trdizin/full`+`orders` şu an zaten boş (muhtemelen daha önce elle temizlenmiş, 8 aylık
  dosya yoktu artık), gerçek birikim `bibliometrics` (53.5 MB, 222 gün), `tezanaliz` (13.9 MB), `makaleanaliz`
  (5.5 MB), `semanticscholar` (1.4 MB) — toplam ~74 MB. Değer çerçevesi maliyet değil **KVKK/veri saklama
  tutarlılığı** (kullanıcı: "KVKK tutarlılığı da maliyet de önemli"). **Yapılan:** `forum/s3_utils.py`'a
  `cleanup_s3_prefix(prefix, days)` (her prefix kendi try/except'inde — eski "bir prefix patlayınca kalanlar
  atlanıyor" bug'ı düzeldi, mock testle doğrulandı); 5 mevcut aracın (`openalex/trdizin/oaipmh/pubmed/yoktez`)
  cleanup fonksiyonları bu ortak yardımcıyı kullanacak şekilde sadeleştirildi (isim/imza aynı kaldı — dış çağıranlar,
  ör. `openalex/management/commands/cleanup_openalex_files.py`, bozulmadı); eksik 4 araca
  (`bibliometrics/semanticscholar/makaleanaliz/tezanaliz`) aynı desenle yeni cleanup fonksiyonu eklendi;
  `forum/api_views.cron_cleanup_s3_files` artık 9 aracın hepsini her biri kendi try/except'inde çağırıyor;
  `settings.py` LOGGING'e 7 eksik logger INFO ile eklendi. Mevcut crontab (`0 5 * * *`, Hetzner, zaten var — yeni
  cron kurulmadı) otomatik olarak yeni 4 aracı da kapsıyor. Migration yok. 12 dosya, 90/90 test yeşil. Commit
  `570be72` (dev) → main merge `080308e`, origin/main'e push edildi (9 Ekim 2026).
- [x] **(7-8 Ekim 2026 → tamamlandı)** Uzman Dizini (`/uzmanlar/`) giriş kriterleri sıkılaştırıldı — kullanıcı
  gözlemi: "bu listeye herkes girmemeli", ekran görüntüsünde 0 puanlı/Çaylak rütbeli bir kullanıcının listede
  göründüğü görülmüştü. Eski kural üç koşuldan herhangi birini yeterli sayıyordu (rank ∈ contributor+ YA DA 1 skill
  YA DA best_answers>0) — skill şartı tek başına çok gevşekti. Yeni kural (`forum/views.py` `uzman_dizini`):
  `is_public=True` + **en az 3 uzmanlık alanı** + **puan ≥ `SiteSettings.uzman_dizini_min_puan`** (admin panelinden
  ayarlanır, varsayılan 200 — Çalışma Odası eşiğiyle aynı) + `email_verified=True` + admin/staff hesapları
  varsayılan dışarıda. `Profile.directory_override` (boş/Evet/Hayır) ile admin tekil kullanıcıyı kurala bakmaksızın
  zorla gösterebilir/gizleyebilir (admin → Profil → Tercihler). Sayfa düzeni de değişti: en yüksek puanlı 10 kişi
  üstte mevcut kart tasarımıyla ("Öne Çıkan Uzmanlar", puana göre sabit), geri kalanlar altta kompakt liste
  ("Diğer Uzmanlar", "Sırala" filtresi yalnız bu listeyi etkiler). CTA'daki yanlış "500 puan → dizinde görünme"
  metni gerçek kurala göre düzeltildi. Migration `forum/0175` (iki yeni alan: `Profile.directory_override`,
  `SiteSettings.uzman_dizini_min_puan`) lokalde uygulandı, henüz deploy edilmedi. 8 yeni pytest testi + mevcut 82 →
  90/90 yeşil. Playwright ile masaüstü + mobil (390px) görsel doğrulama yapıldı (taşma/hizalama yok). **Not:**
  Bu değişiklikle production'daki "Bünyamin Keles" ve "admin" hesapları da (Yönetici rütbesi) dizinden kalkacak —
  gerçekten danışmanlık veren bir admin kalsın istenirse o profilde `directory_override=True` elle işaretlenmeli.
  **Deploy öncesi:** kullanıcı kendi bilgisayarında `scripts/yedek_indir.sh --simdi` (migration production DB'yi
  etkiler), sonra "push et"/"deploy et" denince uygulanacak.
  görünmesinin sebebi buydu). Kök neden: `static/css/style.css:30`'daki global "KESİN KONTRAST FİX" kuralı
  (`input,select,textarea{padding:10px 15px !important}`) `.forum-search-input`'un ikon için ayırdığı sol padding'i
  (`!important` içermediği için) eziyordu. Ayrıca `forum_index.html` içinde aynı sınıflar için ikinci, çakışan bir
  inline `<style>` tanımı daha vardı. Düzeltme: `trend_topics.css`'teki `.forum-search-input/-icon` kurallarına
  `!important` eklendi (padding-left 2.5rem'e çıkarıldı), şablondaki tekrarlı inline blok silindi, cache v=0003→0004.
  Playwright ile hem canlıda (önce) hem lokalde (sonra) doğrulandı, forum testleri 82/82 geçti.

> **YENİ OTURUM BURADAN BAŞLA (10 Ekim 2026, beşinci tur).** Önceki oturum (9 Ekim akşamı): **BÜYÜK SEO DÖNÜŞÜMÜ
> Faz 5 — İç linkleme tamamen kapandı, main'de canlı** (commit `a8acf35`+`c022225`+`b0a86c5`, ayrıntı aşağıdaki
> "BÜYÜK SEO DÖNÜŞÜMÜ" başlığı Faz 5). Plandaki 3 maddeden 2'sinin (footer "Hizmetler" linki, araç sayfalarındaki
> "uzmana yaptır" bandının kendisi) zaten var olduğu görüldü — gerçek iş bu bandın `/hizmetler/<slug>/`'a hiç link
> vermemesiydi. Araç sayfaları + `/analiz/` hub kategori başlıkları + sayfa sonu bant + `/uzmanlar/?cat=` artık
> ilgili hizmet sayfasına link veriyor; migration yok, 90/90 test yeşil. Ardından GSC+rakip araştırmasıyla **Faz 6
> içerik takvimine 5 maddelik somut öncelik sırası eklendi** (SPSS alternatifi, Kaplan-Meier, NVivo/MAXQDA,
> SmartPLS/SEM, etik kurul — ayrıntı aşağıda "Faz 6"). `analizus.md` §12 + §27 "#### SEO" güncellendi (commit
> `ee7f606`, yalnız doküman olduğu için `dev`'de push edilmeden bekliyor — kullanıcı istemeden push gereksiz).
> Paralel bir oturumdan da main'e 2 ayrı düzeltme geldi (ana sayfa "Akademik Tarama" kutusu: EN/DE'de tamamen
> gizliydi + eksik Semantic Scholar/PubMed linkleri — `5f7e868`, `acf06af`), bu oturumla ilgisiz, kendi başına
> belgelenmiş. **Sıradaki öncelik:** Faz 6'nın 5 maddelik sırasından ilk ikisi (SPSS alternatifi + Kaplan-Meier,
> hazır içerik yok) hızlı kazanç; yoksa "2 Ekim 2026 sonrası açık kalanlar" / "GELİR MODELİ" / "GÜVENLİ ÖDEME" /
> "AI AJAN" taslaklarından kullanıcı hangisini önceliklendirirse ondan devam.
>
> **ÖNCEKİ (7 Ekim 2026, üçüncü tur).** Bu oturum: **BÜYÜK SEO DÖNÜŞÜMÜ Faz 2 ve Faz 4
> tamamen kapandı** (ayrıntı aşağıdaki başlıkta). Faz 2: GSC redirect fix doğrulandı (canlı curl), `category_topics`
> N+1 sorgusu düzeltildi (`select_related('starter')`), blog slug/H1 uyumsuzluğu incelendi → kullanıcı kararıyla
> dokunulmadı (H1 kuralı). Faz 4: diğer 3 hizmet sayfasının içeriğinin zaten 4 Ekim'de girilip canlıya alındığı
> doğrulandı (önceden todo'da "yapılmadı" yazıyordu — stale'di), Playwright ile 4 sayfa × masaüstü/mobil taşma
> kontrolü yapıldı (hepsi OK), **15 blog kategorisi → 4 hizmet sayfası eşlemesi yeni eklendi**
> (`BlogPost.SERVICE_PAGE_BY_BLOG_CATEGORY`, `forum/models.py`) — blog yazısı sonundaki "uzman desteği" kartı artık
> eşleşen hizmet sayfasına gidiyor ve kart görünürlüğü genişletildi (önceden kart hiç göstermeyen 5 kategoride de
> artık çıkıyor). Forum testleri 82/82. **YENİ ÖNCELİK (yukarıda "AÇIK İŞLER" listesinin başında):** YÖK Tez tarama
> (`/yoktez/`) — en çok trafik/tıklama alan alan, kapsamlı iyileştirme çalışması sıradaki oturumun işi.
> **Dev → main merge edildi (kullanıcı: "sorun yoksa merge et"), Hetzner deploy kullanıcıda.**
>
> **ÖNCEKİ (2 Ekim 2026) — CANLI = main = 2416b69** (dev = 10b2cb1 + yerelde push'suz 9c8d10a
> betik/doküman commit'leri). Bu oturum (ayrıntı `analizus.md` §27 "2 Ekim 2026"): **pazar** — ilan admin onayı (onay/ret
> e-postası, panel "İlan Onayı" sekmesi), haftalık ilan hakkı normal 2 / Premium 5 (admin muaf), kategori yetenek listesi +
> "Diğer", başlık 80 / açıklama 1500 karakter + sayaç, "hizmet tanıtımı değil" kuralı; **bağış → Premium akışı düzeltildi**
> (önceden onayda Premium verilmiyordu; söz verilen gün sabit, bitiş tarihi kullanıcıya); **profil "Hakkında" kartı**;
> deploy öncesi yedek `scripts/yedek_indir.sh --simdi`. Migration forum/0165–0169 canlıda. Forum testleri 82/82.
> **Kullanıcıda bekleyen (canlı admin):** hizmet tanıtımı ilanları (189 vb.) → "Reddet: hizmet tanıtımı"; Bağışlar'da
> Tamamlandı + Verilen Premium Gün = 0 kayıt var mı (varsa Premium elle / ayrı düzeltme); eski pasif iş kategorileri;
> sunucuda kalan 2 eski `/root/yedek_*.sql` SİLİNDİ (kullanıcı, 2 Ekim). **Küçük açıklar:** ilan formundaki mavi bilgi kutusunun ilk satırı
> koyu zeminde okunmuyor; `.ax-form-select` `background-size` eksik (pubmed landing); Render'da profil fotoğrafı yüklenmiyor
> (kalıcı disk yok?); uzman profillerinin anonime açılması hâlâ ertelendi.
> Sonraki büyük iş yine **BÜYÜK SEO DÖNÜŞÜMÜ** (aşağıda): Faz 3 blog → uzman desteği kartı, araç SSS'leri, Faz 6 blog yazıları.
>
> **ÖNCEKİ NOT (1 Ekim 2026) — CANLI = main = bb85064** (dev = + docs commit'leri). Bu oturum: **BÜYÜK SEO
> DÖNÜŞÜMÜ Faz 1–2 bitti ve canlıda** (aşağıdaki başlık): 4 tarama sayfası Google başlıkları, 12 blog yazısına SEO alanları,
> veri kazıma / nitel yazıları düzeltildi, t tablosu, `/section/` 301, az konulu forum kategorisi noindex, Uzman Dizini
> `?cat=` tanıtım metinleri (+ ?cat=abc 500 düzeltmesi), analiz konsolu 18 araç tek düzen. Migration forum/0162–0164 canlıda.
> Kullanıcı GSC adımlarını yaptı (validate fix, request indexing, sitemap).
> **Sıradaki (kullanıcı önceliği: yeni sayfa açmadan metin/blog):** Faz 3 blog → uzman desteği kartı; araç SSS'lerini
> zenginleştirme (Friedman/Wilcoxon 1 soru); Faz 6 blog yazıları ("spss öğrenci ücretsiz", "spss benzeri programlar",
> "kaplan meier"). Sonra Faz 4 (5 hizmet sayfası — içerik admin modeli mi, yalnız TR mi kararları). **~29 Ekim:** GSC
> dışa aktarımı → CTR karşılaştırması. Diğer açıklar: canlı DB eski OpenAlex `error_message` anahtar kontrolü (izin
> bekliyor), `category_topics` N+1, BASE e-posta yanıtı.
>
> **ÖNCEKİ NOT (29 Eylül 2026 gece) — CANLI = main = 8393eec; dev = + docs/betik commit'leri** (doğrulandı: siteler 200, log temiz): OpenAlex 5xx bekleme + çevrili
> hata + anahtar gizleme; PubMed anahtar gizleme; DM WebSocket `@.+-` adlar; 500 hata e-postası (ADMIN_NOTIFICATION_EMAIL,
> sel koruması). Hetzner: NCBI_API_KEY eklendi, Docker log sınırı (daemon.json 20m×5, tüm container'lar), disk temizliği
> %65→%45. **`feature_pubmed` canlıda AÇIK.** Sunucu dışı yedek YAPILDI (kullanıcı: ek maliyet yok → yerel): `scripts/yedek_indir.sh` + kullanıcı crontab saatlik :15 →
> `~/yedekler/analizus/` (gzip ~55 MB, son 14; doğrulama gzip + "dump complete"; geçici PG'ye geri yükleme testi OK: 80 tablo,
> 125 kullanıcı). Log `~/yedekler/analizus/yedek.log`. Render NCBI_API_KEY tanımlı; hata e-postası canlıda sınandı (geldi).
>
> **ÖNCELİK (30 Eylül 2026): BÜYÜK SEO DÖNÜŞÜMÜ — aşağıdaki başlık, Faz 1'den başla.** Diğer adaylar: OpenAlex dergi adlarında kontrol karakteri (`_clean`); istatistik sütun adı self-XSS; Research Gap
> trend yöntemi (karar); SSS/SEO EN/DE; BASE (e-posta yanıtı bekleniyor). Doküman: `analizus.md` §3 (sunucu bakımı), §16
> (500 e-postası), §26 (yeni satırlar), §27 "29 Eylül 2026 gece".
>
> **ÖNCEKİ NOT (29 Eylül 2026 akşam):**
> - **Canlı = main = dev = c02093f** (Hetzner, 29 Eylül akşam doğrulandı: /openalex/ 200, log temiz). İçerik: OpenAlex ilk
>   sayfa + sipariş arka plan işi, PubMed modülü `feature_pubmed` KAPALI, admin'den fiyatlar, 6 tarama sayfasında XSS
>   düzeltmesi, Premium günlük 7 arama (OpenAlex/TR Dizin/YÖK Tez/PubMed), OpenAlex `block.super`.
> - **BASE:** kullanıcı Gmail'den e-posta gönderdi (IP 89.167.5.224 + UA `AnalizusBot/1.0 (mailto:info@analizus.com)`
>   beyaz liste + "non-commercial" teyidi). Yanıt gelince Hetzner'de tek curl testi → gerçek yanıtla modül planı.
>   Kararlar: DE + EN, bibliometri YOK, ilk 100 ücretsiz + fazlası proje talebi, 1 istek/sn, flag kapalı başlar.
> - **PubMed'i açmak kullanıcıda:** `/app/.env` NCBI_API_KEY (opsiyonel) + `docker compose up -d web` → admin flag.
> - **Sıradaki adaylar:** OpenAlex ham hata + 503 bekleme; dergi adlarında kontrol karakteri; istatistik sütun adı self-XSS;
>   Research Gap trend yöntemi (karar); SSS/SEO EN/DE. Sistem özeti `analizus.md` §14, §15, §20, §27 "SIRADAKİ adaylar".
> - BASE API (rbace kaynağından; resmi PDF Anubis engelli, doğrulanmadı): `func=PerformSearch`, `hits` ≤100, `offset` ≤1000
>   (sorgu başı ~1.100 kayıt), `format=json`, erişim IP + User-Agent (anahtar parametresi yok).
> - Açık kullanıcı soruları: (1) "2026 yayınları tarih/DOI varsa alınsın" netleşmedi; (2) Research Gap trend yöntemi
>   (yıllık ortalama önerisi).
> - Diğer açıklar bu listede `- [ ]`; ayrıntı `analizus.md` §14 (bibliometri), §15 (tarama), §26, §27.

**2 Ekim 2026 sonrası açık kalanlar:**
- [x] **YAPILDI (2 Ekim 2026, kullanıcı)** Canlıda hizmet tanıtımı ilanları (189 vb.) — admin "Reddet: hizmet tanıtımı" (kullanıcı kararı)
- [x] **YAPILDI (2 Ekim 2026, kullanıcı)** Canlı Bağışlar: Tamamlandı + Verilen Premium Gün = 0 kayıt var mı → varsa Premium elle ya da ayrı düzeltme (kullanıcı)
- [x] **YAPILDI (2 Ekim 2026, kullanıcı): 6 pasiften 5'i silindi (189'un virgüllü adı, C++, Java, Javascript, Google SEO hizmetleri); "Web sayfası tasarımı" pasif bırakıldı (kullanıcı kararı)** Eski kullanıcı yazımı pasif `JobCategory` kayıtları — sil / aktifleştir (kullanıcı, admin)
- [ ] Aktif iş kategorilerinin çoğunda tanıtım metni (`intro`) boş → Uzman Dizini `?cat=` sayfaları noindex (ör. Faktör analizi, R ile veri analizi, Tez danışmanlığı, Yapay zekâ modelleme, Zaman serisi). SEO Faz 3 ile birlikte metin hazırlanabilir (canlı admin; abartısız)
- [x] **YAPILDI YERELDE (2 Ekim 2026, commit yok): Davranış Analizi** — Sayfa Ziyaretleri / Ziyaret Özetleri listesinde kullanıcı adı → Navigasyon Grafiği `?user=` kişi analizi (özet kartları, bölüm + günlük grafik, son 5 gün navigasyon akışı / oturumlar, sık geçişler; ilk 20'de olmayan da açılır); "Ziyaret Özetleri" menüden kalktı; görünmeyen kart başlıkları + yanlış "Son 7 Gün" etiketi düzeltildi; testler analytics 4 + forum 82 = 86/86; Playwright masaüstü/mobil (test verisiyle) OK
- [ ] Ölü kod: `PageViewSummaryAdmin.summary_chart_view` + `templates/admin/analytics/summary_chart.html` artık linklenmiyor — silinebilir (karar)
- [ ] Navigasyon Grafiği mobilde "En Çok Ziyaret" yatay grafiğinde bazı bölüm etiketleri atlanıyor (Chart.js autoSkip; önceden de vardı; admin mobil, düşük öncelik)
- [x] **DÜZELTİLDİ (2 Ekim 2026: kutuya `color: var(--ax-text-primary)`)** İlan formu (post_job.html) mavi bilgi kutusunun ilk satırı ("…X gün aktif kalacaktır") koyu zeminde okunmuyor
- [x] **DÜZELTİLDİ (2 Ekim 2026: `background-size: var(--ax-space-3) var(--ax-space-2)`, bundle yeniden üretildi, v=0008)** `.ax-form-select` (base.css) `background-size` yok → ok simgesi kutuyu kaplıyor (pubmed landing kullanıyor)
- [ ] Render'da profil fotoğrafı yüklenmiyor (alt metin görünüyor) — kalıcı disk/medya; canlıda da var mı kontrol

**BAĞIŞ → PREMIUM AKIŞI KIRIK (2 Ekim 2026 bulgusu, kullanıcı "verilen süre doğru mu" sorusundan) — onay bekliyor:**
- [x] **DÜZELTİLDİ (2 Ekim 2026, migration forum/0167; testler 75/75)** **Admin bağışı onaylayınca Premium VERİLMİYOR** — `Donation.grant_premium()` yalnız `dashboard_approve_donation`
  (forum/views.py ~2925) çağırıyor; bu view hiçbir şablonda bağlı değil. Panel "Bağışlar/Ödemeler" → admin değişiklik
  sayfası; orada Durum=Tamamlandı yapınca sinyal/save_model yok → Premium, `premium_days_granted`, rozet, teşekkür e-postası
  hiçbiri yok. `grant_supporter_badge()` ve `emails/donation_thank_you.html` hiç çağrılmıyor (ölü kod). Canlıda tamamlanmış
  bağış + `premium_days_granted=0` kayıt var mı → Hetzner salt okuma kontrolü (kullanıcı izniyle).
- [x] **DÜZELTİLDİ (2 Ekim 2026, migration forum/0167; testler 75/75)** **Katman değişince bekleyen bağışın günü yanlış hesaplanır** — bağış talebinde `amount = tier.min_amount` (o anki),
  gün onay anında GÜNCEL katmandan `amount`'a göre bulunur. Örn. Bronz 50 TL/7 gün iken talep → katman 500 TL'ye çekildi →
  onayda 50 TL'ye uyan katman yok → 0 gün. E-postada söz verilen gün ≠ verilen gün. Çözüm: talep anında gün sayısını bağışa yaz.
- [x] **DÜZELTİLDİ (2 Ekim 2026, migration forum/0167; testler 75/75)** **Kullanıcı Premium bitiş tarihini hiçbir yerde görmüyor** — `premium_expires_at` hiçbir şablonda yok.

**Pazar / profil talepleri (kullanıcı, 2 Ekim 2026) — her biri ayrı görev, önce onay:**
- [x] **YAPILDI YERELDE (2 Ekim 2026, commit yok): Normal 2 / Premium 5 haftalık, admin → Site Ayarları → Limitler; migration forum/0165; footer + bağış e-postası dinamik (TR/EN/DE doğrulandı), forum testleri 64/64.** Eski not: İlan hakkı normal kullanıcı için 2 — şu an `Profile.get_weekly_job_limit()` (`forum/models.py` ~398): Free=1,
  Premium=3 (haftalık, son 7 gün) + referans bonusu (her 5 → +1, maks +2); sabit kodda. Netleştir: haftalık mı kalacak?
  Premium 3 kalıyor mu? Kural gereği limit `SiteSettings` alanına + admin'e taşınmalı (migration).
- [x] **YAPILDI YERELDE (2 Ekim 2026): admin onayı + onay/ret e-postası (TR/EN/DE), Site Ayarları → Limitler'den aç/kapa, 3 hazır ret gerekçesi + not, süre/ilk ilan hediyesi onay anından, reddedilen hak düşer; migration forum/0166 (veri adımı: mevcut ilanlar approved_at=created_at); forum testleri 70/70; Playwright masaüstü/mobil OK. Canlıda 189 nolu ilan için admin kararı bekliyor.** Eski not: İlan yayını admin onayına bağlı + kullanıcıya e-posta — `FreelanceJob.status` varsayılanı `'open'`, `post_job`
  (`forum/views.py` ~502) ilanı anında yayınlıyor. Gerekli: onay bekleyen durum (liste/detay/sitemap/arama'da gizli),
  admin onay/ret aksiyonu, onay ve ret e-postası (`recipient_language(user)` + çeviri), "ilanınız onaya gönderildi"
  mesajı; `expires_at` ve ilk ilan 3 gün öne çıkarma onay anından mı başlasın (karar). Mevcut açık ilanlar onaylı sayılır. Migration.
- [x] **YAPILDI (2 Ekim 2026): profilde 'Hakkında' kartı (sağ sütun, sekmelerin üstü) — biyografi + unvan/üniversite/bölüm/konum + bağlantılar (Profile.public_links: yalnız http(s), geçerli ORCID/X/GitHub); giriş yapmış herkese (anonim erişim kararı ertelendi); boşsa yalnız sahibine 'Profili Düzenle' daveti; bio kayıtta 500 karakter; testler 78/78. NOT: profilde girilen hiçbir alan (bio, akademik, bağlantılar) önceden gösterilmiyordu.** Eski not: Profilde herkese açık biyografi — `Profile.bio` alanı (TextField, 500) zaten var, `profile_edit`'te düzenleniyor;
  profil sayfasında görünürlüğü kontrol edilecek. "Herkes görebilsin" → `profile_detail` şu an `@login_required` (SEO
  planında "profil hariç şimdilik" diye ERTELENDİ) — anonim erişim mi, yalnız giriş yapmış herkese mi? karar. Kaçışlı çıktı (`linebreaks`/escape).
- [x] **YAPILDI (2 Ekim 2026): SiteSettings.job_description_max_chars (varsayılan 1500, Limitler; migration forum/0168), form doğrulaması (CRLF tek sayılır) + canlı sayaç; ilan açma formu artık hata gösteriyor.** Eski not: İlan açıklamasına karakter sınırı — `JobPostForm` açıklama alanı (form + model + sayaç). Sınır değeri karar
  (admin'den mi, sabit mi); mevcut uzun ilanlar etkilenmemeli (yalnız yeni/düzenlenen ilanlarda doğrulama).
- [x] **YAPILDI (2 Ekim 2026): ilan açma/düzenleme formunda kural kutusu (profil 'Hakkında'ya yönlendirme), açıklama placeholder'ı iş talebine yönlendiriyor, admin ret gerekçesi 'hizmet tanıtımı' + e-postada profil linki (3945e85). KALAN: canlıdaki 189 vb. mevcut ilanlar için admin kararı.** Eski not: İlan alanı "hizmet/yetenek tanıtımı"na dönüşmemeli — örnek: canlı `/market/job/189/` ("Profesyonel SPSS Veri
  Analizi & Akademik Raporlama Danışmanlığı" — kullanıcı ilan vermiyor, kendi hizmetini anlatıyor). Pazar = iş talebi;
  hizmet tanıtımı yeri profil/biyografi + Uzman Dizini. Önlemler: ilan formunda açık kural metni ("ilan = yaptırmak
  istediğiniz iş; hizmet tanıtımı profilinize"), admin onayında ret gerekçesi ("hizmet tanıtımı") + e-postada yönlendirme;
  mevcut bu türden ilanlar için admin kararı (189 dahil). Admin onayı maddesine bağlı.

**Ödeme talepleri (kullanıcı, 2 Ekim 2026):**
- [ ] **EN/DE PARA BİRİMİ + PAYPAL ENTEGRASYONU** — taslak aşağıda ("EN/DE PARA BİRİMİ + PAYPAL — TASLAK"); kod yok,
  Faz 0 öncesi 6 açık karar (§D) netleşmeli.
- [ ] **GÜVENLİ ÖDEME (emanet) + DAVET KAZANCI (%5)** — taslak hemen aşağıda ("GÜVENLİ ÖDEME — TASLAK"); kod yok,
  önce §F kararları + mali müşavir görüşü (§B1). `feature_secure_payment` kapalı başlar.
- [ ] **GELİR MODELİ — AÇIK KONU (kullanıcı, 2 Ekim 2026): "platform paraya hiç dokunmasın"** (pazaryeri/ödeme kuruluşu
  yolu elendi — iyzico reddi). Gelir yalnız platformun kendi sattığı hizmetlerden. Mevcut: ilan vitrini (250/400 TL),
  tarama siparişleri, bibliometri, Premium (bağış karşılığı — satış sayılabilir, müşavire sor), danışmanlık/eğitim.
  Seçenekler: (1) uzman Premium'u (öneri — teklif hakkı zaten Premium/rütbe/EDU ile; üstte görünme, rozet, aylık teklif
  sayısı), (2) teklif kredisi (aylık ücretsiz + satın alma), (3) ilan sahibine "acil" etiketi / uzmana doğrudan davet,
  (4) pazardan "Analizus ekibi yapsın" ile kendi hizmetlere yönlendirme. Davet: %5 nakit yerine davetlinin satın
  alımından Premium gün/kredi. Önce canlıdan son 3 ay ilan/teklif sayıları (pazar küçükse uzmandan ücret arzı kurutur).
  Karar yok, kod yok.

### GÜVENLİ ÖDEME (EMANET) + DAVET KAZANCI — TASLAK (2 Ekim 2026; BEKLEMEDE — kullanıcı: "olgunlaşmayı beklesin"; kullanıcı açmadan başlanmaz)

**Kullanıcının planı:** (1) Ödeme yöntemine "Güvenli Ödeme" seçeneği. (2) İlanda güvenli ödeme olduğu görünür; teklif
veren uzmana da bildirilir. (3) Ödeme bağıştaki IBAN'a, açıklamaya ilan kodu yazılarak yapılır. (4) Teklif kabul →
kullanıcı havale → admin ödemeyi onaylar → uzmana otomatik e-posta (süreç nasıl yürür). (5) Uzmana %10 kesintiyle ödenir.
(6) İki taraf yorum + yıldız verip iş kapandıktan sonra uzmana ödeme yapılır.
**Davet kazancı:** (1) Davet koduyla gelen kullanıcının güvenli ödemesinden davet edene %5 alacak yazılır. (2) Biriken
tutar ay sonu bildirilir, IBAN istenip ödenir. (3) Tüm adımlar ilgili kişinin onayına sunulur.

#### A. Mevcut durum (koddan, 2 Ekim 2026)
- `accept_proposal` (`forum/views.py` ~636): kabul anında ilan `in_progress`, diğer teklifler `rejected`, uzmana DM.
  Ödeme adımı yok.
- Kapanış: `JobReview.save()` (`forum/models.py` ~1100) — **iki onaylı (admin `is_approved`) yorum** olunca ilan
  `completed`. "Teslim ettim" adımı ve süre aşımı yok → taraflardan biri yorum yapmazsa iş hiç kapanmaz.
- `JobPayment` modeli = vitrin ödemesi (iyzico dönemi alanları); emanet için kullanılmaz.
- Havale deseni hazır: bağış akışı (`Donation` pending → pending_confirmation → completed, "Havaleyi yaptım" linki
  `mark_donation_transferred`, admin onayı, sinyalle ödül). Aynı desen tekrar kullanılabilir.
- IBAN `TR73 0003 2000 0000 0079 1034 65` **6 yerde sabit**: openalex/trdizin/semanticscholar/oaipmh views,
  oaipmh job_runner, `promote_job_iban.html`, `emails/support_payment_details.html`.
- Davet: `ReferralUse(referrer, referred, flagged, rewarded)`; ödül şu an Premium gün + itibar (`referral_service.py`).
- Ana sayfa (`forum/templates/forum/home.html`) uzman kartı: **"Komisyonsuz çalışın"** — %10 ile çelişir.

#### B. Görüşüm — önce netleşmesi gereken riskler
1. **Hukuki/mali (en kritik):** Başkası adına para toplayıp üçüncü kişiye aktarmak 6493 sayılı Kanun kapsamında
   "ödeme hizmeti" sayılabilir (lisans gerektirir). İki güvenli yol: (a) **Platform hizmetin satıcısı** olur — müşteriye
   tam tutar faturalanır, uzmandan hizmet alınır (serbest meslek makbuzu / gider pusulası + stopaj); "emanet" değil
   alt yüklenici modeli. (b) Lisanslı ödeme kuruluşunun pazaryeri (alt üye işyeri) ürünü (iyzico izni yok — başka
   kuruluş). **Mali müşavir/avukat görüşü olmadan canlıya alınmamalı.** Davet kazancı ödemesi de belge gerektirir.
   **Kullanıcı kararı (2 Ekim 2026): (b) pazaryeri yolu ELENDİ** — "daha önce reddedildik (iyzico), yine benzeri olur".
   Kalan: (a) platform hizmet satıcısı modeli ya da paraya hiç dokunmayan güvence (para taraflar arasında).
2. **Hesap:** Bağış ile emanet parası aynı hesapta karışır; şahıs hesabına çok sayıda üçüncü kişi havalesi banka/MASAK
   sorgusu tetikleyebilir. Ayrı hesap (tercihen şirket) + sistemde "emanette tutulan toplam" raporu.
3. **Rehin riski:** Ödeme yalnız "iki yorum + admin onayı" ile serbest kalırsa müşteri yorum yapmayarak parayı
   kilitleyebilir, uzman da teslim etmeden bekleyebilir. Şart: **teslim adımı + süre aşımı + itiraz** (§C).
4. **Değer sabitleme:** Komisyon oranı ve tutarlar talep (kabul) anında kayda yazılmalı (bağış `premium_days_promised`
   dersi) — oran sonradan admin'de değişse de söz verilen geçerli.
5. **Kötüye kullanım:** Davet eden kişi, davet ettiği müşterinin işini uzman olarak alırsa %5 almamalı (kendi kendine
   komisyon). `flagged` davetler kazanç üretmez. Davet kazancı ödeme onayında değil **iş kapanınca** yazılmalı (iade riski).
6. **Akademik etik:** Platform ödemeden pay alınca ilan içeriğinden sorumluluğu artar — güvenli ödemeli ilanlarda
   "tez/ödev yazdırma" ret kuralı sıkı uygulanmalı (ilan onayı zaten var).
7. **Çok dil:** TL + TR IBAN; EN/DE kullanıcısına ilk sürümde gösterilmesin mi? (karar)

#### C. Önerilen akış
**İlan:** İlan formunda "Güvenli Ödeme ile ödeyeceğim" seçeneği + Güvenli Ödeme Koşulları onay kutusu →
`FreelanceJob.secure_payment` (+ `secure_terms_accepted_at`). Liste/detayda "Güvenli Ödeme" rozeti.
**Teklif:** Güvenli ödemeli ilanda teklif formunda canlı hesap: "Teklif 1.000 TL → %10 hizmet bedeli 100 TL → size
ödenecek 900 TL" + onay kutusu (`JobProposal.secure_terms_accepted_at`).
**Durum makinesi — yeni `SecurePayment` modeli (ilan başına bir kayıt):**

| Durum | Ne olur | Kim |
|---|---|---|
| `awaiting_payment` | Kabul anında oluşur; tutar/oran/net sabitlenir; müşteriye IBAN + tutar + açıklama kodu (ör. `ANZ-2026-0042`, `reference_number`'dan) ekranda + e-postada; uzmana "kabul edildi, ödeme onayını bekleyin — işe başlamayın" | sistem |
| `payment_reported` | Müşteri "Havaleyi yaptım" → admin bildirimi | müşteri |
| `funded` | Admin havaleyi görür, onaylar → **sinyal**: uzmana "ödeme güvencede, süreç" e-postası, müşteriye "ödemeniz alındı"; ilan `in_progress` | admin |
| `delivered` | Uzman "İşi teslim ettim" → müşteriye e-posta: X gün içinde yorum ya da itiraz | uzman |
| `completed` | İki yorum (veya süre aşımında itiraz yoksa otomatik) → ödeme serbest | sistem |
| `payout_ready` → `paid_out` | Uzman ödeme bilgisini (ad soyad + IBAN) onaylar → admin havale eder, "ödendi" işaretler → uzmana döküm e-postası (brüt / %10 / net) | uzman + admin |
| `expired` | X gün içinde ödeme yoksa kabul düşer, ilan yeniden açılır (karar) | cron |
| `disputed` → `refunded` / `paid_out` | Taraflardan biri itiraz eder → admin karar verir (tam/kısmi iade) | admin |

- Uzmana giden "süreç" e-postası içeriği (madde 4): ödeme güvencede/işe başla; iletişim platform mesajlarında;
  teslim "İşi teslim ettim" butonuyla; müşteri onayı + karşılıklı yorum; süre aşımı kuralı; %10 kesinti ve net tutar;
  ödeme zamanı ve IBAN istenmesi; itiraz yolu.
- Kural uyumu: durum geçişleri sinyalde, admin aksiyonu kayıt kayıt `save()`; e-postalar `recipient_language(user)`
  + TR/EN/DE çeviri; tutarlar `Decimal` + kuruşa `ROUND_HALF_UP`.
- **Ayarlar (`SiteSettings`, sabit kod yok):** `secure_payment_commission_rate` (10), `payment_iban`,
  `payment_account_holder`, `secure_payment_deadline_days`, `delivery_review_days`, `referral_commission_rate` (5),
  `referral_min_payout`. IBAN'ın 6 kopyası bu alana taşınır (ayrı küçük görev).
- **Admin:** `SecurePayment` admin + panelde "Güvenli Ödeme" sekmesi (onay bekleyen havaleler / ödenecek uzmanlar /
  itirazlar / emanette tutulan toplam / ay komisyonu).
- **IBAN verisi (KVKK):** Profilde kalıcı tutulmaz; yalnız ödeme kaydında, TR IBAN mod-97 doğrulaması; gizlilik
  politikasına ek.

#### D. Davet kazancı
- Yeni `ReferralEarning`: referrer, `ReferralUse`, `SecurePayment` (tekil), taban tutar, oran (sabitlenmiş), tutar,
  durum `accrued` → `payout_requested` → `paid` / `cancelled`.
- Tetik: güvenli ödeme `completed` olunca; koşul: ödeyen (`job.owner`) davetli, davet `flagged` değil, referrer ≠ uzman.
- Ay sonu: cron uç noktası (mevcut cron anahtar deseni) → bakiyesi olan her referrer'a e-posta; eşik altı devreder.
  E-postadaki link → `referral_dashboard`'da "Kazançlarım" tablosu + "Ödeme talep et" (ad soyad + IBAN + onay) →
  admin listesine düşer → havale + "ödendi" → e-posta.

#### E. Onaylar (madde 3) — her adımda ilgili kişinin açık onayı, zaman damgasıyla
- İlan sahibi: ilan açarken koşullar; teklif kabulünde özet ekranı (tutar, IBAN, ödeme süresi) "Onaylıyorum".
- Uzman: teklif verirken komisyon + net tutar; ödeme aşamasında IBAN beyanı.
- Davet eden: ödeme yalnız kendi talebiyle (IBAN beyanı) — otomatik havale yok.
- Yeni sayfa: **"Güvenli Ödeme Koşulları"** (hukuki metin — kullanıcı/hukukçu yazar; abartılı vaat yok).

#### F. Açık kararlar (kullanıcı)
1. Hukuki/mali model (§B1) ve hangi hesap (bağışla aynı mı, şirket mi)?
2. Ödeme süresi (öneri 3 gün) dolunca: kabul düşer + ilan yeniden açılır mı?
3. Diğer teklifler kabul anında mı, ödeme onayında mı reddedilsin? (Öneri: ödeme onayında — müşteri ödemezse başka
   teklife geçebilir.)
4. Teslim sonrası yorum süresi (öneri 7 gün) ve süre aşımında otomatik kapanış — onay?
5. İade/itiraz politikası: uzman teslim etmezse tam iade; kısmi iade olacak mı; iadede %10 kesilir mi?
6. Yorumların admin onayı ödemeyi geciktirir — güvenli ödemede yorum onayı beklenmeden mi kapansın?
7. Davet %5: **brüt tutarın %5'i mi** (komisyonun yarısı) **yoksa komisyonun %5'i mi**? Yalnız davetli müşteri mi, davetli
   uzmanın kazancı da sayılır mı? Süresiz mi (ör. ilk 12 ay)?
8. Asgari ödeme eşiği (davet kazancı)?
9. Mevcut davet Premium gün ödülü kalıyor mu (ek) yoksa kalkıyor mu?
10. EN/DE'de güvenli ödeme gösterilsin mi?
11. "Komisyonsuz çalışın" metni → "Doğrudan anlaşmada komisyon yok; Güvenli Ödeme'de %10 hizmet bedeli" gibi?

#### G. Uygulama fazları (her faz ayrı onay; migration'lı fazlar canlı DB'yi etkiler)
- [ ] Faz 0 — Kararlar (§F) + müşavir görüşü + Koşullar metni; `SiteSettings` alanları + IBAN taşıma (migration)
- [ ] Faz 1 — Modeller: `FreelanceJob.secure_payment`, ilan durumu `awaiting_payment`, `SecurePayment` + admin (migration)
- [ ] Faz 2 — İlan formu seçeneği + rozet; teklif formu net hesap + onay kutuları
- [ ] Faz 3 — Kabul → ödeme talimatı (ekran + e-posta) → "Havaleyi yaptım" → admin onayı → sinyal e-postaları
- [ ] Faz 4 — Teslim / yorum / süre aşımı cron'u / itiraz
- [ ] Faz 5 — Uzman ödeme bilgisi + "ödendi" + döküm e-postası; panel "Güvenli Ödeme" sekmesi
- [ ] Faz 6 — Davet kazancı + aylık cron + talep formu + dashboard tablosu
- [ ] Faz 7 — Testler (durum geçişleri, yetki, tutar yuvarlama, kötüye kullanım), TR/EN/DE çeviri, `analizus.md`

### EN/DE PARA BİRİMİ + PAYPAL — TASLAK (19 Ekim 2026; BEKLEMEDE — §D kararları netleşmeden kod yok)

**Kaynak:** Kullanıcı EN/DE "Create a New Job Listing" formunda (`/en/market/new/`) "Budget (TRY)" etiketini fark etti
(ekran görüntüsü); ardından "Become a Premium Member" bağış modalındaki TL fiyatların da aynı sorunu taşıdığını belirtip
EN/DE kullanıcılar için PayPal entegrasyonunu gündeme getirdi.

#### A. Bulunan sorunlar (koddan, 19 Ekim 2026)
1. **`budget_max` etiketi yanlış çevrilmiş, gerçek dönüşüm yok.** `forum/forms.py:152`
   `JobPostForm.Meta.labels['budget_max'] = gettext_lazy('Bütçe (TL)')` — EN/DE `.po` çevirileri
   (`locale/en/LC_MESSAGES/django.po:2089`, `locale/de/...:2136`) "TL" yerine yanlışlıkla "TRY" yazmış ama para birimi
   hâlâ Türk Lirası; tek `JobPostForm` her dilde aynı alanı kullanıyor, dil bazlı currency ayrımı/dönüşüm yok (benzer
   sorun: "Teklifiniz (TL)" `forms.py:210`, "Teklif Tutarı (TL)" `forms.py:215`). `FreelanceJob.language` alanı
   (4388762 commit, intl market) yalnız ilan havuzunu ayırıyor, currency kavramı hiç eklenmemiş.
2. **Bağış/Premium modalında da aynı sorun.** "Become a Premium Member" (`DonationTier`: 500/1250/2500/5000 TL
   paketleri, `forum/models.py:1286`) EN/DE kullanıcıya da TL gösteriyor. `Donation.amount` (`forum/models.py:1323`)
   yalnız TL alanı, currency alanı yok.
3. Kapsam dışı ama ilişkili not: `job_detail.html:36` JSON-LD `"currency": "TRY"` sabit; `job_list.html`/
   `job_detail.html`'de tutar gösterilirken `₺{{ amount }}` sembolü dil fark etmeksizin sabit basılıyor.

#### B. Kullanıcı kararı — ödeme yöntemi
- EN/DE kullanıcılar için **PayPal tam API entegrasyonu** (Checkout + webhook, otomatik premium aktivasyonu) —
  manuel PayPal.me değil.
- Alıcı (merchant) hesabı **Türkiye'deki Analizus şirketine değil, Almanya'da yaşayan bir kişiye ait PayPal Business
  hesabına** bağlı olacak — bu, PayPal'ın Türkiye'deki lisans engelini (2016 BDDK reddi, bkz. TechCrunch/FinTech
  Futures haberleri) devre dışı bırakıyor; alıcı taraf zaten AB'de olduğu için bu engel geçerli değil.
- Admin panelinde bağış gelirlerini **EUR olarak ayrı takip** edecek bir ekleme istendi.
- Kapsam: en azından "Become a Premium Member" bağış/premium akışı. İş ilanı bütçesi (`budget_max`) alanının aynı
  turda ele alınıp alınmayacağı netleşmedi (açık karar, §D.3).

#### C. Maliyet notu (doğrulanmamış, üçüncü parti kaynaklara dayalı — resmi PayPal sayfasından teyit edilmedi)
- PayPal API/SDK/sandbox kullanımı ücretsiz; yalnızca gerçekleşen işlemlerden komisyon kesilir.
- Almanya merchant hesabı tahmini oranlar: AB içi alıcı ~%2.49 + 0.35€; AB dışı alıcı (ör. ABD/UK) +%1.29 sürşarj;
  EUR dışı para birimiyle ödemede +%3–4 döviz çevrim ücreti. Kesin oran, Almanya'daki hesap sahibinin PayPal
  panelinden ("Satıcı Ücretleri") doğrulanmalı.

#### D. Açık kararlar (kullanıcı)
1. Almanya'daki hesap sahibi kim olacak, PayPal Business hesabı zaten var mı yoksa yeni mi açılacak?
2. EUR paket fiyatları ne olacak — mevcut TL tutarların (500/1250/2500/5000) sabit bir kurla çevrimi mi, yoksa
   ayrı/yuvarlak EUR fiyatlar mı (ör. 15€/35€/70€/140€) belirlenecek?
3. Bu tur yalnız Premium/bağış modalını mı kapsayacak, yoksa iş ilanı `budget_max` (Bütçe) alanı da aynı anda mı
   ele alınacak?
4. Almanya'daki kişiden API kimlik bilgileri (Client ID + Secret, webhook URL kurulumu) ne zaman temin edilecek —
   Faz 0'ın ön koşulu.
5. Admin'deki "EUR bağış geliri" raporu nasıl görünsün (ayrı tablo/filtre mi, toplam kartı mı)?
6. EN/DE kullanıcıya hâlâ TL seçeneği (banka havalesi) gösterilsin mi, yoksa PayPal tek seçenek mi olacak?

#### E. Uygulama fazları (her faz ayrı onay; migration'lı fazlar canlı DB'yi etkiler)
- [ ] Faz 0 — Kararlar (§D) netleşir; Almanya'daki hesaptan PayPal Business + Client ID/Secret/webhook URL alınır;
  `.env`'e `PAYPAL_*` eklenir (commit'e dahil edilmez)
- [ ] Faz 1 — Model: `Donation`'a `currency` alanı (TRY/EUR) + `DonationTier`'a EUR karşılığı alanı (migration)
- [ ] Faz 2 — PayPal Checkout entegrasyonu (EN/DE'de "Become a Premium Member" modalında PayPal butonu; TR'de
  mevcut IBAN akışı değişmez)
- [ ] Faz 3 — Webhook endpoint (ödeme onayında `Donation.status` → `completed`, mevcut sinyal/e-posta akışı
  tetiklenir — `premium_days_promised` deseni korunur, tutar talep anında kayda sabitlenir)
- [ ] Faz 4 — Admin: `DonationAdmin`'e currency filtresi + EUR toplam raporu
- [ ] Faz 5 — Testler (webhook imza doğrulama, durum geçişleri, yuvarlama), TR/EN/DE çeviri, `analizus.md` güncelleme
- [ ] (Ayrı karar bekliyor, §D.3) — kapsam genişlerse: `budget_max` dile göre doğru etiket/currency (forms.py +
  migration, ayrı görev olarak ele alınmalı)

### AI AJAN İLE SİTE YÖNETİMİ — TASLAK (2 Ekim 2026; BEKLEMEDE — §E kararları netleşmeden kod yok)

**Kullanıcının isteği:** analizus.com ekosistemini bir AI ajan yönetsin — gerektiğinde admin gibi davransın, istisnai
durumlarda e-posta / DM ile kullanıcıya danışsın, SEO girdisi yapsın, konsolu kontrol etsin, kod üretsin.
**Görüş:** mümkün; ama "tam yetkili otonom admin" değil — **katmanlı yetki + onay kuyruğu + her adım denetim kaydında**.

#### A. Mimari (beyin / eller / ağız)
- **Beyin (Claude):** DB'ye ve sunucu shell'ine doğrudan dokunmaz; yalnız anahtarla korunan, beyaz listeli uçları çağırır.
  - Seçenek A (öneri, başlangıç): **Claude Code routine'leri** (bulutta zamanlanmış ajan; repo erişimi var, sunucu gerekmez).
  - Seçenek B (sonra, gerekirse): Hetzner'de **Claude Agent SDK** container'ı — 7/24, olay güdümlü (yeni ilan anında);
    bakım + API token ücreti. Routine'lerin ücretlendirmesi, dış ağ ve sır (anahtar) yönetimi kurulumda doğrulanacak.
- **Eller (Django):** "Ajan API'si" — salt okunur uçlar (günlük özet: 500 hatalar, bekleyen ilan/bağış, job_queue
  hataları, AI kotası, disk/yedek) + `AgentAction` modeli (ne, neden, önce/sonra, durum: önerildi/onaylandı/uygulandı/
  reddedildi/geri alındı). Onaylanan eylemi **Django uygular** (ajan değil) — mevcut `save()` / sinyal akışıyla
  (ilan pending→open, bağış→completed; `queryset.update` değil). Anahtar `hmac.compare_digest` (cron anahtarı gibi).
- **Ağız (iletişim):** e-postada imzalı, tek kullanımlık, 48 saat geçerli onay linki → staff girişli **onay sayfası +
  POST düğmesi** (GET doğrudan uygulamaz — Gmail/güvenlik tarayıcıları linki önceden açabilir) + aynı istek AnalizBot'tan
  kullanıcıya site DM'i.
- **Acil fren:** `feature_ai_agent` flag'i (SiteSettings); günlük otomatik eylem sınırı admin → Limitler (kodda sabit yok).

#### B. Yetki seviyeleri
- **Serbest (okuma + taslak):** günlük durum raporu, GSC analizi, `meta_title`/`meta_description` önerisi, blog taslağı
  (`draft`), todo'ya madde.
- **Yap + bildir:** `agent/*` dalında kod + PR açma, spam şüphesi işaretleme.
- **Önce sor:** ilan onay/ret, bağış onayı, kullanıcıya e-posta, yayındaki blog/SEO alanını değiştirme, fiyat/limit,
  PR'ı dev'e alma.
- **Asla:** main'e merge, Hetzner deploy, canlıda migration, kullanıcı silme, `.env`, sunucu shell'i.
- Bir iş haftalarca doğru karar verirse bir üst seviyeye taşınabilir (ör. ilan onayı "önce sor"dan başlar).

#### C. Riskler / kurallar
- **Prompt injection:** ajan kullanıcı içeriği (forum, ilan, DM) okur → içerikteki "talimat"a göre eylem yok; kullanıcı
  içeriğini okuduğu her işte eylem yetkisi dar.
- Para / güven / analiz sonuçları geri dönüşü zor → insan onayı. "Hızlı değil, doğru."
- SEO/blog metinlerinde **abartılı vaat yok** kuralı ajan talimatına yazılır; her iddia koddan doğrulanır.
- Ajan Django superuser değil — ayrı hesap / dar yetkili token.

#### D. Fazlar (her faz ayrı onay)
- [ ] Faz 1 — Gözlemci (1–2 hafta): Ajan API'si salt okunur uçlar + her sabah durum e-postası; eylem yok
- [ ] Faz 2 — Önerici: `AgentAction` + onay linki/sayfası + AnalizBot DM + `feature_ai_agent` (migration — canlı DB)
- [ ] Faz 3 — SEO: GSC API (şu an elle zip) → haftalık analiz, meta önerileri, taslak blog
- [ ] Faz 4 — Kodlayıcı: todo'daki küçük işler / hata e-postaları → `agent/*` dalı + test + PR
- [ ] Faz 5 — Sınırlı otonomi: kendini kanıtlamış işler "yap + bildir"e
- [ ] Her fazda testler + `analizus.md` güncellemesi

#### E. Açık kararlar (kullanıcı)
1. Beyin: Seçenek A (routine) ile başlansın mı?
2. Onay kanalı: e-posta, site DM'i, ikisi birden?
3. "Asla" listesine eklenecek / çıkarılacak iş var mı?
4. Aylık bütçe?

### BÜYÜK SEO DÖNÜŞÜMÜ — PLAN (30 Eylül 2026; ÖNCELİK — faz faz, her faz önce onay)
**Hedef:** portal = analiz/danışmanlık ihtiyacı olanlar ↔ analistler (tez merkezleri, AI mühendisleri, istatistikçiler,
eğitmenler). Kapsam: akademik danışmanlık, etik kurul, tez önerisi, metin editörlüğü, makale danışmanlığı, metodoloji ve
analiz (Excel, EViews, SPSS, SmartPLS, Power BI, Tableau, Python, ML/DL/NLP, AI agentic, MAXQDA, NVivo, konu analizi,
geçerlilik-güvenirlik, içerik analizi, fark/regresyon/korelasyon), proje danışmanlığı.

**Başlangıç ölçümü (GSC son 3 ay, 30 Eylül 2026):** 459 tık, 34,3 bin gösterim, CTR %1,3, ort. sıra 7,7. Gösterim Ağustos
sonundan beri ~4× (günde ~250 → ~1.000), tık yerinde sayıyor. Tık dağılımı: blog 258 (%56), tarama 78, forum 58, araçlar 27,
eğitim 7, EN/DE 0. %94 Türkiye, ~%70 masaüstü. Hizmet niyetli sorgu (danışmanlık/yaptırma/ücret/SmartPLS/NVivo/etik kurul) = 0.
İndeksleme: 262 indeksli / 377 değil — çoğu bilinçli (robots 192, alternatif canonical 97, yönlendirme 32, noindex 31); gerçek
sorun ~25 sayfa (Faz 2). Yapılandırılmış veri hatası 0 (Temmuz'da 1 sayfa, geçti). Ham GSC zip'i proje kökünde — commit'lenmez.

**Verilen kararlar (30 Eylül 2026):** navbar DEĞİŞMEZ (Pazaryeri düz link kalır); 15 değil **5 küme hizmet sayfası**; alt hizmet
ayrı sayfaya ancak GSC talep gösterince; "tez yazdırma / ödev yaptırma" niyeti hedeflenmez; şehir × hizmet programatik sayfa
yok; ilanlara JobPosting şeması yok (Google yalnız istihdam için); `/analiz/` = "kendin yap, ücretsiz", `/hizmetler/nicel-analiz/`
= "uzmana yaptır" (title/H1 ayrı — yamyamlık önlemi). **ERTELENDİ (kullanıcı: "profil hariç şimdilik"):** uzman profillerinin
anonime açılması — `profile_detail` `@login_required` → Google profilleri göremiyor (login'e yönleniyor → robots engeli).

**Faz 1 — CTR hızlı kazanç (yalnız title/meta, migration yok)**
- **CANLIDA (1 Ekim 2026, main = 37e2720; 0162 + 0163 uygulandı):** dışarıdan doğrulandı — 4 tarama sayfası + EN OpenAlex yeni
  başlık, blog SEO başlıkları, t tablosu, veri kazıma ve nitel içerikleri yeni. Nitel yazısı SEO alanları kullanıcı tarafından admin'den girildi (canlıda doğrulandı, 1 Ekim). **Kullanıcı (1 Ekim):**
  GSC Validate fix (redirect error, Google farklı canonical, taranmış-indekslenmemiş), 9 URL Request indexing, sitemap yeniden
  gönderildi; `feature_tezanaliz` kontrol edildi. Ölçüm başlangıcı: 1 Ekim 2026 → 29 Ekim'de GSC karşılaştırması.
- [x] **YAPILDI YERELDE (30 Eylül 2026, commit yok):** anonim (Googlebot) `service_promo.html` görür → başlık/açıklama/H1 view'daki `promo_title`/`promo_description`'dan; 4 view + landing.html (girişli) + OpenAlex EN/DE po + SSS "OpenAlex nedir?"; anonim doğrulandı (TR/EN/DE), forum 61/61. Eski not: Tarama sayfaları: `/yoktez/` (8.748 gösterim, CTR %0,4, sıra 7,5), `/trdizin/`, `/oaipmh/` (~1.500'er, CTR ~%1),
  `/openalex/` — resmî siteden farkı söyleyen title + meta (toplu tarama, Excel'e aktarma, filtre)
- [x] **YAPILDI YERELDE (1 Ekim 2026, commit yok):** veri migration `forum/0162_blog_seo_meta_ctr` — 6 yazıya `meta_title`/`meta_description` (alan doluysa dokunmaz; geri alma yalnız kendi değerini siler); sayfadaki başlık/içerik/slug aynı. Yerel ileri-geri-ileri OK, anonim `<title>` doğrulandı. Örneklem (CTR %3,7) ve ANOVA (%6,7) bilinçli dokunulmadı. **Deploy: migration'lı → önce DB yedeği.** KALAN: "t tablosu" (408 gösterim, niyet = kritik değer tablosu) → t-testi yazısına t dağılım tablosu bölümü (öneri, onay bekliyor). Eski not: En çok gösterim alan blog yazıları: AFA/DFA (3.091), Cronbach ×2 (2.150 + 1.384), örneklem (2.096), t tablosu (1.062),
  normallik ×2 (900 + 706), VIF (655) — 0 tık alan sorgulara uygun title ("afa nedir" 230, "dfa" 225, "cronbach alfa nedir",
  "t tablosu" 408 gösterim/1 tık)
- [x] **YAPILDI YERELDE (1 Ekim 2026, commit yok): veri migration `forum/0163_blog_seo_icerik_duzeltme`** — korumalı (beklenen eski
  metin yoksa dokunmaz): (1) 6 yazıya SEO başlık/açıklama (t-testi, SPSS alternatifi, survival, Shapiro 0.049, veri kazıma, nitel);
  (2) veri kazıma yazısı yeniden yazıldı — "Neden Veri Kazımıyor?" çelişkisi ve gerçek dışı "ULAKBİM kurumsal protokolü" iddiası
  çıktı; kullanıcı: "veri kazıyoruz ama kısıtlı; künye/özetlerden içerik ve konu analizi" → "Sınırlı ve Amaca Yönelik Kazıma" +
  "Metinsel Analizler" (Tez Analizi: TF-IDF, LDA, benzer tezler; tam metin için proje talebi); abartılı vaatler (binlerce tez,
  .csv, 250M) düzeltildi; arXiv numarası 2205.01833; (3) nitel yazısı: yapay zekâ sohbet artığı cümle, tekrarlı H2, kod bloğuna
  dönüşmüş liste düzeltildi, kaynaksız "makale kanıtlıyor" çıktı (~400 kelime — hâlâ kısa); (4) t-testi yazısına t dağılımı
  kritik değer tablosu (scipy, df 1–120 + ∞). Yerel: uygula + rollback'te nitel testi + idempotent ikinci çalıştırma OK; anonim
  render doğrulandı. **AÇIK:** canlıda `feature_tezanaliz` açık mı (yazı Tez Analizi'ni anlatıyor) — kullanıcıya soruldu.
- [ ] 4 hafta sonra aynı sayfalarda CTR karşılaştırması (GSC dışa aktarımı)

**Faz 2 — İndeksleme temizliği**
- [x] **DOĞRULANDI (7 Ekim 2026, canlı curl ile):** GSC "Redirect error" → `analizus.com/egitim/`, `/proje-talebi/` tek 301 → 200 (REDIRECTS: 1, HTTP_CODE: 200).
- [x] **YAPILDI YERELDE (1 Ekim 2026, commit yok): migration `forum/0164_jobcategory_intro`** (şema + veri) — `JobCategory.intro`
  (admin'den düzenlenir), 20 kategoriye başlığa göre tanıtım metni (alan doluysa dokunmaz). `?cat=N`: title "Uzman Bul: {kategori}",
  H1 + tanıtım metni, meta açıklama metinden; **index yalnız metin dolu ve ≥2 uzman** varsa, yoksa noindex. **Canlı 500 düzeltildi:**
  `?cat=abc` (sayı olmayan) filtrede çöküyordu → olmayan/pasif/geçersiz kimlik 301 `/uzmanlar/`. Test: geçici kayıtlarla 8 senaryo,
  admin liste/form 200, forum 61/61. Eski not: `/uzmanlar/?cat=N` — "Google chose different canonical" (5 sayfa): kendini canonical gösteriyor ama title/içerik
  `/uzmanlar/` ile aynı → kategoriye özgü title/H1/2 cümle giriş; <2 uzman → `noindex` + canonical `/uzmanlar/` (Faz 4 ile)
- [x] **YAPILDI YERELDE (1 Ekim 2026, commit yok):** `section_detail` → 301 `/forum/#section-<pk>` (forum ana sayfası bölümleri zaten listeliyor; yok olan pk 404; test: geçici bölümle 301 + çapa var, forum 61/61). Şablon `section_detail.html` artık kullanılmıyor (silinmedi). Eski not: `/section/<pk>/` — title ana sayfayla aynı, ~330 kelime ("Crawled – not indexed") → kendi title/meta ya da `noindex` (karar)
- [x] **YAPILDI (7 Ekim 2026, commit yok):** `category_topics` N+1 düzeltildi — `forum/views.py` `select_related('starter')`
  eklendi (`.prefetch_related('tags')` yanına). Tek satır. Forum testleri 82/82.
- [x] **YAPILDI YERELDE (1 Ekim 2026, commit yok):** `Category.INDEX_MIN_TOPICS = 3` — altındaki kategori sayfası `noindex, follow`
  + `CategorySitemap` dışı; konu eklenince kendiliğinden açılır. Ek sorgu yok (len() queryset önbelleği). Test: 1 konulu noindex,
  3 konulu index, sitemap yalnız 3 konulu; forum 61/61. Eski not: Boş forum kategorileri (`/forum/panel-veri-analizi/`, `/zaman-serisi-analizi/`, `/veri-temizleme/`, `/bibliometrik-analizler/`
  ~220 kelime) → konu sayısı eşiğin altında `noindex` (eşik kararı)
- [x] **KARAR (7 Ekim 2026, kullanıcı: "hiçbir şeye dokunma"):** `/blog/nitel-arastirma-yontemleri/` incelendi — H1
  "Nitel Araştırma Yöntemleri" genel/placeholder kalmış ama gövde tamamen "30 dakikalık kısa nitel mülakat" konusunda;
  canlı `meta_title`/`meta_description` ("Kısa Nitel Mülakat: 30 Dakikada Etkili Görüşme Rehberi…") zaten içerikle uyumlu
  — asıl uyumsuz olan H1. CLAUDE.md kuralı H1/slug'a dokunmayı yasaklıyor (sıralama kaybı) → bilinçli dokunulmadı, madde kapandı.
- Dokunulmayacak (normal): robots engelli `/login/?next=`, `/forum/*/new/`, `/market/job/*/bookmark/`; `/market/?category=`
  canonical `/market/`; `/istatistik/*` 301 → `/analiz/*`

**Faz 3 — Blog → hizmet köprüsü (trafiğin %56'sı blogda)**
- [x] **YAPILDI YERELDE (4 Ekim 2026, commit yok): blog yazısı sonunda "Bu konuda uzman desteği" kartı** —
  hedef `/uzmanlar/?cat=` (ilan açma değil, doğrudan uzman dizini; gerekçe: `/market/` kategori ön-seçimini
  desteklemiyor, `/proje-talebi/` sabit hizmet türü listesiyle blog konularına uymuyor, dizin zaten ≥2 uzman
  kontrolüne sahip). `BlogPost.EXPERT_CATEGORY_BY_BLOG_CATEGORY` (forum/models.py) — 15 kategoriden 10'u
  JobCategory'e eşlendi (SPSS rehberleri→SPSS ile veri analizi, Tez süreci→Tez danışmanlığı, Ekonometri→EViews,
  Açık Bilim/Veri Güvenliği-Araştırma Etiği/Akademik Etik&AI→Etik kurul desteği, Sağlık İstatistiği→SPSS,
  İstatistik(-101)→Akademik danışmanlık, Veri Kazıma→Python ile veri analizi); 5'i (Bilim Felsefesi&Metodoloji,
  Akademik Kariyer&Etik, Bibliometri&Türkiye'de Bilim, Veri Güvenliği&Etik, Sağlık Verisi&Bilim Politikası) net
  karşılığı olmadığı için eşlenmedi → kart basılmaz (kullanıcı onayladı). `forum/views.py` `blog_detail`:
  eşleşen JobCategory `is_active` + ≥2 herkese açık uzman (skill) şartı (uzman_dizini'ndeki aynı eşik) —
  sağlanmazsa kart yok. Kart `ax-tool-guide`/`ax-btn` (service_promo.html'deki "uzmana bırak" bandıyla aynı
  desen), `{% trans %}`/`{% blocktrans %}` ile EN/DE locale'e eklendi (blog `forum.urls` i18n_patterns dışında
  olduğu için şu an yalnız TR'de görünür — ileride i18n'e alınırsa hazır). Doğrulama: forum 82/82, oturumsuz
  `curl` ile eşleşen kategoride kart+doğru link (`/uzmanlar/?cat=<id>`), eşleşmeyen kategoride kart yok, <2
  uzmanda kart yok (yerel geçici veriyle test edilip temizlendi — canlıda JobCategory verisi farklı, admin
  panelinden alınan güncel liste kullanıldı). Faz 4 hizmet sayfaları açılınca kart hedefi `/hizmetler/<slug>`'a
  taşınabilir.

**Faz 4 — 4 hizmet sayfası (4 Ekim 2026'da gözden geçirildi, kullanıcıyla mockup üzerinden netleşti)**
> **KARARLAR (4 Ekim 2026):**
> - **5 değil 4 hizmet sayfası** — `proje-danismanligi` ÇIKARILDI: navbardaki mevcut "Proje Talebi" linkiyle
>   (`ProjectRequest` formu, `forum/views.py` `proje_talebi`) isim/niyet çakışıyordu, iki rakip akış YALIN ilkesine
>   aykırıydı. Kalan 4: `akademik-danismanlik`, `nicel-analiz`, `nitel-analiz`, `veri-ve-yapay-zeka`.
> - **İçerik yeri: admin modeli + migration** (onaylandı) — `JobCategory.intro` deseni (`forum/models.py` ~875,
>   admin `forum/admin.py` ~498).
> - **`/market/`'e YENİ ŞERİT EKLENMİYOR** — ilk taslakta önerilen "Hizmet Alanları" 5 kart şeridi iptal edildi:
>   `/market/`'teki kategori çipleri zaten aynı işi (filtreleme) sıfır ekstra tıkla yapıyor, şerit gereksiz dolambaçtı.
> - **Navbara yeni madde EKLENMİYOR.** Hizmet sayfaları yalnız **dış trafik** (Google aramasından iniş) için;
>   platform içi gezinmeye (`/market/`, uzman dizini, blog kartı) hiç dokunmuyor. Hizmet sayfasında yalnız navbar
>   "Pazaryeri" linki aktif/vurgulu + breadcrumb "Pazaryeri › …" (konum göstergesi, yeni link değil).
> - **YALIN ilkesi (kullanıcı):** Google sonucundan hizmet sayfasına iniş → "İlan Aç" (kategori ön-seçili, 1 tık)
>   veya "Tüm Uzmanları Gör" (`/uzmanlar/?cat=`, 1 tık) — ara sayfa yok. Uzman tarafı zaten mevcut `/market/` +
>   çiplerle karşılanıyor, hizmet sayfası onlara dokunmuyor.
> - Eşlenmeyen `JobCategory`'lerdeki ilanlar kaybolmaz — `/market/` ana listede ve çiplerde normal görünmeye devam
>   eder; hizmet sayfası yalnız ekstra bir SEO giriş kapısı, tek görünürlük kanalı değil.
> - Mockup: `claude.ai/artifact/ADTZ9xDK4ieSHt7GxDWGgN` (navbar + /market/ + örnek hizmet sayfası akışı).
> - **İç link kararı (4 Ekim 2026, kullanıcı: "diğer hizmetler gelince footer uzar mı?"):** footer'daki "Araçlar"
>   sütununa her hizmet sayfası için ayrı satır eklemek yerine tek bir **`/hizmetler/` indeks sayfası** +
>   footer'da tek "Hizmetler" linki — kaç hizmet sayfası olursa olsun footer sabit kalır, indeks otomatik listeler
>   (`ServicePage.objects.filter(is_active=True)`).
> - **CANLIDA (4 Ekim 2026, main merge 2617896, Hetzner deploy edildi):** kullanıcı 4 sayfayı da (`is_active=True`)
>   ve `feature_hizmet_sayfalari` flag'ini production'da elle açtı — `/hizmetler/` + 4 alt sayfa şu an gerçek
>   kullanıcılara görünür durumda. **GSC'ye gönderildi (4 Ekim 2026):** sitemap yeniden gönderildi + 5 URL
>   (`/hizmetler/` + 4 alt sayfa) tek tek Request Indexing. Ölçüm: ~2-4 hafta sonra Performance raporunda hizmet
>   niyetli sorgularda gösterim çıkıp çıkmadığına bak (Faz 1 analizinde bu sorgular 0 gösterimdi).

- [x] **YAPILDI (4 Ekim 2026, commit `e5aee67` + sonrası, main'e merge edildi + Hetzner'e deploy edildi): pilot
  `/hizmetler/nicel-analiz/` + `/hizmetler/` indeksi — canlıda.** `ServicePage`/`ServicePageSection`/`ServicePageFAQ` modelleri (`forum/models.py`,
  migration forum/0170 şema + forum/0171 veri — Nicel Analiz 7 bölüm + 2 SSS, `is_active=False` varsayılan),
  admin (`JobCategory.intro` pattern'i, inline bölüm/SSS), `SiteSettings.feature_hizmet_sayfalari` flag
  (varsayılan kapalı). `post_job` artık `?category=<id>` ile ön-seçim destekliyor. Service + BreadcrumbList +
  FAQPage JSON-LD, sitemap (`ServicePageSitemap` + indeks `StaticViewSitemap`'e flag'li eklendi), AI asistan
  `_ALLOWED_PATHS`'e `/hizmetler/` eklendi. **Düzeltilen hata:** ilk uygulamada `JobCategory.localized_title`
  property'si yanlışlıkla `ServicePageFAQ`'ya kaymıştı (model ekleme sırası hatası) — fark edilip düzeltildi,
  forum testleri 82/82'ye geri döndü. Lokalde `JobCategory` verisi olmadığından (yalnız canlıda var) bölümlerdeki
  uzman kartları lokalde boş görünür — normal.
- [x] **YAPILDI (4 Ekim 2026, commit `c7a4f9e` + `3e296e2`, main'e merge edildi, canlıda):** diğer 3 sayfanın
  (`akademik-danismanlik`, `nitel-analiz`, `veri-ve-yapay-zeka`) içeriği migration `forum/0172` ile girildi (her
  sayfa kendi bölümleri + JobCategory eşlemesiyle); migration `forum/0173` ile 23 bölümün hepsi (4 sayfa) "ne zaman
  ihtiyaç duyulur" + "teslimat" cümleleriyle genişletildi. Nicel Analiz bölümleri zaten SmartPLS/AMOS (SEM) ve
  EViews'i kapsıyordu (bu maddenin "ileri modellerle zenginleştirme" kısmı da fiilen karşılanmış). Hero'ya
  "Uzmanları Gör" butonu eklendi. **7 Ekim 2026'da doğrulandı:** canlıda 4 sayfa da `is_active=True` +
  `feature_hizmet_sayfalari` AÇIK, 200 dönüyor, doğru title'lar görünüyor; bu oturumda ayrıca Playwright ile
  masaüstü+mobil (4 sayfa × 2 görünüm) taşma/hiza kontrolü yapıldı — hepsi OK, ekran görüntüsüyle de teyit edildi.
- [x] **YAPILDI (7 Ekim 2026, commit yok):** 15 blog kategorisinin 4 hizmet sayfasına eşlenmesi — `forum/models.py`
  `BlogPost.SERVICE_PAGE_BY_BLOG_CATEGORY` sözlüğü (15/15 kategori → `nicel-analiz`/`akademik-danismanlik`/
  `veri-ve-yapay-zeka`; `nitel-analiz`'e hiç blog kategorisi düşmedi — gerçek durum, yapay eşleme yapılmadı,
  kullanıcı onayı). `blog_detail` view artık eşleşen aktif `ServicePage`'i context'e ekliyor; `blog_detail.html`
  kartı (kullanıcı kararı: "genişlet") artık yalnız `expert_category` (≥2 uzman şartlı JobCategory) değil, hizmet
  sayfası eşleşmesi tek başına da kartı gösteriyor — önceden hiç kart görmeyen 5 kategoride (etik kurul/akademik
  kariyer/bibliometri/bilim felsefesi/veri güvenliği-etik) artık kart çıkıyor, hedefi `/hizmetler/<slug>/`. İkisi
  de eşleşirse hizmet sayfası önceliklidir. Yeni msgid'ler (`Hizmet Sayfasına Git` + blocktrans) EN/DE'ye elle
  eklendi (host'ta `msgfmt`, container'da gettext yok), `makemessages --no-location` denendi ama 10 günlük kod
  kayması yüzünden ilgisiz ~8800 satırlık diff çıkardı → geri alındı, elle ekleme yapıldı. Doğrulama: 3 gerçek blog
  yazısıyla (bibliometri/tez-süreci/spss) canlı hedef linkleri curl ile kontrol edildi, Playwright taşma=0, forum
  82/82.

**Faz 4 — SEO metin taslağı (4 Ekim 2026, WebSearch ile Armut.com'un hedeflediği terimler referans alındı —
Armut rakip örneği, amaç ona rakip olmak; kesin arama hacmi yok, rakibin onlarca şehir sayfası açmış olması talep
sinyali). Henüz hiçbir yere yazılmadı — `ServicePage` modeli kurulunca admin'e girilecek:**
- **`/hizmetler/nicel-analiz/`** — meta_title: "Nicel Analiz Desteği: SPSS, R, EViews ile İstatistik Analizi |
  Analizus"; meta_description: "Tezinizin veya araştırmanızın istatistiksel analizini SPSS, R, EViews, SmartPLS'e
  hakim uzman analistlere bırakın. Teklif alın, karşılaştırın, siz seçin."; H1: "İstatistiksel Analiz ve Nicel Veri
  Analizi Desteği"; giriş: "SPSS, R, EViews, SmartPLS ve ileri istatistiksel yöntemlerle — verinizi gönderin,
  alanında uzman analistler sizin adınıza analiz edip raporlasın. Analizus'ta uzmanlar teklif verir, siz
  karşılaştırıp seçersiniz."
- **`/hizmetler/veri-ve-yapay-zeka/`** — meta_title: "Veri Bilimi ve Yapay Zeka Desteği: Python, Makine Öğrenmesi |
  Analizus"; meta_description: "Python, makine öğrenmesi, NLP ve büyük veri projelerinizde uzman veri
  bilimcilerle çalışın. Akademik ve kurumsal projeler için teklif alın."; H1: "Python, Makine Öğrenmesi ve Veri
  Bilimi Desteği"; giriş: "Veri setinizi modellemek, tahmin kurmak ya da NLP/metin analizi yapmak için Python ve
  makine öğrenmesi konusunda deneyimli uzmanlarla eşleşin."
- **`/hizmetler/akademik-danismanlik/`** — meta_title: "Tez ve Akademik Danışmanlık Desteği: Yöntem, Etik Kurul,
  Makale | Analizus"; meta_description: "Tez sürecinizde yöntem seçimi, etik kurul başvurusu ve makale
  hazırlığında deneyimli akademisyenlerden danışmanlık desteği alın. Teklif alın, karşılaştırın."; H1: "Tez ve
  Akademik Süreçlerinizde Danışmanlık Desteği"; giriş: "Tez önerisinden etik kurul başvurusuna, yöntem seçiminden
  makale hazırlığına kadar sürecinizin her adımında deneyimli akademisyenlerden danışmanlık alın. Analizus bir
  yazım hizmeti değildir — sürecinize rehberlik eden uzmanlarla sizi buluşturur." ⚠️ Armut'ta komşu kategori
  "proje yazma" — bizim kaçındığımız "tez yazdırma" sınırına yakın; bilerek "yazım hizmeti değiliz" cümlesi
  girişe eklendi, kural + rakipten ayrışma.
- **`/hizmetler/nitel-analiz/`** — meta_title: "Nitel Analiz Desteği: MAXQDA, NVivo, İçerik Analizi | Analizus";
  meta_description: "Görüşme, odak grup ve doküman verilerinizin nitel analizini MAXQDA ve NVivo'ya hakim
  uzmanlarla yapın. İçerik ve konu analizinde teklif alın."; H1: "Nitel Araştırma ve İçerik Analizi Desteği";
  giriş: "Görüşme kayıtları, odak grup verileri ya da doküman setlerinizin kodlanması ve analizinde MAXQDA, NVivo
  deneyimine sahip uzmanlardan destek alın."

**Faz 5 — İç linkleme**
- [x] **YAPILDI (1 Ekim 2026):** analiz konsolu (giriş yapmış görünüm, 18 araç) — SEO rehberi + "uzmana bırak" bandı
  `.ax-console-layout` dışında basılıyordu (sidebar boyu kadar boşluk, hizasız blok) → içerik sütununa taşındı; rehber giriş
  paragrafı kendi "… Nedir?" kartı olan 15 araçta gizlendi (tekrar), kartı olmayan orneklem/friedman/tekrarli_anova'da kalır
  (`TOOLS_WITHOUT_INTRO_CARD`). Anonim tanıtım sayfası (Google) değişmedi. Playwright 18/18 kontrol.
- [x] **DÜZELTME (1 Ekim 2026, kullanıcı: "hepsinde bozukluk"):** önceki adım rehberi 12 px içeriden başlatıyordu (konteyner
  iç boşluğu) → rehber + CTA `row/col-12` içinde, kartlarla aynı hiza (Playwright 18/18 masaüstü + mobil, yatay taşma yok).
  Kartlarla örtüşen 4 bölüm (ne zaman/varsayımlar/yorum/APA) konsolda yalnız kartı olmayan 3 araçta; ilk gruba "Kullanım
  Rehberi" başlığı (konsol, tanıtım sayfası, tarama konsolu; EN/DE çevirili) → SSS başlığı ortada sahipsiz kalmıyor; SSS
  başlığı 0.88→1rem. Tarama rehberinde 4 px iç kayma ÖNCEDEN VAR (dokunulmadı).
- [x] **TEK DÜZEN (1 Ekim 2026, kullanıcı: Friedman ile Wilcoxon farklı görünüyor):** 18 aracın hepsi Metodoloji → "Nedir?"
  kartı → SSS → İlgili Araçlar → uzmana bırak. Kartı olmayan Friedman / Tekrarlayan Ölçümler ANOVA / Örneklem'e Wilcoxon tarzı
  kart (metin seo_content: giriş + ne zaman + yorum; EN/DE başlık çevirili); konsolda "Kullanım Rehberi" + 4 akordeon hiç yok
  (istisna listesi kaldırıldı). Kart→SSS boşluğu kartlar arasıyla eşit (24 px). Hata: iki satırlı `{# #}` yorum sayfaya metin
  olarak basılıyordu → tek satır. ÖNCEDEN VAR düzeltildi: Wilcoxon/Friedman/Tekrarlı ANOVA view'ı `tool_title` göndermiyordu →
  CTA'da araç adı ve gizli H1 boştu. Playwright TR+EN 18/18, forum 61/61.
- NOT: "araç sayfasına uzmana yaptırın bandı" ZATEN VAR (konsol + tanıtım sayfası, hedef `/proje-talebi/?source=tool`).
- [x] **YAPILDI (9 Ekim 2026, commit `a8acf35`):** araç sayfaları → ilgili hizmet sayfasına link. Kontrol edilince
  footer "Hizmetler" linkinin ve "uzmana yaptırın" bandının zaten var olduğu, gerçek boşluğun bu bandın hizmet
  sayfasına hiç link vermemesi olduğu görüldü. `TOOL_CATEGORIES`'teki 6 grup `/hizmetler/<slug>/`'a eşlendi (5 grup
  → `nicel-analiz`, "Makine Öğrenmesi" → `veri-ve-yapay-zeka`), `SEO_CONTENT` üzerinden hem konsol hem anonim
  tanıtım bandına ikinci satır link eklendi (18 araç fonksiyonunun hiçbirine dokunmadan — mevcut `seo_guide`
  mekanizması üzerinden). Migration yok, 90/90 forum testi yeşil, anonim+girişli curl ile doğrulandı.
- [x] **YAPILDI (9 Ekim 2026, commit `c022225`):** `/analiz/` hub — 6 kategori başlığının yanına "Uzmana yaptır →"
  linki (aynı grup→slug eşlemesi); sayfa sonu proje talebi bandı artık yalnız anonime değil girişli kullanıcıya da
  görünüyor (`/proje-talebi/?source=analiz_hub`). Migration yok, 90/90 forum testi yeşil, Playwright masaüstü+mobil
  taşma kontrolü (0px).
- [x] **YAPILDI (9 Ekim 2026, commit yok, `tasks/todo.md` ile birlikte commit'lenecek):** `/uzmanlar/?cat=<id>` →
  ilgili hizmet sayfası linki. Footer "Hizmetler" linki zaten vardı (değişiklik gerekmedi); gerçek boşluk
  `JobCategory`→`ServicePage` bağlantısıydı — yeni alan/migration yerine var olan
  `ServicePageSection.related_job_categories` M2M'i üzerinden ters sorgu kuruldu (`forum/views.py` `uzman_dizini`).
  Eşleşme varsa kategori başlığının altına link. Geçici (rollback'li) veriyle hem eşleşen hem eşleşmeyen senaryo
  test edildi, 90/90 forum testi yeşil.

**Faz 6 — İçerik takvimi (öneri ayda 6–8 yazı, `blog_yazisi_create.md` tonu)**
> **ÖNCELİK SIRASI (9 Ekim 2026, GSC + dış araştırma ile netleşti — `tasks/todo.md` dışına yazılmayan WebSearch
> bulguları):** Gerçek Google arama hacmine (Keyword Planner/Ahrefs) doğrudan erişim yok (login/abonelik gerektiriyor);
> sıralama GSC'nin kendi gösterim verisi + rakip (Armut.com) kategori/talep sinyali + akademik kurum içerik
> yoğunluğu birleştirilerek yapıldı. Yarın buradan devam.
1. **[x] YAPILDI (10 Ekim 2026, migration `forum/0176`, commit edilecek) — "SPSS'e benzer/alternatif ücretsiz
   programlar" (40 gösterim, sıra 27).** Dünkü "içerik yok" varsayımı **yanlıştı** — kontrol edilince konuyla ilgili
   **3 yayınlanmış yazı** bulundu: `ucretsiz-spss-alternatifi-var-mi-...` zaten tam SEO alanlarına sahipti (852
   kelime) → yeni yazı cannibalization yaratırdı, yazılmadı. Bunun yerine gerçek boşluk bulundu: `spss-mi-r-mi-
   tez-icin-hangisi-daha-kolay` ve `spsste-t-testi-adim-adim-...` yayında ama `meta_title`/`meta_description`
   **tamamen boştu** (0/0 karakter) — ikisine de dolduruldu (korumalı migration, Faz 1 0162 deseni). İleri-geri-ileri
   + 90/90 test yeşil.
2. **KARAR (10 Ekim 2026): "Kaplan-Meier analizi nedir" (35 gösterim) için yeni içerik GEREKMİYOR.** Kontrol edilince
   `survival-analizi-101-kaplan-meier-cox-regresyon-...` adında zaten iyi optimize edilmiş bir yazı bulundu (857
   kelime, meta_title 55kr, meta_description 157kr, `saglik-istatistigi` kategorisi). Düşük gösterim içerik/meta
   eksikliğinden değil — muhtemelen iç link zayıflığı, niş konu veya zaman meselesi; "içerik yaz" burada yanlış
   çözüm olurdu. Ayrı bir teşhis gerekirse ileride ele alınabilir, şimdilik kapatıldı.
3. **NVivo/MAXQDA ile nitel veri analizi serisi (4–6 yazı)** — `/hizmetler/nitel-analiz/`'e hiç blog kategorisi
   bağlı değil (Faz 3 notu), en büyük yapısal boşluk; MAXQDA'nın tam Türkçe desteği var, gerçek "nasıl yapılır" talebi
   doğrulandı (üniversite ders içerikleri/eğitim videoları).
4. **SmartPLS / Yapısal Eşitlik Modellemesi (SEM) serisi** — Başkent Üniv. (BEDAM, 90 saat ücretli eğitim) ve Erzurum
   Teknik Üniv. ayrı eğitim düzenlemiş; akademik çevrede ücret ödenen somut talep var. `/hizmetler/nicel-analiz/`'e
   bağlanır.
5. **"Tez etik kurul onayı ne zaman gerekir"** — net/somut soru; bulgu: onay yalnız anket/gözlem/mülakat/deney içeren
   tezlerde zorunlu, literatür taraması/ikincil veride gerekmiyor — bu ayrım yazının ekseni olabilir.
   `/hizmetler/akademik-danismanlik/`'a link.
- [ ] Önce talebi görünen (mevcut GSC, sıra 1-2 ile aynı): "spss öğrenci ücretsiz" (47), "spss benzeri programlar"
  (40, sıra 27), "kaplan meier analizi" (35), "spss güvenirlik analizi" (33), "iç tutarlılık katsayısı nasıl
  hesaplanır" (46)
- [ ] Boş kümeler (her biri 4–6 yazı → hizmet sayfasına link, sıra 3-5 ile aynı): nitel (NVivo/MAXQDA, içerik analizi,
  konu analizi), SEM/SmartPLS, EViews/zaman serisi, Power BI/Tableau, Python/ML/NLP, etik kurul, tez önerisi,
  akademik editörlük
- Rakip sinyali (Armut.com, 9 Ekim araştırması): "istatistik-veri-analizi" kategorisinde 1.169 analist, 2.889
  onaylı değerlendirme, fiyat aralığı 1.000-8.000 TL — pazarın gerçek boyutuna işaret ediyor. Şehir×hizmet sayfa
  modelini (Armut'un yaptığı) daha önce bilinçli reddettik (4 Ekim kararı, Faz 4 notu) — duruyor, değişmedi.

**Faz 7 — Araç sayfalarını 1. sayfaya (uzun vade)**
- [ ] 2. sayfadakiler: anova 13,8, mann-whitney 14,7, tekrarlı anova 14,4, orneklem 23,2, hangi-test 16,0, cronbach 11,2 —
  içerik derinliği + blog/hizmet sayfalarından iç link

**Faz 8 — Dış otorite (kullanıcı, kod yok)**
- [ ] Google Business Profile, akademik topluluklar / üniversite kulüpleri, LinkedIn, eğitmenlerle misafir yazar imzası (E-E-A-T)

**Ölçüm:** aylık GSC dışa aktarımı. KPI: tık, CTR, hizmet niyetli sorgu gösterimi, `/hizmetler/` → proje talebi / ilan dönüşümü.

- [x] **CANLIDA (ba9560b, main 8393eec; 29 Eylül 2026): regex `[\w.@+-]+` + `encodeURIComponent`; test: @/.+- adlar eski ROUTE YOK → yeni bağlandı, düz ad ve yok kullanıcı aynı; forum 61/61.** Canlı log: DM WebSocket "No route found for path 'ws/chat/240401005@/'" (29 Eylül 2026, d39af06 deploy sonrası
  görüldü; ÖNCEDEN VAR, Ocak 2026)** — `forum/routing.py:12` `(?P<username>\w+)` Django kullanıcı adlarındaki `@ . + -`
  karakterlerini kabul etmiyor → bu kullanıcılarla DM'de canlı mesaj (WebSocket) bağlanmıyor. Öneri: regex `[\w.@+-]+` +
  `send_message.html:369` `encodeURIComponent`; consumer'da kullanıcı adı çözümü kontrol. Karar/onay bekliyor.

- [x] **YAPILDI (29 Eylül 2026): daemon.json + `up -d --force-recreate` ile tüm container'lara uygulandı (analizus.md §3). Eski not: daemon.json yazıldı, docker restart, db log boşaltıldı (248 MB → 4 KB), siteler 200. KALAN: mevcut container'lar eski ayarla (LogConfig boş) — sınır ancak yeniden oluşturulunca geçer → bir sonraki deploy'da `docker compose up -d --force-recreate` (db dahil; veri external volume'da). nginx log'u 48 MB.** Hetzner Docker log rotasyonu YOK (29 Eylül 2026, salt okuma)** — `/etc/docker/daemon.json` yok, `docker-compose.yml`'de
  `logging:` yok → container logları sınırsız büyüyor (`/var/lib/docker/containers` 295 MB; disk ~%76). Öneri: compose'a
  `logging: {driver: json-file, options: {max-size: "20m", max-file: "5"}}` (container yeniden oluşturulunca geçerli). Onay bekliyor.
  **Güncelleme (29 Eylül 2026):** compose'a EKLENMEZ — Hetzner `docker-compose.yml`'de commit'lenmemiş `rlprehber` servisi var →
  git'te dosya değişirse `git pull` durur. Doğru yer `/etc/docker/daemon.json` (tüm container'lar, rlprehber dahil).
  Boyutlar: db 248 MB (Haziran'dan beri), nginx 48 MB, web 8 KB; disk %66. Plan: daemon.json → `systemctl restart docker`
  (iki site ~30 sn kesinti) → db log'u bir kez `truncate -s 0` → yeni ayar container yeniden oluşturulunca geçerli.
- [x] **YAPILDI (29 Eylül 2026): `mail_admins` → ADMIN_NOTIFICATION_EMAIL, yalnız DEBUG=False + 500 (404 yok); `analizdestek/log_filters.py` aynı hata 15 dk'da 1, saatte ≤20 (worker başına); test: locmem e-posta, gövdede gizli env değeri yok, oturum çerezi gizli. Arka plan işi hataları kapsam dışı.** Hata bildirimi yok (29 Eylül 2026, karar bekliyor) — 500/istisnalar yalnız Docker log'unda; kimse haberdar olmuyor
  (WebSocket hatası tesadüfen görüldü). Seçenekler: (a) Django `ADMINS` + `mail_admins` (mevcut SMTP, 3. taraf yok) —
  önerilen; (b) Sentry ücretsiz katman (veri 3. tarafa gider → `send_default_pii=False`, gizlilik metni).

- [x] **TEMİZLİK YAPILDI (29 Eylül 2026, kullanıcı): image/builder prune + journald 500M → disk %65 → %45 (20 GB boş); iki site 200. Sunucu dışı yedek de YAPILDI (95c35d0, yerel saatlik indirme).** Hetzner kapasite (29 Eylül 2026, salt okuma) — CPU 2 çekirdek yük 0,16; RAM 3,7 GB (kullanılabilir 2,9 GB, OOM yok);
  disk 38 GB'ın 24 GB'ı dolu (13 GB boş). Acil sorun YOK. Geri kazanılabilir: eski Docker imajları ~10 GB
  (`docker image prune -a`), build cache ~3 GB (`docker builder prune`), journald 3,7 GB (`journalctl --vacuum-size=500M`),
  elle alınmış `yedek_*.sql` 4 dosya ~0,7 GB. Günlük `backup_analizus_*` 7 gün rotasyonlu (OK). RİSK: tüm DB yedekleri aynı
  diskte — sunucu kaybında yedek de gider → sunucu dışı yedek (Hetzner Backup / S3) kararı. Her `--build` ~1–2 GB imaj bırakır.

**PUBMED NCBI ANAHTARI — TAMAMLANDI (29 Eylül 2026)** — kullanıcı yerel `.env`'ye anahtarı `PUBMED_API_KEY` adıyla
girdi; kod `NCBI_API_KEY` okuyor → şu an anahtar KULLANILMIYOR (3 istek/sn).
- [x] 1. (kullanıcı yaptı, 29 Eylül; doğrulandı) Ad uyumu: yerel `.env`'de `PUBMED_API_KEY` → `NCBI_API_KEY` (önerilen; kod/doküman/help_text zaten bu ad)
- [x] 2. YAPILDI (29 Eylül 2026): `_get` son denemede istisnayı `api_key=***` mesajıyla aynı türde yeniden fırlatır → job_runner/bibliometri traceback'leri de temiz; test eski kodda sızıntıyı yakaladı, yenide yok; gerçek arama 3.839 sonuç/3,5 sn. KALAN (YAPILDI 29 Eylül 2026 — OpenAlex `_fetch_page` aynı kalıp; test eski kodda sızıntı yakaladı, yenide yok): OpenAlex scraper istisnayı ham fırlatıyor → `bibliometrics/services/job_runner.py` `exc_info` traceback'inde ve `openalex` `ensure_full_results`/sipariş log'unda OpenAlex anahtarı log'a düşebilir (kullanıcıya değil) — aynı kalıp önerilir, onay bekliyor. Eski: Log'da anahtar gizleme: `pubmed/services/scraper.py` hata log'ları (`_get`, sayfalama) + `job_runner.py` log'u
  URL'yi `api_key=` ile yazıyor (kullanıcı mesajı zaten sabit — kullanıcıya sızma yok). OpenAlex'teki `redact_api_key` kalıbı.
- [x] 3. (yerel + Hetzner doğrulandı: anahtar görünüyor, min_interval 0.11, esearch 200) Yerel doğrulama: `docker compose up -d web` (restart env okumaz) → container'da anahtar var mı, `min_interval=0.11`,
  gerçek esearch 200 (geçersiz anahtarda NCBI 400 "API key invalid" döner)
- [x] 4. (kullanıcı: tanımlı) Render env: `NCBI_API_KEY` (kullanıcı, panelden)
- [x] 5. (kullanıcı yaptı, doğrulandı) Hetzner (29 Eylül: `/app/.env`'de NCBI/PUBMED değişkeni YOK — salt okuma kontrol): `/app/.env`'ye `NCBI_API_KEY` → `docker compose up -d web` + `restart nginx` → container'da doğrula + tek gerçek sorgu
- [x] 6. (canlıda AÇIK, DB'den doğrulandı) `feature_pubmed` admin'den aç (kullanıcı kararı; önce Render'da uçtan uca dene)
- [x] 7. (5594229) Doküman: `analizus.md` §5/§9 + bu liste

**PUBMED MODÜLÜ — PLAN (29 Eylül 2026, ONAY BEKLİYOR)** — OpenAlex kalıbı, TR/EN/DE; ilk sayfa + ihtiyaçta tam veri.
- [x] Faz 1 — YAPILDI YERELDE (29 Eylül 2026; gerçek API: 250 sonuçlu sorgu arama 2 istek/3,6 sn, tam veri 3 istek; sıfır sonuç + hata yolu OK; forum 61/61; affiliation'dan yazar e-postası temizleniyor). Faz 2'ye kalan: S3 temizlik cron'u + hesap silme listesi (`forum/api_views.py`). `pubmed` app çekirdeği: `PubMedSearchJob` (+ migration pubmed/0001), `services/scraper.py` (esearch
  `usehistory=y` → WebEnv; efetch XML 200'lük sayfa; `tool`/`email` + ops. `NCBI_API_KEY`; 3 req/s, anahtarla 10),
  `services/job_runner.py` (arama 1–2 istek, demo TXT, `ensure_full_results`), `job_queue.py` (tür + kurtarma + sıra),
  `INSTALLED_APPS`, admin. Doğrulama: gerçek API ile uçtan uca betik.
- [x] Faz 2 — YAPILDI YERELDE (29 Eylül 2026): `/pubmed/` (ax- sınıfları, mobil önce, API verisi escape), TR/EN/DE 200,
  flag kapalıyken 404 + hub/sitemap'te yok; tam akış (POST → polling → TXT/Excel) OK; 32 msgid EN/DE; migration forum/0160
  (`feature_pubmed`, **varsayılan KAPALI** → canlıda admin'den açılacak); S3 temizlik cron'u + hesap silme + çalışan işler
  paneli bağlandı. Arayüz: `forms.py`, `views.py`, `urls.py` (i18n_patterns, `/pubmed/`), `templates/pubmed/landing.html`
  (OpenAlex landing kalıbı, ax- sınıfları), Excel (demo), günlük limit; `feature_pubmed` flag (forum migration),
  context_processors, tarama hub kartı (`forum/views.py`), konsol + navbar aktif link, sitemap. EN/DE çeviri.
- [x] Faz 3 — YAPILDI YERELDE (29 Eylül 2026): gerçek veriyle 265 kayıt → 13 analiz; atıfa dayanan 4 analiz (en çok atıf,
  H-index, yıllık atıf trendi, Research Gap — dikey ekseni atıf) "kaynak atıf vermiyor" nedeniyle atlanır; ülke %91, kurum
  %98 (adres metninden tahmin, Kısıtlar'da yazıyor); anahtar kelime yoksa MeSH. OpenAlex regresyonu değişmedi (17 analiz).
  Migration bibliometrics/0005 (pubmed_job FK, nullable). 13 msgid EN/DE. Bibliometri köprüsü: `BibliometricJob.pubmed_job` FK (bibliometrics migration), `parse_pubmed_json`,
  `/bibliometrics/from-pubmed/<id>/`, runner (`source='pubmed'`), rapor notları kaynak metni. PubMed'de atıf sayısı yok →
  atıf analizleri "üretilemedi" nedenine düşer; ülke yalnız affiliation metninden (sezgisel) — karar.
  **Kararlar (29 Eylül 2026):** sipariş ŞİMDİLİK YOK (tam veri → proje talebi, EN/DE gibi; Faz 4 ileride); atıf analizleri
  yok, ülke affiliation metninden tahmin + Kısıtlar bölümünde "tahmini" notu; NCBI anahtarını kullanıcı alacak
  (`NCBI_API_KEY`, yoksa 3 req/s); günlük limit OpenAlex ile aynı.
- [x] **ZORUNLU — Tarama sipariş fiyatları adminden düzenlenebilir olmalı** — YAPILDI YERELDE (29 Eylül 2026): Site Ayarları → Fiyatlandırma'ya 4 alan (migration forum/0161, varsayılanlar eski fiyatlar; 0–6000 kayıtta eski formülle birebir aynı tutar doğrulandı); 4 model `calculate_price` + 4 sipariş şablonu (tablo + JS) + vitrin paketleri ayardan okur; fiyat değiştirilince sipariş tutarı/sayfa/vitrin güncellendi (test). Kararlar: 4 araç ortak tek fiyat (ilk 100 + sonraki her 100); ilan vitrini paketleri (3/7 gün) de dahil. SiteSettings alanları + migration; model/view/sipariş şablonu (tablo + JS) SiteSettings'ten okur. (kullanıcı: "hard coded olmaz", 29 Eylül 2026;
  PubMed Faz 1'den sonra ayrı iş, plan+onay): OpenAlex,
  TR Dizin, OAI-PMH, Semantic Scholar `calculate_price` = 250 TL/ilk 100 + 100 TL/her 100 — SiteSettings'te alan yok.
  Adminden düzenlenebilen yalnız bibliometri rapor fiyatları (`biblio_price_*`). SiteSettings alanı (migration) + şablonlardaki sabit fiyat metinleri.
- [x] **KARAR (12 Ekim 2026) — Faz 4 ŞİMDİLİK YAPILMAYACAK.** TR sipariş akışı
  (`PubMedOrder`, OpenAlex sipariş kopyası — model/form/view/admin/template/
  job_runner/job_queue/hesap silme, toplam ~10 dosya) için tam plan çıkarıldı
  (OpenAlex'in `AlexOrder` akışı birebir incelendi) ama **kullanıcı kararıyla
  uygulanmadı** — gerekçe: PubMed yeni bir araç, gerçek talep (kaç kullanıcı
  tam veri istiyor) henüz ölçülmedi; manuel IBAN+admin-onay akışı admin'e
  sürekli iş yükü bindiriyor, kanıtlanmamış talep için bu maliyete değmiyor
  (OpenAlex'te de sipariş özelliği eklenmeden önce aynı temkinli yol
  izlenmişti). **Mevcut davranış korunuyor, değişiklik yapılmadı:**
  `pubmed/services/job_runner.py` `send_demo_email()` zaten TR dahil tüm
  dillerde kullanıcıyı `proje_talebi` sayfasına yönlendiriyor (kod zaten bu
  haldeydi, hiçbir dosya değişmedi). **Yeniden değerlendirme sinyali:**
  `proje_talebi?source=tool` üzerinden gelen taleplerde PubMed payı somut
  şekilde artarsa (admin/analytics'ten izlenebilir), bu plan (yukarıdaki
  10 dosyalık liste) hazır — tekrar çıkarmaya gerek yok.

- [ ] **OpenAlex sayfası bulguları (PubMed yazılırken görüldü, 29 Eylül 2026)** — (1) ~~XSS~~ DÜZELTİLDİ YERELDE (29 Eylül
  2026; CANLIDA main 08472b2, Hetzner restart, /openalex/ 200): 6 tarama sayfası (OpenAlex, S2, TR Dizin, OAI-PMH, YÖK Tez, Tez Analizi) dış veriyi `_esc()` ile basıyor, S2 PDF
  linki yalnız http(s), DOI `encodeURI`; Playwright: eski sürümde yük 7 kez çalıştı, yenide 6 sayfada 0. Kalan düşük risk:
  istatistik araçlarında yüklenen dosyanın sütun adları kaçışsız (karar_agaci, korelasyon, lineer/lojistik regresyon, svm —
  yalnız kullanıcının kendi dosyası, self-XSS). (2) ~~`extra_js` block.super~~ DÜZELTİLDİ YERELDE (29 Eylül 2026: bildirim/
  widget script'leri artık yükleniyor, JS hatası yok). (3) ~~Premium 7~~ DÜZELTİLDİ YERELDE (kullanıcı: "7 arama"): OpenAlex,
  TR Dizin, YÖK Tez, PubMed'de Premium 7 / normal 3 (S2 3'te; vaat etmiyor); PubMed limit mesajı premium önerisi. Eski not: (2) `extra_js`
  bloğu `block.super` çağırmıyor → bildirim/widget script'leri bu sayfada yüklenmiyor; (3) "Premium üyelikle 7 aramaya"
  metni var ama `get_daily_limit` premium'a da 3 veriyor.

**A. Kod işleri (öncelik sırasıyla)**
- [x] **Hetzner deploy — main ab57dcd YAPILDI (28 Eylül 2026 gece; doğrulandı: bibtexparser 1.4.4, import ok, web log hata 0, /, /bibliometrics/ TR/EN/DE 200)**: bibliometri "Veri, Yöntem ve
  Kısıtlar" (A–G) + BibTeX (bibtexparser==1.4.4) + virgüllü anahtar kelime. requirements.txt değişti → `--build` ŞART; migration yok.
  Canlıda kontrol: `pip show bibtexparser` → 1.4.4; OpenAlex bibliometri işi → tam PDF sonunda bölüm.
- [x] **Hetzner deploy — main a5c5984 YAPILDI (28 Eylül 2026, kullanıcı: "sorun çıkmadı"; dışarıdan /, /bibliometrics/, /en|de/bibliometrics/ 200, başlıklar çevrili)**: bibliometri EN/DE + Research Gap + K1–K7 + A/B. requirements.txt
  değişti (Babel) → `docker compose up -d --build web` ŞART; migration yok. Sonra canlıda: OpenAlex araması + bibliometri işi.
- [x] **BibTeX virgüllü anahtar kelimeler — DÜZELTİLDİ (28 Eylül 2026, `_parse_bibtex`: `;`/`|` yoksa `,` ile böl; 5 durum test edildi)** Eski not: — `parser._split_keywords` yalnız `;`/`|` ile ayırıyor;
  Zotero/Mendeley/Google Scholar .bib `keywords = {a, b}` → tek kelime "a, b" → kelime analizleri bozuk. Scopus .bib `;` (sorun yok).
  Öneri: yalnız BibTeX'te `;` yoksa `,` ile böl (fonksiyon WoS/Scopus'ta da kullanılıyor — onlara dokunma).
- [x] **BibTeX düzeltildi YERELDE (28 Eylül 2026): `bibtexparser==1.4.4` sabitlendi, build + uçtan uca iş testi OK
  (LaTeX→Türkçe, yazar sırası, note'tan atıf). CANLIDA HÂLÂ BOZUK (2.0.1 doğrulandı; şimdiye dek .bib işi yok) → deploy'da
  `docker compose up -d --build web` ŞART.** Eski not: — `requirements.txt` `bibtexparser` sürümsüz →
  2.0.1 kurulu; `parser._parse_bibtex` v1 API (`bibtexparser.bparser`) kullanıyor → "No module named 'bibtexparser.bparser'",
  iş "Dosyadan kayıt okunamadı" ile başarısız. Canlıda da muhtemelen aynı (kontrol edilmedi). Seçenek: `bibtexparser<2` sabitle
  (build gerekir) veya v2 API'ye geçir.
- [x] **DÜZELTİLDİ (12 Ekim 2026, kullanıcı kararı: EN/DE'de gizle)** Bibliometri SSS/SEO bölümü EN/DE'de Türkçe (ÖNCEDEN VAR, 28 Eylül 2026) — anonim `/en|de/bibliometrics/` sayfası
  `tarama_seo_content.py` (TR-only düz metin) SSS'ini gösteriyordu. `templates/service_promo.html` `{% if seo_guide %}` → `{% if seo_guide and LANGUAGE_CODE == 'tr' %}` yapıldı (6 aracın hepsini tek yerden kapsıyor: yoktez, openalex, trdizin, oaipmh, bibliometrics, semanticscholar). Tam EN/DE çevirisi ayrı, daha büyük bir iş olarak ertelendi (kullanıcı kararı).
- [x] **DÜZELTİLDİ (12 Ekim 2026)** Bibliometri metin tutarsızlıkları (28 Eylül 2026) — (1) `tarama_seo_content.py` ~366 "Bradford kanunu dağılımı" cümlesi kaldırıldı, yerine gerçek raporda olan Lotka kanunu açıklaması kondu (raporda Bradford analizi hiç yok); (2) `bibliometrics/templates/bibliometrics/landing.html:159` demo kartı "Yayın Trendi + Yazarlar + Kelime Bulutu" → "Yayın Trendi + Büyüme Oranı + Yazarlar" (gerçek demo = `analyzer.py` ilk 3 analiz: Trend, Büyüme Oranı, Yazarlar — `job_runner.py` `figures[:3]`); EN/DE `.po` çevirisi + host'ta `msgfmt` ile `.mo` derleme yapıldı, `manage.py check` ve template yükleme testiyle doğrulandı.
- [x] **KONTROL EDİLDİ — sızıntı YOK (12 Ekim 2026)** GÜVENLİK — canlı DB'de eski OpenAlex `error_message` kayıtlarında API anahtarı (29 Eylül 2026 bulgusu, takipsiz kalmıştı) —
  d39af06 öncesi ham hata mesajı URL'deki `api_key=` değerini kullanıcıya gösterip DB'ye yazıyordu. Hetzner'de salt okuma ile
  `AlexSearchJob.error_message` ve `BibliometricJob.error_message` (`icontains='api_key='`) kontrol edildi (`AlexOrder`'da bu alan hiç yok) —
  0/0 sonuç, temizlenecek kayıt yok, anahtar yenileme gerekmedi.
- [ ] **Veri temizliği: kontrol karakterleri** — OpenAlex bazı dergi adlarında C1 kontrol karakteri gönderiyor
  ("\x98The \x9cJournal of practical nursing") → grafikte boş kutu (glif uyarısı). `_clean` kontrol karakterlerini atmalı. (28 Eylül 2026)
- [x] **OpenAlex hata mesajı — CANLIDA (d39af06 + 9f50d0b, main 8393eec; 29 Eylül 2026): 429/502/503/504 bekle+yeniden dene (Retry-After, üst sınır 60 sn); kullanıcıya çevrili sabit mesaj (TR/EN/DE); log/hata metninde `api_key=***`. BULGU: ham mesaj URL'deki API ANAHTARINI kullanıcıya gösteriyordu → canlı DB'de eski `error_message` kayıtları kontrol edilmeli, varsa anahtar yenilenmeli.** Eski not: — kullanıcıya ham "503 Server Error… for url: https://api.openalex.org/…" gösteriliyor → çevrili,
  anlaşılır mesaj; scraper 503'te de beklemeli (şu an yalnız 429). (28 Eylül 2026)
- [x] **OpenAlex bütçe verimliliği — YAPILDI (e8e39bb, canlıda: arama yalnız ilk sayfa, tam veri bibliometri/sipariş istenince).** Eski not: — arama tüm sonuçları (5000'e kadar, 25 istek) baştan çekiyor;
  yalnız ilk sayfa + tam veri bibliometri/indirme istenince çekilirse arama başı 1 istek (≈1.000 arama/gün). Önce canlıda
  günlük arama sayısı ölçülebilir (salt okuma, kullanıcı izniyle).
- [x] **OpenAlex API anahtarı EKLENDİ (28 Eylül 2026, kullanıcı: "canlı ve lokalde ok")** — yerelde doğrulandı: anahtarlı
  arama 200 (30.159 sonuç), anahtarsız 503. Render env kullanıcıda. KALAN (ayrı madde aşağıda): ham hata mesajı + 503 bekleme.
  Eski not: **ACİL — OpenAlex aramaları 503 (28 Eylül 2026)**: OpenAlex anonim aramayı yoğunluk nedeniyle durdurdu ("Anonymous
  search is paused… use a free API key"). Kod `OPENALEX_API_KEY` destekliyor ama yerelde (.env) ve Docker'da TANIMSIZ;
  Hetzner/Render kontrol edilmedi. Yapılacak: openalex.org'dan ücretsiz anahtar → yerel .env, Render env, Hetzner
  `/app/.env` + `docker compose up -d web` (restart env'i yeniden okumaz). Ek: (1) kullanıcıya ham hata + API URL'si
  gösteriliyor ("503 Server Error… for url: https://api.openalex.org/…") → çevrili, anlaşılır mesaj olmalı;
  (2) scraper 503'te beklemeden 3 kez deniyor (yalnız 429'da bekleme var).
  **Bütçe (help.openalex.org/access/example-costs, 28 Eylül 2026):** anahtarsız $0,10/gün, ücretsiz anahtar $1/gün; arama
  $1 / 1.000 istek (liste+filtre $0,10 / 1.000). 5000 kayıtlık arama = 25 istek (per_page=200) → anahtarsız ≈4, anahtarlı
  ≈40 tam arama/gün. Kod `api_key` parametresini zaten gönderiyor — yalnız env gerekli. Not: doküman per_page max 100
  diyor, pratikte 200 çalışıyor (anahtarsız denendi) — uygulanırsa `MAX_PER_PAGE=100` (istek sayısı 2 katı).
- [x] **ACİL — "Havaleyi yaptım" bağlantısı 500 veriyor** — DÜZELTİLDİ (28 Eylül 2026, target=donation → admin bağış sayfası). Eski not:
  `mark_donation_transferred` adminlere `Notification(target=None)` oluşturuyor; model
  `content_type`/`object_id` NOT NULL → IntegrityError, try/except yok. Donation durumu
  `pending_confirmation`'a kaydediliyor ama kullanıcı hata sayfası görüyor, admin bildirimi yok.
- [x] **Davet ödül bildirimi hiç oluşmuyor** — DÜZELTİLDİ (28 Eylül 2026, target=referral_use → /davet/). Eski not: `_notify_referral_reward`
  aynı nedenle (content_type yok) patlıyor; try/except yuttuğu için ödül (20 gün premium,
  +50 itibar, Davetçi rozeti) VERİLİYOR, sadece zil bildirimi + anlık bildirim gitmiyor.
  Davet akışının geri kalanı uçtan uca test edildi, çalışıyor.
- [x] **WhatsApp hazır mesajları Türkçe** — ÇEVRİLDİ (26 Eylül 2026): 6 şablon, `{% filter urlencode:"" %}{% trans %}`; TR mesajları aynen. Eski not:
  `wa.me/...?text=Merhaba%2C...` URL-kodlu sabit TR metin — footer, iletişim, proje
  talebi, eğitim, eğitim talebi, ilan verme sayfaları (6 yer). EN/DE'de mesaj
  kullanıcının dilinde olmalı (`{% trans %}` + `|urlencode`).
- [x] **Footer "Akademik Kaynaklar" EN/DE** — TAMAMLANDI (26 Eylül 2026, kullanıcı
  kararı "uluslararası 4'lü"): EN/DE → Google Scholar, Semantic Scholar, OpenAlex,
  BASE (Bielefeld); TR listesi aynen. `LANGUAGE_CODE` koşulu, yeni ikonlar
  Bootstrap Icons (dış favicon indirilmedi). Eski not (25 Eylül 2026): `templates/partials/footer.html` ~69-92 — başlık çevrili ama liste
  sabit ve Türkiye'ye özgü: Google Scholar, DergiPark, Semantic Scholar, YÖK Tez
  Merkezi (+ yerel favicon'lar `static/img/favicon-*.ico`). EN/DE'de DergiPark ve
  YÖK yerine uluslararası kaynaklar (ör. PubMed, arXiv, OpenAlex, BASE / DE için
  DNB) — dile göre liste (`LANGUAGE_CODE`); kaynak seçimi kullanıcıyla
  netleştirilecek. TR listesi aynı kalır.
- [x] **Hesap silme cron'u kullanıcı kararlarına uydurulacak** (25 Eylül 2026) — 3 adım TAMAMLANDI.
  DÜZELTME: 24 Eylül'deki "silen kod yok" bulgusu YANLIŞTI — işlev var:
  `forum/api_views.py` `cron_process_account_deletions`, Hetzner crontab
  `0 3 * * *`, nginx logunda 23-25 Eylül her gün 200 (processed: 0).
  Kullanıcı kararları (25 Eylül): açık içerik anonimleştir ✅ (zaten öyle);
  DM'ler karşı tarafta kalsın ❌ (kod ikisini de siliyor); mali kayıt anonim
  sakla ⚠️ (Donation.name/email temizlenmiyor); 30 gün içinde giriş yapınca
  iptal ❌ (yok). Ek eksik: tarama/analiz işleri+dosyaları, bildirim,
  PageView, quiz skorları, oda üyelikleri, takip listesi silinmiyor; açık
  ilanlar iptal edilmiyor. Silme mesajı çevrilmemiş.
  - [x] 1. Cron kararlara uyduruldu (25 Eylül 2026): `_anonymize_deleted_account`
    — DM'ler kalır, bağış scrub, siparişli iş korunur (URL+S3 dosyası silinir),
    özel veriler silinir, açık ilan iptal, tek transaction + S3 on_commit.
    Rollback testinde doğrulandı. Canlıya merge ile gider (cron aynı URL).
  - [x] 2. "Geri al" akışı (25 Eylül 2026): custom_login pasif + 30 gün içi +
    şifre doğru → oturuma 10 dk'lık işaret → `/account/restore/` (i18n);
    "Hesabımı geri al" / "Silme işlemi devam etsin". 7 senaryo test edildi.
  - [x] 3. Metinler (25 Eylül 2026): `account_delete.html` gerçek davranışa göre
    yeniden yazıldı (3 yanlış ifade düzeltildi) + EN/DE; silme e-postası alıcının
    dilinde, onay linki `reverse()` ile dil önekli (URL'ler urls_i18n'e taşındı,
    TR yolları aynı); flash mesajları çevrildi; gizlilik metnine "30 gün" +
    anonim mali kayıt geri eklendi.
- [x] **Silinmiş hesabın görünen adı** — ÇÖZÜLDÜ (25 Eylül 2026, kullanıcı
  kararı "okunur kullanıcı adı"): cron artık `silinmis-kullanici-<hex>` üretiyor;
  mevcut `deleted_<hex>` hesaplar **veri migration 0155** ile dönüştürülüyor
  (yalnızca `@deleted.invalid` e-postalılar; ileri/geri test edildi).
  Dile göre "Silinmiş kullanıcı / Deleted user" gösterimi YAPILMADI (37 şablon,
  83 yer + Python tarafı) — istenirse ayrı iş.
- [x] **Profil sayfaları tek dilli** — ÇEVRİLDİ (26 Eylül 2026): `profile_detail`,
  `profile_edit`, `profile_private` + 6 view mesajı; URL'ler `urls_i18n.py`'ye
  taşındı (TR yolları aynı). Telefon (kullanıcı kararı "+90 ekleyebiliriz"):
  `_normalize_tr_phone` 05…/5…/+90/90/0090 kabul eder, `05XXXXXXXXX` saklar;
  yurt dışı numara hâlâ reddedilir. 116 msgid EN/DE. Eski not: profil/profil düzenleme (ve "Hesabımı Sil"
  butonu) i18n dışında — EN/DE kullanıcı silme sayfasına TR olarak ulaşır.
- [x] **Rütbe adları tek dilli** — ÇEVRİLDİ (26 Eylül 2026): `pgettext('rütbe', …)` bağlamı
  ("Üye"/"Aktif Üye" başka yerde çoğul çevrili olduğu için); RANK_CHOICES + RANK_INFO +
  "Ziyaretçi"; migration ÇIKMADI (makemigrations "No changes"). Kullanıcının kendi
  yazdığı Ünvan (`profile.title`, ör. "Platform Yöneticisi") kullanıcı içeriği — çevrilmez.
  Çalışma odası kartındaki "… seviye üye" odalar tek dilli olduğu için kapsam dışı. Eski not: `forum/templatetags/forum_extras.py`
  `RANK_INFO` ("🌱 Çaylak", "Uzman"…) ve `Profile.RANK_CHOICES` (models.py ~156)
  çeviri dışı — site genelinde (navbar, forum, profil) görünür. `gettext_lazy`
  ile sarılınca `RANK_CHOICES` için **no-op AlterField migration** çıkar.
- [x] **Rozet adları/açıklamaları** — ÇEVRİLDİ (26 Eylül 2026, kullanıcı kararı "DB'de dil
  alanları"): `Badge.name_en/_de`, `description_en/_de` + `localized_name` /
  `localized_description` (boşsa TR'ye düşer). **Migration 0156** (4 AddField + mevcut
  18 rozeti slug ile dolduran RunPython; yalnız boş alanları doldurur; geri alma
  test edildi). Admin'de yeni alanlar otomatik görünür. Kullanım yerleri: profil,
  `render_badge`/`render_user_badges`, `can_propose()` gerekçesi.
  **Canlıya çıkışta:** migration'lı deploy → önce DB yedeği.
- [ ] **`create_badges` komutu EN/DE içermiyor** (26 Eylül 2026): boş DB'de komutla
  oluşan rozetler TR'ye düşer (0156 yalnız mevcut kayıtları doldurur).
- [x] **Arena + ★ EN/DE'de gizlendi** (26 Eylül 2026, kullanıcı kararı: "EN/DE yayında; hedef
  proje talebi, analist kazanımı değil → en kayıpsız yol"): `LANGUAGE_CODE == 'tr'` koşulu —
  navbar ★ + Topluluk menüsü/mobil menü/footer Arena linki, anasayfa quiz sütunu + quiz.js
  (AI Asistan sütunu kalır, alt başlık Arena'sız ayrı msgid), market "Arena'da puan kazan"
  linki + oyunlaştırma bandı, profil "Hemen Çöz" butonu. Veri/puan hesabı DEĞİŞMEDİ
  (EN/DE'de analiz puanı arka planda birikmeye devam eder). TR aynen. 3 dilde doğrulandı.
- [x] **EN/DE'de Türkçe sayfalara giden bağlantılar kaldırıldı** (26 Eylül 2026, kullanıcı kararı):
  ölçüm — EN anasayfada 23 bağlantı öneksiz (tüm arayüzü TR'ye çeviren) sayfaya gidiyordu.
  A (forum, blog + anasayfa blog bölümü, başarı hikayeleri + hakkımızda alıntıları) ve
  B (YÖK Tez, TR Dizin, OAI-PMH, uzman dizini, "Uzman olarak katıl") EN/DE'de gizlendi;
  Topluluk menüsü (masaüstü+mobil) ve footer Topluluk sütunu EN/DE'de tamamen yok.
  C (bibliometrik, Tableau, Akademik Tarama/OpenAlex) EN/DE'de GEÇİCİ gizli. D (gelen
  kutusu, ödemelerim, davet) kaldı. Sonuç: EN/DE'de öneksiz hedef yalnız D (ölçüldü).
- [x] **TR-only sayfadan dil değiştirme "sadece yenileniyordu"** — DÜZELTİLDİ (26 Eylül 2026,
  kullanıcı raporu: /tarama/'da TR→EN): Django `set_language` karşılık bulamayınca `next`'i
  aynen döndürüyordu (tarama, forum, blog, YÖK Tez, odalar… hepsi). `forum.views.set_language`
  sarmalayıcı: seçilen dilde karşılık yoksa o dilin ana sayfasına (/en/, /de/). 10 senaryo test.
- [x] **KÖK NEDEN — statik dosyalar hash'siz + 1 yıl immutable önbellek** — ÇÖZÜLDÜ (27 Eylül 2026,
  kullanıcı kararı "1"): settings.py `STORAGES` → staticfiles = whitenoise
  CompressedManifestStaticFilesStorage (hash'li URL: profiles.4d09cb3a1464.css); default =
  FileSystemStorage (fiili davranış korundu). DEBUG=False yerel doğrulama: collectstatic 639
  post-processed hatasız; 294 sayfa gezildi, 0 adet 5xx. deploy.sh collectstatic'i sunucudan
  önce çalıştırıyor. Elle ?v= artık gereksiz (zararsız, kalabilir). Eski not:
  Django 5.2 `STATICFILES_STORAGE` ayarını OKUMUYOR (5.1'de kaldırıldı; settings.py:139) →
  `STORAGES['staticfiles']` = düz StaticFilesStorage, URL'ler hash'siz (`/static/css/profiles.css`).
  nginx `/static/` → `expires 1y` + `Cache-Control: public, immutable`. Sonuç: CSS/JS değişince
  tarayıcılar 1 yıl eskisini kullanır (profil sayfası 3 kez "önbellek" sorunu; canlıda avatar
  devasa göründü). Geçici: `profiles.css?v=0200` (hotfix). Kalıcı çözüm KARARI: (a) `STORAGES`
  ile ManifestStaticFilesStorage'ı gerçekten aç (collectstatic, CSS içindeki eksik url() referanslarında
  hata verebilir → önce yerelde `collectstatic` denenmeli; ?v= elle sürümleme gereksizleşir),
  (b) elle ?v= disiplinine devam. Elle ?v= olmayan diğerleri: inter.css, analiz_console.css,
  sidebar_widgets.js.

- [ ] **`DEFAULT_FILE_STORAGE` da ölü ayar** (27 Eylül 2026): settings.py ~662 Django 5.1+'da
  okunmuyor; S3 alanları `storage=get_storage` ile çalıştığı için bugün sorun yok, ama
  `storage=` verilmemiş bir FileField canlıda yerel diske yazar — denetlenmeli.
- [ ] **Anasayfa TR Dizin kartı bayrağa bakmıyor** (27 Eylül 2026): `/trdizin/` feature_trdizin
  kapalıyken 404 (yerel); home.html araç kartı + kazıma bandı bayrakla koşullanmalı.

**İŞ SIRASI (27 Eylül 2026, kullanıcı):**
- [ ] **Impressum (DE)** (27 Eylül 2026, kullanıcı: "de için bir sayfanın ismini impressum'a mı
  dönüştürsek, hangisi uygun?"): kısa cevap verildi — Impressum yeniden adlandırma değil, ayrı
  yasal sayfa (Almanya §5 DDG / Avusturya ECG: sağlayıcı adı, adres, iletişim, sicil/vergi no.);
  footer'dan her sayfada 1 tıkla ulaşılmalı. İçerik (şirket bilgileri) kullanıcı/avukattan.
- [x] **1. Akademik Tarama hub'ı (/tarama/) EN/DE'de** — YAPILDI (27 Eylül 2026): URL i18n'e taşındı (TR yolu aynı), araçlarda `intl` bayrağı (EN/DE: OpenAlex + Semantic Scholar), tüm metinler EN/DE, navbar her dilde hub'a gider (açılır menü kaldırıldı), `?next` dile göre. Yeni kazıma modülü = listeye bir kayıt. Eski not: (kullanıcı: "tr'de gelen fotoğraflı
  landing'i de/en için de aktif et; buraya iki veri kazıma daha eklenecek"): hub i18n'e
  taşınacak; EN/DE'de yalnız uluslararası araçlar (OpenAlex, Semantic Scholar — YÖK Tez,
  TR Dizin, OAI-PMH gizli); `tarama_hub` view'daki araç başlık/açıklamaları çeviriye;
  EN/DE navbar "Academic Search" hub'a bağlanacak; yeni kazıma modülleri kart eklemeye hazır
  yapı. **Planlanan modüllerin dil kapsamı (kullanıcı, 28 Eylül 2026): PubMed TR/EN/DE üç dilde;
  BASE yalnız DE** (hub'da `intl` yerine dil listesi gerekebilir — tek bayrak DE-only'i ifade etmez).
- [x] **2. Proje talebi EN/DE'de kalan Türkçe ifadeler** — YAPILDI (27 Eylül 2026): kategori `localized_title` + 'Veri Analizi' çevirisi ("New Analysis" bulanık hatası düzeltildi → Data Analysis / Datenanalyse); süre tam cümle ngettext ("completed in 4 months" / "in 4 Monaten abgeschlossen"), şablondaki "{{ duration }} tamamlandı" parçası kaldırıldı; e-posta örneği dile göre (jane@company.com / maria@firma.de). 3 dilde 4 senaryo test. Eski not: (kullanıcı ekran görüntüsü, DE):
  (a) "Kürzlich abgeschlossene Analysen" listesinde kategori adları TR — `views.py` ~2202
  `job.category.title` → `localized_title`, varsayılan 'Veri Analizi' → gettext;
  (b) süre "abgeschlossen in 4 ayda" — `views.py` ~2196 f"{days} günde/haftada/ayda" TR
  parça → çoğul destekli tam cümle msgid (ngettext); (c) e-posta placeholder
  "ayse@sirket.com" (`proje_talebi.html` ~153) → dile göre örnek.
- [x] **3. Profil resmi** — YAPILDI (27 Eylül 2026, kullanıcı onaylı plan): `_process_avatar` —
  yalnız JPEG/PNG/WebP, ≤5 MB, ≤40 MP, Pillow verify; EXIF yönü uygulanır + EXIF/GPS atılır;
  512×512 kare WebP (alfa korunur); ad `avatars/<id>-<rastgele>.webp`. Değiştirince/kaldırınca
  eski dosya depodan silinir (kayıt başarılıysa). "Mevcut fotoğrafı kaldır" seçeneği;
  önizleme + 5 MB istemci ön kontrolü; TR/EN/DE uyarılar. Güvenlik ek: arayüzde olmayan
  `cover_image` doğrulamasız yükleme yolu KAPATILDI. 8 sunucu senaryosu + headless JS testi.
  Mevcut avatarlar değişmedi. Eski not: (kullanıcı: "silme yok; nasıl
  olması gerekirse öyle olmalı"): mevcut akışı incele (yükleme doğrulaması — tür/boyut, eski
  dosyanın S3'ten silinmesi, önizleme, mevcut fotoğrafın gösterilmesi) + "Fotoğrafı kaldır"
  seçeneği ekle. Önce ölçüm + öneri, sonra uygulama.
- [x] **Canlı profil düzenleme sayfası stilsiz görünüyor** — ÇÖZÜLDÜ (tarayıcı önbelleği; 27 Eylül 2026 kullanıcı ekran görüntüsünde doğru). Ek: kayıtlı fotoğraf dosyası yüklenemezse (Render'da kalıcı disk yok) önizleme baş harfe düşüyor (headless test). Eski not: (27 Eylül 2026, kullanıcı ekran
  görüntüsü /de/profile/edit/: başlık büyük, kart yok; sekmeler stilli): canlı profiles.css'te
  yeni sınıflar VAR (ölçüldü) → büyük ihtimal tarayıcı önbelleği; kullanıcıdan Ctrl+Shift+R
  sonucu bekleniyor, sürerse incele.

- [x] **OpenAlex + Semantic Scholar tam çeviri — TAMAMLANDI (dev, merge bekliyor)** (kullanıcı: "önerilerine göre devam et"
  27 Eylül 2026 → SEO rehberi EN/DE gizli; sipariş EN/DE gizli + proje talebi).
  - [x] Aşama 1 tanıtım sayfası: view promo metinleri gettext (22 msgid EN/DE), SEO rehberi yalnız
    TR, S2 "sipariş oluşturun" adımı EN/DE'de "proje talebi bırakın". EN/DE anonim sayfada TR 0.
  - [x] Aşama 2 arama sayfası (27 Eylül 2026): tarama_console_base çevrili + EN/DE yan menüde yalnız
    OpenAlex/S2; giriş yapmış sayfada SEO rehberi yalnız TR; form doğrulama hataları + view mesajları
    (e-posta doğrulama, günlük limit — parça birleştirme 2 tam cümleye bölündü, demo e-posta) çevrili;
    25 msgid (bulanık tahminler yanlıştı, hepsi elle). EN/DE giriş yapmış sayfada TR 0.
    Not: landing JS metinleri zaten etiketliydi (ölçüm aracı yanlış saymıştı).
  - [ ] **DURAKLATILDI (27 Eylül 2026, kullanıcı: "pause")** — bibliometri Aşama 1–4 dev'de (2e94544, d9af3f5, 0865346), main/canlı cd68fa1 (28 Eylül; araya 3 düzeltme cherry-pick ile girdi); MERGE EDİLMEDİ (migration yok, 61/61). Sıradaki öneri: (a) Research Gap grafiği + 15 analizin doğruluk testleri → (b) S2 bağlantısı (migration: BibliometricJob'a S2 FK) → (c) OpenAlex tekrar kayıt.
  - [ ] **BİBLİOMETRİ EN/DE — DEVAM EDİYOR** (kullanıcı kararları 27 Eylül 2026: S2 bağlantısı eklensin +
    analiz sonuçları test edilsin; bibliometri sayfası EN/DE evet; tekrar kayıt incelensin evet).
    - [x] Aşama 1 tetikleme+e-posta: bibliometrics URL'leri i18n'e; OpenAlex JS fetch `{% url %}`+sentinel;
      views mesajları (66 msgid, bulanık tahminler elle düzeltildi); arka plan `_in_user_language`
      (upload + openalex); 3 e-posta alıcı dilinde (OpenAlex işinde "yüklediğiniz dosya" hatası ve
      Türkçe karaktersiz e-posta düzeltildi); tam rapor EN/DE → proje talebi. Test: DE kullanıcı
      gerçek analiz motoruyla 130 kayıt → completed, e-posta Almanca.
    - [x] Aşama 2 PDF rapor (27 Eylül 2026): analyzer (grafik başlık/eksen/lejant/tablo/yayın türü,
      grafik İÇİ f-string başlıklar dahil) + pdf_builder (kapak, sayfa "Seite x / y", altbilgi) + sorgu
      özeti alan adları çevrili; ~95 msgid elle (bulanıklar yanlıştı). 🎯 kaldırıldı (glif uyarısı 0).
      **Doğruluk düzeltmesi:** kapak "TAM RAPOR (10 Analiz)" diyordu, rapor 15 analiz içeriyordu →
      sayı gerçek grafik sayısından. Test: 160 kayıt, 3 dil PDF; EN/DE metin katmanında TR 0; DE
      sayfaları görsel kontrol (Lotka, atıf tablosu tamamen Almanca). Ders: tarayıcıda `\w` Türkçe
      harfleri kapsıyor (lessons.md).
    - [x] **Araştırma Boşluğu Haritası PDF'te bozuk (ÖNCEDEN VAR)** — kapatıldı (düzeltme 28 Eylül'de canlıya gitti; E testlerinde PDF'te düzgün) (27 Eylül 2026): `research_gap`
      bbox_inches='tight' ile 744×15562 px üretiyor (grafik dışında bir öğe alanı uzatıyor) → PDF'te
      ince boş şerit. Orijinal kodla birebir aynı (sentetik 160 kayıt). Ücretli raporda — "analiz
      sonuçları test edilsin" kapsamında düzeltilecek.
      → **DÜZELTİLDİ (28 Eylül 2026, commit bekliyor):** kök neden alt kadran etiketleri `y=med_impact*0.15`
      (veri koordinatı, eksen 0'dan başlar varsayımı); etki değerleri dar aralıkta (0.946–1.003) toplanınca
      etiket −10180 px'e düşüyordu. Kadran etiketleri artık x=veri / y=eksen oranı. 160 kayıt: 1472×13294 → 1472×1071.
    - [x] Research Gap (1)–(3) DÜZELTİLDİ (28 Eylül 2026): gölge medyan çizgilerine göre `fill_between`,
      lejant eksenin üstünde (4 sütun), "RESEARCH GAP"/"ALTIN ALAN" gettext (EN GOLDEN AREA, DE FORSCHUNGSLÜCKE /
      GOLDENES FELD). DE çıktı kontrol edildi.
    - [ ] Research Gap (4) yöntem sorusu kullanıcı kararı bekliyor. Tarihçe — kalan sorunlar (28 Eylül 2026):
      (1) kadran arka plan gölgesi `ymin=0.5` (eksenin yarısı) — medyan çizgisiyle çakışmıyor, x'te de eksenin
      tamamını kaplamıyor → kadran yanlış gösteriliyor; (2) "YÜKSELİŞTEKİ ALAN" etiketi lejantın altında kalıyor;
      (3) "ALTIN ALAN" / "★ RESEARCH GAP" etiketleri gettext'e sarılmamış (EN/DE PDF'te TR);
      (4) yöntem sorusu: trend = (son 3 yıl − önceki tüm yıllar)/toplam — dönem uzunlukları farklı, uzun
      zaman aralıklı veride tüm anahtar kelimeler negatif ("azalıyor") çıkıyor; kadranlar medyana göre göreli
      olduğu için sınıflama çalışıyor ama eksen etiketi yanıltıcı. Yıllık ortalamaya normalize etmek önerilir.
      Bibliometri analizlerinin otomatik testi YOK (forum/tests.py'de yalnız 1 proje-talebi testi).
    - [x] Aşama 3 bibliometri sayfası (27 Eylül 2026): landing (HTML + JS `T` sözlüğü + `fmt`), form etiket/
      hata mesajları çevrili; sabit `/bibliometrics/...` fetch adresleri `{% url %}`+sentinel; EN/DE
      navbar'da (masaüstü+mobil) açık. TR görünen metin öncekiyle birebir aynı (otomatik karşılaştırma;
      "Email"→"E-posta" gibi istemeden yaptığım TR değişiklikleri geri alındı). EN/DE TR kalan 0.
    - [x] Aşama 4 sipariş (27 Eylül 2026): EN/DE'de sonuç panelinde fiyat gizli + buton proje talebi,
      geçmiş tablosunda "Sipariş" → proje talebi, sipariş sayfası 302 → /en|de/proje-talebi/.
    - [ ] **BİBLİOMETRİ DOĞRULUK DENETİMİ (28 Eylül 2026)** — 17 analiz + parser okundu. Doğru bulunan: h-index,
      CAGR formülü, yıllık büyüme formülü, Lotka normalizasyonu, top yazar/dergi/atıf sayımları.
      Hatalı / karar gerektiren (öncelik sırasıyla):
      - [x] **K1 DÜZELTİLDİ (28 Eylül 2026):** WoS TSV `;` + `_wos_fmt_author` (.txt ile aynı ad biçimi); Scopus/generic
        `_split_author_list` (`;` varsa o, yoksa `,` + "Soyad, Baş harf" çiftlerini birleştirme); 8 örnek + WoS betiği geçti.
        Eski not: **K1 Yazar adları virgülden bölünüyor** — `_parse_wos_csv`, `_parse_scopus_csv`, `_parse_generic_csv`
        `re.split(r'[;,]')`: WoS sekmeli "Smith, J; Doe, JA" → ['Smith','J','Doe','JA']; yeni Scopus
        "Smith, J.; Doe, J.A." de aynı (eski Scopus "Smith J., Doe J.A." doğru). Örnekle doğrulandı. Etkilenen:
        En Verimli Yazarlar ("J" üretken yazar görünür), Lotka, Yazar İşbirliği Ağı. WoS düz metin (.txt) doğru.
      - [x] **K2 DÜZELTİLDİ (28 Eylül 2026):** ortalama/medyan ve yıllık ortalama tüm yayınlar üzerinden; h-index ve sıralı
        grafik aynı. Bilinen veri (10,5,3,0,0): ort 3.6 / medyan 3 (eski 6.0 / 5). Eski not: **K2 Ortalama/medyan atıf yalnız atıflı yayınlardan** — `citation_analysis` "Ort. Atıf / Yayın" ve
        "Medyan Atıf" 0 atıflıları dışlıyor (değer şişik); `annual_citation_trend` yıllık ortalama da öyle.
      - [x] **K3 DÜZELTİLDİ (28 Eylül 2026):** scraper'a `institution_list` (liste) eklendi, `institutions` metni aynen
        (CSV/TXT dışa aktarım etkilenmez); parser yalnız listeden okur, eski aramalarda kurum boş → grafik üretilmez
        (kullanıcı kararı "a"). Not: grafik kayıt başına İLK kurumu sayar (ilk yazarın kurumu) — ayrı karar.
        Eski not: **K3 OpenAlex kurumları tek metin** — scraper `', '.join(institutions[:5])`, analyzer `split(';')[0]` →
        "Kurumlara Göre Dağılım" 5 kurumluk birleşik metni tek kurum sayıyor (OpenAlex ana kaynak). Kurum adları
        virgül içerdiği için eski kayıtlar güvenilir bölünemez; yeni aramalar için ayırıcı '; ' olmalı.
      - [x] K4 DÜZELTİLDİ (28 Eylül 2026, kullanıcı: "önerilerine göre" = Babel + tam sayım): scraper `country_list`
        (ISO-2, tüm yazarlar), parser `country`='TR; US', analyzer `_country_label` (Babel, etkin dil) +
        `_record_countries` (ülke dağılımı ve işbirliği ağı ortak; "Turkey; USA" artık 2 ülke). Eski aramalarda ülke yok.
        ⚠️ **requirements.txt'e Babel eklendi → Hetzner deploy'da `docker compose build` ŞART** (yoksa kod gösterir, çökmez).
        Eski not: K4 OpenAlex'te ülke yok → Ülke dağılımı / Ülke İşbirliği Ağı OpenAlex işlerinde hiç üretilmiyor
        (API `authorships[].countries` veriyor). WoS düz metinde de CU etiketi standart değil (ülke C1 adresinde).
      - [x] K5 DÜZELTİLDİ (28 Eylül 2026): yayın trendi, büyüme oranı ve anahtar kelime trendi ardışık takvim yılları (boş
        yıl 0); önceki yılı 0 olan yılın büyümesi tanımsız → çubuk yok. Test: 2018 eski −%50 (2016'ya göre) → boş. Eski not: K5 Boş yıllar: yayın olmayan yıl atlanıyor → büyüme oranı ardışık olmayan yıllar arasında hesaplanıyor.
      - [x] K6 DÜZELTİLDİ (28 Eylül 2026, kullanıcı: "dışarıda bırakılsın"): `_last_complete_year()` = bugün−1; yayın trendi,
        büyüme/CAGR, kw trendi, yıllık atıf, Research Gap (yılsız kayıtlar da artık "eski" sayılmıyor). Diğer analizler (yazar,
        dergi, atıf tablosu) tüm kayıtlarla. Eski not: K6 İçinde bulunulan (eksik) yıl dahil → son yılda yapay düşüş (büyüme, CAGR, Research Gap trendi). Karar.
      - [x] K7 DÜZELTİLDİ (28 Eylül 2026, kullanıcı onayı): `parse_openalex_json` concepts yalnız keyword yoksa yedek;
        boş keyword elenir. 4 senaryo test edildi. Eski not: OpenAlex "concepts" (Computer science, Medicine gibi geniş alanlar) anahtar kelimelere katılıyor →
        kelime bulutu/ağı/trendi/Research Gap'e baskın genel terimler giriyor. Karar.
    - [ ] **ŞEFFAFLIK: "Veri ve Yöntem" bölümü (28 Eylül 2026, kullanıcı sorusu: hangi filtreler, hangi kayıtlar neden
      dışarıda, kısıtlar nasıl bilinecek?)** — raporda şu an yalnız toplam kayıt + dosya adı var; elemeler sadece log'a.
      ⚠️ **KRİTİK bulgu:** OpenAlex çekimi `sort=publication_year:desc` + `scrap_max_records` (varsayılan 5000) → sonuç
      5000'den fazlaysa yalnız EN YENİ 5000 analiz ediliyor; eski yıllar kesiliyor → yayın trendi/CAGR/Research Gap
      yapay "artış" gösterir, raporda hiç belirtilmiyor. Sayfalama hatasında da sessizce kısmi veriyle devam ediliyor.
      Öneri (onay bekliyor): PDF'e kapaktan sonra "Veri ve Yöntem" sayfası — (1) veri akışı tablosu (kaynakta bulunan →
      çekilen → başlıksız çıkarılan → tekrar çıkarılan → analize giren), (2) alan doluluk tablosu (yıl/yazar/kelime/atıf/
      dergi/ülke/kurum: kaç kayıt, %), (3) uygulanan kurallar/eşikler, (4) üretilemeyen analizler ve nedeni, (5) bilinen
      kısıtlar; her grafiğin altına "n = X kayıt". Migration yok (tam PDF aynı çalıştırmada üretiliyor).
      **Kullanıcı kararı (28 Eylül 2026):** analizler "örnek" niteliğinde; kısıtlar raporun SONUNDA verilsin + kapsamlı analiz
      için uzmanlarla görüşme yönlendirmesi. 5000 sınırı için hesap değişmez (seçenek b), açıkça yazılır.
      PLAN (dosya listesi onay bekliyor):
      - [x] A (28 Eylül 2026, test edildi) `parser.py`: `_deduplicate_and_filter(records, stats=None)` başlıksız/tekrar sayılarını `stats`'a yazar;
            `parse_file` ve `parse_openalex_json` `stats` geçirir (geriye uyumlu, varsayılan None).
      - [x] B (28 Eylül 2026, test edildi) `analyzer.py`: `run_all_analyses(records, skipped=None)` üretilemeyen analizleri (başlık + neden) toplar.
      - [x] C (28 Eylül 2026, sentetik test: sınır aşan/eksik/tam/dosya) YENİ `report_notes.py` → `build_report_notes(records, stats, skipped, source)`
            dict döner (flow, coverage, rules, skipped, limitations, source_warnings, partial_year); eşikler analyzer varsayılanlarından (inspect).
            Not F: "%{pct}" içeren msgid — makemessages python-format işaretlerse kontrol et.
            Eski plan: alan doluluk tablosu, uygulanan kurallar/eşikler, bilinen kısıtlar, sınır uyarısı
            (OpenAlex: bulunan > çekilen → "en yeni N kayıt, YYYY öncesi kapsam dışı"; çekilen < min(bulunan, sınır) →
            "çekim eksik kaldı").
      - [x] D (28 Eylül 2026, uçtan uca test: OpenAlex + 2 dosyalı Scopus CSV, rollback) `build_full_pdf(..., notes=)` parametresi eklendi (E'ye kadar kullanılmıyor). Eski plan: `job_runner.py`: iki akışta (dosya / OpenAlex) `stats` + `skipped` + kaynak bilgisi → `build_full_pdf`.
      - [x] E (28 Eylül 2026, test: sınır aşan/eksik çekim/dosya+üretilemeyen analiz, job_runner uçtan uca, sayfa görüntüleri kontrol)
            Kullanıcı kararları: kapanış notu HER DİLDE proje talebi; demo'ya yalnız uyarı satırı (bölüm yok); zaman serisi
            bayrağı `run_all_analyses(time_series=)` (başlık karşılaştırma yok). Kesinti uyarısı eksik çekimde de çıkar
            (`partial_year`). Atıf 0 ve DOI doluluk kısıtı sayılmaz. DejaVu `<b>` eşlemesi eklendi. Eski plan: `pdf_builder.py`: tam raporun sonuna "Veri, Yöntem ve Kısıtlar" sayfası(ları) + kapanış notu (TR sipariş,
            EN/DE proje talebi); sınır aşıldıysa trend grafiklerinin sayfasına kısa uyarı satırı. Demo PDF değişmez.
      - [x] F (28 Eylül 2026) 62 msgid EN/DE (C/E metinleri + B'nin 16 "üretilemeyen analiz" nedeni — onlar da çevrilmemişti);
            po sonuna düz metin eklendi, host `msgfmt -c` exit 0 (container'da msgfmt yok; polib container'a geçici kuruldu). Eski plan: `locale/en|de` po+mo (yeni msgid'ler elle).
      - [x] G (28 Eylül 2026) 3 senaryo (sınır aşan / eksik çekim / dosya+üretilemeyen) × TR/EN/DE × tam+demo: EN/DE metin katmanında
            Türkçe kalıntı yok (özel harf + ö/ü'lü TR kelime + ASCII TR kelime taraması), sayfa görüntüleri kontrol; metin içi sayılar
            dile göre binlik ayırıcılı yapıldı. Eski plan: Test: dosya + OpenAlex (sınır aşan/aşmayan) sentetik iş, 3 dil PDF, metin katmanında TR kalıntısı kontrolü.
      Açık soru: kullanıcının "2026 yayınları tarih/DOI varsa alınsın" isteği netleşmedi (şu an 2026 yalnız yıllık grafiklerde yok).
    - [ ] Yükleme hata mesajında "file: " alan adı öneki (önceden var) — view form hatalarını ham basıyor.
    - [ ] **İçerik kararı:** bibliometri sayfası/promo "10 analiz" diyor, rapor 15 analiz içeriyor (kapak
      artık gerçek sayıyı yazıyor) — pazarlama metni güncellensin mi? (kullanıcı)
    - [ ] Semantic Scholar → bibliometri bağlantısı + analiz sonuç testleri
    - [ ] OpenAlex tekrar kayıt (dedup) incelemesi
    Not: bibliometri promo "10 farklı analiz / 10 grafik" diyor, e-postalar/rapor 15 — içerik tutarsızlığı.
    İnceleme notu: (kullanıcı: "bibliometri de
    de/en olmalı; open alex ve scholar işleyişini incele"). Akış: OpenAlex (≥100 sonuç) → buton →
    i18n DIŞI `/bibliometrics/from-openalex/<id>/` → parse_openalex_json → arka planda 15 analiz →
    demo PDF (3 grafik) e-posta → tam rapor sipariş (Türk IBAN/TL) + admin onayı. **Semantic
    Scholar → bibliometri bağlantısı YOK** (buton/adapter/endpoint yok; veri yapısı uygun). Dil:
    tamamen TR — views ~38, analyzer ~73 (grafik başlık/etiket/yorum → EN/DE'ye TR PDF gidiyor),
    pdf_builder ~13, e-postalar 3 tür (recipient_language yok), landing ~90, order ~34.
    Plan: 1 tetikleme+e-posta (i18n URL, arka plan dili) → 2 PDF rapor → 3 bibliometri sayfası
    EN/DE → 4 sipariş EN/DE → proje talebi. Karar bekleyen: S2 bibliometri bağlantısı (yeni
    özellik, önerilen: evet, çeviriden sonra); bibliometri sayfası EN/DE'de açılsın mı (önerilen evet).
  - [ ] **OpenAlex sonuçlarında aynı yayın tekrarı** (27 Eylül 2026, kullanıcı ekran görüntüsü DE:
    "Design, Fabrication, and Performance Evaluation of a Weeder…" iki kez) — muhtemelen aynı çalışmanın
    iki OpenAlex kaydı (Zenodo). Liste + bibliometri sonuçlarını etkiler (dedup) — incelenmeli.
  - [x] (eski) **Bibliometrik analize gönder** (OpenAlex sonuçları) `/bibliometrics/`'e gidiyor — o sayfa TR-only
    ve EN/DE'de gizli; promo'da "Tek Tıkla Bibliometrik Analiz" EN/DE'de vaat ediliyor → Aşama 3'te karar.
  - [x] Aşama 3 sonuç/indirme (27 Eylül 2026): `_execute_job` → işi başlatan kullanıcının dili
    (recipient_language, profil tercihi — restart'ta kaybolmaz) altında `_execute_job_body`; TXT
    üreticileri çevrili + hizalama etiket uzunluğuna göre; Excel başlıkları/sayfa adı çevrili
    ("No" → pgettext 'sıra numarası': TR'de Django'nun "Hayır" çevirisine düşüyordu — yakalandı);
    S2 API hata mesajları çevrili. Test: DE kullanıcı arka plan TXT Almanca, TR Türkçe; S2 limit
    hatası DE; Excel/TXT indirme 3 dilde doğru.
  - [x] Aşama 4 sipariş (27 Eylül 2026): demo e-postası EN/DE'de sipariş yerine proje talebi linki
    (alıcı dilinde /en|de/proje-talebi/?source=tool), TR aynı; sipariş sayfası EN/DE'de proje
    talebine 302, TR 200. Test: TR/DE kullanıcı × 2 araç × 3 dil.
  Ölçüm notu:
  etiketli 148 msgid'in hepsi çevrili; eksik olan ETİKETSİZ metin ~270: promo context (views) +
  service_promo.html ~40 (anonim ziyaretçi), SEO rehberi tarama_seo_content.py ~6.600 kr,
  landing (şablon+JS) + tarama_console_base.html ~90, forms ~23, order.html ~60, TXT/Excel
  başlıkları + scraper hata mesajları ~60 (job_runner arka plan → dil taşınmalı). Aşamalar:
  1 promo → 2 arama sayfası → 3 sonuç/indirme → 4 sipariş. Karar bekleyen: SEO rehberi EN/DE
  (a gizle önerilen / b ayrı içerik); sipariş sayfası EN/DE — Türk IBAN + TL havale
  (a çevir / b gizle + proje talebi önerilen / c ödeme kararına kadar beklet).
- [x] (eski) **OpenAlex + Semantic Scholar tam EN/DE çevirisi** (26 Eylül 2026, kullanıcı: "todo'ya
  yaz, şimdiden açık kalabilir"): EN/DE navbar'da "Academic Search" açılır menüsüyle AÇIK
  (masaüstü + mobil; /tarama/ hub'ı yerine doğrudan iki araç). Kalan çeviri: landing'lerde
  EN render'da görünür metnin ~2/3'ü TR (OpenAlex 27/41, S2 25/41) — kaynağı (view context /
  `tarama_console_base.html` / msgstr boş) ÖLÇÜLECEK; `order.html`'ler 0 etiket (~60 metin);
  sonuç/iş durumu JS metinleri ve e-postalar da kontrol edilecek. (Anasayfadaki sabit
  `href="/openalex/"`'ler artık yalnız TR'de render ediliyor — EN/DE sorunu kalmadı.)
- [ ] **C grubu sayfaların EN/DE çevirisi** (26 Eylül 2026, kullanıcı: "sonraki projede
  lazım olacak, bibliometrik analizler gibi"): Bibliometrik Analiz, Tableau Analizleri,
  Akademik Tarama (/tarama/, OpenAlex, Semantic Scholar). DÜZELTME (26 Eylül 2026, ölçüldü):
  OpenAlex ve Semantic Scholar URL'leri ZATEN i18n_patterns içinde (/en/openalex/ 200) ama
  içerik yarı çevrili — EN'de görünür metnin ~2/3'ü TR (OpenAlex 27/41, S2 25/41; başlık/
  özellik kartları Python context veya ortak şablondan TR geliyor olabilir — doğrulanmadı),
  `order.html`'lerde 0 etiket (~60 metin). `/tarama/` hub'ı i18n dışı (EN'de 404) ve
  YÖK Tez/TR Dizin'i de listeliyor. Kullanıcı: "sonraki projede yeni veri kazıma
  modülleri eklenecek" → EN/DE "Academic Search" hub'ı o projede kurulmalı. Çevrilince
  URL'ler `urls_i18n`'e taşınır ve base.html/home.html'deki `LANGUAGE_CODE == 'tr'`
  koşulları kaldırılır. İlgili: `BASE_PubMed_Integration_Project.md` (ayrı oturum) — **dil kapsamı:
  PubMed TR/EN/DE üç dilde, BASE yalnız DE** (kullanıcı, 28 Eylül 2026).
- [ ] **D grubu hesap sayfaları tek dilli** (26 Eylül 2026): gelen kutusu, ödemelerim,
  arkadaşını davet et — EN/DE kullanıcısını TR arayüze götürüyor; şimdilik kalsın (kullanıcı).
- [ ] **YouTube Transcript tamamen kaldırılacak — AŞAMA 2 ERTELENDİ (kullanıcı: "todo'ya al", 26 Eylül 2026); bir sonraki merge'den önce ayrı iş olarak** (26 Eylül 2026,
  kullanıcı: "TR'de de ihtiyaç değil"): Aşama 1 YAPILDI — navbar bağlantısı kaldırıldı.
  Aşama 2 (kod+DB): `transcript/` app (3 migration, TranscriptJob/TranscriptSettings),
  INSTALLED_APPS, urls.py, `analizdestek/job_queue.py`, hesap silme listesi
  (`api_views` ~567), `SiteSettings.feature_transcript` + context_processors + admin,
  `requirements.txt` youtube-transcript-api (→ docker build), `transcript_local.py`,
  analizus.md. DB tabloları: `migrate transcript zero` (canlı DB) + S3 dosyaları.
- [ ] **Başarı hikayesi modalı ölü kod** (26 Eylül 2026): `openStoryModal()` hiçbir yerden
  çağrılmıyor; `#storyModal` her sayfada render ediliyor (profil modalıyla aynı durum).
- [x] **EN/DE anasayfa JSON-LD** — DÜZELTİLDİ (27 Eylül 2026): 4 TR blok (WebSite tr-TR, FAQ
  forum atıflı, ItemList + SoftwareApplication YÖK Tez/TR Dizin) yalnız TR; EN/DE'ye dile uygun
  WebSite bloğu (inLanguage en/de, /en/ URL); base.html Organization açıklaması çevrili
  (EN "Academic Analysis and Data Science Platform"). 9 sayfada JSON geçerliliği test edildi.
- [ ] **Organization JSON-LD `availableLanguage: "Turkish"`** (27 Eylül 2026, iş kararı): EN/DE
  müşteri desteği veriliyor mu? Veriliyorsa ["Turkish","English","German"] yapılmalı.
- [x] (eski) **EN/DE anasayfa JSON-LD TR URL'leri** (26 Eylül 2026): home.html ~168–196 structured
  data EN/DE sayfada da YÖK Tez/TR Dizin/OpenAlex/OAI-PMH URL'lerini ve TR açıklamaları veriyor.
- [x] **EN/DE → proje talebi AŞAMA 1** — YAPILDI (27 Eylül 2026): `ProjectRequest.language`
  (**migration 0158**, yalnız AddField; ileri/geri test), admin Dil sütunu + filtre, ekip
  e-postasına konu `[EN]`/`[DE]` + "Dil: EN — müşteriye bu dilde dönüş yapın"; admin
  e-postasında ad/e-posta/şirket/açıklama escape (XSS test: `<img onerror>`/`<script>`
  kaçışlandı). 3 dilde gönderim test edildi. Eski kayıtlarda dil boş.
- [x] **EN/DE → proje talebi AŞAMA 2** — YAPILDI (27 Eylül 2026): EN/DE hero birincil buton
  "Get your analysis done by an expert" (+ "Free initial assessment · No obligation"), dosya
  alanı ikincil; market uzman sütunu → proje talebi kartı; navbar çerçeveli CTA (bundle.css
  kaynaklardan yeniden üretildi — önce birebir aynı olduğu doğrulandı); footer Kurumsal'a link;
  Nasıl Çalışır + SSS sonuna çağrı; pazar yeri sayfasına yönlendirme. EN anasayfada proje
  talebi çağrısı 5 → 9. Yeni kaynaklar: nav, footer, home_market, home_steps, home_faq,
  market_page + eksik olan analiz_triyaj (önceden 'direct' sayılıyordu) → **migration 0159**
  (yalnız choices, SQL no-op). TR görünümü aynı. Eski not: (kullanıcı kararları 27 Eylül 2026: pazar yeri EN/DE
  "(a) kalsın + proje talebi yönlendirmesi"; hero birincil CTA EN/DE'de proje talebi "olsun"):
  hero birincil CTA, market uzman sütunu → proje talebi kartı, navbar buton, footer link,
  nasıl çalışır/SSS sonu çağrı, market sayfası üstüne proje talebi yönlendirmesi.
- [ ] **AŞAMA 3:** 2–4 hafta sonra admin'de dil + kaynak filtresiyle talep ölçümü.
- [x] (eski) **EN/DE'yi proje talebine evriltme — ÖNERİ** (27 Eylül 2026, ölçüldü):
  EN anasayfa: navbar sade link; hero yalnız ikincil link; market bölümü sağ sütunu UZMAN
  KAZANIMI (EN/DE'de ters); nasıl çalışır/güven/araçlar/SSS'de çağrı yok; footer'da yok;
  18 araç sayfasında var. Form EN/DE hazır (onay e-postası müşteri dilinde). EKSİK: ekibe
  giden bildirimde müşteri dili yok, ProjectRequest'te dil alanı yok (ölçülemiyor); admin
  e-postasında ad/açıklama escape edilmiyor (güvenlik).
  Öneri: Aşama 1 dil alanı (migration) + admin filtre + e-posta [EN]/[DE] + escape;
  Aşama 2 (EN/DE şablon) hero birincil CTA → proje talebi, market uzman sütunu → proje
  talebi kartı, navbar buton, footer link, nasıl çalışır/SSS sonu çağrı; Aşama 3 2–4 hafta
  sonra dil+kaynak ölçümü. Kullanıcı kararı bekleyen: pazar yeri EN/DE (a kalsın+yönlendirme
  önerilen / b gizle / c aynen), hero birincil CTA değişsin mi.
- [x] (eski) **EN/DE'yi proje talebine evriltme** (26 Eylül 2026, kullanıcı hedefi): EN/DE'de
  hâlâ uzman/topluluk odaklı yüzeyler var (Topluluk menüsü → forum/çalışma odaları TR-only,
  market uzman tanıtımı, puan/rütbe/rozet vurgusu profilde). EN/DE navigasyon ve anasayfa
  akışının "proje talebi" etrafında yeniden düzenlenmesi — ayrı iş, önce öneri + onay.
- [x] **Yerel runserver'da dil değiştirme** — ÇÖZÜLDÜ (26 Eylül 2026): kod sorunu değildi;
  kullanıcının runserver'ına doğrudan POST → 302 /en/ + `django_language` çerezi doğru.
  Sunucu yeniden başlatma + tarayıcı yenilemesiyle düzeldi (önbellek). Eski not: Docker
  yerel + Render'da çalışıyor (CSRF'li testte TR→EN→DE→TR 302 doğru). Şüphe: yerel SQLite'ta
  0156/0157 uygulanmamış → hedef sayfa 500. Kullanıcıdan runserver konsol çıktısı bekleniyor.
- [x] (eski) **Quiz (İstatistik Arena) modülü tamamen tek dilli** (26 Eylül 2026, ölçüldü):
  435 soru (yerel; python 130, r 130, spss 125, statistics 50) yalnız TR DB metni;
  `static/js/quiz.js` 16 satır sabit TR (geri bildirim "Doğru! +10 puan kazandın.",
  "Yanlış. Doğru cevap:", "Yeni rozet:", yedek sorular); base.html eski quiz modalı
  (`loadQuizQuestion`) + "TEBRİKLER! İstatistik Ustası" metni; `api_submit_quiz_answer`
  hata mesajları TR. EN/DE anasayfada Arena bölümü TR sorularla görünüyor.
  Seçenekler: (a) EN/DE'de Arena'yı gizle, (b) arayüz metinlerini çevir + sorulara
  dil alanı (435 soru çevirisi), (c) EN/DE için ayrı soru seti. Rozet adı işi buna bağlı.
  Ek bulgu: `badge_awarded` sayaç ==50 / ==1000 olunca rozetin gerçekten verilip
  verilmediğine bakmadan gösteriliyor.
- [x] (eski not) **Quiz rozet bildirimi TR sabit** (26 Eylül 2026): `forum/views.py` ~3010
  `category_badge_map` / `'Quiz Efsanesi'` sabit Türkçe adlar — `Badge.localized_name`
  ile slug'dan alınmalı (quiz modülü genel olarak tek dilli mi — önce ölç).
- [x] **EDU "Doğrulanmış Akademisyen" DM** — ÇEVRİLDİ (26 Eylül 2026): tek msgid,
  `recipient_language(user)` ile alıcının dilinde üretilip DB'ye yazılıyor (istek dili
  TR olsa da); TR/EN/DE doğrulandı.
- [ ] **EDU tanıma yalnız `.edu` / `.edu.tr`** (26 Eylül 2026): `_handle_edu_user` Alman
  (`uni-*.de`, `tu-*.de`, `*.uni-*.de`), İngiliz (`.ac.uk`), Avusturya (`.ac.at`) vb.
  akademik adresleri tanımıyor → EN/DE akademisyen rozet/3 gün teklif hakkı alamaz.
  Alan adı listesi iş kararı (hangi ülkeler, sahte alan riski).
- [x] **EN/DE kullanıcı puan/yetki ekonomisi** — KARAR: EN/DE'de uzman kazanımı hedef değil; puan kuralları aynı, ★ EN/DE'de gizli (26 Eylül 2026). Ölçüm notu:
  Navbar ★ = `reputation`; kaynaklar: analiz tamamlama +5 (EN/DE çevrili), forum konu
  +5 / cevap +2 / beğeni +5 / en iyi cevap +20 (forum TR-only, i18n dışı), Arena doğru
  cevap +10 (EN/DE'de gizlenecek). Puana bağlı işlevler: rütbe (50/200/500/1000/2500/
  5000), teklif verme (rütbe ≥ Uzman = 1000 puan, veya Premium/EDU/özel rozet), ilan
  süresi (<500 → 10 gün, 500+ → 20, 1000+ → 30), çalışma odası açma
  (`STUDYROOM_MIN_POINTS`), puan rozetleri. İlan AÇMA puana bağlı değil (e-posta
  doğrulama + haftalık limit 1/3). EN/DE'de tek kaynak analiz → 1000 puan = 200 analiz.
  Ayrıca ★ tıklanınca `#istatistik-arenasi`'ya gidiyor — Arena gizlenince EN/DE'de hedef değişmeli.
- [x] (eski not) **EDU "Doğrulanmış Akademisyen" DM metni TR sabit** (26 Eylül 2026):
  `forum/views.py` ~1330 — DM DB'ye yazılıyor; alıcının dilinde (`recipient_language`) üretilmeli.
- [x] **Profil modal — ölü kod silindi** (26 Eylül 2026, kullanıcı onayı): ölçüm — view
  `api_get_profile_summary` hiçbir URL'ye bağlı değildi, `openProfileModal()` hiç
  çağrılmıyordu, iki şablon kopyası kullanılmıyordu. Silinenler: view, base.html
  `#profileModal` + JS, `forum/profile_modal_content.html`, `templates/profile_modal_content.html`
  (169 satır). 12 sayfa 200/302, 38 inline script `node --check` temiz, 61/61. Eski not: `views.py` ~3043
  `forum/partials/profile_modal_content.html` render ediyor ama bu şablon yok
  (`forum/profile_modal_content.html` ve `templates/profile_modal_content.html` var,
  ikisi farklı). URL'nin kullanılıp kullanılmadığı ölçülecek.
- [x] **Rozet adları/açıklamaları tek dilli** — eski not (26 Eylül 2026): `Badge.name` /
  `Badge.description` DB içeriği ("Profesör", "2500 akademik puan kazandınız -
  TEKLİF VEREBİLİR"…) EN/DE profilde TR. Strateji kararı gerekli: slug→çeviri
  sözlüğü (kod) mi, DB'de dil alanları (migration) mı. `can_propose()` rozet
  adını gerekçe olarak döndürüyor — o da etkilenir.
- [x] **Yetenek (JobCategory) başlıkları** — YAPILDI (26 Eylül 2026, kullanıcı kararları:
  DB dil alanları + yeni kategori admin onayına + onaylı temizlik tablosu).
  **Migration 0157**: `title_en/_de` + veri adımı — 6 birleştirme (37,41,42→3;
  39→25; 35→23; 34→6; ilan FK + uzman yetenekleri taşınır, çift bağ oluşmaz),
  6 ad düzeltme, 5 pasife alma (C++, Java, Javascript, SEO, Web tasarımı),
  32 aktif kaydın EN/DE çevirisi. Her adım id+başlık eşleşirse çalışır;
  idempotent; geri alma veri için no-op → **deploy öncesi DB yedeği şart**.
  Canlı kopyasıyla (43 kayıt + yabancı kayıt) test edildi: 43→37, aktif 32.
  `JobPostForm`: yazılan metin TR/EN/DE başlıkla (iexact) eşleşir; yoksa
  `is_active=False` oluşur. Gösterim: profil, düzenleme, uzman dizini,
  expert showcase, market liste/detay, ilan datalist'i.
- [ ] **Kategori eşleşmesinde Türkçe İ/i** (26 Eylül 2026): `title__iexact`
  PostgreSQL'de "YENİ" ile "yeni"yi eşleştirmiyor → ayrı pasif kayıt açılır
  (admin onayına düştüğü için etkisi düşük). Gerekirse Python tarafında
  `casefold` + TR i/İ normalizasyonu.
- [ ] **Yeni pasif kategoriler için admin bildirimi yok** (26 Eylül 2026): ilan
  formundan açılan kategori admin'de yalnız "Aktif" filtresiyle görülür.
- [ ] **Kategori sıralaması TR başlığa göre** (26 Eylül 2026): EN/DE listelerde
  `order_by('order','title')` Türkçe başlığa göre sıralar; `order` alanı hepsi 0.
- [ ] **İlan e-postasındaki kategori TR** (26 Eylül 2026): `views.py` ~2191
  `job.category.title` / varsayılan 'Veri Analizi'.
- [x] **Yetenek (JobCategory) başlıkları** — eski not (26 Eylül 2026): profil düzenleme
  chip'leri ve profil etiketleri DB `JobCategory.title` — EN/DE'de TR olup
  olmadığı kontrol edilecek (market ile ortak).
  **ÖLÇÜM (26 Eylül 2026):** Evet, tek dilli. Kritik bulgu: kategoriler kullanıcı
  girişiyle oluşuyor — `JobPostForm.save()` (forms.py ~168) ilan verirken yazılan
  metni `JobCategory.objects.get_or_create(title=…)` ile YENİ kategori yapıyor; bu
  kayıtlar `is_active=True` olduğu için profil düzenlemedeki yetenek listesine ve
  ilan datalist'ine de düşüyor. Gösterim yerleri: profil (2), profil düzenleme,
  uzman dizini, `_expert_showcase`, `_studyroom_founder_card`, market liste/detay,
  post_job/edit_job datalist, ilan e-postası (views ~2191, varsayılan 'Veri Analizi' TR).
  Yerel DB'de 0 kayıt → canlı liste ölçülmeden çeviri verisi yazılamaz.
  **Canlı liste ölçüldü (26 Eylül 2026): 43 kayıt, hepsi aktif, `order` hepsi 0.**
  - id 2–33 (32 kayıt) seed/küratörlü görünüyor; id 34–44 (11) ilan formundan
    kullanıcı girişiyle oluşmuş: "SPSS ve içerik analizi", "Maxquda ile 27 kişiye
    ait verinin çalışılması" (ilan başlığı kategori olmuş), "Nitel Veri Analizi",
    "Yapay zeka modelleme", "Veri etiketleme", "Python", "Python eğitimi",
    "Ai modelleme", "Yapay Zeka & ML, Python, Otomasyon", "Makale Desteği",
    "Tez danışmanlığı".
  - Yinelenenler: yapay zeka (3, 37, 41, 42), Python (39, 40, 25), nitel (36, 22, 23).
  - Yazım: "MAXQUDA"→MAXQDA (23, 35), "modlellemesi" (5), "Geçerlik" (29).
  - 11 kaydın hiç ilanı/uzmanı yok (C++, Java, Javascript, SEO, Web tasarımı…).
  Bekleyen: (1) ~~canlıdaki kategori listesi~~ ölçüldü,
  (2) karar: rozetlerdeki gibi `title_en/_de` + migration mı; kullanıcı kaynaklı
  kategoriler ne olacak (admin onayı / serbest metin kalır).
- [x] **Profil düzenleme: geçersiz telefonda çift mesaj** — DÜZELTİLDİ (26 Eylül 2026):
  diğer alanlar kaydedilir, başarı + hata yerine tek uyarı ("Diğer bilgileriniz
  kaydedildi; ancak telefon numarası … kaydedilmedi") — TR/EN/DE test edildi.
- [x] **Profil kaydı hatasında başarı mesajı** — DÜZELTİLDİ (26 Eylül 2026): `profile.save()`
  hata verirse hata mesajı + düzenleme sayfasına dönüş; `user.save()` ve yetenekler
  artık profil kaydı başarılı olunca yazılıyor (yarım kayıt yok). Teşhis logu ayrı
  try'da (log hatası kaydı başarısız saymaz). Simülasyonla TR/EN/DE test edildi.
  Kalan: LinkedIn dalı `profile.save()`'i erken çağırıyor (rozet için) — o dalda
  yarım kayıt hâlâ mümkün (düşük öncelik). Eski not:
  önceden var): `profile_edit` `profile.save()` istisnasını loglayıp yutuyor, sonra
  başarı mesajı gösteriyor (views.py ~1440). Hata mesajı gösterilmeli — karar/iş.
- [x] (eski not) **Profil düzenleme: geçersiz telefonda çift mesaj** (26 Eylül 2026, önceden
  var olan davranış): hata mesajının yanında "Profiliniz başarıyla güncellendi"
  da çıkıyor (diğer alanlar kaydediliyor). Mesaj akışı düzeltilecek mi — karar.
- [x] **Profil düzenleme JS hatası** — DÜZELTİLDİ (26 Eylül 2026, kullanıcı kararı "ölü kodu
  sil"): olmayan elemanlara bağlı "Manuel yetenek ekleme" JS bloğu + `.custom-tag` CSS
  kaldırıldı; `node --check` OK, sayfa 200. Eski not: `profile_edit.html`
  scripti olmayan `#custom-skill-input` / `#custom-skills-hidden` elemanlarını
  kullanıyor → konsolda TypeError (chip seçimi ve arama etkilenmiyor, hata
  onlardan sonra). Ölü kod silinmeli ya da manuel yetenek alanı eklenmeli — karar.
- [x] **GÜVENLİK — yetenek chip'inde innerHTML** — DÜZELTİLDİ (26 Eylül 2026): `append`
  ile metin olarak ekleniyor. Headless Chrome ile doğrulandı: eski kodda
  `<img onerror>` adlı kategori JS çalıştırdı (title değişti), yenisinde metin
  olarak göründü. Eski not: `profile_edit.html`
  `syncTags()` seçili etiketi `tag.innerHTML = chip.textContent + …` ile kuruyor;
  kategori adı kullanıcı girişiyle oluşabildiği için (`JobPostForm`) `<img onerror=…>`
  gibi bir ad seçen kullanıcının kendi sayfasında çalışır. Yeni kategoriler artık
  admin onayına düştüğü için risk düşük; yine de `textContent` + `append` ile
  düzeltilmeli (küçük iş). Canlıdaki 43 kategoride HTML karakteri yok (ölçüldü).
- [x] **Profil detay "Hesabı Sil" bloğu ax- sistemine taşındı** (26 Eylül 2026): Bootstrap
  util + `btn-outline-danger` + hardcode rgba → `profiles.css` `.ax-profile-danger-zone`
  (token'lı, mobilde alt alta / ≥576px yan yana); 375px ve 900px ekran görüntüsüyle doğrulandı.
- [x] **Profil düzenleme sayfası ax- sistemine taşındı** — KULLANICI ONAYLADI (26 Eylül 2026): `ax-form-*` + profil sekme bileşeni (vanilla JS), token'lı
  CSS `profiles.css` `.ax-profile-edit*`; mobil tek sütun / ≥768px iki sütun; chip'ler
  `<span>`; yetenek seçimi N+1 kaldırıldı (`with`); "listeden seçin" metni. POST
  tüm alanları kaydediyor (test edildi), 61/61.
- [x] **Profil sekmeleri DE'de sığmıyordu** (26 Eylül 2026, kullanıcı ekran görüntüsü):
  gizli yatay kaydırma "Vertrauen"i görünmez yapıyordu → `flex-wrap: wrap`.
- [x] **Profil "bewertung" (küçük harf) / "Assessment"** (26 Eylül 2026): profildeki
  "Değerlendirme" `context "puan ortalaması"` → Rating / Bewertung.
- [x] **proje_talebi parça birleştirmeleri** — DÜZELTİLDİ (26 Eylül 2026): aynı blokta 3 çift
  ("Tamamlanan"+"Analiz", "Kayıtlı"+"Üye", "Ön"+"Değerlendirme") tek msgid oldu; `<br>`
  kaldırıldı (dar kutu kendisi kırıyor). DE "Ücretsiz" "Kostenlose" → "Kostenlos"
  (hakkımızda karşılaştırma tablosunda dil bilgisi hatasıydı). 3 dilde 375/900px kontrol. Eski not:
  `proje_talebi.html` ~121 `{% trans "Ön" %}<br>{% trans "Değerlendirme" %}` —
  tam ifade msgid olmalı (DE "bewertung" küçük harf buradan).
- [ ] **Global legacy CSS `label`/`input` `!important`** (26 Eylül 2026): `bundle.css`
  (style.css kökenli) tüm `label`'lara neon-mavi renk, tüm `input`'lara padding/border
  `!important` basıyor — `ax-form-*` bileşenlerini eziyor. Site geneli etkiler;
  kaldırılması ayrı iş + tüm formların görsel kontrolü.
- [x] **Yerel ekran görüntüsü notu** (bilgi, iş değil): container `staticfiles` ayrı Docker volume —
  hosttaki `staticfiles/` eski; dosyadan render'da `static/` kullan.
- [x] (eski not) **Profil düzenleme sayfası ax- sistemine taşınacak** (26 Eylül 2026, sıradaki): tamamı
  Bootstrap (card, form-control, nav-tabs, form-switch) + `data-bs-toggle` sekmeler +
  hardcode renkler; önce taslak ekran görüntüsü → kullanıcı onayı.
- [x] **Yerel SQLite'ta 0156/0157** — KAPANDI (26 Eylül 2026, kullanıcı: bekleyen migration yok). Eski not: kullanıcının yerel
  runserver'ı (`db.sqlite3`) `no such column: forum_badge.name_en` ile 500 verdi —
  `python manage.py migrate forum` gerekli (0157 temizliği yerel kopyaya da uygulanır).
- [x] (eski not) **Profil şablonları ax- sistemine aykırı** (26 Eylül 2026, önceden var):
  `profile_edit.html` Bootstrap `card`/`btn`/`nav-tabs` + `data-bs-toggle`,
  hardcode renkler; `profile_detail.html` "Hesabımı Sil" `btn btn-outline-danger`.
- [ ] **Takip API hata metni tek dilli** (düşük öncelik): `api_views.toggle_follow_user`
  "Kendinizi takip edemezsiniz." — arayüzden ulaşılamıyor.
- [x] **Ana sayfa hero test çipleri** — ÇEVRİLDİ (25 Eylül 2026) "t-testi · korelasyon · regresyon"
  EN/DE'de Türkçe.
- [x] **"Güvenilir Üye" rozet mesajı** — ÇEVRİLDİ (25 Eylül 2026) (`_check_and_award_trust_badge`,
  forum/views.py ~1700) Türkçe — e-posta doğrulama sonrasında çıkabiliyor.
- [x] **AI Asistan `/istatistik/…` linkleri** — ÇÖZÜLDÜ (25 Eylül 2026):
  EN/DE'de `/istatistik/<slug>/` → `/<dil>/analiz/<slug>/` (18 slug birebir,
  hepsi 200, bilinmeyen slug 404 — doğrulandı). TR davranışı aynı.
- [x] **AI Asistan ölü/koşullu linkler** — ÇÖZÜLDÜ (25 Eylül 2026): `/makaleanaliz/` kaldırıldı (giriş sayfası yok → talimatta `/tarama/` + "tarama sonucundan başlatılır"); `_PATH_FEATURE_FLAGS` ile bayrağı kapalı sayfaların talimat satırları ve izinli linkleri istek anında çıkarılıyor. Açık tüm hedefler 3 dilde 200/302 doğrulandı. Eski not:
  `/makaleanaliz/` her ortamda 404 (izinli listede + talimatta var ama kökte
  sayfa yok); `/ai-cozumler/`, `/egitim/`, `/egitim-talebi/` feature flag
  kapalıyken 404 — talimat/izinli liste flag'e göre filtrelenmeli.
- [x] **AI Asistan kapasite** — İYİLEŞTİRİLDİ (25 Eylül 2026): talimat kural
  kaybı olmadan sıkıştırıldı; ölçülen istek başı token TR 2625→1772 (-%32), EN
  ~2994→1868 (-%38) → dakikada ~3 → ~4,5 soru (~1,5x). 5 senaryo canlı test
  (test seçimi, uzman isteği, NVivo yok, kapalı eğitim sayfası, tez yazdırma
  reddi) + EN/DE dil: OK. `reasoning_effort=low` ölçüldü (+%15) ama yanıtları
  kısalttığı için EKLENMEDİ.
- [ ] **AI Asistan — kalan kapasite sınırı:** ücretsiz katman yine site geneli
  8000 token/dk + **1000 istek/gün**. Trafik artarsa: Groq ücretli katman
  (kullanıcı kararı) ya da `reasoning_effort=low` (kalite ödünü).
- [x] ~~`manage.py test forum` 0 test buluyor~~ — ÇÖZÜLDÜ: proje pytest
  kullanıyor (`conftest.py`, `analizdestek/test_settings.py`); doğru komut
  `docker compose exec web python -m pytest forum/tests.py` (61 test).
- [x] **Başarısız test: `test_yoktez_job_daily_limit_normal_user`** — ÇÖZÜLDÜ
  (25 Eylül 2026): test eskimişti; limit fa1c281 (18 Mayıs 2026) ile bilinçli
  olarak herkese 3 yapılmış. Test 3'e güncellendi → pytest 61/61.
- [x] **Ölü kod temizliği** — TAMAMLANDI (25 Eylül 2026, kullanıcı onayı):
  forum/templates/registration/password_reset_{form,done,confirm,complete}.html
  (templates/registration gölgeliyordu — get_template ile doğrulandı),
  forum/ai_service.py (import yok), istatistik/tool_base.html (referans yok).
  Sayfalar 200, pytest 61/61. `forum/tasks.py` (Celery, bağlı değil — analizus.md
  §23) bu tura dahil edilmedi.
- [x] **Gizlilik tablosu mobilde yatay kayıyor** — ÇÖZÜLDÜ (25 Eylül 2026): mobil önce kart düzeni (data-label ile sütun adı, 3 dil), 576px+ tablo; 390/1100px ekran görüntüsüyle doğrulandı.
- [x] **Float buton çakışması** — ARTIK YOK (25 Eylül 2026 doğrulandı): kodda
  sabit (position:fixed) duran tek buton AI Asistan; WhatsApp/Destekçi sabit
  butonları kaldırılmış (sayfa içi link olarak duruyor). 390px ve 700px ekran
  görüntüsünde çakışma yok. (Alttaki "AYRI BULGU" notu tarihçe.)

**B. Kullanıcı / avukat kararı bekleyen**
- [ ] Gizlilik metnine eklenecekler: ABD aktarım güvencesi (SCC/DPF), KVKK
  md. 9 bildirimi, GA saklama süresi, AB temsilcisi (md. 27) — "Gizlilik
  metnine eklenecekler" maddesi.
- [ ] Etik Protokolü: 4. ve 7. maddeler yalnızca TCK/KVKK'ya atıf (GDPR?),
  başlık "Akademik Etik Protokolü" yeni konumlandırmayla uyumsuz.
- [ ] Avukat kontrolü (gizlilik + etik) — NOT: EN/DE 26 Eylül 2026 itibarıyla zaten yayında; kontrol yayın sonrası yapılacak.
- [x] **"Türkiye/Türkçe" vurgusu genelleştirildi** (25 Eylül 2026, kullanıcı
  onayı): ana sayfa alt başlığı + og/twitter → "Uçtan uca analiz ekosistemi…",
  AI Asistan/blog/forum/Tez Analizi açıklamaları, forum kategori açıklaması,
  AI talimatı son satırı; Hakkımızda "Türkçe Arayüz" satırı KALDIRILDI.
  Olgusal olanlar korundu (TR Dizin/YÖK/19 Türk üniversitesi, KVKK/TCK, Türkçe
  NLP dersi, transkript dil listesi, blog yazı içerikleri).
- [x] **"Tez" vurgusu genelleştirildi** (25 Eylül 2026, kullanıcı onayı, 14 madde):
  varsayılan meta + keywords, ana sayfa JSON-LD (Tez Danışmanlığı → Araştırma
  Danışmanlığı) + AI kartı, Hangi Test/AI Asistan/blog/forum/bölüm/örneklem/
  uzman dizini/başarı hikayeleri açıklamaları; forum açıklamasındaki kaçak
  "Ücretsiz, Türkçe." da düzeltildi. E-posta imzası zaten "Araştırma ve Analiz
  Platformu"ydu; doğrulama + hoş geldin e-postası altlığı "© 2024 … Akademik
  Analiz ve Veri Bilimi Forumu" → "© {yıl} … Araştırma ve Analiz Platformu".
  Korunan: öğrenci segmentine özel "Tezin için:", onboarding "Akademik Destek",
  tez araçları. JSON-LD geçerli, pytest 61/61.
- [x] **"Tez için" kalıbı** — genelleştirildi (Adım 6 altındaki maddeye bak).
- [x] **Adım 6 — TAMAMLANDI (25 Eylül 2026). KARAR: hepsi, aşamalı (ekran + PDF birlikte); PDF başlığı
  "Tezinde Nasıl Raporlarsın?" → "APA Formatında Raporlama"** (25 Eylül 2026)
  - [x] Aşama 1 altyapı: dil işçi thread'ine taşındı (`_pending_job_languages`,
    run_job yakalar, `_execute_job` translation.override) — gerçek kuyrukla
    TR/EN/DE doğrulandı; job_runner (6) + data_validator (9) mesajları EN/DE;
    Likert uyarısındaki numpy repr sızıntısı ("np.int64(9)") düzeltildi.
  - EK ÖLÇÜM: şablonlardaki JS (ekranda APA cümlesi üretimi) 46 metin / ~790
    kelime, 18 şablon — ilk ölçüm yalnız .py taradığı için eksikti; partilere dahil.
  - [x] Parti 2 (25 Eylül 2026): normallik, betimsel, cronbach, korelasyon,
    orneklem — servis (ekran+PDF) + şablon JS; APA cümleleri {süslü} yer
    tutucu ile Python/JS ORTAK msgid ({% trans %} %-işaretini kaçışladığından
    %(x)s ortak olamaz). Yan düzeltmeler: "p = < .001" → "p < .001"; Cronbach
    cümlesinde etiket aralıksız + TR'ye duyarlı küçük harf ("İyi".lower() →
    "i̇yi" sorunu); 3b-2d'den kalan kaçaklar (örneklem "Orta etki…" ×3,
    "Hesapla" butonu, cronbach "' madde'"). Doğrulama: PDF metni (pdftotext)
    EN'de TR kalıntı yok; 15 sayfa JS node --check + APA node'da üretildi.
    NOT: AST tarayıcı Türkçe harfsiz metinleri ("Yorum", "Madde", "Hesapla")
    kaçırıyor — kalan partilerde dosyalar ayrıca gözle okunmalı.
  - [x] Parti 3 (25 Eylül 2026): ttesti, anova, mann_whitney, kruskal_wallis,
    ki_kare — servis + şablon JS (ANOVA JS tablo başlıkları, Post-Hoc başlığı,
    ki-kare "Toplam" dahil); parça birleştirmeli sonuç/APA cümleleri tam cümle
    msgid'lerine bölündü; JS'te de "p < .001" (pStr). **DOĞRULUK HATASI
    DÜZELTİLDİ:** eşleştirilmiş t-testinde yön tersti (son > ilk iken "ölçüm
    azalmıştır" diyordu). Ki-kare tablosunda 'Toplam' → pgettext('tablo')
    (bağlamsız çevirisi "Total of"). EN PDF'lerde TR kalıntı yok; 15 sayfa JS OK.
  - [x] Sonuç cümlelerinde "p = 0.0000" → "p < .001" (7 servis, 18 msgid; p ifadesi
    tek parça) — 25 Eylül 2026.
  - [x] Wilcoxon yön kontrolü — hata yok (Parti 4).
  - [x] Parti 4 (25 Eylül 2026): wilcoxon, friedman, tekrarli_anova, afa —
    servis + şablon JS. Wilcoxon yönü DOĞRU (diff = col2 − col1). Düzeltilen
    önceden var hatalar: APA'da "p 0.123" (eşittir eksikti) — 4 araç, ekran+PDF;
    **AFA: Bartlett anlamsızken de "anlamlı bulunmuştur" yazıyordu** (PDF+ekran);
    faktör sayısı elle seçilince de "Özdeğer > 1 kriteri" diyordu; ekran ve PDF
    APA metinleri farklıydı → tek ortak metin (afa._apa_text + JS). Yüzde biçimi
    dile göre ('%%%(value)s' / '%{value}' msgid'leri: %62.3 / 62.3% / 62.3 %).
    Kaçaklar: wilcoxon "(Medyan)", afa "madde". EN PDF TR kalıntı yok; 12 sayfa JS OK.
  - [x] Parti 5 yüzde kalıpları düzeltildi.
  - [x] Parti 5 (25 Eylül 2026): lineer_regresyon, lojistik_regresyon,
    karar_agaci, svm — servis + şablon JS. **Tuzak düzeltildi:** JS ve PDF sabit
    terimi `c.name !== 'Sabit'` ile tanıyordu (Türkçe harfsiz olduğu için
    karşılaştırma taramasında görünmedi) → `is_const` bayrağı; ad artık
    çevriliyor (Intercept/Konstante). Önceden var: APA'da "p = < .001",
    yüzdeler karışık ("85.2%" tabloda / "%85.2" APA'da) → dile göre tek biçim
    (betimsel frekans tablosu dahil). Kaçaklar: "Kriter:", "Yaprak:", "Polinom".
  - [x] **ADIM 6 TAMAMLANDI (25 Eylül 2026):** 20 servis + 18 şablon; son tam
    taramada kalan yalnız yöntem/terim adları (Bonferroni, Pearson, Wald…),
    HTML etiketleri ve dosya yolları.
  - [x] Ekran APA başlığı → "APA Formatında Raporlama" (18 şablon) + "Tez için"
    kalıbı genelleştirildi (4 araç açıklaması, ana sayfa açıklaması + SSS sorusu,
    AI Asistan örnek sorusu, betimsel tanıtım metni) — 25 Eylül 2026. Korunan:
    eğitici metinlerdeki olgusal "tezlerde ve raporlarda", tez tarama aracı,
    öğrenci segmentine özel öneri.
  Ölçüm notu: istatistik
  servislerinde (20 dosya) çeviriye işaretlenmemiş Türkçe: EKRAN 221 metin /
  ~1380 kelime (APA cümleleri, etki yorumları, veri uyarıları, hata mesajları),
  PDF 300 metin / ~1190 kelime (başlık/tablo etiketleri). Türkçe değerle mantık
  karşılaştırması YOK (güvenli). Mimari bulgular: (1) PDF ekran metinlerini
  yeniden kullanıyor (`Paragraph(result['conclusion'])`) → yalnız ekran
  çevrilirse PDF karışık dilli olur; (2) analiz işçi thread'inde çalışıyor
  (`job_queue.enqueue`) → dil thread'e taşınmalı (aktif dil thread-local).
  PDF başlığında "Tezinde Nasıl Raporlarsın?" (tez vurgusu) var. Tarayıcı:
  scratchpad `scan_tr.py` (AST; docstring/log/gettext hariç).
- [ ] "Ufak tefek aksamalar" listesi kullanıcıdan alınacak (cilalama turu).

- [x] **GÜVENLİK — `_verify_cron_secret` beklenen anahtarı loga yazıyor** —
  DÜZELTİLDİ (25 Eylül 2026): anahtar hiç loglanmıyor (yalnızca yol + IP),
  `hmac.compare_digest`, env yoksa varsayılan anahtar yalnızca DEBUG'da
  geçerli (prod'da red + error log). pytest: 60/61 (tek hata yoktez — önceden
  bilinen). NOT: canlıdaki mevcut loglarda eski anahtar düz metin duruyor →
  anahtar yenileme maddesi hâlâ geçerli.
- [ ] **CRON_SECRET_KEY yenileme:** 25 Eylül 2026'da anahtarın TAMAMI
  nginx log çıktısıyla sohbete yapıştırıldı (yerel oturum). Ayrıca anahtar
  `?secret=` ile URL'de gittiği için nginx access loguna düz metin yazılıyor —
  yenilerken `X-Cron-Secret` header'ına geçmek de değerlendirilmeli. Yenilenirse
  `.env` + Hetzner crontab'daki TÜM `/api/cron/*` satırları birlikte güncellenmeli.

**C00000. ALTINCI MERGE — 27 Eylül 2026 (kullanıcı: "merge et")**
- [x] Ön kontrol: 61/61, makemigrations temiz, DEBUG=False collectstatic hatasız; migration YOK,
  requirements değişmedi. main ← dev fast-forward (6 commit: OpenAlex/S2 tam çeviri 4 aşama).
- [x] Hetzner deploy — YAPILDI (27 Eylül 2026, Claude; kullanıcı: "yap"): sunucu e86b17d, web restart, log temiz; canlı ölçüm: /en|de/openalex|semantic-scholar/ 200 ve görünür Türkçe metin 0 (başlıklar EN/DE); TR /openalex/ Türkçe (SEO rehberi dahil).

**C0000. BEŞİNCİ MERGE — 27 Eylül 2026 (kullanıcı: "merge edelim"; DB yedeği: "sen al")**
- [x] DB yedeği (Claude, SSH root@89.167.5.224, proje klasörü `/app`): `/root/yedek_2026-09-27_1214.sql`
  (180 MB, 80 tablo; önceki 25 Eylül yedeğiyle aynı boyut).
- [x] Ön kontrol: 61/61, makemigrations temiz, DEBUG=False collectstatic hatasız, requirements değişmedi.
- [x] main ← dev fast-forward + push (5 commit: proje talebi Aşama 1+2). Migration **0158** (dil alanı)
  + **0159** (choices, SQL no-op).
- [x] Hetzner deploy — YAPILDI (27 Eylül 2026; kod çekimi + web restart kullanıcı, doğrulama Claude): sunucu
  dae62f0, 0158/0159 [X], /, /en/, /de/, proje talebi, /de/tarama/, /market/ 200. nginx yeniden başlatılmadı
  (site sorunsuz; restart almanyalirehber'i de etkiler).
- [x] **DE hero butonu taşıyordu** — DÜZELTİLDİ VE CANLIDA (27 Eylül 2026, kullanıcı: "canlıya al"): main 101cb2f, sunucuda git pull + web restart (Claude); canlı hero.72858e6aff95.css yeni kuralı içeriyor; /, /en/, /de/, /de/proje-talebi/ 200.

**C000. DÖRDÜNCÜ MERGE (hotfix) — 27 Eylül 2026 (kullanıcı: "et")**
- [x] main ← dev fast-forward + push: **9203f3d** — STORAGES ile hash'li statik (kalıcı önbellek
  çözümü), profiles.css ?v=0200, test_settings düz storage, fotoğraf önizleme yedek baş harf.
  Migration yok. 61/61.
- [x] Hetzner deploy — YAPILDI ve doğrulandı (27 Eylül 2026): kullanıcı ekran görüntüsünde fotoğraf 72px dairede; canlı HTML'de CSS'ler hash'li (`bundle.54c75d1e42b0.css` 200), hash'siz CSS referansı yok; /, /en/, /de/tarama/, /market/, /proje-talebi/ 200. Adım notu: `git pull origin main` → `docker compose restart web && docker compose
  restart nginx` (deploy.sh collectstatic hash'li dosyaları üretir). Sonra: profil düzenleme
  sayfasında fotoğraf 72px dairede mi; sayfa kaynağında `/static/css/profiles.<hash>.css` var mı.
- Not (kullanıcı sorusu): canlıdaki devasa fotoğraf eski/yeni fotoğrafla ilgili DEĞİLDİ — eski
  profiles.css tarayıcı önbelleğinde (1y immutable) kaldığı için önizleme kuralı yoktu. Render'da
  yeni yükleme sorunsuz (kullanıcı teyidi).

**C000. 28 EYLÜL 2026 — cherry-pick ile main'e (kullanıcı: "merge et" / "al"; bibliometri bilerek dışarıda)**
- [x] bd7f8ea e-posta dili: `PreferredLanguageMiddleware` çok dilli sayfanın öneksiz TR sürümünde (GET,
  `/en`+yol çözülüyorsa) tercihi `tr`'ye döndürür. Bulgu: /de/ ziyaretinden sonra TR sitede istenen bağış
  e-postası Almanca geliyordu. Yalnız TR sayfalar (forum, blog) tercihi değiştirmez (bilinçli).
- [x] 1fb9fe7 `Notification` `content_type`/`object_id` NOT NULL: `mark_donation_transferred` (`target=None`
  → 500) ve `_notify_referral_reward` (hedefsiz → sessizce yutuluyordu) düzeltildi; `Donation.get_absolute_url`
  (admin bağış sayfası), `ReferralUse.get_absolute_url` (/davet/). Davet akışı uçtan uca test edildi.
- [x] cd68fa1 navbar: mobilde hamburger ekran dışına taşıyordu (giriş yapınca 430 px gerekiyordu). Logo yazısı
  <480px 2xl, ≥480px 4xl; dar ekranda gap küçük; <360px yalnız logo görseli. 320–1024 px ölçüldü.
- [x] Hetzner deploy (kullanıcı yaptı, 28 Eylül 2026); canlı bundle.css'te yeni kural doğrulandı.

**C00. ÜÇÜNCÜ MERGE — 27 Eylül 2026 (kullanıcı: "sorun yoksa merge edelim")**
- [x] Ön kontrol: 61/61, makemigrations temiz, migration YOK, requirements değişmedi, main'de dev'de olmayan commit yok.
- [x] main ← dev fast-forward + push (8 commit: JSON-LD, tarama hub EN/DE, set_language, proje talebi TR ifadeler, profil fotoğrafı).
- [x] Hetzner deploy — YAPILDI (sonraki merge'lerle birlikte canlıda doğrulandı).

**C0. İKİNCİ MERGE — 26 Eylül 2026 (kullanıcı: "merge edelim, sorun yoksa")**
- [x] Ön kontrol: çalışma ağacı temiz, 61/61 pytest, `makemigrations --check` temiz,
  `check --deploy` (DEBUG=False) yalnız W009 (yerel test anahtarı), main'de dev'de olmayan commit yok.
- [x] main ← dev fast-forward + push: **c2b3aec** (30 commit). requirements.txt DEĞİŞMEDİ → build yok.
- [x] **Hetzner deploy** — YAPILDI (27 Eylül 2026 dışarıdan doğrulandı: EN/DE'de "Academic Search" menüsü var, Topluluk yok; TR'de Topluluk var; transcript linki yok). Eski adım notu: ÖNCE DB yedeği (0157 veri adımı geri alınamaz) →
  `git pull origin main` → `docker compose restart web && docker compose restart nginx`
  (deploy.sh açılışta migrate + collectstatic) → `showmigrations forum | tail -3` ile 0156/0157 [X].
- [x] Deploy sonrası doğrulama (dışarıdan, 27 Eylül 2026): /, /en/, /de/ 200; market EN/DE kategori çipleri çevrili ("AI Modelling", "Thesis Consulting"…), TR'de 0157 yeniden adlandırma ve birleştirme görünüyor ("Yapay zekâ modelleme"). Sayı kontrolü (37/32) DB erişimi gerektirir — yapılmadı. Plan notu: kategori sayısı 37 / aktif 32; /en/ /de/ 200; /en/tarama/ yok;
  TR'de /tarama/ → EN seçince /en/'e gider; profil düzenleme sayfası yeni tasarım.

**C. Canlıya alma (yalnızca kullanıcı "merge et" deyince)** — 25 Eylül 2026 ölçümü:
dev, main'den 78 commit ileride, main'de dev'de olmayan commit yok (fast-forward);
requirements.txt değişmedi (--build GEREKMEZ); settings.py: 3 middleware +
hreflang context processor + 'de' dili; .mo dosyaları git'te (compilemessages
şart değil); container başlarken deploy.sh migrate + collectstatic çalıştırır
(yine de elle çalıştırıp çıktıyı görmek önerilir). Staging (analizus-dev.onrender.com)
en son dev'i çalıştırıyor, 200.
**Gerekli migration'lar: forum 0153 (SiteSettings.feature_multilingual, şema),
0154 (Profile.preferred_language, şema, varsayılan 'tr' — mevcut kullanıcılar
TR), 0155 (anonim kullanıcı adları, veri, geri alınabilir).** Başka uygulamada yok.
- [x] 0. Canlı DB yedeği (kullanıcı aldı, 25 Eylül 2026): `docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > /root/yedek_$(date +%F).sql`
- [x] 1. main ← dev fast-forward merge + push (132327f, 25 Eylül 2026)
- [x] 2. Hetzner: git pull
- [x] 3-4. migrate + collectstatic — container yeniden başlarken deploy.sh uyguladı (0153-0155 applied 2026-09-25 21:07 UTC; 0152 23 Temmuz → staging canlı DB'yi kullanmıyor, doğrulandı)
- [x] 5. web + nginx yeniden başlatıldı
- [x] 6. Kontroller (curl): tüm sayfalar 200, /en/ 404 (bayrak kapalı), inter.css + font 200, log temiz; canlı HTML: yeni og açıklaması, Yandex yok, Google Fonts yok, GDPR bölümü var. Tarayıcıda AI Asistan testi kullanıcıda. Eski not: ana sayfa/giriş/araç sayfası 200; çerez banner'ı (GA ID varsa);
      AI Asistan bir soru; `showmigrations` hepsi [X]; nginx/web log hata yok.
- [x] 7. `feature_multilingual` — AÇIK, EN/DE YAYINDA (kullanıcı teyidi 26 Eylül 2026). Avukat maddeleri B bölümünde ayrıca açık.
- [ ] **Canlıda `GOOGLE_ANALYTICS_ID` TANIMLI DEĞİL** (25 Eylül 2026, canlı HTML'de GA script/banner yok; deploy öncesi de yoktu) → sitede hiç analiz aracı çalışmıyor. İstenirse .env'e eklenir, banner otomatik devreye girer. Eski not: Canlıda kontrol: `GOOGLE_ANALYTICS_ID` tanımlı mı (banner ona bağlı);
  canlı `GROQ_API_KEY` ile gpt-oss-120b yanıt veriyor mu.
- [ ] Yandex Metrica hesabı/sayacı kapatılabilir (kod kaldırıldı).
- [ ] **Deploy sonrası (bayrak kapalı) — arama/analitik panelleri:**
  Google Search Console: sitemap.xml yeniden gönder; ana sayfa + gizlilik için
  URL denetimi → dizine eklenmeyi iste; 1-2 hafta "Sayfalar" raporunda 404/5xx
  artışı izle. GA4: Yönetici → Veri ayarları → Veri saklama süresini kontrol et
  (2/14 ay → gizlilik metnine yazılacak), Google sinyalleri kapalı mı; onay
  banner'ı nedeniyle trafik düşüşünü açıklama (annotation) olarak not et.
  Bing Webmaster Tools: site doğrulandı mı (BING_SITE_VERIFICATION ya da GSC'den
  içe aktar), sitemap gönder. Canlı .env'de GOOGLE/BING_SITE_VERIFICATION dolu mu.
- [ ] **feature_multilingual açıldıktan sonra:** GSC + Bing'e sitemap'i yeniden
  gönder (artık /en/ /de/ + hreflang içerir); /en/ ve /de/ ana sayfa + birkaç
  araç sayfası için URL denetimi → dizine eklenmeyi iste; oluşturulan HTML'de
  hreflang ve <html lang> doğrula (GSC'de ayrı hreflang raporu yok).
- [ ] 8. `feature_agentic_landing` flag'i merge sonrası elle açılmalı (önceki
  turdan hatırlatma).


**Tamamlanan:** Adım 1 (ayarlar), 2 (URL yapısı + 3 kritik bug), 3a
(base+footer), 3b-1 (register+login), 3b-2a (home.html), 3b-2b
(makaleanaliz/openalex/semanticscholar), 3b-2c (proje talebi/AI
çözümler/eğitim), 4 — ilk çeviri turu (601 metin), 5a (dil seçici +
admin flag), Market arayüzü (commit `52bd6dc`, 176 metin daha — bkz.
"Kapsam Kararı"). Detaylar aşağıdaki ilgili maddelerde.

**3b-2d TAMAMLANDI (23 Eylül 2026):** `/analiz/` hub + 18 araç şablonu +
landing view metinleri + yükleme/önizleme hata mesajları (commit'ler
`ddff5d4`, `e363169`). `tool_base.html` ölü dosya (hiçbir yerden
kullanılmıyor). Kullanıcı kararıyla APA cümleleri + sunucu sonuç
metinleri Türkçe bırakıldı (Adım 6'da PDF ile birlikte).

**23 Eylül 2026 devamı — TAMAMLANDI:** base.html kalıntıları (skip-link,
quiz/profil/hikaye modalları, AI widget), DE terim birliği (Ausschreibung →
Auftrag), `seo_content.py` rehberi (18 araç, 176 metin), footer "Bize Destek
Ol" + bağış modalı (paket adları `gettext_noop` ile), footer alt satırı
"Araştırma ve Analiz Platformu", yeni slogan "Veriden karara…".
EN/DE araç sayfalarında kalan Türkçe: yalnızca yasal adres satırı (kasıtlı).

**24 Eylül 2026 — TAMAMLANDI (kullanıcı isteği: eğitim kataloğu, kayıt/giriş, e-postalar):**
- Eğitim kataloğu (`training_catalog.py`, 362 metin) — `56c597f`
- Kayıt formu hataları + kayıt mesajları — `9bfad5d` (giriş formu hataları
  Django kataloğundan zaten çevrili)
- E-postalar (alıcının dilinde): E1 `Profile.preferred_language` +
  middleware + `forum/i18n_utils.py` (`91154b0`) → E2 hesap e-postaları →
  E3 kullanıcı bildirimleri (admin bildirimleri TR sabit) → E4 Makale
  Analiz/OpenAlex/Semantic Scholar sonuç e-postaları → E5 destek/eğitim/
  proje talebi onayları (`0cc2b4d`).
  ⚠ **Canlıya alırken MIGRATION 0154 zorunlu:** `docker compose exec web
  python manage.py migrate` — mevcut tüm kullanıcılar 'tr' etiketlenir.
  Kasıtlı TR kalan: yoktez/trdizin/tezanaliz/bibliometrics e-postaları,
  TXT/PDF sonuç dosyası içerikleri (Adım 6), havale açıklaması.

**Menüden erişilen tek dilli sayfalar (kullanıcı isteği, 24 Eylül 2026):**
Hiçbiri i18n_patterns'te değil ve şablonları işaretlenmemiş — her biri için
URL taşıma + şablon + sitemap(static-i18n) + robots.txt.
- [x] Hakkımızda (+ "Neden Analizus?") — TR metin güncellendi (11 madde,
  kullanıcı onayı) + EN/DE — `fc543cc`
- [x] İletişim — form + flash mesajları EN/DE — `fc543cc`
- [x] Hangi Test? — karar ağacı (233 metin) + SSS JSON-LD + araç linkleri
  dile duyarlı. Açık soru: meta açıklama "Tezin için…" (tez vurgusu) TR'de
  aynen bırakıldı
- [x] **AI Asistan** — TAMAMLANDI (24 Eylül 2026): `ai-asistan/` sayfası
  urls_i18n'e taşındı (API `/api/ai/chat/` öneksiz kaldı — doğrulanmamış
  kullanıcı `/api/` muafiyeti), sayfa + limit/hata mesajları EN/DE. Widget
  `lang` gönderiyor (tr/en/de dışı → tr). EN/DE'de sistem talimatının başına
  ve sonuna dil kuralı ekleniyor (TR talimatı birebir aynı). Yanıttaki
  platform linkleri `translate_url` ile dil önekini alıyor (/en/hangi-test/);
  tek dilli sayfalar (/istatistik/…, /forum/) öneksiz kalıyor. Gerçek API
  testi (gpt-oss-120b ile, betikte geçici): EN/DE yanıtlar tamamen hedef
  dilde. İlk denemede DE gövde Türkçe kalmıştı → dil kuralı başa da eklendi.
  Açık soru: TR meta açıklama "anında Türkçe yanıt… tez yazımı" (EN/DE'de
  "Türkçe" düşürülerek çevrildi).
- [x] **ACİL — AI Asistan hiç yanıt vermiyor** — ÇÖZÜLDÜ (24 Eylül 2026): kullanıcı kararı "ücretsiz en yüksek limitli model" → ölçüldü (API yanıt başlıkları): gpt-oss-120b = gpt-oss-20b (8000 TPM, 1000 RPD, 131K bağlam) > qwen3.8-27b (16K çıktı) > allam-2-7b (4K bağlam); `openai/gpt-oss-120b` seçildi, uçtan uca test OK. Eski not:
  Groq `llama-3.3-70b-versatile` modelini artık tanımıyor (404, 24 Eylül
  2026). Hesapta erişilebilen: openai/gpt-oss-120b, openai/gpt-oss-20b,
  qwen/qwen3.8-27b… Model seçimi kullanıcı kararı. Not: gpt-oss-120b
  ücretsiz katmanda 8000 token/dk limitine takılıyor (istek başına ~2900
  token: talimat + 1024 yanıt payı → dakikada ~2-3 soru).
- [x] **A. Çerez onayı + Yandex kaldırma** — TAMAMLANDI (24 Eylül 2026,
  kullanıcı kararı: Yandex kaldır). `partials/cookie_consent.html`: Reddet /
  Kabul et (eşit boyut), `ax_cookie_consent` çerezi 180 gün; GA yalnızca
  onayla yüklenir (`axLoadAnalytics`), onay geri çekilince _ga* silinir;
  eski `_ym_*` çerezleri temizlenir; footer'da "Çerez ayarları". GA ID
  yoksa banner/bağlantı hiç çıkmaz. `yandex-verification` meta etiketi
  (yalnızca Webmaster sahiplik doğrulaması, veri göndermez) bırakıldı.
- [x] **B. Google Fonts self-host** — TAMAMLANDI (24 Eylül 2026): Inter
  değişken font (latin + latin-ext, Google Fonts v20) `static/fonts/inter/`
  + OFL.txt, `static/css/inter.css`; base.html ve admin_theme_v2.css artık
  yerelden yüklüyor, gstatic preconnect / googleapis dns-prefetch kaldırıldı.
  Net-log ile doğrulandı: sayfadan fonts.googleapis/gstatic isteği yok.
  Deploy'da `collectstatic` şart (yeni statik dosyalar).
- [x] ~~ÖNEMLİ — Hesap silme vaadi uygulanmıyor~~ — YANLIŞ BULGU (25 Eylül 2026 düzeltildi): cron mevcut ve çalışıyor; bkz. AÇIK İŞLER'deki "Hesap silme cron'u kullanıcı kararlarına uydurulacak".
- [x] **Küçük i18n kaçağı (B sırasında görüldü)** — ÇEVRİLDİ (88c10d5): ana sayfa hero'sundaki test
  çipleri "t-testi · korelasyon · regresyon" EN/DE'de Türkçe kalıyor.
- [x] **C. Gizlilik sayfası: KVKK çevirisi + GDPR bölümü** — TAMAMLANDI
  (24 Eylül 2026, kullanıcı onayı): TR metni güncellendi (tablo: AI soruları,
  talep formları, zorunlu/analiz çerezi ayrımı; alıcılar adıyla; çerez
  bölümü banner'a göre; yeni 7. GDPR bölümü; sabit tarih 24.09.2026), EN/DE
  çevrildi, URL i18n'e + StaticI18nSitemap'e taşındı. [KARAR] cümleleri ve
  "30 gün içinde silinir" BİLEREK çıkarıldı — aşağıdaki maddeye bak.
- [ ] **Gizlilik metnine eklenecekler — karar/uygulama bekliyor:**
  - **"Hesap silme talebinden sonra 30 gün içinde silinir"** — işlev zaten
    çalışıyor (24 Eylül bulgusu yanlıştı); cron kullanıcı kararlarına
    uydurulunca GDPR "Saklama süreleri" maddesine geri eklenir.
  - **AB dışı aktarım güvencesi** (Google, Groq → ABD): SCC ve/veya AB-ABD
    Veri Gizliliği Çerçevesi — sağlayıcı sözleşmeleri kontrol edilmeli.
  - **KVKK md. 9 yurt dışı aktarım** (2024 değişikliği): standart sözleşme +
    KVK Kurumu'na bildirim yapıldıysa bölüm 3'e cümle eklenir.
  - **Google Analytics saklama süresi** (GA hesabındaki ayar: 2 / 14 ay).
  - **AB temsilcisi (GDPR md. 27)** — avukat görüşü.
  - Avukat kontrolü EN/DE canlıya açılmadan önce önerildi.
  Olgular: Olgular: Hetzner (DE), AWS S3
  eu-north-1 (SE), Groq (ABD, AI soruları), Google Analytics (ABD, onaylı),
  e-posta Gmail üzerinden (Google, ABD; alan adı hosting.com.tr), Render
  yalnızca test verisi (metne girmez). "Son güncelleme" `{% now %}` → sabit
  tarih. Açık: AB temsilcisi (GDPR md. 27), somut saklama süreleri.
- [x] **Gizlilik/KVKK** — çevrildi (C paketi, 3f648ee) (`gizlilik_politikasi.html`) — hukuki metin;
  çeviri kullanıcı onayıyla yayına girer (etik protokol modalıyla aynı tur)

**Kayıt akışı — yapılacaklar (kullanıcı isteği, 23 Eylül 2026):**
- [x] **Giriş/kayıt sayfasında dil seçici yok** (kullanıcı raporu, 24 Eylül
  2026) — TAMAMLANDI: `templates/partials/auth_lang_switcher.html` (set_language
  formu, `features.multilingual` kapalıysa gizli) iki sayfanın `.top-bar`'ına
  eklendi. Mobilde top-bar akışa alındı (`position: static`) ve form
  `margin-block: auto` ile ortalandı — uzun kayıt formunda üst kısım artık
  kırpılmıyor.
- [x] **Kullanım Şartları / Akademik Etik Protokolü modalı** — TAMAMLANDI
  (24 Eylül 2026): 7 maddelik gövde `blocktrans trimmed` ile işaretlendi,
  EN/DE çeviri kullanıcı onayıyla ("devam") yayına alındı. Açık kalan
  (hukuki karar, çeviri değil): 4. ve 7. maddeler yalnızca TCK/KVKK'ya atıf
  yapıyor — AB kullanıcıları için DSGVO/GDPR atfı eklenip eklenmeyeceği;
  modal başlığı "Akademik Etik Protokolü" yeni konumlandırmayla uyumsuz;
  yayın öncesi avukat kontrolü önerildi.
- [x] **Kayıt sonrası akış tek dilli** — TAMAMLANDI (24 Eylül 2026):
  verify-email, verification-pending, resend-verification, onboarding
  (forum/urls.py → urls_i18n.py) ve 4 şifre sıfırlama URL'i i18n_patterns'e
  alındı (TR adresleri değişmedi, eski linkler çalışır). Şablonlar, view
  mesajları, SEGMENT_CHOICES (gettext_lazy — migration YOK, `makemigrations
  --check` doğrulandı) ve middleware doğrulama uyarısı EN/DE. Şifre sıfırlama
  sayfalarına dil seçici + dinamik `<html lang>` + login'deki mobil düzeltme.
  Doğrulama e-postasındaki link artık alıcının dil önekiyle (`reverse()` +
  `recipient_language`). robots.txt: /en|de/accounts/, /en|de/onboarding/.
  Not: `forum/templates/registration/password_reset_*.html` kopyaları
  `templates/registration/` tarafından gölgeleniyor (ölü kod, dokunulmadı);
  `_check_and_award_trust_badge` mesajı hâlâ Türkçe (nadir, kapsam dışı).

**Not (kullanıcıya sorulacak):** ana sayfa og/twitter açıklaması hâlâ
"Türkiye'nin analiz ekosistemi…" diyor — yeni sloganla aynı konumlandırma
sorunu (yalnızca Türkiye vurgusu); değiştirilsin mi?

**Sonra:** 6 (Python tarafı — kapsam kararı bekliyor), 7 (deploy).

**Sona bırakılan (kullanıcı kararı, 22 Eylül 2026):** "Ufak tefek
aksamalar" — somut liste henüz çıkarılmadı; 3b-2d/4 bittikten sonra
kullanıcıya "hangi ufak aksamalar" diye sorulacak, ayrı cilalama turu.

**Açık kapsam kararı bekliyor:** Adım 6 (Python tarafı metinler —
istatistik hata mesajları, PDF rapor içerikleri, SEO_GUIDES,
training_catalog, TOOL_CATEGORIES, quiz bankası).

**Her makemessages sonrası hatırlatma:** fuzzy girişleri temizle
(compilemessages fuzzy'leri sessizce atlar); aynı msgid'in hem tekil hem
çoğul kullanımı xgettext uyarısı verir — farklı değişken adı
(`counter`) ile ayrıştır.

---

## Kapsam Kararı

**Dahil (EN + DE çevrilecek):**
- Ana sayfa, navbar, footer, kayıt/giriş akışı
- Makale Analiz (`makaleanaliz/`), OpenAlex (`openalex/`), Semantic
  Scholar (`semanticscholar/`) — uluslararası kaynaklar, Türkiye'ye özgü değil
- 18 istatistik aracının açıklama/giriş sayfaları (evrensel yöntemler):
  ttesti, anova, mann_whitney, kruskal_wallis, ki_kare, korelasyon,
  cronbach, normallik, betimsel, orneklem, lineer_regresyon,
  lojistik_regresyon, friedman, tekrarli_anova, karar_agaci, svm, afa,
  wilcoxon

**Kapsam dışı (Türkiye'ye özgü / UGC / karar bekliyor):**
- YÖK Tez (`yoktez/`), TR Dizin (`trdizin/`), Tez Analiz (`tezanaliz/`)
  — YÖK Tez tabanlı, Türkiye'ye özgü
- OAI-PMH (`oaipmh/`) — 17 aktif arşivin hepsi Türk üniversitesi
- Forum — UGC, Türkçe topluluk
- ~~Market/iş ilanları~~ → **YALNIZCA ARAYÜZ DAHİL edildi** (23 Eylül 2026
  kullanıcı kararı): `market/*` URL'leri `forum/urls_i18n.py`'ye taşındı;
  şablonlar + pazar view'larındaki flash mesajları + ilan/teklif form
  etiketleri çevrildi. Çevrilmeyen (kasıtlı): ilan/teklif içerikleri (UGC),
  ₺ fiyatlar, `promote_job_iban.html` (TL/IBAN ödeme akışı), otomatik
  DM/bildirim metinleri (alıcının dil tercihi bilinmiyor). Ayrıca çevrildi:
  `forum/models.py` → `FreelanceJob`/`JobProposal` durum etiketleri
  (`gettext_lazy`, migration gerekmedi — `makemigrations --check` temiz) ve
  `Profile.can_post_job*/can_propose()` sebep metinleri. Rütbe adları
  (`get_rank_display`, ör. "Çaylak") ve rozet adları (DB) Türkçe kalıyor.
- Blog — mevcut içerik Türkiye SEO'suna göre üretilmiş
- ~~Proje talebi / Danışmanlık / Eğitim landing sayfaları~~ → **DAHİL edildi**
  (22 Eylül 2026 kullanıcı kararı), aşağıdaki dosya listesine eklendi

## Uygulama Adımları (sırayla, her adım sonrası onay bekle)

- [x] **1. Ayarlar:** `analizdestek/settings.py` → `LANGUAGES` listesine
  `('de', _('German'))` eklendi (22 Eylül 2026)
- [x] **2. URL yapısı:** TAMAMLANDI (22 Eylül 2026). `analizdestek/urls.py`
  → `i18n_patterns(..., prefix_default_language=False)` ile sarıldı:
  `forum.urls_i18n` (yeni dosya — home/register/proje-talebi/ai-cozumler/
  egitim*), `makaleanaliz.urls`, `openalex.urls`, `semanticscholar.urls`,
  `istatistik.urls_analiz`. Kapsam dışı app'ler (yoktez, trdizin, tezanaliz,
  oaipmh, bibliometrics, transcript, istatistik.urls legacy polling, tarama,
  forum.urls geri kalanı, admin, sitemap, robots.txt) prefix dışında kaldı.
  - `forum/urls.py` → 7 path (`home`, `register`, `proje_talebi`,
    `ai_cozumler`, `egitim`, `egitim_talebi`, `egitim_detay`) yeni
    `forum/urls_i18n.py`'ye taşındı.
  - **Bulunup düzeltilen regresyon:** `login` adı hem `django.contrib.auth.urls`
    (dahili) hem `custom_login`'de (rate-limited) kullanılıyor —
    `reverse()` aynı isimde son kayıt edileni döndürüyor. `login`'i
    i18n_patterns'e alınca dahili view kazanmaya başladı. Düzeltme: `login`
    orijinal konumunda (accounts/ include'undan SONRA), prefix'siz bırakıldı
    — çeviri için soruna yol açmaz, `LocaleMiddleware` prefix'siz sayfalarda
    da dil çerezine bakar.
  - **Bulunup düzeltilen 3 sabit-kodlanmış link** (i18n_patterns'e alınan
    URL'lere `{% url %}` yerine `/analiz/` veya `/register/` hardcode
    edilmişti — EN/DE sayfalarda tıklanınca kullanıcıyı sessizce Türkçe'ye
    geri atıyordu): `templates/base.html` (2× navbar `/analiz/` linki + 1×
    quiz "Üye ol" linki), `istatistik/templates/istatistik/
    analiz_console_base.html` ("İlgili Araçlar" linki).
  - **Ertelenen (düşük risk, AJAX/JSON, görünür metin değil):**
    `fetch('/analiz/clear-session/')`, `makaleanaliz/results.html`
    `STATUS_URL`, `openalex`/`semanticscholar` landing'lerindeki
    `/status/` polling fetch'leri — hardcoded kalsa da sadece job durumu
    döndürüyor, dil karışıklığı görünür değil. İstenirse adım 6'da ele alınır.
  - **Doğrulama:** `manage.py check` temiz; `reverse()` ile tr/en/de için
    `home`/`login`/`analiz_home`/`register`/`proje_talebi` test edildi;
    local runserver ile `/`, `/en/`, `/de/`, `/analiz/`, `/en/analiz/ttesti/`,
    `/de/openalex/`, `/de/semantic-scholar/`, `/login/`, `/forum/`,
    `/yoktez/`, `/istatistik/ttesti/` (301→/analiz/ttesti/, değişmedi)
    curl ile 200/301 olarak doğrulandı; ana sayfa HTML çıktısında `/en/`
    için navbar linklerinin doğru prefix aldığı görüldü.
- [x] **3a. `templates/base.html` + `templates/partials/footer.html`:**
  TAMAMLANDI (22 Eylül 2026). Navbar (desktop dropdown'lar, mobil drawer,
  auth butonları, hamburger/close/arama/dil-seç aria-label'ları), `<title>`/
  meta description varsayılanları, footer (marka tagline, Araçlar/Topluluk/
  Kurumsal kolonları, alt satır copyright+link) `{% trans %}` ile işaretlendi.
  **Kasıtlı olarak İŞARETLENMEDİ:** "Forum"/"Blog" (dilller arası aynı
  kelime), footer "Akademik Kaynaklar" kolonu (Google Scholar/DergiPark/
  Semantic Scholar/YÖK Tez Merkezi — marka isimleri), footer "Bize Destek
  Ol" + bağış modalı (TL/IBAN havale bazlı ödeme — kapsam dışı, proje
  kuralı: ödeme sistemi belirsiz, sormadan genişletme), fiziksel adres,
  ana sayfadaki quiz limit-aşımı JS metni (İstatistik Arena/quiz soru
  içeriği zaten Türkçe kalacak, forum-bitişik özellik).
  Doğrulama: `manage.py check` temiz, local Docker'da restart+curl ile
  sayfa 200 dönüyor, `{% trans %}` sarılan metinler `.po` derlenmediği için
  (beklendiği gibi) hâlâ Türkçe kaynak metin olarak görünüyor.
- [x] **3b-1. `templates/forum/register.html` + `forum/templates/registration/login.html`:**
  TAMAMLANDI (22 Eylül 2026). İkisi de `base.html`'i extend ETMEYEN bağımsız
  sayfalar (özel split-screen tasarım) — `{% load i18n %}` eklendi,
  `<html lang="tr">` → `<html lang="{{ LANGUAGE_CODE }}">`, form label/hint/
  buton metinleri `{% trans %}` ile işaretlendi. **Kasıtlı işaretlenmedi:**
  register.html'deki "Akademik Etik Protokolü" modalının 7 paragraflık
  metni — KVKK ve Türk Ceza Kanunu'na doğrudan atıf yapıyor, EN/DE
  kullanıcılar için hukuken anlamsız/yanıltıcı olur; ayrı bir hukuki karar
  gerektirir (GDPR'a uyarlanmış ayrı metin mi, yoksa sadece Türkçe mi
  kalacak — henüz karar yok).
  Doğrulama: `manage.py check` temiz, `/login/` ve `/register/` 200,
  `/en/login/` 404 (beklenen — login kasıtlı olarak i18n_patterns dışında,
  bkz. yukarıdaki bug notu).
- [x] **3b-2a. `forum/templates/forum/home.html`:** TAMAMLANDI (23 Eylül
  2026). **Karar değişikliği (kullanıcı):** ana sayfanın büyük kısmının
  Pazaryeri/Uzman/Quiz içeriği olduğu keşfedildi (kapsam dışı diye
  kararlaştırılan Market özelliği doğrudan ana sayfaya gömülü) — kullanıcı
  "tüm sayfayı çevir" dedi, tutarlılık için TÜMÜ işaretlendi (navbar'da
  uygulanan aynı mantık: hedef sayfa çevrili olmasa bile UI metni çevrilir).
  İşaretlenen bölümler: title/meta, hero, pazar yeri yönlendirme (2 kart),
  nasıl çalışıyoruz (4 adım), istatistik şeridi, güven unsurları, uzman
  vitrini + iş ilanı kartları (statik chrome; `job.title`/`job.description`
  DB içeriği olduğu için dokunulmadı), araştırma konsolu, AI Asistan+Arena
  (statik chrome; quiz soru bankası DB içeriği hâlâ Türkçe), AI çağı bandı,
  SSS (5 soru-cevap), haberler bölümü (statik chrome; blog post içeriği
  dokunulmadı), hero dropzone + quiz JS'teki statik metinler.
  **Kasıtlı atlanan:** JSON-LD structured data (4 `<script type="application/
  ld+json">` bloğu — SEO metadata, ayrı küçük bir iş olarak bırakıldı),
  "Gündemdeki Tartışmalar" include'u (`_gundem_tartismalar.html` — forum
  konuları, dinamik DB içeriği), `q.difficulty` JS karşılaştırma mantığı
  ('Kolay'/'Zor' — CSS class routing için backend-bağımlı, çevrilirse mantık
  bozulur).
  Doğrulama: `manage.py check` temiz, sayfa 200 dönüyor, kalan düz Türkçe
  metin taraması yalnızca marka isimleri (TR Dizin, Cronbach, OpenAlex)
  buldu.
- [x] **3b-2b. `makaleanaliz/results.html` + `openalex/landing.html` +
  `semanticscholar/landing.html`:** TAMAMLANDI (23 Eylül 2026).
  **`order.html` (her iki app'te) KASITLI ATLANDI** — TL fiyatlı sipariş/
  ödeme akışı (IBAN havale benzeri), footer bağış modalıyla aynı kapsam
  dışı kategori (proje kuralı: ödeme sistemi belirsiz, sormadan genişletme).
  Doğrulama: `manage.py check` temiz, `/openalex/` ve `/semantic-scholar/`
  200, kalan Türkçe metin taraması yalnızca CSS `font-family` değeri buldu.
- [x] **3b-2c. `proje_talebi.html` + `ai_cozumler.html` + `egitim.html` +
  `egitim_detay.html` + `egitim_talebi.html`:** TAMAMLANDI (23 Eylül 2026).
  Title/meta blokları, form alanları (label/placeholder/option), SSS
  akordeonları, zaman çizelgeleri, kart metinleri işaretlendi.
  **Kasıtlı atlanan:** `item.title`/`item.summary`/`item.audience`/
  `item.syllabus`/`item.faq` gibi `training_catalog.py`'den (Python) gelen
  DİNAMİK kurs verileri — bunlar adım 6'nın (Python tarafı metinler)
  kapsamına giriyor, şablon seviyesinde çevrilemez. JSON-LD blokları da
  (home.html'deki gibi) kasıtlı atlandı.
  **Bulunup düzeltilen 2. tür hata:** `{% blocktrans %}` içine `{% url %}`/
  `{% if %}` gibi iç içe template tag koymak `TemplateSyntaxError` verir
  (Django blocktrans yalnızca basit `{{ değişken }}` enterpolasyonuna izin
  verir). İki yerde bu hata yapılmıştı (egitim.html, egitim_talebi.html) —
  fark edilip URL'yi `{% url ... as x %}` ile önceden hesaplayıp
  `{{ x }}` olarak geçirme veya cümleyi ayrı `{% trans %}` parçalarına
  bölme yöntemiyle düzeltildi. Tüm dosyalar bu kalıp için ayrıca tarandı,
  başka örnek çıkmadı.
  Doğrulama: `manage.py check` temiz; flag'ler geçici açılıp (sonra
  kapatılıp) `/egitim/`, `/ai-cozumler/`, `/egitim-talebi/`,
  `/egitim/spss-uygulamali/` gerçek render ile 200 test edildi; kalan
  Türkçe metin taraması temiz.
- [ ] **3b-2d. Kalan dosyalar** (18 istatistik şablonu):
  - `istatistik/templates/istatistik/{afa,anova,betimsel,cronbach,
    friedman,karar_agaci,ki_kare,korelasyon,kruskal_wallis,
    lineer_regresyon,lojistik_regresyon,mann_whitney,normallik,
    orneklem,svm,tekrarli_anova,ttesti,wilcoxon}.html`
    (+ ortak `analiz_console_base.html`/`tool_base.html` iskelet metinleri)
- [ ] **4. Çeviri dosyaları:** `django-admin makemessages -l en -l de`
  (mevcut `locale/en/` var, `locale/de/` yeni oluşacak) → `.po` doldur →
  `compilemessages`
- [x] **5a. Navbar dil seçici + dinamik `<html lang>`:** TAMAMLANDI
  (22 Eylül 2026, kullanıcı isteğiyle sıra dışı erken yapıldı — adım 3'ten
  önce test kolaylığı için). `templates/base.html`: desktop navbar'da globe
  ikonlu dropdown + mobil drawer'da TR/EN/DE buton satırı, ikisi de
  `{% get_language_info_list %}` ile `django.conf.urls.i18n`'in `set_language`
  view'ına POST eden mini formlar (`next` = `request.get_full_path`, Django
  `translate_url()` otomatik doğru dil prefix'ine çeviriyor — ayrıca kod
  yazmaya gerek yok). `<html lang="tr">` → `<html lang="{{ LANGUAGE_CODE }}">`.
  - **Kritik tuzak bulundu:** `static/css/navbar.css` **ölü dosya** —
    `base.html` yalnızca `static/css/bundle.css`'i yüklüyor (temmuz 2026'da
    5 kaynak dosya birleştirilip minify edildi, bkz. analizus.md §26).
    CSS eklerken doğru akış izlendi: `navbar.css`'e yeni kurallar eklendi →
    `rcssmin` ile `bundle.css` container içinde yeniden üretildi → `?v=0004`
    → `?v=0005`.
  - **Doğrulama (lokal Docker):** `manage.py check` temiz, `collectstatic`
    ile `staticfiles_data` volume güncellendi, `web`+`nginx` restart edildi,
    curl ile `/`, `/en/`, `/de/` üzerinde dropdown markup + `<html lang>`
    doğru görüldü, `/i18n/setlang/`'e gerçek POST ile `next=/analiz/ttesti/`
    + `language=de` gönderildi → `Location: /de/analiz/ttesti/` +
    `Set-Cookie: django_language=de` doğrulandı (Django'nun `translate_url()`
    mekanizması sorunsuz çalışıyor).
  - **5a-devam (aynı gün, kullanıcı isteğiyle):** (1) dil butonuna seçili
    dili gösteren rozet eklendi (`{{ LANGUAGE_CODE|upper }}`, `.site-nav__
    lang-trigger`/`.site-nav__lang-code` CSS). (2) `forum/middleware.py` →
    yeni `ForceDefaultLanguageMiddleware` (settings.py'de
    `AuthenticationMiddleware`'den sonra, `LocaleMiddleware`'den ÖNCE) —
    çerez yoksa `Accept-Language` header'ını temizler, tarayıcı dili ne
    olursa olsun prefix'siz sayfa hep `tr` açılır. **Araştırılıp Django'nun
    kendi tasarımı olduğu doğrulanan (bug değil) davranış:** `prefix_default
    _language=False` ile çıplak `/` URL'si, `django_language` çerezi ne
    olursa olsun HER ZAMAN varsayılan dili (`tr`) gösterir — Django'nun
    `LocaleMiddleware.process_request`'i bunu kasıtlı yapıyor (bkz. Django
    kaynağı: `language_from_path` yoksa + `i18n_patterns` kullanılıyorsa +
    `prefixed_default_language=False`'sa → `language = settings.LANGUAGE_CODE`
    ile override eder). Kullanıcı dil değiştirince (`/i18n/setlang/` POST)
    `translate_url()` doğru prefix'li URL'ye (`/de/`) yönlendiriyor, oradan
    itibaren tüm `{% url %}` linkleri prefix'i koruyor — sorun yalnızca
    "çerez set edilmişken çıplak `/`'i elle tekrar ziyaret etme" senaryosunda
    ve bu, tek-URL=tek-dil SEO ilkesiyle örtüştüğü için kasıtlı bırakıldı.
    Doğrulama: curl ile Accept-Language:en-US + çerezsiz → tr; `/en/` hâlâ
    çalışıyor; gerçek POST ile `next=/` + `language=de` → `Location: /de/`.
- [x] **5b. Kalan SEO işleri:** TAMAMLANDI (23 Eylül 2026).
  `forum.context_processors.hreflang_alternates` → base.html'de tr/en/de +
  x-default `<link rel="alternate">` (yalnızca i18n_patterns sayfaları:
  translate_url her dilde farklı yol üretirse) + dile göre `og:locale` /
  `og:locale:alternate`. Sitemap: `MultilingualSitemapMixin` (Django
  `i18n`/`alternates`/`x_default`) — static-i18n, istatistik, training,
  tools-i18n; tek dilliler (forum, blog, uzman dizini, yoktez…, ilanlar)
  değişmedi. Hepsi `feature_multilingual`'a bağlı (kapalıyken /en/ 404).
  18 araç şablonundaki sabit TR canonical → `{% url 'analiz_console' %}`.
  robots.txt'ye özel sayfaların /en/ /de/ karşılıkları eklendi.
  Kasıtlı: ilan detayları sitemap'te tek dilli (içerik Türkçe UGC — ince
  kopya içerik riski); sayfa başlığındaki hreflang yine üretilir.
- [ ] **6. Python tarafı metinler:** kapsamdaki app'lerin (istatistik
  servisleri, makaleanaliz, openalex, semanticscholar) view/form hata
  mesajları ve PDF çıktı metinleri — ayrı görev olarak scope'u netleştir
  (PDF font/layout Türkçe karaktere göre ayarlı, `pdf_fonts.py` etkilenir mi
  kontrol edilmeli)
- [ ] **7. Deploy:** dev → Render'da doğrula, sonra kullanıcı onayıyla
  main → Hetzner'de `docker compose exec web python manage.py
  compilemessages` + `restart web` + `restart nginx`

## Bulunup Düzeltilen Kritik Bug (22 Eylül 2026, kullanıcı raporu)

**Belirti:** "de ve tr seçilmiyor, en seçilebiliyor" — `/en/` veya `/de/`
sayfasındayken dil dropdown'undan başka bir dile geçiş çoğunlukla
çalışmıyordu (sessizce aynı sayfada kalıyordu).

**Kök neden:** `path('i18n/', include('django.conf.urls.i18n'))`
`i18n_patterns` dışında (prefix'siz) tanımlıydı. Django'nun
`LocaleMiddleware`'i, prefix'siz HER isteğin aktif dilini zorla varsayılana
(`tr`) çeviriyor (`prefix_default_language=False` tasarımının bir parçası —
bkz. yukarıdaki "5a-devam" notu). `/i18n/setlang/`'in KENDİSİ prefix'siz
olduğu için, bu POST isteği işlenirken aktif dil hep `tr`'ye zorlanıyordu.
Django'nun `set_language` view'ı içindeki `translate_url(next, lang_code)`,
`next` değerini (`/en/...` gibi) çözerken bu yanlış ('tr') aktif dil
bağlamını kullanıyor — `i18n_patterns`'in prefix regex'i dinamik olarak
aktif dile göre kurulduğu için (`LocalePrefixPattern.language_prefix`),
`/en/...` yolu 'tr' bağlamında hiçbir pattern'e uymuyor (`Resolver404`),
`translate_url` `next`'i DEĞİŞTİRMEDEN döndürüyor.

**Düzeltme:** `analizdestek/urls.py` → `i18n/` path'i `i18n_patterns(...)`
bloğunun İÇİNE taşındı. Artık `{% url 'set_language' %}` her sayfada kendi
dil prefix'ini taşıyor (`/en/i18n/setlang/`, `/de/i18n/setlang/`), bu
isteğin aktif dili artık her zaman doğru (`en`/`de`) oluyor, `translate_url`
`next`'i doğru çözüyor.

**Doğrulama:** 3 kaynak sayfa (`/`, `/en/`, `/de/`) × 3 hedef dil = 9
kombinasyonun hepsi gerçek POST ile test edildi, hepsi doğru `Location`
başlığı döndürdü. `/en/analiz/ttesti/` → `de` seçimi de ayrıca doğrulandı
(`/de/analiz/ttesti/`).

## Bulunup Düzeltilen 2. Kritik Bug + Admin Flag (22 Eylül 2026)

**Belirti:** "dil seçiminden sonra sayfa değiştiğinde otomatik olarak tr'ye
geçiliyor" — `/en/`/`/de/` sayfasındayken "Giriş" linkine tıklayınca dil
bağlamı kayboluyordu.

**Kök neden:** `login`/`logout` bilinçli olarak `i18n_patterns` dışında
(prefix'siz) tutulmuştu — `django.contrib.auth.urls`'ün kendi `login`/
`logout` adlarıyla çakıştığı için (`reverse()` belirsizliği). Prefix'siz
kalınca aynı "5a-devam"/"i18n/ path'i" bug'larıyla aynı kök sorun: bu
sayfaya giden isteğin KENDİSİ prefix'siz olduğu için `LocaleMiddleware`
aktif dili zorla `tr`'ye çekiyordu.

**Düzeltme:** `django.contrib.auth.urls` include'u KALDIRILDI (sadece
kullanılmayan `password_change`/`password_change_done` elle tanımlandı —
kod tabanında `password_change` hiç kullanılmıyor, grep ile doğrulandı),
`login`/`logout` artık `i18n_patterns` içinde. Artık isim çakışması yok,
`{% url 'login' %}` her sayfada kendi dil prefix'ini koruyor
(`/en/login/`, `/de/login/`).

**Ek — Admin'den açılır/kapanır flag (kullanıcı isteği):**
- `SiteSettings.feature_multilingual` (BooleanField, `default=False` —
  diğer "hazır ama henüz yayında değil" flag'leriyle tutarlı:
  `feature_agentic_landing`/`feature_training` gibi)
- `forum/context_processors.py` → `feature_flags()`'e eklendi
- `forum/admin.py` → `SiteSettingsAdmin.fieldsets`'e eklendi (KRİTİK adım —
  unutulursa flag DB'de var ama admin'den hiç değiştirilemez, bkz.
  analizus.md §26 "Yeni SiteSettings feature flag" dersi)
- `forum/middleware.py` → yeni `MultilingualFeatureMiddleware`: flag
  kapalıyken `/en/`, `/de/` prefix'li TÜM istekleri 404 ile keser
  (`settings.MIDDLEWARE`'de `ForceDefaultLanguageMiddleware`'den sonra,
  `LocaleMiddleware`'den önce)
- `templates/base.html` → navbar'daki dil seçici (desktop + mobil)
  `{% if features.multilingual and is_multilingual_page %}` ile sarıldı

**Ek — kapsam dışı sayfalarda dil seçici gizleme (kullanıcı kararı: "Gizle"):**
- `forum/context_processors.py` → yeni `multilingual_page_context()`:
  Django'nun `set_language` view'ının kullandığı AYNI `translate_url()`
  mekanizmasıyla, `'en'` ve `'de'` hedeflerine çeviri farklı URL üretiyorsa
  sayfa kapsamda demektir (`is_multilingual_page=True`); kapsam dışı
  sayfalarda (tarama, forum, yoktez, trdizin, oaipmh) ikisi de değişmeden
  aynı path'e eşit döner → seçici hiç gösterilmez. Öncesinde seçici orada
  da görünüyordu ama tıklayınca "görünürde hiçbir şey değişmiyordu" (çerez
  set ediliyordu ama gidecek prefix'li adres yoktu) — kafa karıştırıcıydı.

**Doğrulama:** `manage.py check` temiz; migration uygulandı; flag kapalıyken
`/en/`→404 + navbar'da seçici yok, flag açıkken `/en/`→200 + seçici var;
`reverse('login')`/`reverse('logout')` tr/en/de için doğru prefix'li;
`/en/login/` 200 + `<html lang="en">` + sayfadaki tüm linkler `/en/`
prefix'ini koruyor; kapsam içi sayfalarda (`/`, `/analiz/ttesti/`) seçici
görünüyor, kapsam dışında (`/tarama/`, `/forum/`) gizli.

## Bulunup Düzeltilen 3. Bug + Karar Değişikliği (22 Eylül 2026)

**Belirti 1 (Render):** Navbar'da "EN" rozetinin yanında boş/kırık bir
kutu görünüyordu (giriş yapmış kullanıcıda).
**Kök neden:** `Gelen kutusu` (`inbox`) linkine `{% trans %}` eklerken
`<a ...>` etiketinin kapanış `>` işareti yanlışlıkla silinmişti — `<svg>`
bir sonraki satırda geldiği için tarayıcı etiketi bozuk parse ediyor,
ikon hiç render olmuyordu. `templates/base.html` düzeltildi, aynı hata
için diğer tüm `aria-label="{% trans ... %}"` satırları taranıp
doğrulandı (başka bozuk yer yok).

**Belirti 2 (Render):** Sayfa değiştikçe dil seçici görünüp kayboluyordu.
**Karar değişikliği:** Kapsam dışı sayfalarda (tarama, forum, yoktez...)
dil seçiciyi gizleme kararı ("Gizle") kullanıcıyı şaşırttı — geri alındı.
Artık **her sayfada her zaman görünür** (kapsam dışı sayfada tıklarsa
çerez set edilir ama görünür bir değişiklik olmaz — kabul edilebilir).
`multilingual_page_context()` context processor'ü ve `is_multilingual_page`
kontrolü kaldırıldı (kullanılmıyordu, sadelik için silindi).

**Ortam notu:** Yerel makinede İKİ ayrı sunucu çalışıyor — Docker
(nginx/443, postgres) ve bağımsız `manage.py runserver` (port 8000,
`db.sqlite3`, .env'de `DATABASE_URL` kapalı olduğu için fallback).
İkisi FARKLI veritabanı kullanıyor — birinde yapılan flag/veri değişikliği
diğerinde görünmez. Test ederken hangi sunucuda olduğunuza dikkat edin.

## Adım 4 — İlk Çeviri Turu Tamamlandı (23 Eylül 2026, kullanıcı isteğiyle öne alındı)

**Neden öne alındı:** 3b-2 grubu (proje talebi/eğitim/AI çözümler) bitince
kullanıcı "hâlâ çeviriler sayfalarında gözükmüyor" dedi — haklı olarak,
o ana kadarki iş sadece `{% trans %}` işaretlemesiydi, gerçek çeviri
metni yoktu. Sırayı değiştirip o ana kadar işaretlenen HER ŞEYİN gerçek
İngilizce+Almanca çevirisini yazdım.

**Yapılanlar:**
- `gettext` container'a geçici kuruldu (kalıcı `requirements.txt`
  bağımlılığı DEĞİL, tek seferlik)
- `makemessages -l en -l de` → 601 msgid çıkarıldı
- `polib` ile Python script (`translate_po.py`, scratchpad'te) yazılıp
  601 metnin TAMAMI için EN+DE çevirisi elle yazıldı (plural + python-format
  placeholder'lar korunarak: `%(daily_limit)s`, `%(job_id)s`,
  `%(tool_title)s`/`%(promo_title)s` vb.)
- `compilemessages` ile derlendi

**Bulunup düzeltilen 2 ek sorun:**
1. **Fuzzy işaretler:** `makemessages` benzer eski msgid'lere göre bazı
   yeni string'leri otomatik "fuzzy" işaretliyor (ör. "Ücretsiz" →
   "Ücretsiz Dene" benzerliği) — `compilemessages` fuzzy girişleri
   VARSAYILAN OLARAK derlemeye dahil etmiyor, msgstr dolu olsa bile
   sessizce atlanıyor. `msgattrib --clear-fuzzy` ile temizlendi (6 kayıt
   etkilenmişti). **Bu adımı gelecekte her `makemessages` sonrası
   unutma.**
2. **`service_promo.html` keşfi:** Anonim kullanıcılar (yeni ziyaretçilerin
   çoğu) istatistik/openalex/semanticscholar araçlarında asıl çevirdiğim
   şablonu değil, `service_promo.html` adında paylaşılan bir "kayıt ol"
   davet şablonunu görüyor (`if not request.user.is_authenticated`).
   Bu dosya orijinal 26 dosyalık listede yoktu — küçük (211 satır) ve
   doğrudan kapsamdaki araçların giriş kapısı olduğu için ek onay
   almadan işaretlendi ve çevrildi.

**Doğrulama:** Giriş yapmış VE anonim oturumla `/en/`, `/de/` üzerinde
home, footer, navbar, openalex, semanticscholar, analiz/anova,
proje-talebi, login/register sayfaları curl ile test edildi — gerçek
İngilizce/Almanca metin görünüyor (`manage.py check` temiz).

**Kasıtlı hâlâ çevrilmemiş (adım 6 kapsamı, Python tarafı):**
`training_catalog.py` kurs verileri, `TOOL_CATEGORIES` sidebar etiketleri,
`seo_guide`/SEO_GUIDES sözlüğü (intro/faq/apa_example vb.), quiz soru
bankası, `analyses_list` (makaleanaliz), tablo satırları (`{{ label }}` /
`{{ m.title }}` gibi DB/servis çıktısı alanlar).

## Açık Sorular (kullanıcıya soruldu, netleşince ilerlenir)
- Proje talebi / Danışmanlık / Eğitim sayfaları kapsama girecek mi?
- İstatistik araçlarının analiz sonuç metinleri (PDF rapor içerikleri) de
  çevrilecek mi, yoksa sadece giriş/açıklama sayfaları mı?

---

# [ÖNCELİKLİ] Local Docker Ortamı — nginx crash-loop + yanlış DB fallback

**Durum:** TAMAMLANDI (23 Temmuz 2026) — nginx crash-loop çözüldü, DB fallback
çözüldü. Aşağıdaki "Önerilen düzeltme" bölümü artık geçmiş kayıt.

## Bulgular

**1. nginx sürekli restart oluyor (`docker compose ps` → `Restarting (1)`)**
Log (`docker compose logs nginx`): her ~60 saniyede bir
`cannot load certificate "/etc/letsencrypt/live/analizus.com/fullchain.pem"`
hatasıyla çöküyor. Kök neden: `docker-compose.yml:41` production nginx config'ini
(`./nginx/conf.d` — Let's Encrypt sertifika yolu bekliyor) mount ediyor, ama bu
sertifika yerel makinede yok (yalnızca Hetzner'de var).

Zaten 13 Temmuz'da (10 gün önce) bunun için bir local override hazırlanmış ama
hiç bağlanmamış: `nginx/conf.d.local/local.conf` (untracked dosya, git'e hiç
eklenmemiş) self-signed sertifika (`/etc/nginx/local-ssl/selfsigned.crt`)
kullanacak şekilde yazılmış — ama:
  - `docker-compose.yml` hâlâ `./nginx/conf.d`'yi mount ediyor, `conf.d.local`'ı değil
  - Self-signed sertifika dosyaları (`selfsigned.crt`/`.key`) henüz üretilmemiş,
    docker-compose.yml'de mount edilecek bir volume de tanımlı değil

**2. Web container Postgres yerine SQLite'a düşüyor**
`.env:9` içinde `DATABASE_URL` satırı yorumlu (`# DATABASE_URL=postgres://...`).
`analizdestek/settings.py:124-129`'daki `dj_database_url.config(default='sqlite:///...')`
bu yüzden sessizce `db.sqlite3`'e fallback yapıyor — halbuki `analizdestek-db-1`
(Postgres) container'ı zaten ayakta ve çalışıyor, web ona hiç bağlanmıyor.
Bu yüzden shell'den sorgulanan sayılar (ör. `FreelanceJob` tamamlanan iş sayısı)
yanlış/boş çıktı verdi — gerçek veri kaybı DEĞİL, yanlış DB'ye bağlanma sorunu.

## Önerilen düzeltme — TÜMÜ TAMAMLANDI (bkz. aşağıdaki "nginx düzeltmesi +
KRİTİK git-güvenlik düzeltmesi" ve "Madde 3 sonucu" bölümleri için uygulama
detayları). Bu blok artık geçmiş kayıt.

## nginx düzeltmesi + KRİTİK git-güvenlik düzeltmesi (23 Temmuz 2026, TAMAMLANDI)

Self-signed sertifika üretildi (`openssl req -x509 ...` → `nginx/local-ssl/
selfsigned.crt`+`.key`, 825 gün geçerli, `.gitignore`'a eklendi — makineye
özel, commit edilmeyecek).

**⚠️ ÖNEMLİ BULGU — `docker-compose.yml` Hetzner ile PAYLAŞILAN tek dosya:**
`analizus.md` §3 doğruladı: Hetzner production da `git pull origin main` ile
aynı `docker-compose.yml`'i çekip `docker compose` ile çalıştırıyor (container
adları `app-web-1`/`app-db-1`/`app-nginx-1`, aynı `web`/`db`/`nginx` servis
isimleri). İlk denemede nginx volume mount'unu VE `web` servisine bir
`environment: DATABASE_URL: ...` override'ını doğrudan bu paylaşılan dosyaya
yazmıştım — bu, Hetzner'in `main`'e merge sonrası `git pull` yapmasıyla
**production nginx'ini (Let's Encrypt yerine self-signed/local config) ve
olası DB bağlantısını kırma riski** taşıyordu (Docker Compose'da `environment:`
her zaman `env_file`'dan önceliklidir — Hetzner'in gerçek `.env`'indeki
`DATABASE_URL`'i sessizce ezebilirdi).

**Düzeltme:** `docker-compose.yml` **main ile birebir aynı** hale geri
döndürüldü (`diff <(git show main:docker-compose.yml) docker-compose.yml` →
fark yok, doğrulandı). Tüm local-only override'lar (`web.environment.
DATABASE_URL`, `nginx.volumes` → `conf.d.local`+`local-ssl`) yeni bir
**`docker-compose.override.yml`** dosyasına taşındı — Docker Compose bunu
`docker compose up`'ta otomatik yükler (ekstra `-f` bayrağı gerekmez) ama
dosya `.gitignore`'a eklendiği için **hiçbir zaman commit'lenmez, Hetzner'e
asla ulaşmaz**. Doğrulama: `docker compose config` ile birleşmiş ayarlar
kontrol edildi (DATABASE_URL doğru, nginx conf.d.local+local-ssl doğru),
`docker compose up -d` sonrası hem Postgres bağlantısı (`ENGINE: postgresql`)
hem nginx (`https://localhost/` → 200, restart döngüsü yok) çalışır durumda.

**Ders (gelecek oturumlar için kritik):** `docker-compose.yml` Hetzner
production'da da kullanılan paylaşılan bir dosya — local-only ayarlar asla
doğrudan bu dosyaya yazılmamalı, her zaman gitignore'lu bir
`docker-compose.override.yml`'e (veya benzeri) izole edilmeli. `nginx/conf.d.
local/local.conf` (sertifika/secret içermiyor) git'e eklenip commit'lendi —
gelecekte tekrar kurulum gerekmesin diye.

**Sonuç:** `docker compose ps` → 4 container da stabil (`db` healthy, `redis`/
`web`/`nginx` Up, hiçbiri restart döngüsünde değil).

## Madde 3 sonucu — TAMAMLANDI (23 Temmuz 2026)
"Tamamlanan pazar talebi istatistikleri" (FreelanceJob completed count)
sorunu çözüldü, 3 katmanlı kök neden bulundu ve düzeltildi:

1. `.env`'de `DATABASE_URL=postgres://bunyamin:analizus@db:5432/analizus`
   eklendi (satır yorumdan çıkarıldı) — web artık SQLite'a değil Postgres'e
   bağlanıyor.
2. **Yeni bulgu:** Bağlantı denenince şifre hatası çıktı — `app_postgres_data`
   volume'ü daha önce farklı bir şifreyle init edilmiş olduğundan `bunyamin`
   rolünün gerçek şifresi `.env`'deki değerle uyuşmuyordu. Yerel unix socket
   üzerinden (`docker exec -u postgres analizdestek-db-1 psql -U bunyamin -d
   analizus`) bağlanılıp `ALTER ROLE bunyamin WITH PASSWORD 'analizus';` ile
   düzeltildi.
3. **Yeni bulgu:** Şifre düzelince DB'nin 107 migration geride olduğu ortaya
   çıktı (forum uygulaması `0068`'de kalmıştı — `seed_initial_users`,
   `freelancejob` alan eklemeleri gibi kritik migration'lar uygulanmamıştı).
   Local/dev DB olduğu için (production etkilenmiyor)
   `docker compose exec web python manage.py migrate` çalıştırıldı, hepsi
   başarıyla uygulandı (`showmigrations` artık 0 bekleyen gösteriyor).

**Yan etki — istenmeyen e-posta patlaması (23 Temmuz 2026, aynı gün çözüldü):**
`docker compose restart web` iki kez çalıştırıldı (madde 1 ve madde 3 sonrası
doğrulama için). `Dockerfile` CMD'si her başlangıçta `deploy.sh`'i çalıştırıyor;
`deploy.sh` "DB boşsa seed yükle" idempotency kontrolü (`Topic.objects.count()`)
kullanıyor. İkinci restart'ta Postgres'e ilk kez gerçekten bağlanıldığı ve forum
tabloları taze/boş olduğu için bu kontrol "boş" algıladı, `load_seed_content`
gerçek `User.objects.create_user()` ile ~78 sahte kullanıcı oluşturdu →
`forum/signals.py:578` `post_save` sinyali → `notify_admin_new_user` →
**gerçek SMTP** (`.env`'deki `mail.analizus.com`) üzerinden admin'in gerçek
Gmail'ine (`ADMIN_NOTIFICATION_EMAIL`) ~78 ayrı e-posta gitti (her biri ayrı
async thread, birkaç dakikaya yayılarak ulaştı). Kaynak süreç kendi kendine
bitti, kalıcı bir hata değildi — bir daha aynı restart'ta tekrar tetiklenmez
çünkü DB artık boş değil (idempotency guard tutar).

**Kök neden düzeltmesi — host/Docker DB ayrışması (23 Temmuz 2026, TAMAMLANDI):**
Yukarıdaki 1. maddede `.env`'e yazılan `DATABASE_URL=postgres://...@db:...`
host'ta (`.venv`/conda ile) normal `python manage.py runserver` çalıştıran
günlük local iş akışını kırdı — `db` hostname'i yalnızca docker-compose
network'ünde çözülüyor (`could not translate host name "db"`).
`analizus.md` §24 ("DATABASE_URL boş bırak, SQLite kullanılır" — host için
dokümante edilmiş varsayılan) ile §26 ("host Docker servis adı olmalı" — bu
kural Docker/prod bağlamı için) referans alınarak iki ortam ayrıştırıldı:
- `.env`'deki `DATABASE_URL` tekrar yorum satırına döndürüldü (host →
  SQLite, eski/dokümante davranış).
- `docker-compose.yml`'de `web` servisine `environment: DATABASE_URL:
  postgres://${POSTGRES_USER:-bunyamin}:${POSTGRES_PASSWORD:-analizus}@db:
  5432/${POSTGRES_DB:-analizus}` override'ı eklendi (yalnızca container için
  Postgres, `env_file`'daki boş değeri ezer).
Doğrulandı: `docker compose up -d web` sonrası container hâlâ Postgres'e
bağlı (`ENGINE: postgresql`, `NAME: analizus`); bu recreate'te `deploy.sh`
seed adımı tekrar denedi ama kaynak `.md` dosyaları bulunamadığından
(`AnalizDestek_Forum_Seed_Content.md` yok) hiç yeni kullanıcı oluşturmadı,
kullanıcı sayısı 97'de sabit kaldı — **yeni e-posta gitmedi**.

**/market/ istatistik bandının local'de görünmemesi — bug DEĞİL, kasıtlı
sıfır kuralı (23 Temmuz 2026, doğrulandı):** Kullanıcı local'de `/market/`
sayfasındaki "Tamamlanan İş / Aktif Uzman / Son 90 Gün" üçlü sayaç bandının
hiç görünmediğini bildirdi. İnceleme: `forum/views.py:450-456`'daki
`market_stats` (`total_completed`, `recent_completed`, `total_experts`) ve
`forum/templates/forum/market/job_list.html:65` `{% if market_stats.
total_completed or market_stats.total_experts or market_stats.
recent_completed %}` — template yorumu bunu zaten "sıfır kuralı: üçü de 0
ise şerit gizli" diye adlandırıyor. Local Postgres DB'de `FreelanceJob` ve
`JobProposal` tabloları tamamen boş (0 kayıt, yukarıdaki DB fallback
sorunundan bağımsız — local ortamda hiç gerçek pazar verisi girilmemiş)
olduğu için üçü de 0 çıkıyor, şerit kasıtlı olarak gizleniyor. Kod tarafında
hata/cache bayatlığı/isim uyuşmazlığı yok. Ana sayfadaki `showcase_jobs`
(views.py:284-299) de aynı sebeple boş. **İş gerekmiyor** — local'de gerçek
iş ilanı/teklif verisi oluşturulursa bant otomatik görünür.

**Sonuç:** `FreelanceJob.objects.count()` artık hatasız çalışıyor, sonuç **0**.
Repo kökündeki `yedek_2026-07-13.sql` yedeği de kontrol edildi — orada da
yalnızca 1 kullanıcı (admin) ve 0 iş var. Yani local ortamda hiçbir zaman
gerçek pazar verisi olmamış; "0 tamamlanan iş" artık **doğru** sonuç,
önceki yanlış/boş çıktı tamamen yanlış DB bağlantısından kaynaklanıyordu.

## Sıradaki adım
Yok — sertifika üretimi de (bkz. yukarı "nginx düzeltmesi" bölümü, 23 Temmuz
2026) dahil tüm maddeler tamamlandı, doğrulandı: 31 Temmuz 2026 itibarıyla
`docker compose ps` 4 container da stabil, nginx restart döngüsünde değil.

---

# Bootstrap Kaldırma — Kademeli Migration Planı

**Durum (25 Ekim 2026):** Faz 1-2 TAMAMLANDI. Faz 3 sürüyor — 19 dosya
migre edildi, **48 dosyada hâlâ gerçek Bootstrap component class'ı var**
(bkz. "Güncel envanter" altı). Faz 4-5 henüz başlamadı.

## Neden gerekli
CLAUDE.md kuralı "Bootstrap yalnızca grid için" diyor ama gerçek kod bunu ihlal
ediyor — Lighthouse'un "kullanılmayan CSS 111 KiB / kullanılmayan JS 164 KiB"
bulgusunun kaynağı bu. Ayrıca Google Fonts/Bootstrap CDN cache-control süresi
bizim kontrolümüzde değil (Lighthouse "verimli önbellek" bulgusu, 177 KiB).

## Envanter (temmuz 2026 taraması)
- **102 template dosyası** Bootstrap component class kullanıyor (`btn`, `card`,
  `badge`, `alert`, `modal`, `dropdown`, `form-control`, `form-select`)
- **13 dosya** `data-bs-toggle`/`data-bs-target`/`data-bs-dismiss` kullanıyor
  (Bootstrap JS bundle'a bağımlı — modal/dropdown açma-kapama)
- **96 dosya** grid class'ı (`container`/`row`/`col-*`) kullanıyor
- **3 dosya** JS'te doğrudan `new bootstrap.Modal(...)` / `bootstrap.Dropdown`
  API'sini çağırıyor: `forum/templates/forum/success_stories.html`,
  `static/js/notifications.js`, `templates/base.html`
- En ağır kullanan dosyalar: `hangi_test.html` (144), `base.html` (127),
  `studyroom_detail.html` (117), `tezanaliz/landing.html` (97),
  `istatistik/korelasyon.html` (93), `market/job_detail.html` (93)

**Not (11 Ekim 2026):** Yukarıdaki temmuz sayıları güvenilmez çıktı —
naif `\bbadge\b` gibi regex'ler `ax-badge` içindeki "badge" alt-dizesini de
sayıyordu (iş. `account_delete.html`/`job_list.html` gibi dosyalarda
"3 component" tahmini gerçekte 8-23 çıktı). Aşağıdaki "Güncel envanter"
`class="..."` içindeki TAM token eşleşmesiyle (ax- öneki hariç tutularak)
yeniden çıkarıldı, güvenilir kaynak odur.

## Güncel envanter (11 Ekim 2026 taraması — tam token eşleşmesi)
Faz 3'te migre edilen 11 dosya ve kapsam dışı bırakılan 6 standalone auth
sayfası + 2 yetim dosya hariç, proje genelinde **55 template dosyasında
toplam ~760 gerçek Bootstrap component class eşleşmesi** (`btn`, `card`,
`card-body`, `card-title`, `card-text`, `badge`, `dropdown`, `dropdown-toggle`,
`dropdown-menu`, `dropdown-item`, `modal`, `alert`, `form-control`,
`form-select`) kaldı. Yoğunluğa göre (düşükten yükseğe, Faz 3'ün kendi
önceliklendirme kuralına uygun):

**Not (25 Ekim 2026) — "Düşük" grubun gerçek sayıları bu aralıktan yüksek
çıktı:** 11 Ekim'deki "4-10 class" tahmini yine iyimserdi (bkz.
[[feedback_verify_inventory_counts]]); bugünkü tam token eşleşmesiyle
yeniden sayımda grup aslında 8-19 class arasında. Üç dosya (aşağıda
işaretli) bu turda migre edildi, grup 20 dosyaya indi.

**Yetim dosya bulgusu (25 Ekim 2026):** `forum/templates/forum/section_detail.html`
hiç render edilmiyor — `views.section_detail` artık yalnızca
`forum_index`'e kalıcı yönlendirme (`redirect(..., permanent=True)`) yapıyor
(GSC "taranmış, indekslenmemiş" sorunu için), template hiçbir `render()`
çağrısında kullanılmıyor. Migrasyon kapsamından çıkarıldı (zaman kaybı,
dosya hiç kullanıcıya görünmüyor), silinmedi — ayrı bir karar.

**Düşük (~8-19 class, ~16 dosya) — sıradaki adaylar:**
`forum_index.html`, `footer.html` (partials),
~~`edit_job.html`~~ (✅ 25 Ekim), ~~`post_job.html`~~ (✅ 25 Ekim),
~~`search_results.html`~~ (✅ 25 Ekim), ~~`verification_pending.html`~~
(✅ 25 Ekim), ~~`my_payments.html`~~ (✅ 25 Ekim), ~~`section_detail.html`~~
(yetim dosya, kapsam dışı — yukarı bkz.),
`bibliometrics/order.html`, `my_jobs.html`, `new_topic.html`,
`studyroom_edit.html`, ~~`category_topics.html`~~ (✅ 25 Ekim),
~~`_review_section.html`~~ (✅ 25 Ekim),
`promote_job_iban.html`, `success_stories.html` (modal JS Faz 2'de taşındı,
component class'ları kaldı), `oaipmh/order.html`, `semanticscholar/order.html`,
`service_promo.html`, `trdizin/order.html`, `how_it_works.html`,
`onboarding.html`, `openalex/order.html`

**Orta (10-20):** `_studyroom_card.html`, `proje_talebi.html`,
`studyroom_list.html`, `templates/base.html` (11 — ayrı, dikkatli ele
alınmalı), `blog_detail.html`, `studyroom_create.html`,
`referral_dashboard.html`, `ai_assistant.html`, çoğu istatistik aracı
(`lineer_regresyon`, `lojistik_regresyon`, `kruskal_wallis`,
`mann_whitney`, `karar_agaci`, `ki_kare`, `svm`, `orneklem`),
`tableau_dashboard.html`, `oaipmh/landing.html`, `trdizin/landing.html`,
`yoktez/landing.html`

**Ağır (20-48) — en sona bırakılacak:** `semanticscholar/landing.html` (21),
`makaleanaliz/results.html` (22), `tezanaliz/results.html` (22),
`tezanaliz/landing.html` (24), `send_message.html` (26),
`uzman_dizini.html` (26), `openalex/landing.html` (27),
`bibliometrics/landing.html` (29), `studyroom_detail.html` (36),
**`market/job_detail.html` (48 — en ağır dosya)**

**Ayrı, hiç envanteri çıkarılmamış bir alt görev:** Bootstrap **utility**
class'ları (`d-flex`, `text-white`/`text-muted`, `fw-bold`, `mb-*`/`py-*`/
`px-*`, `gap-*`, `rounded-*`, `shadow-*`, `bg-*`, `border-*`) — migre edilmiş
10 dosyada bile hâlâ kasıtlı olarak bırakıldı (Faz 3 kararı, bkz. yukarı).
Faz 4 (CDN kaldırma) güvenli olmadan önce bunların da envanterinin
çıkarılıp ayrı bir turda ele alınması gerekiyor — bu iş hiç başlamadı.

## Mevcut ax- sistem durumu (static/css/)
Var olan: `.ax-btn` (base.css), `.ax-card` (cards.css), `.ax-badge` (8 tanım,
cards.css/profiles.css/home_sections.css'e dağılmış)

Eksik — inşa edilmesi gereken: `.ax-alert`, `.ax-modal`, `.ax-dropdown`,
`.ax-form-control`/`.ax-form-select`/`.ax-form-check`, `.ax-tooltip`,
`.ax-toast`, `.ax-collapse`/`.ax-tab`

## Fazlar

### Faz 1 — Eksik ax- CSS bileşenlerini inşa et (sıfır görsel etki) — TAMAMLANDI
`static/css/base.css`'e 4 yeni bölüm eklendi (7. Alert, 8. Modal, 9. Dropdown,
10. Form Controls — dosya sonu Responsive Utilities artık 11), mevcut
numaralandırma/token/isimlendirme deseni takip edildi. Hiçbir template
değiştirilmedi.
- `.ax-alert` (+ success/danger/warning/info varyantları)
- `.ax-modal` (backdrop + dialog + header/body/footer, `.is-open` toggle)
- `.ax-dropdown` (site-nav'daki `.site-nav__dropdown*` ile aynı görsel dil,
  genel kullanım için ayrı isimlendirildi — `.ax-dropdown-wrap`/`.ax-dropdown`)
- `.ax-form-control` / `.ax-form-select` / `.ax-form-check` (+ `.ax-form-group`,
  `.ax-form-label`, `.ax-form-hint`)

**Not — "sıfır görsel etki" tam sağlanamadı, bilinçli olarak kabul edildi:**
Uygulamadan önce tarama yapıldı, 2 sayfa zaten bu class isimlerini
kullanıyor ama hiçbir CSS tanımı yoktu (çıplak/stilsiz kullanım):
- `yoktez/templates/yoktez/results.html` (54, 192. satır) —
  `ax-alert ax-alert--danger` artık gerçekten stillenecek
- `istatistik/templates/istatistik/anova.html` (61, 66. satır) —
  `ax-form-control` artık gerçekten stillenecek

Kullanıcı onayıyla bug-fix niteliğinde kabul edildi. **TODO: bu 2 sayfa
tarayıcıda görsel doğrulanmalı** (deploy sonrası).

Çakışma olmayan (kontrol edildi, dokunulmadı): `ttesti.html`/`hangi_test.html`
kendi `.ax-form-control` tanımına sahip (body içindeki `<style>` bloğu,
cascade'de kazanıyor); `normallik.html` vb. istatistik sayfaları tek tireli
`ax-alert-danger`/`ax-alert-info` kullanıyor (farklı isim, çakışmıyor);
`hangi_test.html`'in `.ax-modal-overlay/-dialog` yapısı tamamen ayrı
isimlendirme.

### Faz 2 — Vanilla JS modal/dropdown controller — TAMAMLANDI (modal+dropdown)
**Kapsam kullanıcı onayıyla daraltıldı:** `notifications.js`'teki
`bootstrap.Toast` kapsam dışı bırakıldı — gerçekte Modal/Dropdown değil Toast
kullanıyordu, `.ax-toast` CSS'i Faz 1'de yok, ayrı görev olarak aşağıda not
edildi.

**Yapılanlar:**
- `static/js/ax-modal.js` (yeni) — `data-ax-toggle="modal"` / `data-ax-target`
  / `data-ax-dismiss="modal"` deseni + backdrop tıklama + Escape ile kapatma +
  `.ax-no-scroll` scroll kilidi + `window.AxModal.open/close` programatik API.
- `static/js/ax-dropdown.js` (yeni) — `.ax-dropdown-wrap`/`[data-ax-dropdown]`
  için genel controller, `navbar.js`'e dokunmadan ayrı çalışır. **Henüz hiçbir
  template kullanmıyor** — Faz 3 migration'larında kullanılacak, şimdilik no-op.
- `templates/base.html` — 4 modal (`searchModal`, `quizModal`, `profileModal`,
  `storyModal`) markup'ı `.ax-modal-backdrop`/`.ax-modal`/`.ax-modal__*`'e
  taşındı; 3 `new bootstrap.Modal()` çağrısı `AxModal.open(el)` ile değiştirildi;
  arama tetikleyicisi `data-ax-toggle`'a geçti. Modal içeriği (quiz butonları,
  badge'ler, spinner-border) kasıtlı olarak Bootstrap class'larıyla bırakıldı
  — o Faz 3'ün kapsamı (component migration), Bootstrap CSS/JS Faz 4'e kadar
  zaten yüklü kalacak.
- `forum/templates/forum/success_stories.html` — `shareStoryModal` aynı şekilde
  taşındı, `bootstrap.Modal(...).show()` → `AxModal.open(...)`.

**Bilinçli küçük görsel sapmalar (doğrulama listesine eklendi):**
- `profileModal`/`storyModal`'ın özel inline arka plan renkleri
  (`rgba(15,23,42,.95)`, gradient) kaldırıldı, `.ax-modal`'ın standart koyu
  arka planı kullanılıyor — görsel olarak çok yakın ama birebir aynı değil.
- `base.html`:511'deki mesaj `alert`/`data-bs-dismiss="alert"` kasıtlı
  dokunulmadı — bu Bootstrap'ın Alert bileşeni (Modal/Dropdown değil),
  kapsam dışı.

**Görsel doğrulama — TAMAMLANDI.** İlk testte modallar gizlenmedi, sayfa
akışının içinde çıplak görünüyorlardı — sebep `base.css`'in cache-busting
versiyonunun (`?v=0100`) Faz 1/2 içerik değişikliklerine rağmen artırılmamış
olmasıydı (bkz. `tasks/lessons.md`). `templates/base.html`'de `?v=0101`'e
yükseltilip tarayıcı yenilendikten sonra kullanıcı doğruladı: sorun düzeldi.

### Faz 3 — Template migration (dosya dosya, düşük riskliden başla) — BAŞLADI
Öncelik sırası: az Bootstrap class'ı olan → çok olan. Her dosya değişikliği
ayrı görev olarak onaya sunulmalı (CLAUDE.md kırmızı çizgi). Her dosyadan
sonra tarayıcıda görsel doğrulama yapılmalı.
- Grid-only sayfalar önce (sadece container/row/col — risk düşük)
- Sonra btn/card/badge kullanan sayfalar (ax- karşılığı zaten var)
- En son modal/dropdown/form kullanan ağır sayfalar (job_detail.html,
  hangi_test.html, studyroom_detail.html, istatistik araçları)

**ÖNEMLİ BULGU (kullanıcı onayıyla kapsam dışı bırakıldı, ayrıca not):**
`profile_private.html` incelenirken görüldü — "grid-only" kategorisinde
gerçek proje dosyası yok (tek eşleşme `aws/dist/awscli/...` idi, 3. parti
kütüphane, proje template'i değil). Ayrıca component class'ı (btn/card/badge)
migrate edilmiş dosyalarda bile Bootstrap **utility** class'ları (`d-flex`,
`text-white`/`text-muted`, `fw-bold`, `mb-*`/`py-*`/`px-*`, `gap-*`,
`rounded-*`, `shadow-*`, `bg-*`, `border-*`) hâlâ yaygın — bunlar CLAUDE.md'nin
"Bootstrap yalnızca grid için" kuralına göre onaylı değil ve **Faz 4'te
CDN kaldırılınca bunlar da kırılır**, sadece modal/dropdown/form değil.
Karar: Faz 3 şimdilik dar tutuldu (sadece component class migration).
Utility class migration'ı **Faz 4'ten önce ayrı bir alt görev olarak**
ele alınmalı — envanteri henüz çıkarılmadı.

**AYRI BULGU — float buton z-index/konum çakışması (Bootstrap kaldırma
kapsamı dışı):** Kullanıcı bildirdi — sayfa dar ekranda (yarım pencere)
görüntülenince sağ alttaki float butonlar (Destekçi/donate, "AI Asistan",
WhatsApp "Proje hakkında konuşalım") üst üste biniyor, biri diğerini
kapatıyor. Mobil öncelikli ([[feedback_mobile_first]] memory) gözden
geçirilmeli — muhtemelen aynı `position: fixed; bottom/right` offset'i
paylaşıyorlar, responsive stacking/offset eksik. Henüz araştırılmadı,
kök neden dosyası bulunmadı. Ayrı bir görev olarak ele alınacak.

**İlk migrate edilen component-density sıralaması (en düşükten):**
`story_modal_content.html` (1, ama 2 farklı kopyası var — `templates/` ve
`templates/forum/partials/`, senkron değiller), `account_delete.html` (2),
`donation_success.html` (3), `job_list.html` (3), `profile_detail.html` (3).

**Dosya bazlı ilerleme:**
- [x] `forum/templates/forum/account_delete.html` — tek değişiklik:
  `btn btn-danger` → `ax-btn ax-btn--danger` (40. satır). Yeni CSS gerekmedi,
  `.ax-btn--danger` zaten vardı. **Görsel doğrulama TAMAMLANDI** —
  `/account/delete/` sayfasında kullanıcı ekran görüntüsüyle onayladı.
- [x] `forum/templates/forum/donation_success.html` — 3 değişiklik:
  `card`→`ax-card` (9. satır), `card-body` kaldırıldı (10. satır, `p-5`
  zaten padding sağlıyordu), `btn`→`ax-btn` (60. satır, inline gradient
  stili korundu). Utility class'lara dokunulmadı. **Görsel doğrulama
  TAMAMLANDI** — `/donation/success/` sayfasında kullanıcı ekran
  görüntüsüyle onayladı, kart/padding/buton hiç bozulmamış.
- [x] `forum/templates/forum/market/job_list.html` — gerçek envanter todo'daki
  "(3)" tahmininin çok üzerindeydi (23 btn, 8 dropdown, 5 card, 7 badge);
  ikinci bir `forum/templates/forum/job_list.html` daha var ama hiçbir view/
  include onu kullanmıyor (yetim dosya, dokunulmadı, ayrı not). Yapılanlar:
  - Sıralama dropdown'ı (130-141. satır) **Faz 3'ün ilk gerçek Bootstrap JS
    (modal dışı) migrasyonu** — `.ax-dropdown-wrap > [data-ax-dropdown] +
    .ax-dropdown--end` yapısına taşındı; mobilde sağ kenardan taşmaması için
    `--end` varyantı seçildi (varsayılan sol hizalı `.ax-dropdown` trigger
    sağda olduğu için dar ekranda viewport dışına taşardı — Bootstrap'ın
    Popper tabanlı otomatik çakışma düzeltmesinin karşılığı yok, kasıtlı
    seçim). Aktif seçeneği vurgulamak için `base.css`'e yeni
    `.ax-dropdown-item--active` kuralı eklendi.
  - İlan kartı (146-183. satır): `card`/`card-body`/`card-title`/`card-text`
    kaldırıldı, düz `div`/`h5`/`p`'ye indirildi (kullanıcı kararı — `.ax-card`
    kullanılsaydı kendi gradient arka plan/gölge/hover efekti mevcut özel
    inline stille çakışıp görünümü değiştirirdi). `.card`'ın sağladığı
    border-radius inline stile elle eklendi (`border-radius:var(--ax-radius-lg)`),
    yoksa köşeler kare kalırdı.
  - `badge ax-tag--category` → `ax-badge ax-tag--category` (`market.css`'teki
    `.badge.ax-tag--category` seçicisi `.ax-badge.ax-tag--category`'e
    güncellendi — proje genelinde başka hiçbir dosya bu seçiciyi kullanmıyordu).
  - `badge bg-danger/warning bg-opacity-25 text-danger/warning` →
    `ax-badge ax-badge--danger`/`ax-badge--warning` (zaten renk olarak birebir
    eşleşiyor, tasarım sapması yok).
  - Boş-ilan CTA'sı (191-193. satır): `btn btn-info btn-sm rounded-pill` →
    `ax-btn ax-btn--primary ax-btn--sm` (kullanıcı kararı — tasarım sisteminde
    "info" camgöbeği karşılığı yok; renk indigo'ya değişti, pill şekli
    kayboldu, kabul edilen küçük görsel sapma).
  - **Kritik altyapı adımı:** `base.css` canlıda hiç yüklenmiyor — yalnızca
    `static/css/bundle.css` (5 kaynak dosyanın `rcssmin` ile birleştirilmiş
    hâli) yükleniyor (bkz. §26, analizus.md §26). `base.css`'teki yeni
    `.ax-dropdown-item--active` kuralının etkili olması için `bundle.css`
    container içinde yeniden üretildi, `templates/base.html`'deki
    `bundle.css?v=0008` → `?v=0009`'a, `job_list.html`'deki
    `market.css?v=0009` → `?v=0010`'a çekildi. `docker compose exec web
    python manage.py collectstatic --noinput` + `restart web` + `restart
    nginx` çalıştırıldı.
  - **Görsel doğrulama TAMAMLANDI** (mobil öncelik gözetilerek, Playwright ile
    375px + 1280px): dropdown açılıyor, mobilde viewport dışına taşmıyor
    (sağ taşma −24px, yani içeride), aktif seçenek vurgulanıyor; geçici bir
    test ilanı oluşturulup kart görünümü (yuvarlak köşe, rozetler, "1 gün
    kaldı" amber uyarı) ekran görüntüsüyle kontrol edildi, sonra silindi.
    `forum/tests.py -k market` (3 test) yeşil.
- [x] **Gerçek envanter yeniden çıkarıldı (11 Ekim 2026):** Eski "(3)" gibi
  tahminler çoğu dosyada yanlıştı (büyük ölçek farkı) — `class="..."` içindeki
  tam token eşleşmesiyle (ör. "ax-badge" içindeki "badge" alt-dizesini yanlış
  sayan naif `\bword\b` grep'inden farklı olarak) proje genelinde yeniden
  sayıldı. En düşük yoğunluklu 4 dosya bulunup migre edildi:
  - `forum/templates/forum/contact.html` ve `forum/templates/forum/
    gizlilik_politikasi.html` — ikisi de aynı tek buton:
    `btn btn-outline-primary rounded-pill px-4` → `ax-btn ax-btn--outline-primary`
    (birebir var olan karşılık, yeni CSS gerekmedi). **Not:** bu iki dosya
    daha önce "sıfırdan ax-* ile yazıldı, Bootstrap borcu yok" diye not
    düşülmüştü (aşağıdaki temmuz 2026 notu) — bu kısmen yanlışmış, birer
    buton kaçmış; not aşağıda düzeltildi.
  - `forum/templates/forum/partials/_studyroom_founder_card.html` — tek kart
    (`card border-secondary mb-3 p-3`) düz div'e indirildi. **Bulgu:**
    Bootstrap'ın `.border-secondary` utility'si yalnızca `border-color` set
    eder, `.card`'ın sağladığı `border-width/style`'a bağımlıdır — `.card`
    kaldırılınca kenarlık tamamen kaybolacaktı, inline
    `border-width:1px;border-style:solid` eklenerek önlendi. Radius için
    Bootstrap'ın gerçek varsayılanına (`--bs-border-radius` ≈ 6px) daha sadık
    kalmak üzere `--ax-radius-sm` kullanıldı (job_list.html'deki kartta
    kullanılan `--ax-radius-lg` yerine — oradaki 12px halen ekranda sorunsuz
    görünüyor, geriye dönük düzeltilmedi, kapsam dışı).
  - `templates/forum/partials/story_modal_content.html` — tek rozet
    (`badge bg-secondary bg-opacity-25 text-secondary border ...`, nötr
    "kaynak" etiketi) için tasarım sisteminde karşılık yoktu, kullanıcı
    onayıyla `base.css`'e yeni `.ax-badge--neutral` varyantı eklendi
    (`--ax-bg-tertiary`/`--ax-text-secondary`/`--ax-border-default` token'ları).
  - **Yetim dosya bulgusu:** `templates/story_modal_content.html` (templates/
    kökünde, partials/ altında değil) hiçbir view/include tarafından
    kullanılmıyor — `forum/views.py:3158` yalnızca `forum/partials/
    story_modal_content.html`'i render ediyor. Dokunulmadı, ayrı not.
  - `base.css`→`bundle.css` yeniden üretildi (`.ax-badge--neutral` için),
    `bundle.css?v=0009`→`?v=0010`. Görsel doğrulama: iki buton sayfası
    Playwright ile 375px/1280px ekran görüntüsüyle kontrol edildi; founder
    card + story badge, DB'de test verisi olmadığından `render_to_string` ile
    üretilip `bundle.css` bağlanarak ayrı bir önizleme sayfasında kontrol
    edildi (DB'ye dokunulmadı). `forum/tests.py -k "story or studyroom"`
    (21 test) yeşil.
- [x] `forum/templates/forum/topic_detail.html` (2 gerçek eşleşme) — cevap
  formu: `form-control text-white` → `ax-form-control text-white`,
  `btn px-3` (gönder butonu, tamamen özel gradient inline stille) →
  `ax-btn` + `padding-left/right:0.75rem` (eski `px-3`'ün karşılığı, `ax-btn`
  kendi dolgusu farklı olduğu için elle korundu). **Bulgu:** `base.css`'te
  (Faz 1'den, "10. FORM CONTROLS" bölümünden bağımsız, dosyanın sonlarında)
  genel/scope'suz bir `.ax-form-control { min-height: 96px; resize: vertical; }`
  kuralı var — bu tek satırlık (`rows="1"`) cevap kutusunu class değişince
  aniden 96px'e büyütecekti; textarea'nın inline stiline `min-height:38px`
  eklenerek (gönder butonuyla aynı yükseklik) önlendi. Görsel doğrulama:
  local DB'de forum kategorisi/konusu olmadığından (boş seed) tam sayfa
  render edilemedi, form parçası bağımsız bir önizleme sayfasında
  `bundle.css` bağlanarak Playwright ile 375px/1280px kontrol edildi —
  textarea tek satır yüksekliğinde kaldı, gönder butonu hizalı. 90 testin
  tamamı (`forum/tests.py`) yeşil.
- [x] `forum/templates/forum/home.html` (3 gerçek eşleşme) —
  - 2× "VİTRİN" rozeti (`badge bg-warning text-dark`, öne çıkan ilan
    etiketi) → **kullanıcı kararıyla** yeni `.ax-badge--warning-solid`
    eklendi (`ax-btn--warning`'deki aynı solid amber + koyu metin WCAG
    formülü) — mevcut yarı-saydam `ax-badge--warning` kullanılsaydı rozet
    belirgin ölçüde soluklaşıp "öne çıkan" vurgusunu kaybederdi.
  - "Tüm Blog Yazıları" CTA'sı (`btn btn-outline-secondary rounded-pill px-4`)
    → `ax-btn ax-btn--ghost` (job_list.html'deki sıralama butonuyla aynı,
    zaten kurulu outline-secondary↔ghost eşleşmesi, yeni karar gerekmedi).
  - Görsel doğrulama: blog butonu gerçek içerikle (seed'li blog yazıları var)
    doğrudan ekran görüntüsüyle kontrol edildi; VİTRİN rozeti için geçici
    `is_featured=True` bir test ilanı oluşturulup ana sayfada solid
    sarı/koyu-metin görünümü doğrulandı, sonra silindi. 90 test yeşil.
- [x] **Kapsam dışı bırakıldı (kullanıcı kararı) — standalone auth sayfaları:**
  `templates/forum/register.html` incelenirken fark edildi — bu sayfa
  `base.html`'i hiç extend etmiyor, kendi `<!DOCTYPE html>`'i ve kendi
  Bootstrap CDN linkini (+ kendi `bootstrap.bundle.min.js`'ini) yüklüyor.
  Faz 4'ün hedefi yalnızca `base.html`'deki CDN'i kaldırmak — bu sayfa zaten
  ayrı olduğu için Faz 4'ten etkilenmeyecek; modal'ı ax-modal'a taşımak
  `bundle.css`+`ax-modal.js`'i bu sayfaya YENİ bir bağımlılık olarak eklemek
  anlamına gelirdi. Aynı kalıp doğrulandı: `forum/templates/registration/
  login.html` (gerçek Bootstrap component borcu yok, önceki "1" eşleşme
  yanlış pozitifti), `templates/registration/password_reset_{complete,done,
  form,confirm}.html` (hepsi aynı standalone doctype). **Bu 6 dosyaya
  dokunulmadı, migrasyon kapsamı dışında tutulacak** (base.html'e taşınmaları
  ayrı ve çok daha büyük bir karar — sorulmadı).
- [x] `templates/partials/order_payment.html` (3 gerçek eşleşme, 5 farklı
  tarama aracının sipariş sayfasında ortak include) —
  `form-control bg-dark text-white border-secondary` → `ax-form-control`;
  `alert alert-secondary` + elle eklenmiş `text-info` ikon → `ax-alert
  ax-alert--info` (zaten semantik olarak "bilgi" kutusuydu, yeni varyant
  gerekmedi); `btn btn-lg w-100` → `ax-btn ax-btn--lg w-100` (özel gradient
  inline stil korundu). **Gerçek bug bulundu ve düzeltildi:** `.ax-alert`
  `display:flex` olduğu için düz metin + `<strong>{{ email }}</strong>`
  karışımını doğrudan içine koymak, `<strong>`'ı ayrı bir flex item'a
  dönüştürüp dikey kaydırıyordu (Playwright ekran görüntüsünde yakalandı) —
  içerik `.ax-alert__body` ile sarmalanarak düzeltildi, ders `tasks/
  lessons.md`'ye eklendi. Görsel doğrulama: gerçek sipariş sayfası login +
  tamamlanmış arama job'ı gerektirdiğinden, parça bağımsız bir önizleme
  sayfasında `bundle.css` ile 375px/500px ekran görüntüsüyle kontrol edildi
  (DB'ye dokunulmadı). 90 test yeşil.
- [x] `istatistik/templates/istatistik/analiz_hub.html` (3) +
  `templates/tarama_hub.html` (3) — iki hub sayfası kasıtlı olarak farklı
  marka rengi kullanıyor (analiz=yeşil/success, tarama=camgöbeği/info),
  ikisi de tasarım sisteminde yoktu.
  - **Kullanıcı kararıyla kalıcı eklendi:** `--ax-accent-info` (#06b6d4) +
    `--ax-accent-info-hover` token'ları, `.ax-btn--success` (mevcut
    `--ax-accent-secondary` emerald token'ını yeniden kullanır) ve
    `.ax-btn--info` — ikisi de `ax-btn--warning`'deki solid-zemin +
    koyu-metin WCAG AA formülünü izliyor (hesaplandı: beyaz metin hem
    emerald hem camgöbeği zeminde ~2.5-2.8:1 kontrastla AA'yı geçemiyor,
    koyu `#1e293b` metin ikisinde de >5.7:1 ile rahatça geçiyor — primary'nin
    "zemini koyult, beyaz metin kullan" formülü bu iki renk için yetersiz
    kalıyordu). Artık bu "info/success rengi yok" sorusu tekrar çıkmayacak.
  - `btn-outline-light` → `ax-btn--ghost` (yeni karar gerekmedi, kurulu
    örüntü). **Dikkat:** `tarama_hub.html`'de butonlara eklenmiş `text-white`
    utility'si bilerek kaldırıldı — Bootstrap'ın `text-white` kuralı
    `!important` taşıyor, `ax-btn--info`'nun WCAG için zorunlu koyu metnini
    ezip tekrar beyaza çevirip kontrastı bozacaktı.
  - Görsel doğrulama: `/analiz/` ve `/tarama/` sayfaları oturumsuz, gerçek
    içerikle (seed'li araç listeleri) 375px/1280px Playwright ekran
    görüntüsüyle kontrol edildi — her iki hub'ın marka rengi kimliği
    (yeşil / camgöbeği) birebir korundu. 90 test yeşil.
- [x] `forum/templates/forum/about.html` (11. dosya, 12 Ekim 2026) — gerçek
  envanter: 1 `badge` + 3 `btn` (277, 280, 290, 294. satır).
  - 277: `badge` → `ax-badge` (renk zaten inline style'dan geliyordu,
    etkilenmedi; kabul edilen küçük sapma: köşe yuvarlaklığı Bootstrap'ın
    hafif yuvarlağından `.ax-badge`'in tam pil şekline döndü).
  - 290: `btn btn-primary` → `ax-btn ax-btn--primary` (birebir karşılık).
  - 280 + 294 (koşullu): `btn btn-outline-light` → `ax-btn ax-btn--outline-light`
    — bu class proje genelinde 12 dosyada daha var (`how_it_works.html`,
    `my_payments.html`, `post_job.html`, `promote_job_iban.html`,
    `service_promo.html`, `uzman_dizini.html`, `job_detail.html`,
    `base.html` dahil), bu yüzden önceki `tarama_hub.html`'de kullanılan
    kabul-edilebilir-sapma `ax-btn--ghost` yerine `base.css`'e yeni, birebir
    Bootstrap `outline-light` davranışını taklit eden `.ax-btn--outline-light`
    varyantı eklendi (şeffaf + açık kenarlık/metin → hover'da dolu açık
    zemin + koyu metin). **Not:** `tarama_hub.html`'deki eski `ax-btn--ghost`
    kullanımı geriye dönük değiştirilmedi (kapsam dışı) — ileride aynı
    dosyaya dönülürse tutarlılık için `ax-btn--outline-light`'a taşınabilir.
  - `bundle.css` `rcssmin` ile yeniden üretildi, `collectstatic` çalıştırıldı,
    `base.html`'deki `bundle.css?v=0012` → `?v=0013`'e çekildi, `web` restart
    edildi. Görsel doğrulama Playwright ile 375px/1280px'te yapıldı (rozet +
    3 buton, computed style dahil) — sorun yok, konsol/ağ hatası yok, yatay
    taşma yok. 90/90 test (`forum/tests.py`) yeşil.

- [x] `forum/templates/forum/blog/blog_list.html` (12. dosya, 12 Ekim 2026) —
  gerçek envanter: 4 (`form-control`, `form-select`, 2× `btn`), hepsi arama
  kutusu/kategori seçici alanında.
  - 29: `form-control text-white border-end-0` → `ax-form-control ...`
  - 32: `btn px-4` (tamamen inline gradient stille boyanmış gönder butonu) →
    `ax-btn px-4` (inline stil korundu).
  - 37: `btn btn-outline-secondary` → `ax-btn ax-btn--ghost` (`home.html`'de
    kurulmuş outline-secondary↔ghost eşleşmesi tekrar kullanıldı).
  - 111: `form-select bg-dark text-white border-secondary` →
    `ax-form-select ...`.
  - **Gerçek bug bulundu ve düzeltildi:** arama kutusu bir Bootstrap
    `.input-group` içinde — Bootstrap'ın `.input-group>.form-control{flex:1 1
    auto;width:1%;min-width:0}` kuralı yalnız `.form-control` class'ına bağlı;
    class `ax-form-control` olunca bu kural düşüyor, `.ax-form-control`'ün
    kendi `width:100%` kuralı input'u tek başına satıra yayıp butonu +
    "Temizle" linkini alt satıra düşürüyordu (hem 375px hem 1280px'te
    Playwright ile ölçülüp doğrulandı). Dosyanın kendi `<style>` bloğuna
    scoped bir düzeltme eklendi: `.input-group > .ax-form-control{flex:1 1
    auto;width:1%;min-width:0}`. Köşe yuvarlaklığı (`.input-group`'un yapısal
    `:not(:first-child)`/`:not(:last-child)` kuralları, class'tan bağımsız)
    etkilenmedi, görsel olarak sorunsuz (ekran görüntüsüyle doğrulandı).
  - Yeni CSS/`bundle.css` değişikliği gerekmedi (kullanılan tüm ax- class'lar
    zaten vardı) — yalnız dosyanın kendi `<style>` bloğuna 1 kural eklendi,
    `docker compose restart web` yeterliydi.
  - Görsel doğrulama Playwright ile 375px/1280px tam sayfa + arama kutusu
    close-up (filtre uygulanmış durum dahil) — sorun yok, konsol hatası yok
    (yalnızca ilgisiz PWA service-worker scope uyarısı, bu dosyadan bağımsız).
    `forum/tests.py` 90/90 yeşil.

- [x] `forum/templates/forum/search_results.html` (13. dosya, 25 Ekim 2026) —
  gerçek envanter: 3× `btn` + 1× `card`/`card-body`.
  - 23: `btn btn-outline-info rounded-pill px-4` → `ax-btn ax-btn--outline-info
    px-4`. **Kullanıcı kararıyla yeni `.ax-btn--outline-info` eklendi**
    (`base.css`, `outline-primary` formülüyle aynı: şeffaf zemin + camgöbeği
    metin/kenarlık, hover'da `color-mix` ile %10 dolgu) — solid `ax-btn--info`
    (12 Ekim) zaten vardı ama outline hali yoktu, bu dosyada 3 kez aynı
    semantik renk kullanıldığı için ghost'a düşmek yerine kalıcı varyant
    tercih edildi.
  - 92 + 104: `btn btn-info rounded-pill px-4 mt-3` → `ax-btn ax-btn--info
    px-4 mt-3` (birebir karşılık, zaten vardı).
  - 68-70: kullanıcı kartı (`card h-100 text-decoration-none user-result` +
    `card-body d-flex align-items-center gap-3`) — `.ax-card` kullanılmadı
    (job_list.html'deki ilan kartı kararıyla aynı gerekçe: `.ax-card`'ın
    kendi padding/hover-transform'u `.user-result`'ın bespoke inline
    arka plan/kenarlık + hover stiliyle çakışır, ayrıca statik bir kart
    olmasına rağmen istenmeyen bir "tıklanabilir" hover efekti eklerdi).
    Düz `div`/`a`'ya indirildi: `<a>`'ya kaybolan `.card`'ın `display:flex`
    davranışı elle eklendi (yoksa `h-100` ve grid hizası bozulurdu),
    `border-radius:var(--ax-radius-sm)` (founder-card kararındaki gibi
    Bootstrap'ın gerçek 6px varsayılanına sadık), `card-body`'nin kaybettiği
    `width:100%`/`padding:1rem`'i manuel eklendi.
  - `base.css`→`bundle.css` yeniden üretildi (`.ax-btn--outline-info` için),
    `collectstatic` + `web`/`nginx` restart edildi, `base.html`'deki
    `bundle.css?v=0014`→`?v=0015`. **Not:** 27 Eylül'den beri whitenoise
    manifest hash'li dosya adı ürettiği için `?v=` artık zorunlu değil
    (zararsız alışkanlık, analizus.md §26).
  - Görsel doğrulama: gerçek seed'li kullanıcılarla (`?q=fatma` eşleşen
    kullanıcı, `?q=zzz...` sonuç yok, boş sorgu min-karakter uyarısı — 3
    farklı buton dalı) Playwright 375px/1280px, konsol hatası yok.
    `forum/tests.py` 104/104 yeşil.
- [x] `forum/templates/forum/verification_pending.html` (14. dosya,
  25 Ekim 2026) — gerçek envanter: 2× `btn` + 1× `card`/`card-body` +
  1× `alert`. Yeni CSS gerekmedi (tüm hedef ax- class'lar zaten vardı).
  - `card border-0 shadow-lg` (tamamen inline bg/border/radius 16px ile
    boyalı) → `card` kaldırıldı, `border-0 shadow-lg` (utility, kapsam
    dışı) + mevcut inline stil aynen kaldı; `.ax-card` kullanılmadı (statik,
    tıklanamayan bir kart, `.ax-card`'ın hover transform'u anlamsız olurdu).
  - `card-body p-5 text-center` → `card-body` kaldırıldı, `p-5` zaten
    Bootstrap'ın card-body padding'ine eşdeğer boşluğu sağlıyordu
    (donation_success.html'deki aynı desen).
  - `alert border-0 rounded-3` (inline `rgba(99,102,241,.1)` bg) →
    `ax-alert ax-alert--info` (renk tonu birebir eşleşiyor, yeni varyant
    gerekmedi); ikon `ax-alert__icon` + metin `ax-alert__body`'e sarıldı
    (order_payment.html'deki flex-kayması bug'ının tekrarını önlemek için);
    ikonun özgün camgöbeği rengi inline `color:var(--ax-accent-info)` ile
    korundu (ax-alert'in varsayılan gövde rengi `--ax-text-primary`, ikonu
    da aynı renge düşürürdü).
  - `btn btn-primary btn-lg rounded-pill` → `ax-btn ax-btn--primary
    ax-btn--lg`; `btn btn-outline-secondary rounded-pill` → `ax-btn
    ax-btn--ghost` (ikisi de birebir kurulu karşılık, `rounded-pill`
    önceki dosyalarda olduğu gibi düşürüldü).
  - Görsel doğrulama: view `@login_required` + e-posta doğrulanmamış
    profil gerektiriyor — geçici bir test kullanıcısı (`Client.force_login`
    + `Profile(email_verified=False)`) ile gerçek URL render edilip
    `staticfiles/` altına yazıldı, nginx üzerinden (`https://localhost/
    static/preview_verification.html`, self-signed sertifika) Playwright
    375px/1280px ile kontrol edildi, sonra hem test kullanıcısı hem önizleme
    dosyası silindi (DB'ye kalıcı iz bırakılmadı). Kart/alert/butonlar
    birebir orijinal görünümde, konsol hatası yok. `forum/tests.py`
    104/104 yeşil.
  - **Yan not (araç/ortam):** localhost:8000'de bağımsız bir
    `manage.py runserver` sürecinin (Docker dışı) çalıştığı görüldü —
    §26'daki "hangi süreç hangi DB'yi kullanıyor" tuzağına girmemek için
    tüm doğrulama `docker compose` + nginx'in gerçek portu (443, self-signed
    https) üzerinden yapıldı, o bağımsız sürece dokunulmadı.

- [x] `forum/templates/forum/category_topics.html` (15. dosya, 25 Ekim 2026) —
  gerçek envanter: 1× `btn` + 5× `badge` + 1× `card`/`card-body`. Yeni CSS
  gerekmedi (tüm hedef ax- class'lar zaten vardı).
  - `btn btn-primary rounded-pill px-4 py-2 fw-bold shadow-lg border-0`
    (inline gradient) → `ax-btn ax-btn--primary` + aynı utility'ler
    (`rounded-pill` düşürüldü, `ax-btn` zaten büyük radius).
  - Çalışma odası rozeti (`badge fw-normal py-2 px-3`, inline amber) →
    `ax-badge` + aynı utility'ler.
  - `card border-0 shadow-lg` (tamamen inline glassmorphism — `--glass-bg`,
    `backdrop-filter`, `border-radius:20px`) + `card-body p-0` → ikisi de
    kaldırıldı, düz `div`'e indirildi (`.ax-card` kullanılmadı — zaten
    tüm görsel kimlik inline stilden geliyordu, `.ax-card`'ın kendi
    padding/hover'ı anlamsız çakışma yaratırdı).
  - "Sabit" rozeti (`badge bg-warning text-dark`) → `ax-badge
    ax-badge--warning-solid` (home.html/category_topics ailesinde kurulu
    karşılık).
  - Etiket rozetleri (`badge rounded-pill`, inline `tag.color`) → `ax-badge`
    (`rounded-pill` düşürüldü, `.ax-badge` zaten tam pil şekilli).
  - Kullanıcı adı rozeti (`badge bg-secondary bg-opacity-25 text-info`) →
    `ax-badge ax-badge--neutral` (kabul edilen küçük sapma: metin rengi
    camgöbeğinden nötr griye döndü).
  - "Kilitli" rozeti (`badge bg-danger`, solid kırmızı) → `ax-badge
    ax-badge--danger` (kabul edilen küçük sapma: solid kırmızı zemin
    yarı saydam kırmızı zemine döndü — job_list.html'deki
    `bg-danger bg-opacity-25` örneğinden farklı olarak bu zaten saydam
    DEĞİLDİ, ama etki çok küçük/düşük görünürlüklü bir etiket olduğu için
    kabul edildi).
  - **Not:** `table table-hover table-dark table-borderless` dokunulmadı —
    migrasyonun izlenen envanter listesinde (`btn`/`card`/`badge`/
    `dropdown`/`modal`/`alert`/`form-control`/`form-select`) `table` hiç
    yer almıyor, kapsam dışı.
  - Görsel doğrulama: geçici `Section`/`Category`/2 `Topic` (biri sabit+
    etiketli, biri kilitli) + 1 aktif `StudyRoom` oluşturulup gerçek URL
    (`/forum/<slug>/`) render edildi, Playwright 375px/1280px ile kontrol
    edildi (tüm 5 rozet + buton + kart doğru görünüyor), sonra `Section`
    cascade silme ile tüm geçici veri (kategori/konu/oda) + test kullanıcısı
    temizlendi. `forum/tests.py` 104/104 yeşil.
  - **Yetim dosya bulgusu:** aynı düşük grup listesindeki
    `forum/templates/forum/section_detail.html` hiç render edilmiyor
    (`views.section_detail` artık yalnızca kalıcı yönlendirme yapıyor) —
    migrasyon kapsamından çıkarıldı, yukarıdaki envanter notuna işlendi.

- [x] `forum/templates/forum/market/edit_job.html` +
  `forum/templates/forum/market/post_job.html` (16-17. dosyalar,
  25 Ekim 2026) — **kullanıcı onayıyla birlikte ele alındı** çünkü ikisi de
  `forum/forms.py`'deki aynı `JobPostForm`'u kullanıyor; formun
  `form-control`/`form-select` class'ları şablonda değil Python'da tanımlı.
  - `forum/forms.py` — `JobPostForm.Meta.widgets` (title/description/
    budget_max/expected_duration) `form-control` → `ax-form-control`,
    `category_choice` alanının `form-select` → `ax-form-select` (ikisi de
    `bg-dark text-light border-secondary` utility'lerini korudu). Aynı
    dosyadaki `ProposalForm` (job_detail.html'in teklif formu, "Ağır" grup,
    henüz migre edilmedi) kasıtlı olarak dokunulmadı.
  - Her iki şablonda da `card border-0 shadow-sm` (inline bg/border) +
    `card-header bg-transparent ...` + `card-body p-4` → `card`/`card-header`/
    `card-body` kaldırıldı, düz `div`'lere indirildi. **Not:** `card-header`
    migrasyonun izlenen envanter listesinde (`btn`/`card`/`card-body`/
    `badge`/`dropdown`/`modal`/`alert`/`form-control`/`form-select`) hiç
    yer almıyordu ama aynı mantıkla `card-body` gibi ele alındı. Bootstrap'ın
    kaybolan varsayılan radius'u (~6px) `border-radius:var(--ax-radius-sm)`
    ile elle eklendi (ikisinde de inline'da yoktu, founder-card kararındaki
    gibi); header+body tek çocuklu değil iki çocuklu ama ikisi de blok
    (div), `display:flex` gerekmedi (arama kartındaki `<a>` durumundan
    farklı).
  - **Gerçek bug bulundu ve düzeltildi:** `forum/templates/forum/market/
    _job_rules.html` (her iki dosyada da include) `ax-alert ax-alert--warn`
    kullanıyordu — doğrusu `ax-alert--warning`, `--warn` hiçbir CSS'te
    tanımlı değildi, kutu tamamen stilsiz (şeffaf zemin, görünmez kenarlık)
    render oluyordu. Düzeltildi. **Aynı yazım hatası
    `forum/templates/forum/market/job_detail.html:83`'te de var** ("Ağır"
    grup, bu turda dokunulmadı) — ayrı not olarak işlendi, aşağıda.
  - `edit_job.html`'deki form hata kutusu (`alert alert-danger`) →
    post_job.html'de zaten kurulu olan `ax-alert ax-alert--danger` +
    `ax-alert__icon`/`ax-alert__body` yapısına taşındı (işlevsel fark
    eklenmedi, yalnızca görsel).
  - `edit_job.html`: `btn btn-warning` → `ax-btn ax-btn--warning`;
    `btn btn-outline-secondary` → `ax-btn ax-btn--ghost`.
  - `post_job.html`: `btn btn-outline-light` → `ax-btn ax-btn--outline-light`;
    `btn btn-info` → `ax-btn ax-btn--info`.
  - **Kullanıcı kararıyla yeni `.ax-alert--cyan` eklendi:** post_job.html'deki
    süre bilgi kutusu (`alert alert-info`, gerçek Bootstrap camgöbeği
    `#0dcaf0`) mevcut `.ax-alert--info`'ya taşınsaydı renk MORA (`--ax-accent-primary`)
    dönerdi — o varyant adına rağmen primary renkli (verification_pending.html'deki
    gibi zaten indigo olan kutularla eşleşmek üzere tasarlanmış). Yeni
    `.ax-alert--cyan` (`--ax-accent-info` token'ı) eklendi, orijinal
    camgöbeği birebir korundu. **Aynı camgöbeği `alert-info` kalıbı
    `my_jobs.html` (düşük grup, sırada) ve `referral_dashboard.html` (orta
    grup) içinde de var** — oralarda da bu yeni varyant kullanılacak.
  - `base.css`→`bundle.css` yeniden üretildi (`.ax-alert--cyan` için,
    `.ax-btn--outline-info` önceki turdan zaten vardı), `collectstatic` +
    `web`/`nginx` restart, `bundle.css?v=0015`→`?v=0016`.
  - Görsel doğrulama: geçici test kullanıcısı (e-posta doğrulanmış) +
    geçici `FreelanceJob` (`approved_at` verilerek — [[feedback_...]]
    FreelanceJob.save() yeniden-yayın tuzağına girilmedi) ile her iki
    gerçek URL (`/market/new/`, `/market/job/<pk>/edit/`) render edilip
    Playwright 375px/1280px ile kontrol edildi (kart radius, uyarı/bilgi
    kutuları, form alanları, butonlar hepsi doğru), sonra kullanıcı+ilan
    silindi (cascade). `forum/tests.py` 104/104 yeşil.

- [ ] **(25 Ekim 2026) Yan bulgu — `ax-alert--warn` yazım hatası, kapsam dışı:**
  `forum/templates/forum/market/job_detail.html:83` aynı `ax-alert
  ax-alert--warn` hatasını taşıyor (tanımsız varyant, kutu stilsiz
  görünüyor). `job_detail.html` "Ağır" migrasyon grubunda (48 class,
  en ağır dosya), o dosyaya geçilince düzeltilecek; o zamana kadar canlıda
  stilsiz kalmaya devam edecek (düşük önemli, görünür ama kritik değil).

- [x] `forum/templates/forum/my_payments.html` +
  `forum/templates/forum/market/_review_section.html` (18-19. dosyalar,
  25 Ekim 2026) — yeni CSS gerekmedi.
  - `my_payments.html`: `card bg-dark border-secondary shadow-sm` → `card`
    kaldırıldı (`bg-dark`/`border-secondary`/`shadow-sm` utility, kapsam
    dışı, aynen kaldı), kaybolan radius `border-radius:var(--ax-radius-sm)`
    ile eklendi. `card-header border-secondary bg-transparent py-3` →
    `card-header` kaldırıldı — **bulgu:** `.border-secondary` yalnız
    border-color verir, `card-header`'ın sağladığı border-width olmadan
    görünmez kalırdı (founder-card'daki aynı tuzak), elle
    `border-bottom-width:1px;border-bottom-style:solid` eklendi.
    `card-body p-0` → kaldırıldı (zaten sıfır dolgu, kayıp yok). 3 durum
    rozeti (`badge bg-success/warning/danger bg-opacity-25 text-* border
    border-* border-opacity-25`) → `ax-badge ax-badge--success/warning/
    danger` + **`border border-* border-opacity-25` utility'leri bilerek
    korundu** (ax-badge--* kendi border'ını tanımlamıyor, Bootstrap utility
    hâlâ yüklü olduğu için halka aynen kaldı, yeni CSS gerekmedi).
    `btn btn-sm btn-outline-light` → `ax-btn ax-btn--sm ax-btn--outline-light`.
  - `_review_section.html`: 3 kart (`card border-0 shadow-sm`, tamamı
    inline bg'li) → `card` kaldırıldı + `border-radius:var(--ax-radius-sm)`
    eklendi; ikisi `card-body py-2 px-3` (utility zaten vardı, kayıpsız
    kaldırıldı), biri çıplak `card-body` (hiç padding utility'si yoktu) →
    kaldırılıp yerine `padding:1rem` eklendi (search_results.html'deki
    kullanıcı kartı kararıyla aynı mantık). `form-control bg-dark text-white
    border-secondary` → `ax-form-control ...`. `btn btn-warning btn-sm` →
    `ax-btn ax-btn--warning ax-btn--sm`.
  - Görsel doğrulama: `my_payments.html` için geçici kullanıcı + 3 durumlu
    (başarılı/bekliyor/başarısız) `JobPayment` ile gerçek URL (`/my-payments/`)
    render edildi; `_review_section.html` `job_detail.html`'in include'u
    olduğu ve o dosya henüz migre edilmediği için `render_to_string` ile
    bağımsız (Bootstrap CDN + bundle.css bağlı) önizleme sayfasında iki
    senaryo (onaylı değerlendirme listesi + değerlendirme formu) kontrol
    edildi. Playwright 375px/1280px, konsol hatası yok, sonra tüm geçici
    kullanıcı/ilan/ödeme/değerlendirme kayıtları silindi. `forum/tests.py`
    104/104 yeşil.

**11 Ekim 2026 oturumu kapandı — `main`'e alındı:** Yukarıdaki 7 commit
(`87c8e26`..`58f52d7`) `dev`'den `main`'e `--no-ff` merge edildi (merge
commit `1e54739`), `origin/main`'e push edildi — GitHub Actions otomatik
Hetzner deploy'u tetikleyecek (migration yok, yalnız template/CSS/docs,
yedek gerekmedi). `dev` kendi uç noktasında (`58f52d7`) bırakıldı, merge
commit'i dev'e fast-forward etmekten kaçınıldı (gereksiz). Bu oturumun
özeti `analizus.md`'nin "Geçmiş Turlar (Kronoloji)" bölümüne de işlendi
(§27), offset tablosu (`CLAUDE.md`) +47 satır kayması için güncellendi.

**Not (temmuz 2026, DÜZELTİLDİ 11 Ekim 2026) — yeni sayfalar envanteri
büyütmedi:** Bu oturumda oluşturulan `forum/templates/forum/contact.html`
(İletişim landing page) ve `forum/templates/forum/gizlilik_politikasi.html`
(KVKK sayfası) sıfırdan `ax-*` sistemiyle yazıldı — migrasyon kapsamına
eklenecek yeni Bootstrap component borcu yok ~~**(yanlış çıktı — her ikisinde
de birer `btn btn-outline-primary rounded-pill px-4` kaçmıştı, 11 Ekim 2026'da
Faz 3 kapsamında migre edildi, yukarı bkz.)**~~. Tek istisna: KVKK sayfasındaki
tablo ilk halde `table table-dark table-borderless` ile yazılmıştı, aynı
oturumda fark edilip (`table-dark`'ın `--bs-table-bg`/`--bs-table-color`
değişkenleri inline satır renkleriyle çakışıp okunaksız görünüyordu)
`.ax-kvkk-table`'a taşındı.

**Not (temmuz 2026) — cache-busting dersi tekrar uygulandı:** Navbar logosuna
eklenen "Analizus" yazısının puntosu `navbar.css`'te iki kez büyütüldü, ama
`templates/base.html:93`'teki `?v=0103` versiyon string'i ilk seferinde
artırılmayı unutuldu — kullanıcı production'da değişikliği göremeyince fark
edildi, `?v=0104`'e çekilip düzeltildi. Bu, §26'daki "CSS değişikliği
production'da görünmüyor" hatasının canlı bir tekrarı; her `static/css/*.css`
değişikliğinde ilgili `<link>` versiyon string'inin de artırılması gerektiği
bir kez daha teyit edildi.

### Faz 4 — Bootstrap CDN'i kaldır
`base.html`'den `bootstrap.min.css` + `bootstrap.bundle.min.js` linklerini
sil. Tüm sayfalarda regresyon taraması (özellikle modal/dropdown/form
davranışları).

### Faz 5 — Temizlik
Kullanılmayan geçiş dönemi shim'leri varsa kaldır.

## Riskler
- Modal/dropdown JS davranışı görsel olarak sessiz kırılabilir (constructor
  hatası fırlatmaz, sadece tıklama işe yaramaz) — her migration adımından
  sonra manuel tıklama testi şart
- Form control stilleri (`form-control`, `form-select`) hem stat hem
  survey/analiz formlarında yoğun kullanılıyor — ax- karşılığı görsel olarak
  input/select native davranışını (autofill, focus ring, disabled state)
  bozmamalı
- 100+ dosyalık migration tek PR'da değil, birden fazla oturuma yayılmalı

## Sıradaki adım
Faz 1 ve 2 TAMAMLANDI. Faz 3 sürüyor — 19 dosya migre edildi (yukarı bkz.
"Dosya bazlı ilerleme"; son yedisi 25 Ekim 2026: `search_results.html`,
`verification_pending.html`, `category_topics.html`, `edit_job.html`,
`post_job.html`, `my_payments.html`, `_review_section.html`). **Güncel
envanter yukarıda** ("Güncel envanter — 11 Ekim 2026 taraması", 25 Ekim
notuyla güncellendi) — düşük grup 16 dosyaya indi (1'i, `section_detail.html`,
yetim/render edilmeyen dosya olduğu için kapsam dışına alındı). Sıradaki
adaylar aynı düşük yoğunluklu grup (`forum_index.html`, `footer.html`
partial'ı, `bibliometrics/order.html` vb., gerçek ~8-19 class). **Dikkat:**
`my_jobs.html` ve `referral_dashboard.html` (orta grup) aynı camgöbeği
`alert-info` kalıbını taşıyor — oraya geçildiğinde bugün eklenen
`.ax-alert--cyan` kullanılacak. Her dosya için: gerçek Bootstrap class'larını
oku → ax- karşılığı yoksa (yeni renk/varyant vb.) kullanıcıya sor → uygula
→ `bundle.css` gerekiyorsa yeniden üret (whitenoise hash'li ad ürettiği
için `?v=` artırmak artık kozmetik, ama alışkanlık korunuyor) → Playwright
ile mobil+masaüstü görsel doğrula → pytest çalıştır → `todo.md` güncelle →
commit. Faz 4 (CDN kaldırma) için önce (1) bu dosyalar bitmeli, (2) hiç
başlanmamış Bootstrap **utility class** envanteri çıkarılıp ayrı ele
alınmalı.

**Deploy notu:** Bu migration'ın tüm adımları yalnızca `dev` branch'ine push
edilecek. `main`'e (Hetzner/prod) kullanıcı açıkça "merge et" demeden
geçilmeyecek — bkz. genel proje kuralı (memory: `git_workflow`, `dev_first`).

---

# Homepage'e 3. Hero Seçeneği: "Bir Projem Var" (fikir aşaması)

**Durum:** Sadece fikir — henüz uygulanmadı, kullanıcı "todo'ya yaz ve bırak"
dedi. (Temmuz 2026)

## Fikir
Homepage'deki iki taraflı pazar yeri yönlendirmesine ("Analiz Yaptırmak
İstiyorum" / "Uzman Olarak Katılmak İstiyorum") üçüncü bir seçenek eklemek:
"Bir Projem Var..." → mevcut `/proje-talebi/` sayfasına (kurumsal danışmanlık
talep formu) yönlendiren bir kart/şerit.

## Teknik bulgular
- İki mevcut kart `forum/templates/forum/home.html:257-341` içinde, `row g-4`
  içinde iki `col-lg-6` — her biri özel SVG illüstrasyon, özellik listesi,
  kategori etiketleri, çoklu CTA içeriyor (zengin/karmaşık içerik).
- Kart shell'i `static/css/home_sections.css:71` — `.ax-market-card` (ortak
  gövde) + `.ax-market-card--demand`/`--supply` (üst renkli çizgi varyantları,
  indigo/amber). Üçüncü `.ax-market-card--project` varyantı (`--ax-accent-secondary`
  yeşili ile) düşük riskli, küçük bir CSS eklemesi olur.
- `/proje-talebi/` zaten var (`forum/views.py: proje_talebi`, "Projenizi
  Anlatın, Size Uygun Uzmanı Bulalım" başlığı) — kurumsal/şirket odaklı.
  **Dikkat:** "Analiz Yaptırmak İstiyorum" kartıyla hedef kitle örtüşmesi
  olabilir (ikisi de "biri benim için analiz yapsın" diyor) — uygulamaya
  geçilirken bu ayrım netleştirilmeli (örn. proje_talebi = kurumsal/resmi
  teklif süreci, mevcut kart = bireysel/hızlı eşleşme).

## Önerilen yaklaşım (kullanıcıya sunuldu, karar bekliyor)
İki mevcut kart hiç değişmeden kalsın (zaten dönüşüm sağlıyorlar, riske
atılmamalı). Altına tam genişlikte, sade/yatay bir üçüncü şerit eklensin —
büyük SVG yok, kısa açıklama + tek CTA (`/proje-talebi/`), yeşil
(`--ax-accent-secondary`) vurgusuyla diğer ikisinden ayrışır. **Reddedilen
alternatif:** 3 eşit kolon (`col-lg-4`) — mevcut zengin kartların
küçültülmesini gerektirir, çalışan/dönüşüm sağlayan elemanlara dokunma
riski taşır.

## Sıradaki adım
Kullanıcı ne zaman uygulamaya geçmek isterse haber verecek; o zaman hedef
kitle ayrımı netleştirilip yukarıdaki yaklaşımla (veya kullanıcının o an
tercih edeceği alternatifle) uygulanacak.

---

# Claude API ile Akademik Tarama Entegrasyonu (fikir aşaması)

**Durum:** Sadece fikir/araştırma notu — henüz plan/onay yok. (Temmuz 2026)

## Kaynak
LinkedIn'de görülen "Claude Science" paylaşımı aslında Claude'un agentic
tool use ile yaptığı bir sistematik literatür taraması: PubMed E-utilities'den
veri çekme, LLM+kural tabanlı hibrit tarama, kod yürütme ile PRISMA diyagramı/
bibliyometrik grafik üretimi, Crossref'ten DOI doğrulama.

## Fikir
Bu yeteneği platformun mevcut "akademik tarama" ve "bibliyometri"
modüllerine (analizus.md §13-15) eklemek.

## Önerilen mimari (taslak)
- **Managed Agents değil, Claude API + tool use** — mevcut Django job/polling
  altyapısına (Celery, S3, `result_data` JSON kaydı) entegre olması ve tam
  backend kontrolü için
- Custom tool: `pubmed_search` (E-utilities çağrısı), `crossref_verify_doi`
- Server-side `code_execution` tool: PRISMA diyagramı + bibliyometrik
  grafikler (matplotlib, mevcut istatistik pipeline'ıyla aynı mantık)
- Hibrit tarama: önce ucuz kural tabanlı filtre, belirsiz kalanlar Claude'a
  (maliyet kontrolü)
- Sonuç: CSV + figür + referans listesi, mevcut polling/job desenine (§12)
  uyacak şekilde

## Tradeoff notu
Managed Agents kullanılırsa ajan döngüsü/konteyner Anthropic tarafında
barınır (daha az backend kodu) ama mevcut Celery/polling mimarisiyle
entegrasyonu daha zor ve ekstra maliyet/karmaşıklık getirir.

## Sıradaki adım
Hangi modüle ekleneceği netleşmedi (mevcut akademik tarama mı, yeni özellik
mi). Karar verilmeden somut plana (dosyalar, endpoint, migration gerekip
gerekmediği) geçilmeyecek.

---

# Site Geneli "Sıfır Kuralı" (Zero-State Sigortası)

**Durum:** TAMAMLANDI (12 Temmuz 2026, commit `b39307c`). Kaynak prompt
`~/Desktop/analizus_sifir_kurali_prompt.md`. Faz 1 envanteri çıkarıldı+onaylandı,
Faz 2 uygulandı (ana sayfa 5 sayaç + `has_any_stats` grup kontrolü, uzman kartı
"0 tamamlanan proje" satırı, "Akademik Haberler" placeholder kaldırıldı,
Gündemdeki Tartışmalar+Akademik Haberler layout bütünlüğü, /hakkimizda/ "Ekip ve
Güven" bölümü), Faz 3'te 9 smoke test eklendi (`forum/tests.py`). /market/ ve
/proje-talebi/ zaten kurala uygun çıktı (yeni iş gerekmedi). Aşağıdaki eski not
artık geçmiş kayıt olarak kalıyor:

## Amaç
Değeri 0 olan hiçbir güven metriği ("0 tamamlanan analiz", "0 aktif uzman" vb.)
ve içi boş hiçbir vitrin bölümü ziyaretçiye gösterilmeyecek. Gerekçe: dev DB
boşluğu değil, canlının doğal dalgalanması (gece 03:00 çevrimiçi uzman
gerçekten 0 olabilir) — "boş dükkân" izlenimini önlemek.

## Protokol (kullanıcının vurguladığı 3 kritik nokta)
1. **Kuralı tanımla, yerleri saydırma.** Talimat sabit bir liste değil: Faz 1
   `grep` ile TÜM template'leri tarayıp tam bir envanter tablosu çıkarır
   (Template · Bölüm · Metrik/Koleksiyon · Mevcut davranış · Önerilen işlem ·
   Kategori), onay alınmadan tek satır değiştirilmez. Bilinen 8-9 aday
   (ana sayfa `ax-stats-section`, uzman vitrini kart içi satırlar, "Akademik
   haberler yakında" şeridi, /proje-talebi/ stats bar, /market/ sayaç üçlüsü,
   /hakkimizda/ "Henüz uzman kadro eklenmedi.") başlangıç noktası, liste
   bunlarla SINIRLI değil — asıl risk modelin kapsamı kendiliğinden
   genişletmesi; envanter+onay kapısı bunu keser.
2. **İstisnayı ilkeyle tanımla, örnekle sabitle — "davet vs itiraf" ayrımı.**
   Davet (bilinçli tasarlanmış CTA içeren boş-durum metni, ör. market'teki
   "İlk analiz işini sen tamamla…") KORUNUR; itiraf ("Henüz uzman kadro
   eklenmedi." gibi) GİZLENİR. Gri kalan her örnek envanterde "karar gerekli"
   işaretlenip kullanıcıya sorulacak.
3. **Yan etkileri kurala bağla.** Bir öğe gizlenince grid/flex kırılmamalı
   (7 sayaçtan 3'ü gizlenince kalan 4'ün doğal dağılması); bir sayaç
   grubundaki TÜMÜ 0 ise kapsayıcı (şerit/başlık dahil) da gizlenir; yeni DB
   sorgusu YASAK — "hepsi sıfır mı" kontrolü mevcut cache'li değerlerden
   türetilen tek bir boolean ile yapılır; parantezli `{% if %}` yasağı
   (analizus.md §26) geçerli.

## Fazlar (kaynak promptta tanımlı)
- Faz 1 — Envanter (uygulama yok, sadece rapor + onay)
- Faz 2 — Uygulama (template `{% if %}`, gerekirse tek boolean context değişkeni)
- Faz 3 — Test + Teslim (0/>0 smoke testleri, migration beklenmiyor)

## Sıradaki adım
Kullanıcı başlamamı istediğinde `analizus_sifir_kurali_prompt.md` içeriğiyle
Faz 1'i (envanter) çalıştırıp tabloyu onaya sunacağım.

---

# Merge Öncesi Son Süpürme (analizus_son_supurme_prompt.md)

**Durum:** TAMAMLANDI — Madde 1-11'in tümü bitti (13 Temmuz 2026). `dev`→`main`
merge de yapıldı (31 Temmuz 2026 itibarıyla iki branch aynı commit'te,
`9b6f58d`). Merge sonrası hatırlatmalardan `feature_agentic_landing` flag'inin
prod'da elle açılıp açılmadığı DOĞRULANMADI — sıradaki oturumda kontrol
edilmeli (bkz. Madde 10 deploy notu).
Kaynak: `~/Desktop/analizus_son_supurme_prompt.md`. Yeni oturumda önce bu dosya
+ bu bölüm okunmalı; `analizus_son_supurme_prompt.md`'nin ORİJİNAL Madde 1
metni artık güncel değil (aşağıdaki kararlarla değişti), bu yüzden bu bölüm
esas alınmalı.

## Tamamlananlar (commit sırasıyla)

- **Madde 1 (huni parametreleri)** — `cd84461`. Tableau CTA metni "Proje Talebi
  Oluştur"a çevrildi; bibliometrik ön-seçim için `ANALYSIS_CHOICES`'a
  `('bibliometric', 'Bibliyometrik Analiz')` eklendi (migration `0147`, no-op
  AlterField). `proje_talebi` view artık `?type=` GET param'ını da okuyor.
  **Karar (kullanıcı onaylı):** bibliometri istatistiksel analiz sayılmadı,
  `statistics` seçeneği yeniden kullanılmadı — ayrı seçenek açıldı.
- **Madde 2 (Sıfır Kuralı)** — `b39307c`. Yukarıdaki bölüme taşındı.
- **Madde 3 (footer tutarsızlığı)** — iş YOK, zaten çözülmüştü (footer tek
  partial, `{% url 'analiz_home' %}` kullanıyor, hardcode `/istatistik/` yok).
- **Madde 4 (forum boş-durum sızıntısı)** — iş YOK, zaten çözülmüştü (`#noResults`
  zaten `d-none` ile başlıyor, JS mantığı zaten doğruydu).
- **Madde 5 (OG override + meta)** — `d73ab72`. 8 hedef sayfaya
  og_title/og_description/twitter_title/twitter_description eklendi.
  **Önemli bulgu:** `/bibliometrics/` misafir kullanıcı için `landing.html`
  değil, PAYLAŞILAN `templates/service_promo.html` render ediyor (6+ istatistik
  araç sayfası da aynı şablonu kullanıyor). Asıl düzeltme oraya, `promo_description`
  context değişkeninden yapıldı — bonus: diğer araç sayfaları da özgün
  og:description kazandı.
- **Madde 6 (dev noindex middleware)** — iş YOK, zaten vardı
  (`forum/middleware.py::NoIndexMiddleware` + `settings.IS_PRODUCTION`).
- **Madde 7a (bibliometri örnek çıktılar + OpenAlex köprüsü)** — `2029ce9`.
  Galeri ve OpenAlex ters köprüsü zaten
  vardı; eklenen tek şey hero altı "OpenAlex'te tarama mı yaptın?" bandı
  (`promo_openalex_bridge` context bayrağı, yalnızca bibliometride true).
  **Karar (kullanıcı onaylı):** galeri kartları spec'in istediği 5 başlıkla
  (Anahtar Kelime Eş-Oluşum Ağı, Anahtar Kelime Zaman Trendi vb.) DEĞİL,
  `static/img/`'de gerçekten var olan 6 görselin gerçek içeriğine uygun
  başlıklarla kuruldu (Yayın Trendi, Anahtar Kelime Bulutu, Yazar İşbirliği
  Ağı, Atıf Analizi & H-index, Araştırma Boşluğu Haritası, Lotka Kanunu) —
  bu zaten `bibliometrics/views.py`'de mevcuttu, değiştirilmedi.
- **Madde 7b (Tableau facade)** — `4ebaa7e`. Poster+buton facade UI önceki
  turda zaten kuruluydu, ama `tableau.embedding.3.latest.min.js` script'i
  `extra_js` block'unda koşulsuz (sayfa yüklenir yüklenmez) çekiliyordu —
  bu da "ilk yüklemede public.tableau.com'a sıfır istek" kabul kriterini
  fiilen bozuyordu. Script artık yalnızca "İnteraktif Dashboard'u Yükle"
  tıklamasında dinamik `<script>` enjeksiyonuyla yükleniyor. Playwright ile
  doğrulandı: yüklemede 0 istek, tıklamada gerçek dashboard (5 istek) açılıyor.
- **Madde 7c (Blog OG/kapak/pagination)** — `8b82242`. og:type=article ve
  pagination linkleri önceki turda zaten doğruydu. Eksik olan tek parça —
  kapaksız yazılarda kategoriye göre varsayılan görsel — `BlogPost.
  cover_image_url` property'siyle eklendi (35/35 yayındaki yazının hiçbirinde
  kapak yoktu, bu yüzden kartlar ve og:image/JSON-LD boş görünüyordu).
  Migration gerekmedi. Playwright ile liste+detay sayfası görsel doğrulandı.
- **Madde 8 (Hero sadeleştirme)** — `c338a7b`. `ax-hero__actions` bloğu
  ("Ücretsiz Başla"/"Analiz Yap" / "Uzman Bul" / "Foruma Katıl", giriş
  yapmış/yapmamış iki varyantıyla) tamamen kaldırıldı. Dropzone, "uzmana
  bırak" linki, veri kazıma bandı, alt CTA kartları değişmedi — Playwright
  ile masaüstü+mobil görsel doğrulandı, orphan spacing/CSS sorunu yok.
- **Madde 10 (Testler + Deploy Notu)** — bu tur. `forum/tests.py`'e 8 yeni smoke
  test eklendi: Madde 1'in 4 ön-seçimi (`?source=verification/agentic/tableau/
  bibliometrics` → `proje_talebi` formunda doğru `<option selected>`), Madde 4
  (forum arama sonucu boş-durumu varsayılan görünümde `d-none` ile gizli),
  Madde 6 (`NoIndexMiddleware` — `IS_PRODUCTION=False`'da header var,
  `True`'da yok, 2 test), Madde 7b (tableau `<tableau-viz>` yalnızca
  `<template>` içinde, ilk yüklemede canlı DOM'da yok). Madde 2 ve 9'un
  testleri zaten mevcuttu (bkz. yukarı Sıfır Kuralı bölümü ve
  `test_register_get_returns_200`/`test_login_get_returns_200`).
  **Sonuç:** 31 test, 30 geçti; tek hata `test_yoktez_job_daily_limit_normal_user`
  — bu turla ilgisiz, önceden bilinen, dokunulmadı (bkz. "Genel notlar").

  **DEPLOY NOTU (main'e merge öncesi — dev, main'den 28 commit ileride):**
  - **Migration:** main→dev arası tam 4 migration — `0144_projectrequest_
    source_choices`, `0145_sitesettings_feature_agentic_landing_and_more`,
    `0146_projectrequest_source_tableau_bibliometrics`,
    `0147_projectrequest_analysis_bibliometric`. Hepsi `AlterField` (choices
    genişletme) + tek `AddField` (boolean flag) — veri kaybı riski yok,
    `--fake` gerekmiyor.
  - **collectstatic:** GEREKLİ. Yeni statik dosyalar: 6 yeni CSS
    (`agentic_landing.css`, `bibliometrics.css`, `brand_visuals.css`,
    `expert_card.css`, `market.css`, `trend_topics.css`) + görseller
    (`agentic-hero(-mobile).webp`, `auth-login(-mobile)/auth-register
    (-mobile).webp`, `biblio-ornek-*.webp` ×6, `tableau-poster-*.webp` ×4).
  - **`?v=` denetimi:** main'de zaten var olup dev'de içeriği değişen yalnızca
    2 CSS dosyası var — ikisi de doğru bump edilmiş: `hero.css` 0103→0105,
    `home_sections.css` 0106→0112. Diğer 6 CSS dosyası main'de hiç yok
    (prod'da eski cache'lenmiş kopya yok), versiyon numaraları (v=0001/0002)
    bu yüzden önemsiz.
  - **Hetzner sırası:** `git pull` (main) → `docker compose exec web python
    manage.py migrate` → `docker compose exec web python manage.py
    collectstatic --noinput` → `docker compose restart web` → `docker compose
    restart nginx` (IP cache sorunu, CLAUDE.md kuralı).
  - **Merge sonrası hatırlatmalar:**
    1. **Feature flag açılmalı:** `feature_agentic_landing` migration'da
       `default=False` geliyor — admin'den `SiteSettings`'te AÇILMAZSA
       `/ai-cozumler/` ne navbar'da (`context_processors.py:75`) ne sitemap'te
       (`sitemaps.py:14`) görünür. Bu adım atlanırsa Madde 1b/7a'nın tüm
       huni işi görünmez kalır.
    2. `robots.txt` içeriği değişti (`Disallow: /istatistik/` satırı
       kaldırıldı, artık 301 üzerinden /analiz/'e akıyor) — GSC "robots.txt
       Test Aracı"ndan yeniden okutulmalı.
    3. Sitemap resubmit (GSC → Sitemaps).
    4. `/ai-cozumler/` + Madde 7'deki araç sayfaları (bibliometrics,
       tableau-analiz vb.) için GSC URL denetimi → elle dizine ekleme iste.
    5. `/istatistik/` → `/analiz/` 301'i GSC URL denetim aracıyla doğrula
       (robots.txt artık bunu engellemiyor, redirect aktif görünmeli).
    6. **Premium fiyat kaynağı kontrol edildi — DÜZELTME GEREKMEDİ.** Kaynak
       tamamen DB: `DonationTier.min_amount` (migration'ları 0031/0032/0045/
       0076, zaten prod'da uygulanmış, bu merge'e dahil değil).
       `footer.html:154-167` yalnızca `{{ tier.min_amount }}` render ediyor,
       hardcode TL değeri yok — prod (250/500/750/1000) ve dev (50/100/250/
       500) farkı tamamen DB seed farkı, template/kod fark yaratmıyor.

- **Madde 9 (Auth panelleri)** — `7837700`. `login.html`/`register.html`
  base.css yüklemiyor (tamamen izole, hardcode renkli sayfalar) — bu yüzden
  `var(--ax-bg)` yerine dosyanın kendi `#0a1628` rengiyle iç vinyet
  (`box-shadow: inset 0 0 90px 70px #0a1628`) eklendi, kullanıcı onaylı.
  Turuncu dikey ayraç çizgisi (`::after`+`@keyframes fall`) kaldırıldı.
  Form `<label>` etiketleri nötr griye (#94a3b8) döndü — sadece etiketler,
  form-subtitle rengi DEĞİŞMEDİ (kullanıcı onaylı kapsam). register.html
  alt başlığı "Ücretsiz hesap — 30 saniye sürer."a çevrildi. <991px
  gizleme davranışı değişmedi, Playwright ile masaüstü+mobil doğrulandı.

## Genel notlar (yeni oturum için önemli)

- **Deploy notu — migration sayısı:** Bu tur `0147`'ye kadar geldi (0144-0147,
  toplam 4 migration). Madde 10'daki deploy notunda bu sayı kullanılmalı.
- **Pre-existing test hatası (bu turla ilgisi yok, dokunma):**
  `forum/tests.py::test_yoktez_job_daily_limit_normal_user` son commit'te de
  başarısız (`assert 3 == 1`) — bu turun DIŞINDA bir konu, `python -m pytest`
  çalıştırınca "1 failed" görürsen şaşırma.
- **service_promo.html gotcha:** Bibliometri, cronbach, normallik, betimsel,
  korelasyon, t-testi, anova, mann-whitney, kruskal-wallis, ki-kare, lineer/
  lojistik regresyon guest (misafir) görünümlerinin HEPSİ bu tek şablonu
  paylaşıyor. Bu sayfalardan birine özel bir düzenleme istenirse, view'daki
  context dict'e yeni bir bayrak eklenip template'te `{% if %}` ile o bayrağa
  göre gösterilmesi gerekir — aksi halde değişiklik ya hiçbir sayfada
  görünmez ya da yanlışlıkla hepsinde birden görünür.

- **Madde 11 (Ana sayfa "AI çağında iki yol" sağ kartı)** — TAMAMLANDI.
  `forum/templates/forum/home.html` FAZ 4 bölümündeki `.ax-agentic-band-card`
  (836-853. satır) sol karttaki (`.ax-brand-visual`) desenle birebir aynı
  yapıya geçti: `<picture>` (agentic-hero.webp masaüstü / agentic-hero-
  mobile.webp mobil, `source media="(min-width:768px)"`) + `.ax-agentic-
  band-card__overlay` gradient + mevcut başlık/metin/CTA içeriği değişmeden
  overlay içine taşındı. `static/css/home_sections.css`'te eski flat-renk
  flex kutusu CSS'i (`.ax-agentic-band-card { display:flex; background:...}`)
  kaldırılıp `__img`/`__overlay` kuralları eklendi (brand_visuals.css'teki
  `.ax-brand-visual__img`/`__overlay` ile aynı desen); `?v=0112`→`0113`.
  **Kritik gözlem:** agentic-hero görselleri sol karttaki ai-dogrulama
  görselleriyle piksel-piksel AYNI boyutta (1600×893 masaüstü, 800×446
  mobil) — bu yüzden iki kart hiçbir grid-stretch hilesine gerek kalmadan
  doğal olarak eşit yükseklikte oluştu, eski `@media(min-width:768px)
  { .ax-agentic-band-card{height:100%} }` kuralı gereksiz hale gelip
  kaldırıldı. `object-fit:cover;object-position:center` yine de güvenlik
  amaçlı bırakıldı (boyutlar eşit olduğu için normal akışta devreye
  girmiyor). Render'a push edilip (`analizus-dev.onrender.com`) Playwright
  ile doğrulandı: masaüstünde iki kart TAM eşit yükseklik (306.7px),
  380px mobilde neredeyse eşit (189.5 vs 190.4px, <1px fark), yatay taşma
  yok, görsel/overlay/metin doğru render ediyor.

## Kalan işler

Yok — "Merge Öncesi Son Süpürme" turunun 11 maddesi tamamlandı ve `dev`→`main`
merge'i de yapıldı (31 Temmuz 2026). Tek açık nokta: `feature_agentic_landing`
flag'inin prod'da elle açıldığı doğrulanmadı (bkz. Madde 10 deploy notu,
"Merge sonrası hatırlatmalar" #1) — sıradaki oturumda admin panelinden
kontrol edilmeli.

## Yeni oturumda nasıl devam edilir

1. Bu dosyayı (`tasks/todo.md`) ve `CLAUDE.md`'yi oku (CLAUDE.md zaten proje
   kökünde, otomatik yükleniyor).
2. Bu tur tamamlandı — yeni oturumda kullanıcı ya merge onayı verecek ya da
   yeni bir görev başlatacak (`/market/` pazaryeri zenginleştirme veya
   aşağıdaki fikir-aşaması maddelerinden biri gibi).

---

# /market/ Pazaryeri Zenginleştirme

**Durum:** Bekliyor — henüz başlanmadı. Kaynak prompt kullanıcı tarafından
hazırlandı (`analizus_pazaryeri_prompt.md`, bu konuşmada paylaşıldı, repo'da
dosya olarak yok). (Temmuz 2026)

## Amaç
`/market/` işlevsel ama çıplak (stats + ilan listesi + 3 adım) — hedef, sayfayı
gerçek bir pazaryeri vitrinine çevirmek: iki tarafı da (ilan açan / uzman)
karşılayan çift kapı, güven işaretleri, gezilebilir kategoriler, akan sosyal
kanıt.

## Protokol (kullanıcının vurguladığı 3 kritik nokta — sıfır kuralıyla aynı disiplin)
1. **Kuralı tanımla, yerleri saydırma.** İlk iş envanter: `/market/` view +
   template, ana sayfa uzman vitrini sorgusu (`home()`), trust bandı, skill
   chip yapısı incelenip YENİDEN KULLANILACAKLAR belirlenir; plan onaya
   sunulmadan uygulamaya geçilmez.
2. **İstisnayı ilkeyle tanımla, örnekle sabitle.** Bu görev "sıfır kuralı"
   görevinin somut uygulama alanlarından biri: market'teki "İlk analiz işini
   sen tamamla…" boş-durum metni bilinçli bir DAVETTİR, korunur — /hakkimizda/
   "Henüz uzman kadro eklenmedi." gibi bir İTİRAF değildir. Faz 4'teki sayaç
   üçlüsü (Tamamlanan İş / Aktif Uzman / Son 90 Günde) sıfır kuralına bağlanır:
   0 olan sayaç gizlenir, üçü de 0 ise şerit tamamen gizlenir.
3. **Yan etkileri kurala bağla.** Fiyat gizliliği kesin (uzman kartlarında
   fiyat/teklif bilgisi ASLA gösterilmez); sayaç/uzman sorguları ana
   sayfadaki `home_stats`/`home_experts` cache pattern'i yeniden kullanılır,
   çift hesaplama yapılmaz; kategori chip'leri ilan modelinde gerçek bir
   skill/kategori alanı yoksa "görsel chip + hepsi aynı listeye" şeklinde
   sessizce degrade EDİLMEZ — durum kullanıcıya bildirilip birlikte karar
   verilir; OG meta override mekanizması `base.html`'e dokunuyorsa ayrı onaya
   sunulur.

## Fazlar (kaynak promptta tanımlı)
- Faz 1 — Hero Bandı + Çift Kapı (İlan Aç / Uzman Olarak Katıl, market-hero
  görseli yoksa CSS-only placeholder)
- Faz 2 — Kategori Gezinmesi (`?skill=` GET filtresi — ilan modelinde kategori
  alanı yoksa DUR ve sor)
- Faz 3 — Sosyal Kanıt Katmanı (uzman vitrini şeridi, başarı hikayeleri varsa,
  oyunlaştırma/puan bandı)
- Faz 4 — Sıfır Temizliği + SEO (sayaç üçlüsü sıfır kuralı, OG override, SEO
  paragrafı)
- Faz 5 — Deploy Notu

## Sıradaki adım
Kullanıcı başlamamı istediğinde `analizus_pazaryeri_prompt.md` içeriğiyle
Faz 1'i çalıştırıp planı onaya sunacağım. Not: /market/ görevi, sıfır kuralı
görevinden ÖNCE veya SONRA yapılabilir — market'in Faz 4'ü sıfır kuralına
bağlı olduğundan, sıfır kuralı önce bitmişse market Faz 4 onun sonucunu
doğrudan kullanabilir (tekrar iş çıkarmaz), ama bu bir ön koşul değil.

---

# Çalışma Odaları Dönüşümü — Ertelenmiş İşler

**Kaynak:** `analizus_odalar_prompt.md` (repoda dosya olarak yok — yalnızca
sohbet eki olarak verildi, karakter kodlaması bozuk geldiği için repoya
olduğu gibi yazılmadı). Faz 1/2/3/4/5/6 tamamlandı (temmuz 2026, `dev`
branch'inde commit'lendi: faz-1, faz-1 ek, faz-2, faz-4, faz-3, faz-5+6).

## Ertelenen: Faz 3 milestone (proje odası ilerleme çekliste)
Proje tipi (`room_type='project'`) odalar için kurucunun işaretleyebildiği
3–7 maddelik ilerleme kontrol listesi özelliği **şimdilik eklenmedi**.
Karar: yalnızca `room_type` etiketi + görsel ayrım yeterli kabul edildi;
milestone checklist'i (JSONField `milestones = models.JSONField(default=list)`
+ kurucunun inline ekleyip işaretlediği küçük bir POST endpoint'i, üyeler
tam listeyi görür, misafir yalnızca "%40 tamamlandı" bar'ını görür) ayrı
bir görev olarak ele alınacak.

**Ne zaman gündeme gelir:** Kullanıcı proje odaları için ilerleme takibi
isteğini tekrar gündeme getirdiğinde, veya `room_type='project'` kullanımı
yaygınlaştığında.

## Henüz yapılmayan fazlar
- **Faz 7 — Görsel yükseltme:** `static/img/odalar-hero.webp` ve
  `odalar-hero-mobile.webp` artık mevcut (kullanıcı sağladı, henüz repoya
  commit'lenmedi/kullanılmadı). Hero + kart dilini market/agentic sayfalarıyla
  hizala.
- **Faz 8 — SEO + teknik temizlik:** Slug Türkçe karakter düzeltmesi
  (mevcut oda slug'larına dokunma), JSON-LD Event schema, sitemap,
  test hesap temizliği (kullanıcı kararı gerekiyor).

---

# Ana Sayfa & Navbar İyileştirme Turu — Faz 12 + Faz 13 (bekleyen)

**Kaynak:** `analizus_anasayfa_prompt.md` (proje kökünde dosya olarak mevcut).
Faz 0,1,2,3,4,5,6,7,8,9,10,11 tamamlandı ve
`main`'e merge edildi (bkz. memory `project_anasayfa_iyilestirme`). Faz 12 ve
13 o turdan kalan, henüz başlanmamış iki faz.

## Faz 12 — Forum vitrini dönüşümü — TAMAMLANDI (kısmi yayın), Temmuz 2026, dev branch
Ana sayfadaki "Gündemdeki Tartışmalar" 6 jenerik AI konusu (Fine-tuning vs RAG,
Prompt Engineering, Açık kaynak LLM'ler, LLM Halüsinasyonu, GPU olmadan Deep
Learning, LLM etik sınırları — hepsi `seed_forum.py`'den sabit views=3456-5678
ile) `forum/management/commands/remove_generic_seed_topics.py` ile silindi.
Konuyla alakalı ama sahte-seed 4 konuya (SPSS normallik, anket örneklem,
Google Forms, Türkçe NLP model) kullanıcı kararıyla dokunulmadı.

`forum/management/commands/reseed_forum_topics.py` (yeni, idempotent,
`--count N` ile kademeli yayın) 12 yeni konu+uzman cevabını (SEO'ya dikkat
edilerek yazıldı) ve 3 yeni Category'yi (`akademik-surec`, `veri-analizi-bi`,
`ai-ml-agentic`) içeriyor — kaynak: `analizus_forum_seed_konular.md`. Bu turda
`--count 3` ile yalnızca ilk 3 konu (Hakem 2/SEM, Etik kurul onam muafiyeti,
YÖK Tez benzerlik) canlıya alındı; kalan 9 konu dosyada hazır, sonraki
haftalarda `docker compose exec web python manage.py reseed_forum_topics
--count N` ile devreye alınır (kademeli yayın kuralı — hepsi bir günde
açılmaz).

`forum/views.py` — yeni `_trending_topics()` yardımcı fonksiyonu (`home()` ve
`forum_index()` ortak kullanıyor, N+1 yok): sıralama artık `-views` değil,
`Exists()` ile uzman (`account_type='Expert'`) cevaplı konular önce, dolmazsa
son aktif konular. `views` alanı DEĞİŞMEDİ (gerçek sayaç, `topic_detail()`'da
artıyor), sadece sıralama kriteri değişti.

`_gundem_tartismalar.html` — "Uzman cevapladı" rozeti (`ax-badge
ax-badge--primary`) + cevap sayısı eklendi. `trend_topics.css`'te forum
varyantı meta satırına `flex-wrap`/`max-width` eklendi (rozet mobilde
taşmasın diye), `?v=0001`→`0002` bump edildi (forum_index.html + home.html×2).

Doğrulama: `python -m pytest forum/tests.py` → 52/53 geçti (tek hata
`test_yoktez_job_daily_limit_normal_user`, bu turla ilgisiz, önceden bilinen).
Django shell üzerinden `/` ve `/forum/` render edildi, "Uzman cevapladı" 5
kez görünüyor, "Fine-tuning" metni artık hiç yok. Playwright ile görsel
(mobil taşma) doğrulaması henüz yapılmadı — sıradaki oturumda önerilir.

**Kalan iş:** 9 konunun kademeli yayını (haftada 2-3, `--count` artırılarak)
+ her yayından sonra ilgili uzman hesabın cevabının gerçekten "vitrin
kalitesinde" durduğunu gözden geçirmek.

## Faz 13 — Dropzone akışı: vaat + triyaj şeridi
Hero dropzone'a dosya bırakan kullanıcı `/analiz/?from=hero` araç listesine
düşüyor ama analiz bilmeyen kullanıcı 18 araç arasında yol göstericisiz
kalıyor — H1 "yapamıyorsan yapan burada" vaadiyle çelişki.

- **Keşif (metinden önce zorunlu):** dosya hero'da sunucuya mı yükleniyor,
  tarayıcıda mı tutuluyor; misafir kullanabiliyor mu; `/analiz/`de dosya
  durumu nasıl taşınıyor.
- **Triyaj şeridi:** `/analiz/`de yalnızca `from=hero` + dosya seçili durumda,
  rozetin altına üç link: Hangi Test? sihirbazı · AI Asistan'a sor
  (`axOpenAiWidget`) · Bu işi uzmana bırak (`?source=analiz_triyaj`). Yeni
  motor yok, mevcut hedefler kullanılır.
- **Hero mikrometni (keşif sonrası):** vaat gerçeğe göre yazılır, yalnızca
  teknik olarak doğrulanan ifadeler kullanılır; uygulamadan önce kullanıcıya
  sunulur.
- ERTELENEN (bu fazın kapsamı dışı): kolon-tipine dayalı gerçek öneri motoru.

## Sıradaki adım
Kullanıcı başlamamı istediğinde önce Faz 12 için karar noktasını (komut mu
elle mi) sorup uygulayacağım; Faz 13 keşif adımıyla başlayacak. İkisi
birbirinden bağımsız, istenen sırada yapılabilir.

## Faz 13 — DURUM: mikrometin + triyaj şeridi tamamlandı (temmuz 2026)
Keşif + uygulama bitti: hero dropzone altına "Kayıt gerekmez — hemen dene"
mikrometni (`forum/templates/forum/home.html` + `static/css/hero.css`,
`.ax-hero-dropzone__trust`, `?v=0107`), `/analiz/` sayfasına `from_hero`
rozetinin altına triyaj şeridi (Hangi Test? · AI Asistan'a sor · Bu işi
uzmana bırak `?source=analiz_triyaj`) eklendi
(`istatistik/templates/istatistik/analiz_hub.html`).

**Doğrulanan mimari bulgular (Faz 13 keşfinden):**
- Hero'dan yüklenen dosya gerçekten sunucuya gidiyor, session'da RAM'de
  tutuluyor (`istatistik/services/job_runner.py` — `_session_datasets`,
  `_pending_file_contents`); disk/DB'ye yazılmıyor.
- Login yalnızca **dosya yükleme** adımında zorunlu değil — misafir dosyayı
  session'a yükleyebiliyor, ama `orneklem` hariç 17 araç view'ı
  `is_authenticated` kontrolünü GET/POST ayrımı yapmadan en başta yapıp
  anonime `service_promo.html` (kayıt/giriş duvarı) döndürüyor; misafir gerçek
  analizi çalıştıramıyor. `is_demo=not request.user.is_authenticated` deseni
  yalnızca zaten giriş yapmış kullanıcıya ulaşan koda ait
  (11 Ekim 2026 hero doğrulama turunda düzeltildi — önceki not yanlıştı).
- Production tek process/tek container (Hetzner: `docker-compose.yml` tek
  `web` servisi, `Dockerfile` CMD'si tek `daphne` process, nginx tek
  `web:8000` upstream'ine proxy; Render/`Procfile` de aynı). **Modül seviyesi
  dict için multi-worker veri kaybı riski şu an gerçek değil** — yalnızca
  ileride yatay ölçeklendirilirse (birden fazla container/process) mimari
  kırılır, dikkat edilecek kısıt olarak not düşülüyor.
- Dosya boyutu limiti zaten var: `MAX_UPLOAD_SIZE = 5MB`
  (`analizdestek/settings.py:529`), `hero_upload` kontrol ediyor — ek iş yok.

## `_session_datasets` TTL temizliği — TAMAMLANDI (31 Temmuz 2026)
Faz 13 keşfinde bulunan bellek sızıntısı riski (terkedilmiş veri setleri
süresiz RAM'de birikiyor) çözüldü ve canlıda doğrulandı:
- `istatistik/services/job_runner.py` — `_session_datasets` artık
  `(content, filename, saved_at)` tutuyor, `SESSION_DATASET_TTL_SECONDS = 2 saat`
  (kullanıcı kararı — `SESSION_COOKIE_AGE` ile hizalı, 24 saat önerisi session
  zaten 2 saatte geçersiz olduğu için gereksiz bulundu), yeni
  `cleanup_expired_session_datasets()` fonksiyonu eklendi.
- `forum/api_views.py` + `forum/urls.py` — mevcut `/api/cron/*` desenine uygun
  yeni `cron_cleanup_session_datasets` endpoint'i (`X-Cron-Secret` doğrulamalı).
  DB değil RAM temizlediği için (ayrı process bu dict'e erişemez) yalnızca bu
  HTTP-tetiklemeli desen çalışır — management command seçeneği mimari olarak
  elenmiş oldu.
- `dev`'den `main`'e fast-forward merge edildi, Hetzner'e deploy edildi
  (`git pull` + `restart web`/`nginx`, migration yok), crontab'a saatlik satır
  eklendi (`0 * * * * curl ... cleanup-session-datasets/?secret=...`).
- Canlı doğrulama: doğru secret → `{"success": true, "deleted": 0}`, yanlış
  secret → `403`; `crontab -l` ile satır teyit edildi.

Aynı turda ayrıca bulunup düzeltilen ilgisiz bug: `cleanup-pageviews` cron
satırı www'suz domain kullandığından 301'e takılıp hiç çalışmıyordu (canonical
domain `www.analizus.com`'a dönmüş, crontab güncellenmemişti); `cleanup-s3`
ve `cleanup-attachments` dokümantasyonda "Aktif" görünüp crontab'da hiç
yoktu. Üçü de düzeltildi/eklendi — detay: `analizus.md` §23.

## PageSpeed Insights — Kalan Optimizasyon Fırsatları (ertelendi, temmuz 2026)

MathJax/Prism/Font Awesome kaldırma, footer kontrast (WCAG AA) ve
bootstrap-icons preload (CLS 0.102→0.009) düzeltmeleri uygulandı ve
`main`'e merge edildi (masaüstü 86→96, mobil 70→80, erişilebilirlik
96→100). Kullanıcı kararıyla burada duruldu — kalanlar ayrı, daha büyük
işler:

- [ ] **Kullanılmayan CSS (Bootstrap, 43 KiB)** — ayrı görev olarak zaten
  planlı, bkz. bu dosyanın başındaki "Bootstrap Kaldırma — Kademeli
  Migration Planı"
- [x] **DÜZELTİLDİ (12 Ekim 2026, henüz push edilmedi) Render-blocking `bundle.css`**
  (188-190ms) + **Ağ bağımlılık ağacı** (kritik yol ~588ms). Plan:
  `~/.claude/plans/synthetic-prancing-engelbart.md`. Tek dosya:
  `templates/base.html`. `bundle.css`'in kendisi/`rcssmin` süreci değişmedi.
  **Yapılan:** (1) `<head>`'in en üstüne, `base.css`/`navbar.css`'ten
  birebir kopyalanan küçük bir "kritik iskelet" `<style>` bloğu eklendi
  (`:root` token'ları, `.ax-container`, `body` padding-top, `.site-nav`
  ailesi — logo/menü/hamburger — navbar'ın ilk boyamada da fixed+arka
  planlı görünmesi, `body{padding-top}` ile CLS'e yol açmaması için).
  (2) `bundle.css` linki Inter/Bootstrap/bootstrap-icons'takiyle BİREBİR
  aynı `media="print" onload="this.media='all'"` + `<noscript>` desenine
  taşındı. **Test sırasında bulunan ek sorun:** `.site-nav__dropdown`,
  `.nav-drawer`, `.nav-overlay`, `.ax-skip-link`, `.ax-modal-backdrop`,
  `.ax-dropdown` — hepsi "gizli" durumunu `display:none` değil
  opacity/visibility/transform ile sağlıyor; kritik blokta olmayınca
  bundle.css gelene kadar İÇERİKLERİ (dropdown menüler, mobil çekmece,
  3 modal — arama/quiz/hikaye) normal akışta GÖRÜNÜR render olup sayfayı
  aşağı itiyordu (Playwright ile route-delay testinde görüldü, ekran
  görüntüsüyle doğrulandı) — bu 6 seçici için de minimal "gizli durum"
  kuralı (yalnızca position/opacity/visibility, tam kutu stili değil)
  kritik bloğa eklendi, ikinci testte sorun kalmadı.
  **Doğrulama:** Docker'da `restart web`; Playwright ile 4 sayfa tipi
  (`/`, forum, market, bibliometrics) × 2 viewport (1280/375px),
  `page.route` ile `bundle.css` 3sn geciktirilip erken/geç anlarda
  `.site-nav` computed style (`position/height/background/body padding-top`)
  karşılaştırıldı — birebir aynı, sıçrama yok; ekran görüntüleriyle de
  teyit edildi. JS kapalıyken `<noscript>` fallback'i tam stilli render
  ediyor. `docker compose exec web python -m pytest forum/tests.py -q`
  → 90/90 yeşil. Lokal Lighthouse (`npx lighthouse`) öncesi/sonrası
  kıyası: `render-blocking-resources` skoru 0 (bundle.css ~630ms,
  "Est savings 450ms") → **1** (temiz); CLS her ikisinde de **birebir aynı**
  (0.215, kaynağı `#ax-cookie` banner'ı — bu PR'dan bağımsız, önceden var
  olan ayrı bir sorun, kapsam dışı bırakıldı, istenirse ayrı todo maddesi).
  `main`'de kayıtlı "CLS 0.009" rakamı muhtemelen farklı ölçüm koşulları
  (üretim/PageSpeed Insights vs. yerel Lighthouse + bu çerez banner'ı) —
  bu PR o rakamı etkilemedi, yalnızca doğruladı.
- [ ] **Yandex Metrica** — verimli önbellek (71 KiB) + kullanılmayan JS
  (43 KiB) + olası uzun görevler; üçüncü parti, init'i `requestIdleCallback`
  ile ertelemek TBT'yi düşürür ama webvisor/bounce-tracking doğruluğunu
  etkileyebilir — iş kararı, kullanıcıya sorulmadan yapılmayacak
- [ ] **Zorunlu yeniden düzenleme** (~103ms ilişkilendirilmemiş) — kesin
  kaynağı Chrome DevTools Performance profiliyle tespit edilmeli, first-party
  JS'te (navbar.js/ax-dropdown.js/widget_collapse.js/main.js) layout-thrashing
  deseni yok (grep ile doğrulandı)
- [ ] **28 birleştirilmemiş (uncomposited) animasyon** — `border-color`/
  `background-color`/`box-shadow` geçişleri ax- tasarım sisteminde ~20 CSS
  dosyasına yaygın, düzeltmek geniş kapsamlı bir tasarım sistemi revizyonu
  gerektirir
- [x] **Görsel boyutu** (`ai-dogrulama.webp`/`agentic-hero.webp`) —
  1600×893 → 1100×614 küçültüldü, kullanıcı kararıyla burada bırakıldı
  (retina netliği öncelikli, 30 KiB'lik kalan Lighthouse uyarısı kabul edildi)

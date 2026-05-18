# 🛍️ Gratis Fiyat Davranışı Analizi
### Tüketici için Veri Odaklı Alışveriş Rehberi

> Gratis'te gerçekten indirimli olan ürünleri bulmak hiç bu kadar kolay olmamıştı.

🔗 **Canlı Uygulama:** [Streamlit Dashboard](https://gratis-indirim-takip-fczbse3yyhmdyev5mgkjzg.streamlit.app/)

---

## 📌 Proje Motivasyonu

Gratis ürünlerinin **%93'ü her zaman indirimli görünüyor.** Medyan indirim oranı **%50**, ortalama indirim **%50.4.**

Bu rakamlar şu soruyu doğuruyor:

> *"Bu indirimler gerçek mi, yoksa fiyatlar zaten yüksek belirlenip yapay olarak indirimli mi gösteriliyor?"*

Verideki en çarpıcı bulgu: 28.000 ürün tam olarak **%50 indirimle** listelenmiş. İndirim oranları yuvarlak değerlerde (%20, %30, %40, %50, %60, %70) yoğunlaşıyor; aradaki ondalık değerlerde neredeyse hiç gözlem yok. Bu, **fiyatlama kararlarının pazar dinamiklerinden değil, pazarlama stratejisinden** kaynaklandığını düşündürüyor.

Bu proje, Gratis'teki fiyat davranışlarını veriyle analiz ederek tüketicinin gerçekten avantajlı ürünleri ayırt edebilmesi için bir **fırsat skoru sistemi** geliştirmeyi amaçlamaktadır.

---

## 📁 Proje Yapısı

```
gratis-indirim-takip/
│
├── data/
│   └── processed/
│       ├── gratis_clean.csv          # Temizlenmiş ana veri seti
│       ├── urun_ozellikleri.csv      # Ürün bazlı davranışsal özellikler
│       ├── urun_kumeleri.csv         # K-Means kümeleme sonuçları
│       └── urun_firsat_skorlari.csv  # Nihai fırsat skorları
│
├── notebooks/
│   ├── 01_veri_yukleme_ve_temizlik_son.ipynb
│   ├── 02_kesifsel_analiz_son.ipynb
│   ├── 03_ozellik_muhendisligi_ve_kumeleme.ipynb
│   ├── 04_firsat_skoru_ve_sonuclar.ipynb
│   └── 05_indirim_tahmini_deneysel_model.ipynb
│
├── app.py                # Streamlit uygulaması
├── gratis.py             # Web scraper
├── requirements.txt
└── README.md
```

---

## 🔧 Kullanılan Teknolojiler

| Katman | Araçlar |
|--------|---------|
| Veri Toplama | Playwright, BeautifulSoup |
| Veri Depolama | SQLite, Pandas |
| Analiz | Pandas, NumPy, Matplotlib, Seaborn |
| Modelleme | Scikit-learn (K-Means, PCA, StandardScaler, Random Forest) |
| Uygulama | Streamlit |

---

## 📊 Veri Seti Özeti

| Metrik | Değer |
|--------|-------|
| Ham kayıt sayısı | 168.356 |
| Temiz gözlem sayısı | 118.812 |
| Benzersiz ürün sayısı | 10.628 |
| Kategori sayısı | 14 |
| Marka sayısı | 422 |
| Tarih aralığı | 4 Nisan – 6 Mayıs 2026 |
| Snapshot günü | 15 |
| Ortalama fiyat | 345 TL |
| Medyan fiyat | 200 TL |
| İndirimli gözlem oranı | %93.3 |
| Ortalama indirim | %50.4 |

---

## 🗂️ Notebook'lar ve Analiz Aşamaları

---

### 📓 Notebook 01 — Veri Yükleme ve Temizlik

**Amaç:** Ham SQLite verisini analiz ve modelleme için hazır hale getirmek.

**Ham verinin yapısı:**
- Kaynak: `gratis.db` SQLite veritabanı (`fiyat_gecmisi` tablosu)
- 168.356 kayıt, 14 sütun
- Sütunlar: `urun_id`, `isim`, `marka`, `kategori`, `fiyat`, `eski_fiyat`, `indirim_yuzde`, `kampanya`, `yorum_sayisi`, `begeni`, `url`, `tarih`, `kayit_zamani`

**Eksik değer profili:**

| Sütun | Eksik Sayı | Yorum |
|-------|-----------|-------|
| `eski_fiyat` | 17.494 | İndirim yok anlamına geliyor |
| `indirim_yuzde` | 17.494 | İndirim yok anlamına geliyor |
| `kampanya` | 129.321 | Kampanya etiketi taşımıyor |
| `begeni` | 201 | Beğeni bilgisi eksik |

**Yapılan temizlik adımları:**

1. **Tarih dönüşümleri:** `tarih` ve `kayit_zamani` sütunları `datetime` formatına çevrildi. `snapshot_gun` (gün hassasiyetinde tarih) türetildi.
2. **Beğeni sayısallaştırma:** `"2B"`, `"13B"` gibi metin formatları sayısal değere (`begeni_sayi`) dönüştürüldü.
3. **Eksik değer stratejisi:**
   - `eski_fiyat` ve `indirim_yuzde` boşları → "indirim yok" anlamında 0/güncel fiyatla dolduruldu
   - `kampanya` boşları → `"Kampanya Yok"` etiketi atandı
4. **Boolean flag:** `indirimde_mi` sütunu türetildi.
5. **Gün bazına indirgeme:** Aynı ürün-aynı günün birden fazla snapshot'ı varsa en güncel kayıt tutuldu → **47.074 satır çıkarıldı**
6. **Minimum gözlem filtresi:** En az **5 farklı günde** gözlemlenen ürünler analiz kapsamına alındı → 1.051 ürün (%9) çıkarıldı
7. **Marka adı düzeltmeleri:** Scraper marka adını ürün adının ilk kelimesinden türettiği için çok kelimeli marka adları manuel olarak düzeltildi (örn: `Bee` → `Bee Beauty`, `Golden` → `Golden Rose`)

**İndirim formülü:**
```python
indirim_orani = (1 - fiyat / eski_fiyat) * 100
```
> Sitenin kendi indirim değeri yerine, tüm ürünlerde tutarlı karşılaştırma sağlamak için yeniden hesaplandı.

**Final veri seti:**
- Temiz gözlem: **118.812**
- Benzersiz ürün: **10.628**
- Mükerrer ürün-gün kaydı: **0**
- Ürün başına ortalama gözlem: **11.2 gün**

---

### 📓 Notebook 02 — Keşifsel Veri Analizi (EDA)

**Amaç:** Modellemeye geçmeden önce verinin yapısını, dağılımlarını ve gizli örüntüleri anlamak.

**İncelenen 8 soru:**
1. Genel manzara: kategori ve marka dağılımı
2. Fiyat yapısı: dağılım ve uç değerler
3. İndirim manzarası: derinlik ve sıklık
4. Kategori karşılaştırması: indirim agresifliği
5. Marka davranışı: fiyat konumlanması
6. Zaman dinamiği: indirim oranları nasıl değişiyor?
7. Popülerlik-fiyat ilişkisi
8. Kampanya analizi

#### Kategori Dağılımı
- **Makyaj** en büyük kategori: 3.666 ürün (katalogunun ~%34'ü)
- İlk 3 kategori (Makyaj + Cilt Bakım + Saç Bakım) katalogunun **%62'sini** oluşturuyor
- En küçük: Elektrikli Ürünler (53 ürün)

#### Fiyat Yapısı
```
Ortalama:  345 TL   (medyandan 1.7x yüksek)
Medyan:    200 TL
%25:       115 TL
%75:       341 TL
%99:     3.396 TL
Max:    22.929 TL   (lüks parfüm seti)
Çarpıklık: 10.90    (aşırı sağa çarpık)
```

**Kategori bazında fiyat segmentleri:**

| Segment | Kategoriler | Medyan Fiyat |
|---------|------------|--------------|
| Premium | Elektrikli Ürünler | 1.099 TL |
| Üst Orta | Güneş Ürünleri, Parfüm | 250–415 TL |
| Orta | Makyaj, Cilt Bakım | 210–225 TL |
| Ekonomik | Süpermarket, Kişisel Bakım | 59–148 TL |

> **Modelleme notu:** Sağa çarpık dağılım nedeniyle fiyat değişkenleri log dönüşümüyle kullanıldı.

#### İndirim Manzarası
```
Ortalama indirim:  %50.4
Medyan indirim:    %50.0
Std sapma:         %13.9
%25:               %40.1
%75:               %60.0
Max:               %88.8
```

**Kritik bulgular:**
- **%50'de devasa tepe:** ~28.000 gözlem tam olarak %50 indirimle listelenmiş
- **Yuvarlak değerlerde yığılma:** %20, %30, %40, %50, %60, %70'te sivri tepeler — aralarında neredeyse hiç gözlem yok
- **%40-60 bandında %63 yoğunlaşma:** Gratis'in "iyi indirim" olarak konumlandırdığı aralık
- **%80+ indirim yok denecek kadar az:** Sadece 173 gözlem

#### Kategori Bazında İndirim Agresifliği

| Kategori | İndirimli Oran | Ortalama İndirim |
|----------|---------------|-----------------|
| Elektrikli Ürünler | %100 | %58.0 |
| Makyaj | %90 | %56.5 |
| Güneş Ürünleri | %98 | %53.8 |
| Cilt Bakım | %98 | %53.2 |
| Saç Bakım | %97 | %49.3 |
| Süpermarket | %66 | %37.8 |

> 14 kategoriden **12'sinin indirimli oranı %90'ın üzerinde.** Süpermarket tek gerçekten farklı davranan kategori.

#### Zaman Dinamiği

İki belirgin kampanya zirvesi tespit edildi:
- **4 Nisan 2026 (%100 indirimli oran, %60 derinlik):** "1-10 Nisan Makyaj + Saç Bakım Bahar Kampanyası" ile örtüşüyor
- **17 Nisan 2026 (%60 derinlik):** Bahar kampanyasının ikinci dalgası

Kampanya bittikten sonra derinlik **%60 → %46** bandına geri çekiliyor ve Mayıs başında bu seviyede stabil kalıyor.

**Veri boşluğu:** 21-26 Nisan tarihleri arasında veri toplanamadı — bu dönem "DEV FIRSAT" kampanyasıyla örtüşüyor.

**Gratis'in iki katmanlı fiyat stratejisi:**
- **Baz katman (her zaman):** ~%46 ortalama indirim
- **Kampanya katmanı (dönemsel):** %60+ derinlik

#### Popülerlik-İndirim İlişkisi
- Pearson korelasyon: **0.139** — Güçlü bir doğrusal ilişki yok

---

### 📓 Notebook 03 — Özellik Mühendisliği ve K-Means Kümeleme

**Amaç:** Her ürün için davranışsal özellikler üretmek ve ürünleri benzer profillere göre kümelemek.

#### 12 Davranışsal Değişken

| Grup | Değişken | Açıklama |
|------|---------|---------|
| Fiyat | `log_ortalama_fiyat` | Log dönüşümlü ortalama fiyat |
| Fiyat | `fiyat_araligi_orani` | (max-min)/ortalama |
| Fiyat | `fiyat_degisim_orani` | Kaç günde fiyat değişti? |
| Fiyat | `fiyat_std` | Fiyat standart sapması |
| İndirim | `ortalama_indirim` | Gözlem dönemi ortalaması |
| İndirim | `max_indirim` | En yüksek ulaşılan indirim |
| İndirim | `indirim_std` | İndirim tutarlılığı |
| İndirim | `indirimli_gun_orani` | Kaç günde indirimde? |
| Kampanya | `kampanyali_gun_orani` | Kaç günde kampanya etiketli? |
| Kampanya | `farkli_kampanya_sayisi` | Kaç farklı kampanyaya girdi? |
| Popülerlik | `populerlik_skoru` | Yorum + beğeni kompozit skor |
| Kapsam | `gozlem_sayisi` | Kaç günde gözlemlendi? |

**Ön işlem:** %1-%99 kırpma + `StandardScaler` standardizasyonu

#### Küme Sayısı Belirleme

**Silhouette skorları:**

| k | Silhouette |
|---|-----------|
| 2 | 0.46 (en yüksek) |
| 3 | **0.43** (seçilen) |
| 4 | 0.18 ← sert düşüş |

**k=3 seçimi:** k=2 matematiksel optimal ama tüketici için yorum gücü sınırlı. k=4'te Silhouette çöküyor. k=3 hem güçlü skor hem de 3 yorumlanabilir profil sunuyor.

#### 3 Ürün Profili

| Küme | Ad | Ürün Sayısı | İndirimli Gün | Ort. İndirim | Kampanya |
|------|---|------------|--------------|-------------|---------|
| 0 | Sürekli İndirimli Ana Katalog | 9.020 (%85) | %100 | ~%50 | %27 |
| 1 | Stabil ve Düşük Kampanyalı | 655 (%6) | %82 | ~%30 | ~%0 |
| 2 | Oynak Fiyatlı, Dönemsel Fırsat | 953 (%9) | %38 | düşük ort, yüksek max | %23 |

**PCA:** PC1 %26.6 + PC2 %24.3 = %50.9 toplam varyans açıklanıyor.

---

### 📓 Notebook 04 — Fırsat Skoru ve Sonuçlar

**Amaç:** Her ürüne tüketici perspektifinden 0-100 arası bir fırsat skoru atamak.

#### Fırsat Skoru Bileşenleri

| Bileşen | Ağırlık | Hesaplama |
|---------|---------|---------|
| Geçmiş fiyata göre avantaj | **%45** | Güncel fiyat geçmiş minimuma ne kadar yakın? |
| İndirim derinliği | **%30** | `guncel_indirim / 70 * 100` (max %70'te doyuyor) |
| Küme davranışı | **%15** | Küme 2: 85, Küme 0: 70, Küme 1: 40 |
| Kampanya bonusu | **%10** | Kampanya varsa: 100, yoksa: 0 |

#### Fırsat Sınıfları

| Skor | Sınıf | Ürün Sayısı |
|------|-------|-------------|
| 80–100 | Çok Güçlü Fırsat | **346** |
| 60–79 | İyi Fırsat | **814** |
| 40–59 | Orta Seviye | **1.274** |
| 0–39 | Beklemek Mantıklı | **8.194** |

> 10.628 üründen yalnızca **%3.3'ü** gerçek anlamda güçlü fırsat.

---

### 📓 Notebook 05 — Deneysel Tahmin Modeli

**Amaç:** Gelecek haftanın indirim oranını tahmin etmek — ve fiyat dinamiklerini anlamak.

**Train/Validation:** Nisan (3 hafta) → Mayıs (1 hafta), zamana göre bölünme.

**Özellik önemi (Random Forest Gini):**

| Değişken | Önem |
|---------|------|
| `lag_1w_indirim` | **0.72** |
| `lag_3w_indirim` | 0.14 |
| `rolling_std_indirim` | 0.06 |
| Diğerleri | < 0.03 |

**Model performansı:**
- Ortalama hata: **0.01** (tarafsız)
- Std: **4.55**

**Kritik bulgu:** `lag_1w` tahminlerin %72'sini açıklıyor → Gratis'te fiyatlar haftalarca sabit kalıyor. Model "öğrenmek" yerine "geçen haftayı kopyalamak" yapıyor.

---

💡 Temel Çıkarımlar
1. Gratis'te "indirim" bir özellik değil, varsayılan durum.
Gözlemlerin %93'ü indirimde — bu bir kampanya değil, kataloğun kalıcı hali. "İndirimde mi?" sorusu artık anlamsız. Doğru soru: "Bu ürün kendi geçmiş fiyatına göre şu an gerçekten avantajlı mı?"
2. %50 indirim rakamı rastlantı değil, tasarım.
28.000 ürün tam olarak %50 indirimle listelenmiş. İndirim oranları yuvarlak değerlerde (%20, %30, %40, %50, %60, %70) keskin tepeler oluşturuyor — aradaki ondalık değerlerde neredeyse hiç gözlem yok. Fiyat, "yarı fiyatına aldım" algısı yaratmak için geriye doğru kurgulanmış.
3. Gratis aslında iki farklı fiyat politikası uyguluyor.
Sürekli var olan ~%46'lık baz indirim katmanı ve belirli dönemlerde %60'ı aşan kampanya katmanı. Kampanya dönemlerinde alışveriş yapmak gerçekten yaklaşık %14 ekstra avantaj sağlıyor.
4. Gerçek fırsat, kataloğun yalnızca %3'ünde.
10.628 ürünün 8.194'ü "Beklemek Mantıklı" kategorisinde. Sadece 346 ürün gerçek anlamda güçlü fırsat — yani platform genelinde her şey indirimli görünse de gerçekten avantajlı ürün sayısı çok küçük bir azınlık.
5. Fiyatlar haftalarca değişmiyor.
Tahmin modelinin en önemli bulgusu: geçen haftanın indirimi, bu haftanın indirimin %72'sini açıklıyor. Model "öğrenmek" yerine "kopyalamak" yapıyor — çünkü kopyalanacak kadar stabil bir yapı var.
6. Hangi ürün tipini ne zaman almalı?

Küme 2 (Oynak Fiyatlı): Kampanya dönemlerini bekle, fırsatı kaçırma
Küme 0 (Sürekli İndirimli): Geçmiş minimum fiyatına bak, anlık değil tarihsel konuma göre karar ver
Küme 1 (Stabil): Beklemek çok avantaj sağlamaz, ihtiyaç varsa al

---

## 🚀 Kurulum ve Çalıştırma

```bash
pip install -r requirements.txt
playwright install chromium

# Veri toplamak için
python gratis.py

# Dashboard için
streamlit run app.py
```

---



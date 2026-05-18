# 🛍️ Gratis Fiyat Davranışı Analizi
### Tüketici için Veri Odaklı Alışveriş Rehberi

> Gratis'te gerçekten indirimli olan ürünleri bulmak hiç bu kadar kolay olmamıştı.

🔗 **Canlı Uygulama:** [Streamlit Dashboard](https://gratis-indirim-takip-fczbse3yyhmdyev5mgkjzg.streamlit.app/)

---

## 📌 Proje Motivasyonu

Gratis ürünlerinin **%93'ü her zaman indirimli görünüyor.** Medyan indirim oranı ise **%50.**

Bu durum şu soruyu doğuruyor: *"Bu indirimler gerçek mi, yoksa fiyatlar zaten yüksek belirlenip yapay olarak indirimli mi gösteriliyor?"*

Bu proje, Gratis'teki fiyat davranışlarını veriyle inceleyerek tüketicinin gerçekten avantajlı ürünleri ayırt edebilmesi için bir **fırsat skoru sistemi** geliştirmeyi amaçlamaktadır.

---

## 📁 Proje Yapısı

```
gratis-indirim-takip/
│
├── data/
│   └── processed/
│       ├── gratis_clean.csv          # Temizlenmiş veri seti
│       ├── urun_ozellikleri.csv      # Ürün bazlı özellikler
│       ├── urun_kumeleri.csv         # Kümeleme sonuçları
│       └── urun_firsat_skorlari.csv  # Fırsat skorları
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
| Modelleme | Scikit-learn (K-Means, PCA, Random Forest, StandardScaler) |
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

---

## 🗂️ Analiz Aşamaları

### 1️⃣ Veri Toplama ve Temizlik

Playwright ile Gratis'in 14 kategorisi otomatik olarak tarandı. Her ürün için fiyat, eski fiyat, kampanya etiketi, yorum ve beğeni sayısı tarih damgasıyla SQLite'a kaydedildi.

**Temizlik adımları:**
- Tarih alanları `datetime` formatına dönüştürüldü
- `begeni` sütunu `"2B"`, `"13B"` gibi metin formatlarından sayısal değere çevrildi
- `eski_fiyat` ve `indirim_yuzde` boşlukları "indirim yok" olarak işaretlendi
- Aynı ürünün aynı gündeki birden fazla kaydından en güncel olanı tutuldu (47K satır azaltıldı)
- En az 5 farklı günde gözlemlenen ürünler filtrelendi

**İndirim hesaplama formülü:**
```
İndirim Oranı = (1 - fiyat / eski_fiyat) × 100
```
> Sitenin kendi indirim değeri yerine tutarlı karşılaştırma sağlamak için yeniden hesaplandı.

---

### 2️⃣ Keşifsel Veri Analizi (EDA)

**Temel bulgular:**

- Gözlemlerin **%93'ü indirimde** — indirim bir promosyon değil, kalıcı varsayılan hal
- İndirimler %40-60 bandında yoğunlaşıyor; **%50'de aşırı tepe** (28.000 gözlem)
- Yuvarlak indirim oranları (20%, 30%, 40%, 50%...) baskın → **psikolojik fiyatlama kanıtı**
- Gratis iki katmanlı strateji uyguluyor:
  - **Baz katman:** ~%46 sürekli indirim
  - **Kampanya katmanı:** %60+ dönemsel indirim (Nisan kampanyaları ile doğrulandı)

---

### 3️⃣ Özellik Mühendisliği ve K-Means Kümeleme

Her ürün için **12 davranışsal değişken** türetildi:

| Grup | Değişkenler |
|------|------------|
| Fiyat davranışı | `log_ortalama_fiyat`, `fiyat_araligi_orani`, `fiyat_degisim_orani`, `fiyat_std` |
| İndirim davranışı | `ortalama_indirim`, `max_indirim`, `indirim_std`, `indirimli_gun_orani` |
| Kampanya davranışı | `kampanyali_gun_orani`, `farkli_kampanya_sayisi` |
| Popülerlik & Kapsam | `populerlik_skoru`, `gozlem_sayisi` |

**Küme sayısı seçimi:**

Elbow ve Silhouette yöntemleri birlikte kullanıldı. k=2'de Silhouette skoru 0.46 ile en yüksek, ancak yalnızca iki profil tüketici için yeterince bilgilendirici değil. k=4'te Silhouette 0.18'e düşüyor. **k=3** hem matematiksel hem yorumlanabilirlik açısından optimal seçildi.

**3 Ürün Profili:**

| Küme | Profil | Ürün Sayısı | Temel Özellikler |
|------|--------|-------------|-----------------|
| 0 | Sürekli İndirimli Ana Katalog | 9.020 (%85) | İndirimli gün oranı %100, ortalama indirim %50 |
| 1 | Stabil ve Düşük Kampanyalı | 655 (%6) | Kampanyasız, fiyat hareketi sınırlı |
| 2 | Oynak Fiyatlı, Dönemsel Fırsat | 953 (%9) | Max indirim yüksek, indirimde gün oranı %38 |

---

### 4️⃣ Kural Tabanlı Fırsat Skorlaması

Her ürüne **0-100** arasında bir fırsat skoru atandı:

| Bileşen | Ağırlık | Açıklama |
|---------|---------|----------|
| Geçmiş fiyata göre avantaj | **%45** | Güncel fiyat geçmiş minimuma ne kadar yakın? |
| İndirim derinliği | **%30** | Güncel indirim oranı ne kadar yüksek? |
| Küme davranışı | **%15** | Ürünün profili fırsat potansiyeli taşıyor mu? |
| Kampanya bonusu | **%10** | Ürün aktif kampanyada mı? |

**Fırsat sınıfları:**

| Skor | Sınıf | Ürün Sayısı |
|------|-------|-------------|
| 80–100 | Çok Güçlü Fırsat | 346 |
| 60–79 | İyi Fırsat | 814 |
| 40–59 | Orta Seviye | 1.274 |
| 0–39 | Beklemek Mantıklı | 8.194 |

> 10.628 üründen yalnızca **346'sı** gerçek anlamda güçlü fırsat olarak belirlendi.

---

### 5️⃣ Deneysel Tahmin Modeli (Random Forest)

Gelecek haftanın indirim oranını tahmin etmek için Random Forest Regressor kullanıldı.

**Özellik önemi sonuçları:**

| Değişken | Gini Önem Skoru |
|----------|----------------|
| lag_1w_indirim (1 hafta önceki indirim) | **0.72** |
| lag_3w_indirim | 0.14 |
| rolling_std_indirim | 0.06 |
| Diğer tüm değişkenler | < 0.03 |

**Kritik bulgu:** Geçen haftanın indirimi tahminlerin %72'sini açıklıyor. Bu, Gratis'te fiyatların haftalarca sabit kaldığını gösteriyor — bu modelin bir başarısı değil, verinin yapısını ortaya koyan önemli bir bulgudur.

**Model performansı (validation seti):**
- Ortalama hata: **0.01** (tarafsız)
- Standart sapma: **4.55**

> Bu model üretim amaçlı değil, fiyat dinamiklerini anlamak için kullanılmıştır.

---

## 🚀 Kurulum ve Çalıştırma

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Playwright browser'ı yükle
playwright install chromium

# Scraper'ı çalıştır (veri toplama)
python gratis.py

# Streamlit uygulamasını başlat
streamlit run app.py
```

---

## 💡 Temel Çıkarımlar

1. **"İndirimde mi?" sorusu yanlış soru.** Gratis'te ürünlerin %93'ü her zaman indirimde. Doğru soru: *"Bu ürün kendi geçmiş fiyatına göre şu an avantajlı mı?"*

2. **%50 indirim bir pazarlama kararı.** 28.000 ürünün tam olarak %50 indirimde olması tesadüf değil — fiyat geriye doğru kurgulanmış.

3. **Gerçek fırsatlar küçük bir grupta.** 10.628 üründen yalnızca 346'sı güçlü fırsat kategorisinde.

4. **Kampanya zamanlaması önemli.** Kampanya dönemlerinde indirim derinliği ~%14 artıyor.

5. **Fiyatlar haftalarca sabit kalıyor.** Tahmin modelinin bulgusu: geçen haftanın indirimi bu haftanın indirimin %72'sini açıklıyor.

---

## ⚠️ Kısıtlar ve Notlar

- 21-26 Nisan tarihleri arasında veri toplanamadı (DEV FIRSAT kampanya dönemi)
- Deneysel tahmin modeli üretim için değil, fiyat dinamiklerini anlamak amacıyla geliştirildi
- Scraper, Gratis'in HTML yapısına bağımlıdır; site güncellemelerinde bakım gerektirebilir
- Veri 15 günlük snapshot'tan oluşmaktadır; daha uzun dönem verisiyle model güçlenebilir

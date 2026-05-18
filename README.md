# Gratis Fiyat Davranışı Analizi
> Tüketici için Veri Odaklı Alışveriş Rehberi

## 📌 Proje Hakkında

Bu proje, Gratis web sitesindeki ürünlerin fiyat ve indirim davranışlarını analiz etmek amacıyla geliştirilmiştir. Web scraping yöntemiyle toplanan günlük fiyat snapshot'ları kullanılarak ürünler davranışsal profillere ayrılmış ve her ürüne bir **fırsat skoru** atanmıştır.

🔗 **Canlı Uygulama:** [Streamlit Dashboard](https://gratis-indirim-takip-fczbse3yyhmdyev5mgkjzg.streamlit.app/)

---

## 📁 Proje Yapısı

```
gratis-fiyat-analizi/
│
├── data/
│   ├── gratis.db               # Ham SQLite veritabanı
│   └── processed/
│       ├── gratis_clean.csv    # Temizlenmiş veri
│       ├── urun_ozellikleri.csv
│       └── urun_kumeleri.csv
│
├── notebooks/
│   ├── 01_veri_yukleme_ve_temizlik.ipynb
│   ├── 02_kesifsel_analiz.ipynb
│   ├── 03_ozellik_muhendisligi_ve_kumeleme.ipynb
│   ├── 04_firsat_skoru_ve_sonuclar.ipynb
│   └── 05_indirim_tahmini_deneysel_model.ipynb
│
├── scraper/
│   └── gratis.py               # Web scraper
│
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
| Modelleme | Scikit-learn (K-Means, Random Forest, PCA) |
| Uygulama | Streamlit |

---

## 🗂️ Analiz Aşamaları

### 1. Veri Toplama
Playwright ile Gratis'in 14 kategorisi tarandı. Her ürün için fiyat, eski fiyat, kampanya etiketi, yorum ve beğeni sayısı toplandı. Veriler tarih damgasıyla SQLite'a kaydedildi.

**İndirim formülü:**
```
İndirim Oranı = (1 - fiyat / eski_fiyat) × 100
```

### 2. Keşifsel Veri Analizi
- 110.801 indirimli gözlem, medyan indirim: **%50**
- İndirimlerin %63'ü %40-60 bandında yoğunlaşıyor
- Zaman dinamiklerinde iki kampanya zirvesi tespit edildi (4 Nisan, 17 Nisan)

### 3. K-Means Kümeleme
12 davranışsal değişken üzerinden K-Means uygulandı. Elbow ve Silhouette analizleriyle **k=3** seçildi.

| Küme | Profil | Ürün Sayısı |
|------|--------|-------------|
| 0 | Sürekli İndirimli Ana Katalog | 9.020 (%85) |
| 1 | Stabil ve Düşük Kampanyalı | 655 (%6) |
| 2 | Oynak Fiyatlı, Dönemsel Fırsat | 953 (%9) |

### 4. Fırsat Skoru
Her ürüne 4 bileşenden oluşan bir skor atandı:

| Bileşen | Ağırlık |
|---------|---------|
| Fiyat avantajı (geçmiş min/max'a göre konum) | %45 |
| İndirim derinliği | %30 |
| Kampanya bonusu | %15 |
| Küme bonusu | %10 |

**Sonuç:** 10.628 üründen yalnızca **346'sı** "Çok Güçlü Fırsat" kategorisine girdi.

### 5. Deneysel Tahmin Modeli
Random Forest Regressor ile gelecek hafta indirim tahmini yapıldı. Lag özellikleri (1 hafta önceki indirim) dominant bulundu — bu, Gratis'te fiyatların zaman içinde çok az değiştiğini doğruluyor.

---

## 🚀 Kurulum ve Çalıştırma

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Playwright browser'ı yükle
playwright install chromium

# Scraper'ı çalıştır
python scraper/gratis.py
```

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

## ⚠️ Kısıtlar ve Notlar

- Veri 21-26 Nisan arasında toplanamadı (DEV FIRSAT kampanya dönemi)
- Deneysel tahmin modeli üretim için değil, fiyat dinamiklerini anlamak amacıyla geliştirildi
- Scraper, Gratis'in HTML yapısına bağımlıdır; site güncellemelerinde bakım gerektirebilir

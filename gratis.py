from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pandas as pd

BASE_URL = "https://www.gratis.com"

KATEGORILER = {
    "Makyaj": "/makyaj-c-501",
    "Cilt Bakım": "/cilt-bakim-c-502",
    "Saç Bakım": "/sac-bakim-c-503",
    "Parfüm & Deodorant": "/parfum-deodorant-c-504",
    "Erkek Bakım": "/erkek-bakim-c-505",
    "Kişisel Bakım": "/kisisel-bakim-c-506",
    "Anne & Bebek": "/anne-bebek-c-507",
    "Ev & Yaşam": "/ev-yasam-c-508",
    "Moda & Aksesuar": "/moda-aksesuar-c-509",
    "Süpermarket": "/supermarket-c-510",
    "Elektrikli Ürünler": "/elektrikli-urunler-c-511",
    "Duş & Banyo": "/dus-banyo-c-514",
    "Hijyen & Bakım": "/hijyen-bakim-c-515",
    "Güneş Ürünleri": "/gunes-urunleri-c-516",
}

def fiyat_parse(fiyat_str: str) -> float:
    if not fiyat_str:
        return None
    fiyat_str = fiyat_str.replace("TL", "").replace(".", "").replace(",", ".").strip()
    try:
        return float(re.sub(r"[^\d.]", "", fiyat_str))
    except:
        return None

def urun_id_cek(url: str) -> str:
    match = re.search(r"-p-(\d+)", url)
    return match.group(1) if match else None

def marka_cek(isim: str) -> str:
    if not isim:
        return None
    return isim.split()[0]

def kart_parse(kart, kategori_adi: str) -> dict:
    try:
        link_tag = kart.find("a", href=lambda h: h and "-p-" in h)
        if not link_tag:
            return None
        url = BASE_URL + link_tag.get("href")
        urun_id = urun_id_cek(url)

        isim_tag = kart.find("h5")
        isim = isim_tag.get_text(strip=True) if isim_tag else None

        yorum_sayisi = None
        yorum_tag = kart.find("span", class_=lambda c: c and "text-primary-700" in c)
        if yorum_tag:
            match = re.search(r"\((\d+)\)", yorum_tag.get_text(strip=True))
            if match:
                yorum_sayisi = int(match.group(1))

        begeni = None
        begeni_tag = kart.find("span", class_=lambda c: c and "text-[10px]" in c and "text-primary-850" in c)
        if begeni_tag:
            begeni = begeni_tag.get_text(strip=True)

        eski_fiyat = None
        eski_div = kart.find("div", class_=lambda c: c and "text-primary-500" in c)
        if eski_div:
            eski_fiyat = fiyat_parse(eski_div.get_text(strip=True))

        kampanya = None
        kampanya_div = kart.find("div", class_=lambda c: c and "text-nowrap" in c)
        if kampanya_div:
            kampanya = kampanya_div.get_text(strip=True)

        fiyat = None
        fiyat_span = kart.find("span", class_=lambda c: c and "text-[16px]" in c and "font-bold" in c and "text-primary-850" in c)
        if fiyat_span:
            fiyat = fiyat_parse(fiyat_span.get_text(strip=True))

        indirim = None
        if eski_fiyat and fiyat and eski_fiyat > fiyat:
            indirim = round((1 - fiyat / eski_fiyat) * 100, 1)

        if not isim or not fiyat:
            return None

        return {
            "urun_id": urun_id,
            "isim": isim,
            "marka": marka_cek(isim),
            "fiyat": fiyat,
            "eski_fiyat": eski_fiyat,
            "indirim_yuzde": indirim,
            "kampanya": kampanya,
            "yorum_sayisi": yorum_sayisi,
            "begeni": begeni,
            "kategori": kategori_adi,
            "url": url,
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    except:
        return None


def tum_kategorileri_tara():
    tum_urunler = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({"Accept-Language": "tr-TR,tr;q=0.9"})

        print("=== GRATİS SCRAPER BAŞLADI ===\n")

        for kategori_adi, kategori_url in KATEGORILER.items():
            print(f"Kategori: {kategori_adi}")
            sayfa = 1

            while True:
                if sayfa == 1:
                    url = f"{BASE_URL}{kategori_url}"
                else:
                    url = f"{BASE_URL}{kategori_url}?page={sayfa}"

                print(f"  Sayfa {sayfa} yükleniyor...")

                try:
                    page.goto(url, timeout=120000)
                    page.wait_for_load_state("load")
                    page.wait_for_timeout(2000)
                except Exception as e:
                    print(f"  Hata: {e}, atlaniyor...")
                    sayfa += 1
                    if sayfa > 200:
                        break
                    continue

                html = page.content()
                soup = BeautifulSoup(html, "html.parser")

                kartlar = soup.find_all("div", class_=lambda c: c and "relative flex flex-col justify-between border rounded-xl" in c)
                print(f"  {len(kartlar)} kart bulundu")

                if not kartlar:
                    print("  Sayfa boş, durduruluyor")
                    break

                onceki = len(tum_urunler)
                for kart in kartlar:
                    sonuc = kart_parse(kart, kategori_adi)
                    if sonuc:
                        tum_urunler.append(sonuc)

                yeni = len(tum_urunler) - onceki
                print(f"  {yeni} ürün eklendi, toplam: {len(tum_urunler)}")

                if yeni == 0:
                    print("  Yeni ürün yok, durduruluyor")
                    break

                sayfa += 1

        browser.close()

    print(f"\n=== TAMAMLANDI: {len(tum_urunler)} ürün ===")

    df = pd.DataFrame(tum_urunler)
    df = df.drop_duplicates(subset=["urun_id"], keep="first")
    print(f"Mükerrer temizlendi, kalan: {len(df)} ürün")

    dosya_adi = f"data/gratis_tum_urunler_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df.to_csv(dosya_adi, index=False, encoding="utf-8-sig", sep=";")
    print(f"CSV kaydedildi: {dosya_adi}")

    return df


if __name__ == "__main__":
    tum_kategorileri_tara()
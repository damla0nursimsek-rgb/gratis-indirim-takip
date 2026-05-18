from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import pandas as pd
import glob
import os

Base = declarative_base()

class FiyatKaydi(Base):
    __tablename__ = "fiyat_gecmisi"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    urun_id       = Column(String, nullable=False)
    isim          = Column(String)
    marka         = Column(String)
    kategori      = Column(String)
    fiyat         = Column(Float)
    eski_fiyat    = Column(Float)
    indirim_yuzde = Column(Float)
    kampanya      = Column(String)
    yorum_sayisi  = Column(Integer)
    begeni        = Column(String)
    url           = Column(String)
    tarih         = Column(String)
    kayit_zamani  = Column(DateTime, default=datetime.now)

def get_engine():
    return create_engine("sqlite:///data/gratis.db", echo=False)

def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Veritabanı hazır: data/gratis.db")
    return engine

def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def csv_den_aktar(csv_yolu: str):
    session = get_session()

    df = pd.read_csv(csv_yolu, sep=";", encoding="utf-8-sig")
    print(f"{len(df)} kayıt okundu")

    for _, row in df.iterrows():
        kayit = FiyatKaydi(
            urun_id       = str(row.get("urun_id", "")),
            isim          = row.get("isim"),
            marka         = row.get("marka"),
            kategori      = row.get("kategori"),
            fiyat         = row.get("fiyat"),
            eski_fiyat    = row.get("eski_fiyat"),
            indirim_yuzde = row.get("indirim_yuzde"),
            kampanya      = row.get("kampanya"),
            yorum_sayisi  = row.get("yorum_sayisi"),
            begeni        = row.get("begeni"),
            url           = row.get("url"),
            tarih         = row.get("tarih"),
        )
        session.add(kayit)

    session.commit()
    print(f"Veritabanına aktarıldı!")
    session.close()

if __name__ == "__main__":
    init_db()
    csv_dosyalari = glob.glob("data/gratis_tum_urunler_*.csv")
    if csv_dosyalari:
        en_son = max(csv_dosyalari, key=os.path.getmtime)
        print(f"Aktarılıyor: {en_son}")
        csv_den_aktar(en_son)
    else:
        print("CSV dosyası bulunamadı!")
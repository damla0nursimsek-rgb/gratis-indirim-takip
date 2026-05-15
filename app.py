import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from pathlib import Path

st.set_page_config(page_title="Gratis İndirim Takip", page_icon="🏷️", layout="wide")

st.markdown("""
<style>
.metric-card { background:#f8f9fa; border-radius:10px; padding:16px; text-align:center; border:1px solid #e9ecef; }
.metric-label { font-size:12px; color:#6c757d; margin-bottom:4px; }
.metric-value { font-size:28px; font-weight:600; color:#212529; }
.metric-sub   { font-size:11px; color:#28a745; margin-top:2px; }
</style>
""", unsafe_allow_html=True)

DATA_DIR = Path("data")

@st.cache_data
def load_data():
    ozet     = pd.read_csv(DATA_DIR/"ozet.csv", encoding="utf-8-sig")
    tahmin   = pd.read_csv(DATA_DIR/"gelecek_hafta_indirim_tahmini.csv", encoding="utf-8-sig")
    kume     = pd.read_csv(DATA_DIR/"urun_kumeleri.csv", encoding="utf-8-sig")
    dogruluk = pd.read_csv(DATA_DIR/"dogruluk_analizi.csv", encoding="utf-8-sig")
    return ozet, tahmin, kume, dogruluk

@st.cache_resource
def load_model():
    return joblib.load(DATA_DIR/"rf_model.pkl")

ozet_df, tahmin_df, kume_df, dogruluk_df = load_data()
model = load_model()

if "kategori_y" in tahmin_df.columns:
    tahmin_df["kategori"] = tahmin_df["kategori_y"].fillna(tahmin_df.get("kategori_x",""))
elif "kategori_x" in tahmin_df.columns:
    tahmin_df["kategori"] = tahmin_df["kategori_x"]

def indirim_etiketi(val):
    if val >= 40:   return "İndirime giriyor"
    elif val >= 15: return "Takipte tut"
    else:           return "İndirim beklenmiyor"

tahmin_df["durum"] = tahmin_df["tahmini_indirim"].apply(indirim_etiketi)

son_guncelleme = ozet_df["son_guncelleme"].iloc[0]
toplam_kayit   = int(ozet_df["toplam_kayit"].iloc[0])

with st.sidebar:
    st.markdown("### 🏷️ Gratis Takip")
    st.markdown("İndirim tahmin sistemi")
    st.markdown("---")
    sayfa = st.radio("Sayfa seç", [
        "🏠 Genel Özet", "🔍 Ürün Ara",
        "📊 Kategori Analizi", "🤖 Model Performansı"
    ], label_visibility="collapsed")
    st.markdown("---")
    st.markdown(f"**Son güncelleme:** {son_guncelleme}")
    st.markdown(f"**Toplam kayıt:** {toplam_kayit:,}")
    st.markdown(f"**Takip edilen ürün:** {len(tahmin_df):,}")

if sayfa == "🏠 Genel Özet":
    st.title("Genel Özet")
    st.caption("Gelecek hafta için tahmin edilen indirim durumu")
    indirime_giren = (tahmin_df["tahmini_indirim"] >= 40).sum()
    ort_indirim    = tahmin_df["tahmini_indirim"].mean()
    max_indirim    = tahmin_df["tahmini_indirim"].max()
    toplam_urun    = len(tahmin_df)
    c1,c2,c3,c4 = st.columns(4)
    for col, label, val, sub in [
        (c1, "Takip edilen ürün",    f"{toplam_urun:,}",       ""),
        (c2, "İndirim beklenen",     f"{indirime_giren:,}",    f"%{indirime_giren/toplam_urun*100:.1f} oran"),
        (c3, "Ort. tahmini indirim", f"%{ort_indirim:.1f}",    ""),
        (c4, "En yüksek tahmin",     f"%{max_indirim:.1f}",    ""),
    ]:
        with col:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Kategori bazında tahmini indirim")
        kat = tahmin_df.groupby("kategori")["tahmini_indirim"].mean().sort_values(ascending=True).reset_index()
        fig, ax = plt.subplots(figsize=(7,5))
        ax.barh(kat["kategori"], kat["tahmini_indirim"], color=plt.cm.Blues(np.linspace(0.4,0.85,len(kat))))
        for b,v in zip(ax.patches, kat["tahmini_indirim"]):
            ax.text(b.get_width()+0.3, b.get_y()+b.get_height()/2, f"%{v:.1f}", va="center", fontsize=9)
        ax.set_xlabel("Tahmini Ortalama İndirim (%)"); ax.set_xlim(0, kat["tahmini_indirim"].max()*1.2)
        ax.spines[["top","right"]].set_visible(False); plt.tight_layout(); st.pyplot(fig); plt.close()
    with col_r:
        st.subheader("En yüksek indirim beklenen 20 ürün")
        top20 = (tahmin_df[["isim","marka","kategori","tahmini_indirim","durum","cluster_adi"]]
                 .sort_values("tahmini_indirim", ascending=False).head(20).reset_index(drop=True))
        top20.index += 1
        top20.columns = ["Ürün Adı","Marka","Kategori","Tahmini İndirim (%)","Durum","Küme"]
        st.dataframe(top20, use_container_width=True, height=380)

elif sayfa == "🔍 Ürün Ara":
    st.title("Ürün Ara")
    c1,c2 = st.columns([2,1])
    with c1:
        arama = st.text_input("Ürün adı veya marka", placeholder="Örn: Flormar, maskara, Nivea...")
    with c2:
        kat_f = st.selectbox("Kategori", ["Tümü"] + sorted(tahmin_df["kategori"].dropna().unique().tolist()))
    sonuc = tahmin_df.copy()
    if arama:
        sonuc = sonuc[sonuc["isim"].str.contains(arama, case=False, na=False) |
                      sonuc["marka"].str.contains(arama, case=False, na=False)]
    if kat_f != "Tümü":
        sonuc = sonuc[sonuc["kategori"] == kat_f]
    sonuc = sonuc.sort_values("tahmini_indirim", ascending=False).reset_index(drop=True)
    sonuc.index += 1
    st.markdown(f"**{len(sonuc):,} ürün bulundu**")
    if len(sonuc):
        goster = sonuc[["isim","marka","kategori","tahmini_indirim","durum","cluster_adi"]].copy()
        goster.columns = ["Ürün Adı","Marka","Kategori","Tahmini İndirim (%)","Durum","Küme"]
        def renk(val):
            if val == "İndirime giriyor": return "background-color:#d4edda;color:#155724"
            elif val == "Takipte tut":    return "background-color:#fff3cd;color:#856404"
            return "background-color:#f8d7da;color:#721c24"
        st.dataframe(goster.style.applymap(renk, subset=["Durum"]), use_container_width=True, height=500)
    else:
        st.info("Arama kriterlerine uygun ürün bulunamadı.")

elif sayfa == "📊 Kategori Analizi":
    st.title("Kategori & Küme Analizi")
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Küme × Kategori heatmap")
        pivot = tahmin_df.groupby(["cluster_adi","kategori"])["tahmini_indirim"].mean().unstack(fill_value=0)
        fig, ax = plt.subplots(figsize=(7,4))
        sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlOrRd", linewidths=0.5, ax=ax,
                    cbar_kws={"label":"Tahmini İndirim (%)"})
        ax.set_xlabel(""); ax.set_ylabel("")
        ax.tick_params(axis="x", rotation=45); ax.tick_params(axis="y", rotation=0)
        plt.tight_layout(); st.pyplot(fig); plt.close()
    with col_r:
        st.subheader("Top 15 marka — tahmini indirim")
        marka = (tahmin_df.groupby("marka")
                 .agg(ort=("tahmini_indirim","mean"), n=("urun_id","count"))
                 .query("n >= 3").sort_values("ort", ascending=True).tail(15).reset_index())
        fig, ax = plt.subplots(figsize=(7,5))
        ax.barh(marka["marka"], marka["ort"], color=plt.cm.Oranges(np.linspace(0.4,0.85,len(marka))))
        for b,v in zip(ax.patches, marka["ort"]):
            ax.text(b.get_width()+0.3, b.get_y()+b.get_height()/2, f"%{v:.1f}", va="center", fontsize=9)
        ax.set_xlabel("Tahmini Ortalama İndirim (%)"); ax.set_xlim(0, marka["ort"].max()*1.2)
        ax.spines[["top","right"]].set_visible(False); plt.tight_layout(); st.pyplot(fig); plt.close()
    st.subheader("Durum dağılımı")
    durum = tahmin_df["durum"].value_counts().reset_index()
    durum.columns = ["Durum","Ürün Sayısı"]
    renkler = {"İndirime giriyor":("#d4edda","#155724"),
               "Takipte tut":("#fff3cd","#856404"),
               "İndirim beklenmiyor":("#f8d7da","#721c24")}
    cols = st.columns(len(durum))
    for i, (_,row) in enumerate(durum.iterrows()):
        bg,fg = renkler.get(row["Durum"],("#f8f9fa","#212529"))
        with cols[i]:
            st.markdown(f"""<div class="metric-card" style="background:{bg}">
                <div class="metric-label" style="color:{fg}">{row["Durum"]}</div>
                <div class="metric-value" style="color:{fg}">{row["Ürün Sayısı"]:,}</div>
            </div>""", unsafe_allow_html=True)

elif sayfa == "🤖 Model Performansı":
    st.title("Model Performansı")
    st.caption("Validation haftası tahmin doğruluğu")
    c1,c2,c3 = st.columns(3)
    for col,lbl,val,sub in [
        (c1,"MAE","2.20","±2.2 puan hata payı"),
        (c2,"RMSE","4.46",""),
        (c3,"R²","0.923","%92.3 doğruluk"),
    ]:
        with col:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">{lbl}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col_l,col_r = st.columns(2)
    with col_l:
        st.subheader("Tahmin doğruluğu (±5 puan)")
        dogru  = int(dogruluk_df["dogru_mu"].sum())
        yanlis = len(dogruluk_df) - dogru
        fig,ax = plt.subplots(figsize=(5,4))
        ax.pie([dogru,yanlis], labels=[f"Doğru\n{dogru:,}",f"Yanlış\n{yanlis:,}"],
               colors=["#28a745","#dc3545"], autopct="%1.1f%%", startangle=90,
               textprops={"fontsize":11})
        plt.tight_layout(); st.pyplot(fig); plt.close()
    with col_r:
        st.subheader("Kategori bazında doğruluk")
        kd = dogruluk_df.groupby("kategori")["dogru_mu"].mean().sort_values().reset_index()
        fig,ax = plt.subplots(figsize=(6,4))
        renkler = ["#dc3545" if v<0.7 else "#ffc107" if v<0.85 else "#28a745" for v in kd["dogru_mu"]]
        ax.barh(kd["kategori"], kd["dogru_mu"]*100, color=renkler)
        ax.axvline(80, color="gray", linestyle="--", linewidth=1)
        ax.set_xlabel("Doğruluk (%)")
        for b,v in zip(ax.patches, kd["dogru_mu"]):
            ax.text(b.get_width()+0.5, b.get_y()+b.get_height()/2, f"%{v*100:.1f}", va="center", fontsize=9)
        ax.spines[["top","right"]].set_visible(False); plt.tight_layout(); st.pyplot(fig); plt.close()
    st.subheader("Hata dağılımı")
    fig,ax = plt.subplots(figsize=(10,3))
    ax.hist(dogruluk_df["hata"], bins=60, color="steelblue", edgecolor="white", linewidth=0.4)
    ax.axvline(5, color="red", linestyle="--", linewidth=1.5, label="±5 puan tolerans")
    ax.axvline(dogruluk_df["hata"].mean(), color="orange", linestyle="--",
               linewidth=1.5, label=f"Ort. hata: {dogruluk_df['hata'].mean():.1f}")
    ax.set_xlabel("Mutlak Hata (puan)"); ax.set_ylabel("Ürün Sayısı")
    ax.legend(); ax.spines[["top","right"]].set_visible(False)
    plt.tight_layout(); st.pyplot(fig); plt.close()

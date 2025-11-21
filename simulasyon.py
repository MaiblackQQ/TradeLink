import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- Sayfa Ayarları ---
st.set_page_config(page_title="Trader Gelişim Günlüğü", layout="wide")

# --- Özel CSS ---
st.markdown("""
<style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
</style>
""", unsafe_allow_html=True)

# --- Başlık ---
st.title("🧠 Trader Strateji ve Gelişim Arşivi")
st.markdown("Kendi setlerini kaydet, geriye dönük incele ve en iyi çalıştığın kurulumları keşfet.")

# --- Dosya ve Klasör Yönetimi ---
FILE_NAME = "trading_journal.csv"
IMAGE_FOLDER = "images"

# Eğer resim klasörü yoksa oluştur
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

def load_data():
    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        # Eğer eski dosyada 'Görsel' sütunu yoksa hata vermemesi için ekleyelim
        if "Görsel" not in df.columns:
            df["Görsel"] = None
        return df
    else:
        return pd.DataFrame(columns=[
            "Tarih", "Parite", "Yön", "Strateji", "Giriş", "Çıkış", 
            "Durum", "PnL", "Duygu", "Notlar", "Görsel"
        ])

df = load_data()

# --- SOL MENÜ: İşlem Kayıt Paneli ---
st.sidebar.header("📝 Yeni Set Kaydet")

with st.sidebar.form("trade_entry_form", clear_on_submit=True):
    st.sidebar.subheader("1. İşlem Detayları")
    symbol = st.text_input("Parite (Örn: BTC, XAU)", "BTCUSDT")
    direction = st.selectbox("Yön", ["Long", "Short"])
    
    strategy = st.selectbox("Kullandığın Setup/Strateji", 
                            ["Trend Kırılımı", "Destek/Direnç Dönüşü", "Supply/Demand", "Fakeout", "RSI Uyumsuzluk", "Diğer"])
    
    entry_price = st.number_input("Giriş Fiyatı", min_value=0.0, format="%.4f")
    exit_price = st.number_input("Çıkış Fiyatı", min_value=0.0, format="%.4f")
    
    st.sidebar.subheader("2. Sonuç ve Psikoloji")
    status = st.selectbox("Sonuç", ["Win", "Loss", "Break-Even"])
    pnl = st.number_input("Kâr/Zarar (Miktar veya R)", format="%.2f")
    
    emotion = st.selectbox("İşlem Anındaki Duygu", ["Sakin/Planlı", "FOMO (Kaçırma Korkusu)", "İntikam İşlemi", "Tereddütlü", "Aşırı Özgüven"])
    
    notes = st.text_area("Dersler & Notlar (Neyi doğru/yanlış yaptın?)")
    
    # Resim yükleme
    uploaded_file = st.file_uploader("Grafik Ekran Görüntüsü", type=['png', 'jpg', 'jpeg'])
    
    submit_button = st.form_submit_button("Arşive Ekle")

    if submit_button:
        # Resim Kaydetme İşlemi
        image_path = None
        if uploaded_file is not None:
            # Benzersiz bir dosya adı oluştur (Çakışmayı önlemek için tarih ekliyoruz)
            file_ext = uploaded_file.name.split('.')[-1]
            file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
            image_path = os.path.join(IMAGE_FOLDER, file_name)
            
            # Dosyayı diske yaz
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        new_data = {
            "Tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Parite": symbol,
            "Yön": direction,
            "Strateji": strategy,
            "Giriş": entry_price,
            "Çıkış": exit_price,
            "Durum": status,
            "PnL": pnl,
            "Duygu": emotion,
            "Notlar": notes,
            "Görsel": image_path # Dosya yolunu kaydediyoruz
        }
        
        # Pandas concat ile veri ekleme (FutureWarning önlemek için liste içinde DF)
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_csv(FILE_NAME, index=False)
        st.sidebar.success("Set ve grafik başarıyla kaydedildi! 🚀")
        st.rerun() # Sayfayı
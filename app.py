import streamlit as st
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="Dolap Şefi", page_icon="👨‍🍳", layout="centered")

# --- ÖZEL TASARIM (Dark Mode Uyumlu CSS) ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        border-radius: 12px;
        padding: 15px;
        font-size: 20px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #D93030;
        transform: scale(1.02);
    }
    h1 {
        text-align: center;
        font-family: 'Helvetica', sans-serif;
        margin-bottom: 0px;
    }
    .subtitle {
        text-align: center;
        opacity: 0.8;
        font-size: 18px;
        margin-bottom: 30px;
    }
    /* Kart Tasarımı */
    .card {
        background-color: #262730;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #444;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
st.markdown("<h1>👨‍🍳 Dolap Şefi</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Evdeki malzemeleri seç, sana özel gurme tarifleri hemen önüne getireyim.</p>", unsafe_allow_html=True)

# --- VERİ TABANI ---
try:
    df = pd.read_csv("menu.csv", sep=";")
except:
    st.error("Menü dosyası okunamadı.")
    st.stop()

# --- ORTA ALAN (SEÇİM) ---
col1, col2 = st.columns([3, 1])
tum_malzemeler = set()
for item in df['Malzemeler']:
    if isinstance(item, str):
        malzemeler = [x.strip() for x in item.replace(';', ',').split(',')]
        tum_malzemeler.update(malzemeler)

with col1:
    secilenler = st.multiselect('Dolabında neler var?', sorted(list(tum_malzemeler)), placeholder="Örn: Yumurta, Domates...")
with col2:
    st.write("")
    st.write("")
    butce_modu = st.checkbox("💸 Öğrenci İşi")

st.write("")
bul_butonu = st.button('🍳 BANA TARİF BUL')
st.markdown("---")

# --- SONUÇLAR ---
if bul_butonu:
    if not secilenler:
        st.warning("⚠️ Şefim, boş dolapla yemek olmaz! Malzeme seçmelisin.")
    else:
        eslesenler = []
        for index, row in df.iterrows():
            if isinstance(row['Malzemeler'], str):
                gerekli = set([x.strip() for x in row['Malzemeler'].replace(';', ',').split(',')])
                elimdeki = set(secilenler)
                if gerekli.intersection(elimdeki):
                    eslesenler.append(row)
        
        if eslesenler:
            st.success(f"🎉 {len(eslesenler)} tarif bulundu.")
            for yemek in eslesenler:
                if butce_modu and yemek['Maliyet'] > 50: continue
                
                # KART TASARIMI
                with st.container():
                    st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                    c1, c2 = st.columns([1, 2])
                    
                    with c1:
                        # --- ACİL DURUM RESMİ (KÖKTEN ÇÖZÜM) ---
                        # CSV'deki link bozuksa bile bu kesin çalışır.
                        st.image("https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&q=80", use_container_width=True)
                            
                    with c2:
                        st.subheader(f"🍽 {yemek['Yemek Adı']}")
                        st.caption(f"⏱ {yemek['Zorluk']} | 🔥 {yemek['Kalori']} kcal | 💰 {yemek['Maliyet']} TL")
                        st.write(f"**Malzemeler:** {yemek['Malzemeler']}")
                        if 'Tarif' in yemek and pd.notna(yemek['Tarif']):
                             with st.expander("👨‍🍳 Tarifi Gör"): st.write(yemek['Tarif'])
                        st.markdown(f"""<a href="{yemek['Link']}" target="_blank" style="text-decoration:none;"><div style="background-color:#f27a1a; color:white; padding:10px; text-align:center; border-radius:8px; font-weight:bold; margin-top:10px; width:100%;">🛒 Eksik Malzemeleri Sipariş Et</div></a>""", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("😔 Eşleşen tarif bulunamadı.")

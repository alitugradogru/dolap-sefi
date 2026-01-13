import streamlit as st
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="Dolap Şefi", page_icon="👨‍🍳", layout="centered")

# --- ÖZEL TASARIM ---
st.markdown("""
    <style>
    /* Ana Buton (Tarif Bul) Rengi - Turuncu */
    .stButton>button {
        width: 100%;
        background-color: #f27a1a;
        color: white;
        font-weight: bold;
        border-radius: 12px;
        padding: 15px;
        font-size: 20px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #d66912; /* Üzerine gelince koyu turuncu */
        transform: scale(1.02);
    }
    
    h1 { text-align: center; font-family: 'Helvetica', sans-serif; margin-bottom: 0px; }
    .subtitle { text-align: center; opacity: 0.8; font-size: 18px; margin-bottom: 30px; }
    
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

# --- AKILLI RESİM FONKSİYONU 🧠 ---
def get_smart_image(yemek_adi):
    yemek_adi = yemek_adi.lower()
    # Kategoriye göre otomatik resim seçimi (Unsplash'tan çalışan linkler)
    if "tavuk" in yemek_adi or "kanat" in yemek_adi:
        return "https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?w=800&q=80" # Tavuk
    elif "balık" in yemek_adi or "somon" in yemek_adi or "hamsi" in yemek_adi:
        return "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=800&q=80" # Balık
    elif "makarna" in yemek_adi or "erişte" in yemek_adi:
        return "https://images.unsplash.com/photo-1551183053-bf91b1dca038?w=800&q=80" # Makarna
    elif "yumurta" in yemek_adi or "menemen" in yemek_adi or "omlet" in yemek_adi:
        return "https://images.unsplash.com/photo-1525351484163-7529414395d8?w=800&q=80" # Yumurta
    elif "köfte" in yemek_adi or "burger" in yemek_adi:
        return "https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=800&q=80" # Et/Köfte
    elif "salata" in yemek_adi or "piyaz" in yemek_adi:
        return "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&q=80" # Salata
    elif "çorba" in yemek_adi:
        return "https://images.unsplash.com/photo-1547592166-23acbe34001b?w=800&q=80" # Çorba
    elif any(x in yemek_adi for in ["kek", "pasta", "tatlı", "helva", "sütlaç", "magnolia"]):
        return "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=800&q=80" # Tatlı
    elif "pilav" in yemek_adi or "bulgur" in yemek_adi:
        return "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=800&q=80" # Pilav/Bakliyat
    else:
        return "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&q=80" # Varsayılan (Bowl)

# --- VERİ TABANI ---
try:
    df = pd.read_csv("menu.csv", sep=";")
except:
    st.error("Menü dosyası okunamadı.")
    st.stop()

# --- ORTA ALAN ---
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
                
                # --- RESİM SEÇİMİ ---
                # Önce CSV'deki linke bakar, bozuksa veya yoksa Akıllı Seçim yapar
                img_url = str(row['Resim'])
                if not img_url.startswith("http") and not img_url.startswith("img/"):
                     # Link yoksa akıllı tahmini kullan
                     img_url = get_smart_image(row['Yemek Adı'])
                elif img_url.startswith("http") and "yemek.com" in img_url:
                     # Yemek.com linkleri bozuk olduğu için direkt akıllıya geç
                     img_url = get_smart_image(row['Yemek Adı'])
                
                with st.container():
                    st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.image(img_url, use_container_width=True)
                    with c2:
                        st.subheader(f"🍽 {yemek['Yemek Adı']}")
                        st.caption(f"⏱ {yemek['Zorluk']} | 🔥 {yemek['Kalori']} kcal | 💰 {yemek['Maliyet']} TL")
                        st.write(f"**Malzemeler:** {yemek['Malzemeler']}")
                        if 'Tarif' in yemek and pd.notna(yemek['Tarif']):
                             with st.expander("👨‍🍳 Tarifi Gör"): st.write(yemek['Tarif'])
                        
                        # --- TURUNCU BUTON ---
                        st.markdown(f"""
                            <a href="{yemek['Link']}" target="_blank" style="text-decoration:none;">
                                <div style="background-color:#f27a1a; color:white; padding:10px; text-align:center; border-radius:8px; font-weight:bold; margin-top:10px; width:100%;">
                                🛒 Eksik Malzemeleri Sipariş Et
                                </div>
                            </a>
                        """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("😔 Eşleşen tarif bulunamadı.")

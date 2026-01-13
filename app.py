import streamlit as st
import pandas as pd
import random

# Sayfa Ayarları (Başlık ve Genişlik)
st.set_page_config(page_title="Dolap Şefi", page_icon="👨‍🍳", layout="centered")

# --- ÖZEL TASARIM (CSS) ---
# Burası siteyi "Yapay Zeka" havasından kurtarıp "Modern Web Sitesi" yapan makyaj kısmı
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        border-radius: 12px;
        padding: 15px;
        font-size: 20px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #D93030;
        color: white;
    }
    h1 {
        text-align: center;
        color: #1E1E1E;
        font-family: 'Helvetica', sans-serif;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 18px;
        margin-bottom: 30px;
    }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- BAŞLIK KISMI (HERO SECTION) ---
st.markdown("<h1>👨‍🍳 Dolap Şefi</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Evdeki malzemeleri seç, sana özel gurme tarifleri hemen önüne getireyim.</p>", unsafe_allow_html=True)

# --- VERİ TABANI ---
try:
    df = pd.read_csv("menu.csv", sep=";")
except:
    st.error("Menü dosyası okunamadı. Lütfen GitHub'daki 'menu.csv' dosyasını kontrol et.")
    st.stop()

# --- ORTA ALAN (MALZEME SEÇİMİ) ---
# Artık Sidebar yok! Her şey ortada.
with st.container():
    st.markdown("<div style='background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
    
    # Malzemeleri topla
    tum_malzemeler = set()
    for item in df['Malzemeler']:
        # Virgül veya noktalı virgül karmaşasını temizle
        if isinstance(item, str):
            malzemeler = [x.strip() for x in item.replace(';', ',').split(',')]
            tum_malzemeler.update(malzemeler)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        secilenler = st.multiselect(
            'Dolabında neler var?', 
            sorted(list(tum_malzemeler)),
            placeholder="Örn: Yumurta, Domates..."
        )
    with col2:
        st.write("") # Boşluk
        st.write("") # Boşluk
        butce_modu = st.checkbox("💸 Öğrenci İşi")
    
    bul_butonu = st.button('🍳 BANA TARİF BUL')
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# --- SONUÇLAR ---
if bul_butonu:
    if not secilenler:
        st.warning("⚠️ Şefim, boş dolapla yemek olmaz! Yukarıdan en az bir malzeme seçmelisin.")
    else:
        eslesenler = []
        for index, row in df.iterrows():
            if isinstance(row['Malzemeler'], str):
                gerekli = set([x.strip() for x in row['Malzemeler'].replace(';', ',').split(',')])
                elimdeki = set(secilenler)
                # Malzemelerden en az biri varsa getir
                if gerekli.intersection(elimdeki):
                    eslesenler.append(row)
        
        if eslesenler:
            st.success(f"🎉 Harika! Senin için {len(eslesenler)} lezzetli tarif buldum.")
            
            # Kart Görünümü
            for yemek in eslesenler:
                if butce_modu and yemek['Maliyet'] > 50: continue

                # --- RESİM ÇÖZÜMÜ ---
                # Eğer resim linki yoksa veya bozuksa, şu standart resmi göster:
                img_url = yemek['Resim']
                if not str(img_url).startswith("http") and not str(img_url).startswith("img/"):
                    # Kırık resim yerine gösterilecek varsayılan resim
                    img_url = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&q=80"
                
                with st.container():
                    st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                    c1, c2 = st.columns([1, 2])
                    
                    with c1:
                        # Resim hatası olursa site çökmesin diye try-except bloklaması
                        try:
                            st.image(img_url, use_container_width=True)
                        except:
                            st.image("https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&q=80", use_container_width=True)
                            
                    with c2:
                        st.subheader(f"🍽 {yemek['Yemek Adı']}")
                        st.caption(f"⏱ {yemek['Zorluk']}  |  🔥 {yemek['Kalori']} kcal  |  💰 {yemek['Maliyet']} TL")
                        st.write(f"**Gerekli Malzemeler:** {yemek['Malzemeler']}")
                        
                        st.markdown(f"""
                            <a href="{yemek['Link']}" target="_blank" style="text-decoration:none;">
                                <div style="background-color:#f27a1a; color:white; padding:10px; text-align:center; border-radius:8px; font-weight:bold; margin-top:10px;">
                                🛒 Eksik Malzemeleri Sipariş Et
                                </div>
                            </a>
                        """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("😔 Üzgünüm, bu malzemelerle eşleşen bir tarif bulamadım. Biraz daha malzeme eklemeyi dene!")

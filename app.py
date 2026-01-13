import streamlit as st
import google.generativeai as genai

# Sayfa Ayarları
st.set_page_config(page_title="Dolap Şefi AI", page_icon="👨‍🍳", layout="centered")

# --- TASARIM ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; background-color: #f27a1a; color: white; padding: 15px; border-radius: 12px; border: none; font-weight: bold; font-size: 18px; transition: 0.3s; }
    .stButton>button:hover { background-color: #d66912; transform: scale(1.02); }
    .card { background-color: #262730; padding: 20px; border-radius: 15px; border: 1px solid #444; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Dolap Şefi: AI Modu")

# --- GÜVENLİK VE AYARLAR ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("🚨 API Anahtarı bulunamadı! Lütfen Streamlit Secrets ayarlarını kontrol et.")
    st.stop()

# --- DEDEKTİF MODU (MOD EL SEÇİMİ) 🕵️‍♂️ ---
# Burası hatayı çözen kısım. Modele biz karar vermiyoruz, sisteme soruyoruz.
try:
    genai.configure(api_key=api_key)
    
    # Sol menüye bilgi basalım (Hata ayıklamak için)
    with st.sidebar:
        st.caption(f"🔧 Kütüphane Sürümü: {genai.__version__}")
        
        # Google'a sor: Hangi modellerin var?
        uygun_modeller = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                uygun_modeller.append(m.name)
        
        # En iyi modeli otomatik seç
        secilen_model = ""
        if 'models/gemini-1.5-flash' in uygun_modeller:
            secilen_model = 'gemini-1.5-flash'
        elif 'models/gemini-pro' in uygun_modeller:
            secilen_model = 'gemini-pro'
        elif uygun_modeller:
            secilen_model = uygun_modeller[0] # Listede ne varsa onu al
            
        st.success(f"✅ Bağlanan Beyin: {secilen_model}")

except Exception as e:
    st.sidebar.error(f"Bağlantı Hatası: {e}")
    secilen_model = None

# --- EKRAN VE İŞLEM ---
malzemeler = st.text_input("Dolabında neler var?", placeholder="Örn: Yumurta, soğan, salça...")
butce_modu = st.checkbox("💸 Öğrenci İşi")
generate_btn = st.button("✨ Yapay Zekaya Tarif Yazdır")

if generate_btn:
    if not secilen_model:
        st.error("⚠️ Uygun bir yapay zeka modeli bulunamadı. Lütfen sayfayı yenile.")
    elif not malzemeler:
        st.warning("⚠️ Malzeme yazmadın şefim!")
    else:
        try:
            with st.spinner("👨‍🍳 Şef düşünüyor..."):
                model = genai.GenerativeModel(secilen_model)
                ozellik = "öğrenci dostu, ucuz" if butce_modu else "lezzetli"
                
                prompt = f"""
                Sen bir şefsin. Malzemeler: {malzemeler}.
                Bana {ozellik} tek bir yemek tarifi ver.
                Format:
                YEMEK ADI: ...
                KATEGORİ: (Tavuk/Et/Sebze/Tatlı/Makarna/Genel)
                TARİF: ...
                """
                
                response = model.generate_content(prompt)
                text = response.text
                
                # Basit Parçalama
                yemek_adi = "Sürpriz Yemek"
                kategori = "Genel"
                if "YEMEK ADI:" in text:
                    for line in text.split('\n'):
                        if "YEMEK ADI:" in line: yemek_adi = line.replace("YEMEK ADI:", "").strip()
                        if "KATEGORİ:" in line: kategori = line.replace("KATEGORİ:", "").strip()

                # Resim Seçimi
                img_map = {
                    "tavuk": "https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?w=800&q=80",
                    "et": "https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=800&q=80",
                    "makarna": "https://images.unsplash.com/photo-1551183053-bf91b1dca038?w=800&q=80",
                    "tatlı": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=800&q=80"
                }
                # Kategoriyi bulamazsa varsayılan resim
                img_url = next((v for k, v in img_map.items() if k in kategori.lower()), "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&q=80")

                st.balloons()
                with st.container():
                    st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                    st.image(img_url, use_container_width=True)
                    st.header(f"🍽 {yemek_adi}")
                    st.write(text.replace(f"YEMEK ADI: {yemek_adi}", "").strip())
                    st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Hata oluştu: {e}")

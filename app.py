import streamlit as st
import google.generativeai as genai

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Dolap Şefi", page_icon="👨‍🍳", layout="centered")

# --- TASARIM ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #0f2027, #203a43, #2c5364); color: white; }
    h1 { text-align: center; color: #f27a1a; }
    .stButton>button { background-color: #28a745; color: white; border-radius: 10px; height: 50px; font-size: 18px; font-weight: bold; border: none; width: 100%; }
    .stButton>button:hover { background-color: #218838; }
    .error-box { background-color: #ff4b4b; color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
st.title("👨‍🍳 Dolap Şefi")
st.caption("Yapay Zeka Destekli Sosyal Mutfak")

# --- API ANAHTARI ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Google API Key", type="password")

# --- MODEL BAĞLANTISI (AKILLI SEÇİM) ---
model = None
active_model_name = "Bilinmiyor"

if api_key:
    genai.configure(api_key=api_key)
    
    # Sırayla bu modelleri deneyeceğiz. Hangisi çalışırsa onu kapacak.
    model_listesi = ['gemini-1.5-flash', 'gemini-pro', 'gemini-1.0-pro']
    
    for m in model_listesi:
        try:
            test_model = genai.GenerativeModel(m)
            # Ufak bir "Merhaba" diyip test edelim
            # test_model.generate_content("test") # Bunu kapattım kota yemesin diye
            model = test_model
            active_model_name = m
            break # Çalışanı bulduk, döngüden çık
        except:
            continue # Bu çalışmadı, sıradakine geç

# --- ARAYÜZ ---
tab1, tab2 = st.tabs(["🔥 Şef'e Sor", "🌟 Vitrin"])

with tab1:
    malzemeler = st.text_input("Dolapta ne var?", placeholder="Örn: Yumurta, soğan, peynir...")
    
    if st.button("🍳 Tarif Bul"):
        if not api_key:
            st.error("⚠️ API Anahtarı eksik!")
        elif not malzemeler:
            st.warning("⚠️ Malzeme girmedin!")
        elif not model:
            # Hiçbir model çalışmadıysa burası çalışır
            st.markdown(f"<div class='error-box'>🔴 HATA: Hiçbir yapay zeka modeline bağlanılamadı. API Anahtarını ve Kota durumunu kontrol et.</div>", unsafe_allow_html=True)
        else:
            with st.spinner(f"Şef düşünüyor... (Kullanılan Beyin: {active_model_name})"):
                try:
                    prompt = f"Malzemeler: {malzemeler}. Bana Türk damak tadına uygun, lezzetli TEK BİR yemek tarifi ver. Adını, malzemelerini ve yapılışını güzelce yaz."
                    response = model.generate_content(prompt)
                    st.success("Tarif Hazır!")
                    st.markdown(response.text)
                    
                    # Trendyol Linki
                    link = f"https://www.trendyol.com/sr?q={malzemeler.split(',')[0]}"
                    st.markdown(f"""<br><a href="{link}" target="_blank" style="background: #f27a1a; color: white; padding: 12px; text-decoration: none; border-radius: 8px; display: block; text-align: center; font-weight: bold;">🛒 Malzemeleri Trendyol'dan Al</a>""", unsafe_allow_html=True)
                
                except Exception as e:
                    # Hatayı gizlemiyoruz, direkt gösteriyoruz
                    st.error(f"BEKLENMEDİK HATA: {e}")

with tab2:
    st.info("Bu alan şu an demo aşamasındadır.")
    st.markdown("### 🍝 Örnek: Fırın Makarna (Şef: Berkecan)")
    st.video("https://www.w3schools.com/html/mov_bbb.mp4")

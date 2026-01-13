import streamlit as st
import requests
import json
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Dolap Şefi", page_icon="👨‍🍳", layout="centered")

# --- HAFIZA ---
if 'oneriler' not in st.session_state: st.session_state.oneriler = []
if 'tam_tarif' not in st.session_state: st.session_state.tam_tarif = ""

# --- TASARIM (AYNI KALDI) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #0f2027, #203a43, #2c5364); color: white; }
    h1 { text-align: center; color: #f27a1a; font-family: 'Arial Black', sans-serif; text-shadow: 2px 2px 4px #000000; }
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 15px; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(255,255,255,0.1); border-radius: 8px; color: white; padding: 10px 20px; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #f27a1a; color: white; }
    .buy-btn { display: block; width: 100%; background-color: #28a745; color: white; text-align: center; padding: 15px; border-radius: 10px; font-weight: bold; text-decoration: none; margin-top: 20px; font-size: 18px; transition: 0.3s; }
    .buy-btn:hover { background-color: #218838; transform: scale(1.02); }
    .vitrin-card { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; margin-bottom: 20px; border-left: 5px solid #f27a1a; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 50px; }
    </style>
""", unsafe_allow_html=True)

# --- API ANAHTARI ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Google API Key", type="password")

# --- AKILLI FONKSİYON (TANK MODU 🛡️) ---
def yapay_zekaya_sor(prompt, key):
    # Sırayla denenecek modeller. Biri bozuksa diğeri devreye girer.
    modeller = ["gemini-1.5-flash", "gemini-pro", "gemini-1.0-pro"]
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    hata_mesaji = ""
    
    for model_ismi in modeller:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_ismi}:generateContent?key={key}"
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                # Başarılı olduysa hemen cevabı döndür ve döngüden çık
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                # Hata aldıysak not et ve bir sonraki modele geç
                hata_mesaji = f"Model ({model_ismi}) Hatası: {response.status_code}"
                continue 
                
        except Exception as e:
            hata_mesaji = f"Bağlantı sorunu: {str(e)}"
            continue

    # Hiçbiri çalışmadıysa son hatayı döndür
    return f"⚠️ Üzgünüm, Google sunucularına ulaşılamadı. Son hata: {hata_mesaji}"

# --- BAŞLIK ---
st.title("👨‍🍳 Dolap Şefi")
st.markdown("<p style='text-align: center; opacity: 0.8;'>Yapay Zeka Destekli Sosyal Mutfak Platformu</p>", unsafe_allow_html=True)

# --- SEKMELER ---
tab1, tab2 = st.tabs(["🔥 Şef'e Sor (AI)", "🌟 Sizden Gelenler (Vitrin)"])

# ================= TAB 1: AI & TARİF =================
with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        malzemeler = st.text_input("Dolabında neler var?", placeholder="Örn: Yumurta, mantar, krema...")
    with col2:
        st.write("")
        st.write("")
        butce_modu = st.checkbox("💸 Ucuz Olsun")

    if st.button("🔍 Bana 3 Fikir Ver", type="primary"):
        if not api_key:
            st.warning("⚠️ API Anahtarı eksik!")
        elif not malzemeler:
            st.warning("⚠️ Malzeme girmedin!")
        else:
            with st.spinner("Şef senin için menü oluşturuyor..."):
                ozellik = "çok ekonomik ve pratik" if butce_modu else "gurme lezzetinde"
                prompt = f"""
                Sen bir şefsin. Malzemeler: {malzemeler}.
                Bana {ozellik} 3 FARKLI yemek fikri ver.
                Sadece listele:
                1. Yemek Adı (Kısa Açıklama)
                2. Yemek Adı (Kısa Açıklama)
                3. Yemek Adı (Kısa Açıklama)
                """
                cevap = yapay_zekaya_sor(prompt, api_key)
                
                if "⚠️" in cevap:
                    st.error(cevap)
                else:
                    st.session_state.oneriler = cevap.split('\n')
                    st.session_state.tam_tarif = "" 
                    st.rerun()

    # SEÇİM VE TARİF
    if st.session_state.oneriler:
        st.divider()
        st.subheader("🤔 Hangisini yapalım?")
        temiz_oneriler = [x for x in st.session_state.oneriler if len(x) > 5]
        
        if temiz_oneriler:
            secim = st.radio("Bir menü seç:", temiz_oneriler)
            
            if st.button("🍳 Tarifini Getir"):
                with st.spinner("Tarif yazılıyor..."):
                    prompt_tarif = f"Seçilen yemek: {secim}. Malzemeler: {malzemeler}. Detaylı tarif yaz."
                    cevap_tarif = yapay_zekaya_sor(prompt_tarif, api_key)
                    
                    if "⚠️" in cevap_tarif:
                        st.error(cevap_tarif)
                    else:
                        st.session_state.tam_tarif = cevap_tarif
                        st.rerun()

    # SONUÇ EKRANI
    if st.session_state.tam_tarif:
        st.success("Afiyet olsun! İşte tarifin:")
        st.markdown(f"<div style='background:rgba(255,255,255,0.05); padding:20px; border-radius:10px;'>{st.session_state.tam_tarif}</div>", unsafe_allow_html=True)
        
        arama_terimi = malzemeler.split(',')[0]
        link = f"https://www.trendyol.com/sr?q={arama_terimi}"
        st.markdown(f"""<a href="{link}" target="_blank" class="buy-btn">🛒 Malzemeleri Trendyol'dan Söyle</a>""", unsafe_allow_html=True)

# ================= TAB 2: VİTRİN =================
with tab2:
    st.header("🌟 Haftanın Yıldız Şefleri")
        with st.container():
        st.markdown("""
        <div class="vitrin-card">
            <h3>🍝 Öğrenci Usulü Makarna</h3>
            <p><strong>Şef:</strong> Berkecan Yılmaz (@berkecan)</p>
            <p><i>"Gece acıkınca 5 dakikada yaptığım spesiyal soslu makarnam."</i></p>
            <p>⭐️⭐️⭐️⭐️⭐️ (124 Beğeni)</p>
        </div>
        """, unsafe_allow_html=True)
        # Demo Video
        st.video("https://www.w3schools.com/html/mov_bbb.mp4") 

    # Örnek 2
       with st.container():
        st.markdown("""
        <div class="vitrin-card">
            <h3>🥞 Pazar Kahvaltısı Krepi</h3>
            <p><strong>Şef:</strong> Ayşe Teyze (@ayseninmutfagi)</p>
            <p><i>"Torunlarım bayılıyor, içine sırrımı da kattım."</i></p>
            <p>⭐️⭐️⭐️⭐️ (89 Beğeni)</p>
        </div>
        """, unsafe_allow_html=True)
        st.video("https://www.w3schools.com/html/mov_bbb.mp4") 

    st.markdown("---")
    st.subheader("📹 Sen de Yükle!")
    with st.form("upload_vitrin"):
        st.text_input("Kullanıcı Adın")
        st.file_uploader("Video Seç")
        if st.form_submit_button("🚀 Vitrine Gönder"):
            st.success("Gönderildi! Onay bekleniyor.")
            time.sleep(2)
            st.rerun()

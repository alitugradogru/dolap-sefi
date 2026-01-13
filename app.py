import streamlit as st
import requests
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Dolap Şefi", page_icon="👨‍🍳", layout="centered")

# --- HAFIZA ---
if 'oneriler' not in st.session_state:
    st.session_state.oneriler = []
if 'tam_tarif' not in st.session_state:
    st.session_state.tam_tarif = ""

# --- TASARIM ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #0f2027, #203a43, #2c5364); color: white; }
    h1 { text-align: center; color: #f27a1a; font-family: 'Arial Black', sans-serif; }
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 15px; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(255,255,255,0.1); border-radius: 8px; color: white; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #f27a1a; color: white; }
    .vitrin-card { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; margin-bottom: 20px; border-left: 5px solid #f27a1a; }
    .buy-btn { display: block; width: 100%; background-color: #28a745; color: white; text-align: center; padding: 15px; border-radius: 10px; font-weight: bold; text-decoration: none; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- API ANAHTARI ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Google API Key", type="password")

# --- AKILLI FONKSİYON (DÜZELTİLMİŞ) ---
def yapay_zekaya_sor(prompt, key):
    model = "gemini-1.5-flash"  # SADECE ÇALIŞAN MODEL
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"⚠️ Google API Hatası: {response.text}"

    except Exception as e:
        return f"⚠️ Bağlantı Hatası: {str(e)}"

# --- ARAYÜZ ---
st.title("👨‍🍳 Dolap Şefi")
st.caption("Yapay Zeka Destekli Sosyal Mutfak Platformu")

tab1, tab2 = st.tabs(["🔥 Şef'e Sor (AI)", "🌟 Sizden Gelenler (Vitrin)"])

# ================= TAB 1 =================
with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        malzemeler = st.text_input("Dolabında neler var?", placeholder="Örn: Yumurta, mantar...")
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
                Sen bir şefsin.
                Malzemeler: {malzemeler}.
                Bana {ozellik} 3 yemek fikri ver.
                Sadece isim ve kısa açıklama listele.
                """
                cevap = yapay_zekaya_sor(prompt, api_key)

                if "⚠️" in cevap:
                    st.error(cevap)
                else:
                    st.session_state.oneriler = cevap.split("\n")
                    st.session_state.tam_tarif = ""
                    st.rerun()

    if st.session_state.oneriler:
        st.divider()
        st.subheader("🤔 Hangisini yapalım?")
        temiz_oneriler = [x for x in st.session_state.oneriler if len(x) > 5]

        if temiz_oneriler:
            secim = st.radio("Bir menü seç:", temiz_oneriler)

            if st.button("🍳 Tarifini Getir"):
                with st.spinner("Tarif yazılıyor..."):
                    prompt_tarif = f"Seçilen yemek: {secim}. Malzemeler: {malzemeler}. Detaylı tarif yaz."
                    st.session_state.tam_tarif = yapay_zekaya_sor(prompt_tarif, api_key)
                    st.rerun()

    if st.session_state.tam_tarif:
        st.success("Afiyet olsun!")
        st.markdown(
            f"<div style='background:rgba(255,255,255,0.05); padding:20px; border-radius:10px;'>{st.session_state.tam_tarif}</div>",
            unsafe_allow_html=True
        )
        link = f"https://www.trendyol.com/sr?q={malzemeler.split(',')[0]}"
        st.markdown(f"""<a href="{link}" target="_blank" class="buy-btn">🛒 Malzemeleri Trendyol'dan Söyle</a>""", unsafe_allow_html=True)

# ================= TAB 2 =================
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
        st.video("https://www.w3schools.com/html/mov_bbb.mp4")

    with st.container():
        st.markdown("""
        <div class="vitrin-card">
            <h3>🥞 Pazar Kahvaltısı Krepi</h3>
            <p><strong>Şef:</strong> Ayşe Teyze (@ayseninmutfagi)</p>
            <p><i>"Torunlarım bayılıyor, içine sırrımı da kattım."</i></p>
            <p>⭐️⭐️⭐️⭐️ (89 Beğeni)</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📹 Sen de Yükle!")

    with st.form("upload_vitrin"):
        st.text_input("Kullanıcı Adın")
        st.file_uploader("Video Seç")
        if st.form_submit_button("🚀 Vitrine Gönder"):
            st.success("Gönderildi! Onay bekleniyor.")
            time.sleep(2)
            st.rerun()

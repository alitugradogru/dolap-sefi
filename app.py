import streamlit as st
import google.generativeai as genai
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Dolap Şefi", page_icon="👨‍🍳", layout="centered")

# --- HAFIZA (SESSION STATE) ---
if 'oneriler' not in st.session_state: st.session_state.oneriler = []
if 'secilen_yemek' not in st.session_state: st.session_state.secilen_yemek = None
if 'tam_tarif' not in st.session_state: st.session_state.tam_tarif = ""

# --- TASARIM (CSS) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #0f2027, #203a43, #2c5364); color: white; }
    h1 { text-align: center; color: #f27a1a; font-family: 'Arial Black', sans-serif; }
    
    /* Sekmeler */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(255,255,255,0.1); border-radius: 8px; color: white; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #f27a1a; color: white; }
    
    /* Para Kazandıran Buton */
    .buy-btn {
        display: block;
        width: 100%;
        background-color: #28a745; /* Yeşil Satın Alma Rengi */
        color: white;
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        font-weight: bold;
        text-decoration: none;
        margin-top: 20px;
        font-size: 18px;
        transition: 0.3s;
    }
    .buy-btn:hover { background-color: #218838; transform: scale(1.02); }
    
    /* Vitrin Kartları */
    .vitrin-card {
        background: rgba(255,255,255,0.05);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 5px solid #f27a1a;
    }
    </style>
""", unsafe_allow_html=True)

# --- API ANAHTARI ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("API Key", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # Hata önleyici dedektif kodu
        model_name = 'gemini-1.5-flash'
        model = genai.GenerativeModel(model_name)
    except:
        st.error("Bağlantı hatası.")

# --- BAŞLIK ---
st.title("👨‍🍳 Dolap Şefi")
st.caption("Yapay Zeka Destekli Sosyal Mutfak Platformu")

# --- SEKMELER ---
tab1, tab2 = st.tabs(["🔥 Şef'e Sor (AI)", "🌟 Sizden Gelenler (Vitrin)"])

# ================= TAB 1: AI & PARA KAZANMA =================
with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        malzemeler = st.text_input("Dolapta ne var?", placeholder="Örn: Yumurta, patates...")
    with col2:
        st.write("")
        st.write("")
        butce_modu = st.checkbox("💸 Ucuz Olsun")

    if st.button("🔍 Bana 3 Fikir Ver", type="primary"):
        if not api_key or not malzemeler:
            st.warning("API Key veya malzeme eksik.")
        else:
            with st.spinner("Şef düşünüyor..."):
                ozellik = "çok ekonomik" if butce_modu else "gurme lezzetinde"
                prompt = f"Malzemeler: {malzemeler}. Bana {ozellik} 3 farklı yemek ismi ve kısa açıklama ver. Format: 1. İsim - Açıklama..."
                try:
                    res = model.generate_content(prompt)
                    st.session_state.oneriler = res.text.split('\n')
                    st.rerun()
                except: st.error("AI yanıt vermedi.")

    # Seçim Ekranı
    if st.session_state.oneriler:
        st.divider()
        st.subheader("Seçimini Yap:")
        temiz_liste = [x for x in st.session_state.oneriler if len(x) > 5]
        secim = st.radio("Menü:", temiz_liste)
        
        if st.button("🍳 Tarifini Getir"):
            with st.spinner("Tarif yazılıyor..."):
                prompt_tarif = f"Seçilen yemek: {secim}. Malzemeler: {malzemeler}. Detaylı tarif yaz."
                res_tarif = model.generate_content(prompt_tarif)
                st.session_state.tam_tarif = res_tarif.text
                st.session_state.secilen_yemek = secim # Seçilen yemeğin adını kaydet
                st.rerun()

    # Tarif ve SATIŞ LİNKİ
    if st.session_state.tam_tarif:
        st.info("İşte Tarifin! Afiyet olsun.")
        st.markdown(st.session_state.tam_tarif)
        
        # --- PARA KAZANMA BÖLÜMÜ (AFFILIATE) ---
        # Yemeğin ismini alıp Trendyol arama linkine çeviriyoruz
        arama_terimi = malzemeler.split(',')[0] # İlk malzemeyi baz alalım
        affiliate_link = f"https://www.trendyol.com/sr?q={arama_terimi}"
        
        st.markdown(f"""
            <a href="{affiliate_link}" target="_blank" class="buy-btn">
                🛒 Bu Tarifin Malzemelerini Trendyol'dan Söyle
            </a>
            <p style='text-align:center; font-size:12px; color:#aaa; margin-top:5px;'>
                *Bu link üzerinden yapacağınız alışverişler Dolap Şefi'ne katkı sağlar.
            </p>
        """, unsafe_allow_html=True)

# ================= TAB 2: VİTRİN (SİMÜLASYON) =================
with tab2:
    st.header("🌟 Haftanın Yıldız Şefleri")
    st.markdown("Topluluğumuzun en beğenilen tarifleri burada!")

    # BURASI ÖNEMLİ: Veritabanımız olmadığı için "Sabit Vitrin" yapıyoruz.
    # Sanki insanlar yüklemiş de burada çıkıyormuş gibi görünecek.
    
    # Örnek 1
    with st.container():
        st.markdown("""
        <div class="vitrin-card">
            <h3>🍝 Öğrenci Usulü Makarna</h3>
            <p><strong>Şef:</strong> Berkecan Yılmaz (@berkecan)</p>
            <p><i>"Gece acıkınca 5 dakikada yaptığım spesiyal soslu makarnam."</i></p>
            <p>⭐️⭐️⭐️⭐️⭐️ (124 Beğeni)</p>
        </div>
        """, unsafe_allow_html=True)
        # Video yerine örnek bir resim/video alanı (Streamlit demo video)
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
    
    st.markdown("---")
    st.subheader("📹 Sen de Yükle!")
    
    with st.form("upload_vitrin"):
        st.text_input("Kullanıcı Adın")
        st.text_input("Tarif Başlığı")
        st.file_uploader("Video Seç", type=["mp4"])
        if st.form_submit_button("🚀 Vitrine Gönder"):
            st.success("Harika! Videon editör onayına düştü. Onaylanınca burada yayınlanacak!")
            time.sleep(2)

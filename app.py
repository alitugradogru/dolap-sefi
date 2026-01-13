import streamlit as st
import google.generativeai as genai
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Dolap Şefi", page_icon="👨‍🍳", layout="centered")

# --- OTURUM DURUMU (HAFIZA) ---
# Sayfa yenilendiğinde seçenekler kaybolmasın diye hafıza tutuyoruz
if 'oneriler' not in st.session_state:
    st.session_state.oneriler = []
if 'secilen_yemek' not in st.session_state:
    st.session_state.secilen_yemek = None
if 'tam_tarif' not in st.session_state:
    st.session_state.tam_tarif = ""

# --- PREMIUM TASARIM (CSS) ---
st.markdown("""
    <style>
    /* Genel Arka Plan ve Yazı Tipi */
    .stApp {
        background: linear-gradient(to bottom, #141e30, #243b55);
        color: white;
    }
    
    /* Başlık Stili */
    h1 {
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #f27a1a;
        text-shadow: 2px 2px 4px #000000;
        font-size: 3rem !important;
    }
    
    /* Sekme (Tab) Tasarımı */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 10px 20px;
        color: white;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #f27a1a;
        color: white;
    }
    
    /* Kart Tasarımı */
    .tarif-card {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* Butonlar */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        font-weight: bold;
        transition: 0.3s;
    }
    </style>
""", unsafe_allow_html=True)

# --- API ANAHTARI KONTROLÜ ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    # Secrets yoksa yine de çalışsın diye manuel giriş (Geliştirici modu)
    api_key = st.sidebar.text_input("API Key Giriniz", type="password")

# --- MODEL SEÇİMİ (OTOMATİK) ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash') # Hızlı model
    except:
        st.error("Model bağlantısı kurulamadı.")

# --- BAŞLIK ---
st.title("👨‍🍳 Dolap Şefi")
st.markdown("<p style='text-align: center; opacity: 0.8;'>Mutfağın Patronu Sensin!</p>", unsafe_allow_html=True)

# --- SEKME SİSTEMİ ---
tab1, tab2 = st.tabs(["🤖 Şef'e Sor", "📹 Sizden Gelenler"])

# ================= TAB 1: YAPAY ZEKA ŞEF =================
with tab1:
    st.write("")
    col1, col2 = st.columns([3, 1])
    with col1:
        malzemeler = st.text_input("Dolabında neler var?", placeholder="Örn: Tavuk, krema, mantar...")
    with col2:
        st.write("")
        st.write("")
        butce_modu = st.checkbox("💸 Öğrenci İşi")

    # ADIM 1: SEÇENEKLERİ GETİR
    if st.button("🔍 Bana Fikir Ver", type="primary"):
        if not api_key:
            st.error("Lütfen API Anahtarını girin.")
        elif not malzemeler:
            st.warning("Malzeme girmeden yemek yapamayız şefim!")
        else:
            try:
                with st.spinner("Şef senin için menü oluşturuyor..."):
                    ozellik = "çok ucuz, pratik ve öğrenci dostu" if butce_modu else "lezzetli ve gurme"
                    
                    prompt_secenek = f"""
                    Sen profesyonel bir şefsin. Elimdeki malzemeler: {malzemeler}.
                    Bana bu malzemelerle yapabileceğim {ozellik} 3 FARKLI yemek fikri ver.
                    
                    Sadece yemek isimlerini ve yanına 3-4 kelimelik kısa açıklama yaz.
                    Format şöyle olsun:
                    1. Yemek Adı - Kısa Açıklama
                    2. Yemek Adı - Kısa Açıklama
                    3. Yemek Adı - Kısa Açıklama
                    """
                    
                    response = model.generate_content(prompt_secenek)
                    # Seçenekleri listeye at
                    st.session_state.oneriler = response.text.split('\n')
                    st.session_state.tam_tarif = "" # Eski tarifi temizle
                    st.rerun() # Sayfayı yenile ki seçenekler görünsün
            except Exception as e:
                st.error(f"Hata: {e}")

    # ADIM 2: KULLANICI SEÇİMİ VE TARİF
    if st.session_state.oneriler:
        st.markdown("---")
        st.subheader("🤔 Hangisini yapalım?")
        
        # Seçenekleri temizle (Boş satırları at)
        temiz_oneriler = [x for x in st.session_state.oneriler if len(x) > 5]
        
        secim = st.radio("Bir menü seç:", temiz_oneriler)
        
        if st.button("🍳 Tarifini Getir"):
            try:
                with st.spinner(f"{secim} için tarif yazılıyor..."):
                    prompt_tarif = f"""
                    Kullanıcı şu yemeği seçti: {secim}.
                    Malzemeler: {malzemeler}.
                    
                    Lütfen bu yemek için detaylı, adım adım, samimi bir dille tarif yaz.
                    Malzeme listesini net ver.
                    Püf noktası eklemeyi unutma.
                    """
                    response_tarif = model.generate_content(prompt_tarif)
                    st.session_state.tam_tarif = response_tarif.text
                    st.rerun()
            except Exception as e:
                st.error("Tarif getirilemedi.")

    # ADIM 3: SONUÇ EKRANI
    if st.session_state.tam_tarif:
        st.markdown(f"<div class='tarif-card'>", unsafe_allow_html=True)
        st.markdown(st.session_state.tam_tarif)
        st.markdown("</div>", unsafe_allow_html=True)

# ================= TAB 2: SİZDEN GELENLER (UPLOAD) =================
with tab2:
    st.header("📹 Kendi Tarifini Paylaş")
    st.markdown("Yaptığın yemeğin videosunu veya tarifini yükle, Dolap Şefi topluluğunda yayınlansın!")
    
    with st.form("upload_form"):
        kullanici_adi = st.text_input("Adın Soyadın / Takma Adın")
        yemek_basligi = st.text_input("Yemeğin Adı")
        video_dosyasi = st.file_uploader("Video Yükle (MP4)", type=['mp4', 'mov'])
        kendi_tarifin = st.text_area("Tarifini Buraya Yaz")
        
        gonder = st.form_submit_button("🚀 Gönder")
        
        if gonder:
            if not video_dosyasi and not kendi_tarifin:
                st.warning("Lütfen en azından bir video veya yazı ekle.")
            else:
                # Simülasyon: Gerçek sunucuya kaydetmek veritabanı gerektirir.
                # Şimdilik kullanıcıya gitmiş gibi gösteriyoruz.
                st.balloons()
                st.success(f"Teşekkürler {kullanici_adi}! '{yemek_basligi}' tarifin editörlerimize iletildi. Onaylandıktan sonra yayınlanacak!")
                time.sleep(2)

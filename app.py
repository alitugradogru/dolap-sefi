import streamlit as st
import google.generativeai as genai
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Dolap Şefi", page_icon="👨‍🍳", layout="centered")

# --- HAFIZA (Sayfa yenilenince gitmesin) ---
if 'oneriler' not in st.session_state: st.session_state.oneriler = []
if 'secilen_yemek' not in st.session_state: st.session_state.secilen_yemek = None
if 'tam_tarif' not in st.session_state: st.session_state.tam_tarif = ""

# --- TASARIM (Senin Sevdiğin Stil) ---
st.markdown("""
    <style>
    /* Arka Plan */
    .stApp {
        background: linear-gradient(to bottom, #0f2027, #203a43, #2c5364);
        color: white;
    }
    
    /* Başlık */
    h1 {
        text-align: center;
        font-family: 'Arial Black', sans-serif;
        color: #f27a1a;
        text-shadow: 2px 2px 4px #000000;
    }
    
    /* Sekmeler */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 15px; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(255,255,255,0.1); border-radius: 8px; color: white; padding: 10px 20px; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #f27a1a; color: white; }
    
    /* Satın Alma Butonu */
    .buy-btn {
        display: block; width: 100%; background-color: #28a745; color: white;
        text-align: center; padding: 15px; border-radius: 10px; font-weight: bold;
        text-decoration: none; margin-top: 20px; font-size: 18px; transition: 0.3s;
    }
    .buy-btn:hover { background-color: #218838; transform: scale(1.02); }
    
    /* Vitrin Kartları */
    .vitrin-card {
        background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px;
        margin-bottom: 20px; border-left: 5px solid #f27a1a; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    /* Normal Butonlar */
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 50px; }
    </style>
""", unsafe_allow_html=True)

# --- API ANAHTARI ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Google API Key", type="password")

# --- MODEL BAĞLANTISI (DÜZELTİLDİ ✅) ---
model = None
if api_key:
    try:
        genai.configure(api_key=api_key)
        # İŞTE ÇÖZÜM: 'gemini-1.5-flash' yerine 'gemini-pro' kullanıyoruz.
        # Bu model daha eski ama her yerde çalışır, hata vermez.
        model = genai.GenerativeModel('gemini-pro')
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")

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

    # ADIM 1: SEÇENEKLERİ GETİR
    if st.button("🔍 Bana 3 Fikir Ver", type="primary"):
        if not api_key:
            st.warning("⚠️ Önce API Anahtarı lazım şefim.")
        elif not malzemeler:
            st.warning("⚠️ Malzeme girmeden yemek yapamayız!")
        else:
            with st.spinner("Şef senin için menü oluşturuyor..."):
                ozellik = "çok ekonomik ve pratik" if butce_modu else "gurme lezzetinde"
                
                # Prompt (Emir)
                prompt_secenek = f"""
                Sen profesyonel bir şefsin. Elimdeki malzemeler: {malzemeler}.
                Bana bu malzemelerle yapabileceğim {ozellik} 3 FARKLI yemek fikri ver.
                
                Sadece yemek isimlerini ve yanına parantez içinde 3-4 kelimelik açıklama yaz.
                Format:
                1. Yemek Adı (Açıklama)
                2. Yemek Adı (Açıklama)
                3. Yemek Adı (Açıklama)
                """
                
                try:
                    response = model.generate_content(prompt_secenek)
                    st.session_state.oneriler = response.text.split('\n')
                    st.session_state.tam_tarif = "" # Eski tarifi temizle
                    st.rerun()
                except Exception as e:
                    st.error(f"Hata oluştu: {e}")
                    st.info("API Anahtarını veya kotanı kontrol et.")

    # ADIM 2: SEÇİM VE TARİF
    if st.session_state.oneriler:
        st.divider()
        st.subheader("🤔 Hangisini yapalım?")
        
        # Boş satırları temizle
        temiz_oneriler = [x for x in st.session_state.oneriler if len(x) > 5]
        
        if temiz_oneriler:
            secim = st.radio("Bir menü seç:", temiz_oneriler)
            
            if st.button("🍳 Tarifini Getir"):
                with st.spinner(f"Tarif hazırlanıyor..."):
                    try:
                        prompt_tarif = f"""
                        Kullanıcı şu yemeği seçti: {secim}.
                        Malzemeler: {malzemeler}.
                        
                        Lütfen bu yemek için:
                        1. Gerekli malzemeleri listele.
                        2. Adım adım, samimi bir dille yapılışını anlat.
                        3. Püf noktası ver.
                        """
                        response_tarif = model.generate_content(prompt_tarif)
                        st.session_state.tam_tarif = response_tarif.text
                        st.rerun()
                    except Exception as e:
                        st.error("Tarif getirilemedi. Lütfen tekrar dene.")
        else:
            st.warning("AI anlamlı bir cevap veremedi, lütfen tekrar 'Fikir Ver' butonuna bas.")

    # ADIM 3: SONUÇ VE PARA KAZANMA
    if st.session_state.tam_tarif:
        st.success("Afiyet olsun! İşte tarifin:")
        
        with st.container():
            st.markdown(f"<div style='background:rgba(255,255,255,0.05); padding:20px; border-radius:10px;'>{st.session_state.tam_tarif}</div>", unsafe_allow_html=True)
            
            # Affiliate Link (Trendyol)
            arama_terimi = malzemeler.split(',')[0]
            link = f"https://www.trendyol.com/sr?q={arama_terimi}"
            
            st.markdown(f"""
                <a href="{link}" target="_blank" class="buy-btn">
                    🛒 Malzemeleri Trendyol'dan Söyle
                </a>
                <p style='text-align:center; font-size:12px; color:#aaa; margin-top:5px;'>
                    *Bu link üzerinden yapacağınız alışverişler Dolap Şefi'ne katkı sağlar.
                </p>
            """, unsafe_allow_html=True)

# ================= TAB 2: VİTRİN (SİMÜLASYON) =================
with tab2:
    st.header("🌟 Haftanın Yıldız Şefleri")
    st.markdown("Topluluğumuzun en beğenilen tarifleri burada!")
    
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
    
    st.markdown("---")
    st.subheader("📹 Sen de Yükle!")
    
    with st.form("upload_vitrin"):
        st.text_input("Kullanıcı Adın")
        st.text_input("Tarif Başlığı")
        st.file_uploader("Video Seç", type=["mp4"])
        if st.form_submit_button("🚀 Vitrine Gönder"):
            st.success("Harika! Videon editör onayına düştü. Onaylanınca burada yayınlanacak!")
            time.sleep(2)
            st.rerun()

import streamlit as st
import google.generativeai as genai

# Sayfa Ayarları
st.set_page_config(page_title="Dolap Şefi AI", page_icon="👨‍🍳", layout="centered")

# --- CSS TASARIM ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #f27a1a;
        color: white;
        font-weight: bold;
        border-radius: 12px;
        padding: 15px;
        font-size: 20px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #d66912;
        transform: scale(1.02);
    }
    .card {
        background-color: #262730;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #444;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
st.title("🤖 Dolap Şefi: AI Modu")
st.markdown("Malzemeni yaz, Yapay Zeka sana özel şef tarifi üretsin!")

# --- GİZLİ ANAHTAR KONTROLÜ ---
# Secrets içinde anahtar var mı diye bakıyoruz
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
else:
    # Secrets yoksa manuel giriş kutusu göster (Test için)
    with st.sidebar:
        api_key = st.text_input("Google API Key", type="password", placeholder="AIzaSy... kodunu buraya gir")
        if api_key:
            genai.configure(api_key=api_key)

# --- ANA EKRAN ---
malzemeler = st.text_input("Dolabında neler var?", placeholder="Örn: Yumurta, bayat ekmek, biraz peynir...")
butce_modu = st.checkbox("💸 Öğrenci İşi (Ekonomik Olsun)")

generate_btn = st.button("✨ Yapay Zekaya Tarif Yazdır")

# --- RESİM SEÇİCİ FONKSİYON ---
def get_category_image(kategori):
    kategori = kategori.lower()
    if "tavuk" in kategori: return "https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?w=800&q=80"
    if "et" in kategori or "kıyma" in kategori: return "https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=800&q=80"
    if "sebze" in kategori or "salata" in kategori: return "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&q=80"
    if "tatlı" in kategori or "kahvaltı" in kategori: return "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=800&q=80"
    if "makarna" in kategori or "hamur" in kategori: return "https://images.unsplash.com/photo-1551183053-bf91b1dca038?w=800&q=80"
    return "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&q=80"

# --- YAPAY ZEKA MANTIĞI ---
if generate_btn:
    if not malzemeler:
        st.warning("⚠️ Malzeme yazmadın şefim!")
    elif not api_key:
        st.error("⚠️ API Anahtarı eksik! Lütfen Secrets ayarını yap veya soldan anahtarı gir.")
    else:
        try:
            with st.spinner("👨‍🍳 Şef düşünüyor... Yeni tarif icat ediliyor..."):
                # GÜNCELLEME BURADA: Modeli 'gemini-1.5-flash' yaptık
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                ozellik = "öğrenci dostu, çok ucuz ve pratik" if butce_modu else "lezzetli ve doyurucu"
                
                prompt = f"""
                Sen dünyaca ünlü bir şefsin. Elimdeki malzemeler şunlar: {malzemeler}.
                Bana bu malzemelerle yapabileceğim {ozellik} TEK BİR yaratıcı yemek tarifi ver.
                
                Cevabını tam olarak şu formatta ver (aralara yıldız koyma):
                YEMEK ADI: (Buraya yemek adını yaz)
                KATEGORİ: (Sadece şunlardan birini seç: Tavuk, Et, Sebze, Tatlı, Makarna, Genel)
                MALİYET: (Tahmini fiyat TL)
                KALORİ: (Tahmini kalori)
                ZORLUK: (Kolay/Orta/Zor)
                MALZEMELER: (Listele)
                TARİF: (Adım adım anlat)
                
                Lütfen samimi ve iştah açıcı bir dil kullan.
                """
                
                response = model.generate_content(prompt)
                text = response.text
                
                # Cevabı Parçala
                lines = text.split('\n')
                yemek_adi = "Sürpriz Yemek"
                kategori = "Genel"
                icerik = ""
                
                for line in lines:
                    if "YEMEK ADI:" in line: yemek_adi = line.replace("YEMEK ADI:", "").strip()
                    elif "KATEGORİ:" in line: kategori = line.replace("KATEGORİ:", "").strip()
                    else: icerik += line + "\n"

                # --- SONUÇ EKRANI ---
                st.balloons()
                img_url = get_category_image(kategori)
                
                with st.container():
                    st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                    st.image(img_url, use_container_width=True)
                    st.header(f"🍽 {yemek_adi}")
                    st.markdown(icerik)
                    
                    # Satış Linki
                    st.markdown(f"""
                        <a href="https://www.trendyol.com/sr?q={malzemeler.split(',')[0]}" target="_blank">
                            <button>🛒 Eksik Malzemeleri Sipariş Et</button>
                        </a>
                    """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
            st.info("API Anahtarın doğru, sorun model ismindeydi. Şimdi çözülmüş olmalı!")

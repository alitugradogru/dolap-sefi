import streamlit as st
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Dolap Şefi", page_icon="👨‍🍳", layout="centered")

# --- HAFIZA ---
if "sonuclar" not in st.session_state:
    st.session_state.sonuclar = [] 
if "secilen_tarif" not in st.session_state:
    st.session_state.secilen_tarif = None 

# --- TASARIM (YENİ KIRMIZI TEMA & ÖZELLİKLER) ---
st.markdown("""
<style>
/* 1. İŞTAH AÇICI KIRMIZI ARKA PLAN */
.stApp { 
    background: linear-gradient(to bottom, #8E0E00, #1F1C18); 
    color: white; 
}

h1 { text-align: center; color: #ffcc00; font-family: 'Arial Black', sans-serif; text-shadow: 2px 2px 4px #000000; }

/* Haber Kartı Tasarımı */
.haber-kart { 
    background: rgba(255,255,255,0.1); 
    padding: 15px; 
    border-radius: 12px; 
    border-left: 6px solid #ffcc00;
    margin-bottom: 15px;
    transition: 0.3s;
}
.haber-kart:hover { background: rgba(255,255,255,0.2); transform: scale(1.01); }

/* Alt Özellik Kutuları (Resimdeki Gibi) */
.feature-box {
    text-align: center;
    padding: 10px;
    color: #ddd;
}
.feature-icon {
    font-size: 30px;
    margin-bottom: 5px;
    display: block;
}
.feature-text {
    font-weight: bold;
    font-size: 14px;
}

.btn-trendyol { display: block; width: 100%; background-color: #28a745; color: white; text-align: center; padding: 15px; border-radius: 10px; font-weight: bold; text-decoration: none; margin-top: 20px; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

# --- DEV TARİF HAVUZU ---
# ŞEFİM, YENİ LİSTENİ ATINCA BURAYI GÜNCELLEYECEĞİZ
TUM_TARIFLER = [
    {
        "ad": "Efsane Menemen",
        "malzemeler": "Yumurta, Domates, Biber, Sıvı Yağ, Tuz",
        "desc": "Kahvaltıların vazgeçilmezi.",
        "tar": "1. Biberleri doğrayıp yağda kavur.\n2. Domatesleri ekle suyunu çeksin.\n3. Yumurtaları kır, çok karıştırma."
    },
    {
        "ad": "Peynirli Omlet",
        "malzemeler": "Yumurta, Kaşar Peyniri, Tereyağı",
        "desc": "5 dakikada protein deposu.",
        "tar": "1. Yumurtaları çırp.\n2. Tavaya dök, altı pişince kaşarı ekle.\n3. İkiye katla servis et."
    },
    {
        "ad": "Fırın Patates",
        "malzemeler": "Patates, Zeytinyağı, Kekik, Pul Biber",
        "desc": "Kızartma tadında ama çok hafif.",
        "tar": "1. Patatesleri elma dilim doğra.\n2. Baharatlarla harmanla.\n3. 200 derecede 30 dk pişir."
    },
    {
        "ad": "Patates Salatası",
        "malzemeler": "Patates, Taze Soğan, Maydanoz, Limon, Zeytinyağı",
        "desc": "Çay saatlerinin yıldızı.",
        "tar": "1. Patatesleri haşla küp doğra.\n2. Yeşillikleri ince kıy ekle.\n3. Sosunu dök karıştır."
    },
    {
        "ad": "Kıymalı Patates Oturtma",
        "malzemeler": "Patates, Kıyma, Soğan, Salça",
        "desc": "Akşama doyurucu ana yemek.",
        "tar": "1. Patatesleri halka doğra hafif kızart.\n2. Kıymalı harç hazırla.\n3. Tepsiye diz fırına ver."
    },
    {
        "ad": "Köri Soslu Tavuk",
        "malzemeler": "Tavuk Göğsü, Krema, Köri, Karabiber",
        "desc": "Dünya mutfağından lezzet.",
        "tar": "1. Tavukları sotele.\n2. Kremayı ve köriyi ekle.\n3. Sos kıvam alana kadar pişir."
    },
    {
        "ad": "Tavuk Sote",
        "malzemeler": "Tavuk Göğsü, Domates, Biber, Soğan",
        "desc": "Klasik ve garantili lezzet.",
        "tar": "1. Tavukları suyunu çekene kadar pişir.\n2. Sebzeleri ekle kavur.\n3. Baharatları at, servise hazır."
    },
    {
        "ad": "Salçalı Makarna",
        "malzemeler": "Makarna, Salça, Nane, Sıvı Yağ",
        "desc": "Öğrenci evinin kralı.",
        "tar": "1. Makarnayı haşla.\n2. Yağda salça ve naneyi yak.\n3. Karıştır."
    },
    {
        "ad": "Krep (Akıtma)",
        "malzemeler": "Un, Süt, Yumurta, Tuz",
        "desc": "İster tatlı ister tuzlu ye.",
        "tar": "1. Tüm malzemeleri çırp.\n2. Tavaya kepçeyle dök.\n3. Arkalı önlü pişir."
    },
    {
        "ad": "Mücver",
        "malzemeler": "Kabak, Yumurta, Un, Dereotu, Peynir",
        "desc": "Kabağın en güzel hali.",
        "tar": "1. Kabağı rendele suyunu sık.\n2. Malzemeleri karıştır.\n3. Kaşık kaşık kızgın yağa dök."
    }
]

# --- ARAMA MOTORU ---
def tarifleri_bul(girdi):
    girdi = girdi.lower()
    bulunanlar = []
    
    for tarif in TUM_TARIFLER:
        if girdi in tarif["malzemeler"].lower() or girdi in tarif["ad"].lower():
            bulunanlar.append(tarif)
            
    return bulunanlar

# --- ARAYÜZ ---

# 4. KOLAJ BÖLÜMÜ (Mevsimlik, iştah açıcı görseller)
c1, c2, c3, c4 = st.columns(4)
with c1: st.image("https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=300", use_container_width=True) # Salata
with c2: st.image("https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=300", use_container_width=True) # Pizza
with c3: st.image("https://images.unsplash.com/photo-1482049016688-2d3e1b311543?w=300", use_container_width=True) # Yumurta/Toast
with c4: st.image("https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=300", use_container_width=True) # Tatlı

st.title("👨‍🍳 Dolap Şefi")
st.caption("Dolabındakilerle Harikalar Yarat!")

tab1, tab2 = st.tabs(["🔥 Tarif Bulucu", "🌟 Vitrin"])

# ================= TAB 1: ANA EKRAN =================
with tab1:
    if st.session_state.secilen_tarif is None:
        malzemeler = st.text_input("Dolabında ne var?", placeholder="Örn: Yumurta, Patates, Tavuk...")
        
        if st.button("🔍 Tarifleri Listele", type="primary"):
            if not malzemeler:
                st.warning("Bir malzeme yazmalısın!")
            else:
                with st.spinner("Lezzetler taranıyor..."):
                    time.sleep(0.3)
                    sonuclar = tarifleri_bul(malzemeler)
                    st.session_state.sonuclar = sonuclar
                    
                    if not sonuclar:
                        st.error("Bu malzemeyle kayıtlı tarif bulamadım. Yeni malzemeler ekleyerek dene!")

        if st.session_state.sonuclar:
            sayi = len(st.session_state.sonuclar)
            st.markdown(f"### 😋 {sayi} Leziz Tarif Bulundu:")
            
            for i, tarif in enumerate(st.session_state.sonuclar):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <div class="haber-kart">
                        <h3 style="margin:0; color:#ffcc00;">{tarif['ad']}</h3>
                        <p style="margin:5px 0 10px 0; color:#ddd;"><i>{tarif['desc']}</i></p>
                        <p style="font-size:13px;"><b>Gerekli Malzemeler:</b><br>{tarif['malzemeler']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.write("") 
                    st.write("")
                    if st.button("Tarife Git 👉", key=f"btn_{i}"):
                        st.session_state.secilen_tarif = tarif
                        st.rerun()

    else:
        yemek = st.session_state.secilen_tarif
        if st.button("⬅️ Geri Dön"):
            st.session_state.secilen_tarif = None
            st.rerun()
            
        st.divider()
        st.header(f"🍽️ {yemek['ad']}")
        st.info(f"💡 {yemek['desc']}")
        st.warning(f"🛒 **İhtiyaç Listesi:** {yemek['malzemeler']}")
        
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.05); padding:25px; border-radius:15px; font-size:16px; line-height:1.8;'>
            {yemek['tar']}
        </div>
        """, unsafe_allow_html=True)
        
        link = f"https://www.trendyol.com/sr?q={malzemeler.split(',')[0]}"
        st.markdown(f"""<a href="{link}" target="_blank" class="btn-trendyol">🛒 Malzemeleri Hemen Al (Trendyol)</a>""", unsafe_allow_html=True)

# ================= TAB 2: VİTRİN =================
with tab2:
    st.header("🌟 Haftanın Yıldızları")
    
    with st.container():
        st.markdown("""
        <div class="haber-kart">
            <h3>🍝 Berkecan'ın Makarnası</h3>
            <p>⭐️⭐️⭐️⭐️⭐️ (124 Beğeni)</p>
        </div>""", unsafe_allow_html=True)
        st.video("https://www.w3schools.com/html/mov_bbb.mp4")
    
    # 1. AYŞE TEYZE GERİ DÖNDÜ!
    with st.container():
        st.markdown("""
        <div class="haber-kart">
            <h3>🥞 Ayşe Teyze'nin Krepi</h3>
            <p><i>"Torunlarım bayılıyor, içine sevgimi kattım."</i></p>
            <p>⭐️⭐️⭐️⭐️ (89 Beğeni)</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.write("Sen de tarifini yükle:")
    with st.form("upload"):
        st.text_input("Adın")
        st.file_uploader("Video")
        if st.form_submit_button("Gönder"):
            st.success("Gönderildi!")
            time.sleep(2)
            st.rerun()

# --- 3. ALT ÖZELLİK KUTULARI (FOTODAKİ GİBİ) ---
st.markdown("---")
col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    st.markdown("""<div class="feature-box"><span class="feature-icon">⚡</span><div class="feature-text">Hızlı Öneri</div></div>""", unsafe_allow_html=True)
with col_b:
    st.markdown("""<div class="feature-box"><span class="feature-icon">🍃</span><div class="feature-text">Taze Fikirler</div></div>""", unsafe_allow_html=True)
with col_c:
    st.markdown("""<div class="feature-box"><span class="feature-icon">👨‍🍳</span><div class="feature-text">Şef Dokunuşu</div></div>""", unsafe_allow_html=True)
with col_d:
    st.markdown("""<div class="feature-box"><span class="feature-icon">🔥</span><div class="feature-text">Sıcak Sunum</div></div>""", unsafe_allow_html=True)

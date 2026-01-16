import streamlit as st
import time
import json
import os

# --- 1. AYARLAR & KURULUM ---
st.set_page_config(
    page_title="Dolap Şefi",
    page_icon="👨‍🍳",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 2. VERİTABANI FONKSİYONLARI ---
DOSYA_ADI = "kullanici_tarifleri.json"

def tarifleri_yukle():
    if os.path.exists(DOSYA_ADI):
        with open(DOSYA_ADI, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def tarifi_kaydet(yeni_tarif):
    mevcut_tarifler = tarifleri_yukle()
    mevcut_tarifler.append(yeni_tarif)
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(mevcut_tarifler, f, ensure_ascii=False, indent=4)

# --- 3. HAFIZA ---
if "sonuclar" not in st.session_state:
    st.session_state.sonuclar = [] 
if "secilen_tarif" not in st.session_state:
    st.session_state.secilen_tarif = None 

# --- 4. PROFESYONEL "SENIOR DEV" TASARIMI (CSS) ---
st.markdown("""
<style>
/* Google Font Import (Modern Yazılımcı Fontu: Inter) */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

/* GENEL SAYFA YAPISI */
.stApp {
    background-color: #0e1117;
    background-image: radial-gradient(circle at 50% 0%, #3a0ca3 0%, #0e1117 50%);
    font-family: 'Inter', sans-serif;
    color: #ffffff;
}

/* BAŞLIKLAR */
h1 {
    font-weight: 800 !important;
    background: -webkit-linear-gradient(45deg, #FFCC00, #FF6B6B);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0px;
    letter-spacing: -1px;
}
h2, h3, h4 { font-weight: 600 !important; color: #f0f0f0 !important; }

/* INPUT ALANLARI (ARAMA ÇUBUĞU) */
.stTextInput > div > div > input {
    background-color: rgba(255, 255, 255, 0.05);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 10px;
    transition: all 0.3s ease;
}
.stTextInput > div > div > input:focus {
    border-color: #FFCC00;
    box-shadow: 0 0 15px rgba(255, 204, 0, 0.2);
}

/* GLASSMORPHISM KART TASARIMI (Buzlu Cam) */
.haber-kart { 
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    padding: 20px; 
    border-radius: 16px; 
    border: 1px solid rgba(255, 255, 255, 0.05);
    margin-bottom: 20px;
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* Yaylanma efekti */
    position: relative;
    overflow: hidden;
}

.haber-kart::before {
    content: "";
    position: absolute;
    top: 0; left: 0; width: 4px; height: 100%;
    background: linear-gradient(to bottom, #FFCC00, #FF6B6B);
}

.haber-kart:hover { 
    transform: translateY(-5px) scale(1.02);
    background: rgba(255, 255, 255, 0.07);
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    border-color: rgba(255, 204, 0, 0.3);
}

/* MALZEME LİSTESİ KUTUSU */
.malzeme-kutusu {
    background: rgba(255, 204, 0, 0.05);
    border: 1px dashed #FFCC00;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 25px;
}
.malzeme-kutusu ul { list-style-type: none; padding: 0; margin: 0; }
.malzeme-kutusu li { 
    padding: 8px 0; 
    border-bottom: 1px solid rgba(255,255,255,0.05); 
    display: flex; 
    align-items: center;
}
.malzeme-kutusu li::before {
    content: "🔸"; margin-right: 10px; font-size: 12px;
}

/* MODERN BUTONLAR (TRENDYOL & DİĞERLERİ) */
.stButton > button {
    width: 100%;
    border-radius: 10px;
    font-weight: 600;
    border: none;
    transition: 0.3s;
    background-color: rgba(255,255,255,0.1);
    color: white;
}
.stButton > button:hover {
    background-color: rgba(255,255,255,0.2);
    color: #FFCC00;
}

/* ÖZEL TRENDYOL BUTONU (HTML) */
.btn-trendyol { 
    display: block; width: 100%; 
    background: linear-gradient(135deg, #10b981, #059669);
    color: white !important; 
    text-align: center; 
    padding: 16px; 
    border-radius: 12px; 
    font-weight: 700; 
    text-decoration: none; 
    margin-top: 20px; 
    font-size: 16px; 
    letter-spacing: 0.5px;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
    transition: 0.3s;
}
.btn-trendyol:hover { 
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(16, 185, 129, 0.6);
}

/* LOGO ORTALAMA */
[data-testid="stImage"] { display: block; margin-left: auto; margin-right: auto; }

/* SCROLLBAR TASARIMI */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #0e1117; }
::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #555; }

/* FOOTER */
.footer { 
    position: fixed; bottom: 0; left: 0; width: 100%; 
    background: rgba(14, 17, 23, 0.9);
    backdrop-filter: blur(5px);
    border-top: 1px solid rgba(255,255,255,0.05);
    color: #666; text-align: center; padding: 8px; font-size: 11px; z-index: 999;
}
</style>
""", unsafe_allow_html=True)

# --- 5. TARİF VERİTABANI ---
TUM_TARIFLER = [
    {"ad": "Efsane Menemen", "kat": "Kahvaltı", "malz": ["3 Yumurta", "2 Domates", "3 Biber", "Yağ", "Tuz"], "desc": "Kahvaltının kralı.", "tar": "1. Biberleri kavur.\n2. Domatesi ekle pişir.\n3. Yumurtayı kır."},
    {"ad": "Sucuklu Yumurta", "kat": "Kahvaltı", "malz": ["Yarım Kangal Sucuk", "3 Yumurta", "Tereyağı"], "desc": "Pazar sabahı klasiği.", "tar": "1. Sucukları yağda çevir.\n2. Yumurtaları kır."},
    {"ad": "Süzme Mercimek", "kat": "Çorba", "malz": ["1 Bardak Mercimek", "1 Patates", "1 Havuç", "Soğan"], "desc": "Limon sık iç.", "tar": "1. Sebzeleri haşla, blenderdan geçir.\n2. Sos dök."},
    {"ad": "Domates Çorbası", "kat": "Çorba", "malz": ["4 Domates", "1 Kaşık Un", "1 Bardak Süt", "Kaşar"], "desc": "Kremalı lezzet.", "tar": "1. Unu kavur, domatesi ekle.\n2. Sütle aç."},
    {"ad": "Kuru Fasulye", "kat": "Ana Yemek", "malz": ["Fasulye", "Kuşbaşı Et", "Soğan", "Salça"], "desc": "Milli yemek.", "tar": "1. Soğan ve eti kavur.\n2. Fasulyeyi ekle pişir."},
    {"ad": "Karnıyarık", "kat": "Ana Yemek", "malz": ["6 Patlıcan", "Kıyma", "Biber", "Domates"], "desc": "Patlıcan efsanesi.", "tar": "1. Patlıcanı kızart.\n2. İçini doldur fırınla."},
    {"ad": "Tavuk Sote", "kat": "Tavuk", "malz": ["Tavuk Göğsü", "Biber", "Domates", "Soğan"], "desc": "Pratik akşam yemeği.", "tar": "1. Tavuğu sotele.\n2. Sebzeleri ekle pişir."},
    {"ad": "Köri Soslu Tavuk", "kat": "Tavuk", "malz": ["Tavuk", "Krema", "Köri", "Karabiber"], "desc": "Dünya mutfağı.", "tar": "1. Tavuğu pişir.\n2. Krema ve köriyi ekle."},
    {"ad": "Salçalı Makarna", "kat": "Makarna", "malz": ["Makarna", "Salça", "Nane", "Yağ"], "desc": "Öğrenci dostu.", "tar": "1. Makarnayı haşla.\n2. Salçalı sos yap karıştır."},
    {"ad": "Pirinç Pilavı", "kat": "Pilav", "malz": ["Pirinç", "Şehriye", "Tereyağı", "Su"], "desc": "Tane tane.", "tar": "1. Şehriyeyi ve pirinci kavur.\n2. Suyu ekle demle."},
    {"ad": "Sütlaç", "kat": "Tatlı", "malz": ["Süt", "Pirinç", "Şeker", "Nişasta"], "desc": "Hafif tatlı.", "tar": "1. Pirinci haşla sütü ekle.\n2. Şekeri kat pişir."},
    {"ad": "Magnolia", "kat": "Tatlı", "malz": ["Süt", "Bisküvi", "Muz/Çilek", "Puding"], "desc": "Kupta lezzet.", "tar": "1. Pudingi yap.\n2. Bisküvi ve meyveyle diz."},
]

def tarif_uret(malzeme):
    m = malzeme.title()
    return {
        "ad": f"Fırında Özel {m}",
        "kat": "Şefin Spesiyali",
        "malz": [m, "Zeytinyağı", "Kekik", "Tuz", "Karabiber"],
        "desc": "Bu malzeme ile garantili lezzet.",
        "tar": f"1. {m} yıkanır ve doğranır.\n2. Baharatlarla harmanlanır.\n3. 200 derece fırında pişirilir."
    }

def tarifleri_bul(girdi, kategori_filtresi):
    girdi = girdi.lower()
    bulunanlar = []
    tam_liste = TUM_TARIFLER + tarifleri_yukle()
    for tarif in tam_liste:
        if kategori_filtresi != "Tümü" and tarif.get("kat") != kategori_filtresi:
            continue
        malz_text = " ".join(tarif["malz"]).lower() if isinstance(tarif["malz"], list) else str(tarif["malz"]).lower()
        if not girdi or (girdi in malz_text or girdi in tarif["ad"].lower()):
            bulunanlar.append(tarif)
    if not bulunanlar and girdi and kategori_filtresi == "Tümü":
        bulunanlar.append(tarif_uret(girdi))
    return bulunanlar

# --- 6. ARAYÜZ ---

with st.sidebar:
    st.image("logo.png", use_container_width=True)
    st.markdown("### 🎛️ Filtreler")
    kategori = st.radio("Kategori Seç:", ["Tümü", "Kahvaltı", "Çorba", "Ana Yemek", "Tavuk", "Makarna", "Pilav", "Tatlı", "Kullanıcı"])
    st.markdown("---")
    st.info("💡 **Pro İpucu:** Dolap Şefi artık akıllı tarif üretebiliyor!")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        pass

st.title("Dolap Şefi")
st.markdown("<p style='text-align: center; color: #aaa; margin-top: -10px; font-weight: 300;'>Akıllı Mutfak Asistanın</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔥 Tarif Bulucu", "👨‍🍳 Mutfak Vitrini"])

# --- TAB 1: ARAMA ---
with tab1:
    if st.session_state.secilen_tarif is None:
        malzemeler = st.text_input("Dolabında ne var?", placeholder="Malzeme ara... (Örn: Yumurta, Patates)")
        
        sonuclar = tarifleri_bul(malzemeler, kategori)
        
        if malzemeler or kategori != "Tümü":
            st.markdown(f"##### 🎉 {len(sonuclar)} Sonuç Bulundu")
            
            for i, tarif in enumerate(sonuclar):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    malz_goster = ", ".join(tarif['malz'][:4]) + "..." if isinstance(tarif['malz'], list) else str(tarif['malz'])[:40]
                    st.markdown(f"""
                    <div class="haber-kart">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h3 style="margin:0; color:#FFCC00; font-size: 1.2rem;">{tarif['ad']}</h3>
                            <span style="font-size:10px; background:rgba(255,255,255,0.1); padding:4px 8px; border-radius:20px; border:1px solid rgba(255,255,255,0.2);">{tarif.get('kat','Genel')}</span>
                        </div>
                        <p style="color:#ccc; font-size: 0.9rem; margin-top: 5px;">{tarif['desc']}</p>
                        <span style="font-size:12px; color:#888;">🛒 {malz_goster}</span>
                    </div>""", unsafe_allow_html=True)
                with col_b:
                    st.write("")
                    st.write("")
                    if st.button("Tarifi Gör →", key=f"btn_{i}"):
                        st.session_state.secilen_tarif = tarif
                        st.rerun()
    else:
        # DETAY SAYFASI
        t = st.session_state.secilen_tarif
        if st.button("⬅️ Listeye Dön"):
            st.session_state.secilen_tarif = None
            st.rerun()
            
        st.divider()
        st.markdown(f"<h1 style='text-align:left; color:#FFCC00;'>{t['ad']}</h1>", unsafe_allow_html=True)
        st.caption(f"{t.get('kat', 'Genel')} • 15-30 Dk • Kolay")
        
        col_d1, col_d2 = st.columns([1, 2])
        
        with col_d1:
            st.markdown('<div class="malzeme-kutusu"><h4>🛒 Malzemeler</h4><ul>', unsafe_allow_html=True)
            malz_list = t['malz'] if isinstance(t['malz'], list) else t['malz'].split('\n')
            for m in malz_list:
                st.markdown(f"<li>{m}</li>", unsafe_allow_html=True)
            st.markdown('</ul></div>', unsafe_allow_html=True)
            
        with col_d2:
             st.markdown(f"""
            <div style='background:rgba(255,255,255,0.02); padding:25px; border-radius:15px; border:1px solid rgba(255,255,255,0.05);'>
                <h4 style="color:#FFCC00; margin-top:0;">👨‍🍳 Hazırlanışı</h4>
                <div style="line-height: 1.8; color: #ddd; white-space: pre-line;">{t['tar']}</div>
            </div>
            """, unsafe_allow_html=True)
             
             ana_malzeme = malz_list[0].split(" ")[-1] if malz_list else "Mutfak"
             link = f"https://www.trendyol.com/sr?q={ana_malzeme}"
             st.markdown(f'<a href="{link}" target="_blank" class="btn-trendyol">🛍️ Malzemeleri Sepete Ekle</a>', unsafe_allow_html=True)

# --- TAB 2: VİTRİN ---
with tab2:
    st.subheader("🌟 Topluluk Vitrini")
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.video("https://www.w3schools.com/html/mov_bbb.mp4")
        st.caption("🔥 Berkecan - 'Öğrenci Makarnası'")
    with col_v2:
        st.image("https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400")
        st.caption("🍕 Melis - 'Gece Pizzası'")

    st.markdown("---")
    st.markdown("### 📤 Kendi Tarifini Ekle")
    with st.form("ekle_form"):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            k_ad = st.text_input("Şef Adı")
            t_ad = st.text_input("Yemek Adı")
        with col_f2:
            t_desc = st.text_input("Slogan (Örn: Efsane Lezzet)")
            
        t_malz = st.text_area("Malzemeler (Her satıra bir tane yaz)")
        t_tar = st.text_area("Tarif Adımları")
        
        if st.form_submit_button("Tarifi Yayınla 🚀"):
            if k_ad and t_ad and t_malz:
                yeni = {
                    "ad": t_ad, "kat": "Kullanıcı", "sef": k_ad,
                    "desc": t_desc, "tar": t_tar,
                    "malz": [m.strip() for m in t_malz.split('\n') if m.strip()]
                }
                tarifi_kaydet(yeni)
                st.balloons()
                st.success("Tarifin Yayında!")

# --- FOOTER ---
st.markdown("""
<div class="footer">
    <p>Designed by Dolap Şefi Team | © 2026</p>
</div>
""", unsafe_allow_html=True)

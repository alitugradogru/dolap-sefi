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
# --- 5. GENİŞLETİLMİŞ TARİF VERİTABANI ---
TUM_TARIFLER = [
    # --- KAHVALTILIKLAR ---
    {"ad": "Efsane Menemen", "kat": "Kahvaltı", "malz": ["3 Yumurta", "2 Domates", "3 Biber", "Sıvı Yağ", "Tuz"], "desc": "Soğanlı mı soğansız mı? Karar senin.", "tar": "1. Biberleri doğrayıp yağda kavur.\n2. Kabuğu soyulmuş domatesleri ekle suyunu çeksin.\n3. Yumurtaları kır, ister karıştır ister bırak."},
    {"ad": "Kuymak (Mıhlama)", "kat": "Kahvaltı", "malz": ["2 Kaşık Mısır Unu", "2 Kaşık Tereyağı", "Trabzon Peyniri", "Su"], "desc": "Karadeniz fırtınası.", "tar": "1. Tereyağında mısır ununu kavur.\n2. Suyu ekle kıvam alana kadar karıştır.\n3. Peyniri ekle, uzayana kadar pişir."},
    {"ad": "Sucuklu Yumurta", "kat": "Kahvaltı", "malz": ["Yarım Kangal Sucuk", "3 Yumurta", "Tereyağı"], "desc": "Pazar sabahı klasiği.", "tar": "1. Sucukları dilimleyip yağda çevir (kurutma).\n2. Yumurtaları göz göz kır."},
    {"ad": "Pankek", "kat": "Kahvaltı", "malz": ["Un", "Süt", "Yumurta", "Kabartma Tozu", "Şeker"], "desc": "Puf puf kabarır.", "tar": "1. Tüm malzemeleri boza kıvamına gelene kadar çırp.\n2. Tavaya kepçeyle dök.\n3. Göz göz olunca çevir."},
    {"ad": "Patatesli Omlet", "kat": "Kahvaltı", "malz": ["2 Patates", "3 Yumurta", "Kaşar Peyniri", "Tuz"], "desc": "Doyurucu ve pratik.", "tar": "1. Patatesleri minik küpler halinde kızart.\n2. Çırpılmış yumurtayı üzerine dök.\n3. Kaşarı ekleyip kapağını kapat."},
    {"ad": "Sigara Böreği", "kat": "Kahvaltı", "malz": ["Yufka", "Lor Peyniri", "Maydanoz", "Sıvı Yağ"], "desc": "Çıtır çıtır.", "tar": "1. Yufkaları üçgen kes.\n2. Harcı koyup sar, ucunu suyla yapıştır.\n3. Kızgın yağda kızart."},

    # --- ÇORBALAR ---
    {"ad": "Süzme Mercimek", "kat": "Çorba", "malz": ["1 Bardak Kırmızı Mercimek", "1 Patates", "1 Havuç", "Soğan", "Yağ"], "desc": "Lokanta usulü.", "tar": "1. Sebzeleri ve mercimeği haşla.\n2. Blenderdan geçir.\n3. Üzerine yağda nane yak."},
    {"ad": "Ezogelin Çorbası", "kat": "Çorba", "malz": ["Mercimek", "Pirinç", "Bulgur", "Salça", "Nane"], "desc": "Geleneksel lezzet.", "tar": "1. Bakliyatları yıkayıp haşla.\n2. Ayrı yerde soğan ve salçayı kavur.\n3. Hepsini birleştir kaynat."},
    {"ad": "Domates Çorbası", "kat": "Çorba", "malz": ["4 Domates", "1 Kaşık Un", "1 Bardak Süt", "Kaşar", "Salça"], "desc": "Kaşarlı efsane.", "tar": "1. Unu kokusu çıkana kadar kavur.\n2. Rende domates ve salçayı ekle.\n3. Suyu ver, pişince sütle bağla."},
    {"ad": "Yayla Çorbası", "kat": "Çorba", "malz": ["Yoğurt", "Pirinç", "Un", "Yumurta", "Nane"], "desc": "Naneli ferahlık.", "tar": "1. Pirinci haşla.\n2. Yoğurt, un ve yumurtayı çırpıp ılıştırarak ekle.\n3. Kaynayınca naneli yağ dök."},
    {"ad": "Tavuk Suyu Çorba", "kat": "Çorba", "malz": ["Tavuk But", "Tel Şehriye", "Limon", "Maydanoz"], "desc": "Şifa deposu.", "tar": "1. Tavuğu haşla ve didikle.\n2. Suyuna şehriyeleri at pişir.\n3. Tavukları ekle, limonla servis et."},

    # --- ANA YEMEKLER (ET & TAVUK) ---
    {"ad": "Kuru Fasulye", "kat": "Ana Yemek", "malz": ["Kuru Fasulye", "Kuşbaşı Et", "Soğan", "Salça", "Tereyağı"], "desc": "Pilavın en iyi arkadaşı.", "tar": "1. Fasulyeyi akşamdan ısla.\n2. Eti ve soğanı kavur, salça ekle.\n3. Fasulyeyi ekle düdüklüde pişir."},
    {"ad": "Karnıyarık", "kat": "Ana Yemek", "malz": ["6 Patlıcan", "Kıyma", "Biber", "Domates", "Soğan"], "desc": "Patlıcanın şahı.", "tar": "1. Patlıcanları alaca soyup kızart.\n2. Ortasını açıp kıymalı harcı doldur.\n3. Salçalı suyla fırınla."},
    {"ad": "İzmir Köfte", "kat": "Ana Yemek", "malz": ["Kıyma", "Patates", "Biber", "Domates Sos", "Ekmek İçi"], "desc": "Fırında soslu ziyafet.", "tar": "1. Köfteleri ve elma dilim patatesleri az kızart.\n2. Tepsiye diz.\n3. Üzerine domates sos döküp fırınla."},
    {"ad": "Tavuk Sote", "kat": "Tavuk", "malz": ["Tavuk Göğsü", "Yeşil Biber", "Kırmızı Biber", "Domates", "Soğan"], "desc": "20 dakikada hazır.", "tar": "1. Tavukları suyunu çekene kadar sotele.\n2. Soğan ve biberi ekle kavur.\n3. Domates ve baharatla bitir."},
    {"ad": "Köri Soslu Tavuk", "kat": "Tavuk", "malz": ["Tavuk Göğsü", "Sıvı Krema", "Köri", "Karabiber"], "desc": "Makarna yanına harika.", "tar": "1. Tavukları sotele.\n2. Kremayı ve 2 kaşık köriyi ekle.\n3. Sos koyulaşınca altını kapat."},
    {"ad": "Hünkar Beğendi", "kat": "Ana Yemek", "malz": ["Kuşbaşı Et", "Patlıcan", "Un", "Süt", "Kaşar"], "desc": "Saray mutfağından.", "tar": "1. Eti soğanla yahni gibi pişir.\n2. Patlıcanı közle, beşamel sos ve kaşarla karıştır (beğendi).\n3. Beğendinin üzerine eti koy."},
    {"ad": "Fırında Tavuk Patates", "kat": "Tavuk", "malz": ["Tavuk Baget", "Patates", "Salça", "Kekik", "Sarımsak"], "desc": "Kurtarıcı yemek.", "tar": "1. Salça, yağ ve baharatla sos yap.\n2. Tavuk ve patatesi sosla harmanla.\n3. Tepsiye diz fırınla."},

    # --- SEBZE YEMEKLERİ ---
    {"ad": "Mücver", "kat": "Ana Yemek", "malz": ["3 Kabak", "2 Yumurta", "Un", "Dereotu", "Peynir"], "desc": "Sebze sevmeyene bile yedirir.", "tar": "1. Kabağı rendele suyunu sık.\n2. Tüm malzemeleri karıştır.\n3. Kaşık kaşık kızgın yağa dök."},
    {"ad": "Zeytinyağlı Taze Fasulye", "kat": "Ana Yemek", "malz": ["Taze Fasulye", "Domates", "Soğan", "Şeker", "Zeytinyağı"], "desc": "Soğuk yenen lezzet.", "tar": "1. Soğanı kavur fasulyeyi ekle sarart.\n2. Domates rendesi ve şekeri at.\n3. Kısık ateşte kendi suyuyla pişir."},
    {"ad": "Ispanak Yemeği", "kat": "Ana Yemek", "malz": ["Ispanak", "Pirinç", "Soğan", "Salça", "Yoğurt"], "desc": "Temel Reis güç kaynağı.", "tar": "1. Soğanı salçayla kavur.\n2. Yıkanmış ıspanakları ekle söndür.\n3. Az pirinç ve sıcak su ekle pişir."},
    
    # --- MAKARNA & PİLAV ---
    {"ad": "Salçalı Makarna", "kat": "Makarna", "malz": ["Makarna", "Domates Salçası", "Kuru Nane", "Sıvı Yağ"], "desc": "Öğrenci efsanesi.", "tar": "1. Makarnayı haşla süz.\n2. Tencerede yağ, salça ve naneyi yak.\n3. Makarnayı ekle karıştır."},
    {"ad": "Kremalı Mantarlı Makarna", "kat": "Makarna", "malz": ["Makarna", "Mantar", "Krema", "Maydanoz"], "desc": "İtalyan restoranı gibi.", "tar": "1. Mantarları yüksek ateşte sotele.\n2. Kremayı ekle kaynat.\n3. Haşlanmış makarna ile buluştur."},
    {"ad": "Pirinç Pilavı", "kat": "Pilav", "malz": ["Baldo Pirinç", "Arpa Şehriye", "Tereyağı", "Tavuk Suyu"], "desc": "Tane tane dökülen.", "tar": "1. Pirinci sıcak suda beklet.\n2. Şehriyeyi tereyağında kavur.\n3. Pirinci ekle, sıcak suyu ver demle."},
    {"ad": "Meyhane Pilavı", "kat": "Pilav", "malz": ["Bulgur", "Domates", "Biber", "Soğan", "Salça"], "desc": "Yanına cacıkla gider.", "tar": "1. Soğan ve biberi kavur.\n2. Salça ve domatesi ekle.\n3. Bulguru ve suyu ekle pişir."},
    {"ad": "Kısır", "kat": "Ana Yemek", "malz": ["İnce Bulgur", "Salça", "Nar Ekşisi", "Yeşillik", "Limon"], "desc": "Altın günlerinin yıldızı.", "tar": "1. Bulguru sıcak suyla şişir.\n2. Salçalı sosu yedir.\n3. Yeşillik ve nar ekşisini ekle."},

    # --- TATLILAR ---
    {"ad": "Fırın Sütlaç", "kat": "Tatlı", "malz": ["1 Litre Süt", "Pirinç", "Şeker", "Nişasta", "Vanilya"], "desc": "Üzeri nar gibi kızarmış.", "tar": "1. Pirinci haşla, sütü ve şekeri ekle.\n2. Nişastayla bağla.\n3. Güveçlere koyup fırında üstünü yak."},
    {"ad": "İrmik Helvası", "kat": "Tatlı", "malz": ["İrmik", "Tereyağı", "Süt", "Şeker", "Fıstık"], "desc": "Sıcak sıcak dondurmayla.", "tar": "1. İrmiği ve fıstığı tereyağında rengi dönene kadar kavur.\n2. Sıcak sütlü şerbeti dök.\n3. Demlenmeye bırak."},
    {"ad": "Magnolia", "kat": "Tatlı", "malz": ["Süt", "Yumurta Sarısı", "Nişasta", "Krema", "Bisküvi", "Çilek"], "desc": "Hafif ve şık.", "tar": "1. Kremasız muhallebiyi pişir soğut.\n2. Kremayı ekle çırp.\n3. Bisküvi ve meyveyle kat kat diz."},
    {"ad": "Mozaik Pasta", "kat": "Tatlı", "malz": ["Petibör Bisküvi", "Kakao", "Tereyağı", "Süt", "Şeker"], "desc": "Pişmeyen pasta.", "tar": "1. Sos malzemelerini erit.\n2. Kırılmış bisküvilerle karıştır.\n3. Streçleyip buzluğa at."},
    {"ad": "Islak Kek (Brownie)", "kat": "Tatlı", "malz": ["Yumurta", "Şeker", "Süt", "Yağ", "Kakao", "Un"], "desc": "Bol soslu.", "tar": "1. Keki çırpıp pişir.\n2. Kalan malzemelerle sos yap kaynat.\n3. Fırından çıkan sıcak keke dök."},
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

import streamlit as st
import time
import json
import os
from datetime import datetime

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
                data = json.load(f)
                for d in data:
                    if 'likes' not in d: d['likes'] = 0
                return data
            except json.JSONDecodeError:
                return []
    return []

def tarifi_kaydet(yeni_tarif):
    mevcut_tarifler = tarifleri_yukle()
    mevcut_tarifler.append(yeni_tarif)
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(mevcut_tarifler, f, ensure_ascii=False, indent=4)

def begeni_arttir(index):
    tarifler = tarifleri_yukle()
    if 0 <= index < len(tarifler):
        tarifler[index]['likes'] = tarifler[index].get('likes', 0) + 1
        with open(DOSYA_ADI, "w", encoding="utf-8") as f:
            json.dump(tarifler, f, ensure_ascii=False, indent=4)

# --- 3. HAFIZA ---
if "sonuclar" not in st.session_state: st.session_state.sonuclar = [] 
if "secilen_tarif" not in st.session_state: st.session_state.secilen_tarif = None 

# --- 4. CSS (SENIOR DEV DESIGN + MİGROS TURUNCUSU) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
.stApp {
    background-color: #0e1117;
    background-image: radial-gradient(circle at 50% 0%, #4a0404 0%, #0e1117 60%);
    font-family: 'Inter', sans-serif;
    color: #fff;
}
h1 {
    font-weight: 800;
    background: -webkit-linear-gradient(45deg, #FFCC00, #FF6B6B);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center; margin-bottom: 0;
}
.haber-kart { 
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(10px);
    padding: 20px; border-radius: 16px; 
    border: 1px solid rgba(255, 255, 255, 0.05);
    margin-bottom: 20px; transition: all 0.3s;
}
.haber-kart:hover { 
    transform: translateY(-5px); 
    border-color: rgba(255, 204, 0, 0.3);
    box-shadow: 0 10px 30px -10px rgba(255, 107, 107, 0.2);
}
.malzeme-kutusu {
    background: rgba(255, 204, 0, 0.05);
    border: 1px dashed #FFCC00;
    padding: 20px; border-radius: 12px; margin-bottom: 25px;
}
/* MİGROS BUTONU */
.btn-migros { 
    display: block; width: 100%; 
    background: linear-gradient(135deg, #FF7900, #F7941D); /* Migros Turuncusu */
    color: white !important; text-align: center; padding: 16px; 
    border-radius: 12px; font-weight: 700; text-decoration: none; 
    box-shadow: 0 4px 15px rgba(255, 121, 0, 0.4); transition: 0.3s;
    font-size: 18px;
}
.btn-migros:hover { 
    transform: scale(1.02); 
    box-shadow: 0 8px 25px rgba(255, 121, 0, 0.6);
}
[data-testid="stImage"] { display: block; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

# --- 5. GENİŞ TARİF HAVUZU (v20 Veritabanı) ---
# --- 5. MEGA TARİF VERİTABANI (GÜNCELLENMİŞ) ---
TUM_TARIFLER = [
    # --- KAHVALTILIKLAR ---
    {"ad": "Efsane Menemen", "kat": "Kahvaltı", "malz": ["3 Yumurta", "2 Domates", "3 Biber", "Sıvı Yağ", "Tuz"], "desc": "Soğanlı mı soğansız mı? Karar senin.", "tar": "1. Biberleri doğrayıp yağda kavur.\n2. Kabuğu soyulmuş domatesleri ekle suyunu çeksin.\n3. Yumurtaları kır, ister karıştır ister bırak."},
    {"ad": "Kuymak (Mıhlama)", "kat": "Kahvaltı", "malz": ["2 Kaşık Mısır Unu", "2 Kaşık Tereyağı", "Trabzon Peyniri", "Su"], "desc": "Karadeniz fırtınası.", "tar": "1. Tereyağında mısır ununu kavur.\n2. Suyu ekle kıvam alana kadar karıştır.\n3. Peyniri ekle, uzayana kadar pişir."},
    {"ad": "Sucuklu Yumurta", "kat": "Kahvaltı", "malz": ["Yarım Kangal Sucuk", "3 Yumurta", "Tereyağı"], "desc": "Pazar sabahı klasiği.", "tar": "1. Sucukları dilimleyip yağda çevir (kurutma).\n2. Yumurtaları göz göz kır."},
    {"ad": "Pankek", "kat": "Kahvaltı", "malz": ["Un", "Süt", "Yumurta", "Kabartma Tozu", "Şeker"], "desc": "Puf puf kabarır.", "tar": "1. Tüm malzemeleri boza kıvamına gelene kadar çırp.\n2. Tavaya kepçeyle dök.\n3. Göz göz olunca çevir."},
    {"ad": "Patatesli Omlet", "kat": "Kahvaltı", "malz": ["2 Patates", "3 Yumurta", "Kaşar Peyniri", "Tuz"], "desc": "Doyurucu ve pratik.", "tar": "1. Patatesleri minik küpler halinde kızart.\n2. Çırpılmış yumurtayı üzerine dök.\n3. Kaşarı ekleyip kapağını kapat."},
    {"ad": "Sigara Böreği", "kat": "Kahvaltı", "malz": ["Yufka", "Lor Peyniri", "Maydanoz", "Sıvı Yağ"], "desc": "Çıtır çıtır.", "tar": "1. Yufkaları üçgen kes.\n2. Harcı koyup sar, ucunu suyla yapıştır.\n3. Kızgın yağda kızart."},
    {"ad": "Pişi", "kat": "Kahvaltı", "malz": ["Un", "Maya", "Su", "Tuz", "Kızartma Yağı"], "desc": "Anne eli değmiş gibi.", "tar": "1. Yumuşak bir hamur yoğur mayalandır.\n2. Parçalar koparıp elinle aç.\n3. Kızgın yağda arkalı önlü kızart."},

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
    {"ad": "Tas Kebabı", "kat": "Ana Yemek", "malz": ["Kuşbaşı Et", "Patates", "Havuç", "Soğan", "Salça"], "desc": "Lokum gibi et.", "tar": "1. Eti suyunu çekene kadar kavur.\n2. Soğan ve salçayı ekle.\n3. Küp doğranmış sebzeleri ve sıcak suyu ekle pişir."},
    
    # --- SEBZE YEMEKLERİ ---
    {"ad": "Mücver", "kat": "Ana Yemek", "malz": ["3 Kabak", "2 Yumurta", "Un", "Dereotu", "Peynir"], "desc": "Sebze sevmeyene bile yedirir.", "tar": "1. Kabağı rendele suyunu sık.\n2. Tüm malzemeleri karıştır.\n3. Kaşık kaşık kızgın yağa dök."},
    {"ad": "Zeytinyağlı Taze Fasulye", "kat": "Ana Yemek", "malz": ["Taze Fasulye", "Domates", "Soğan", "Şeker", "Zeytinyağı"], "desc": "Soğuk yenen lezzet.", "tar": "1. Soğanı kavur fasulyeyi ekle sarart.\n2. Domates rendesi ve şekeri at.\n3. Kısık ateşte kendi suyuyla pişir."},
    {"ad": "Ispanak Yemeği", "kat": "Ana Yemek", "malz": ["Ispanak", "Pirinç", "Soğan", "Salça", "Yoğurt"], "desc": "Temel Reis güç kaynağı.", "tar": "1. Soğanı salçayla kavur.\n2. Yıkanmış ıspanakları ekle söndür.\n3. Az pirinç ve sıcak su ekle pişir."},
    {"ad": "Biber Dolması", "kat": "Ana Yemek", "malz": ["Dolmalık Biber", "Pirinç", "Kıyma", "Soğan", "Maydanoz"], "desc": "Yoğurtla servis et.", "tar": "1. İç harcı çiğden hazırla.\n2. Biberleri doldur tencereye diz.\n3. Salçalı su ile kısık ateşte pişir."},

    # --- SALATA & MEZE (YENİ KATEGORİ) ---
    {"ad": "Çoban Salata", "kat": "Salata", "malz": ["Domates", "Salatalık", "Biber", "Soğan", "Maydanoz"], "desc": "Her yemeğin yanına.", "tar": "1. Tüm malzemeleri küçük küpler halinde doğra.\n2. Zeytinyağı, limon ve tuzla harmanla."},
    {"ad": "Cacık", "kat": "Meze", "malz": ["Yoğurt", "Salatalık", "Sarımsak", "Nane", "Zeytinyağı"], "desc": "Pilavın ekürisi.", "tar": "1. Salatalıkları rendeleyip yoğurtla karıştır.\n2. Ezilmiş sarımsak ve tuz ekle.\n3. Üzerine zeytinyağı ve nane gezdir."},
    {"ad": "Kısır", "kat": "Salata", "malz": ["İnce Bulgur", "Salça", "Nar Ekşisi", "Yeşillik", "Limon"], "desc": "Altın günlerinin yıldızı.", "tar": "1. Bulguru sıcak suyla şişir.\n2. Salçalı sosu yedir.\n3. Yeşillik ve nar ekşisini ekle."},
    {"ad": "Rus Salatası", "kat": "Meze", "malz": ["Garnitür (Bezelye/Havuç/Patates)", "Mayonez", "Yoğurt", "Salatalık Turşusu"], "desc": "Soğuk sandviçlerin vazgeçilmezi.", "tar": "1. Suyu süzülmüş garnitürü kaba al.\n2. Küp doğranmış turşu, mayonez ve yoğurtla karıştır."},
    {"ad": "Şakşuka", "kat": "Meze", "malz": ["Patlıcan", "Biber", "Domates", "Sarımsak", "Yoğurt"], "desc": "Kızartma sevenlere.", "tar": "1. Patlıcan ve biberi küp doğrayıp kızart.\n2. Domates ve sarımsakla sos yapıp üzerine dök."},

    # --- MAKARNA & PİLAV ---
    {"ad": "Salçalı Makarna", "kat": "Makarna", "malz": ["Makarna", "Domates Salçası", "Kuru Nane", "Sıvı Yağ"], "desc": "Öğrenci efsanesi.", "tar": "1. Makarnayı haşla süz.\n2. Tencerede yağ, salça ve naneyi yak.\n3. Makarnayı ekle karıştır."},
    {"ad": "Kremalı Mantarlı Makarna", "kat": "Makarna", "malz": ["Makarna", "Mantar", "Krema", "Maydanoz"], "desc": "İtalyan restoranı gibi.", "tar": "1. Mantarları yüksek ateşte sotele.\n2. Kremayı ekle kaynat.\n3. Haşlanmış makarna ile buluştur."},
    {"ad": "Pirinç Pilavı", "kat": "Pilav", "malz": ["Baldo Pirinç", "Arpa Şehriye", "Tereyağı", "Tavuk Suyu"], "desc": "Tane tane dökülen.", "tar": "1. Pirinci sıcak suda beklet.\n2. Şehriyeyi tereyağında kavur.\n3. Pirinci ekle, sıcak suyu ver demle."},
    {"ad": "Meyhane Pilavı", "kat": "Pilav", "malz": ["Bulgur", "Domates", "Biber", "Soğan", "Salça"], "desc": "Yanına cacıkla gider.", "tar": "1. Soğan ve biberi kavur.\n2. Salça ve domatesi ekle.\n3. Bulguru ve suyu ekle pişir."},
    
    # --- TATLILAR ---
    {"ad": "Fırın Sütlaç", "kat": "Tatlı", "malz": ["1 Litre Süt", "Pirinç", "Şeker", "Nişasta", "Vanilya"], "desc": "Üzeri nar gibi kızarmış.", "tar": "1. Pirinci haşla, sütü ve şekeri ekle.\n2. Nişastayla bağla.\n3. Güveçlere koyup fırında üstünü yak."},
    {"ad": "İrmik Helvası", "kat": "Tatlı", "malz": ["İrmik", "Tereyağı", "Süt", "Şeker", "Fıstık"], "desc": "Sıcak sıcak dondurmayla.", "tar": "1. İrmiği ve fıstığı tereyağında rengi dönene kadar kavur.\n2. Sıcak sütlü şerbeti dök.\n3. Demlenmeye bırak."},
    {"ad": "Magnolia", "kat": "Tatlı", "malz": ["Süt", "Yumurta Sarısı", "Nişasta", "Krema", "Bisküvi", "Çilek"], "desc": "Hafif ve şık.", "tar": "1. Kremasız muhallebiyi pişir soğut.\n2. Kremayı ekle çırp.\n3. Bisküvi ve meyveyle kat kat diz."},
    {"ad": "Mozaik Pasta", "kat": "Tatlı", "malz": ["Petibör Bisküvi", "Kakao", "Tereyağı", "Süt", "Şeker"], "desc": "Pişmeyen pasta.", "tar": "1. Sos malzemelerini erit.\n2. Kırılmış bisküvilerle karıştır.\n3. Streçleyip buzluğa at."},
    {"ad": "Islak Kek (Brownie)", "kat": "Tatlı", "malz": ["Yumurta", "Şeker", "Süt", "Yağ", "Kakao", "Un"], "desc": "Bol soslu.", "tar": "1. Keki çırpıp pişir.\n2. Kalan malzemelerle sos yap kaynat.\n3. Fırından çıkan sıcak keke dök."},
    {"ad": "Şekerpare", "kat": "Tatlı", "malz": ["Un", "İrmik", "Pudra Şekeri", "Yumurta", "Tereyağı", "Şerbet"], "desc": "Klasik şerbetli tatlı.", "tar": "1. Hamuru yoğur yuvarlak şekil ver.\n2. Ortasına fındık batır fırınla.\n3. Sıcak tatlıya ılık şerbet dök."},
]

def tarif_uret(malzeme):
    m = malzeme.title()
    return {
        "ad": f"Fırında Özel {m}", "kat": "Şefin Spesiyali",
        "malz": [m, "Zeytinyağı", "Kekik", "Tuz"],
        "desc": "Bu malzeme ile garantili lezzet.",
        "tar": f"1. {m} yıkanır, baharatlanır.\n2. 200 derece fırında pişirilir."
    }

def tarifleri_bul(girdi, kategori_filtresi):
    girdi = girdi.lower()
    bulunanlar = []
    tam_liste = TUM_TARIFLER + tarifleri_yukle()
    for tarif in tam_liste:
        if kategori_filtresi != "Tümü" and tarif.get("kat") != kategori_filtresi: continue
        malz_text = " ".join(tarif["malz"]).lower() if isinstance(tarif["malz"], list) else str(tarif["malz"]).lower()
        if not girdi or (girdi in malz_text or girdi in tarif["ad"].lower()): bulunanlar.append(tarif)
    if not bulunanlar and girdi and kategori_filtresi == "Tümü": bulunanlar.append(tarif_uret(girdi))
    return bulunanlar

# --- 6. ARAYÜZ ---

# Zaman Algısı
saat = datetime.now().hour
if 5 <= saat < 12: selamlama = "Günaydın ☀️ Kahvaltı Zamanı!"
elif 12 <= saat < 18: selamlama = "Tünaydın 🌤️ Öğle Yemeği Hazır mı?"
else: selamlama = "İyi Akşamlar 🌙 Akşama Ne Yesek?"

with st.sidebar:
    try: st.image("logo.png", use_container_width=True)
    except: pass
    st.markdown("### 🎛️ Filtreler")
    kategori = st.radio("Menü:", ["Tümü", "Kahvaltı", "Çorba", "Ana Yemek", "Tavuk", "Makarna", "Pilav", "Tatlı", "Kullanıcı"])
    st.markdown("---")
    st.success("👨‍💻 **Status:** Online (Migros Mode)")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try: st.image("logo.png", use_container_width=True)
    except: pass

st.title("Dolap Şefi")
st.markdown(f"<p style='text-align: center; color: #ffcc00; margin-top: -10px; font-weight: 600;'>{selamlama}</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔥 Tarif Bulucu", "🏆 Şefler Vitrini"])

# --- TAB 1: ARAMA ---
with tab1:
    if st.session_state.secilen_tarif is None:
        malzemeler = st.text_input("Dolabında ne var?", placeholder="Örn: Yumurta, Patates...")
        sonuclar = tarifleri_bul(malzemeler, kategori)
        
        if malzemeler or kategori != "Tümü":
            st.markdown(f"##### 🎉 {len(sonuclar)} Lezzet Bulundu")
            for i, tarif in enumerate(sonuclar):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    malz_goster = ", ".join(tarif['malz'][:4]) + "..." if isinstance(tarif['malz'], list) else str(tarif['malz'])[:40]
                    st.markdown(f"""
                    <div class="haber-kart">
                        <div style="display:flex; justify-content:space-between;">
                            <h3 style="margin:0; color:#FFCC00;">{tarif['ad']}</h3>
                            <span style="font-size:10px; border:1px solid #fff; padding:2px 6px; border-radius:10px;">{tarif.get('kat','Genel')}</span>
                        </div>
                        <p style="color:#ddd; margin:5px 0;">{tarif['desc']}</p>
                        <span style="font-size:12px; color:#888;">🛒 {malz_goster}</span>
                    </div>""", unsafe_allow_html=True)
                with col_b:
                    st.write("")
                    if st.button("Tarife Bak →", key=f"btn_{i}"):
                        st.session_state.secilen_tarif = tarif
                        st.rerun()
    else:
        t = st.session_state.secilen_tarif
        if st.button("⬅️ Geri Dön"):
            st.session_state.secilen_tarif = None
            st.rerun()
        st.divider()
        st.markdown(f"<h1 style='text-align:left; color:#FFCC00;'>{t['ad']}</h1>", unsafe_allow_html=True)
        col_d1, col_d2 = st.columns([1, 2])
        with col_d1:
            st.markdown('<div class="malzeme-kutusu"><h4>🛒 Malzemeler</h4><ul>', unsafe_allow_html=True)
            malz_list = t['malz'] if isinstance(t['malz'], list) else t['malz'].split('\n')
            for m in malz_list: st.markdown(f"<li>{m}</li>", unsafe_allow_html=True)
            st.markdown('</ul></div>', unsafe_allow_html=True)
        with col_d2:
             st.markdown(f"<div style='background:rgba(255,255,255,0.05); padding:20px; border-radius:15px;'>{t['tar']}</div>", unsafe_allow_html=True)
             
             # --- MİGROS BUTONU ENTEGRASYONU ---
             ana_malzeme = malz_list[0].split(" ")[-1] if malz_list else "Yemek"
             link = f"https://www.migros.com.tr/arama?q={ana_malzeme}"
             st.markdown(f'<a href="{link}" target="_blank" class="btn-migros">🍊 Malzemeleri Migros\'tan Söyle</a>', unsafe_allow_html=True)

# --- TAB 2: VİTRİN ---
with tab2:
    st.subheader("🌟 Haftanın En İyileri")
    st.video("https://cdn.pixabay.com/video/2022/10/24/136195-763486150_large.mp4")
    st.caption("🔥 Şefin Seçimi: Izgara Mevsimi Başladı!")

    st.markdown("---")
    st.markdown("### 🍝 Topluluk Tarifler")
    kullanici_t = tarifleri_yukle()
    if kullanici_t:
        kullanici_t.sort(key=lambda x: x.get('likes', 0), reverse=True)
        for idx, k in enumerate(kullanici_t):
            with st.container():
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"""
                    <div class="haber-kart" style="border-left: 5px solid #28a745;">
                        <h4 style="margin:0;">{k['ad']} <span style="font-size:12px; color:#aaa;">(Şef: {k['sef']})</span></h4>
                        <p><i>"{k['desc']}"</i></p>
                    </div>""", unsafe_allow_html=True)
                with c2:
                    st.write("")
                    likes = k.get('likes', 0)
                    if st.button(f"❤️ {likes}", key=f"like_{idx}"):
                        begeni_arttir(idx)
                        st.balloons()
                        st.rerun()

    st.markdown("---")
    with st.expander("➕ Kendi Tarifini Ekle"):
        with st.form("ekle_form"):
            k_ad = st.text_input("Şef Adı")
            t_ad = st.text_input("Yemek Adı")
            t_desc = st.text_input("Slogan")
            t_malz = st.text_area("Malzemeler")
            t_tar = st.text_area("Tarif")
            if st.form_submit_button("Yayınla"):
                if k_ad and t_ad:
                    yeni = {"ad": t_ad, "kat": "Kullanıcı", "sef": k_ad, "desc": t_desc, "tar": t_tar, "malz": t_malz.split('\n'), "likes": 0}
                    tarifi_kaydet(yeni)
                    st.success("Eklendi!")
                    time.sleep(1)
                    st.rerun()

st.markdown("<div style='text-align:center; padding:20px; color:#666; font-size:12px;'>© 2026 Dolap Şefi Inc.</div>", unsafe_allow_html=True)

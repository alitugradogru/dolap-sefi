import streamlit as st
import requests
from deep_translator import GoogleTranslator
import random
import json
import os

# --- 1. AYARLAR ---
st.set_page_config(
    page_title="Dolap Şefi: Dolaptaki Yardımcınız", 
    page_icon="👨‍🍳", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# API ANAHTARI
API_KEY = "1cb477a1c23a4594aac7d09f5099ae8b"
DOSYA_ADI = "tarifler.json"

# --- 2. HAFIZA VE DOSYA YÖNETİMİ ---

def verileri_yukle():
    if os.path.exists(DOSYA_ADI):
        try:
            with open(DOSYA_ADI, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return [] 
    return []

def verileri_kaydet(veri_listesi):
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(veri_listesi, f, ensure_ascii=False, indent=4)

if 'sayfa' not in st.session_state:
    st.session_state.sayfa = 'ana_sayfa'
if 'secilen_tarif_id' not in st.session_state:
    st.session_state.secilen_tarif_id = None
if 'arama_sonuclari' not in st.session_state:
    st.session_state.arama_sonuclari = []
if 'vitrin_verisi' not in st.session_state:
    st.session_state.vitrin_verisi = []
if 'kullanici_tarifleri' not in st.session_state:
    st.session_state.kullanici_tarifleri = verileri_yukle()

# --- 3. FONKSİYONLAR ---

def cevir_tr_en(metin):
    try: return GoogleTranslator(source='tr', target='en').translate(metin)
    except: return metin

def cevir_en_tr(metin):
    try: return GoogleTranslator(source='en', target='tr').translate(metin)
    except: return metin

KATEGORILER = {
    "Tümü": None,
    "Kahvaltı 🥞": "breakfast",
    "Ana Yemek 🥘": "main course",
    "Çorba 🥣": "soup",
    "Tatlı 🍰": "dessert",
    "Atıştırmalık 🍿": "snack",
    "Salata 🥗": "salad",
    "İçecek 🥤": "drink"
}

@st.cache_data(ttl=3600, show_spinner=False)
def vitrin_getir():
    url = "https://api.spoonacular.com/recipes/random"
    params = {"apiKey": API_KEY, "number": 12}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            recipes = response.json().get('recipes', [])
            for r in recipes:
                r['title_tr'] = cevir_en_tr(r['title'])
            return recipes
    except: return []
    return []

@st.cache_data(ttl=3600, show_spinner=False)
def tarif_ara(malzemeler, kategori_kod):
    ingilizce_malz = cevir_tr_en(malzemeler)
    url = "https://api.spoonacular.com/recipes/complexSearch"
    params = {
        "apiKey": API_KEY, "number": 12, "addRecipeInformation": False
    }
    if kategori_kod: params["type"] = kategori_kod
    if ingilizce_malz:
        params["includeIngredients"] = ingilizce_malz
        params["sort"] = "min-missing-ingredients"
    else:
        if kategori_kod: params["sort"] = "popularity"
        else: return []

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            veriler = response.json()
            sonuclar = veriler.get('results', [])
            for yemek in sonuclar:
                yemek['title_tr'] = cevir_en_tr(yemek['title'])
            return sonuclar
    except: return []
    return []

@st.cache_data(ttl=3600, show_spinner=False)
def detay_getir(tarif_id):
    if isinstance(tarif_id, str) and tarif_id.startswith("local_"):
        guncel_liste = st.session_state.kullanici_tarifleri
        for t in guncel_liste:
            if t and 'id' in t and t['id'] == tarif_id:
                return t
        return None

    url = f"https://api.spoonacular.com/recipes/{tarif_id}/information"
    params = {"apiKey": API_KEY}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            detay = response.json()
            detay['title'] = cevir_en_tr(detay['title'])
            for m in detay['extendedIngredients']:
                m['original'] = cevir_en_tr(m['original'])
            if detay.get('analyzedInstructions'):
                for step in detay['analyzedInstructions'][0]['steps']:
                    step['step'] = cevir_en_tr(step['step'])
            elif detay.get('instructions'):
                detay['instructions'] = cevir_en_tr(detay['instructions'])
            return detay
    except: return None
    return None

# --- 4. TASARIM (GİZLİLİK MODU AKTİF) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
:root { color-scheme: dark; }

/* GİZLİLİK AYARLARI (Menüleri Sakla) */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

[data-testid="stAppViewContainer"], .stApp { background-color: #0e1117 !important; background-image: radial-gradient(circle at 50% 0%, #2b0c0c 0%, #0e1117 80%) !important; color: white !important; font-family: 'Poppins', sans-serif; }
p, h1, h2, h3, h4, span, div, label { color: white !important; }
h1 { font-weight: 900; font-size: 3rem; background: -webkit-linear-gradient(45deg, #FF9966, #FF5E62); -webkit-background-clip: text; -webkit-text-fill-color: transparent !important; text-align: center; margin-top: -50px; }

[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] { background: rgba(255, 255, 255, 0.05) !important; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 15px; transition: transform 0.3s; }
img { border-radius: 10px; width: 100%; object-fit: cover; }
.stButton > button { width: 100%; border-radius: 10px; font-weight: 700; color: white !important; background: linear-gradient(90deg, #FF9966 0%, #FF5E62 100%) !important; border: none; padding: 10px; }
.btn-migros { display: block; width: 100%; background: linear-gradient(45deg, #F7941D, #FFCC00); color: white !important; text-align: center; padding: 15px; border-radius: 12px; font-weight: 900; text-decoration: none; margin-top: 20px; box-shadow: 0 4px 15px rgba(247, 148, 29, 0.4); transition: 0.3s; }
[data-testid="stSidebar"] { background-color: #161a25 !important; border-right: 1px solid #333; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea { color: white !important; background-color: #262730 !important; }
@media only screen and (max-width: 600px) { h1 { font-size: 2rem !important; } .stButton > button { padding: 8px !important; font-size: 0.9rem !important; } }
</style>
""", unsafe_allow_html=True)

# --- 5. EKRAN YÖNETİMİ ---

if st.session_state.sayfa == 'detay':
    if st.button("⬅️ Geri Dön", use_container_width=True):
        st.session_state.sayfa = 'ana_sayfa'
        st.rerun()

    with st.spinner("Tarif açılıyor..."):
        d = detay_getir(st.session_state.secilen_tarif_id)
        if d:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(d['image'], use_container_width=True)
                st.info(f"⏱️ **Süre:** {d['readyInMinutes']} dk\n\n🍴 **Porsiyon:** {d['servings']} Kişi")
                try: ana_malz = d['extendedIngredients'][0]['original'].split(' ')[-1]
                except: ana_malz = "Yemek"
                st.markdown(f'<a href="https://www.migros.com.tr/arama?q={ana_malz}" target="_blank" class="btn-migros">🛒 {ana_malz} Sipariş Ver</a>', unsafe_allow_html=True)
            with col2:
                st.markdown(f"<h2 style='color: #FF9966;'>{d['title']}</h2>", unsafe_allow_html=True)
                
                st.markdown("### 🛒 Malzemeler")
                if d.get('extendedIngredients'):
                    for m in d['extendedIngredients']:
                        st.write(f"• {m['original']}")
                else: st.write("• Malzeme bilgisi yok.")
                
                st.markdown("### 👨‍🍳 Hazırlanışı")
                if d.get('analyzedInstructions'):
                    for step in d['analyzedInstructions'][0]['steps']:
                        st.write(f"**{step['number']}.** {step['step']}")
                elif d.get('instructions'):
                     st.write(d['instructions'])
                else: st.write("Tarif detayı yok.")
        else:
            st.error("Hata: Tarif yüklenemedi.")

else:
    with st.sidebar:
        st.title("🍽️ Menü")
        secenekler = list(KATEGORILER.keys())
        secenekler.append("✍️ Tarif Ekle (Yeni)")
        secilen_menu = st.radio("Seçimini Yap:", secenekler)
        st.markdown("---")

    if secilen_menu == "✍️ Tarif Ekle (Yeni)":
        st.title("✍️ Kendi Tarifini Ekle")
        st.markdown("Buradan eklediğin tarif **kalıcı olarak** vitrine eklenir.")
        
        with st.form("tarif_ekle_form"):
            y_isim = st.text_input("Yemeğin Adı", placeholder="Örn: Anne Köftesi")
            y_sure = st.number_input("Hazırlama Süresi (Dk)", min_value=5, value=30)
            y_kisi = st.number_input("Kaç Kişilik?", min_value=1, value=2)
            y_resim = st.text_input("Resim Linki (Varsa)", placeholder="https://...")
            y_malz = st.text_area("Malzemeler", placeholder="Kıyma\nSoğan...")
            y_yapilis = st.text_area("Yapılışı", placeholder="Yapılışını anlat...")
            
            kaydet = st.form_submit_button("✅ Tarifi Kaydet ve Yayınla")
            
            if kaydet and y_isim:
                yeni_id = f"local_{random.randint(1000, 9999)}"
                if not y_resim: y_resim = "https://img.freepik.com/free-vector/chef-hat-concept-illustration_114360-3669.jpg"
                malz_listesi = [{"original": m.strip()} for m in y_malz.split('\n') if m.strip()]
                
                yeni_tarif = {
                    "id": yeni_id,
                    "title": y_isim,
                    "image": y_resim,
                    "readyInMinutes": y_sure,
                    "servings": y_kisi,
                    "title_tr": y_isim,
                    "extendedIngredients": malz_listesi,
                    "instructions": y_yapilis,
                    "analyzedInstructions": []
                }
                
                st.session_state.kullanici_tarifleri.insert(0, yeni_tarif)
                verileri_kaydet(st.session_state.kullanici_tarifleri)
                st.success(f"Harika! **{y_isim}** dosyaya kaydedildi ve yayınlandı.")
                st.balloons()

    else:
        secilen_kategori_kod = KATEGORILER[secilen_menu]
        st.title("👨‍🍳 Dolap Şefi: Dolaptaki Yardımcınız")
        
        with st.form("arama_formu"):
            c1, c2 = st.columns([3, 1])
            with c1:
                malz = st.text_input("Dolapta ne var?", placeholder="Örn: Tavuk, Krema...")
            with c2:
                st.write(""); st.write("")
                ara_butonu = st.form_submit_button("🔍 BUL", use_container_width=True)

        gosterilecek_liste = []
        
        # 1. DURUM: Arama butonuna basıldıysa (Sonuçları Getir)
        if ara_butonu:
             with st.spinner(f"Aranıyor..."):
                st.session_state.arama_sonuclari = tarif_ara(malz, secilen_kategori_kod)
                gosterilecek_liste = st.session_state.arama_sonuclari
        
        # 2. DURUM: Arama yapılmadıysa ve sonuçlar boşsa...
        elif not st.session_state.arama_sonuclari:
            
            # --- KRİTİK DEĞİŞİKLİK BURADA ---
            # Sadece "Tümü" seçiliyse Vitrini göster.
            if secilen_menu == "Tümü":
                gosterilecek_liste = list(st.session_state.kullanici_tarifleri)
                
                if not st.session_state.vitrin_verisi:
                     with st.spinner("Menü Hazırlanıyor..."):
                        st.session_state.vitrin_verisi = vitrin_getir()
                gosterilecek_liste += st.session_state.vitrin_verisi
                st.markdown(f"### ✨ Vitrin")
            
            # Başka bir kategori seçiliyse (Örn: Kahvaltı) BOŞ GÖSTER.
            else:
                gosterilecek_liste = [] 
                st.info(f"💡 **{secilen_menu}** kategorisinde arama yapmak için malzemeleri girip 'BUL' butonuna basın.")

        # 3. DURUM: Hafızadaki sonuçları göster
        else:
             gosterilecek_liste = st.session_state.arama_sonuclari

        # LİSTELEME
        if gosterilecek_liste:
            cols = st.columns(4)
            for i, t in enumerate(gosterilecek_liste):
                if not t or 'id' not in t: continue

                with cols[i % 4]:
                    with st.container():
                        st.image(t.get('image', 'https://via.placeholder.com/300'), use_container_width=True)
                        baslik = t.get('title_tr', t.get('title', 'İsimsiz'))
                        if len(baslik) > 35: baslik = baslik[:32] + "..."
                        st.markdown(f"**{baslik}**")
                        
                        if st.button("Tarife Git", key=f"btn_{t['id']}"):
                            st.session_state.secilen_tarif_id = t['id']
                            st.session_state.sayfa = 'detay'
                            st.rerun()
        else:
             if ara_butonu: st.warning("Tarif bulunamadı.")

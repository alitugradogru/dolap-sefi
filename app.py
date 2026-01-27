import streamlit as st
import requests
# Çeviri için gerekli kütüphane
from deep_translator import GoogleTranslator

# --- 1. AYARLAR ---
st.set_page_config(
    page_title="Dolap Şefi: PRO", 
    page_icon="👨‍🍳", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# API ANAHTARI
API_KEY = "1cb477a1c23a4594aac7d09f5099ae8b"

# --- 2. AKILLI ÇEVİRİ MOTORU (YAPAY ZEKA) ---
def cevir_tr_en(metin):
    """Türkçeden İngilizceye çevirir (API araması için)"""
    try:
        return GoogleTranslator(source='tr', target='en').translate(metin)
    except:
        return metin

def cevir_en_tr(metin):
    """İngilizceden Türkçeye çevirir (Ekrana yazdırmak için)"""
    try:
        return GoogleTranslator(source='en', target='tr').translate(metin)
    except:
        return metin

# --- 3. FONKSİYONLAR ---
def tarif_ara(malzemeler):
    # 1. ADIM: Türkçe malzemeyi İngilizceye çevir
    ingilizce_malz = cevir_tr_en(malzemeler)
    
    url = f"https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "apiKey": API_KEY,
        "ingredients": ingilizce_malz,
        "number": 8, # 8 Adet getir (Hızlı olsun diye)
        "ranking": 1,
        "ignorePantry": True
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            sonuclar = response.json()
            # 2. ADIM: Başlıkları Türkçeye çevir
            for yemek in sonuclar:
                yemek['title_tr'] = cevir_en_tr(yemek['title'])
            return sonuclar
        elif response.status_code == 402:
            st.error("Günlük API limitin doldu şefim! Yarın tekrar gel.")
            return []
    except:
        return []
    return []

def detay_getir(tarif_id):
    url = f"https://api.spoonacular.com/recipes/{tarif_id}/information"
    params = {"apiKey": API_KEY}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            detay = response.json()
            
            # --- DETAYLI ÇEVİRİ İŞLEMİ ---
            # Başlık
            detay['title'] = cevir_en_tr(detay['title'])
            
            # Malzemeler
            for m in detay['extendedIngredients']:
                m['original'] = cevir_en_tr(m['original'])
            
            # Tarif Adımları
            if detay.get('analyzedInstructions'):
                for step in detay['analyzedInstructions'][0]['steps']:
                    step['step'] = cevir_en_tr(step['step'])
            elif detay.get('instructions'):
                detay['instructions'] = cevir_en_tr(detay['instructions'])
            
            return detay
    except:
        return None
    return None

# --- 4. TASARIM (PREMIUM CSS) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');

/* Arka Plan */
.stApp {
    background-color: #0e1117;
    background-image: radial-gradient(circle at 50% 0%, #2b0c0c 0%, #0e1117 80%);
    color: white;
    font-family: 'Poppins', sans-serif;
}

/* Başlık */
h1 {
    font-weight: 900;
    font-size: 3rem;
    background: -webkit-linear-gradient(45deg, #FF9966, #FF5E62);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 20px;
}

/* Kartlar */
[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 15px;
    transition: transform 0.3s;
}
[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"]:hover {
    border-color: #FF9966;
    transform: translateY(-5px);
}

img { border-radius: 10px; width: 100%; object-fit: cover; }

/* Genel Butonlar */
.stButton > button {
    width: 100%;
    border-radius: 10px;
    font-weight: 700;
    color: white;
    background: linear-gradient(90deg, #FF9966 0%, #FF5E62 100%);
    border: none;
    padding: 10px;
}

/* ÖZEL MİGROS BUTONU (DİKKAT ÇEKİCİ) */
.btn-migros {
    display: block; width: 100%;
    background: linear-gradient(45deg, #F7941D, #FFCC00);
    color: white !important;
    text-align: center;
    padding: 15px;
    border-radius: 12px;
    font-weight: 900;
    text-decoration: none;
    margin-top: 20px;
    box-shadow: 0 4px 15px rgba(247, 148, 29, 0.4);
    font-size: 1.1rem;
    transition: 0.3s;
}
.btn-migros:hover { 
    transform: scale(1.05); 
    box-shadow: 0 6px 20px rgba(247, 148, 29, 0.6);
}
</style>
""", unsafe_allow_html=True)

# --- 5. ANA SAYFA ---
st.title("👨‍🍳 Dolap Şefi: Tam Türkçe")
st.markdown("<p style='text-align:center; color:#ccc;'>İstediğin malzemeyi yaz, dünya mutfağı Türkçeye çevrilip önüne gelsin.</p>", unsafe_allow_html=True)

if 'secilen' not in st.session_state: st.session_state.secilen = None

# Arama Bölümü
col1, col2 = st.columns([3, 1])
with col1:
    malz = st.text_input("Dolapta ne var?", placeholder="Örn: Karnabahar, Zerdeçal, Tavuk (Her şeyi yazabilirsin!)")
with col2:
    st.write(""); st.write("")
    ara = st.button("🔍 BUL", use_container_width=True)

# --- SONUÇLAR ---
if ara and malz:
    with st.spinner("🌍 Tarifler bulunuyor ve Türkçeye çevriliyor..."):
        sonuclar = tarif_ara(malz)
        if sonuclar:
            st.success(f"🎉 {len(sonuclar)} tarif bulundu!")
            cols = st.columns(4)
            for i, t in enumerate(sonuclar):
                with cols[i % 4]:
                    with st.container():
                        st.image(t['image'])
                        # Türkçe Başlık
                        baslik = t.get('title_tr', t['title'])
                        # Başlık çok uzunsa kısalt
                        if len(baslik) > 40: baslik = baslik[:37] + "..."
                        st.markdown(f"**{baslik}**")
                        
                        if st.button("Tarife Git", key=f"btn_{t['id']}"):
                            st.session_state.secilen = t['id']
                            st.rerun()
        else:
            st.warning("😔 Tarif bulunamadı veya API limiti doldu.")

# --- DETAY SAYFASI ---
if st.session_state.secilen:
    st.markdown("---")
    with st.spinner("Tarif detayları tercüme ediliyor... (Biraz sürebilir)"):
        d = detay_getir(st.session_state.secilen)
        if d:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(d['image'], use_container_width=True)
                st.info(f"⏱️ **Süre:** {d['readyInMinutes']} dk\n\n🍴 **Porsiyon:** {d['servings']} Kişi")
                
                # --- PARA KAZANDIRAN MİGROS BUTONU ---
                # Kullanıcının aradığı ilk malzemeyi alıp linke koyuyoruz
                ana_malz = malz.split(',')[0].strip() if malz else "Yemek"
                st.markdown(f'''
                    <a href="https://www.migros.com.tr/arama?q={ana_malz}" target="_blank" class="btn-migros">
                        🛒 {ana_malz} Sipariş Ver <br><small>(Migros Güvencesiyle)</small>
                    </a>
                ''', unsafe_allow_html=True)

            with col2:
                st.header(d['title']) # Türkçe Başlık
                
                st.markdown("### 🛒 Malzemeler")
                for m in d['extendedIngredients']:
                    # Türkçe Malzeme
                    st.write(f"• {m['original']}")
                
                st.markdown("### 👨‍🍳 Hazırlanışı")
                if d.get('analyzedInstructions'):
                    for step in d['analyzedInstructions'][0]['steps']:
                        # Türkçe Adım
                        st.write(f"**{step['number']}.** {step['step']}")
                else:
                    # Türkçe Metin
                    st.write(d.get('instructions', 'Tarif detayları alınamadı.'))
            
            if st.button("❌ KAPAT", use_container_width=True):
                st.session_state.secilen = None
                st.rerun()

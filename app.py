import streamlit as st
import requests
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

# --- 2. SESSION STATE (SAYFA HAFIZASI) ---
# Sayfa yenilense bile nerede olduğumuzu unutmasın diye.
if 'sayfa' not in st.session_state:
    st.session_state.sayfa = 'ana_sayfa' # Başlangıç sayfası
if 'secilen_tarif_id' not in st.session_state:
    st.session_state.secilen_tarif_id = None
if 'arama_sonuclari' not in st.session_state:
    st.session_state.arama_sonuclari = [] # Sonuçları hafızada tutuyoruz

# --- 3. ÇEVİRİ VE API FONKSİYONLARI ---
def cevir_tr_en(metin):
    try: return GoogleTranslator(source='tr', target='en').translate(metin)
    except: return metin

def cevir_en_tr(metin):
    try: return GoogleTranslator(source='en', target='tr').translate(metin)
    except: return metin

def tarif_ara(malzemeler):
    ingilizce_malz = cevir_tr_en(malzemeler)
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "apiKey": API_KEY,
        "ingredients": ingilizce_malz,
        "number": 8,
        "ranking": 1,
        "ignorePantry": True
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            sonuclar = response.json()
            for yemek in sonuclar:
                yemek['title_tr'] = cevir_en_tr(yemek['title'])
            return sonuclar
    except: return []
    return []

def detay_getir(tarif_id):
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

# --- 4. CSS TASARIM ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
.stApp { background-color: #0e1117; background-image: radial-gradient(circle at 50% 0%, #2b0c0c 0%, #0e1117 80%); color: white; font-family: 'Poppins', sans-serif; }
h1 { font-weight: 900; font-size: 3rem; background: -webkit-linear-gradient(45deg, #FF9966, #FF5E62); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 15px; transition: transform 0.3s; }
[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"]:hover { border-color: #FF9966; transform: translateY(-5px); }
img { border-radius: 10px; width: 100%; object-fit: cover; }
.stButton > button { width: 100%; border-radius: 10px; font-weight: 700; color: white; background: linear-gradient(90deg, #FF9966 0%, #FF5E62 100%); border: none; padding: 10px; }
.btn-migros { display: block; width: 100%; background: linear-gradient(45deg, #F7941D, #FFCC00); color: white !important; text-align: center; padding: 15px; border-radius: 12px; font-weight: 900; text-decoration: none; margin-top: 20px; box-shadow: 0 4px 15px rgba(247, 148, 29, 0.4); transition: 0.3s; }
.btn-migros:hover { transform: scale(1.05); }
</style>
""", unsafe_allow_html=True)

# --- 5. EKRAN YÖNETİMİ (ROUTER) ---

# --- EKRAN 1: DETAY SAYFASI ---
if st.session_state.sayfa == 'detay':
    if st.button("⬅️ Geri Dön (Listeye)", use_container_width=True):
        st.session_state.sayfa = 'ana_sayfa'
        st.rerun()

    with st.spinner("Tarif tercüme ediliyor..."):
        d = detay_getir(st.session_state.secilen_tarif_id)
        if d:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(d['image'], use_container_width=True)
                st.info(f"⏱️ **Süre:** {d['readyInMinutes']} dk\n\n🍴 **Porsiyon:** {d['servings']} Kişi")
                ana_malz = d['extendedIngredients'][0]['original'].split(' ')[-1] # İlk malzemeyi al
                st.markdown(f'<a href="https://www.migros.com.tr/arama?q={ana_malz}" target="_blank" class="btn-migros">🛒 {ana_malz} Sipariş Ver</a>', unsafe_allow_html=True)
            with col2:
                st.header(d['title'])
                st.markdown("### 🛒 Malzemeler")
                for m in d['extendedIngredients']:
                    st.write(f"• {m['original']}")
                st.markdown("### 👨‍🍳 Hazırlanışı")
                if d.get('analyzedInstructions'):
                    for step in d['analyzedInstructions'][0]['steps']:
                        st.write(f"**{step['number']}.** {step['step']}")
                else:
                    st.write(d.get('instructions', 'Tarif detayları kaynakta.'))
        else:
            st.error("Tarif detayları yüklenemedi.")

# --- EKRAN 2: ANA SAYFA (ARAMA) ---
else:
    st.title("👨‍🍳 Dolap Şefi: Global")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        malz = st.text_input("Dolapta ne var?", placeholder="Örn: Tavuk, Mantar, Krema")
    with col2:
        st.write(""); st.write("")
        if st.button("🔍 BUL", use_container_width=True):
            if malz:
                with st.spinner("Aranıyor..."):
                    st.session_state.arama_sonuclari = tarif_ara(malz)
            else:
                st.warning("Lütfen malzeme yazın.")

    # Sonuçları Göster (Hafızadan)
    if st.session_state.arama_sonuclari:
        st.success(f"🎉 {len(st.session_state.arama_sonuclari)} tarif bulundu!")
        cols = st.columns(4)
        for i, t in enumerate(st.session_state.arama_sonuclari):
            with cols[i % 4]:
                with st.container():
                    st.image(t['image'])
                    baslik = t.get('title_tr', t['title'])
                    if len(baslik) > 40: baslik = baslik[:37] + "..."
                    st.markdown(f"**{baslik}**")
                    
                    # BUTONA BASINCA SAYFA DEĞİŞTİRİYORUZ
                    if st.button("Tarife Git", key=f"btn_{t['id']}"):
                        st.session_state.secilen_tarif_id = t['id']
                        st.session_state.sayfa = 'detay' # Sayfa modunu değiştir
                        st.rerun() # Sayfayı yenile (Artık detay ekranı açılacak)

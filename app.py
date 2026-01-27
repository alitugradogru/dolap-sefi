import streamlit as st
import requests
import pandas as pd

# --- 1. AYARLAR ---
st.set_page_config(page_title="Dolap Şefi: GLOBAL", page_icon="🌍", layout="wide")

# 🔥🔥🔥 API ANAHTARIN BURADA (Hatasız) 🔥🔥🔥
API_KEY = "1cb477a1c23a4594aac7d09f5099ae8b"

# --- 2. FONKSİYONLAR (Spoonacular API) ---
def tarif_ara_malzeme_ile(malzemeler):
    """Malzemelere göre yemek arar"""
    url = f"https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "apiKey": API_KEY,
        "ingredients": malzemeler,
        "number": 12, # 12 tane tarif getir
        "ranking": 1, # En iyi eşleşenler
        "ignorePantry": True
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 402:
            st.error("Günlük API limitin dolmuş şefim! Yarın tekrar gel. (Bedava sürüm limiti)")
            return []
        else:
            return []
    except:
        return []

def tarif_detayi_getir(tarif_id):
    """Seçilen yemeğin detaylarını (Yapılışı, Malzemeler) getirir"""
    url = f"https://api.spoonacular.com/recipes/{tarif_id}/information"
    params = {"apiKey": API_KEY}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

# --- 3. TASARIM (CSS) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;600&display=swap');
.stApp { background-color: #0e1117; color: white; font-family: 'Poppins', sans-serif; }
.baslik { text-align: center; font-size: 3rem; background: -webkit-linear-gradient(45deg, #00b09b, #96c93d); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; }
.kart { background: rgba(255,255,255,0.05); border-radius: 15px; padding: 10px; margin-bottom: 20px; transition: 0.3s; border: 1px solid #333; }
.kart:hover { border-color: #96c93d; transform: translateY(-5px); }
.resim { width: 100%; border-radius: 10px; height: 200px; object-fit: cover; }
.yemek-adi { font-size: 1.1rem; font-weight: bold; margin-top: 10px; color: #eee; height: 50px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 4. ANA SAYFA ---
st.markdown('<div class="baslik">🌍 Dolap Şefi: Global</div>', unsafe_allow_html=True)
st.caption("Dünyadaki 360.000+ tarif arasından, senin dolabına uygun olanları bulur.")

# Oturum Durumu
if 'secilen_tarif' not in st.session_state: st.session_state.secilen_tarif = None

# Arama Kutusu
col1, col2 = st.columns([3, 1])
with col1:
    # Kullanıcıya ipucu verelim
    malzemeler = st.text_input("Dolabında ne var? (İngilizce daha iyi sonuç verir)", placeholder="Örn: tomato, cheese, chicken (veya domates, peynir)")
with col2:
    st.write("") # Boşluk
    st.write("") 
    ara_buton = st.button("🔍 Şef'e Sor", use_container_width=True)

# --- ARAMA SONUÇLARI ---
if ara_buton and malzemeler:
    with st.spinner("Dünya mutfağı taranıyor... 🌍"):
        sonuclar = tarif_ara_malzeme_ile(malzemeler)
        
        if sonuclar:
            st.success(f"🎉 Bu malzemelerle yapabileceğin {len(sonuclar)} harika tarif buldum!")
            
            # Kartları 3 kolon halinde diz
            cols = st.columns(3)
            for i, tarif in enumerate(sonuclar):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="kart">
                        <img src="{tarif['image']}" class="resim">
                        <div class="yemek-adi">{tarif['title']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Tarife Git 👉", key=f"btn_{tarif['id']}"):
                        st.session_state.secilen_tarif = tarif['id']
                        st.rerun()
        else:
            st.warning("😔 Bu malzemelerle eşleşen bir tarif bulamadım. Malzemeleri İngilizce yazmayı dener misin? (Örn: 'egg' yerine 'yumurta' yazınca bazen bulamayabilir)")

# --- DETAY SAYFASI ---
if st.session_state.secilen_tarif:
    st.markdown("---")
    with st.spinner("Tarif detayları getiriliyor..."):
        detay = tarif_detayi_getir(st.session_state.secilen_tarif)
        
        if detay:
            c1, c2 = st.columns([1, 2])
            with c1:
                st.image(detay['image'], use_container_width=True)
                st.markdown(f"### ⏱️ {detay['readyInMinutes']} Dakika | 🍴 {detay['servings']} Kişilik")
                
                st.info("**🛒 Gereken Malzemeler:**")
                for malz in detay['extendedIngredients']:
                    st.write(f"• {malz['original']}")
            
            with c2:
                st.header(detay['title'])
                # HTML temizliği yapılmış özet
                ozet = detay.get('summary', 'Açıklama yok.').replace("<b>","").replace("</b>","").replace("<a href=","").replace("</a>","")
                st.markdown(f"_{ozet[:400]}..._", unsafe_allow_html=True)
                
                st.success("**👨‍🍳 Hazırlanışı:**")
                # Adım adım anlatım varsa onu kullan
                if detay.get('analyzedInstructions'):
                    for adim in detay['analyzedInstructions'][0]['steps']:
                        st.write(f"**{adim['number']}.** {adim['step']}")
                else:
                    st.write(detay.get('instructions', 'Tarif detayları kaynak sitede mevcut.'))
            
            if st.button("❌ Kapat / Listeye Dön"):
                st.session_state.secilen_tarif = None
                st.rerun()

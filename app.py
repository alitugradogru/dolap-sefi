import streamlit as st
import time
import json
import os
from datetime import datetime
import random

# --- 1. AYARLAR ---
st.set_page_config(page_title="Dolap Şefi", page_icon="👨‍🍳", layout="wide", initial_sidebar_state="expanded")

# --- 2. DOSYA İSİMLERİ (SİHİRLİ DOKUNUŞ BURADA) ---
# İsmi değiştirdik ki sistem eski bozuk dosyayı unutup yenisini kursun.
TARIF_DB = "tarifler_v2.json"
USER_DB = "kullanici_tarifleri_v2.json" 
YORUM_DB = "yorumlar.json"
USER_AUTH = "kullanicilar.json"
FAV_DB = "favoriler.json"

# --- 3. DÜZELTİLMİŞ & DOĞRU FOTOLU MENÜ ---
DEV_MENU = [
    # --- KAHVALTI ---
    {"ad": "Trabzon Kuymak", "kat": "Kahvaltı", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Muhlama_-_Kuymak.jpg/640px-Muhlama_-_Kuymak.jpg", "malz": ["Mısır Unu", "Tereyağı", "Çeçil Peyniri", "Su"], "tar": "Tereyağını erit, unu kavur. Suyu ekle pişir, peyniri ekle.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Menemen", "kat": "Kahvaltı", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Menemen.jpg/640px-Menemen.jpg", "malz": ["Yumurta", "Domates", "Biber", "Yağ"], "tar": "Biberi kavur, domatesi ekle sos yap, yumurtayı kır.", "sure": "15 dk", "zorluk": "Kolay"},
    {"ad": "Sucuklu Yumurta", "kat": "Kahvaltı", "img": "https://images.unsplash.com/photo-1582236319830-14ef74b34b41?w=600", "malz": ["Sucuk", "Yumurta", "Tereyağı"], "tar": "Sucuğu pişir, yumurtayı kır.", "sure": "10 dk", "zorluk": "Kolay"},
    {"ad": "Pankek", "kat": "Kahvaltı", "img": "https://images.unsplash.com/photo-1506084868230-bb9d95c24759?w=600", "malz": ["Un", "Süt", "Yumurta", "Kabartma Tozu", "Şeker"], "tar": "Çırp, tavada arkalı önlü pişir.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Pişi", "kat": "Kahvaltı", "img": "https://iasbh.tmgrup.com.tr/856950/650/444/0/0/752/513?u=https://isbh.tmgrup.com.tr/sbh/2020/04/09/pisi-tarifi-mayali-ve-mayasiz-pisi-nasil-yapilir-1586427329297.jpg", "malz": ["Un", "Maya", "Tuz", "Su", "Yağ"], "tar": "Hamuru mayala, kızgın yağda kızart.", "sure": "45 dk", "zorluk": "Orta"},
    {"ad": "Çılbır", "kat": "Kahvaltı", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/%C3%87%C4%B1lb%C4%B1r.jpg/640px-%C3%87%C4%B1lb%C4%B1r.jpg", "malz": ["Yumurta", "Yoğurt", "Sarımsak", "Tereyağı", "Pulbiber"], "tar": "Yumurtayı poşe yap, sarımsaklı yoğurt ve yağla servis et.", "sure": "15 dk", "zorluk": "Orta"},
    {"ad": "Avokado Toast", "kat": "Kahvaltı", "img": "https://images.unsplash.com/photo-1588137372308-15f75323ca8d?w=600", "malz": ["Avokado", "Ekmek", "Limon", "Yumurta"], "tar": "Avokadoyu ez, ekmeğe sür, yumurta koy.", "sure": "10 dk", "zorluk": "Kolay"},
    {"ad": "Sigara Böreği", "kat": "Kahvaltı", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Sigara_b%C3%B6re%C4%9Fi_and_dips.jpg/640px-Sigara_b%C3%B6re%C4%9Fi_and_dips.jpg", "malz": ["Yufka", "Lor Peyniri", "Maydanoz"], "tar": "Sar ve kızart.", "sure": "25 dk", "zorluk": "Orta"},
    
    # --- ÇORBALAR ---
    {"ad": "Mercimek Çorbası", "kat": "Çorba", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Mercimek_%C3%A7orbas%C4%B1.jpg/640px-Mercimek_%C3%A7orbas%C4%B1.jpg", "malz": ["Mercimek", "Havuç", "Patates", "Soğan"], "tar": "Haşla, blenderdan geçir, yağ yak.", "sure": "30 dk", "zorluk": "Kolay"},
    {"ad": "Domates Çorbası", "kat": "Çorba", "img": "https://images.unsplash.com/photo-1547592166-23acbe3b624b?w=600", "malz": ["Domates", "Un", "Süt", "Kaşar"], "tar": "Unu kavur, domatesi ekle, sütle aç.", "sure": "25 dk", "zorluk": "Kolay"},
    {"ad": "Tavuk Suyu", "kat": "Çorba", "img": "https://images.unsplash.com/photo-1574653853961-9a674e227a92?w=600", "malz": ["Tavuk", "Tel Şehriye", "Limon"], "tar": "Tavuğu haşla, suyuna şehriye at.", "sure": "40 dk", "zorluk": "Kolay"},
    {"ad": "Brokoli Çorbası", "kat": "Çorba", "img": "https://images.unsplash.com/photo-1604152135912-04a022e23696?w=600", "malz": ["Brokoli", "Süt", "Krema", "Patates"], "tar": "Haşla, blender yap, krema ekle.", "sure": "30 dk", "zorluk": "Kolay"},

    # --- ANA YEMEKLER ---
    {"ad": "Kuru Fasulye", "kat": "Ana Yemek", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Kuru_fasulye.jpg/640px-Kuru_fasulye.jpg", "malz": ["Fasulye", "Et", "Salça", "Soğan"], "tar": "Akşamdan ısla, etle düdüklüde pişir.", "sure": "50 dk", "zorluk": "Orta"},
    {"ad": "Karnıyarık", "kat": "Ana Yemek", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Karn%C4%B1yar%C4%B1k.jpg/640px-Karn%C4%B1yar%C4%B1k.jpg", "malz": ["Patlıcan", "Kıyma", "Biber", "Domates"], "tar": "Patlıcanı kızart, kıymayı doldur, fırınla.", "sure": "60 dk", "zorluk": "Zor"},
    {"ad": "İzmir Köfte", "kat": "Ana Yemek", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Izmir_kofte.jpg/640px-Izmir_kofte.jpg", "malz": ["Kıyma", "Patates", "Domates Sos"], "tar": "Köfte patatesi kızart, sosla fırınla.", "sure": "50 dk", "zorluk": "Orta"},
    {"ad": "Tavuk Sote", "kat": "Ana Yemek", "img": "https://images.unsplash.com/photo-1604908177453-7462950a6a3b?w=600", "malz": ["Tavuk", "Biber", "Domates", "Soğan"], "tar": "Tavuğu mühürle, sebzeleri ekle.", "sure": "25 dk", "zorluk": "Kolay"},
    {"ad": "Fırında Tavuk Patates", "kat": "Ana Yemek", "img": "https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?w=600", "malz": ["Tavuk But", "Patates", "Salçalı Sos"], "tar": "Sosla harmanla, fırına at.", "sure": "50 dk", "zorluk": "Kolay"},
    {"ad": "Mantı", "kat": "Ana Yemek", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Manti.jpg/640px-Manti.jpg", "malz": ["Un", "Kıyma", "Yoğurt", "Salça"], "tar": "Hamuru aç doldur, haşla.", "sure": "90 dk", "zorluk": "Zor"},
    {"ad": "Biber Dolması", "kat": "Ana Yemek", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Biber_dolmas%C4%B1.jpg/640px-Biber_dolmas%C4%B1.jpg", "malz": ["Dolmalık Biber", "Pirinç", "Kıyma", "Nane"], "tar": "İçi hazırla doldur, tencerede pişir.", "sure": "45 dk", "zorluk": "Orta"},
    {"ad": "Şinitzel", "kat": "Ana Yemek", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Breitenlesau_Krug_Br%C3%A4u_Schnitzel.JPG/640px-Breitenlesau_Krug_Br%C3%A4u_Schnitzel.JPG", "malz": ["Tavuk Göğsü", "Galeta Unu", "Yumurta"], "tar": "Tavuğu incelt, panele, kızart.", "sure": "20 dk", "zorluk": "Orta"},
    
    # --- MAKARNA & PİLAV ---
    {"ad": "Pirinç Pilavı", "kat": "Makarna", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Pilav.jpg/640px-Pilav.jpg", "malz": ["Pirinç", "Tereyağı", "Şehriye"], "tar": "Şehriyeyi kavur, pirinci ekle, demle.", "sure": "25 dk", "zorluk": "Orta"},
    {"ad": "Spagetti Bolonez", "kat": "Makarna", "img": "https://images.unsplash.com/photo-1622973536968-3ead9e780960?w=600", "malz": ["Spagetti", "Kıyma", "Domates Sos", "Havuç"], "tar": "Kıymalı sos yap, makarnanın üstüne dök.", "sure": "30 dk", "zorluk": "Orta"},
    {"ad": "Kremalı Mantarlı Makarna", "kat": "Makarna", "img": "https://images.unsplash.com/photo-1555949258-eb67b1ef0ceb?w=600", "malz": ["Makarna", "Mantar", "Krema", "Fesleğen"], "tar": "Mantarı sotele, krema ekle, makarna ile karıştır.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Lahmacun", "kat": "Ana Yemek", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Lahmacun.jpg/640px-Lahmacun.jpg", "malz": ["Kıyma", "Lavaş", "Sebzeler"], "tar": "Lavaşa sür fırınla.", "sure": "20 dk", "zorluk": "Kolay"},

    # --- SEBZELİ ---
    {"ad": "Zeytinyağlı Fasulye", "kat": "Sebzeli", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Taze_fasulye.jpg/640px-Taze_fasulye.jpg", "malz": ["Taze Fasulye", "Domates", "Soğan", "Şeker"], "tar": "Kendi suyunda kısık ateşte pişir.", "sure": "50 dk", "zorluk": "Kolay"},
    {"ad": "İmam Bayıldı", "kat": "Sebzeli", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/%C4%B0mam_bay%C4%B1ld%C4%B1.jpg/640px-%C4%B0mam_bay%C4%B1ld%C4%B1.jpg", "malz": ["Patlıcan", "Bol Soğan", "Sarımsak", "Zeytinyağı"], "tar": "Patlıcanı kızart, soğanlı harçla doldur.", "sure": "50 dk", "zorluk": "Orta"},
    {"ad": "Mücver", "kat": "Sebzeli", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/M%C3%BCcver.jpg/640px-M%C3%BCcver.jpg", "malz": ["Kabak", "Yumurta", "Un", "Dereotu", "Peynir"], "tar": "Rendele, sık, karıştır, kızart.", "sure": "30 dk", "zorluk": "Orta"},
    
    # --- DÜNYA MUTFAĞI ---
    {"ad": "Ev Yapımı Burger", "kat": "Dünya Mutfağı", "img": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600", "malz": ["Kıyma", "Burger Ekmeği", "Cheddar", "Karamelize Soğan"], "tar": "Köfteyi döküm tavada pişir.", "sure": "30 dk", "zorluk": "Orta"},
    {"ad": "Pizza", "kat": "Dünya Mutfağı", "img": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600", "malz": ["Un", "Maya", "Mozzarella", "Sucuk/Mantar"], "tar": "Hamuru aç, malzemeyi diz fırınla.", "sure": "60 dk", "zorluk": "Zor"},
    {"ad": "Sushi", "kat": "Dünya Mutfağı", "img": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=600", "malz": ["Sushi Pirinci", "Nori Yosunu", "Salatalık", "Somon"], "tar": "Pirinci lapa yap, yosuna sar.", "sure": "50 dk", "zorluk": "Zor"},

    # --- TATLILAR ---
    {"ad": "Fırın Sütlaç", "kat": "Tatlı", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/F%C4%B1r%C4%B1n_S%C3%BCtla%C3%A7.jpg/640px-F%C4%B1r%C4%B1n_S%C3%BCtla%C3%A7.jpg", "malz": ["Süt", "Pirinç", "Şeker", "Nişasta"], "tar": "Güveçte fırınla.", "sure": "45 dk", "zorluk": "Orta"},
    {"ad": "Magnolia", "kat": "Tatlı", "img": "https://images.unsplash.com/photo-1517084507022-e613898f057c?w=600", "malz": ["Süt", "Krema", "Bisküvi", "Çilek/Muz"], "tar": "Muhallebi yap, bisküviyle diz.", "sure": "30 dk", "zorluk": "Kolay"},
    {"ad": "Islak Kek (Brownie)", "kat": "Tatlı", "img": "https://images.unsplash.com/photo-1606313564200-e75d5e30476d?w=600", "malz": ["Yumurta", "Süt", "Kakao", "Un"], "tar": "Keki pişir, sosunu dök.", "sure": "40 dk", "zorluk": "Kolay"},
    {"ad": "Künefe", "kat": "Tatlı", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/K%C3%BCnefe.jpg/640px-K%C3%BCnefe.jpg", "malz": ["Kadayıf", "Peynir", "Şerbet"], "tar": "Tavada arkalı önlü kızart.", "sure": "20 dk", "zorluk": "Orta"},
    {"ad": "Baklava", "kat": "Tatlı", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Baklava%281%29.png/640px-Baklava%281%29.png", "malz": ["Yufka", "Fıstık", "Şerbet"], "tar": "Hazır yufka ile yap.", "sure": "60 dk", "zorluk": "Zor"}
]

# --- 4. FONKSİYONLAR ---
def baslangic_verisini_olustur():
    if not os.path.exists(TARIF_DB):
        with open(TARIF_DB, "w", encoding="utf-8") as f:
            json.dump(DEV_MENU, f, ensure_ascii=False, indent=4)

# 🔥 GÜÇLENDİRİLMİŞ VERİ YÜKLEME (HATA ÖNLEYİCİ) 🔥
def db_yukle(dosya):
    if not os.path.exists(dosya):
        # Eğer dosya yoksa ve tarif dosyasıysa boş liste dön, yoksa sözlük dön
        return [] if "tarif" in dosya else {}
    
    with open(dosya, "r", encoding="utf-8") as f:
        try:
            veri = json.load(f)
        except:
            return [] if "tarif" in dosya else {}

    # TÜR KONTROLÜ (ÇOK ÖNEMLİ): Listeyse liste, değilse boş liste dön
    if "tarif" in dosya:
        return veri if isinstance(veri, list) else []
        
    return veri if isinstance(veri, dict) else {}

def db_kaydet(dosya, veri):
    with open(dosya, "w", encoding="utf-8") as f: json.dump(veri, f, ensure_ascii=False, indent=4)

def get_image(url, kat):
    # Eğer geçerli bir URL varsa onu kullan
    if url and "http" in url: return url
    # Yoksa kategoriye göre en azından "alakalı" bir yedek kullan
    defaults = {
        "Kahvaltı": "https://images.unsplash.com/photo-1533089862017-5c32417a1a08?w=600",
        "Ana Yemek": "https://images.unsplash.com/photo-1547592180-85f173990554?w=600",
        "Tatlı": "https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=600",
        "Çorba": "https://images.unsplash.com/photo-1547592166-23acbe3b624b?w=600",
        "Makarna": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=600",
        "Dünya Mutfağı": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=600",
        "Sebzeli": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600"
    }
    return defaults.get(kat, "https://images.unsplash.com/photo-1495195134817-aeb325a55b65?w=600")

# --- 5. BAŞLANGIÇ ---
baslangic_verisini_olustur()

# --- 6. ARAMA ---
def tarifleri_bul(girdi, kategori):
    girdi = girdi.lower()
    arananlar = [x.strip() for x in girdi.replace(",", " ").split() if x.strip()]
    tum_liste = db_yukle(TARIF_DB) + db_yukle(USER_DB)
    if not arananlar and kategori == "Tümü": return tum_liste
    bulunanlar = []
    for t in tum_liste:
        if kategori != "Tümü" and t.get("kat") != kategori: continue
        metin = (t["ad"] + " " + " ".join(t["malz"])).lower()
        if not arananlar: bulunanlar.append(t)
        else:
            for kelime in arananlar:
                if kelime in metin:
                    bulunanlar.append(t); break
    return bulunanlar

# --- 7. ARAYÜZ ---
if "login" not in st.session_state: st.session_state.login = False
if "user" not in st.session_state: st.session_state.user = None
if "page" not in st.session_state: st.session_state.page = "home"
if "secilen" not in st.session_state: st.session_state.secilen = None

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
.stApp { background-color: #0e1117; background-image: radial-gradient(circle at 50% 0%, #2e0000 0%, #0e1117 80%); color: #fff; font-family: 'Inter', sans-serif; }
.haber-kart { background: rgba(255,255,255,0.05); backdrop-filter: blur(10px); border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px; overflow: hidden; transition: 0.3s; }
.haber-kart:hover { transform: translateY(-5px); border-color: #ffcc00; }
.kart-resim { width: 100%; height: 180px; object-fit: cover; }
.kart-icerik { padding: 15px; }
.btn-migros { display: block; width: 100%; background: #ff7900; color: white !important; text-align: center; padding: 15px; border-radius: 12px; font-weight: bold; text-decoration: none; margin-top: 10px; }
.etiket { background: rgba(255, 204, 0, 0.2); color: #ffcc00; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-right: 5px; }
h1 { background: -webkit-linear-gradient(45deg, #FFCC00, #FF6B6B); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 4px 15px rgba(255, 69, 0, 0.4); }
</style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    if st.button("🏠 Ana Sayfa", use_container_width=True): st.session_state.page="home"; st.session_state.secilen=None; st.rerun()
    if st.button("🎲 Rastgele Yemek", use_container_width=True):
        tum = db_yukle(TARIF_DB) + db_yukle(USER_DB)
        if tum:
            t = random.choice(tum)
            st.session_state.secilen=t; st.session_state.page="detail"; st.rerun()
    
    st.markdown("---")
    if st.session_state.login:
        st.success(f"👤 {st.session_state.user}")
        if st.button("Profilim"): st.session_state.page="profile"; st.rerun()
        if st.button("Çıkış"): st.session_state.login=False; st.session_state.user=None; st.rerun()
    else:
        t1, t2 = st.tabs(["Giriş", "Kayıt"])
        with t1:
            k=st.text_input("Ad"); p=st.text_input("Şifre", type="password")
            if st.button("Gir"):
                u = db_yukle(USER_AUTH)
                if u.get(k)==p or (k=="admin" and p=="2026"): st.session_state.login=True; st.session_state.user=k; st.rerun()
                else: st.error("Hatalı")
        with t2:
            nk=st.text_input("Y. Ad"); np=st.text_input("Y. Şifre", type="password")
            if st.button("Kayıt"):
                u = db_yukle(USER_AUTH); u[nk]=np; db_kaydet(USER_AUTH, u); st.success("Oldu")
                
    st.markdown("---")
    kat = st.radio("Kategori:", ["Tümü", "Kahvaltı", "Çorba", "Ana Yemek", "Makarna", "Sebzeli", "Tatlı", "Dünya Mutfağı", "Kullanıcı"])

st.markdown(f'<h1 style="text-align:center;">Dolap Şefi</h1>', unsafe_allow_html=True)

# SAYFALAR
if st.session_state.page == "profile":
    st.header("👤 Profilim")
    tf, te = st.tabs(["❤️ Favoriler", "📝 Eklediklerim"])
    with tf:
        favs = db_yukle(FAV_DB).get(st.session_state.user, [])
        tum = db_yukle(TARIF_DB) + db_yukle(USER_DB)
        my_favs = [t for t in tum if t['ad'] in favs]
        for t in my_favs:
            with st.container():
                c1, c2 = st.columns([1,4])
                c1.image(get_image(t.get('img'), t.get('kat')))
                c2.subheader(t['ad']); 
                if c2.button("Git", key=f"f_{t['ad']}"): st.session_state.secilen=t; st.session_state.page="detail"; st.rerun()
            st.divider()
    with te:
        myt = [t for t in db_yukle(USER_DB) if t.get('sef') == st.session_state.user]
        for t in myt: st.write(f"- {t['ad']}")
        
elif st.session_state.page == "detail" and st.session_state.secilen:
    t = st.session_state.secilen
    st.image(get_image(t.get('img'), t.get('kat')), use_container_width=True)
    c1, c2 = st.columns([5,1])
    c1.markdown(f"<h2>{t['ad']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<span class='etiket'>⏱️ {t.get('sure','30 dk')}</span> <span class='etiket'>📊 {t.get('zorluk','Orta')}</span>", unsafe_allow_html=True)
    
    if st.session_state.login:
        favs = db_yukle(FAV_DB)
        is_fav = t['ad'] in favs.get(st.session_state.user, [])
        if c2.button("❤️" if is_fav else "🤍"):
            if st.session_state.user not in favs: favs[st.session_state.user] = []
            if is_fav: favs[st.session_state.user].remove(t['ad'])
            else: favs[st.session_state.user].append(t['ad'])
            db_kaydet(FAV_DB, favs); st.rerun()

    c1, c2 = st.columns([1,2])
    with c1:
        st.info("**Malzemeler:**\n\n"+"\n".join([f"- {m}" for m in t['malz']]))
        ana = t['malz'][0].split(" ")[-1] if t['malz'] else "Yemek"
        st.markdown(f'<a href="https://www.migros.com.tr/arama?q={ana}" target="_blank" class="btn-migros">🛒 Migros</a>', unsafe_allow_html=True)
    with c2:
        st.success(f"**Tarif:**\n\n{t['tar']}")
        st.subheader("Yorumlar")
        if st.session_state.login:
            with st.form("y"):
                ym = st.text_area("Yorum")
                if st.form_submit_button("Yolla"):
                    d = db_yukle(YORUM_DB); 
                    if t['ad'] not in d: d[t['ad']] = []
                    d[t['ad']].insert(0, {"isim": st.session_state.user, "msg": ym}); db_kaydet(YORUM_DB, d); st.rerun()
        for y in db_yukle(YORUM_DB).get(t['ad'], []):
            st.markdown(f"<div class='yorum-kutu'><b>{y['isim']}</b>: {y['msg']}</div>", unsafe_allow_html=True)
            
else:
    t1, t2 = st.tabs(["🔍 Ara", "➕ Ekle"])
    with t1:
        ara = st.text_input("Ara...", placeholder="Patates, Tavuk...")
        res = tarifleri_bul(ara, kat)
        if res:
            st.write(f"🎉 **{len(res)}** Tarif")
            cols = st.columns(3)
            for i, t in enumerate(res):
                with cols[i%3]:
                    st.image(get_image(t.get('img'), t.get('kat')), use_container_width=True)
                    st.markdown(f"**{t['ad']}**")
                    st.markdown(f"<span style='font-size:0.8rem; color:#aaa'>⏱️ {t.get('sure','30 dk')}</span>", unsafe_allow_html=True)
                    if st.button("Git", key=f"b_{i}"): st.session_state.secilen=t; st.session_state.page="detail"; st.rerun()
        else: st.warning("Yok.")
    with t2:
        if st.session_state.login:
            with st.form("add"):
                ta=st.text_input("Ad"); ti=st.text_input("Resim URL (Varsa yapıştır)"); tm=st.text_area("Malzeme"); tt=st.text_area("Tarif"); tk=st.selectbox("Kat", ["Kahvaltı", "Ana Yemek", "Tatlı", "Kullanıcı"])
                if st.form_submit_button("Ekle"):
                    u = db_yukle(USER_DB)
                    u.append({"ad": ta, "img": ti, "malz": tm.split("\n"), "tar": tt, "kat": tk, "sef": st.session_state.user, "sure": "45 dk", "zorluk": "Orta"})
                    db_kaydet(USER_DB, u); st.success("Oldu"); st.rerun()
        else: st.warning("Giriş yap.")

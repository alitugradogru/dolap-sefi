import streamlit as st
import time
import json
import os
from datetime import datetime
import random

# --- 1. AYARLAR ---
st.set_page_config(page_title="Dolap Şefi: Gold Edition", page_icon="👨‍🍳", layout="centered", initial_sidebar_state="expanded")

# --- 2. DOSYA YÖNETİMİ ---
TARIF_DOSYASI = "kullanici_tarifleri.json"
YORUM_DOSYASI = "yorumlar.json"
KULLANICI_DOSYASI = "kullanicilar.json"
FAVORI_DOSYASI = "favoriler.json"

# --- 3. FONKSİYONLAR ---
def liste_yukle(dosya):
    if os.path.exists(dosya):
        with open(dosya, "r", encoding="utf-8") as f:
            try: return json.load(f) if isinstance(json.load(f), list) else []
            except: return []
    return []

def sozluk_yukle(dosya):
    if os.path.exists(dosya):
        with open(dosya, "r", encoding="utf-8") as f:
            try: return json.load(f) if isinstance(json.load(f), dict) else {}
            except: return {}
    return {}

def veri_kaydet(dosya, veri):
    with open(dosya, "w", encoding="utf-8") as f: json.dump(veri, f, ensure_ascii=False, indent=4)

def get_image(url, kat):
    if url and "http" in url: return url
    defaults = {
        "Kahvaltı": "https://images.unsplash.com/photo-1533089862017-5c32417a1a08?w=600",
        "Ana Yemek": "https://images.unsplash.com/photo-1547592180-85f173990554?w=600",
        "Tatlı": "https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=600",
        "Çorba": "https://images.unsplash.com/photo-1547592166-23acbe3b624b?w=600",
        "Makarna": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=600"
    }
    return defaults.get(kat, "https://images.unsplash.com/photo-1495195134817-aeb325a55b65?w=600")

# --- 4. CSS TASARIM ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
.stApp { background-color: #0e1117; background-image: radial-gradient(circle at 50% 0%, #4a0000 0%, #0e1117 80%); color: #fff; font-family: 'Inter', sans-serif; }
.haber-kart { background: rgba(255,255,255,0.05); backdrop-filter: blur(10px); border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px; overflow: hidden; transition: 0.3s; }
.haber-kart:hover { transform: translateY(-5px); border-color: #ffcc00; }
.kart-resim { width: 100%; height: 200px; object-fit: cover; }
.kart-icerik { padding: 15px; }
.btn-migros { display: block; width: 100%; background: #ff7900; color: white !important; text-align: center; padding: 15px; border-radius: 12px; font-weight: bold; text-decoration: none; margin-top: 10px; }
.yorum-kutu { background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #ffcc00; }
h1 { background: -webkit-linear-gradient(45deg, #FFCC00, #FF6B6B); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 4px 15px rgba(255, 69, 0, 0.4); }
</style>
""", unsafe_allow_html=True)

# --- 5. EFSANE VE DETAYLI TARİFLER (50+ SEÇKİN TARİF) ---
SABIT_TARIFLER = [
    # --- KAHVALTI ---
    {"ad": "Trabzon Kuymak", "kat": "Kahvaltı", "img": "", "malz": ["2 YK Tereyağı", "2 YK Mısır Unu", "1 Kase Çeçil Peyniri", "1 Bardak Su"], "desc": "Karadeniz efsanesi.", 
     "tar": "1. Tereyağını bakır tavada yakmadan eritin.\n2. Mısır ununu ekleyip kokusu çıkana ve rengi dönene kadar kavurun.\n3. Suyu yavaşça ekleyip boza kıvamına gelene kadar karıştırın.\n4. Peyniri ekleyin ve hiç karıştırmadan peynirin eriyip yağın üste çıkmasını bekleyin."},
    {"ad": "Efsane Menemen", "kat": "Kahvaltı", "img": "", "malz": ["3 Yumurta", "3 Biber", "2 Domates", "Tuz-Karabiber"], "desc": "Pazar sabahı klasiği.", 
     "tar": "1. Biberleri ince doğrayıp yağda öldürün.\n2. Soyulmuş küp domatesleri ekleyip suyunu salıp çekene kadar pişirin.\n3. Yumurtaları kırın ama çok karıştırmayın, beyazı ve sarısı tane tane kalsın."},
    {"ad": "Puf Pankek", "kat": "Kahvaltı", "img": "", "malz": ["1.5 Bardak Un", "1 Bardak Süt", "1 Yumurta", "Kabartma Tozu", "Şeker"], "desc": "Bulut gibi yumuşak.", 
     "tar": "1. Yumurta ve şekeri köpürene kadar çırpın.\n2. Süt, un ve kabartma tozunu ekleyip pürüzsüz olana kadar çırpın.\n3. Yağsız teflon tavaya kepçeyle dökün. Göz göz olunca çevirin."},
    {"ad": "Çılbır", "kat": "Kahvaltı", "img": "", "malz": ["2 Yumurta", "1 Kase Yoğurt", "Sarımsak", "Tereyağı", "Pulbiber"], "desc": "Saray kahvaltısı.", 
     "tar": "1. Kaynayan suya sirke ve tuz atın. Yumurtayı dağıtmadan içine kırıp 3-4 dk poşeleyin.\n2. Tabağa sarımsaklı yoğurdu yayın, üzerine yumurtayı alın.\n3. Tavada yaktığınız biberli tereyağını üzerine gezdirin."},
    {"ad": "Sucuklu Yumurta", "kat": "Kahvaltı", "img": "", "malz": ["Yarım Kangal Sucuk", "3 Yumurta", "Tereyağı"], "desc": "Klasik lezzet.", 
     "tar": "1. Sucukları dilimleyip kendi yağını salana kadar pişirin (Kurutmayın).\n2. Göz göz yumurtaları üzerine kırın.\n3. Sarısını patlatmadan beyazı pişince ocaktan alın."},
    {"ad": "Pişi", "kat": "Kahvaltı", "img": "", "malz": ["Un", "Maya", "Tuz", "Su", "Kızartma Yağı"], "desc": "Mayalı hamur kızartması.", 
     "tar": "1. Un, su ve mayadan yumuşak bir hamur yoğurup 40dk mayalandırın.\n2. Elinizi yağlayıp parçalar koparın ve açın.\n3. Kızgın yağda arkalı önlü kızartın."},
    {"ad": "Simit Pizza", "kat": "Kahvaltı", "img": "", "malz": ["1 Simit", "Kaşar", "Sucuk", "Domates"], "desc": "Bayat simitleri değerlendir.", 
     "tar": "1. Simidi enlemesine ikiye bölün.\n2. Üzerine dilimlenmiş kaşar, sucuk ve domates koyun.\n3. Fırında kaşarlar eriyene kadar pişirin."},
    {"ad": "Avokado Toast", "kat": "Kahvaltı", "img": "", "malz": ["1 Avokado", "2 Dilim Ekşi Mayalı Ekmek", "Limon", "Haşlanmış Yumurta"], "desc": "Modern ve sağlıklı.", 
     "tar": "1. Avokadoyu ezip limon, tuz ve karabiberle tatlandırın.\n2. Kızarmış ekmeğe sürün.\n3. Üzerine dilimlenmiş rafadan yumurtayı koyun."},

    # --- ANA YEMEK ---
    {"ad": "Karnıyarık", "kat": "Ana Yemek", "img": "", "malz": ["6 Patlıcan", "250gr Kıyma", "Soğan", "Domates", "Biber"], "desc": "Patlıcanın en güzel hali.", 
     "tar": "1. Patlıcanları alaca soyup tuzlu suda bekletin, kurulayıp kızartın.\n2. Kıymayı soğan, biber ve domatesle kavurup iç harcı hazırlayın.\n3. Patlıcanların ortasını açıp harcı doldurun. Salçalı su döküp 200 derecede 20dk fırınlayın."},
    {"ad": "Kuru Fasulye", "kat": "Ana Yemek", "img": "", "malz": ["2 Bardak Fasulye", "250gr Et", "Soğan", "Salça"], "desc": "Suyuna pilav şart.", 
     "tar": "1. Fasulyeyi geceden ıslatın. Eti düdüklüde mühürleyin.\n2. Soğan ve salçayı kavurun. Fasulyeyi ekleyin.\n3. Üzerini geçecek kadar suyla düdüklüde 30dk pişirin."},
    {"ad": "İzmir Köfte", "kat": "Ana Yemek", "img": "", "malz": ["500gr Kıyma", "3 Patates", "3 Biber", "Domates Sos"], "desc": "Fırında soslu ziyafet.", 
     "tar": "1. Köfteleri yoğurun, patatesleri elma dilim kesin.\n2. Hepsini az yağda hafifçe kızartın.\n3. Tepsiye dizip üzerine bol domates sos dökün, fırında özleşene kadar pişirin."},
    {"ad": "Hünkar Beğendi", "kat": "Ana Yemek", "img": "", "malz": ["500gr Kuşbaşı Et", "3 Bostan Patlıcan", "Un", "Süt", "Kaşar"], "desc": "Saray mutfağından.", 
     "tar": "1. Eti soğanla yumuşayana kadar pişirin.\n2. Patlıcanı közleyip ezin. Un ve yağı kavurun, patlıcanı ve sütü ekleyip beşamel yapın. Kaşarı ekleyin.\n3. Beğendinin üzerine eti koyup servis yapın."},
    {"ad": "Tavuk Sote", "kat": "Ana Yemek", "img": "", "malz": ["Tavuk Göğsü", "Yeşil Biber", "Kapya Biber", "Domates"], "desc": "Pratik akşam yemeği.", 
     "tar": "1. Tavuğu yüksek ateşte soteleyin.\n2. Soğan ve biberleri ekleyip kavurun.\n3. Domates ve baharatları ekleyip kısık ateşte pişirin."},
    {"ad": "Fırında Tavuk Patates", "kat": "Ana Yemek", "img": "", "malz": ["Tavuk But", "4 Patates", "Salça", "Kekik", "Sarımsak"], "desc": "Kurtarıcı yemek.", 
     "tar": "1. Salça, yağ, kekik, sarımsak ve suyu karıştırıp sos yapın.\n2. Tavuk ve patatesleri bu sosla harmanlayıp tepsiye dizin.\n3. 200 derecede üzeri kızarana kadar pişirin."},
    {"ad": "Mantı", "kat": "Ana Yemek", "img": "", "malz": ["Un", "Kıyma", "Soğan", "Yoğurt", "Salça"], "desc": "Kayseri usulü.", 
     "tar": "1. Hamuru yoğurup açın, küçük kareler kesin.\n2. Kıymalı harcı koyup kapatın.\n3. Tuzlu suda haşlayıp sarımsaklı yoğurt ve salçalı yağ ile servis yapın."},
    {"ad": "Orman Kebabı", "kat": "Ana Yemek", "img": "", "malz": ["Kuşbaşı Et", "Bezelye", "Havuç", "Patates"], "desc": "Bol sebzeli.", 
     "tar": "1. Eti pişirin. Küp doğranmış havuç ve patatesi kızartın.\n2. Hepsini bezelye ve salçalı suyla birleştirip 15dk tencerede pişirin."},

    # --- ÇORBALAR ---
    {"ad": "Süzme Mercimek", "kat": "Çorba", "img": "", "malz": ["1 Bardak Mercimek", "1 Patates", "1 Havuç", "Soğan"], "desc": "Lokanta usulü.", 
     "tar": "1. Sebzeleri iri doğrayıp mercimekle beraber haşlayın.\n2. Blenderdan geçirip pürüzsüz yapın.\n3. Üzerine tereyağlı nane yakın."},
    {"ad": "Yayla Çorbası", "kat": "Çorba", "img": "", "malz": ["1 Kase Yoğurt", "1 Yumurta", "Pirinç", "Nane"], "desc": "Naneli ferahlık.", 
     "tar": "1. Pirinci haşlayın. Yoğurt ve yumurtayı çırpın.\n2. Çorba suyundan alıp terbiyeyi ılıştırın ve tencereye dökün (Kesilmesin diye).\n3. Kaynayınca tuzunu atın ve naneli yağ gezdirin."},
    {"ad": "Domates Çorbası", "kat": "Çorba", "img": "", "malz": ["4 Domates", "1 Kaşık Un", "1 Bardak Süt", "Kaşar"], "desc": "Kaşarlı.", 
     "tar": "1. Unu kokusu çıkana kadar kavurun.\n2. Rende domatesi ekleyip pişirin. Suyu ekleyip kaynatın.\n3. Sütü ekleyip bir taşım kaynatın, kaşarla servis yapın."},
    {"ad": "Tarhana Çorbası", "kat": "Çorba", "img": "", "malz": ["3 Kaşık Tarhana", "1 Kaşık Salça", "Sarımsak", "Nane"], "desc": "Şifa kaynağı.", 
     "tar": "1. Tarhanayı soğuk suda ezin.\n2. Salçayı kavurun, tarhanalı suyu ve sıcak suyu ekleyin.\n3. Sürekli karıştırarak koyulaşana kadar pişirin."},
    {"ad": "Tavuk Suyu Çorba", "kat": "Çorba", "img": "", "malz": ["Tavuk But", "Tel Şehriye", "Limon", "Maydanoz"], "desc": "Hasta çorbası.", 
     "tar": "1. Tavuğu haşlayıp didikleyin.\n2. Tavuk suyuna şehriyeleri atıp pişirin.\n3. Tavukları ekleyip bol limon ve karabiberle servis yapın."},

    # --- MAKARNA & PİLAV ---
    {"ad": "Kremalı Mantarlı Makarna", "kat": "Makarna", "img": "", "malz": ["Penne Makarna", "400gr Mantar", "1 Kutu Krema", "Fesleğen"], "desc": "Restoran lezzeti.", 
     "tar": "1. Mantarları yüksek ateşte soteleyin.\n2. Kremayı ekleyip kaynatın. Haşlanmış makarnayı sosa atın.\n3. Fesleğen ve parmesanla servis yapın."},
    {"ad": "Spagetti Bolonez", "kat": "Makarna", "img": "", "malz": ["Spagetti", "200gr Kıyma", "Domates Sos", "Havuç"], "desc": "İtalyan klasiği.", 
     "tar": "1. Kıymayı, rendelenmiş havuç ve soğanı kavurun.\n2. Domates sosunu ekleyip kısık ateşte pişirin.\n3. Haşlanmış spagettinin üzerine dökün."},
    {"ad": "Şehriyeli Pirinç Pilavı", "kat": "Ana Yemek", "img": "", "malz": ["2 Bardak Baldo Pirinç", "3 Bardak Sıcak Su", "Tereyağı"], "desc": "Tane tane.", 
     "tar": "1. Pirinci sıcak suda bekletip yıkayın.\n2. Şehriyeyi kavurun, pirinci ekleyip şeffaflaşana kadar kavurun.\n3. Sıcak su ve tuzu ekleyip suyunu çekene kadar demleyin."},
    {"ad": "Meyhane Pilavı", "kat": "Ana Yemek", "img": "", "malz": ["Bulgur", "Domates", "Biber", "Salça"], "desc": "Yanına cacıkla.", 
     "tar": "1. Soğan ve biberi kavurun. Salça ve domatesi ekleyin.\n2. Bulguru ekleyip kavurun, suyunu verip pişirin."},

    # --- SEBZELİ ---
    {"ad": "Zeytinyağlı Fasulye", "kat": "Sebzeli", "img": "", "malz": ["500gr Taze Fasulye", "Domates", "Soğan", "Şeker"], "desc": "Yaz yemeği.", 
     "tar": "1. Soğanı ve fasulyeyi zeytinyağında sararana kadar kavurun.\n2. Domates, tuz ve şekeri ekleyin.\n3. Hiç su koymadan (veya çok az) kısık ateşte pişirin."},
    {"ad": "Mücver", "kat": "Sebzeli", "img": "", "malz": ["3 Kabak", "2 Yumurta", "Dereotu", "Un", "Peynir"], "desc": "Kızartma sevenlere.", 
     "tar": "1. Kabakları rendeleyip suyunu iyice sıkın (Yoksa hamur olur).\n2. Malzemeleri karıştırıp kaşıkla kızgın yağa dökün.\n3. Arkalı önlü kızartıp sarımsaklı yoğurtla yiyin."},
    {"ad": "İmam Bayıldı", "kat": "Sebzeli", "img": "", "malz": ["Patlıcan", "Bol Soğan", "Sarımsak", "Domates"], "desc": "Soğuk meze.", 
     "tar": "1. Patlıcanı bütün kızartın.\n2. Bol soğanı karamelize edin, içine doldurun.\n3. Zeytinyağlı sosla tencerede pişirin."},
    
    # --- DÜNYA MUTFAĞI ---
    {"ad": "Ev Yapımı Burger", "kat": "Dünya Mutfağı", "img": "", "malz": ["Dana Döş Kıyma", "Burger Ekmeği", "Cheddar", "Karamelize Soğan"], "desc": "Sulu sulu.", 
     "tar": "1. Kıymayı sadece tuz ve karabiberle yoğurup şekil verin.\n2. Döküm tavada yüksek ateşte pişirin. Üzerine peyniri koyup eritin.\n3. Ekmeği kızartıp soslayın ve birleştirin."},
    {"ad": "Taco", "kat": "Dünya Mutfağı", "img": "", "malz": ["Tortilla", "Kıyma", "Mısır", "Meksika Fasulyesi"], "desc": "Meksika ateşi.", 
     "tar": "1. Kıymayı taco baharatıyla kavurun.\n2. Küçük tortilla ekmeklerini ısıtın.\n3. İçini doldurup salsa sos ve limonla servis yapın."},
    {"ad": "Pizza", "kat": "Dünya Mutfağı", "img": "", "malz": ["Un", "Maya", "Mozzarella", "Sucuk/Mantar"], "desc": "İnce hamur.", 
     "tar": "1. Hamuru yoğurup mayalandırın. İncecik açın.\n2. Domates sosunu sürün, peyniri ve malzemeleri dizin.\n3. En yüksek derecede fırının tabanında pişirin."},

    # --- TATLI ---
    {"ad": "Fırın Sütlaç", "kat": "Tatlı", "img": "", "malz": ["1 Litre Süt", "1 Bardak Şeker", "Pirinç", "Nişasta"], "desc": "Kızarmış.", 
     "tar": "1. Pirinci haşlayın, süt ve şekeri ekleyin.\n2. Nişastayla bağlayın. Güveçlere koyun.\n3. Fırın tepsisine su koyup sadece üst ızgarada kızartın."},
    {"ad": "Magnolia", "kat": "Tatlı", "img": "", "malz": ["1 Litre Süt", "Krema", "Bebek Bisküvisi", "Çilek"], "desc": "Kupta mutluluk.", 
     "tar": "1. Muhallebiyi pişirip soğutun. İçine kremayı ekleyip çırpın.\n2. Bisküviyi toz yapın.\n3. Kuplara bisküvi, çilek ve muhallebi sırasıyla dizin."},
    {"ad": "Islak Kek (Brownie)", "kat": "Tatlı", "img": "", "malz": ["3 Yumurta", "Süt", "Kakao", "Un"], "desc": "Bol soslu.", 
     "tar": "1. Keki çırpıp pişirin.\n2. Süt, şeker, kakao ve yağı kaynatıp sos yapın.\n3. Fırından çıkan sıcak keke sosu dökün."},
    {"ad": "İrmik Helvası", "kat": "Tatlı", "img": "", "malz": ["İrmik", "Tereyağı", "Süt", "Fıstık"], "desc": "Dondurmalı.", 
     "tar": "1. İrmiği ve fıstığı tereyağında rengi dönene kadar (yaklaşık 20dk) sabırla kavurun.\n2. Sıcak şerbeti döküp kapağını kapatın, demlensin."}
]

# --- 6. AKILLI ARAMA ---
def tarifleri_bul(girdi, kategori):
    girdi = girdi.lower()
    arananlar = [x.strip() for x in girdi.replace(",", " ").split() if x.strip()]
    tum_liste = SABIT_TARIFLER + liste_yukle(TARIF_DOSYASI)
    
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

def go_home(): st.session_state.page = "home"; st.session_state.secilen = None
def go_detail(tarif): st.session_state.secilen = tarif; st.session_state.page = "detail"
def go_profile(): st.session_state.page = "profile"

with st.sidebar:
    if st.button("🏠 ANA SAYFA", use_container_width=True): go_home(); st.rerun()
    try: st.image("logo.png", use_container_width=True)
    except: pass
    if st.session_state.login:
        st.success(f"Şef {st.session_state.user}")
        if st.button("👤 Profilim", use_container_width=True): go_profile(); st.rerun()
        if st.button("Çıkış", use_container_width=True): st.session_state.login=False; st.session_state.user=None; go_home(); st.rerun()
    else:
        t1, t2 = st.tabs(["Giriş", "Kayıt"])
        with t1:
            k = st.text_input("Kullanıcı"); p = st.text_input("Şifre", type="password")
            if st.button("Giriş"):
                res = giris_kontrol(k, p)
                if res: st.session_state.login=True; st.session_state.user=k if res=="user" else "admin"; st.rerun()
                else: st.error("Hatalı!")
        with t2:
            yk = st.text_input("Yeni Ad"); yp = st.text_input("Yeni Şifre", type="password")
            if st.button("Kayıt Ol"):
                if kullanici_kaydet(yk, yp): st.success("Oldu!"); else: st.error("Dolu.")
    st.markdown("---")
    kat = st.radio("Filtrele:", ["Tümü", "Kahvaltı", "Ana Yemek", "Çorba", "Makarna", "Sebzeli", "Tatlı", "Dünya Mutfağı", "Kullanıcı"])

st.markdown('<a href="#" class="home-link" target="_self"><h1>🔥 Dolap Şefi: Gold Edition</h1></a>', unsafe_allow_html=True)

if st.session_state.page == "profile":
    st.header(f"👤 {st.session_state.user}")
    t1, t2 = st.tabs(["❤️ Favoriler", "📝 Tariflerim"])
    with t1:
        favs = sozluk_yukle(FAVORI_DOSYASI).get(st.session_state.user, [])
        objs = [t for t in SABIT_TARIFLER+liste_yukle(TARIF_DOSYASI) if t['ad'] in favs]
        if objs:
            for t in objs:
                with st.container():
                    c1, c2 = st.columns([1,4])
                    c1.image(get_image(t.get('img'), t.get('kat')))
                    c2.subheader(t['ad']); 
                    if c2.button("Git", key=f"fv_{t['ad']}"): go_detail(t); st.rerun()
                st.divider()
        else: st.info("Boş.")
    with t2:
        my = [t for t in liste_yukle(TARIF_DOSYASI) if t.get('sef') == st.session_state.user]
        if my: 
            for t in my: st.write(f"- {t['ad']}")
        else: st.info("Yok.")
    if st.button("Geri"): go_home(); st.rerun()

elif st.session_state.page == "detail" and st.session_state.secilen:
    t = st.session_state.secilen
    st.image(get_image(t.get('img'), t.get('kat')), use_container_width=True)
    c1, c2 = st.columns([5,1])
    c1.markdown(f"<h2>{t['ad']}</h2>", unsafe_allow_html=True)
    if st.session_state.login:
        if c2.button("❤️" if favori_kontrol(st.session_state.user, t['ad']) else "🤍"):
            st.toast(favori_ekle_cikar(st.session_state.user, t['ad'])); time.sleep(0.5); st.rerun()
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
                if st.form_submit_button("Yolla"): yorum_ekle(t['ad'], st.session_state.user, ym); st.rerun()
        for y in sozluk_yukle(YORUM_DOSYASI).get(t['ad'], []):
            st.markdown(f"<div class='yorum-kutu'><b>{y['isim']}</b>: {y['msg']}</div>", unsafe_allow_html=True)
    if st.button("Geri"): go_home(); st.rerun()

else:
    t1, t2 = st.tabs(["🔍 Ara", "➕ Ekle"])
    with t1:
        ara = st.text_input("Ara...", placeholder="Patates, Tavuk...")
        res = tarifleri_bul(ara, kat)
        if res:
            st.write(f"**{len(res)}** Tarif")
            cols = st.columns(3)
            for i, t in enumerate(res):
                with cols[i%3]:
                    st.image(get_image(t.get('img'), t.get('kat')), use_container_width=True)
                    st.markdown(f"**{t['ad']}**")
                    if st.button("Git", key=f"b_{i}"): go_detail(t); st.rerun()
        else: st.warning("Yok.")
    with t2:
        if st.session_state.login:
            with st.form("add"):
                ta = st.text_input("Ad"); ti = st.text_input("Resim URL"); tm = st.text_area("Malzeme"); tt = st.text_area("Tarif"); tk = st.selectbox("Kat", ["Kullanıcı", "Kahvaltı", "Ana Yemek", "Tatlı"])
                if st.form_submit_button("Ekle"): 
                    tarif_ekle({"ad": ta, "img": ti, "malz": tm.split("\n"), "tar": tt, "kat": tk, "sef": st.session_state.user, "desc": "Kullanıcı"}); st.success("Tamam"); st.rerun()
        else: st.warning("Giriş yap.")
        if st.session_state.user == "admin":
            st.write("Admin:"); 
            for i, k in enumerate(liste_yukle(TARIF_DOSYASI)):
                c1, c2 = st.columns([4,1]); c1.write(k['ad']); 
                if c2.button("Sil", key=f"d_{i}"): tarif_sil(i); st.rerun()

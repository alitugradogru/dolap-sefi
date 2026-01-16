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

# --- 2. DOSYA YÖNETİMİ & VERİTABANI ---
TARIF_DOSYASI = "kullanici_tarifleri.json"
YORUM_DOSYASI = "yorumlar.json"
KULLANICI_DOSYASI = "kullanicilar.json"

# --- Kullanıcı İşlemleri ---
def kullanicilari_yukle():
    if os.path.exists(KULLANICI_DOSYASI):
        with open(KULLANICI_DOSYASI, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return {}
    return {}

def kullanici_kaydet(kullanici_adi, sifre):
    users = kullanicilari_yukle()
    if kullanici_adi in users:
        return False # Kullanıcı zaten var
    users[kullanici_adi] = sifre
    with open(KULLANICI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)
    return True

def giris_yap(kullanici_adi, sifre):
    # Önce Admin Kontrolü
    if kullanici_adi == "admin" and sifre == "2026":
        return "admin"
    # Sonra Normal Kullanıcı
    users = kullanicilari_yukle()
    if users.get(kullanici_adi) == sifre:
        return "user"
    return False

# --- Tarif İşlemleri ---
def tarifleri_yukle():
    if os.path.exists(TARIF_DOSYASI):
        with open(TARIF_DOSYASI, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                for d in data: 
                    if 'likes' not in d: d['likes'] = 0
                return data
            except: return []
    return []

def tarifi_kaydet(yeni_tarif):
    mevcut = tarifleri_yukle()
    mevcut.append(yeni_tarif)
    with open(TARIF_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(mevcut, f, ensure_ascii=False, indent=4)

def tarifi_sil(index):
    """Sadece Admin kullanabilir"""
    mevcut = tarifleri_yukle()
    if 0 <= index < len(mevcut):
        del mevcut[index]
        with open(TARIF_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(mevcut, f, ensure_ascii=False, indent=4)
        return True
    return False

def begeni_arttir(index):
    tarifler = tarifleri_yukle()
    if 0 <= index < len(tarifler):
        tarifler[index]['likes'] = tarifler[index].get('likes', 0) + 1
        with open(TARIF_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(tarifler, f, ensure_ascii=False, indent=4)

# --- Yorum İşlemleri ---
def yorumlari_yukle():
    if os.path.exists(YORUM_DOSYASI):
        with open(YORUM_DOSYASI, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return {}
    return {}

def yorum_ekle(yemek_adi, isim, yorum):
    data = yorumlari_yukle()
    if yemek_adi not in data: data[yemek_adi] = []
    data[yemek_adi].insert(0, {"isim": isim, "yorum": yorum, "tarih": datetime.now().strftime("%d-%m %H:%M")})
    with open(YORUM_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 3. SESSION STATE (OTURUM) ---
if "login_status" not in st.session_state: st.session_state.login_status = False # False, 'user', 'admin'
if "username" not in st.session_state: st.session_state.username = None
if "sonuclar" not in st.session_state: st.session_state.sonuclar = [] 
if "secilen_tarif" not in st.session_state: st.session_state.secilen_tarif = None 

# --- 4. CSS TASARIM ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
.stApp { background-color: #0e1117; background-image: radial-gradient(circle at 50% 0%, #4a0404 0%, #0e1117 60%); font-family: 'Inter', sans-serif; color: #fff; }
h1 { font-weight: 800; background: -webkit-linear-gradient(45deg, #FFCC00, #FF6B6B); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
.haber-kart { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); padding: 20px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 20px; transition: all 0.3s; }
.haber-kart:hover { transform: translateY(-3px); border-color: rgba(255, 204, 0, 0.3); }
.btn-migros { display: block; width: 100%; background: linear-gradient(135deg, #FF7900, #F7941D); color: white !important; text-align: center; padding: 12px; border-radius: 10px; font-weight: 700; text-decoration: none; margin-top: 15px; }
.yorum-kutu { background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #FFCC00; font-size: 0.9rem;}
.admin-badge { background-color: #e74c3c; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 5. DEV TARİF HAVUZU (YENİLER EKLENDİ) ---
# Kodun çok uzamaması için kısa tutarak maksimum çeşitliliği ekliyorum.
SABIT_TARIFLER = [
    # --- KAHVALTILIKLAR (20 Adet Hedefli) ---
    {"ad": "Efsane Menemen", "kat": "Kahvaltı", "malz": ["Yumurta", "Domates", "Biber", "Yağ"], "desc": "Kahvaltının kralı.", "tar": "Biberleri kavur, domatesi ekle, yumurtayı kır."},
    {"ad": "Kuymak", "kat": "Kahvaltı", "malz": ["Mısır Unu", "Tereyağı", "Çeçil Peyniri"], "desc": "Karadeniz efsanesi.", "tar": "Yağda unu kavur, suyu ekle, peyniri erit."},
    {"ad": "Çılbır", "kat": "Kahvaltı", "malz": ["Yumurta", "Yoğurt", "Sarımsak", "Tereyağı", "Pulbiber"], "desc": "Saray kahvaltısı.", "tar": "Kaynayan sirkeli suya yumurtayı kır poşe et. Sarımsaklı yoğurt ve biberli yağ ile servis yap."},
    {"ad": "Pankek", "kat": "Kahvaltı", "malz": ["Un", "Süt", "Yumurta", "Kabartma Tozu"], "desc": "Puf puf.", "tar": "Çırp, tavada arkalı önlü pişir."},
    {"ad": "Yumurtalı Ekmek", "kat": "Kahvaltı", "malz": ["Bayat Ekmek", "Yumurta", "Süt", "Sıvı Yağ"], "desc": "Ekmekleri değerlendir.", "tar": "Ekmekleri yumurtalı süte batır, kızgın yağda kızart."},
    {"ad": "Sucuklu Yumurta", "kat": "Kahvaltı", "malz": ["Sucuk", "Yumurta", "Tereyağı"], "desc": "Pazar klasiği.", "tar": "Sucukları kurutmadan pişir, yumurtayı ekle."},
    {"ad": "Pişi", "kat": "Kahvaltı", "malz": ["Un", "Su", "Maya", "Tuz"], "desc": "Hamur kızartması.", "tar": "Mayalı hamur yap, kızgın yağda pişir."},
    {"ad": "Patatesli Omlet", "kat": "Kahvaltı", "malz": ["Patates", "Yumurta", "Kaşar"], "desc": "Doyurucu.", "tar": "Küp patatesleri kızart, üzerine yumurtayı dök."},
    {"ad": "Simit Pizza", "kat": "Kahvaltı", "malz": ["Simit", "Kaşar", "Sucuk", "Domates"], "desc": "Pratik lezzet.", "tar": "Simidi ortadan kes, malzemeleri koy, fırınla."},
    {"ad": "Avokado Toast", "kat": "Kahvaltı", "malz": ["Avokado", "Ekmek", "Limon", "Yumurta"], "desc": "Modern kahvaltı.", "tar": "Avokadoyu ez sür, üzerine haşlanmış yumurta koy."},
    
    # --- ATIŞTIRMALIKLAR (20 Adet Hedefli) ---
    {"ad": "Mücver", "kat": "Atıştırmalık", "malz": ["Kabak", "Yumurta", "Un", "Dereotu"], "desc": "Çıtır sebze.", "tar": "Rendele, karıştır, kızart."},
    {"ad": "Soğan Halkası", "kat": "Atıştırmalık", "malz": ["Kuru Soğan", "Un", "Soda", "Galeta Unu"], "desc": "Ev yapımı çıtır.", "tar": "Halkaları sosa batır, galetaya bula, kızart."},
    {"ad": "Paçanga Böreği", "kat": "Atıştırmalık", "malz": ["Yufka", "Pastırma", "Kaşar", "Biber"], "desc": "Sıcak sıcak.", "tar": "Malzemeyi sar, kızart."},
    {"ad": "Patates Kroket", "kat": "Atıştırmalık", "malz": ["Patates", "Yumurta", "Un", "Galeta Unu"], "desc": "Püre topu.", "tar": "Püreyi şekillendir, panela, kızart."},
    {"ad": "Bruschetta", "kat": "Atıştırmalık", "malz": ["Ekmek", "Domates", "Fesleğen", "Sarımsak"], "desc": "İtalyan başlangıç.", "tar": "Ekmekleri kızart, domatesli karışımı üstüne koy."},
    {"ad": "Çıtır Tavuk", "kat": "Atıştırmalık", "malz": ["Tavuk Göğsü", "Mısır Gevreği", "Yumurta"], "desc": "Kova menü gibi.", "tar": "Tavuğu gevreğe bula fırınla."},
    {"ad": "Humus", "kat": "Atıştırmalık", "malz": ["Nohut", "Tahin", "Limon", "Kimyon"], "desc": "En iyi meze.", "tar": "Hepsini robottan geçir."},
    {"ad": "Sigara Böreği", "kat": "Atıştırmalık", "malz": ["Yufka", "Lor Peyniri"], "desc": "Klasik.", "tar": "Sar ve kızart."},
    
    # --- DÜNYA MUTFAĞI (20 Adet Hedefli) ---
    {"ad": "Ev Yapımı Pizza", "kat": "Dünya Mutfağı", "malz": ["Un", "Maya", "Mozzarella", "Sucuk/Mantar"], "desc": "İtalyan işi.", "tar": "Hamuru aç, sosu sür, malzemeyi diz fırınla."},
    {"ad": "Hamburger", "kat": "Dünya Mutfağı", "malz": ["Kıyma", "Hamburger Ekmeği", "Cheddar", "Turşu"], "desc": "Fast food evde.", "tar": "Köfteyi pişir, ekmek arası yap."},
    {"ad": "Taco", "kat": "Dünya Mutfağı", "malz": ["Lavaş/Tortilla", "Kıyma", "Mısır", "Meksika Fasulyesi"], "desc": "Meksika ateşi.", "tar": "Kıymalı harcı hazırla, lavaşa koy."},
    {"ad": "Sebzeli Noodle", "kat": "Dünya Mutfağı", "malz": ["Noodle/Spagetti", "Soya Sosu", "Havuç", "Lahana"], "desc": "Uzak doğu.", "tar": "Sebzeleri yüksek ateşte çevir, haşlanmış makarnayla karıştır."},
    {"ad": "Falafel", "kat": "Dünya Mutfağı", "malz": ["Nohut", "Maydanoz", "Soğan", "Sarımsak"], "desc": "Orta doğu köftesi.", "tar": "Malzemeleri robottan çek, top yap kızart."},
    {"ad": "Mac and Cheese", "kat": "Dünya Mutfağı", "malz": ["Makarna", "Cheddar", "Süt", "Un"], "desc": "Peynir şelalesi.", "tar": "Beşamel sos yap, peyniri erit, makarnayla karıştır."},
    {"ad": "Quesadilla", "kat": "Dünya Mutfağı", "malz": ["Tortilla", "Tavuk", "Kaşar", "Biber"], "desc": "Peynirli Meksika gözlemesi.", "tar": "Lavaşa malzemeyi koy, katla, tavada pişir."},
    {"ad": "Sushi (Ev Usulü)", "kat": "Dünya Mutfağı", "malz": ["Pirinç", "Nori Yosunu", "Salatalık", "Somon/Ton"], "desc": "Japon sanatı.", "tar": "Pirinci lapa yap, yosuna yay, sar."},

    # --- SEBZELİ (20 Adet Hedefli) ---
    {"ad": "İmam Bayıldı", "kat": "Sebzeli", "malz": ["Patlıcan", "Soğan", "Sarımsak", "Domates"], "desc": "Zeytinyağlı efsane.", "tar": "Patlıcanı kızart, soğanlı harcı içine doldur, pişir."},
    {"ad": "Şakşuka", "kat": "Sebzeli", "malz": ["Patlıcan", "Biber", "Kabak", "Domates Sos"], "desc": "Yaz mezesi.", "tar": "Sebzeleri küp kızart, domates sos dök."},
    {"ad": "Zeytinyağlı Enginar", "kat": "Sebzeli", "malz": ["Enginar", "Bezelye", "Havuç", "Portakal Suyu"], "desc": "Karaciğer dostu.", "tar": "Garnitürü enginarın üstüne koy, portakal suyuyla pişir."},
    {"ad": "Karnabahar Kızartması", "kat": "Sebzeli", "malz": ["Karnabahar", "Yumurta", "Un", "Yoğurt"], "desc": "Sarımsaklı yoğurtla.", "tar": "Haşla, panele, kızart."},
    {"ad": "Kabak Sıyırma", "kat": "Sebzeli", "malz": ["Girit Kabağı", "Zeytinyağı", "Limon", "Pirinç"], "desc": "Hafif Ege yemeği.", "tar": "Kabakları şerit doğra, az pirinçle kavur."},
    {"ad": "Fırın Sebze", "kat": "Sebzeli", "malz": ["Patates", "Kabak", "Havuç", "Biber", "Kekik"], "desc": "Diyet dostu.", "tar": "Hepsini doğra, yağla baharatla, fırına at."},
    {"ad": "Mercimek Köftesi", "kat": "Sebzeli", "malz": ["Mercimek", "Bulgur", "Salça", "Yeşillik"], "desc": "Etsiz köfte.", "tar": "Mercimeği haşla bulguru at şişsin, yoğur."},
    
    # --- KLASİKLER (Mevcutlar) ---
    {"ad": "Kuru Fasulye", "kat": "Ana Yemek", "malz": ["Fasulye", "Et", "Salça"], "desc": "Milli yemek.", "tar": "Islat, haşla, pişir."},
    {"ad": "Karnıyarık", "kat": "Ana Yemek", "malz": ["Patlıcan", "Kıyma"], "desc": "Patlıcan kebabı.", "tar": "Kızart doldur fırınla."},
    {"ad": "Sütlaç", "kat": "Tatlı", "malz": ["Süt", "Pirinç", "Şeker"], "desc": "Sütlü tatlı.", "tar": "Kaynat fırınla."},
]

# --- AKILLI ARAMA ---
def tarifleri_bul(girdi, kategori):
    girdi = girdi.lower()
    kelimeler = [x.strip() for x in girdi.replace(",", " ").split() if x.strip()]
    bulunanlar = []
    
    # Sabit + Kullanıcı Tariflerini Birleştir
    tum_liste = SABIT_TARIFLER + tarifleri_yukle()
    
    for t in tum_liste:
        # Kategori Filtresi
        if kategori != "Tümü" and t.get("kat") != kategori:
            continue
            
        text = (t["ad"] + " " + " ".join(t["malz"])).lower()
        
        if not kelimeler: # Arama yoksa hepsini göster
            bulunanlar.append(t)
        else: # Varsa ara (OR mantığı)
            for k in kelimeler:
                if k in text:
                    bulunanlar.append(t)
                    break
    return bulunanlar

# --- ARAYÜZ ---

# YAN MENÜ (LOGIN PANELİ)
with st.sidebar:
    try: st.image("logo.png", use_container_width=True)
    except: pass
    
    st.markdown("### 👤 Üyelik Paneli")
    
    if st.session_state.login_status:
        st.success(f"Hoşgeldin, {st.session_state.username}")
        if st.session_state.username == "admin":
            st.warning("🔧 YÖNETİCİ MODU")
        if st.button("Çıkış Yap"):
            st.session_state.login_status = False
            st.session_state.username = None
            st.rerun()
    else:
        tab_giris, tab_kayit = st.tabs(["Giriş", "Kayıt"])
        with tab_giris:
            g_ad = st.text_input("Kullanıcı Adı", key="g_ad")
            g_sifre = st.text_input("Şifre", type="password", key="g_sifre")
            if st.button("Giriş Yap"):
                sonuc = giris_yap(g_ad, g_sifre)
                if sonuc:
                    st.session_state.login_status = True
                    st.session_state.username = "admin" if sonuc == "admin" else g_ad
                    st.rerun()
                else:
                    st.error("Hatalı bilgi.")
        with tab_kayit:
            k_ad = st.text_input("Yeni Kullanıcı Adı", key="k_ad")
            k_sifre = st.text_input("Yeni Şifre", type="password", key="k_sifre")
            if st.button("Kayıt Ol"):
                if kullanici_kaydet(k_ad, k_sifre):
                    st.success("Kayıt başarılı! Giriş yapabilirsin.")
                else:
                    st.error("Bu isim alınmış.")

    st.markdown("---")
    kategori = st.radio("Menü:", ["Tümü", "Kahvaltı", "Atıştırmalık", "Ana Yemek", "Sebzeli", "Dünya Mutfağı", "Tatlı", "Kullanıcı"])

# ANA EKRAN
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try: st.image("logo.png", use_container_width=True)
    except: pass

st.title("Dolap Şefi")

tab1, tab2 = st.tabs(["🔍 Tarif Ara", "🌟 Vitrin & Paylaş"])

# --- TAB 1: ARAMA ---
with tab1:
    if st.session_state.secilen_tarif is None:
        malzemeler = st.text_input("Ne yemek istersin?", placeholder="Örn: Patates, Mantar, Pizza...")
        sonuclar = tarifleri_bul(malzemeler, kategori)
        
        if sonuclar:
            st.markdown(f"##### 🎉 {len(sonuclar)} Tarif")
            for i, t in enumerate(sonuclar):
                with st.container():
                    c1, c2 = st.columns([3, 1])
                    c1.markdown(f"**{t['ad']}** ({t.get('kat','Genel')})\n\n_{t['desc']}_")
                    if c2.button("İncele", key=f"btn_{i}"):
                        st.session_state.secilen_tarif = t
                        st.rerun()
                    st.markdown("---")
        else:
            st.info("Bu kriterde tarif bulunamadı.")
            
    else:
        # DETAY SAYFASI
        t = st.session_state.secilen_tarif
        if st.button("⬅️ Listeye Dön"):
            st.session_state.secilen_tarif = None
            st.rerun()
        
        st.header(t['ad'])
        st.info(f"💡 {t['desc']}")
        
        c1, c2 = st.columns(2)
        c1.markdown("#### 🛒 Malzemeler")
        for m in t['malz']: c1.markdown(f"- {m}")
        
        c2.markdown("#### 👨‍🍳 Yapılışı")
        c2.write(t['tar'])
        
        # MİGROS BUTONU
        ana_malz = t['malz'][0].split(" ")[-1] if t['malz'] else "Yemek"
        st.markdown(f'<a href="https://www.migros.com.tr/arama?q={ana_malz}" target="_blank" class="btn-migros">🍊 Migros\'tan Al</a>', unsafe_allow_html=True)
        
        # YORUMLAR
        st.markdown("---")
        st.subheader("Yorumlar")
        if st.session_state.login_status:
            with st.form("y_form"):
                y_mesaj = st.text_area("Yorum yaz...")
                if st.form_submit_button("Gönder"):
                    yorum_ekle(t['ad'], st.session_state.username, y_mesaj)
                    st.rerun()
        else:
            st.warning("Yorum yapmak için giriş yapmalısın.")
            
        for y in yorumlari_yukle().get(t['ad'], []):
            st.markdown(f"<div class='yorum-kutu'><b>{y['isim']}</b>: {y['yorum']} <small>({y['tarih']})</small></div>", unsafe_allow_html=True)

# --- TAB 2: VİTRİN & EKLEME ---
with tab2:
    st.subheader("Topluluk Tarifleri")
    
    # Sadece Kullanıcı Tariflerini Göster
    k_tarifler = tarifleri_yukle()
    
    if not k_tarifler:
        st.info("Henüz kullanıcı tarifi yok.")
    
    for idx, k in enumerate(k_tarifler):
        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.markdown(f"#### {k['ad']} \n *Şef: {k.get('sef', 'Anonim')}*")
            st.caption(k['desc'])
        with col_b:
            if st.button(f"❤️ {k.get('likes',0)}", key=f"lk_{idx}"):
                begeni_arttir(idx)
                st.rerun()
            
            # --- ADMİN SİLME BUTONU ---
            if st.session_state.username == "admin":
                if st.button("🗑️ SİL", key=f"del_{idx}"):
                    if tarifi_sil(idx):
                        st.success("Silindi!")
                        time.sleep(1)
                        st.rerun()
        st.markdown("---")

    # TARİF EKLEME
    if st.session_state.login_status:
        with st.expander("➕ Yeni Tarif Ekle"):
            with st.form("add_form"):
                t_ad = st.text_input("Yemek Adı")
                t_desc = st.text_input("Kısa Açıklama")
                t_malz = st.text_area("Malzemeler (Virgülle ayır)")
                t_tar = st.text_area("Yapılışı")
                if st.form_submit_button("Paylaş"):
                    yeni = {
                        "ad": t_ad, "kat": "Kullanıcı", 
                        "sef": st.session_state.username, 
                        "desc": t_desc, 
                        "malz": t_malz.split(","), 
                        "tar": t_tar, 
                        "likes": 0
                    }
                    tarifi_kaydet(yeni)
                    st.success("Tarif eklendi!")
                    time.sleep(1)
                    st.rerun()
    else:
        st.info("Tarif eklemek için lütfen giriş yapın.")

st.markdown("<div style='text-align:center; margin-top:50px; color:#666;'>© 2026 Dolap Şefi</div>", unsafe_allow_html=True)

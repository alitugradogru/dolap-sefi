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

# --- 2. DOSYA YÖNETİMİ ---
TARIF_DOSYASI = "kullanici_tarifleri.json"
YORUM_DOSYASI = "yorumlar.json"
KULLANICI_DOSYASI = "kullanicilar.json"

# --- 3. VERİTABANI FONKSİYONLARI ---
def veri_yukle(dosya_adi):
    if os.path.exists(dosya_adi):
        with open(dosya_adi, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return {} if "json" in dosya_adi else []
    return {} if "yorum" in dosya_adi or "kullanici" in dosya_adi else []

def veri_kaydet(dosya_adi, veri):
    with open(dosya_adi, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

# --- Kullanıcı İşlemleri ---
def kullanici_kaydet(k_adi, sifre):
    users = veri_yukle(KULLANICI_DOSYASI)
    if k_adi in users: return False
    users[k_adi] = sifre
    veri_kaydet(KULLANICI_DOSYASI, users)
    return True

def giris_kontrol(k_adi, sifre):
    if k_adi == "admin" and sifre == "2026": return "admin"
    users = veri_yukle(KULLANICI_DOSYASI)
    return "user" if users.get(k_adi) == sifre else False

# --- Tarif & Yorum İşlemleri ---
def tarif_ekle(yeni):
    mevcut = veri_yukle(TARIF_DOSYASI)
    if isinstance(mevcut, dict): mevcut = [] # Hata önleyici
    mevcut.append(yeni)
    veri_kaydet(TARIF_DOSYASI, mevcut)

def tarif_sil(idx):
    mevcut = veri_yukle(TARIF_DOSYASI)
    if 0 <= idx < len(mevcut):
        del mevcut[idx]
        veri_kaydet(TARIF_DOSYASI, mevcut)
        return True
    return False

def yorum_ekle(yemek, isim, mesaj):
    data = veri_yukle(YORUM_DOSYASI)
    if yemek not in data: data[yemek] = []
    data[yemek].insert(0, {"isim": isim, "msg": mesaj, "tarih": datetime.now().strftime("%d-%m %H:%M")})
    veri_kaydet(YORUM_DOSYASI, data)

# --- 4. CSS (PREMIUM TASARIM - İŞTAH AÇICI MOD) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
.stApp { background-color: #0e1117; background-image: radial-gradient(circle at 50% 0%, #5e0a0a 0%, #0e1117 80%); font-family: 'Inter', sans-serif; color: #fff; }

/* Başlık */
h1 { 
    font-weight: 900; 
    font-size: 3rem;
    background: -webkit-linear-gradient(45deg, #FFCC00, #FF4500); 
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent; 
    text-align: center; 
    text-shadow: 0px 4px 15px rgba(255, 69, 0, 0.4);
}

/* Kart Tasarımı (Daha Büyük ve Şık) */
.haber-kart { 
    background: rgba(255, 255, 255, 0.04); 
    backdrop-filter: blur(12px); 
    padding: 25px; 
    border-radius: 20px; 
    border: 1px solid rgba(255, 255, 255, 0.08); 
    margin-bottom: 25px; 
    transition: all 0.4s ease;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}
.haber-kart:hover { 
    transform: translateY(-7px) scale(1.01); 
    border-color: rgba(255, 204, 0, 0.5); 
    box-shadow: 0 15px 35px -5px rgba(255, 69, 0, 0.3);
}

/* Malzeme Listesi */
.malzeme-kutusu { 
    background: rgba(255, 165, 0, 0.08); 
    border-left: 5px solid #FF7900; 
    padding: 20px; 
    border-radius: 10px; 
    margin: 20px 0;
    font-size: 1.05rem;
}

/* Migros Butonu */
.btn-migros { 
    display: block; width: 100%; 
    background: linear-gradient(135deg, #FF7900, #F7941D); 
    color: white !important; text-align: center; padding: 18px; 
    border-radius: 15px; font-weight: 800; text-decoration: none; 
    box-shadow: 0 5px 20px rgba(255, 121, 0, 0.5); transition: 0.3s; font-size: 18px; 
}
.btn-migros:hover { transform: scale(1.02); filter: brightness(1.1); }

/* Yorumlar */
.yorum-kutu { 
    background: rgba(255,255,255,0.05); 
    padding: 15px; border-radius: 12px; margin-bottom: 10px; 
    border-left: 3px solid #FFCC00; 
}

/* Genel */
[data-testid="stImage"] { display: block; margin: 0 auto; border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

# --- 5. DETAYLI & İŞTAH AÇAN TARİFLER (Özenle Yazılmış) ---
SABIT_TARIFLER = [
    # KAHVALTI
    {
        "ad": "Trabzon Usulü Kuymak", "kat": "Kahvaltı", 
        "malz": ["2 Dolu Yemek Kaşığı Tereyağı", "2 Yemek Kaşığı Mısır Unu", "1 Kase Trabzon/Çeçil Peyniri", "1 Su Bardağı Ilık Su"], 
        "desc": "Karadeniz'in uzadıkça uzayan, tereyağı kokan efsanesi.", 
        "tar": "1. Bakır tavada tereyağını eritin ama yakmayın, sadece köpürsün.\n2. Mısır ununu ekleyip rengi hafif dönene ve o mis gibi kavrulmuş koku çıkana kadar kısık ateşte karıştırın.\n3. Suyu yavaş yavaş eklerken bir yandan hızlıca karıştırın ki topaklanmasın. (Boza kıvamı alacak).\n4. Karışım göz göz olup yağını hafif salmaya başlayınca peyniri ekleyin.\n5. **Püf Noktası:** Peynir eriyip, tereyağı sapsarı üste çıkana kadar hiç karıştırmadan pişirin. Sıcak servis yapın, ekmeği banın!"
    },
    {
        "ad": "Efsane Menemen", "kat": "Kahvaltı", 
        "malz": ["3 Adet Yumurta", "3 Adet Sivri Biber", "2 Adet Orta Boy Domates", "Sıvı Yağ & Tereyağı", "Tuz, Karabiber, Pul Biber"], 
        "desc": "Pazar sabahlarının vazgeçilmezi. Ekmeği hazırlayın.", 
        "tar": "1. Biberleri ince halkalar halinde doğrayın. Tavaya yağı alıp biberleri ölene kadar kavurun.\n2. Kabukları soyulmuş domatesleri küp küp doğrayın ve tavaya ekleyin. Kapağını kapatıp domatesler sos kıvamına gelene kadar pişirin.\n3. İster ayrı bir kapta çırpın, ister direkt kırın; yumurtaları ekleyin.\n4. **Önemli:** Yumurtayı çok karıştırmayın, bırakın beyazı ve sarısı hafifçe birbirine geçsin. Baharatları ekleyip, yumurtalar istediğiniz kıvama gelince ocaktan alın."
    },
    {
        "ad": "Puf Puf Pankek", "kat": "Kahvaltı",
        "malz": ["1.5 Su Bardağı Un", "1 Su Bardağı Süt", "1 Yumurta", "1 Paket Kabartma Tozu", "1 Paket Vanilya", "2 YK Şeker"],
        "desc": "Bulut gibi yumuşacık, bal ve çikolatanın en iyi arkadaşı.",
        "tar": "1. Derin bir kapta yumurta ve şekeri köpürene kadar iyice çırpın.\n2. Sütü, sıvı yağı (1 kaşık) ekleyin.\n3. Un, kabartma tozu ve vanilyayı eleyerek karışıma dökün. (Topak kalmayana kadar çırpın).\n4. Yapışmaz tavayı çok az yağlayın ve ısıtın. Hamurdan bir kepçe dökün.\n5. Üzeri göz göz baloncuk olunca diğer tarafını çevirin. İki tarafı da altın sarısı olunca alın."
    },
    
    # ANA YEMEKLER
    {
        "ad": "Lokanta Usulü Tavuk Sote", "kat": "Tavuk",
        "malz": ["500gr Tavuk Göğsü (Küp)", "2 Adet Yeşil Biber", "1 Adet Kapya Biber", "2 Adet Domates", "1 Soğan", "Sarımsak", "Kekik, Kimyon"],
        "desc": "Suyuna ekmek banmalık, 20 dakikada hazır ziyafet.",
        "tar": "1. Geniş bir tavayı (veya wok) iyice ısıtın. Tavukları atıp sularını salıp çekene kadar yüksek ateşte mühürleyin.\n2. Yemeklik doğranmış soğanları ekleyip şeffaflaşana kadar kavurun.\n3. Biberleri ekleyip 2-3 dakika daha çevirin.\n4. Kabuğu soyulmuş küp domatesleri, ezilmiş sarımsağı ve baharatları ekleyin.\n5. Domatesler suyunu salıp sos kıvamına gelene kadar, kapağı kapalı olarak kısık ateşte pişirin. En son kekik serpip servis edin."
    },
    {
        "ad": "Anne Köftesi & Patates", "kat": "Ana Yemek",
        "malz": ["500gr Kıyma (Orta Yağlı)", "1 Adet Kuru Soğan (Rende)", "1 Yumurta", "3-4 Dilim Bayat Ekmek İçi", "Maydanoz", "Kimyon, Tuz, Karabiber"],
        "desc": "Çocukluğun o unutulmaz tadı. Yanına kızarmış patates şart.",
        "tar": "1. Soğanı rendeleyin ve suyunu sıkın (Acısını atması için).\n2. Yoğurma kabına kıymayı, soğan posasını, yumurtayı, ıslatılıp sıkılmış ekmek içini, ince kıyılmış maydanozu ve baharatları alın.\n3. **Püf Noktası:** En az 10-15 dakika macun kıvamına gelene kadar yoğurun. Vaktiniz varsa buzdolabında 1 saat dinlendirin.\n4. Elinizle şekil verip, kızgın yağda arkalı önlü kızartın.\n5. Yanına elma dilim patates kızartarak servis yapın."
    },
    {
        "ad": "Karnıyarık", "kat": "Ana Yemek",
        "malz": ["6 Adet Kemer Patlıcan", "250gr Kıyma", "2 Yeşil Biber", "1 Soğan", "1 Domates", "Salça", "Maydanoz"],
        "desc": "Türk mutfağının şahı. Pilavsız gitmez.",
        "tar": "1. Patlıcanları alaca soyup tuzlu suda 20dk bekletin (Acısı çıksın). Sonra kurulayıp bütün halde kızgın yağda çevirerek kızartın.\n2. **İç Harcı:** Soğanı kavurun, kıymayı ekleyip rengi dönene kadar pişirin. Biberi, domates rendesini ve salçayı ekleyin. En son maydanozu atıp ocaktan alın.\n3. Kızarmış patlıcanları tepsiye dizin, ortalarını kaşıkla nazikçe açın (Sandam gibi).\n4. İç harcı patlıcanlara doldurun. Üzerine birer dilim domates ve biber koyun.\n5. Bir kasede salçalı sıcak su hazırlayıp tepsinin tabanına dökün. 180 derece fırında 20-25 dakika özleşene kadar pişirin."
    },

    # MAKARNA & DÜNYA MUTFAĞI
    {
        "ad": "Kremalı Mantarlı Makarna", "kat": "Makarna",
        "malz": ["1 Paket Penne/Burgu Makarna", "400gr Mantar", "1 Kutu Sıvı Krema", "2 Diş Sarımsak", "Taze Fesleğen veya Maydanoz", "Tereyağı"],
        "desc": "Lüks restoran lezzetini evde yapın.",
        "tar": "1. Makarnayı bol tuzlu suda haşlayın (Çok yumuşamasın, 'al dente' kalsın).\n2. Bu sırada mantarları ince doğrayın. Geniş tavada tereyağını eritin ve mantarları **yüksek ateşte** suyunu salıp hemen çekene kadar soteleyin.\n3. Ezilmiş sarımsağı ekleyip kokusu çıkana kadar çevirin.\n4. Kremayı ekleyin, kaynamaya başlayınca altını kısın. Tuz ve karabiber atın.\n5. Haşlanan makarnaları süzüp (haşlama suyundan yarım çay bardağı ayırın) sosun içine atın.\n6. Sosla makarnayı harmanlayın, gerekirse ayırdığınız sudan ekleyin. Üzerine yeşillik serpip sıcak servis yapın."
    },
    {
        "ad": "Ev Yapımı Pizza", "kat": "Dünya Mutfağı",
        "malz": ["3 Su Bardağı Un", "1 Su Bardağı Ilık Su", "1 Paket Maya", "Mozzarella/Kaşar", "Sucuk, Mantar, Zeytin", "Domates Sosu"],
        "desc": "Dışarıdan söylemeye son. İncecik hamur, bol malzeme.",
        "tar": "1. Un, maya, su, tuz ve 2 kaşık zeytinyağını yoğurun. Ele yapışmayan yumuşak bir hamur elde edin. 40dk mayalandırın.\n2. Hamuru incecik açın ve yağlı kağıt serili tepsiye koyun.\n3. Üzerine domates sosunu (salça+su+kekik) sürün.\n4. Önce peynirin yarısını, sonra dilediğiniz malzemeleri (sucuk, mantar vs.) dizin.\n5. Önceden ısıtılmış **en yüksek derece (220-250)** fırının en alt rafında pişirin. Çıkmaya yakın kalan peyniri serpin."
    },

    # SEBZELİ & SALATA
    {
        "ad": "Zeytinyağlı Taze Fasulye", "kat": "Sebzeli",
        "malz": ["500gr Taze Fasulye", "1 Büyük Soğan", "2 Domates", "Yarım Çay Bardağı Zeytinyağı", "1 Tatlı Kaşığı Şeker", "Sıcak Su"],
        "desc": "Soğuk yendiğinde tadına doyum olmaz.",
        "tar": "1. Fasulyeleri ayıklayıp isteğe göre kırın veya boyuna kesin.\n2. Tencereye zeytinyağını ve yemeklik doğranmış soğanları alıp hafifçe kavurun.\n3. Fasulyeleri ekleyip renkleri canlı yeşile dönene kadar (sarartana kadar) kavurun.\n4. Rendelenmiş domatesi, tuzu ve **mutlaka şekeri** ekleyin.\n5. Üzerini geçmeyecek kadar az sıcak su ekleyin. Kapağı kapalı, kısık ateşte fasulyeler yumuşayana kadar pişirin. Tenceresinde soğutun."
    },
    {
        "ad": "Mücver", "kat": "Atıştırmalık",
        "malz": ["3 Adet Kabak", "2 Yumurta", "3-4 Dal Taze Soğan", "Yarım Demet Dereotu", "Un", "Beyaz Peynir"],
        "desc": "Sebze sevmeyene bile kabak yediren lezzet.",
        "tar": "1. Kabakları rendeleyin ve **suyunu avucunuzla sımsıkı sıkın.** (Bu çok önemli, yoksa içi hamur kalır).\n2. Bir kaba kabakları, yumurtaları, ince kıyılmış yeşillikleri, ezilmiş peyniri ve baharatları alın.\n3. Kıvam alana kadar (kek hamurundan biraz koyu) un ekleyin.\n4. Tavada az yağı kızdırın. Kaşıkla harçtan alıp tavaya dökün ve üzerini düzeltin.\n5. Arkalı önlü altın sarısı olana kadar kızartın. Sarımsaklı yoğurtla servis yapın."
    },
    
    # TATLILAR
    {
        "ad": "Fırın Sütlaç", "kat": "Tatlı",
        "malz": ["1 Litre Süt", "1 Çay Bardağı Pirinç", "1 Su Bardağı Şeker", "2 Dolu Yemek Kaşığı Nişasta", "1 Paket Vanilya"],
        "desc": "Üzeri nar gibi kızarmış, kıvamı yerinde.",
        "tar": "1. Pirinci 2 su bardağı suda yumuşayana kadar haşlayın (suyunu çeksin).\n2. Sütü ve şekeri ekleyip kaynatın.\n3. Nişastayı yarım çay bardağı sütle açıp tencereye yavaşça dökün. Kıvam alana kadar karıştırın. Vanilyayı ekleyip ocaktan alın.\n4. Sütlacı güveç kaplarına paylaştırın.\n5. Fırın tepsisine güveçlerin yarısına gelecek kadar soğuk su koyun.\n6. Önceden ısıtılmış 200 derece fırının **sadece üst ızgarasını** açın ve üzeri kızarana kadar pişirin."
    },
    {
        "ad": "Islak Kek (Brownie)", "kat": "Tatlı",
        "malz": ["3 Yumurta", "1.5 Su Bardağı Şeker", "1.5 Su Bardağı Süt", "1 Su Bardağı Sıvı Yağ", "3 YK Kakao", "2 Su Bardağı Un"],
        "desc": "Bol soslu, ağızda eriyen efsane.",
        "tar": "1. Yumurta ve şekeri köpürene kadar çırpın. Süt, yağ ve kakaoyu ekleyip çırpın.\n2. **Önemli:** Bu karışımdan 1 su bardağı ayırın (Sosu için).\n3. Kalan karışıma un ve kabartma tozu ekleyip yağlanmış tepsiye dökün. 180 derecede pişirin.\n4. Ayırdığınız sosa yarım bardak daha süt ekleyip bir taşım kaynatın.\n5. Kek fırından çıkınca dilimleyin ve sıcak keke sosu dökün. Soğuyunca hindistan cevizi ile süsleyin."
    }
]

# --- 6. AKILLI ARAMA ---
def tarifleri_bul(girdi, kategori):
    girdi = girdi.lower()
    # "domates, biber" -> ['domates', 'biber']
    arananlar = [x.strip() for x in girdi.replace(",", " ").split() if x.strip()]
    
    # Veritabanlarını birleştir
    tum_liste = SABIT_TARIFLER + veri_yukle(TARIF_DOSYASI)
    
    # Eğer arama boşsa ve kategori tümü ise -> Vitrin modunda karışık göster
    if not arananlar and kategori == "Tümü":
        return tum_liste

    bulunanlar = []
    for t in tum_liste:
        # Kategori Filtresi
        if kategori != "Tümü" and t.get("kat") != kategori:
            continue
            
        metin = (t["ad"] + " " + " ".join(t["malz"])).lower()
        
        # Eğer kelime yazılmadıysa (sadece kategori seçildiyse) ekle
        if not arananlar:
            bulunanlar.append(t)
        else:
            # OR Mantığı: Kelimelerden HERHANGİ BİRİ varsa ekle
            for kelime in arananlar:
                if kelime in metin:
                    bulunanlar.append(t)
                    break
    return bulunanlar

# --- 7. ARAYÜZ ---
if "login" not in st.session_state: st.session_state.login = False
if "user" not in st.session_state: st.session_state.user = None
if "secilen" not in st.session_state: st.session_state.secilen = None

# Yan Menü
with st.sidebar:
    try: st.image("logo.png", use_container_width=True)
    except: pass
    
    if st.session_state.login:
        st.success(f"Hoşgeldin, {st.session_state.user}")
        if st.button("Çıkış Yap"):
            st.session_state.login = False
            st.session_state.user = None
            st.rerun()
    else:
        st.info("Tarif eklemek/yorum yapmak için giriş yap.")
        tab1, tab2 = st.tabs(["Giriş", "Kayıt"])
        with tab1:
            k = st.text_input("Kullanıcı Adı")
            s = st.text_input("Şifre", type="password")
            if st.button("Giriş"):
                res = giris_kontrol(k, s)
                if res:
                    st.session_state.login = True
                    st.session_state.user = k if res == "user" else "admin"
                    st.rerun()
                else: st.error("Hatalı!")
        with tab2:
            yk = st.text_input("Yeni Ad")
            ys = st.text_input("Yeni Şifre", type="password")
            if st.button("Kayıt Ol"):
                if kullanici_kaydet(yk, ys): st.success("Kayıt oldun! Giriş yapabilirsin.")
                else: st.error("İsim alınmış.")

    st.markdown("---")
    kat = st.radio("Kategori:", ["Tümü", "Kahvaltı", "Ana Yemek", "Tavuk", "Makarna", "Sebzeli", "Atıştırmalık", "Tatlı", "Kullanıcı"])

# Ana Ekran
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try: st.image("logo.png", use_container_width=True)
    except: pass

st.title("Dolap Şefi")

# Navigasyon
t1, t2 = st.tabs(["🔍 Tarif Ara", "👨‍🍳 Tarif Paylaş"])

with t1:
    if st.session_state.secilen is None:
        aramas = st.text_input("Bugün canın ne çekiyor?", placeholder="Malzeme (Patates, Tavuk) veya Yemek Adı...")
        sonuclar = tarifleri_bul(aramas, kat)
        
        if sonuclar:
            st.write(f"🎉 **{len(sonuclar)}** Lezzet Seni Bekliyor")
            for i, t in enumerate(sonuclar):
                # Kart Görünümü
                st.markdown(f"""
                <div class="haber-kart">
                    <h3 style="margin:0; color:#FFCC00;">{t['ad']}</h3>
                    <p style="color:#ccc; font-style:italic; font-size:0.9rem;">{t['desc']}</p>
                    <span style="background:rgba(255,255,255,0.1); padding:3px 8px; border-radius:5px; font-size:0.8rem;">{t.get('kat','Genel')}</span>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Tarife Git 👉", key=f"btn_{i}"):
                    st.session_state.secilen = t
                    st.rerun()
        else:
            st.warning("Bu kriterde tarif bulamadım şefim. Başka bir şey deneyelim mi?")
            
    else:
        # DETAY EKRANI (FULL EKRAN)
        t = st.session_state.secilen
        if st.button("⬅️ Geri Dön"):
            st.session_state.secilen = None
            st.rerun()
        
        st.markdown(f"<h1>{t['ad']}</h1>", unsafe_allow_html=True)
        st.caption(f"Kategori: {t.get('kat','Genel')}")
        
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.markdown('<div class="malzeme-kutusu"><h4>🛒 Malzemeler</h4><ul>', unsafe_allow_html=True)
            malz = t['malz'] if isinstance(t['malz'], list) else t['malz'].split('\n')
            for m in malz: st.markdown(f"<li>{m}</li>", unsafe_allow_html=True)
            st.markdown("</ul></div>", unsafe_allow_html=True)
            
            # Migros Butonu
            ana_malz = malz[0].split(" ")[-1] if malz else "Yemek"
            st.markdown(f'<a href="https://www.migros.com.tr/arama?q={ana_malz}" target="_blank" class="btn-migros">🍊 Malzemeleri Al</a>', unsafe_allow_html=True)

        with c2:
            st.markdown("### 👨‍🍳 Hazırlanışı")
            st.markdown(f"<div style='font-size:1.1rem; line-height:1.8; color:#eee;'>{t['tar']}</div>", unsafe_allow_html=True)
            
            # Yorumlar
            st.markdown("---")
            st.subheader("💬 Yorumlar")
            if st.session_state.login:
                with st.form("yform"):
                    ymsg = st.text_area("Yorumun nedir?")
                    if st.form_submit_button("Gönder"):
                        yorum_ekle(t['ad'], st.session_state.user, ymsg)
                        st.rerun()
            else: st.info("Yorum yapmak için giriş yap.")
            
            yorumlar = veri_yukle(YORUM_DOSYASI).get(t['ad'], [])
            for y in yorumlar:
                st.markdown(f"<div class='yorum-kutu'><b>{y['isim']}</b> <small>{y['tarih']}</small><br>{y['msg']}</div>", unsafe_allow_html=True)

with t2:
    st.header("Topluluk Tarifleri & Ekleme")
    
    # Ekleme Formu
    if st.session_state.login:
        with st.expander("➕ Yeni Tarif Ekle", expanded=True):
            with st.form("add"):
                ta = st.text_input("Yemek Adı")
                td = st.text_input("Kısa Açıklama (İştah açıcı olsun)")
                tm = st.text_area("Malzemeler (Alt alta veya virgülle)")
                tt = st.text_area("Tarif (Detaylı anlat)")
                tkat = st.selectbox("Kategori", ["Kullanıcı", "Kahvaltı", "Ana Yemek", "Tatlı"])
                if st.form_submit_button("Yayınla"):
                    if ta and tt:
                        yeni = {"ad": ta, "desc": td, "malz": tm.split("\n"), "tar": tt, "kat": tkat, "sef": st.session_state.user}
                        tarif_ekle(yeni)
                        st.success("Tarif eklendi!")
                        time.sleep(1)
                        st.rerun()
    else:
        st.warning("Tarif eklemek için giriş yapmalısın.")
    
    st.markdown("---")
    # Kullanıcı Tariflerini Listele (Admin Silebilir)
    k_tarifler = veri_yukle(TARIF_DOSYASI)
    if k_tarifler:
        for i, k in enumerate(k_tarifler):
            col_x, col_y = st.columns([4, 1])
            col_x.markdown(f"**{k['ad']}** (Şef: {k.get('sef','Anonim')})\n\n_{k['desc']}_")
            if st.session_state.user == "admin":
                if col_y.button("🗑️", key=f"del_{i}"):
                    tarif_sil(i)
                    st.rerun()
            st.markdown("---")
    else:
        st.info("Henüz kullanıcı tarifi yok. İlk sen ekle!")

st.markdown("<br><center><small>© 2026 Dolap Şefi</small></center>", unsafe_allow_html=True)

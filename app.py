import streamlit as st
import time
import json
import os
from datetime import datetime

# --- 1. AYARLAR & GÜVENLİK ---
st.set_page_config(
    page_title="Dolap Şefi",
    page_icon="👨‍🍳",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 🔥 GÜVENLİK ŞİFRESİ
ADMIN_SIFRESI = "2026"

# --- 2. VERİTABANI SİSTEMLERİ ---
TARIF_DOSYASI = "kullanici_tarifleri.json"
YORUM_DOSYASI = "yorumlar.json"

def tarifleri_yukle():
    if os.path.exists(TARIF_DOSYASI):
        with open(TARIF_DOSYASI, "r", encoding="utf-8") as f:
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
    with open(TARIF_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(mevcut_tarifler, f, ensure_ascii=False, indent=4)

def begeni_arttir(index):
    tarifler = tarifleri_yukle()
    if 0 <= index < len(tarifler):
        tarifler[index]['likes'] = tarifler[index].get('likes', 0) + 1
        with open(TARIF_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(tarifler, f, ensure_ascii=False, indent=4)

def yorumlari_yukle():
    if os.path.exists(YORUM_DOSYASI):
        with open(YORUM_DOSYASI, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def yorum_ekle(yemek_adi, isim, yorum):
    tum_yorumlar = yorumlari_yukle()
    if yemek_adi not in tum_yorumlar:
        tum_yorumlar[yemek_adi] = []
    
    yeni_yorum = {
        "isim": isim,
        "yorum": yorum,
        "tarih": datetime.now().strftime("%d-%m-%Y %H:%M")
    }
    tum_yorumlar[yemek_adi].insert(0, yeni_yorum)
    
    with open(YORUM_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(tum_yorumlar, f, ensure_ascii=False, indent=4)

# --- 3. HAFIZA ---
if "sonuclar" not in st.session_state: st.session_state.sonuclar = [] 
if "secilen_tarif" not in st.session_state: st.session_state.secilen_tarif = None 

# --- 4. CSS (SENIOR DEV DESIGN) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
.stApp { background-color: #0e1117; background-image: radial-gradient(circle at 50% 0%, #4a0404 0%, #0e1117 60%); font-family: 'Inter', sans-serif; color: #fff; }
h1 { font-weight: 800; background: -webkit-linear-gradient(45deg, #FFCC00, #FF6B6B); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 0; }
.haber-kart { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); padding: 20px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 20px; transition: all 0.3s; }
.haber-kart:hover { transform: translateY(-5px); border-color: rgba(255, 204, 0, 0.3); box-shadow: 0 10px 30px -10px rgba(255, 107, 107, 0.2); }
.malzeme-kutusu { background: rgba(255, 204, 0, 0.05); border: 1px dashed #FFCC00; padding: 20px; border-radius: 12px; margin-bottom: 25px; }
.btn-migros { display: block; width: 100%; background: linear-gradient(135deg, #FF7900, #F7941D); color: white !important; text-align: center; padding: 16px; border-radius: 12px; font-weight: 700; text-decoration: none; box-shadow: 0 4px 15px rgba(255, 121, 0, 0.4); transition: 0.3s; font-size: 18px; margin-top: 20px; }
.btn-migros:hover { transform: scale(1.02); box-shadow: 0 8px 25px rgba(255, 121, 0, 0.6); }
.yorum-kutu { background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; margin-bottom: 10px; border-left: 3px solid #FFCC00; }
[data-testid="stImage"] { display: block; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

# --- 5. DETAYLI ŞEF TARİFLERİ ---
TUM_TARIFLER = [
    # KAHVALTI
    {"ad": "Efsane Menemen", "kat": "Kahvaltı", "malz": ["3 Adet Yumurta", "2 Orta Boy Domates", "3 Adet Sivri Biber", "2 Yemek Kaşığı Sıvı Yağ", "Tuz, Karabiber, Pulbiber"], "desc": "Soğanlı mı soğansız mı tartışmasını bitiren lezzet.", "tar": "1. Biberleri ince ince doğrayın ve kızgın yağda renkleri dönene kadar kavurun.\n2. Kabukları soyulmuş ve küp doğranmış domatesleri ekleyin. Tavanın kapağını kapatıp domatesler suyunu çekip sos kıvamına gelene kadar pişirin.\n3. Yumurtaları ayrı bir kapta hafifçe çırpın (veya direkt kırın) ve tavaya dökün.\n4. **Püf Noktası:** Yumurtayı çok karıştırmayın, bırakın beyazı ve sarısı hafifçe birbirine geçsin. Baharatları ekleyip sıcak servis yapın."},
    {"ad": "Kuymak (Mıhlama)", "kat": "Kahvaltı", "malz": ["2 Yemek Kaşığı Mısır Unu", "2 Dolu Yemek Kaşığı Tereyağı", "1 Kase Trabzon Peyniri (veya Çeçil)", "1 Su Bardağı Ilık Su"], "desc": "Karadeniz usulü, uzadıkça uzayan lezzet.", "tar": "1. Bakır tavada tereyağını eritin (yakmadan köpürtün).\n2. Mısır ununu ekleyip rengi hafif dönene ve kokusu çıkana kadar kısık ateşte kavurun.\n3. Suyu yavaş yavaş eklerken bir yandan hızlıca karıştırın (topaklanmasın).\n4. Karışım göz göz olup yağını salmaya başlayınca peyniri ekleyin.\n5. Peynir eriyip yağ yüzeye çıkana kadar hiç dokunmadan pişirin. Sıcak servis şart!"},
    {"ad": "Pankek", "kat": "Kahvaltı", "malz": ["1.5 Su Bardağı Un", "1 Su Bardağı Süt", "1 Yumurta", "1 Kabartma Tozu", "2 Yemek Kaşığı Şeker"], "desc": "Pazar sabahlarının vazgeçilmezi, puf puf kabarır.", "tar": "1. Yumurta ve şekeri köpürene kadar çırpın. Sütü ekleyin.\n2. Un ve kabartma tozunu eleyerek karışıma ekleyin. Boza kıvamında akışkan bir hamur olmalı.\n3. Yapışmaz tavayı çok az yağlayın ve ısıtın.\n4. Hamurdan bir kepçe dökün. Üzeri göz göz delik olunca diğer tarafını çevirin.\n5. **Servis:** Bal, çikolata veya reçelle servis yapın."},
    
    # ANA YEMEKLER
    {"ad": "Köri Soslu Tavuk", "kat": "Tavuk", "malz": ["500gr Tavuk Göğsü (Küp doğranmış)", "1 Kutu Sıvı Krema (200ml)", "1.5 Tatlı Kaşığı Köri", "Karabiber, Tuz", "2 Yemek Kaşığı Sıvı Yağ"], "desc": "Dışarıda yediğinizden çok daha lezzetli.", "tar": "1. Tavukları kızgın tavaya atın ve suyunu salıp çekene kadar yüksek ateşte soteleyin.\n2. Tavuklar kızarınca ocağın altını kısın, kremayı dökün.\n3. Köri, tuz ve karabiberi ekleyip karıştırın.\n4. Sos hafif koyulaşıp tavukla özleşene kadar (yaklaşık 3-4 dakika) pişirin.\n5. Yanına makarna çok yakışır."},
    {"ad": "Karnıyarık", "kat": "Ana Yemek", "malz": ["6 Adet Orta Boy Patlıcan", "250gr Kıyma", "2 Yeşil Biber", "1 Soğan", "1 Domates", "Salça", "Maydanoz"], "desc": "Patlıcan ve kıymanın mükemmel uyumu.", "tar": "1. Patlıcanları alaca soyup tuzlu suda 15dk bekletin (acısı çıksın). Sonra kurulayıp kızgın yağda çevirerek kızartın.\n2. **İç Harcı:** Soğanı ve biberi kavurun, kıymayı ekleyin. Pişince domates rendesi, tuz, karabiber ekleyin. En son maydanozu atıp ocaktan alın.\n3. Patlıcanların ortasını bir kaşık yardımıyla açın ve harcı doldurun.\n4. Bir kasede 1 kaşık salçayı sıcak suyla açıp tepsinin tabanına dökün.\n5. 180 derece fırında 20-25 dakika pişirin."},
    {"ad": "Kuru Fasulye", "kat": "Ana Yemek", "malz": ["2 Su Bardağı Kuru Fasulye", "250gr Kuşbaşı Et", "1 Büyük Soğan", "1 Yemek Kaşığı Biber Salçası", "Tereyağı"], "desc": "Tam kıvamında, helmelenmiş milli yemeğimiz.", "tar": "1. Fasulyeleri mutlaka bir gece önceden suda bekletin.\n2. Düdüklü tencerede tereyağı ile yemeklik doğranmış soğanları ve etleri kavurun.\n3. Salçayı ekleyip kokusu çıkana kadar kavurmaya devam edin.\n4. Süzdüğünüz fasulyeleri ekleyin, üzerini 2 parmak geçecek kadar sıcak su koyun.\n5. Düdüklünün kapağını kapatıp fasulyenin cinsine göre 25-30 dakika pişirin."},

    # MAKARNA & PİLAV
    {"ad": "Kremalı Mantarlı Makarna", "kat": "Makarna", "malz": ["1 Paket Penne Makarna", "400gr Mantar", "1 Kutu Krema", "2 Diş Sarımsak", "Maydanoz", "Tereyağı"], "desc": "Restoran kalitesinde, 15 dakikada hazır.", "tar": "1. Makarnayı bol tuzlu suda haşlayın (hafif diri kalsın, 'al dente').\n2. Bu sırada mantarları ince doğrayın ve tereyağında suyunu salıp çekene kadar yüksek ateşte kavurun.\n3. Ezilmiş sarımsağı ekleyip 1 dakika daha çevirin.\n4. Kremayı ekleyin, kaynamaya başlayınca tuz ve karabiber atın.\n5. Süzdüğünüz makarnaları sosun içine atıp 1-2 dakika karıştırın. Üzerine maydanoz serpip servis yapın."},
    {"ad": "Şehriyeli Pirinç Pilavı", "kat": "Pilav", "malz": ["2 Su Bardağı Baldo Pirinç", "3 Su Bardağı Sıcak Su (veya Tavuk Suyu)", "Yarım Çay Bardağı Arpa Şehriye", "3 Yemek Kaşığı Tereyağı", "Tuz"], "desc": "Tane tane dökülen pilavın sırrı burada.", "tar": "1. Pirinci ılık ve tuzlu suda 20 dakika bekletin, sonra nişastası gidene kadar (suyu berraklaşana kadar) yıkayın.\n2. Tencerede tereyağını eritin, şehriyeleri rengi koyulaşana kadar kavurun.\n3. Süzülen pirinçleri ekleyip pirinçler şeffaflaşana ve birbirine yapışmayana kadar (yaklaşık 5dk) kavurun. **Bu aşama çok önemli!**\n4. Sıcak suyu ve tuzu ekleyip karıştırın. Kapağını kapatın.\n5. Önce yüksek ateşte kaynasın, sonra en kısık ateşte suyunu çekene kadar pişirin. Demlenmesi için kapağın altına kağıt havlu koyun."},

    # TATLILAR
    {"ad": "Fırın Sütlaç", "kat": "Tatlı", "malz": ["1 Litre Süt", "1 Çay Bardağı Pirinç", "1 Su Bardağı Şeker", "2 Dolu Yemek Kaşığı Nişasta", "1 Paket Vanilya"], "desc": "Üzeri nar gibi kızarmış, kıvamı yerinde.", "tar": "1. Pirinci 2 su bardağı suda yumuşayana kadar haşlayın (suyunu çeksin).\n2. Sütü ve şekeri ekleyip kaynatın.\n3. Nişastayı yarım çay bardağı sütle açıp tencereye yavaşça dökün. Kıvam alana kadar karıştırın. Vanilyayı ekleyip ocaktan alın.\n4. Sütlacı güveç kaplarına paylaştırın.\n5. Fırın tepsisine güveçlerin yarısına gelecek kadar soğuk su koyun.\n6. Önceden ısıtılmış 200 derece fırının **sadece üst ızgarasını** açın ve üzeri kızarana kadar pişirin."},
    {"ad": "Magnolia", "kat": "Tatlı", "malz": ["1 Litre Süt", "1 Su Bardağı Şeker", "2 YK Un, 2 YK Nişasta", "1 Yumurta Sarısı", "1 Kutu Krema", "Bisküvi ve Çilek/Muz"], "desc": "Kaşık kaşık mutluluk.", "tar": "1. Tencereye süt, şeker, un, nişasta ve yumurta sarısını alın. Kaynayıp koyulaşana kadar sürekli karıştırarak pişirin.\n2. Ocaktan alıp ılımaya bırakın. Ilıyınca içine 1 kutu sıvı krema ekleyip mikserle 3-4 dakika çırpın (Pürüzsüz olsun).\n3. Bisküvileri robottan geçirin.\n4. Kupların dibine bisküvi, kenarlara meyve dilimleri, ortaya muhallebi olacak şekilde kat kat dizin.\n5. Buzdolabında en az 2 saat dinlendirin."},
    # Ekstra Klasikler
    {"ad": "İzmir Köfte", "kat": "Ana Yemek", "malz": ["Kıyma", "Patates", "Biber", "Domates Sos", "Ekmek İçi"], "desc": "Fırında soslu ziyafet.", "tar": "1. Köfteleri ve elma dilim patatesleri az kızart.\n2. Tepsiye diz.\n3. Üzerine domates sos döküp fırınla."},
    {"ad": "Mücver", "kat": "Ana Yemek", "malz": ["3 Kabak", "2 Yumurta", "Un", "Dereotu", "Peynir"], "desc": "Sebze sevmeyene bile yedirir.", "tar": "1. Kabağı rendele suyunu sık.\n2. Tüm malzemeleri karıştır.\n3. Kaşık kaşık kızgın yağa dök."},
     {"ad": "Çoban Salata", "kat": "Salata", "malz": ["Domates", "Salatalık", "Biber", "Soğan", "Maydanoz"], "desc": "Her yemeğin yanına.", "tar": "1. Tüm malzemeleri küçük küpler halinde doğra.\n2. Zeytinyağı, limon ve tuzla harmanla."},
    {"ad": "Cacık", "kat": "Meze", "malz": ["Yoğurt", "Salatalık", "Sarımsak", "Nane", "Zeytinyağı"], "desc": "Pilavın ekürisi.", "tar": "1. Salatalıkları rendeleyip yoğurtla karıştır.\n2. Ezilmiş sarımsak ve tuz ekle.\n3. Üzerine zeytinyağı ve nane gezdir."}
]

# --- AKILLI ARAMA ALGORİTMASI (OR MANTIĞI) ---
def tarifleri_bul(girdi, kategori_filtresi):
    # Girdiyi temizle (küçük harf, virgülleri boşluk yap, listeye çevir)
    girdi = girdi.lower()
    # Örnek: "domates, marul" -> ['domates', 'marul']
    aranan_kelimeler = [x.strip() for x in girdi.replace(",", " ").split() if x.strip()]
    
    bulunanlar = []
    tam_liste = TUM_TARIFLER + tarifleri_yukle()
    
    for tarif in tam_liste:
        # 1. Kategori Kontrolü
        if kategori_filtresi != "Tümü" and tarif.get("kat") != kategori_filtresi:
            continue
            
        # 2. Malzeme Eşleşmesi (VEYA Mantığı)
        # Tarifin malzemelerini ve adını tek bir metne çeviriyoruz
        malz_text = " ".join(tarif["malz"]).lower() if isinstance(tarif["malz"], list) else str(tarif["malz"]).lower()
        tarif_adi = tarif["ad"].lower()
        
        # Eğer arama kutusu boşsa hepsini göster (Kategoriye uyanları)
        if not aranan_kelimeler:
            bulunanlar.append(tarif)
        else:
            # Aranan kelimelerden HERHANGİ BİRİ varsa ekle
            for kelime in aranan_kelimeler:
                if kelime in malz_text or kelime in tarif_adi:
                    bulunanlar.append(tarif)
                    break # Bir eşleşme yeterli, diğer kelimeye bakmaya gerek yok
                    
    return bulunanlar

# --- 6. ARAYÜZ ---
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
    st.info("🔐 **Yönetici:** Tarif eklemek için şifre gerekir.")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try: st.image("logo.png", use_container_width=True)
    except: pass

st.title("Dolap Şefi")
st.markdown(f"<p style='text-align: center; color: #ffcc00; margin-top: -10px; font-weight: 600;'>{selamlama}</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔥 Tarif Bulucu", "🏆 Şefler Vitrini"])

# --- TAB 1: ARAMA & DETAY & YORUMLAR ---
with tab1:
    if st.session_state.secilen_tarif is None:
        malzemeler = st.text_input("Dolabında ne var?", placeholder="Örn: Domates, Biber, Yumurta... (Hepsini bulur!)")
        
        # Arama Fonksiyonunu Çağır
        sonuclar = tarifleri_bul(malzemeler, kategori)
        
        # Sonuç Gösterimi
        if sonuclar:
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
             st.warning("😔 Malesef bu malzemelerle eşleşen bir tarif bulamadım. Başka bir malzeme dener misin?")

    else:
        # --- DETAY EKRANI ---
        t = st.session_state.secilen_tarif
        if st.button("⬅️ Geri Dön"):
            st.session_state.secilen_tarif = None
            st.rerun()
        st.divider()
        st.markdown(f"<h1 style='text-align:left; color:#FFCC00;'>{t['ad']}</h1>", unsafe_allow_html=True)
        st.caption(f"Kategori: {t.get('kat','Genel')} • Hazırlama: 20-30 dk")

        col_d1, col_d2 = st.columns([1, 2])
        with col_d1:
            st.markdown('<div class="malzeme-kutusu"><h4>🛒 Malzemeler</h4><ul>', unsafe_allow_html=True)
            malz_list = t['malz'] if isinstance(t['malz'], list) else t['malz'].split('\n')
            for m in malz_list: st.markdown(f"<li>{m}</li>", unsafe_allow_html=True)
            st.markdown('</ul></div>', unsafe_allow_html=True)
        with col_d2:
             st.markdown(f"""
             <div style='background:rgba(255,255,255,0.05); padding:25px; border-radius:15px; border:1px solid rgba(255,255,255,0.1);'>
                <h3 style='color:#FFCC00; margin-top:0;'>👨‍🍳 Hazırlanışı</h3>
                <div style='line-height: 1.8; white-space: pre-line; color:#eee;'>{t['tar']}</div>
             </div>
             """, unsafe_allow_html=True)
             
             ana_malzeme = malz_list[0].split(" ")[-1] if malz_list else "Yemek"
             link = f"https://www.migros.com.tr/arama?q={ana_malzeme}"
             st.markdown(f'<a href="{link}" target="_blank" class="btn-migros">🍊 Malzemeleri Migros\'tan Söyle</a>', unsafe_allow_html=True)

        # --- YORUM BÖLÜMÜ ---
        st.markdown("---")
        st.subheader(f"💬 {t['ad']} Hakkında Yorumlar")
        
        # Yorum Ekleme Formu
        with st.form("yorum_form"):
            y_isim = st.text_input("Adın Nedir?")
            y_mesaj = st.text_area("Yorumun")
            if st.form_submit_button("Yorumu Gönder"):
                if y_isim and y_mesaj:
                    yorum_ekle(t['ad'], y_isim, y_mesaj)
                    st.success("Yorumun kaydedildi!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.warning("Adını ve yorumunu yazmalısın.")

        # Yorumları Listeleme
        tum_yorumlar = yorumlari_yukle()
        if t['ad'] in tum_yorumlar:
            for y in tum_yorumlar[t['ad']]:
                st.markdown(f"""
                <div class="yorum-kutu">
                    <small style="color:#FFCC00;">{y['isim']} • {y['tarih']}</small><br>
                    {y['yorum']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Henüz yorum yapılmamış. İlk yorumu sen yap!")

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
    # --- GÜVENLİ TARİF EKLEME FORMU ---
    with st.expander("➕ Tarif Ekle (Sadece Yönetici)"):
        with st.form("ekle_form"):
            sifre_girilen = st.text_input("🔑 Yönetici Şifresi", type="password")
            k_ad = st.text_input("Şef Adı")
            t_ad = st.text_input("Yemek Adı")
            t_desc = st.text_input("Slogan")
            t_malz = st.text_area("Malzemeler")
            t_tar = st.text_area("Tarif (Detaylı Anlatım)")
            
            if st.form_submit_button("Yayınla"):
                if sifre_girilen == ADMIN_SIFRESI:
                    if k_ad and t_ad:
                        yeni = {"ad": t_ad, "kat": "Kullanıcı", "sef": k_ad, "desc": t_desc, "tar": t_tar, "malz": t_malz.split('\n'), "likes": 0}
                        tarifi_kaydet(yeni)
                        st.balloons()
                        st.success("✅ Tarif Başarıyla Eklendi!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("Lütfen alanları doldurun.")
                else:
                    st.error("⛔ Hatalı Şifre! Yetkiniz yok.")

st.markdown("<div style='text-align:center; padding:20px; color:#666; font-size:12px;'>© 2026 Dolap Şefi Inc.</div>", unsafe_allow_html=True)

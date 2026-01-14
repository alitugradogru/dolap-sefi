import streamlit as st
import time
import json
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Dolap Şefi", page_icon="👨‍🍳", layout="centered")

# --- DOSYA KAYIT SİSTEMİ (DATABASE) ---
DOSYA_ADI = "kullanici_tarifleri.json"

def tarifleri_yukle():
    """Dosyadan kayıtlı tarifleri çeker."""
    if os.path.exists(DOSYA_ADI):
        with open(DOSYA_ADI, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def tarifi_kaydet(yeni_tarif):
    """Yeni tarifi dosyaya kalıcı olarak yazar."""
    mevcut_tarifler = tarifleri_yukle()
    mevcut_tarifler.append(yeni_tarif)
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(mevcut_tarifler, f, ensure_ascii=False, indent=4)

# --- HAFIZA ---
if "sonuclar" not in st.session_state:
    st.session_state.sonuclar = [] 
if "secilen_tarif" not in st.session_state:
    st.session_state.secilen_tarif = None 

# --- TASARIM (KIRMIZI TEMA) ---
st.markdown("""
<style>
.stApp { background: linear-gradient(to bottom, #8E0E00, #1F1C18); color: white; }
h1 { text-align: center; color: #ffcc00; font-family: 'Arial Black', sans-serif; text-shadow: 2px 2px 4px #000000; margin-top: 0px; }
.haber-kart { 
    background: rgba(255,255,255,0.1); 
    padding: 15px; 
    border-radius: 12px; 
    border-left: 6px solid #ffcc00;
    margin-bottom: 15px;
    cursor: pointer;
    transition: 0.3s;
}
.haber-kart:hover { background: rgba(255,255,255,0.2); transform: scale(1.02); }
.malzeme-kutusu {
    background-color: rgba(255, 204, 0, 0.1);
    border-left: 4px solid #ffcc00;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
}
.malzeme-kutusu h4 { margin-top: 0; color: #ffcc00; }
.malzeme-kutusu ul { margin-bottom: 0; padding-left: 20px; }
.malzeme-kutusu li { margin-bottom: 5px; }
.btn-trendyol { display: block; width: 100%; background-color: #28a745; color: white; text-align: center; padding: 15px; border-radius: 10px; font-weight: bold; text-decoration: none; margin-top: 20px; font-size: 18px; }
/* Logo ortalama için */
[data-testid="stImage"] {
    display: block;
    margin-left: auto;
    margin-right: auto;
}
</style>
""", unsafe_allow_html=True)

# --- 🔥 SABİT TARİF VERİTABANI ---
TUM_TARIFLER = [
    # --- KAHVALTILIKLAR ---
    {"ad": "Efsane Menemen", "kat": "Kahvaltı", "malz": ["3 Adet Yumurta", "2 Adet Domates", "3 Adet Sivri Biber", "2 Yemek Kaşığı Sıvı Yağ", "Tuz", "Karabiber"], "desc": "Kahvaltıların vazgeçilmezi.", "tar": "1. Biberleri doğrayıp yağda kavur.\n2. Domatesleri ekle suyunu çeksin.\n3. Yumurtaları kır, çok karıştırma."},
    {"ad": "Sucuklu Yumurta", "kat": "Kahvaltı", "malz": ["Yarım Kangal Sucuk", "3 Adet Yumurta", "1 Yemek Kaşığı Tereyağı"], "desc": "Pazar sabahı klasiği.", "tar": "1. Sucukları yağda çevir.\n2. Göz göz yumurtaları kır.\n3. Sarısını patlatmadan pişir."},
    {"ad": "Kaşarlı Omlet", "kat": "Kahvaltı", "malz": ["2 Adet Yumurta", "1 Çay Bardağı Rendelenmiş Kaşar", "1 Yemek Kaşığı Tereyağı", "Tuz"], "desc": "Uzayan lezzet.", "tar": "1. Yumurtayı çırp tavaya dök.\n2. Altı pişince kaşarı koy.\n3. Katla ve servis et."},
    {"ad": "Patatesli Yumurta", "kat": "Kahvaltı", "malz": ["2 Orta Boy Patates", "3 Adet Yumurta", "Sıvı Yağ", "Tuz", "Pul Biber"], "desc": "Doyurucu ve pratik.", "tar": "1. Patatesleri küp küp kızart.\n2. Üzerine yumurtayı kır karıştır."},
    {"ad": "Krep (Akıtma)", "kat": "Kahvaltı", "malz": ["2 Su Bardağı Un", "2.5 Su Bardağı Süt", "2 Adet Yumurta", "1 Çay Kaşığı Tuz"], "desc": "İster tatlı ister tuzlu.", "tar": "1. Malzemeleri akışkan olana kadar çırp.\n2. Tavaya kepçeyle dök.\n3. Arkalı önlü pişir."},

    # --- ÇORBALAR ---
    {"ad": "Süzme Mercimek", "kat": "Çorba", "malz": ["1 Su Bardağı Kırmızı Mercimek", "1 Adet Patates", "1 Adet Havuç", "1 Adet Soğan", "2 Yemek Kaşığı Yağ"], "desc": "Limon sık iç.", "tar": "1. Sebzeleri haşla, blenderdan geçir.\n2. Yağ ve nane yakıp üzerine dök."},
    {"ad": "Ezogelin Çorbası", "kat": "Çorba", "malz": ["1 Çay Bardağı Kırmızı Mercimek", "2 Yemek Kaşığı Bulgur", "1 Yemek Kaşığı Pirinç", "Salça", "Nane"], "desc": "Lokanta usulü.", "tar": "1. Bakliyatları haşla.\n2. Ayrı yerde soğan ve salçayı kavur.\n3. Hepsini birleştir kaynat."},
    {"ad": "Domates Çorbası", "kat": "Çorba", "malz": ["4 Adet Domates", "1 Yemek Kaşığı Un", "1 Su Bardağı Süt", "Rendelenmiş Kaşar"], "desc": "Kremalı gibi yumuşak.", "tar": "1. Unu kavur, domates rendesi ekle.\n2. Suyunu ver, pişince süt ekle.\n3. Kaşarla servis et."},
    {"ad": "Yayla Çorbası", "kat": "Çorba", "malz": ["1 Kase Yoğurt", "1 Çay Bardağı Pirinç", "1 Yumurta Sarısı", "Kuru Nane"], "desc": "Naneli ferahlık.", "tar": "1. Pirinci haşla.\n2. Yoğurtlu terbiyeyi ılıştırarak ekle.\n3. Üzerine naneli yağ yak."},

    # --- SULU YEMEKLER ---
    {"ad": "Kuru Fasulye", "kat": "Ana Yemek", "malz": ["2 Su Bardağı Kuru Fasulye", "250gr Kuşbaşı Et", "1 Adet Soğan", "2 Yemek Kaşığı Salça"], "desc": "Milli yemeğimiz.", "tar": "1. Akşamdan ısla.\n2. Soğanla eti kavur, salça ekle.\n3. Fasulyeyi ekle düdüklüde pişir."},
    {"ad": "Nohut Yemeği", "kat": "Ana Yemek", "malz": ["2 Su Bardağı Nohut", "250gr Et", "1 Adet Soğan", "Salça"], "desc": "Pilavın ekürisi.", "tar": "1. Eti kavur.\n2. Haşlanmış nohutu ekle.\n3. Özleşene kadar pişir."},
    {"ad": "Taze Fasulye", "kat": "Ana Yemek", "malz": ["Yarım Kg Taze Fasulye", "2 Adet Domates", "1 Adet Soğan", "Zeytinyağı"], "desc": "Yazın vazgeçilmezi.", "tar": "1. Soğanı kavur, fasulyeyi ekle.\n2. Domatesle kısık ateşte pişir."},
    {"ad": "Karnıyarık", "kat": "Ana Yemek", "malz": ["6 Adet Patlıcan", "300gr Kıyma", "2 Adet Biber", "1 Adet Domates", "Soğan"], "desc": "Patlıcanın kralı.", "tar": "1. Patlıcanı kızart.\n2. İçini kıymalı harçla doldur.\n3. Fırınla."},
    {"ad": "Patates Yemeği", "kat": "Ana Yemek", "malz": ["4 Adet Patates", "1 Adet Soğan", "1 Yemek Kaşığı Salça", "Sıvı Yağ"], "desc": "En pratik tencere yemeği.", "tar": "1. Soğanı kavur.\n2. Küp patatesleri ve salçalı suyu ekle pişir."},

    # --- ET & TAVUK ---
    {"ad": "Anne Köftesi", "kat": "Et", "malz": ["Yarım Kg Kıyma", "1 Adet Soğan (Rende)", "1 Yumurta", "Bayat Ekmek İçi", "Maydanoz", "Kimyon"], "desc": "Patates kızartmasıyla.", "tar": "1. Yoğur.\n2. Şekil ver.\n3. Az yağda kızart."},
    {"ad": "Tavuk Sote", "kat": "Tavuk", "malz": ["500gr Tavuk Göğsü", "2 Adet Biber", "1 Adet Domates", "1 Adet Soğan"], "desc": "Ekmek banmalık.", "tar": "1. Tavuğu suyunu çekene kadar pişir.\n2. Sebzelerle kavur."},
    {"ad": "Köri Soslu Tavuk", "kat": "Tavuk", "malz": ["500gr Tavuk", "1 Kutu Krema", "1 Tatlı Kaşığı Köri", "Karabiber"], "desc": "Dünya mutfağı.", "tar": "1. Tavuğu sotele.\n2. Krema ve köri ekle çektir."},
    {"ad": "Fırın Tavuk", "kat": "Tavuk", "malz": ["Tavuk Baget/Kanat", "Patates", "Salçalı Sos", "Kekik"], "desc": "Nar gibi kızarmış.", "tar": "1. Salçalı sosla harmanla.\n2. Tepsiye diz fırınla."},

    # --- MAKARNA & PİLAV ---
    {"ad": "Pirinç Pilavı", "kat": "Pilav", "malz": ["2 Su Bardağı Pirinç", "Yarım Çay Bardağı Şehriye", "2 Yemek Kaşığı Tereyağı", "3 Su Bardağı Sıcak Su"], "desc": "Tane tane.", "tar": "1. Şehriyeyi kavur.\n2. Pirinci kavur.\n3. Suyunu ekle demle."},
    {"ad": "Salçalı Makarna", "kat": "Makarna", "malz": ["1 Paket Makarna", "1 Yemek Kaşığı Salça", "1 Tatlı Kaşığı Nane", "Sıvı Yağ"], "desc": "Öğrenci efsanesi.", "tar": "1. Makarnayı haşla.\n2. Yağda salça nane yak.\n3. Karıştır."},
    {"ad": "Kremalı Mantarlı Makarna", "kat": "Makarna", "malz": ["1 Paket Makarna", "1 Paket Mantar", "1 Kutu Krema"], "desc": "İtalyan işi.", "tar": "1. Mantarı sotele.\n2. Krema ekle kaynat.\n3. Makarna ile buluştur."},

    # --- TATLILAR ---
    {"ad": "Sütlaç", "kat": "Tatlı", "malz": ["1 Litre Süt", "1 Çay Bardağı Pirinç", "1 Su Bardağı Şeker", "2 Yemek Kaşığı Nişasta"], "desc": "Anne eli değmiş.", "tar": "1. Pirinci haşla sütü ekle.\n2. Şekeri ve nişastayı kat.\n3. Kıvam alınca kaselere paylaştır."},
    {"ad": "İrmik Helvası", "kat": "Tatlı", "malz": ["2 Su Bardağı İrmik", "125gr Tereyağı", "Şerbet (Sütlü/Su)"], "desc": "Kavrulmuş lezzet.", "tar": "1. İrmiği rengi dönene kadar kavur.\n2. Sıcak şerbeti dök demlenmeye bırak."},
    {"ad": "Magnolia", "kat": "Tatlı", "malz": ["1 Litre Süt", "1 Su Bardağı Şeker", "2 YK Un", "2 YK Nişasta", "1 Paket Burçak Bisküvi", "Muz veya Çilek"], "desc": "Kupta modern tatlı.", "tar": "1. Muhallebi yap.\n2. Bisküvi ve meyveyle kat kat diz."},
]

# --- AKILLI TARİF ÜRETİCİSİ ---
def tarif_uret(malzeme):
    malzeme_baslik = malzeme.title()
    return {
        "ad": f"Fırında Özel {malzeme_baslik}",
        "kat": "Şefin Spesiyali",
        "malz": [f"{malzeme_baslik}", "Zeytinyağı", "Tuz", "Karabiber", "Kekik", "İsteğe bağlı sarımsak"],
        "desc": "Bu malzeme ile yapabileceğin en garanti lezzet.",
        "tar": f"1. {malzeme_baslik} güzelce yıkanır ve doğranır.\n2. Bir kapta zeytinyağı ve baharatlarla harmanlanır.\n3. Yağlı kağıt serili tepsiye dizilir.\n4. 200 derece önceden ısıtılmış fırında kızarana kadar pişirilir.\n5. Sıcak servis yapılır. Yanına yoğurt çok yakışır!"
    }

# --- ARAMA MOTORU ---
def tarifleri_bul(girdi):
    girdi = girdi.lower()
    bulunanlar = []
    
    # 1. Önce SABİT listede ara
    for tarif in TUM_TARIFLER:
        malzeme_metni = " ".join(tarif["malz"]).lower()
        if girdi in malzeme_metni or girdi in tarif["ad"].lower():
            bulunanlar.append(tarif)

    # 2. Sonra KULLANICI (DOSYA) tariflerinde ara
    kullanici_tarifleri = tarifleri_yukle()
    for tarif in kullanici_tarifleri:
        # Eski format kontrolü
        malz_veri = tarif["malz"]
        if isinstance(malz_veri, str):
             malz_metni = malz_veri.lower()
        else:
             malz_metni = " ".join(malz_veri).lower()
             
        if girdi in malz_metni or girdi in tarif["ad"].lower():
            bulunanlar.append(tarif)
            
    # 3. Eğer hiç sonuç yoksa, OTOMATİK ÜRET
    if not bulunanlar:
        bulunanlar.append(tarif_uret(girdi))
        
    return bulunanlar

# --- ARAYÜZ ---

# --- LOGO BÖLÜMÜ (EN TEPEDE) ---
# logo.png dosyasının app.py ile aynı klasörde olduğundan emin olun!
col_logo_sol, col_logo_orta, col_logo_sag = st.columns([1, 2, 1])
with col_logo_orta:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.warning("⚠️ 'logo.png' dosyası bulunamadı! Lütfen dosyayı proje klasörüne yükleyin.")

st.title("👨‍🍳 Dolap Şefi")
st.markdown("<h4 style='text-align: center; color: #ddd; margin-top: -15px;'>Ne pişirsem derdine son!</h4>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔥 Tarif Bulucu", "🌟 Vitrin (+Tarif Ekle)"])

# ================= TAB 1: ARAMA =================
with tab1:
    if st.session_state.secilen_tarif is None:
        malzemeler = st.text_input("Dolabında ne var?", placeholder="Örn: Patates, Kıyma, Yumurta...")
        
        if st.button("🔍 Tarifleri Listele", type="primary"):
            if not malzemeler:
                st.warning("Malzeme yazmadın şefim!")
            else:
                with st.spinner("Şef arşivine bakıyor..."):
                    time.sleep(0.4)
                    st.session_state.sonuclar = tarifleri_bul(malzemeler)

        if st.session_state.sonuclar:
            sayi = len(st.session_state.sonuclar)
            st.success(f"🎉 {sayi} Tarif Bulundu!")
            
            for i, tarif in enumerate(st.session_state.sonuclar):
                col1, col2 = st.columns([3, 1])
                with col1:
                    # Kart gösterimi
                    try:
                        malz_gosterim = tarif['malz']
                        if isinstance(malz_gosterim, list):
                            ozet = ", ".join(malz_gosterim[:3]) + "..."
                        else:
                            ozet = malz_gosterim[:50] + "..."
                    except:
                        ozet = "Malzemeler tarifte..."

                    st.markdown(f"""
                    <div class="haber-kart">
                        <div style="display:flex; justify-content:space-between;">
                            <h3 style="margin:0; color:#ffcc00;">{tarif['ad']}</h3>
                            <span style="background:rgba(255,255,255,0.2); padding:2px 6px; border-radius:4px; font-size:10px;">{tarif.get('kat', 'Genel')}</span>
                        </div>
                        <p style="margin:5px 0 10px 0; color:#ddd;"><i>{tarif['desc']}</i></p>
                        <span style="font-size:12px; color:#ccc;">Malzemeler: {ozet}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.write("") 
                    st.write("")
                    if st.button("Tarife Git 👉", key=f"btn_{i}"):
                        st.session_state.secilen_tarif = tarif
                        st.rerun()

    else:
        # DETAY EKRANI
        yemek = st.session_state.secilen_tarif
        if st.button("⬅️ Listeye Dön"):
            st.session_state.secilen_tarif = None
            st.rerun()
            
        st.divider()
        st.header(f"🍽️ {yemek['ad']}")
        st.info(f"💡 {yemek['desc']}")
        
        # --- MALZEME KUTUSU (FORMAT KONTROLLÜ) ---
        malz_html = "<ul>"
        raw_malz = yemek['malz']
        
        if isinstance(raw_malz, list):
            for m in raw_malz:
                malz_html += f"<li>{m}</li>"
        else:
            # Eğer kullanıcı eski tip text girdiyse onu da düzgün göster
            for satir in raw_malz.split('\n'):
                malz_html += f"<li>{satir}</li>"
        
        malz_html += "</ul>"

        st.markdown(f"""
        <div class="malzeme-kutusu">
            <h4>🛒 Gerekli Malzemeler:</h4>
            {malz_html}
        </div>
        """, unsafe_allow_html=True)
        # --------------------------------------------------
        
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.05); padding:25px; border-radius:15px; font-size:16px; line-height:1.8;'>
            {yemek['tar']}
        </div>
        """, unsafe_allow_html=True)
        
        # Trendyol Linki (Hata korumalı)
        try:
            if isinstance(raw_malz, list):
                ana_malzeme = raw_malz[0].split(' ')[-1]
            else:
                ana_malzeme = raw_malz.split(' ')[0]
        except:
            ana_malzeme = "mutfak"

        link = f"https://www.trendyol.com/sr?q={ana_malzeme}"
        st.markdown(f"""<a href="{link}" target="_blank" class="btn-trendyol">🛒 Malzemeleri Al (Trendyol)</a>""", unsafe_allow_html=True)

# ================= TAB 2: VİTRİN & TARİF EKLEME =================
with tab2:
    st.header("🌟 Haftanın Yıldız Şefleri")

    # --- KULLANICI TARİFLERİ (DOSYADAN) ---
    kayitli_tarifler = tarifleri_yukle()
    if kayitli_tarifler:
        for k_tarif in reversed(kayitli_tarifler): # En yeniyi en üstte göster
             st.markdown(f"""
            <div class="haber-kart" style="border-left: 6px solid #28a745;">
                <h3>🆕 {k_tarif['ad']}</h3>
                <p><strong>Şef:</strong> {k_tarif['sef']}</p>
                <p><i>"{k_tarif['desc']}"</i></p>
                 <p style="font-size:12px; color:#ccc;">(Kullanıcı Tarifi)</p>
            </div>""", unsafe_allow_html=True)

    
    with st.container():
        st.markdown("""
        <div class="haber-kart">
            <h3>🍝 Berkecan'ın Makarnası</h3>
            <p>⭐️⭐️⭐️⭐️⭐️ (124 Beğeni)</p>
        </div>""", unsafe_allow_html=True)
        st.video("https://www.w3schools.com/html/mov_bbb.mp4")
    
    with st.container():
        st.markdown("""
        <div class="haber-kart">
            <h3>🥞 Ayşe Teyze'nin Krepi</h3>
            <p>⭐️⭐️⭐️⭐️ (98 Beğeni)</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    # --- YENİ ÇALIŞAN TARİF EKLEME FORMU ---
    st.subheader("Sen de Mutfağa Katıl! 👨‍🍳")
    with st.form("tarif_ekle_form"):
        sef_adi = st.text_input("Adın Soyadın (Şef Adı)")
        tarif_adi = st.text_input("Tarifin Adı (Örn: Anne Köftesi)")
        kisa_aciklama = st.text_input("Kısa Bir Slogan (Örn: Parmak yedirtir!)")
        # Basitlik olsun diye malzemeleri alt alta yazdırıp biz listeye çevireceğiz
        malzemeler_input = st.text_area("Malzemeler (Her satıra bir malzeme yaz)")
        yapilis_input = st.text_area("Nasıl Yapılır?")
        
        submitted = st.form_submit_button("🚀 Tarifi Kalıcı Olarak Kaydet")
        
        if submitted:
            if not sef_adi or not tarif_adi or not malzemeler_input:
                 st.warning("Lütfen şef adı, tarif adı ve malzemeleri gir.")
            else:
                # Malzemeleri listeye çevir (Her satır bir malzeme)
                malzeme_listesi = [m.strip() for m in malzemeler_input.split('\n') if m.strip()]

                # Yeni tarifi oluştur
                yeni_tarif = {
                    "sef": sef_adi,
                    "ad": tarif_adi,
                    "desc": kisa_aciklama,
                    "malz": malzeme_listesi, 
                    "tar": yapilis_input,
                    "kat": "Kullanıcı"
                }
                
                # DOSYAYA KAYDET
                tarifi_kaydet(yeni_tarif)
                
                st.success("Harika! Tarifin veritabanına işlendi.")
                time.sleep(1)
                st.rerun()

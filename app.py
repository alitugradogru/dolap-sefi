import streamlit as st
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Dolap Şefi", page_icon="👨‍🍳", layout="centered")

# --- HAFIZA ---
if "secilen_tarif" not in st.session_state:
    st.session_state.secilen_tarif = None

# --- TASARIM ---
st.markdown("""
<style>
.stApp { background: linear-gradient(to bottom, #0f2027, #203a43, #2c5364); color: white; }
h1 { text-align: center; color: #f27a1a; font-family: 'Arial Black', sans-serif; }
.vitrin-card { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; margin-bottom: 20px; border-left: 5px solid #f27a1a; }
/* Sadece Trendyol Butonu Kaldı */
.btn-trendyol { display: block; width: 100%; background-color: #28a745; color: white; text-align: center; padding: 15px; border-radius: 10px; font-weight: bold; text-decoration: none; margin-top: 20px; font-size: 18px; transition: 0.3s; }
.btn-trendyol:hover { background-color: #218838; transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)

# --- DEV TARİF ARŞİVİ (OFFLINE MOD) ---
def tarif_bulucu(girdi):
    girdi = girdi.lower()
    
    # İşte burası senin hazinen. En çok aranan tarifleri buraya gömdüm.
    arsiv = {
        # KAHVALTILIKLAR
        "yumurta": {"ad": "Sokak Usulü Menemen", "desc": "Soğanlı, bol domatesli, ekmek banmalık efsane.", "tar": "1. Biberleri ince ince doğra ve yağda öldür.\n2. Kabukları soyulmuş domatesleri ekle, suyunu çekene kadar pişir.\n3. Yumurtaları kır ama çok karıştırma, beyazı gözüksün.\n4. İsteğe göre kaşar rendele."},
        "tost": {"ad": "Büfe Tostu (Atom)", "desc": "Evdeki malzemelerle büfe lezzeti.", "tar": "1. Ekmeğin içine sucuk, kaşar ne varsa doldur.\n2. Dışına tereyağı ve çok az salça sür.\n3. Tost makinesinde iyice bastır."},
        "krep": {"ad": "Tam Kıvamında Krep", "desc": "İster reçelle ye, ister peynirle.", "tar": "1. 2 yumurta, 1.5 su bardağı süt, 1.5 su bardağı unu çırp.\n2. Akışkan bir hamur olsun.\n3. Kızgın tavaya kepçeyle dök, arkalı önlü pişir."},
        
        # ANA YEMEKLER
        "tavuk": {"ad": "Köri Soslu Tavuk (Dünya Mutfağı)", "desc": "Restoranlarda 300 TL vermeye son.", "tar": "1. Tavukları küp doğra, yüksek ateşte suyunu salmadan pişir.\n2. Ayrı yerde krema, köri ve karabiberi karıştır.\n3. Tavuklar pişince sosu dök, 5 dk kıvam aldır."},
        "köfte": {"ad": "Anne Köftesi", "desc": "Yanına patates kızartmasıyla klasik lezzet.", "tar": "1. Kıyma, rendelenmiş soğan, yumurta, bayat ekmek içi ve kimyonu yoğur.\n2. Şekil ver ve dinlendir.\n3. Az yağlı tavada kızart."},
        "patates": {"ad": "Fırında Baharatlı Patates (Cips Gibi)", "desc": "Yağ çekmeyen çıtır lezzet.", "tar": "1. Patatesleri elma dilim doğra.\n2. Zeytinyağı, kekik, pul biber ve tuzla harmanla.\n3. Yağlı kağıt serili tepside 200 derecede kızarana kadar pişir."},
        "makarna": {"ad": "Demleme Usulü Makarna", "desc": "Süzmek yok, lezzeti içinde kalır.", "tar": "1. Tencereye az yağ, salça ve naneyi koyup kavur.\n2. Makarnaları ekle, üzerini 1 parmak geçecek kadar sıcak su koy.\n3. Suyunu çekene kadar kapağı kapalı pişir."},
        "fasulye": {"ad": "Etli Kuru Fasulye", "desc": "Pilavın en iyi arkadaşı.", "tar": "1. Fasulyeleri akşamdan suya koy.\n2. Soğanı ve eti düdüklüde kavur, salça ekle.\n3. Fasulyeleri ve sıcak suyu ekle. Düdüklüde 25-30 dk pişir."},
        "nohut": {"ad": "Lokanta Usulü Nohut", "desc": "Kıvamlı ve lezzetli.", "tar": "1. Haşlanmış nohutun varsa işin kolay. Yoksa akşamdan ısla.\n2. Bol soğanı yağda kavur, salçasını bol koy.\n3. Et suyu veya kemik suyu varsa ekle, kısık ateşte özleşsin."},
        "patlıcan": {"ad": "Karnıyarık", "desc": "Türk mutfağının kralı.", "tar": "1. Patlıcanları alaca soy ve kızart.\n2. Ortalarını yar, kıymalı soğanlı harcı doldur.\n3. Üstüne salçalı su gezdirip fırına ver."},
        "kabak": {"ad": "Fırın Mücver", "desc": "Kızartma derdi yok, hafif ve lezzetli.", "tar": "1. Kabakları rendele, suyunu sık (Çok önemli!).\n2. Yumurta, un, dereotu, peynir ekle karıştır.\n3. Yağlanmış tepsiye dök, fırında kızarana kadar pişir."},
        "ıspanak": {"ad": "Yumurtalı Ispanak Kavurması", "desc": "Hem sağlıklı hem doyurucu.", "tar": "1. Soğanları pembeleşinceye kadar kavur.\n2. Yıkanmış ıspanakları ekle, sönene kadar çevir.\n3. Ispanakların arasında boşluk aç, yumurtaları oraya kır. Kapağı kapat."},
        
        # ÇORBALAR
        "mercimek": {"ad": "Süzme Mercimek Çorbası", "desc": "Limon sıkıp içmelik şifa.", "tar": "1. Mercimek, patates, havucu tencereye al, su ekle haşla.\n2. Sebzeler yumuşayınca blenderdan geçir.\n3. Ayrı tavada tereyağı ve toz biberi yak, üzerine dök."},
        "tarhana": {"ad": "Kış Çorbası (Tarhana)", "desc": "Anne eli değmiş gibi.", "tar": "1. Tarhanayı soğuk suda ezip aç.\n2. Tencerede salça, nane ve yağı kavur.\n3. Tarhanalı suyu ekle, kaynayana kadar karıştır."},
        
        # TATLILAR
        "süt": {"ad": "Tam Kıvamında Sütlaç", "desc": "Üzeri nar gibi kızarmış.", "tar": "1. Pirinci az suda haşla.\n2. Sütü, şekeri ekle kaynat.\n3. Nişastayı az sütle açıp tencereye ekle.\n4. Kaselere paylaştır, fırında üzerini yak."},
        "irmik": {"ad": "İrmik Helvası", "desc": "Dondurmalı servis önerilir.", "tar": "1. Tereyağında irmiği rengi dönene kadar kavur (Sabır lazım).\n2. Ayrı yerde sıcak süt ve şekeri karıştır.\n3. Şerbeti irmiğe dök (Dikkat sıçrar!), kapağı kapat demlensin."},
        "muz": {"ad": "Muzlu Magnolia", "desc": "Kupta pratik tatlı.", "tar": "1. Süt, un, şeker, nişasta ile muhallebi yap.\n2. Burçak bisküviyi robottan geçir.\n3. Kupa sırayla bisküvi, muhallebi ve muz dilimleri diz."},
        "kakao": {"ad": "Islak Kek (Brownie Tadında)", "desc": "Bol soslu, ağızda dağılan lezzet.", "tar": "1. Yumurta ve şekeri iyice çırp.\n2. Süt, yağ, kakao, un, kabartma tozu ekle.\n3. Fırından çıkınca üzerine ayırdığın kakaolu sosu dök."},
    }
    
    # AKILLI ARAMA MOTORU
    for anahtar, deger in arsiv.items():
        if anahtar in girdi:
            return deger
            
    # HİÇBİR ŞEY BULUNAMAZSA (UYDURMA MODU)
    # Burası sayesinde "Ejder Meyvesi" bile yazsa boş dönmez.
    return {
        "ad": f"Şefin Özel {girdi.title()} Tabağı",
        "desc": "Dolabındaki malzemelerle yaratıcılığını konuştur!",
        "tar": f"1. {girdi.title()} güzelce yıkanır ve hazırlanır.\n2. Bir tavada az yağ ile sotelenir.\n3. Evde varsa soğan ve baharatlarla lezzetlendirilir.\n4. Kısık ateşte pişirilip sıcak servis edilir.\n\n*Bu özel bir malzeme olduğu için doğaçlama yapmanı öneririm!*"
    }

# --- ARAYÜZ (GÖVDE) ---
st.title("👨‍🍳 Dolap Şefi")
st.caption("Yapay Zeka Destekli Sosyal Mutfak")

tab1, tab2 = st.tabs(["🔥 Tarif Bulucu", "🌟 Vitrin"])

# ================= TAB 1 =================
with tab1:
    malzemeler = st.text_input("Dolabında neler var?", placeholder="Örn: Patates, Tavuk, Süt...")
    
    if st.button("🔍 Tarif Bul", type="primary"):
        if not malzemeler:
            st.warning("Malzeme yazmadın şefim!")
        else:
            with st.spinner("Şef senin için en iyi tarifi seçiyor..."):
                time.sleep(1.0) # Yapay zeka taklidi (Havalı olsun diye)
                st.session_state.secilen_tarif = tarif_bulucu(malzemeler)
                
    if st.session_state.secilen_tarif:
        yemek = st.session_state.secilen_tarif
        st.success(f"🍽️ {yemek['ad']}")
        st.info(f"💡 {yemek['desc']}")
        
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.1); padding:20px; border-radius:10px; font-size:16px; line-height:1.6;'>
            {yemek['tar']}
        </div>
        """, unsafe_allow_html=True)
        
        # PARA KAZANMA BUTONU
        arama_terimi = malzemeler.split(',')[0]
        link_trendyol = f"https://www.trendyol.com/sr?q={arama_terimi}"
        
        st.markdown(f"""
            <a href="{link_trendyol}" target="_blank" class="btn-trendyol">
                🛒 Malzemeleri Trendyol'dan Söyle
            </a>
            <p style='text-align:center; font-size:12px; color:#aaa; margin-top:5px;'>
                *Sponsorlu Link
            </p>
        """, unsafe_allow_html=True)

# ================= TAB 2: VİTRİN =================
with tab2:
    st.header("🌟 Haftanın Yıldızları")
    # Vitrin 1
    with st.container():
        st.markdown("""
        <div class="vitrin-card">
            <h3>🍝 Berkecan'ın Makarnası</h3>
            <p><i>"Öğrenci evi usulü ama gurme lezzetinde!"</i></p>
            <p>⭐️⭐️⭐️⭐️⭐️ (124 Beğeni)</p>
        </div>""", unsafe_allow_html=True)
        st.video("https://www.w3schools.com/html/mov_bbb.mp4")
    
    # Vitrin 2
    with st.container():
        st.markdown("""
        <div class="vitrin-card">
            <h3>🥞 Ayşe Teyze'nin Krepi</h3>
            <p><i>"Torunlarım bayılıyor, içine sevgimi kattım."</i></p>
            <p>⭐️⭐️⭐️⭐️ (89 Beğeni)</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.write("Sen de tarifini yükle:")
    with st.form("upload_form"):
        st.text_input("Adın")
        st.file_uploader("Video")
        if st.form_submit_button("Gönder"):
            st.success("Tarifin alındı! Onaylandıktan sonra yayınlanacak.")
            time.sleep(2)
            st.rerun()

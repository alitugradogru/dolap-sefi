import streamlit as st
import time
import random

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Dolap Şefi", page_icon="👨‍🍳", layout="centered")

# --- HAFIZA ---
if "sonuclar" not in st.session_state:
    st.session_state.sonuclar = [] 
if "secilen_tarif" not in st.session_state:
    st.session_state.secilen_tarif = None 

# --- TASARIM (KIRMIZI TEMA) ---
st.markdown("""
<style>
.stApp { background: linear-gradient(to bottom, #8E0E00, #1F1C18); color: white; }
h1 { text-align: center; color: #ffcc00; font-family: 'Arial Black', sans-serif; text-shadow: 2px 2px 4px #000000; }
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
.malzeme-etiketi { background-color: #ffcc00; color: #000; padding: 3px 8px; border-radius: 5px; font-size: 12px; font-weight: bold; }
.btn-trendyol { display: block; width: 100%; background-color: #28a745; color: white; text-align: center; padding: 15px; border-radius: 10px; font-weight: bold; text-decoration: none; margin-top: 20px; font-size: 18px; }

</style>
""", unsafe_allow_html=True)

# --- 🔥 MEGA TARİF VERİTABANI (KATEGORİZE EDİLMİŞ) ---
TUM_TARIFLER = [
    # --- KAHVALTILIKLAR ---
    {"ad": "Efsane Menemen", "kat": "Kahvaltı", "malz": "Yumurta, Domates, Biber, Yağ", "desc": "Soğanlı mı soğansız mı? Karar senin.", "tar": "Biberleri kavur, domatesi ekle pişir, yumurtayı kır."},
    {"ad": "Sucuklu Yumurta", "kat": "Kahvaltı", "malz": "Sucuk, Yumurta, Tereyağı", "desc": "Pazar sabahı klasiği.", "tar": "Sucukları yağda çevir, yumurtaları göz göz kır."},
    {"ad": "Kaşarlı Omlet", "kat": "Kahvaltı", "malz": "Yumurta, Kaşar, Tereyağı", "desc": "Uzayan lezzet.", "tar": "Yumurtayı çırp pişir, arasına kaşar koy katla."},
    {"ad": "Patatesli Yumurta", "kat": "Kahvaltı", "malz": "Patates, Yumurta, Baharat", "desc": "Doyurucu ve pratik.", "tar": "Patatesleri küp küp kızart, üzerine yumurta kır."},
    {"ad": "Krep (Akıtma)", "kat": "Kahvaltı", "malz": "Un, Süt, Yumurta", "desc": "İster tatlı ister tuzlu.", "tar": "Akışkan hamur yap, tavada arkalı önlü pişir."},
    {"ad": "Pankek", "kat": "Kahvaltı", "malz": "Un, Süt, Yumurta, Kabartma Tozu", "desc": "Puf puf kabarır.", "tar": "Koyu kıvamlı hamur yap, tavada küçük küçük pişir."},
    {"ad": "Sigara Böreği", "kat": "Kahvaltı", "malz": "Yufka, Peynir, Maydanoz", "desc": "Çıtır çıtır.", "tar": "Yufkaları üçgen kes, peynir koy sar, kızart."},
    {"ad": "Mıhlama (Kuymak)", "kat": "Kahvaltı", "malz": "Mısır Unu, Tereyağı, Kolot Peyniri", "desc": "Karadeniz efsanesi.", "tar": "Yağda unu kavur, su ekle, peyniri eritip uzat."},
    {"ad": "Atom Tost", "kat": "Kahvaltı", "malz": "Ekmek, Sucuk, Kaşar, Yumurta", "desc": "Büfe usulü.", "tar": "Ekmeği doldur, yumurtayı içine kır, bas makineye."},
    {"ad": "Pişi", "kat": "Kahvaltı", "malz": "Un, Maya, Su, Tuz", "desc": "Hamur kızartması.", "tar": "Hamuru mayala, şekil ver, kızgın yağda kızart."},

    # --- ÇORBALAR ---
    {"ad": "Süzme Mercimek", "kat": "Çorba", "malz": "Mercimek, Patates, Havuç", "desc": "Limon sık iç.", "tar": "Sebzeleri haşla, blenderdan geçir, üzerine yağ yak."},
    {"ad": "Ezogelin Çorbası", "kat": "Çorba", "malz": "Mercimek, Bulgur, Pirinç, Salça", "desc": "Lokanta usulü.", "tar": "Bakliyatları haşla, salçalı naneli sosla birleştir."},
    {"ad": "Domates Çorbası", "kat": "Çorba", "malz": "Domates, Un, Süt, Kaşar", "desc": "Kremalı gibi yumuşak.", "tar": "Unu kavur, domatesi ekle, sütle aç, kaşarla servis et."},
    {"ad": "Yayla Çorbası", "kat": "Çorba", "malz": "Yoğurt, Pirinç, Nane, Yumurta", "desc": "Naneli ferahlık.", "tar": "Pirinci haşla, yoğurtlu terbiyeyi ılıştırıp ekle."},
    {"ad": "Tarhana Çorbası", "kat": "Çorba", "malz": "Tarhana, Salça, Nane, Sarımsak", "desc": "Şifa deposu.", "tar": "Tarhanayı suda aç, salçalı suya ekle kaynat."},
    {"ad": "Tavuk Suyu Çorba", "kat": "Çorba", "malz": "Tavuk, Şehriye, Limon", "desc": "Hasta çorbası.", "tar": "Tavuğu haşla didikle, suyuna şehriye at pişir."},
    {"ad": "Şehriye Çorbası", "kat": "Çorba", "malz": "Tel Şehriye, Domates, Biber", "desc": "Pratik ve sıcak.", "tar": "Salçalı suya şehriyeleri at, yumuşayana kadar pişir."},
    {"ad": "Mantar Çorbası", "kat": "Çorba", "malz": "Mantar, Süt/Krema, Un", "desc": "Yoğun lezzet.", "tar": "Mantarları kavur, un ve süt ekle kıvam aldır."},
    {"ad": "Brokoli Çorbası", "kat": "Çorba", "malz": "Brokoli, Patates, Süt", "desc": "Vitamin deposu.", "tar": "Sebzeleri haşla, blender yap, sütle bağla."},

    # --- SULU YEMEKLER (Tencere) ---
    {"ad": "Kuru Fasulye", "kat": "Ana Yemek", "malz": "Fasulye, Et/Sucuk, Salça", "desc": "Milli yemeğimiz.", "tar": "Akşamdan ısla, soğanla eti kavur, düdüklüde pişir."},
    {"ad": "Nohut Yemeği", "kat": "Ana Yemek", "malz": "Nohut, Et, Salça", "desc": "Pilavın ekürisi.", "tar": "Eti kavur, haşlanmış nohutu ekle, özleşene kadar pişir."},
    {"ad": "Taze Fasulye", "kat": "Ana Yemek", "malz": "Fasulye, Domates, Soğan, Zeytinyağı", "desc": "Yazın vazgeçilmezi.", "tar": "Soğanı kavur, fasulyeyi ekle, domatesle kısık ateşte pişir."},
    {"ad": "Karnıyarık", "kat": "Ana Yemek", "malz": "Patlıcan, Kıyma, Biber", "desc": "Patlıcanın kralı.", "tar": "Patlıcanı kızart, içini kıymayla doldur, fırınla."},
    {"ad": "Musakka", "kat": "Ana Yemek", "malz": "Patlıcan, Kıyma, Salça", "desc": "Karnıyarığın kardeşi.", "tar": "Patlıcanı küp doğra kızart, kıymalı sosla tencerede pişir."},
    {"ad": "Türlü", "kat": "Ana Yemek", "malz": "Patlıcan, Patates, Biber, Kabak", "desc": "Sebze şöleni.", "tar": "Tüm sebzeleri doğra, et veya kıymayla tencerede pişir."},
    {"ad": "Patates Yemeği", "kat": "Ana Yemek", "malz": "Patates, Soğan, Salça", "desc": "En pratik tencere yemeği.", "tar": "Soğanı kavur, küp patatesleri ve salçalı suyu ekle."},
    {"ad": "Ispanak Yemeği", "kat": "Ana Yemek", "malz": "Ispanak, Pirinç, Soğan", "desc": "Demir deposu.", "tar": "Soğanı kavur, ıspanağı öldür, az pirinç at pişir."},
    {"ad": "Pırasa", "kat": "Ana Yemek", "malz": "Pırasa, Havuç, Pirinç, Limon", "desc": "Zeytinyağlı lezzet.", "tar": "Havuç ve pırasayı kavur, pirinç ve limonlu suyla pişir."},
    {"ad": "Bezelye Yemeği", "kat": "Ana Yemek", "malz": "Bezelye, Patates, Havuç, Kıyma", "desc": "Garnitürlü lezzet.", "tar": "Kıymayı kavur, küp sebzeleri ve bezelyeyi ekle."},

    # --- ET & TAVUK & KÖFTE ---
    {"ad": "Anne Köftesi", "kat": "Et", "malz": "Kıyma, Soğan, Ekmek, Maydanoz", "desc": "Patates kızartmasıyla.", "tar": "Yoğur, şekil ver, az yağda kızart."},
    {"ad": "İzmir Köfte", "kat": "Et", "malz": "Köfte, Patates, Domates Sos", "desc": "Fırında soslu.", "tar": "Köfte ve patatesi hafif kızart, tepsiye diz, sosla fırınla."},
    {"ad": "Tavuk Sote", "kat": "Tavuk", "malz": "Tavuk Göğsü, Biber, Domates", "desc": "Ekmek banmalık.", "tar": "Tavuğu suyunu çekene kadar pişir, sebzelerle kavur."},
    {"ad": "Köri Soslu Tavuk", "kat": "Tavuk", "malz": "Tavuk, Krema, Köri", "desc": "Dünya mutfağı.", "tar": "Tavuğu sotele, krema ve köri ekle çektir."},
    {"ad": "Fırın Tavuk", "kat": "Tavuk", "malz": "Tavuk But/Kanat, Patates", "desc": "Nar gibi kızarmış.", "tar": "Salçalı sosla harmanla, tepsiye diz fırınla."},
    {"ad": "Tavuk Şinitzel", "kat": "Tavuk", "malz": "Tavuk Göğsü, Galeta Unu, Yumurta", "desc": "Çıtır dış kaplama.", "tar": "Tavuğu una, yumurtaya, galetaya batır kızart."},
    {"ad": "Et Sote", "kat": "Et", "malz": "Kuşbaşı Et, Biber, Domates", "desc": "Yumuşacık lokum.", "tar": "Eti suyunu salıp çekene kadar pişir, sebze ekle."},
    {"ad": "Orman Kebabı", "kat": "Et", "malz": "Et, Bezelye, Patates, Havuç", "desc": "Sebzeli et yemeği.", "tar": "Eti ve sebzeleri sırayla tencerede pişir."},

    # --- MAKARNA & PİLAV ---
    {"ad": "Pirinç Pilavı", "kat": "Pilav", "malz": "Pirinç, Şehriye, Tereyağı", "desc": "Tane tane.", "tar": "Şehriyeyi kavur, pirinci kavur, 1.5 ölçü sıcak su ekle."},
    {"ad": "Bulgur Pilavı", "kat": "Pilav", "malz": "Bulgur, Salça, Soğan", "desc": "Meyhane usulü.", "tar": "Soğan salçayı kavur, bulguru ve sıcak suyu ekle."},
    {"ad": "Salçalı Makarna", "kat": "Makarna", "malz": "Makarna, Salça, Nane", "desc": "Öğrenci efsanesi.", "tar": "Makarnayı haşla, yağda salça nane yak, karıştır."},
    {"ad": "Kremalı Mantarlı Makarna", "kat": "Makarna", "malz": "Makarna, Mantar, Krema", "desc": "İtalyan işi.", "tar": "Mantarı sotele, krema ekle, makarnayla buluştur."},
    {"ad": "Fırın Makarna", "kat": "Makarna", "malz": "Makarna, Beşamel Sos, Kaşar", "desc": "Börek tadında.", "tar": "Makarnayı haşla, sosla karıştır, kaşarla fırınla."},
    {"ad": "Erişte", "kat": "Makarna", "malz": "Erişte, Tereyağı, Ceviz/Peynir", "desc": "Köy usulü.", "tar": "Erişteyi pilav gibi demleyerek pişir, üzerine ceviz dök."},
    {"ad": "Kısır", "kat": "Salata", "malz": "İnce Bulgur, Salça, Yeşillik", "desc": "Altın günlerinin yıldızı.", "tar": "Bulguru ısla, salçalı sos ve yeşillikle yoğur."},

    # --- TATLILAR ---
    {"ad": "Sütlaç", "kat": "Tatlı", "malz": "Süt, Pirinç, Şeker", "desc": "Anne eli değmiş.", "tar": "Pirinci haşla, süt şeker nişasta ekle, fırınla."},
    {"ad": "İrmik Helvası", "kat": "Tatlı", "malz": "İrmik, Tereyağı, Süt, Şeker", "desc": "Kavrulmuş lezzet.", "tar": "İrmiği rengi dönene kadar kavur, sıcak şerbeti dök."},
    {"ad": "Un Helvası", "kat": "Tatlı", "malz": "Un, Tereyağı, Şerbet", "desc": "Klasik lezzet.", "tar": "Unu kokusu çıkana kadar kavur, şerbetle bağla."},
    {"ad": "Magnolia", "kat": "Tatlı", "malz": "Süt, Bisküvi, Muz/Çilek", "desc": "Kupta modern tatlı.", "tar": "Muhallebi yap, bisküvi ve meyveyle kat kat diz."},
    {"ad": "Islak Kek", "kat": "Tatlı", "malz": "Kakao, Yumurta, Un, Süt", "desc": "Bol soslu brownie.", "tar": "Keki pişir, üzerine sıcak kakaolu sosu dök."},
    {"ad": "Revani", "kat": "Tatlı", "malz": "İrmik, Yumurta, Un, Şerbet", "desc": "Şerbetli sünger tatlı.", "tar": "Keki pişir, sıcak şerbete soğuk dök."},
    {"ad": "Şekerpare", "kat": "Tatlı", "malz": "Un, İrmik, Tereyağı, Şerbet", "desc": "Kıyır kıyır.", "tar": "Hamur yap fırınla, şerbetle buluştur."},
    {"ad": "Puding (Ev Yapımı)", "kat": "Tatlı", "malz": "Süt, Kakao, Un, Şeker", "desc": "Hazırdan farksız.", "tar": "Tüm malzemeleri tencerede koyulaşana kadar karıştır."},
    {"ad": "Mozaik Pasta", "kat": "Tatlı", "malz": "Bisküvi, Kakao, Yağ", "desc": "Pişmeyen pasta.", "tar": "Sosu yap, kırık bisküviyle karıştır, dondurucuya at."},
]

# --- AKILLI TARİF ÜRETİCİSİ (LİSTEDE YOKSA UYDURUR) ---
def tarif_uret(malzeme):
    malzeme = malzeme.title()
    # Eğer malzeme listede yoksa, jenerik bir tarif döndür
    return {
        "ad": f"Fırında Özel {malzeme}",
        "kat": "Şefin Spesiyali",
        "malz": f"{malzeme}, Zeytinyağı, Kekik, Tuz",
        "desc": "Bu malzeme ile yapabileceğin en garanti lezzet.",
        "tar": f"1. {malzeme} güzelce yıkanır ve doğranır.\n2. Zeytinyağı ve baharatlarla harmanlanır.\n3. 200 derece fırında kızarana kadar pişirilir.\n4. Yoğurt sos ile servis edilir."
    }

# --- ARAMA MOTORU ---
def tarifleri_bul(girdi):
    girdi = girdi.lower()
    bulunanlar = []
    
    # 1. Önce listede ara
    for tarif in TUM_TARIFLER:
        if girdi in tarif["malz"].lower() or girdi in tarif["ad"].lower():
            bulunanlar.append(tarif)
            
    # 2. Eğer hiç sonuç yoksa, OTOMATİK ÜRET
    if not bulunanlar:
        bulunanlar.append(tarif_uret(girdi))
        
    return bulunanlar

# --- ARAYÜZ ---
c1, c2, c3, c4 = st.columns(4)
with c1: st.image("https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=300", use_container_width=True) 
with c2: st.image("https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=300", use_container_width=True) 
with c3: st.image("https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=300", use_container_width=True) 
with c4: st.image("https://images.unsplash.com/photo-1482049016688-2d3e1b311543?w=300", use_container_width=True) 

st.title("👨‍🍳 Dolap Şefi")
st.markdown("<h4 style='text-align: center; color: #ddd;'>Ne pişirsem derdine son!</h4>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔥 Tarif Bulucu", "🌟 Vitrin"])

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
                    st.markdown(f"""
                    <div class="haber-kart">
                        <div style="display:flex; justify-content:space-between;">
                            <h3 style="margin:0; color:#ffcc00;">{tarif['ad']}</h3>
                            <span style="background:rgba(255,255,255,0.2); padding:2px 6px; border-radius:4px; font-size:10px;">{tarif['kat']}</span>
                        </div>
                        <p style="margin:5px 0 10px 0; color:#ddd;"><i>{tarif['desc']}</i></p>
                        <span class="malzeme-etiketi">{tarif['malz']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.write("") 
                    st.write("")
                    if st.button("Tarife Git 👉", key=f"btn_{i}"):
                        st.session_state.secilen_tarif = tarif
                        st.rerun()

    else:
        yemek = st.session_state.secilen_tarif
        if st.button("⬅️ Listeye Dön"):
            st.session_state.secilen_tarif = None
            st.rerun()
            
        st.divider()
        st.header(f"🍽️ {yemek['ad']}")
        st.info(f"💡 {yemek['desc']}")
        st.warning(f"🛒 **Gerekli Malzemeler:** {yemek['malz']}")
        
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.05); padding:25px; border-radius:15px; font-size:16px; line-height:1.8;'>
            {yemek['tar']}
        </div>
        """, unsafe_allow_html=True)
        
        # HATA BURADAYDI, DÜZELTİLDİ:
        # Artık 'malzemeler' değişkenini değil, seçilen yemeğin ilk malzemesini kullanıyoruz.
        ana_malzeme = yemek['malz'].split(',')[0]
        link = f"https://www.trendyol.com/sr?q={ana_malzeme}"
        
        st.markdown(f"""<a href="{link}" target="_blank" class="btn-trendyol">🛒 Malzemeleri Al (Trendyol)</a>""", unsafe_allow_html=True)

with tab2:
    st.header("🌟 Haftanın Yıldız Şefleri")
    
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
    st.write("Sen de tarifini yükle:")
    with st.form("upload"):
        st.text_input("Adın")
        st.file_uploader("Video")
        if st.form_submit_button("Yükle"):
            st.success("Tarifin gönderildi!")
            time.sleep(2)
            st.rerun()

st.markdown("---")
col_a, col_b, col_c, col_d = st.columns(4)
with col_a: st.markdown("""<div class="feature-box"><span class="feature-icon">⚡</span><div class="feature-text">Hızlı</div></div>""", unsafe_allow_html=True)
with col_b: st.markdown("""<div class="feature-box"><span class="feature-icon">🍃</span><div class="feature-text">Taze</div></div>""", unsafe_allow_html=True)
with col_c: st.markdown("""<div class="feature-box"><span class="feature-icon">👨‍🍳</span><div class="feature-text">Lezzetli</div></div>""", unsafe_allow_html=True)
with col_d: st.markdown("""<div class="feature-box"><span class="feature-icon">🔥</span><div class="feature-text">Sıcak</div></div>""", unsafe_allow_html=True)

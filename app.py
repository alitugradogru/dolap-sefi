import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dolap Şefi", page_icon="🍳", layout="wide")

# --- BAŞLIK ---
st.title("🍳 Dolap Şefi v2.0")
st.markdown("**Akıllı Mutfak Asistanın: Malzemeni Seç, Tarifini Bul!**")
st.info("💡 İpucu: Listede olmayan bir yemeği eklemek için GitHub'daki 'menu.csv' dosyasını düzenlemen yeterli!")

# --- VERİ TABANI BAĞLANTISI ---
try:
    # CSV dosyasını noktalı virgül ile okuyoruz
    df = pd.read_csv("menu.csv", sep=";")
except Exception as e:
    st.error(f"Veri tabanı okunamadı! Hata: {e}")
    st.stop()

# --- ARAYÜZ (SIDEBAR) ---
with st.sidebar:
    st.header("🛒 Mutfak Durumu")
    
    # Tüm malzemeleri dinamik olarak bulalım
    tum_malzemeler = set()
    for item in df['Malzemeler']:
        # Virgülle ayrılan malzemeleri tek tek listeye ekle
        malzemeler = [x.strip() for x in item.split(',')]
        tum_malzemeler.update(malzemeler)
    
    secilenler = st.multiselect('Dolabında Neler Var?', sorted(list(tum_malzemeler)))
    
    st.markdown("---")
    butce_modu = st.checkbox("💸 Öğrenci İşi (Ucuz Tarifler)")
    
    st.markdown("---")
    st.caption("Geliştirici: @alitugradogru")

# --- MANTIK MOTORU ---
if st.button('🔎 Tarifleri Getir', type="primary"):
    if not secilenler:
        st.warning("Lütfen dolaptan en az bir malzeme seç!")
    else:
        # Eşleşenleri bul
        eslesenler = []
        for index, row in df.iterrows():
            gerekli = set([x.strip() for x in row['Malzemeler'].split(',')])
            elimdeki = set(secilenler)
            
            # Eğer seçilen malzemelerden EN AZ BİRİ yemekte varsa göster (Esnek Arama)
            if gerekli.intersection(elimdeki):
                eslesenler.append(row)
        
        if eslesenler:
            st.success(f"Senin için {len(eslesenler)} lezzetli tarif buldum!")
            
            cols = st.columns(2)
            for i, yemek in enumerate(eslesenler):
                # Bütçe filtresi (Maliyet sütunu varsa)
                if butce_modu and yemek['Maliyet'] > 30:
                    continue

                col = cols[i % 2]
                with col:
                    # Resim yüklenmezse hata vermesin diye kontrol
                    try:
                        st.image(yemek['Resim'], use_container_width=True)
                    except:
                        st.warning("Resim yüklenemedi")
                        
                    st.subheader(yemek['Yemek Adı'])
                    st.write(f"⏱ **{yemek['Zorluk']}** | 🔥 **{yemek['Kalori']} kcal** | 💰 **{yemek['Maliyet']} TL**")
                    st.write(f"📝 **Malzemeler:** {yemek['Malzemeler']}")
                    
                    # Satış Butonu
                    link = yemek['Link']
                    st.markdown(f"""
                        <a href="{link}" target="_blank">
                            <button style="width:100%; background-color:#f27a1a; color:white; border:none; padding:10px; border-radius:8px; font-weight:bold; cursor:pointer; margin-top:5px;">
                            🛒 Eksik Malzemeleri Sipariş Et
                            </button>
                        </a>
                    """, unsafe_allow_html=True)
                    st.markdown("---")
        else:
            st.error("Bu malzemelerle eşleşen tarif bulunamadı. Başka malzeme eklemeyi dene! 🥕")

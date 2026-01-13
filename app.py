import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Dolap Şefi", page_icon="🍳", layout="wide")

# --- BAŞLIK ---
st.title("🍳 Dolap Şefi: Masterchef Modu")
st.markdown("**Akıllı Mutfak Asistanın: Malzemeni Seç, Tarifini Bul!**")

# --- VERİ TABANI ---
try:
    # CSV dosyasını okuyoruz
    df = pd.read_csv("menu.csv", sep=";")
except Exception as e:
    st.error(f"Veri tabanı okunamadı! Hata: {e}")
    st.stop()

# --- ARAYÜZ ---
with st.sidebar:
    st.header("🛒 Mutfak Durumu")
    tum_malzemeler = set()
    for item in df['Malzemeler']:
        malzemeler = [x.strip() for x in item.split(',')]
        tum_malzemeler.update(malzemeler)
    
    secilenler = st.multiselect('Dolabında Neler Var?', sorted(list(tum_malzemeler)))
    st.markdown("---")
    butce_modu = st.checkbox("💸 Öğrenci İşi (Ucuz Tarifler)")

# --- MANTIK MOTORU ---
if st.button('🔎 Tarifleri Getir', type="primary"):
    if not secilenler:
        st.warning("Lütfen dolaptan en az bir malzeme seç!")
    else:
        eslesenler = []
        for index, row in df.iterrows():
            gerekli = set([x.strip() for x in row['Malzemeler'].split(',')])
            elimdeki = set(secilenler)
            if gerekli.intersection(elimdeki):
                eslesenler.append(row)
        
        if eslesenler:
            st.success(f"Senin için {len(eslesenler)} tarif buldum!")
            cols = st.columns(2)
            
            for i, yemek in enumerate(eslesenler):
                if butce_modu and yemek['Maliyet'] > 30: continue

                col = cols[i % 2]
                with col:
                    # --- RESİM YÖNETİMİ (ÖNEMLİ GÜNCELLEME) ---
                    resim_yolu = yemek['Resim']
                    
                    # Eğer link "http" ile başlıyorsa internetten çek, başlamıyorsa GitHub klasöründen al
                    if resim_yolu.startswith("http"):
                        st.image(resim_yolu, use_container_width=True)
                    else:
                        # Yerel dosya kontrolü
                        if os.path.exists(resim_yolu):
                            st.image(resim_yolu, use_container_width=True)
                        else:
                            st.warning(f"Resim bulunamadı: {resim_yolu}")

                    st.subheader(yemek['Yemek Adı'])
                    st.write(f"⏱ **{yemek['Zorluk']}** | 🔥 **{yemek['Kalori']} kcal** | 💰 **{yemek['Maliyet']} TL**")
                    st.write(f"📝 **Malzemeler:** {yemek['Malzemeler']}")
                    
                    # --- TARİF DETAYI (YENİ) ---
                    # CSV'de 'Tarif' sütunu varsa göster, yoksa uyarı verme
                    if 'Tarif' in yemek and pd.notna(yemek['Tarif']):
                        with st.expander("👨‍🍳 Nasıl Yapılır? (Tarifi Gör)"):
                            st.write(yemek['Tarif'])
                    
                    # Satış Linki
                    st.markdown(f"""
                        <a href="{yemek['Link']}" target="_blank">
                            <button style="width:100%; background-color:#f27a1a; color:white; border:none; padding:8px; border-radius:5px; font-weight:bold; cursor:pointer; margin-top:5px;">
                            🛒 Eksik Malzemeleri Sipariş Et
                            </button>
                        </a>
                    """, unsafe_allow_html=True)
                    st.markdown("---")
        else:
            st.error("Eşleşen tarif bulunamadı.")

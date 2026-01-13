import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dolap Şefi", page_icon="🍳", layout="wide")

# --- VERİ VE SATIŞ LİNKLERİ ---
data = {
    "Yemek Adı": ["Efsane Menemen", "Patatesli Omlet", "Köri Soslu Tavuk"],
    "Malzemeler": [
        ["Yumurta", "Domates", "Soğan", "Biber"],
        ["Patates", "Yumurta", "Kaşar"],
        ["Tavuk", "Kremsi Sos", "Soğan"]
    ],
    "Resim": [
        "https://cdn.yemek.com/mnresize/1250/833/uploads/2021/03/menemen-yemekcom.jpg",
        "https://cdn.yemek.com/mnresize/1250/833/uploads/2022/05/patatesli-omlet-one-cikan.jpg",
        "https://cdn.yemek.com/mnresize/1250/833/uploads/2020/12/kori-soslu-tavuk-sote-tarifi.jpg"
    ],
    # Burası senin para kazanacağın linkler (Şimdilik Trendyol aramasına gidiyor)
    "Satin_Alma_Linki": [
        "https://www.trendyol.com/sr?q=menemenlik&qt=menemenlik&st=menemenlik&os=1",
        "https://www.trendyol.com/sr?q=yumurta&qt=yumurta&st=yumurta&os=1",
        "https://www.trendyol.com/sr?q=tavuk&qt=tavuk&st=tavuk&os=1"
    ]
}

df = pd.DataFrame(data)

st.title("🍳 Dolap Şefi: Bugün Ne Pişirsem?")
st.info("💡 İpucu: Bu uygulama ile yemek yaparken para da kazandırabilirsin!")

# --- ARAYÜZ ---
tum_malzemeler = ['Yumurta', 'Domates', 'Soğan', 'Patates', 'Kaşar', 'Tavuk', 'Biber']
secilenler = st.multiselect('Dolabında Neler Var?', tum_malzemeler)

if st.button('🔎 Tarifleri Getir'):
    if not secilenler:
        st.warning("Lütfen malzeme seç!")
    else:
        st.success("İşte yapabileceğin yemekler:")
        
        cols = st.columns(2)
        
        # Sadece ilk 3 tarifi gösteriyoruz örnek olarak
        for index, row in df.iterrows():
            col = cols[index % 2]
            with col:
                st.image(row['Resim'], use_container_width=True)
                st.subheader(row['Yemek Adı'])
                st.write(f"Malzemeler: {', '.join(row['Malzemeler'])}")
                
                # İŞTE PARA KAZANDIRAN BUTON BURASI 👇
                st.markdown(f"""
                    <a href="{row['Satin_Alma_Linki']}" target="_blank">
                        <button style="
                            width: 100%;
                            background-color: #f27a1a; 
                            color: white; 
                            border: none; 
                            padding: 10px; 
                            border-radius: 5px; 
                            cursor: pointer;
                            font-weight: bold;">
                            🛒 Eksik Malzemeleri Sipariş Et
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
                st.caption("Bu butona tıklanırsa komisyon kazanırsın.")
                st.markdown("---")

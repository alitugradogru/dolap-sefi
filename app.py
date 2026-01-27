import streamlit as st
import time
import json
import os
from datetime import datetime
import random

# --- 1. AYARLAR ---
st.set_page_config(page_title="Dolap Şefi: Sınırsız", page_icon="👨‍🍳", layout="wide", initial_sidebar_state="expanded")

# --- 2. DOSYA İSİMLERİ ---
TARIF_DB = "tarifler.json"          # Ana dev veritabanı
USER_DB = "kullanici_tarifleri.json" # Kullanıcıların ekledikleri
YORUM_DB = "yorumlar.json"
USER_AUTH = "kullanicilar.json"
FAV_DB = "favoriler.json"

# --- 3. DEVASA BAŞLANGIÇ VERİTABANI (OTOMATİK OLUŞACAK) ---
# Şefim, buraya aklına gelebilecek HER ŞEYİ koydum.
DEV_MENU = [
    # --- KAHVALTI ---
    {"ad": "Trabzon Kuymak", "kat": "Kahvaltı", "malz": ["Mısır Unu", "Tereyağı", "Çeçil Peyniri", "Su"], "tar": "Tereyağını erit, unu kavur. Suyu ekle pişir, peyniri ekle.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Menemen", "kat": "Kahvaltı", "malz": ["Yumurta", "Domates", "Biber", "Yağ"], "tar": "Biberi kavur, domatesi ekle sos yap, yumurtayı kır.", "sure": "15 dk", "zorluk": "Kolay"},
    {"ad": "Sucuklu Yumurta", "kat": "Kahvaltı", "malz": ["Sucuk", "Yumurta", "Tereyağı"], "tar": "Sucuğu pişir, yumurtayı kır.", "sure": "10 dk", "zorluk": "Kolay"},
    {"ad": "Pankek", "kat": "Kahvaltı", "malz": ["Un", "Süt", "Yumurta", "Kabartma Tozu", "Şeker"], "tar": "Çırp, tavada arkalı önlü pişir.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Pişi", "kat": "Kahvaltı", "malz": ["Un", "Maya", "Tuz", "Su", "Yağ"], "tar": "Hamuru mayala, kızgın yağda kızart.", "sure": "45 dk", "zorluk": "Orta"},
    {"ad": "Çılbır", "kat": "Kahvaltı", "malz": ["Yumurta", "Yoğurt", "Sarımsak", "Tereyağı", "Pulbiber"], "tar": "Yumurtayı poşe yap, sarımsaklı yoğurt ve yağla servis et.", "sure": "15 dk", "zorluk": "Orta"},
    {"ad": "Patatesli Omlet", "kat": "Kahvaltı", "malz": ["Patates", "Yumurta", "Kaşar"], "tar": "Patatesi küp kızart, yumurtayı ekle.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Simit Pizza", "kat": "Kahvaltı", "malz": ["Simit", "Kaşar", "Sucuk", "Domates"], "tar": "Simidi böl, malzemeyi diz fırınla.", "sure": "15 dk", "zorluk": "Kolay"},
    {"ad": "Avokado Toast", "kat": "Kahvaltı", "malz": ["Avokado", "Ekmek", "Limon", "Yumurta"], "tar": "Avokadoyu ez, ekmeğe sür, yumurta koy.", "sure": "10 dk", "zorluk": "Kolay"},
    {"ad": "Yumurtalı Ekmek", "kat": "Kahvaltı", "malz": ["Bayat Ekmek", "Süt", "Yumurta"], "tar": "Ekmeği sosa bula kızart.", "sure": "10 dk", "zorluk": "Kolay"},
    {"ad": "Acuka", "kat": "Kahvaltı", "malz": ["Salça", "Ceviz", "Sarımsak", "Baharat"], "tar": "Hepsini robottan geçir.", "sure": "5 dk", "zorluk": "Kolay"},
    {"ad": "Sigara Böreği", "kat": "Kahvaltı", "malz": ["Yufka", "Lor Peyniri", "Maydanoz"], "tar": "Sar ve kızart.", "sure": "25 dk", "zorluk": "Orta"},
    {"ad": "Hellim Kızartma", "kat": "Kahvaltı", "malz": ["Hellim Peyniri", "Tereyağı"], "tar": "Tavada iz vererek pişir.", "sure": "5 dk", "zorluk": "Kolay"},
    {"ad": "Bazlama Tost", "kat": "Kahvaltı", "malz": ["Bazlama", "Sucuk", "Kaşar", "Salça"], "tar": "Salçayı sür, malzemeyi koy bas.", "sure": "10 dk", "zorluk": "Kolay"},
    {"ad": "Soğanlı Yumurta", "kat": "Kahvaltı", "malz": ["Bol Soğan", "Yumurta", "Tereyağı", "Karabiber"], "tar": "Soğanı karamelize et, yumurtayı kır.", "sure": "25 dk", "zorluk": "Orta"},
    
    # --- ÇORBALAR ---
    {"ad": "Süzme Mercimek", "kat": "Çorba", "malz": ["Mercimek", "Havuç", "Patates", "Soğan"], "tar": "Haşla, blenderdan geçir, yağ yak.", "sure": "30 dk", "zorluk": "Kolay"},
    {"ad": "Yayla Çorbası", "kat": "Çorba", "malz": ["Yoğurt", "Pirinç", "Yumurta", "Nane"], "tar": "Pirinç haşla, terbiyeyi ekle, nane yak.", "sure": "30 dk", "zorluk": "Orta"},
    {"ad": "Ezogelin", "kat": "Çorba", "malz": ["Mercimek", "Bulgur", "Pirinç", "Salça"], "tar": "Bakliyatları pişir, soğanlı sos yap.", "sure": "40 dk", "zorluk": "Orta"},
    {"ad": "Domates Çorbası", "kat": "Çorba", "malz": ["Domates", "Un", "Süt", "Kaşar"], "tar": "Unu kavur, domatesi ekle, sütle aç.", "sure": "25 dk", "zorluk": "Kolay"},
    {"ad": "Tarhana", "kat": "Çorba", "malz": ["Tarhana", "Kıyma", "Sarımsak", "Salça"], "tar": "Tarhanayı ıslat, salçalı suya ekle.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Tavuk Suyu", "kat": "Çorba", "malz": ["Tavuk", "Tel Şehriye", "Limon"], "tar": "Tavuğu haşla, suyuna şehriye at.", "sure": "40 dk", "zorluk": "Kolay"},
    {"ad": "Mantar Çorbası", "kat": "Çorba", "malz": ["Mantar", "Krema", "Un", "Süt"], "tar": "Mantarı kavur, unla çevir, süt ekle.", "sure": "25 dk", "zorluk": "Orta"},
    {"ad": "Brokoli Çorbası", "kat": "Çorba", "malz": ["Brokoli", "Süt", "Krema", "Patates"], "tar": "Haşla, blender yap, krema ekle.", "sure": "30 dk", "zorluk": "Kolay"},
    {"ad": "İşkembe (Yalancı)", "kat": "Çorba", "malz": ["Tavuk Göğsü", "Yoğurt", "Sarımsak", "Sirke"], "tar": "Tavuğu didikle, terbiyeli su yap.", "sure": "45 dk", "zorluk": "Orta"},
    {"ad": "Kabak Çorbası", "kat": "Çorba", "malz": ["Kabak", "Dereotu", "Süt"], "tar": "Kabağı haşla ez, sütle bağla.", "sure": "25 dk", "zorluk": "Kolay"},

    # --- ANA YEMEKLER ---
    {"ad": "Kuru Fasulye", "kat": "Ana Yemek", "malz": ["Fasulye", "Et", "Salça", "Soğan"], "tar": "Akşamdan ısla, etle düdüklüde pişir.", "sure": "50 dk", "zorluk": "Orta"},
    {"ad": "Karnıyarık", "kat": "Ana Yemek", "malz": ["Patlıcan", "Kıyma", "Biber", "Domates"], "tar": "Patlıcanı kızart, kıymayı doldur, fırınla.", "sure": "60 dk", "zorluk": "Zor"},
    {"ad": "İzmir Köfte", "kat": "Ana Yemek", "malz": ["Kıyma", "Patates", "Domates Sos"], "tar": "Köfte patatesi kızart, sosla fırınla.", "sure": "50 dk", "zorluk": "Orta"},
    {"ad": "Hünkar Beğendi", "kat": "Ana Yemek", "malz": ["Kuşbaşı Et", "Patlıcan", "Beşamel Sos", "Kaşar"], "tar": "Beğendiyi yap, üstüne et sote koy.", "sure": "60 dk", "zorluk": "Zor"},
    {"ad": "Tavuk Sote", "kat": "Ana Yemek", "malz": ["Tavuk", "Biber", "Domates", "Soğan"], "tar": "Tavuğu mühürle, sebzeleri ekle.", "sure": "25 dk", "zorluk": "Kolay"},
    {"ad": "Fırında Tavuk Patates", "kat": "Ana Yemek", "malz": ["Tavuk But", "Patates", "Salçalı Sos"], "tar": "Sosla harmanla, fırına at.", "sure": "50 dk", "zorluk": "Kolay"},
    {"ad": "Mantı", "kat": "Ana Yemek", "malz": ["Un", "Kıyma", "Yoğurt", "Salça"], "tar": "Hamuru aç doldur, haşla.", "sure": "90 dk", "zorluk": "Zor"},
    {"ad": "Biber Dolması", "kat": "Ana Yemek", "malz": ["Dolmalık Biber", "Pirinç", "Kıyma", "Nane"], "tar": "İçi hazırla doldur, tencerede pişir.", "sure": "45 dk", "zorluk": "Orta"},
    {"ad": "Tas Kebabı", "kat": "Ana Yemek", "malz": ["Kuşbaşı", "Patates", "Havuç"], "tar": "Eti pişir, sebzeleri ekle.", "sure": "60 dk", "zorluk": "Orta"},
    {"ad": "Orman Kebabı", "kat": "Ana Yemek", "malz": ["Et", "Bezelye", "Havuç", "Patates"], "tar": "Eti ve sebzeleri tencerede buluştur.", "sure": "50 dk", "zorluk": "Orta"},
    {"ad": "Musakka", "kat": "Ana Yemek", "malz": ["Patlıcan", "Kıyma", "Domates"], "tar": "Patlıcanı küp kızart, kıymayla pişir.", "sure": "45 dk", "zorluk": "Orta"},
    {"ad": "Ali Nazik", "kat": "Ana Yemek", "malz": ["Kıyma", "Süzme Yoğurt", "Patlıcan"], "tar": "Köz patlıcanlı yoğurt üstüne kıyma.", "sure": "40 dk", "zorluk": "Orta"},
    {"ad": "Ciğer Tava", "kat": "Ana Yemek", "malz": ["Ciğer", "Un", "Kızartma Yağı"], "tar": "Ciğeri unla, kızgın yağda 2 dk pişir.", "sure": "15 dk", "zorluk": "Orta"},
    {"ad": "Saç Kavurma", "kat": "Ana Yemek", "malz": ["Et", "Kuyruk Yağı", "Biber", "Domates"], "tar": "Saçta yüksek ateşte çevir.", "sure": "30 dk", "zorluk": "Orta"},
    {"ad": "Şinitzel", "kat": "Ana Yemek", "malz": ["Tavuk Göğsü", "Galeta Unu", "Yumurta"], "tar": "Tavuğu incelt, panele, kızart.", "sure": "20 dk", "zorluk": "Orta"},
    
    # --- MAKARNA & PİLAV ---
    {"ad": "Pirinç Pilavı", "kat": "Makarna", "malz": ["Pirinç", "Tereyağı", "Şehriye"], "tar": "Şehriyeyi kavur, pirinci ekle, demle.", "sure": "25 dk", "zorluk": "Orta"},
    {"ad": "Bulgur Pilavı", "kat": "Makarna", "malz": ["Bulgur", "Salça", "Domates", "Biber"], "tar": "Sebzeleri kavur, bulguru ekle.", "sure": "25 dk", "zorluk": "Kolay"},
    {"ad": "Kremalı Mantarlı Makarna", "kat": "Makarna", "malz": ["Makarna", "Mantar", "Krema", "Fesleğen"], "tar": "Mantarı sotele, krema ekle, makarna ile karıştır.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Spagetti Bolonez", "kat": "Makarna", "malz": ["Spagetti", "Kıyma", "Domates Sos", "Havuç"], "tar": "Kıymalı sos yap, makarnanın üstüne dök.", "sure": "30 dk", "zorluk": "Orta"},
    {"ad": "Fırın Makarna", "kat": "Makarna", "malz": ["Kalın Makarna", "Beşamel Sos", "Kaşar", "Peynir"], "tar": "Makarnayı beşamel ile karıştır fırınla.", "sure": "45 dk", "zorluk": "Orta"},
    {"ad": "Noodle (Ev Usulü)", "kat": "Makarna", "malz": ["Erişte", "Soya Sosu", "Lahana", "Havuç"], "tar": "Sebzeleri wok tavada çevir, erişteyi ekle.", "sure": "15 dk", "zorluk": "Kolay"},
    {"ad": "Penne Arabiata", "kat": "Makarna", "malz": ["Penne", "Acı Biber", "Domates", "Sarımsak"], "tar": "Acılı domates sosu yap.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Perde Pilavı", "kat": "Makarna", "malz": ["Pirinç", "Yufka", "Tavuk", "Badem", "Kuş Üzümü"], "tar": "Yufkanın içine pilavı doldur fırınla.", "sure": "90 dk", "zorluk": "Zor"},
    {"ad": "Lazanya", "kat": "Makarna", "malz": ["Lazanya Yaprağı", "Kıyma", "Beşamel", "Kaşar"], "tar": "Kat kat diz fırınla.", "sure": "60 dk", "zorluk": "Zor"},
    {"ad": "Kuskus", "kat": "Makarna", "malz": ["Kuskus", "Salça", "Sebze"], "tar": "Makarna gibi haşla veya pilav gibi demle.", "sure": "20 dk", "zorluk": "Kolay"},

    # --- SEBZELİ ---
    {"ad": "Zeytinyağlı Fasulye", "kat": "Sebzeli", "malz": ["Taze Fasulye", "Domates", "Soğan", "Şeker"], "tar": "Kendi suyunda kısık ateşte pişir.", "sure": "50 dk", "zorluk": "Kolay"},
    {"ad": "İmam Bayıldı", "kat": "Sebzeli", "malz": ["Patlıcan", "Bol Soğan", "Sarımsak", "Zeytinyağı"], "tar": "Patlıcanı kızart, soğanlı harçla doldur.", "sure": "50 dk", "zorluk": "Orta"},
    {"ad": "Mücver", "kat": "Sebzeli", "malz": ["Kabak", "Yumurta", "Un", "Dereotu", "Peynir"], "tar": "Rendele, sık, karıştır, kızart.", "sure": "30 dk", "zorluk": "Orta"},
    {"ad": "Ispanak Yemeği", "kat": "Sebzeli", "malz": ["Ispanak", "Pirinç", "Salça", "Yoğurt"], "tar": "Soğanla kavur, pirinç at.", "sure": "30 dk", "zorluk": "Kolay"},
    {"ad": "Şakşuka", "kat": "Sebzeli", "malz": ["Patlıcan", "Biber", "Kabak", "Domates Sos"], "tar": "Küp kızart, sosla.", "sure": "30 dk", "zorluk": "Kolay"},
    {"ad": "Zeytinyağlı Enginar", "kat": "Sebzeli", "malz": ["Enginar", "Bezelye", "Havuç", "Patates"], "tar": "Garnitürü çanağa koy pişir.", "sure": "40 dk", "zorluk": "Orta"},
    {"ad": "Mercimek Köftesi", "kat": "Sebzeli", "malz": ["Mercimek", "İnce Bulgur", "Salça", "Yeşillik"], "tar": "Mercimeği haşla bulguru at şişsin, yoğur.", "sure": "40 dk", "zorluk": "Orta"},
    {"ad": "Karnabahar Kızartma", "kat": "Sebzeli", "malz": ["Karnabahar", "Yumurta", "Un", "Yoğurt"], "tar": "Haşla, panele, kızart.", "sure": "35 dk", "zorluk": "Orta"},
    {"ad": "Kabak Sıyırma", "kat": "Sebzeli", "malz": ["Girit Kabağı", "Limon", "Zeytinyağı", "Pirinç"], "tar": "Kabakları şerit yap, hafif pişir.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Pırasa Yemeği", "kat": "Sebzeli", "malz": ["Pırasa", "Havuç", "Pirinç", "Limon"], "tar": "Zeytinyağlı pişir.", "sure": "35 dk", "zorluk": "Kolay"},

    # --- DÜNYA MUTFAĞI & FAST FOOD ---
    {"ad": "Ev Yapımı Burger", "kat": "Dünya Mutfağı", "malz": ["Kıyma", "Burger Ekmeği", "Cheddar", "Karamelize Soğan"], "tar": "Köfteyi döküm tavada pişir.", "sure": "30 dk", "zorluk": "Orta"},
    {"ad": "Pizza", "kat": "Dünya Mutfağı", "malz": ["Un", "Maya", "Mozzarella", "Sucuk/Mantar"], "tar": "Hamuru aç, malzemeyi diz fırınla.", "sure": "60 dk", "zorluk": "Zor"},
    {"ad": "Taco", "kat": "Dünya Mutfağı", "malz": ["Tortilla", "Kıyma", "Meksika Fasulyesi", "Mısır"], "tar": "Kıymayı baharatla, ekmeğe doldur.", "sure": "25 dk", "zorluk": "Kolay"},
    {"ad": "Falafel", "kat": "Dünya Mutfağı", "malz": ["Nohut", "Maydanoz", "Sarımsak", "Kimyon"], "tar": "Robottan çek, top yap kızart.", "sure": "40 dk", "zorluk": "Orta"},
    {"ad": "Sushi (Ev)", "kat": "Dünya Mutfağı", "malz": ["Sushi Pirinci", "Nori Yosunu", "Salatalık", "Somon"], "tar": "Pirinci lapa yap, yosuna sar.", "sure": "50 dk", "zorluk": "Zor"},
    {"ad": "Quesadilla", "kat": "Dünya Mutfağı", "malz": ["Tortilla", "Tavuk", "Kaşar", "Biber"], "tar": "Lavaşa koy, ikiye katla kızart.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Mac & Cheese", "kat": "Dünya Mutfağı", "malz": ["Makarna", "Cheddar Peyniri", "Süt", "Un"], "tar": "Peynir sosu yap makarna ile karıştır.", "sure": "25 dk", "zorluk": "Kolay"},
    {"ad": "Fajita", "kat": "Dünya Mutfağı", "malz": ["Et/Tavuk", "Renkli Biberler", "Soğan"], "tar": "Jülyen doğra, yüksek ateşte sotele.", "sure": "25 dk", "zorluk": "Kolay"},

    # --- TATLILAR ---
    {"ad": "Fırın Sütlaç", "kat": "Tatlı", "malz": ["Süt", "Pirinç", "Şeker", "Nişasta"], "tar": "Güveçte fırınla.", "sure": "45 dk", "zorluk": "Orta"},
    {"ad": "Magnolia", "kat": "Tatlı", "malz": ["Süt", "Krema", "Bisküvi", "Çilek/Muz"], "tar": "Muhallebi yap, bisküviyle diz.", "sure": "30 dk", "zorluk": "Kolay"},
    {"ad": "Islak Kek", "kat": "Tatlı", "malz": ["Yumurta", "Süt", "Kakao", "Un"], "tar": "Keki pişir, sosunu dök.", "sure": "40 dk", "zorluk": "Kolay"},
    {"ad": "İrmik Helvası", "kat": "Tatlı", "malz": ["İrmik", "Tereyağı", "Süt", "Fıstık"], "tar": "Kavur, şerbetle.", "sure": "30 dk", "zorluk": "Orta"},
    {"ad": "Revani", "kat": "Tatlı", "malz": ["İrmik", "Yoğurt", "Un", "Şerbet"], "tar": "Keki pişir şerbetle.", "sure": "50 dk", "zorluk": "Orta"},
    {"ad": "Şekerpare", "kat": "Tatlı", "malz": ["Un", "Pudra Şekeri", "Tereyağı", "Şerbet"], "tar": "Kurabiye gibi yap, şerbetle.", "sure": "50 dk", "zorluk": "Orta"},
    {"ad": "Mozaik Pasta", "kat": "Tatlı", "malz": ["Petibör Bisküvi", "Kakao", "Tereyağı"], "tar": "Karıştır buzluğa at.", "sure": "15 dk", "zorluk": "Kolay"},
    {"ad": "Trileçe", "kat": "Tatlı", "malz": ["Kek", "Sütlü Sos", "Karamel"], "desc": "Balkan.", "tar": "Keki sütle ıslat karamel dök.", "sure": "60 dk", "zorluk": "Zor"},
    {"ad": "Cheesecake", "kat": "Tatlı", "malz": ["Labne", "Krema", "Bisküvi Tabani"], "tar": "Düşük ısıda uzun pişir.", "sure": "90 dk", "zorluk": "Zor"},
    {"ad": "Kabak Tatlısı", "kat": "Tatlı", "malz": ["Bal Kabağı", "Şeker", "Tahin", "Ceviz"], "tar": "Şekerle beklet pişir.", "sure": "50 dk", "zorluk": "Kolay"},
    {"ad": "Künefe (Hazır)", "kat": "Tatlı", "malz": ["Kadayıf", "Peynir", "Şerbet"], "tar": "Tavada arkalı önlü kızart.", "sure": "20 dk", "zorluk": "Orta"},
    {"ad": "Waffle (Ev)", "kat": "Tatlı", "malz": ["Waffle Hamuru", "Çikolata", "Meyve"], "tar": "Makinede pişir süsle.", "sure": "15 dk", "zorluk": "Kolay"}
]

# --- 4. FONKSİYONLAR ---
def baslangic_verisini_olustur():
    """Eğer tarif dosyası yoksa dev menüyü oluşturur."""
    if not os.path.exists(TARIF_DB):
        with open(TARIF_DB, "w", encoding="utf-8") as f:
            json.dump(DEV_MENU, f, ensure_ascii=False, indent=4)

def db_yukle(dosya):
    if os.path.exists(dosya):
        with open(dosya, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return [] if dosya == TARIF_DB or dosya == USER_DB else {}
    return [] if dosya == TARIF_DB or dosya == USER_DB else {}

def db_kaydet(dosya, veri):
    with open(dosya, "w", encoding="utf-8") as f: json.dump(veri, f, ensure_ascii=False, indent=4)

def get_image(url, kat):
    if url and "http" in url: return url
    # Kategoriye özel rastgele görsel havuzu
    pool = {
        "Kahvaltı": ["https://images.unsplash.com/photo-1533089862017-5c32417a1a08?w=500", "https://images.unsplash.com/photo-1525351484163-7529414395d8?w=500"],
        "Ana Yemek": ["https://images.unsplash.com/photo-1547592180-85f173990554?w=500", "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500"],
        "Çorba": ["https://images.unsplash.com/photo-1547592166-23acbe3b624b?w=500", "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=500"],
        "Tatlı": ["https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=500", "https://images.unsplash.com/photo-1551024601-56455205cb31?w=500"],
        "Makarna": ["https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=500", "https://images.unsplash.com/photo-1555949258-eb67b1ef0ceb?w=500"],
        "Dünya Mutfağı": ["https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=500", "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500"],
        "Sebzeli": ["https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500"]
    }
    return random.choice(pool.get(kat, ["https://images.unsplash.com/photo-1495195134817-aeb325a55b65?w=500"]))

# --- 5. BAŞLANGIÇ İŞLEMLERİ ---
baslangic_verisini_olustur() # Veritabanını oluştur

# --- 6. ARAMA MANTIĞI ---
def tarifleri_bul(girdi, kategori):
    girdi = girdi.lower()
    arananlar = [x.strip() for x in girdi.replace(",", " ").split() if x.strip()]
    
    # Ana DB + Kullanıcı DB
    tum_liste = db_yukle(TARIF_DB) + db_yukle(USER_DB)
    
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

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
.stApp { background-color: #0e1117; background-image: radial-gradient(circle at 50% 0%, #2e0000 0%, #0e1117 80%); color: #fff; font-family: 'Inter', sans-serif; }
.haber-kart { background: rgba(255,255,255,0.05); backdrop-filter: blur(10px); border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px; overflow: hidden; transition: 0.3s; }
.haber-kart:hover { transform: translateY(-5px); border-color: #ffcc00; }
.kart-resim { width: 100%; height: 180px; object-fit: cover; }
.kart-icerik { padding: 15px; }
.btn-migros { display: block; width: 100%; background: #ff7900; color: white !important; text-align: center; padding: 15px; border-radius: 12px; font-weight: bold; text-decoration: none; margin-top: 10px; }
.etiket { background: rgba(255, 204, 0, 0.2); color: #ffcc00; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-right: 5px; }
h1 { background: -webkit-linear-gradient(45deg, #FFCC00, #FF6B6B); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 4px 15px rgba(255, 69, 0, 0.4); }
</style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    if st.button("🏠 Ana Sayfa", use_container_width=True): st.session_state.page="home"; st.session_state.secilen=None; st.rerun()
    if st.button("🎲 Rastgele Yemek", use_container_width=True):
        tum = db_yukle(TARIF_DB) + db_yukle(USER_DB)
        t = random.choice(tum)
        st.session_state.secilen=t; st.session_state.page="detail"; st.rerun()
    
    st.markdown("---")
    if st.session_state.login:
        st.success(f"👤 {st.session_state.user}")
        if st.button("Profilim"): st.session_state.page="profile"; st.rerun()
        if st.button("Çıkış"): st.session_state.login=False; st.session_state.user=None; st.rerun()
    else:
        t1, t2 = st.tabs(["Giriş", "Kayıt"])
        with t1:
            k=st.text_input("Ad"); p=st.text_input("Şifre", type="password")
            if st.button("Gir"):
                u = db_yukle(USER_AUTH)
                if u.get(k)==p or (k=="admin" and p=="2026"): 
                    st.session_state.login=True; st.session_state.user=k; st.rerun()
                else: st.error("Hatalı")
        with t2:
            nk=st.text_input("Y. Ad"); np=st.text_input("Y. Şifre", type="password")
            if st.button("Kayıt"):
                u = db_yukle(USER_AUTH); u[nk]=np; db_kaydet(USER_AUTH, u); st.success("Oldu")
                
    st.markdown("---")
    kat = st.radio("Kategori:", ["Tümü", "Kahvaltı", "Çorba", "Ana Yemek", "Makarna", "Sebzeli", "Tatlı", "Dünya Mutfağı", "Kullanıcı"])

st.markdown(f'<h1 style="text-align:center;">Dolap Şefi</h1>', unsafe_allow_html=True)

# SAYFALAR
if st.session_state.page == "profile":
    st.header("👤 Profilim")
    tf, te = st.tabs(["❤️ Favoriler", "📝 Eklediklerim"])
    with tf:
        favs = db_yukle(FAV_DB).get(st.session_state.user, [])
        tum = db_yukle(TARIF_DB) + db_yukle(USER_DB)
        my_favs = [t for t in tum if t['ad'] in favs]
        for t in my_favs:
            with st.container():
                c1, c2 = st.columns([1,4])
                c1.image(get_image(t.get('img'), t.get('kat')))
                c2.subheader(t['ad']); 
                if c2.button("Git", key=f"f_{t['ad']}"): st.session_state.secilen=t; st.session_state.page="detail"; st.rerun()
            st.divider()
    with te:
        myt = [t for t in db_yukle(USER_DB) if t.get('sef') == st.session_state.user]
        for t in myt: st.write(f"- {t['ad']}")
        
elif st.session_state.page == "detail" and st.session_state.secilen:
    t = st.session_state.secilen
    st.image(get_image(t.get('img'), t.get('kat')), use_container_width=True)
    c1, c2 = st.columns([5,1])
    c1.markdown(f"<h2>{t['ad']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<span class='etiket'>⏱️ {t.get('sure','30 dk')}</span> <span class='etiket'>📊 {t.get('zorluk','Orta')}</span>", unsafe_allow_html=True)
    
    if st.session_state.login:
        favs = db_yukle(FAV_DB)
        is_fav = t['ad'] in favs.get(st.session_state.user, [])
        if c2.button("❤️" if is_fav else "🤍"):
            if st.session_state.user not in favs: favs[st.session_state.user] = []
            if is_fav: favs[st.session_state.user].remove(t['ad'])
            else: favs[st.session_state.user].append(t['ad'])
            db_kaydet(FAV_DB, favs); st.rerun()

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
                if st.form_submit_button("Yolla"):
                    d = db_yukle(YORUM_DB); 
                    if t['ad'] not in d: d[t['ad']] = []
                    d[t['ad']].insert(0, {"isim": st.session_state.user, "msg": ym}); db_kaydet(YORUM_DB, d); st.rerun()
        for y in db_yukle(YORUM_DB).get(t['ad'], []):
            st.markdown(f"<div class='yorum-kutu'><b>{y['isim']}</b>: {y['msg']}</div>", unsafe_allow_html=True)
            
else:
    t1, t2 = st.tabs(["🔍 Ara", "➕ Ekle"])
    with t1:
        ara = st.text_input("Ara...", placeholder="Patates, Tavuk...")
        res = tarifleri_bul(ara, kat)
        if res:
            st.write(f"🎉 **{len(res)}** Tarif")
            cols = st.columns(3)
            for i, t in enumerate(res):
                with cols[i%3]:
                    st.image(get_image(t.get('img'), t.get('kat')), use_container_width=True)
                    st.markdown(f"**{t['ad']}**")
                    st.markdown(f"<span style='font-size:0.8rem; color:#aaa'>⏱️ {t.get('sure','30 dk')}</span>", unsafe_allow_html=True)
                    if st.button("Git", key=f"b_{i}"): st.session_state.secilen=t; st.session_state.page="detail"; st.rerun()
        else: st.warning("Yok.")
    with t2:
        if st.session_state.login:
            with st.form("add"):
                ta=st.text_input("Ad"); ti=st.text_input("Resim"); tm=st.text_area("Malzeme"); tt=st.text_area("Tarif"); tk=st.selectbox("Kat", ["Kahvaltı", "Ana Yemek", "Tatlı", "Kullanıcı"])
                if st.form_submit_button("Ekle"):
                    u = db_yukle(USER_DB)
                    u.append({"ad": ta, "img": ti, "malz": tm.split("\n"), "tar": tt, "kat": tk, "sef": st.session_state.user, "sure": "45 dk", "zorluk": "Orta"})
                    db_kaydet(USER_DB, u); st.success("Oldu"); st.rerun()
        else: st.warning("Giriş yap.")

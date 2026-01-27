import streamlit as st
import time
import json
import os
from datetime import datetime
import random

# --- 1. AYARLAR ---
st.set_page_config(page_title="Dolap Şefi: MEGA", page_icon="👨‍🍳", layout="wide", initial_sidebar_state="expanded")

# --- 2. DOSYA İSİMLERİ (YENİ VERİTABANI İSMİ) ---
TARIF_DB = "tarifler_mega.json" # Yeni isim, sıfırdan kuracak
USER_DB = "kullanici_tarifleri.json"
YORUM_DB = "yorumlar.json"
USER_AUTH = "kullanicilar.json"
FAV_DB = "favoriler.json"

# --- 3. MEGA MENÜ (100+ TARİF) ---
DEV_MENU = [
    # --- KAHVALTI ---
    {"ad": "Trabzon Kuymak", "kat": "Kahvaltı", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Muhlama_-_Kuymak.jpg/640px-Muhlama_-_Kuymak.jpg", "malz": ["Mısır Unu", "Tereyağı", "Çeçil Peyniri", "Su"], "tar": "Tereyağını erit, unu kavur. Suyu ekle pişir, peyniri ekle.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Menemen", "kat": "Kahvaltı", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Menemen.jpg/640px-Menemen.jpg", "malz": ["Yumurta", "Domates", "Biber", "Yağ"], "tar": "Biberi kavur, domatesi ekle sos yap, yumurtayı kır.", "sure": "15 dk", "zorluk": "Kolay"},
    {"ad": "Sucuklu Yumurta", "kat": "Kahvaltı", "img": "https://images.unsplash.com/photo-1582236319830-14ef74b34b41?w=600", "malz": ["Sucuk", "Yumurta", "Tereyağı"], "tar": "Sucuğu pişir, yumurtayı kır.", "sure": "10 dk", "zorluk": "Kolay"},
    {"ad": "Pankek", "kat": "Kahvaltı", "img": "https://images.unsplash.com/photo-1506084868230-bb9d95c24759?w=600", "malz": ["Un", "Süt", "Yumurta", "Kabartma Tozu", "Şeker"], "tar": "Çırp, tavada arkalı önlü pişir.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Pişi", "kat": "Kahvaltı", "img": "https://iasbh.tmgrup.com.tr/856950/650/444/0/0/752/513?u=https://isbh.tmgrup.com.tr/sbh/2020/04/09/pisi-tarifi-mayali-ve-mayasiz-pisi-nasil-yapilir-1586427329297.jpg", "malz": ["Un", "Maya", "Tuz", "Su", "Yağ"], "tar": "Hamuru mayala, kızgın yağda kızart.", "sure": "45 dk", "zorluk": "Orta"},
    {"ad": "Çılbır", "kat": "Kahvaltı", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/%C3%87%C4%B1lb%C4%B1r.jpg/640px-%C3%87%C4%B1lb%C4%B1r.jpg", "malz": ["Yumurta", "Yoğurt", "Sarımsak", "Tereyağı", "Pulbiber"], "tar": "Yumurtayı poşe yap, sarımsaklı yoğurt ve yağla servis et.", "sure": "15 dk", "zorluk": "Orta"},
    {"ad": "Avokado Toast", "kat": "Kahvaltı", "img": "https://images.unsplash.com/photo-1588137372308-15f75323ca8d?w=600", "malz": ["Avokado", "Ekmek", "Limon", "Yumurta"], "tar": "Avokadoyu ez, ekmeğe sür, yumurta koy.", "sure": "10 dk", "zorluk": "Kolay"},
    {"ad": "Sigara Böreği", "kat": "Kahvaltı", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Sigara_b%C3%B6re%C4%9Fi_and_dips.jpg/640px-Sigara_b%C3%B6re%C4%9Fi_and_dips.jpg", "malz": ["Yufka", "Lor Peyniri", "Maydanoz"], "tar": "Sar ve kızart.", "sure": "25 dk", "zorluk": "Orta"},
    {"ad": "Patatesli Omlet", "kat": "Kahvaltı", "img": "", "malz": ["Patates", "Yumurta", "Kaşar"], "tar": "Patatesi küp kızart, yumurtayı ekle.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Simit Pizza", "kat": "Kahvaltı", "img": "", "malz": ["Simit", "Kaşar", "Sucuk", "Domates"], "tar": "Simidi böl, malzemeyi diz fırınla.", "sure": "15 dk", "zorluk": "Kolay"},
    {"ad": "Yumurtalı Ekmek", "kat": "Kahvaltı", "img": "", "malz": ["Bayat Ekmek", "Süt", "Yumurta"], "tar": "Ekmeği sosa bula kızart.", "sure": "10 dk", "zorluk": "Kolay"},
    {"ad": "Acuka", "kat": "Kahvaltı", "img": "", "malz": ["Salça", "Ceviz", "Sarımsak", "Baharat"], "tar": "Hepsini robottan geçir.", "sure": "5 dk", "zorluk": "Kolay"},
    {"ad": "Hellim Kızartma", "kat": "Kahvaltı", "img": "", "malz": ["Hellim Peyniri", "Tereyağı"], "tar": "Tavada iz vererek pişir.", "sure": "5 dk", "zorluk": "Kolay"},
    {"ad": "Bazlama Tost", "kat": "Kahvaltı", "img": "", "malz": ["Bazlama", "Sucuk", "Kaşar", "Salça"], "tar": "Salçayı sür, malzemeyi koy bas.", "sure": "10 dk", "zorluk": "Kolay"},
    {"ad": "Soğanlı Yumurta", "kat": "Kahvaltı", "img": "", "malz": ["Bol Soğan", "Yumurta", "Tereyağı", "Karabiber"], "tar": "Soğanı karamelize et, yumurtayı kır.", "sure": "25 dk", "zorluk": "Orta"},
    {"ad": "Kaşarlı Mantar", "kat": "Kahvaltı", "img": "", "malz": ["Mantar", "Kaşar", "Tereyağı"], "tar": "Mantarların içine tereyağı ve kaşar koy fırınla.", "sure": "20 dk", "zorluk": "Kolay"},
    
    # --- ÇORBALAR ---
    {"ad": "Mercimek Çorbası", "kat": "Çorba", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Mercimek_%C3%A7orbas%C4%B1.jpg/640px-Mercimek_%C3%A7orbas%C4%B1.jpg", "malz": ["Mercimek", "Havuç", "Patates", "Soğan"], "tar": "Haşla, blenderdan geçir, yağ yak.", "sure": "30 dk", "zorluk": "Kolay"},
    {"ad": "Domates Çorbası", "kat": "Çorba", "img": "https://images.unsplash.com/photo-1547592166-23acbe3b624b?w=600", "malz": ["Domates", "Un", "Süt", "Kaşar"], "tar": "Unu kavur, domatesi ekle, sütle aç.", "sure": "25 dk", "zorluk": "Kolay"},
    {"ad": "Tavuk Suyu", "kat": "Çorba", "img": "https://images.unsplash.com/photo-1574653853961-9a674e227a92?w=600", "malz": ["Tavuk", "Tel Şehriye", "Limon"], "tar": "Tavuğu haşla, suyuna şehriye at.", "sure": "40 dk", "zorluk": "Kolay"},
    {"ad": "Brokoli Çorbası", "kat": "Çorba", "img": "https://images.unsplash.com/photo-1604152135912-04a022e23696?w=600", "malz": ["Brokoli", "Süt", "Krema", "Patates"], "tar": "Haşla, blender yap, krema ekle.", "sure": "30 dk", "zorluk": "Kolay"},
    {"ad": "Yayla Çorbası", "kat": "Çorba", "img": "", "malz": ["Yoğurt", "Pirinç", "Yumurta", "Nane"], "tar": "Pirinç haşla, terbiyeyi ekle, nane yak.", "sure": "30 dk", "zorluk": "Orta"},
    {"ad": "Ezogelin", "kat": "Çorba", "img": "", "malz": ["Mercimek", "Bulgur", "Pirinç", "Salça"], "tar": "Bakliyatları pişir, soğanlı sos yap.", "sure": "40 dk", "zorluk": "Orta"},
    {"ad": "Tarhana", "kat": "Çorba", "img": "", "malz": ["Tarhana", "Kıyma", "Sarımsak", "Salça"], "tar": "Tarhanayı ıslat, salçalı suya ekle.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Mantar Çorbası", "kat": "Çorba", "img": "", "malz": ["Mantar", "Krema", "Un", "Süt"], "tar": "Mantarı kavur, unla çevir, süt ekle.", "sure": "25 dk", "zorluk": "Orta"},
    {"ad": "İşkembe (Yalancı)", "kat": "Çorba", "img": "", "malz": ["Tavuk Göğsü", "Yoğurt", "Sarımsak", "Sirke"], "tar": "Tavuğu didikle, terbiyeli su yap.", "sure": "45 dk", "zorluk": "Orta"},
    {"ad": "Kabak Çorbası", "kat": "Çorba", "img": "", "malz": ["Kabak", "Dereotu", "Süt"], "tar": "Kabağı haşla ez, sütle bağla.", "sure": "25 dk", "zorluk": "Kolay"},
    {"ad": "Şehriye Çorbası", "kat": "Çorba", "img": "", "malz": ["Tel Şehriye", "Domates", "Salça", "Maydanoz"], "tar": "Salçalı suya şehriye at, pişir.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Düğün Çorbası", "kat": "Çorba", "img": "", "malz": ["Gerdan Eti", "Yoğurt", "Yumurta", "Limon"], "tar": "Eti haşla didikle, terbiye yap.", "sure": "60 dk", "zorluk": "Zor"},

    # --- ANA YEMEKLER ---
    {"ad": "Kuru Fasulye", "kat": "Ana Yemek", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Kuru_fasulye.jpg/640px-Kuru_fasulye.jpg", "malz": ["Fasulye", "Et", "Salça", "Soğan"], "tar": "Akşamdan ısla, etle düdüklüde pişir.", "sure": "50 dk", "zorluk": "Orta"},
    {"ad": "Karnıyarık", "kat": "Ana Yemek", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Karn%C4%B1yar%C4%B1k.jpg/640px-Karn%C4%B1yar%C4%B1k.jpg", "malz": ["Patlıcan", "Kıyma", "Biber", "Domates"], "tar": "Patlıcanı kızart, kıymayı doldur, fırınla.", "sure": "60 dk", "zorluk": "Zor"},
    {"ad": "İzmir Köfte", "kat": "Ana Yemek", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Izmir_kofte.jpg/640px-Izmir_kofte.jpg", "malz": ["Kıyma", "Patates", "Domates Sos"], "tar": "Köfte patatesi kızart, sosla fırınla.", "sure": "50 dk", "zorluk": "Orta"},
    {"ad": "Tavuk Sote", "kat": "Ana Yemek", "img": "https://images.unsplash.com/photo-1604908177453-7462950a6a3b?w=600", "malz": ["Tavuk", "Biber", "Domates", "Soğan"], "tar": "Tavuğu mühürle, sebzeleri ekle.", "sure": "25 dk", "zorluk": "Kolay"},
    {"ad": "Fırında Tavuk Patates", "kat": "Ana Yemek", "img": "https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?w=600", "malz": ["Tavuk But", "Patates", "Salçalı Sos"], "tar": "Sosla harmanla, fırına at.", "sure": "50 dk", "zorluk": "Kolay"},
    {"ad": "Mantı", "kat": "Ana Yemek", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Manti.jpg/640px-Manti.jpg", "malz": ["Un", "Kıyma", "Yoğurt", "Salça"], "tar": "Hamuru aç doldur, haşla.", "sure": "90 dk", "zorluk": "Zor"},
    {"ad": "Biber Dolması", "kat": "Ana Yemek", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Biber_dolmas%C4%B1.jpg/640px-Biber_dolmas%C4%B1.jpg", "malz": ["Dolmalık Biber", "Pirinç", "Kıyma", "Nane"], "tar": "İçi hazırla doldur, tencerede pişir.", "sure": "45 dk", "zorluk": "Orta"},
    {"ad": "Şinitzel", "kat": "Ana Yemek", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Breitenlesau_Krug_Br%C3%A4u_Schnitzel.JPG/640px-Breitenlesau_Krug_Br%C3%A4u_Schnitzel.JPG", "malz": ["Tavuk Göğsü", "Galeta Unu", "Yumurta"], "tar": "Tavuğu incelt, panele, kızart.", "sure": "20 dk", "zorluk": "Orta"},
    {"ad": "Hünkar Beğendi", "kat": "Ana Yemek", "img": "", "malz": ["Kuşbaşı Et", "Patlıcan", "Beşamel Sos", "Kaşar"], "tar": "Beğendiyi yap, üstüne et sote koy.", "sure": "60 dk", "zorluk": "Zor"},
    {"ad": "Tas Kebabı", "kat": "Ana Yemek", "img": "", "malz": ["Kuşbaşı", "Patates", "Havuç"], "tar": "Eti pişir, sebzeleri ekle.", "sure": "60 dk", "zorluk": "Orta"},
    {"ad": "Orman Kebabı", "kat": "Ana Yemek", "img": "", "malz": ["Et", "Bezelye", "Havuç", "Patates"], "tar": "Eti ve sebzeleri tencerede buluştur.", "sure": "50 dk", "zorluk": "Orta"},
    {"ad": "Musakka", "kat": "Ana Yemek", "img": "", "malz": ["Patlıcan", "Kıyma", "Domates"], "tar": "Patlıcanı küp kızart, kıymayla pişir.", "sure": "45 dk", "zorluk": "Orta"},
    {"ad": "Ali Nazik", "kat": "Ana Yemek", "img": "", "malz": ["Kıyma", "Süzme Yoğurt", "Patlıcan"], "tar": "Köz patlıcanlı yoğurt üstüne kıyma.", "sure": "40 dk", "zorluk": "Orta"},
    {"ad": "Ciğer Tava", "kat": "Ana Yemek", "img": "", "malz": ["Ciğer", "Un", "Kızartma Yağı"], "tar": "Ciğeri unla, kızgın yağda 2 dk pişir.", "sure": "15 dk", "zorluk": "Orta"},
    {"ad": "Saç Kavurma", "kat": "Ana Yemek", "img": "", "malz": ["Et", "Kuyruk Yağı", "Biber", "Domates"], "tar": "Saçta yüksek ateşte çevir.", "sure": "30 dk", "zorluk": "Orta"},
    {"ad": "Yaprak Sarma", "kat": "Ana Yemek", "img": "", "malz": ["Yaprak", "Pirinç", "Zeytinyağı", "Limon"], "tar": "İnce ince sar, limonlu suda pişir.", "sure": "90 dk", "zorluk": "Zor"},
    {"ad": "Tantuni", "kat": "Ana Yemek", "img": "", "malz": ["Dana Eti", "Lavaş", "Maydanoz", "Soğan"], "tar": "Eti haşla, sacda yağ ve toz biberle çevir.", "sure": "40 dk", "zorluk": "Orta"},
    {"ad": "Etli Ekmek (Lavaşla)", "kat": "Ana Yemek", "img": "", "malz": ["Lavaş", "Kıyma", "Domates", "Biber"], "tar": "Harcı lavaşa sür, fırınla.", "sure": "20 dk", "zorluk": "Kolay"},
    
    # --- MAKARNA & PİLAV ---
    {"ad": "Pirinç Pilavı", "kat": "Makarna", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Pilav.jpg/640px-Pilav.jpg", "malz": ["Pirinç", "Tereyağı", "Şehriye"], "tar": "Şehriyeyi kavur, pirinci ekle, demle.", "sure": "25 dk", "zorluk": "Orta"},
    {"ad": "Spagetti Bolonez", "kat": "Makarna", "img": "https://images.unsplash.com/photo-1622973536968-3ead9e780960?w=600", "malz": ["Spagetti", "Kıyma", "Domates Sos", "Havuç"], "tar": "Kıymalı sos yap, makarnanın üstüne dök.", "sure": "30 dk", "zorluk": "Orta"},
    {"ad": "Kremalı Mantarlı Makarna", "kat": "Makarna", "img": "https://images.unsplash.com/photo-1555949258-eb67b1ef0ceb?w=600", "malz": ["Makarna", "Mantar", "Krema", "Fesleğen"], "tar": "Mantarı sotele, krema ekle, makarna ile karıştır.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Lahmacun", "kat": "Ana Yemek", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Lahmacun.jpg/640px-Lahmacun.jpg", "malz": ["Kıyma", "Lavaş", "Sebzeler"], "tar": "Lavaşa sür fırınla.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Bulgur Pilavı", "kat": "Makarna", "img": "", "malz": ["Bulgur", "Salça", "Domates", "Biber"], "tar": "Sebzeleri kavur, bulguru ekle.", "sure": "25 dk", "zorluk": "Kolay"},
    {"ad": "Fırın Makarna", "kat": "Makarna", "img": "", "malz": ["Kalın Makarna", "Beşamel Sos", "Kaşar", "Peynir"], "tar": "Makarnayı beşamel ile karıştır fırınla.", "sure": "45 dk", "zorluk": "Orta"},
    {"ad": "Noodle (Ev Usulü)", "kat": "Makarna", "img": "", "malz": ["Erişte", "Soya Sosu", "Lahana", "Havuç"], "tar": "Sebzeleri wok tavada çevir, erişteyi ekle.", "sure": "15 dk", "zorluk": "Kolay"},
    {"ad": "Penne Arabiata", "kat": "Makarna", "img": "", "malz": ["Penne", "Acı Biber", "Domates", "Sarımsak"], "tar": "Acılı domates sosu yap.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Perde Pilavı", "kat": "Makarna", "img": "", "malz": ["Pirinç", "Yufka", "Tavuk", "Badem", "Kuş Üzümü"], "tar": "Yufkanın içine pilavı doldur fırınla.", "sure": "90 dk", "zorluk": "Zor"},
    {"ad": "Lazanya", "kat": "Makarna", "img": "", "malz": ["Lazanya Yaprağı", "Kıyma", "Beşamel", "Kaşar"], "tar": "Kat kat diz fırınla.", "sure": "60 dk", "zorluk": "Zor"},
    {"ad": "Kuskus", "kat": "Makarna", "img": "", "malz": ["Kuskus", "Salça", "Sebze"], "tar": "Makarna gibi haşla veya pilav gibi demle.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Domatesli Pilav", "kat": "Makarna", "img": "", "malz": ["Pirinç", "Domates", "Tereyağı"], "tar": "Rende domatesle pirinci kavur, demle.", "sure": "30 dk", "zorluk": "Kolay"},
    {"ad": "Makarna Salatası", "kat": "Makarna", "img": "", "malz": ["Makarna", "Yoğurt", "Mayonez", "Garnitür", "Mısır"], "tar": "Haşla soğut, malzemelerle karıştır.", "sure": "20 dk", "zorluk": "Kolay"},

    # --- SEBZELİ ---
    {"ad": "Zeytinyağlı Fasulye", "kat": "Sebzeli", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Taze_fasulye.jpg/640px-Taze_fasulye.jpg", "malz": ["Taze Fasulye", "Domates", "Soğan", "Şeker"], "tar": "Kendi suyunda kısık ateşte pişir.", "sure": "50 dk", "zorluk": "Kolay"},
    {"ad": "İmam Bayıldı", "kat": "Sebzeli", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/%C4%B0mam_bay%C4%B1ld%C4%B1.jpg/640px-%C4%B0mam_bay%C4%B1ld%C4%B1.jpg", "malz": ["Patlıcan", "Bol Soğan", "Sarımsak", "Zeytinyağı"], "tar": "Patlıcanı kızart, soğanlı harçla doldur.", "sure": "50 dk", "zorluk": "Orta"},
    {"ad": "Mücver", "kat": "Sebzeli", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/M%C3%BCcver.jpg/640px-M%C3%BCcver.jpg", "malz": ["Kabak", "Yumurta", "Un", "Dereotu", "Peynir"], "tar": "Rendele, sık, karıştır, kızart.", "sure": "30 dk", "zorluk": "Orta"},
    {"ad": "Ispanak Yemeği", "kat": "Sebzeli", "img": "", "malz": ["Ispanak", "Pirinç", "Salça", "Yoğurt"], "tar": "Soğanla kavur, pirinç at.", "sure": "30 dk", "zorluk": "Kolay"},
    {"ad": "Şakşuka", "kat": "Sebzeli", "img": "", "malz": ["Patlıcan", "Biber", "Kabak", "Domates Sos"], "tar": "Küp kızart, sosla.", "sure": "30 dk", "zorluk": "Kolay"},
    {"ad": "Zeytinyağlı Enginar", "kat": "Sebzeli", "img": "", "malz": ["Enginar", "Bezelye", "Havuç", "Patates"], "tar": "Garnitürü çanağa koy pişir.", "sure": "40 dk", "zorluk": "Orta"},
    {"ad": "Mercimek Köftesi", "kat": "Sebzeli", "img": "", "malz": ["Mercimek", "İnce Bulgur", "Salça", "Yeşillik"], "tar": "Mercimeği haşla bulguru at şişsin, yoğur.", "sure": "40 dk", "zorluk": "Orta"},
    {"ad": "Karnabahar Kızartma", "kat": "Sebzeli", "img": "", "malz": ["Karnabahar", "Yumurta", "Un", "Yoğurt"], "tar": "Haşla, panele, kızart.", "sure": "35 dk", "zorluk": "Orta"},
    {"ad": "Kabak Sıyırma", "kat": "Sebzeli", "img": "", "malz": ["Girit Kabağı", "Limon", "Zeytinyağı", "Pirinç"], "tar": "Kabakları şerit yap, hafif pişir.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Pırasa Yemeği", "kat": "Sebzeli", "img": "", "malz": ["Pırasa", "Havuç", "Pirinç", "Limon"], "tar": "Zeytinyağlı pişir.", "sure": "35 dk", "zorluk": "Kolay"},
    {"ad": "Patlıcan Salatası", "kat": "Sebzeli", "img": "", "malz": ["Köz Patlıcan", "Köz Biber", "Sarımsak", "Zeytinyağı"], "tar": "Közle, soy, ez, karıştır.", "sure": "30 dk", "zorluk": "Kolay"},
    {"ad": "Semizotu Salatası", "kat": "Sebzeli", "img": "", "malz": ["Semizotu", "Süzme Yoğurt", "Sarımsak", "Ceviz"], "tar": "Yıka, karıştır, ceviz serp.", "sure": "10 dk", "zorluk": "Çok Kolay"},

    # --- DÜNYA MUTFAĞI ---
    {"ad": "Ev Yapımı Burger", "kat": "Dünya Mutfağı", "img": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600", "malz": ["Kıyma", "Burger Ekmeği", "Cheddar", "Karamelize Soğan"], "tar": "Köfteyi döküm tavada pişir.", "sure": "30 dk", "zorluk": "Orta"},
    {"ad": "Pizza", "kat": "Dünya Mutfağı", "img": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600", "malz": ["Un", "Maya", "Mozzarella", "Sucuk/Mantar"], "tar": "Hamuru aç, malzemeyi diz fırınla.", "sure": "60 dk", "zorluk": "Zor"},
    {"ad": "Sushi", "kat": "Dünya Mutfağı", "img": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=600", "malz": ["Sushi Pirinci", "Nori Yosunu", "Salatalık", "Somon"], "tar": "Pirinci lapa yap, yosuna sar.", "sure": "50 dk", "zorluk": "Zor"},
    {"ad": "Taco", "kat": "Dünya Mutfağı", "img": "", "malz": ["Tortilla", "Kıyma", "Meksika Fasulyesi", "Mısır"], "tar": "Kıymayı baharatla, ekmeğe doldur.", "sure": "25 dk", "zorluk": "Kolay"},
    {"ad": "Falafel", "kat": "Dünya Mutfağı", "img": "", "malz": ["Nohut", "Maydanoz", "Sarımsak", "Kimyon"], "tar": "Robottan çek, top yap kızart.", "sure": "40 dk", "zorluk": "Orta"},
    {"ad": "Quesadilla", "kat": "Dünya Mutfağı", "img": "", "malz": ["Tortilla", "Tavuk", "Kaşar", "Biber"], "tar": "Lavaşa koy, ikiye katla kızart.", "sure": "20 dk", "zorluk": "Kolay"},
    {"ad": "Mac & Cheese", "kat": "Dünya Mutfağı", "img": "", "malz": ["Makarna", "Cheddar Peyniri", "Süt", "Un"], "tar": "Peynir sosu yap makarna ile karıştır.", "sure": "25 dk", "zorluk": "Kolay"},
    {"ad": "Fajita", "kat": "Dünya Mutfağı", "img": "", "malz": ["Et/Tavuk", "Renkli Biberler", "Soğan"], "tar": "Jülyen doğra, yüksek ateşte sotele.", "sure": "25 dk", "zorluk": "Kolay"},
    {"ad": "Ratatouille", "kat": "Dünya Mutfağı", "img": "", "malz": ["Kabak", "Patlıcan", "Domates", "Sos"], "tar": "Sebzeleri yuvarlak doğra, sosla fırınla.", "sure": "60 dk", "zorluk": "Orta"},
    {"ad": "Burrito", "kat": "Dünya Mutfağı", "img": "", "malz": ["Lavaş", "Pirinç", "Fasulye", "Kıyma"], "tar": "Tüm malzemeyi sar dürüm yap.", "sure": "30 dk", "zorluk": "Orta"},

    # --- TATLILAR ---
    {"ad": "Fırın Sütlaç", "kat": "Tatlı", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/F%C4%B1r%C4%B1n_S%C3%BCtla%C3%A7.jpg/640px-F%C4%B1r%C4%B1n_S%C3%BCtla%C3%A7.jpg", "malz": ["Süt", "Pirinç", "Şeker", "Nişasta"], "tar": "Güveçte fırınla.", "sure": "45 dk", "zorluk": "Orta"},
    {"ad": "Magnolia", "kat": "Tatlı", "img": "https://images.unsplash.com/photo-1517084507022-e613898f057c?w=600", "malz": ["Süt", "Krema", "Bisküvi", "Çilek/Muz"], "tar": "Muhallebi yap, bisküviyle diz.", "sure": "30 dk", "zorluk": "Kolay"},
    {"ad": "Islak Kek (Brownie)", "kat": "Tatlı", "img": "https://images.unsplash.com/photo-1606313564200-e75d5e30476d?w=600", "malz": ["Yumurta", "Süt", "Kakao", "Un"], "tar": "Keki pişir, sosunu dök.", "sure": "40 dk", "zorluk": "Kolay"},
    {"ad": "Künefe", "kat": "Tatlı", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/K%C3%BCnefe.jpg/640px-K%C3%BCnefe.jpg", "malz": ["Kadayıf", "Peynir", "Şerbet"], "tar": "Tavada arkalı önlü kızart.", "sure": "20 dk", "zorluk": "Orta"},
    {"ad": "Baklava", "kat": "Tatlı", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Baklava%281%29.png/640px-Baklava%281%29.png", "malz": ["Yufka", "Fıstık", "Şerbet"], "tar": "Hazır yufka ile yap.", "sure": "60 dk", "zorluk": "Zor"},
    {"ad": "İrmik Helvası", "kat": "Tatlı", "img": "", "malz": ["İrmik", "Tereyağı", "Süt", "Fıstık"], "tar": "Kavur, şerbetle.", "sure": "30 dk", "zorluk": "Orta"},
    {"ad": "Revani", "kat": "Tatlı", "img": "", "malz": ["İrmik", "Yoğurt", "Un", "Şerbet"], "tar": "Keki pişir şerbetle.", "sure": "50 dk", "zorluk": "Orta"},
    {"ad": "Şekerpare", "kat": "Tatlı", "img": "", "malz": ["Un", "Pudra Şekeri", "Tereyağı", "Şerbet"], "tar": "Kurabiye gibi yap, şerbetle.", "sure": "50 dk", "zorluk": "Orta"},
    {"ad": "Mozaik Pasta", "kat": "Tatlı", "img": "", "malz": ["Petibör Bisküvi", "Kakao", "Tereyağı"], "tar": "Karıştır buzluğa at.", "sure": "15 dk", "zorluk": "Kolay"},
    {"ad": "Trileçe", "kat": "Tatlı", "img": "", "malz": ["Kek", "Sütlü Sos", "Karamel"], "desc": "Balkan.", "tar": "Keki sütle ıslat karamel dök.", "sure": "60 dk", "zorluk": "Zor"},
    {"ad": "Cheesecake", "kat": "Tatlı", "img": "", "malz": ["Labne", "Krema", "Bisküvi Tabani"], "tar": "Düşük ısıda uzun pişir.", "sure": "90 dk", "zorluk": "Zor"},
    {"ad": "Kabak Tatlısı", "kat": "Tatlı", "img": "", "malz": ["Bal Kabağı", "Şeker", "Tahin", "Ceviz"], "tar": "Şekerle beklet pişir.", "sure": "50 dk", "zorluk": "Kolay"},
    {"ad": "Waffle (Ev)", "kat": "Tatlı", "img": "", "malz": ["Waffle Hamuru", "Çikolata", "Meyve"], "tar": "Makinede pişir süsle.", "sure": "15 dk", "zorluk": "Kolay"},
    {"ad": "Sufle", "kat": "Tatlı", "img": "", "malz": ["Çikolata", "Yumurta", "Tereyağı"], "tar": "İçi akışkan pişir.", "sure": "15 dk", "zorluk": "Zor"},
    {"ad": "Kazandibi", "kat": "Tatlı", "img": "", "malz": ["Süt", "Şeker", "Pirinç Unu"], "tar": "Tepsiyi yak, muhallebiyi dök.", "sure": "45 dk", "zorluk": "Zor"}
]

# --- 4. FONKSİYONLAR ---
def baslangic_verisini_olustur():
    # Eğer bu versiyonun dosyası yoksa oluştur
    if not os.path.exists(TARIF_DB):
        with open(TARIF_DB, "w", encoding="utf-8") as f:
            json.dump(DEV_MENU, f, ensure_ascii=False, indent=4)

def db_yukle(dosya):
    if not os.path.exists(dosya):
        return [] if "tarif" in dosya else {}
    with open(dosya, "r", encoding="utf-8") as f:
        try:
            veri = json.load(f)
        except:
            return [] if "tarif" in dosya else {}
    if "tarif" in dosya: return veri if isinstance(veri, list) else []
    return veri if isinstance(veri, dict) else {}

def db_kaydet(dosya, veri):
    with open(dosya, "w", encoding="utf-8") as f: json.dump(veri, f, ensure_ascii=False, indent=4)

def get_image(url, kat):
    # Eğer geçerli bir URL varsa onu kullan
    if url and "http" in url: return url
    # Yoksa kategoriye göre en azından "alakalı" bir yedek kullan
    defaults = {
        "Kahvaltı": "https://images.unsplash.com/photo-1533089862017-5c32417a1a08?w=600",
        "Ana Yemek": "https://images.unsplash.com/photo-1547592180-85f173990554?w=600",
        "Tatlı": "https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=600",
        "Çorba": "https://images.unsplash.com/photo-1547592166-23acbe3b624b?w=600",
        "Makarna": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=600",
        "Dünya Mutfağı": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=600",
        "Sebzeli": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600"
    }
    return defaults.get(kat, "https://images.unsplash.com/photo-1495195134817-aeb325a55b65?w=600")

# --- 5. BAŞLANGIÇ ---
baslangic_verisini_olustur()

# --- 6. ARAMA ---
def tarifleri_bul(girdi, kategori):
    girdi = girdi.lower()
    arananlar = [x.strip() for x in girdi.replace(",", " ").split() if x.strip()]
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
        if tum:
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
                if u.get(k)==p or (k=="admin" and p=="2026"): st.session_state.login=True; st.session_state.user=k; st.rerun()
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
                ta=st.text_input("Ad"); ti=st.text_input("Resim URL (Varsa yapıştır)"); tm=st.text_area("Malzeme"); tt=st.text_area("Tarif"); tk=st.selectbox("Kat", ["Kahvaltı", "Ana Yemek", "Tatlı", "Kullanıcı"])
                if st.form_submit_button("Ekle"):
                    u = db_yukle(USER_DB)
                    u.append({"ad": ta, "img": ti, "malz": tm.split("\n"), "tar": tt, "kat": tk, "sef": st.session_state.user, "sure": "45 dk", "zorluk": "Orta"})
                    db_kaydet(USER_DB, u); st.success("Oldu"); st.rerun()
        else: st.warning("Giriş yap.")

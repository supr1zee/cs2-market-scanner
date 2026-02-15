import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="CS2 Market Scanner", layout="wide")
st.title("📊 Сканер цен: Steam Market vs CSFloat")

# Список предметов для отслеживания (добавляй сюда любые названия с ТП)
items_to_track = [
    "AK-47 | Slate (Field-Tested)",
    "Glove Case",
    "P250 | Sand Dune (Field-Tested)",
    "Fracture Case"
]

def get_prices(item_name):
    # Прямой запрос к Steam
    steam_url = f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name={item_name}"
    # Прямой запрос к CSFloat
    float_url = f"https://csfloat.com/api/v1/listings/items/basic?market_hash_name={item_name}"
    
    data = {"Предмет": item_name, "Steam ($)": 0, "CSFloat ($)": 0, "Профит ($)": 0}
    
    try:
        s_res = requests.get(steam_url).json()
        if s_res.get("success"):
            price = s_res["lowest_price"].replace("$", "").replace(",", ".")
            data["Steam ($)"] = float(price)
            
        f_res = requests.get(float_url).json()
        if len(f_res) > 0:
            data["CSFloat ($)"] = f_res[0]["price"] / 100
            
        # Расчет прибыли (Комиссия Float 2%)
        data["Профит ($)"] = round((data["CSFloat ($)"] * 0.98) - data["Steam ($)"], 2)
    except:
        pass
    
    return data

if st.button('Обновить цены'):
    results = []
    progress_bar = st.progress(0)
    
    for i, item in enumerate(items_to_track):
        results.append(get_prices(item))
        progress_bar.progress((i + 1) / len(items_to_track))
        time.sleep(2) # Пауза для Steam
        
    df = pd.DataFrame(results)
    st.table(df)
else:
    st.info("Нажмите кнопку для сканирования рынка")

import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="CS2 Scanner", layout="wide")
st.title("📊 Сканер: Steam Market vs CSFloat")

def get_prices(item_name):
    # Заголовки, чтобы сайты не блокировали запрос
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    res = {"Предмет": item_name, "Steam": 0.0, "Float": 0.0, "Profit": 0.0, "ROI %": 0.0}
    
    try:
        # Получаем цену Steam
        s_url = f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name={item_name}"
        s_req = requests.get(s_url, headers=headers, timeout=10).json()
        if s_req.get("success") and "lowest_price" in s_req:
            p_str = s_req["lowest_price"].replace("$", "").replace("USD", "").replace(",", ".").strip()
            res["Steam"] = round(float(p_str), 2)
            
        # Получаем цену CSFloat
        f_url = f"https://csfloat.com/api/v1/listings/items/basic?market_hash_name={item_name}"
        f_req = requests.get(f_url, headers=headers, timeout=10).json()
        if f_req and len(f_req) > 0:
            res["Float"] = round(f_req[0]["price"] / 100, 2)
            
        # Расчет профита
        if res["Steam"] > 0 and res["Float"] > 0:
            # Считаем чистыми (вычитаем 2% комиссии Float)
            res["Profit"] = round((res["Float"] * 0.98) - res["Steam"], 2)
            res["ROI %"] = round((res["Profit"] / res["Steam"]) * 100, 2)
    except:
        pass
    return res

# Боковая панель для ввода предметов
input_items = st.sidebar.text_area("Список предметов (по одному на строку):", 
                                   "AK-47 | Slate (Field-Tested)\nFracture Case\nGlove Case")
items_list = [i.strip() for i in input_items.split('\n') if i.strip()]

if st.button('🚀 Запустить сканирование'):
    results = []
    progress_bar = st.progress(0)
    
    for i, name in enumerate(items_list):
        data = get_prices(name)
        results.append(data)
        progress_bar.progress((i + 1) / len(items_list))
        time.sleep(4) # Пауза для защиты от бана Steam
        
    df = pd.DataFrame(results)
    # Показываем таблицу
    st.dataframe(df, use_container_width=True)

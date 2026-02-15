import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="CS2 Pro Scanner", layout="wide")

# Кастомный CSS для красоты
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stDataFrame"] { background-color: #161b22; border-radius: 10px; }
    </style>
    """, unsafe_allow_path=True)

st.title("📊 Мой личный сканер ТП vs CSFloat")

def get_prices(item_name):
    # Заголовки, чтобы сайты нас не банили
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    res = {"Предмет": item_name, "Steam": 0.0, "Float": 0.0, "Profit": 0.0, "ROI %": 0.0}
    
    try:
        # Steam
        s_url = f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name={item_name}"
        s_req = requests.get(s_url, headers=headers, timeout=10).json()
        if s_req.get("success"):
            # Очищаем цену от знаков валют и лишних точек
            p_str = s_req["lowest_price"].replace("$", "").replace("USD", "").replace(",", ".").strip()
            res["Steam"] = round(float(p_str), 2)
            
        # CSFloat
        f_url = f"https://csfloat.com/api/v1/listings/items/basic?market_hash_name={item_name}"
        f_req = requests.get(f_url, headers=headers, timeout=10).json()
        if f_req and len(f_req) > 0:
            res["Float"] = round(f_req[0]["price"] / 100, 2)
            
        # Математика
        if res["Steam"] > 0 and res["Float"] > 0:
            # Чистыми после комиссии Float (2%)
            net_sale = res["Float"] * 0.98
            res["Profit"] = round(net_sale - res["Steam"], 2)
            res["ROI %"] = round((res["Profit"] / res["Steam"]) * 100, 2)
            
    except Exception as e:
        pass
    return res

# Боковая панель
input_items = st.sidebar.text_area("Список предметов:", "AK-47 | Slate (Field-Tested)\nFracture Case\nGlove Case")
items_list = [i.strip() for i in input_items.split('\n') if i.strip()]

if st.button('🚀 Запустить поиск выгоды'):
    results = []
    bar = st.progress(0)
    
    for i, name in enumerate(items_list):
        data = get_prices(name)
        results.append(data)
        bar.progress((i + 1) / len(items_list))
        time.sleep(3.5) # Пауза, чтобы не получить бан
        
    df = pd.DataFrame(results)
    
    # Сортируем по профиту сразу
    df = df.sort_values(by="ROI %", ascending=False)
    
    # Вывод красивой таблицы
    st.dataframe(df, use_container_width=True, height=600)

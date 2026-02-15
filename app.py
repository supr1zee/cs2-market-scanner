import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="CS2 Pro Scanner", layout="wide")
st.title("📈 Авто-Сканер: Выгода Steam -> CSFloat")

def get_prices(item_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    res = {"Предмет": item_name, "Steam $": 0.0, "Float $": 0.0, "Profit $": 0.0, "ROI %": 0.0, "Купить": ""}
    
    try:
        # 1. Запрос Steam
        s_url = f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name={item_name}"
        s_req = requests.get(s_url, headers=headers, timeout=10).json()
        if s_req.get("success"):
            p_str = s_req["lowest_price"].replace("$", "").replace("USD", "").replace(",", ".").strip()
            res["Steam $"] = round(float(p_str), 2)
            
        # 2. Запрос CSFloat
        f_url = f"https://csfloat.com/api/v1/listings/items/basic?market_hash_name={item_name}"
        f_req = requests.get(f_url, headers=headers, timeout=10).json()
        if f_req and len(f_req) > 0:
            res["Float $"] = round(f_req[0]["price"] / 100, 2)
            
        # 3. Расчет профита и формирование ссылок
        if res["Steam $"] > 0 and res["Float $"] > 0:
            res["Profit $"] = round((res["Float $"] * 0.98) - res["Steam $"], 2)
            res["ROI %"] = round((res["Profit $"] / res["Steam $"]) * 100, 2)
            res["Купить"] = f"https://steamcommunity.com/market/listings/730/{item_name}"
            
    except:
        pass
    return res

# --- ИНТЕРФЕЙС ---
st.sidebar.header("Настройки")
# Сюда вставляй список из 50-100 предметов, который я давал выше
input_text = st.sidebar.text_area("Список предметов для мониторинга:", 
                                  "AK-47 | Slate (Field-Tested)\nFracture Case\nGlove Case\nRecoil Case", height=300)

items_list = [i.strip() for i in input_text.split('\n') if i.strip()]

if st.button('🚀 Начать поиск выгодных сделок'):
    st.info(f"Запущено сканирование {len(items_list)} предметов. Пожалуйста, подождите...")
    results = []
    progress_bar = st.progress(0)
    
    for i, name in enumerate(items_list):
        data = get_prices(name)
        results.append(data)
        progress_bar.progress((i + 1) / len(items_list))
        # Пауза 4 секунды критически важна для защиты от блокировок Steam
        time.sleep(4) 
        
    df = pd.DataFrame(results)
    
    # Сортировка по ROI (самые выгодные сверху)
    if not df.empty:
        df = df.sort_values(by="ROI %", ascending=False)
        
        # Настройка отображения ссылок
        st.data_editor(
            df,
            column_config={
                "Купить": st.column_config.LinkColumn("Ссылка на Steam")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.error("Не удалось получить данные. Попробуйте уменьшить список предметов.")

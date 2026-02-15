import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="CS2 Real-Time Scanner", layout="wide")
st.title("🔥 Актуальный сканер: Ликвид до $1")

def get_prices(item_name):
    # Улучшенные заголовки для обхода блокировок
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://csfloat.com/"
    }
    
    res = {"Предмет": item_name, "Steam $": 0.0, "Float $": 0.0, "Profit $": 0.0, "ROI %": 0.0, "Ссылка": ""}
    
    try:
        # 1. ЗАПРОС STEAM (с параметром для сброса кэша)
        s_url = f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name={item_name}&nocache={time.time()}"
        s_req = requests.get(s_url, headers=headers, timeout=10).json()
        if s_req.get("success"):
            p_str = s_req["lowest_price"].replace("$", "").replace("USD", "").replace(",", ".").strip()
            res["Steam $"] = round(float(p_str), 2)
            
        # 2. ЗАПРОС CSFLOAT (через API поиска)
        f_url = f"https://csfloat.com/api/v1/listings/items/basic?market_hash_name={item_name}&limit=1"
        f_req = requests.get(f_url, headers=headers, timeout=10).json()
        
        if f_req and len(f_req) > 0:
            # Берем самую низкую цену текущего листинга
            res["Float $"] = round(f_req[0]["price"] / 100, 2)
            
        # 3. МАТЕМАТИКА
        if res["Steam $"] > 0 and res["Float $"] > 0:
            res["Profit $"] = round((res["Float $"] * 0.98) - res["Steam $"], 2)
            res["ROI %"] = round((res["Profit $"] / res["Steam $"]) * 100, 2)
            res["Ссылка"] = f"https://steamcommunity.com/market/listings/730/{item_name}"
            
    except Exception as e:
        print(f"Ошибка на {item_name}: {e}")
        
    return res

# --- ИНТЕРФЕЙС ---
input_text = st.sidebar.text_area("Вставь список (ликвид до $1):", 
                                  "Recoil Case\nFracture Case\nAK-47 | Slate (Field-Tested)\nM4A1-S | Night Terror (Field-Tested)", height=300)

items_list = [i.strip() for i in input_text.split('\n') if i.strip()]

if st.button('🚀 Найти выгоду сейчас'):
    results = []
    prog = st.progress(0)
    
    for i, name in enumerate(items_list):
        data = get_prices(name)
        results.append(data)
        prog.progress((i + 1) / len(items_list))
        # Пауза 3.5 секунды — золотая середина, чтобы не забанили
        time.sleep(3.5) 
        
    df = pd.DataFrame(results)
    
    if not df.empty:
        # Сортируем: сначала те, где есть цена и на Steam, и на Float
        df = df[df["Float $"] > 0].sort_values(by="ROI %", ascending=False)
        
        st.data_editor(
            df,
            column_config={"Ссылка": st.column_config.LinkColumn("Steam Link")},
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("Данные не получены. Попробуйте еще раз через минуту.")

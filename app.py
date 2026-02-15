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
import streamlit as st
import requests
import pandas as pd
import time

# Настройка страницы
st.set_page_config(page_title="CS2 Pro Scanner", layout="wide")
st.title("🚀 Автоматический сканер Steam vs CSFloat")

# Функция для получения цен
def get_prices(item_name):
    steam_url = f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name={item_name}"
    float_url = f"https://csfloat.com/api/v1/listings/items/basic?market_hash_name={item_name}"
    
    res = {"Предмет": item_name, "Steam": 0, "Float": 0, "Profit": 0, "ROI %": 0}
    
    try:
        # Запрос к Steam
        s_data = requests.get(steam_url).json()
        if s_data.get("success"):
            p = s_data["lowest_price"].replace("$", "").replace(",", ".")
            res["Steam"] = float(p)
            
        # Запрос к CSFloat
        f_data = requests.get(float_url).json()
        if f_data:
            res["Float"] = f_data[0]["price"] / 100
            
        # Расчет (2% комиссия Float)
        res["Profit"] = round((res["Float"] * 0.98) - res["Steam"], 2)
        if res["Steam"] > 0:
            res["ROI %"] = round((res["Profit"] / res["Steam"]) * 100, 1)
    except:
        pass
    return res

# Интерфейс
st.sidebar.header("Настройки списка")
# Поле, куда ты можешь просто вставить 100 названий через запятую или с новой строки
input_items = st.sidebar.text_area("Вставь список предметов (каждый с новой строки):", 
                                   "AK-47 | Slate (Field-Tested)\nFracture Case\nGlove Case")

items_list = [i.strip() for i in input_items.split('\n') if i.strip()]

if st.button('Начать сканирование'):
    st.write(f"Сканируем {len(items_list)} предметов...")
    results = []
    prog = st.progress(0)
    
    for i, name in enumerate(items_list):
        results.append(get_prices(name))
        prog.progress((i + 1) / len(items_list))
        # Важно: Steam банит за частые запросы. Делаем паузу 3-5 сек.
        time.sleep(4) 
    
    df = pd.DataFrame(results)
    
    # Подсветка выгодных сделок
    def highlight_profit(val):
        color = 'lightgreen' if val > 5 else 'white'
        return f'background-color: {color}'

    st.dataframe(df.style.applymap(highlight_profit, subset=['ROI %']))

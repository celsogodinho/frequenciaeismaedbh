from datetime import datetime
import streamlit as st
from streamlit_option_menu import option_menu


from paginas import rme 
from paginas import regional as reg

agora = datetime.now()
mes_atual = agora.month
ano_atual = agora.year

dias_letivos = {
    2:16,	
    3:19,	
    4:22,	
    5:20,
    6:20,
    7:10,
    8:21,
    9:21,
    10:18,
    11:19,
    12:13
}

dias_letivos_acumulados = 0
for i in range(2, mes_atual+2):
    dias_letivos_acumulados += dias_letivos[i]

ids_regionais = {
    "Regional Barreiro":1,
    "Regional Centro Sul":2,
    "Regional Leste":3,
    "Regional Nordeste":4,
    "Regional Noroeste":5,
    "Regional Norte":6,
    "Regional Oeste":7,
    "Regional Pampulha":8,
    "Regional Venda Nova":9
}


st.set_page_config(page_title='Frequência EF - SMED - PBH', page_icon='static/favicon.png', layout="wide", initial_sidebar_state="auto", menu_items=None)
with st.sidebar:
    options = [
        "Rede Municipal de Educação",
        "Regional Barreiro",
        "Regional Centro Sul",
        "Regional Leste",
        "Regional Nordeste",
        "Regional Noroeste",
        "Regional Norte",
        "Regional Oeste",
        "Regional Pampulha",
        "Regional Venda Nova"
    ]
    selected = option_menu("Frequência - EI 4 / 5 anos e 5 / 6 anos", options, 
        icons=[
               'play-fill', 'play-fill','play-fill', 
               'play-fill', 'play-fill','play-fill',
               'play-fill', 'play-fill','play-fill',
               'play-fill', 'play-fill' 
               ], 
        menu_icon="house", 
        default_index=0)

if selected == "Rede Municipal de Educação":
    rme.rme(dias_letivos_acumulados, ano_atual, mes_atual)    
else:
    reg.regional(selected, ids_regionais[selected], dias_letivos_acumulados, ano_atual, mes_atual)

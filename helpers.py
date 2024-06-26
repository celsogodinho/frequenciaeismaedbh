import streamlit as st

meses = {
    1:'Janeiro',
    2:'Fevereiro',
    3:'Março',
    4:'Abril',
    5:'Maio',
    6:'Junho',
    7:'Julho',
    8:'Agosto',
    9:'Setembro',
    10:'Outubro',
    11:'Novembro',
    12:'Dezembro'
}


def obtem_conexao():
    conn = st.connection("postgresql")
    return conn

@st.cache_data
def busca_dados(tabela):
    conn = obtem_conexao()
    df = conn.query("select * from %s"%tabela)
    return df

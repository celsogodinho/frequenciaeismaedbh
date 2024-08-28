import streamlit as st
import pandas as pd
from streamlit_apexjs import st_apexcharts
import pandas as pd
from streamlit_extras.metric_cards import style_metric_cards

from helpers import obtem_conexao, meses, DT_ATUALIZACAO

@st.cache_data
def busca_resultados(dias_letivos, ano):
    regional = pd.DataFrame.from_dict({
        'regional_id':[1,2,3,4,5,6,7,8,9],
        'regional':['BARREIRO','CENTRO SUL','LESTE','NORDESTE','NOROESTE','NORTE','OESTE','PAMPULHA','VENDA NOVA']
    })

    conn = obtem_conexao()

    sql_35 = '''
        select e.regional regional_id, count(fa.cod_aluno) _0_35
        from faltas_acumuladas fa, aluno a , escola e, turma t
        where ano = %s
        and a.cod_aluno = fa.cod_aluno 
        and e.cod_escl = a.cod_escl_atua
        and t.cod_sequ_turm = a.cod_turm_atua
        and t.ensino in (5,6)
        and 100*(cast(fa.total_sem_jus as float)/%s) < 35.0
        group by e.regional
    '''%(ano, dias_letivos)

    data_menor_35 = conn.query(sql_35)

    sql_35_40 = '''
        select e.regional regional_id, count(fa.cod_aluno) _35_40
        from faltas_acumuladas fa, aluno a , escola e, turma t
        where ano = %s
        and a.cod_aluno = fa.cod_aluno 
        and e.cod_escl = a.cod_escl_atua
        and t.cod_sequ_turm = a.cod_turm_atua
        and t.ensino in (5,6)        
        and 100*(cast(fa.total_sem_jus as float)/%s) >= 35.0
        and 100*(cast(fa.total_sem_jus as float)/%s) < 40.0
        group by e.regional
    '''%(ano, dias_letivos, dias_letivos)

    data_35_40 = conn.query(sql_35_40)

    sql_maior_40 = '''
        select e.regional regional_id, count(fa.cod_aluno) _40_100
        from faltas_acumuladas fa, aluno a , escola e, turma t
        where ano = %s
        and a.cod_aluno = fa.cod_aluno 
        and e.cod_escl = a.cod_escl_atua
        and t.cod_sequ_turm = a.cod_turm_atua
        and t.ensino in (5,6)        
        and 100*(cast(fa.total_sem_jus as float)/%s) >= 40.0
        group by e.regional
    '''%(ano, dias_letivos)

    data_maior_40 = conn.query(sql_maior_40)

    result = regional.merge(data_menor_35, on='regional_id', how='left' )
    result = result.merge(data_35_40, on='regional_id', how='left')
    result = result.merge(data_maior_40, on='regional_id', how='left')

    result.fillna(0, inplace=True)

    result['total'] = result['_0_35'] + result['_35_40'] + result['_40_100']
    result['p_0_35'] = 100*result['_0_35']/result['total']
    result['p_35_40'] = 100*result['_35_40']/result['total']
    result['p_40_100'] = 100*result['_40_100']/result['total']

    return result


def rme(dias_letivos, ano, mes):
    st.header("Secretaria Municipal de Educação - PBH", divider='rainbow')
    st.subheader("Percentual de Alunos de 4 e 5 anos da Educação Infantil por Taxa de Infrequência na RME")
    st.write('Acumulado de Fevereiro à  %s de %s - Dias Letivos no período: %s - Dados atualizados em %s'%(meses[mes], ano, dias_letivos, DT_ATUALIZACAO))

    resultado = busca_resultados(dias_letivos, ano)

    total_0_35 = resultado['_0_35'].sum(axis=0)
    total_35_40 = resultado['_35_40'].sum(axis=0)
    total_40_100 = resultado['_40_100'].sum(axis=0)
    total = resultado['total'].sum(axis=0)

    #col1, col2, col3, col4 = st.columns(4)
    '''
    col1.metric(
                label='Menor ou igual à 10%', 
                value= str(round(100*(total_0_10/total), 1))+'%'
                )
    col2.metric(
                label='Entre 10% e 20%', 
                value=str(round(100*(total_10_20/total), 1))+'%'
                )
    '''
    col3, col4 = st.columns(2)
    col3.metric(
                label='Entre 35% e 40%', 
                value=str(round(100*(total_35_40/total), 1))+'%'
                )
    col4.metric(
                label='Maior ou igual à 40%', 
                value=str(round(100*(total_40_100/total), 1))+'%'
                )
    style_metric_cards()

    options = {
        'chart': {
          'type': 'bar',
          'height': 1000,
          'stacked': True,
          'stackType': '100%'
        },
        'colors': ['#1ED0DF', '#ffa500', "#ff0000"],
        'plotOptions': {
          'bar': {
            'horizontal': True,
          },
        },
        'stroke': {
          'width': 1,
          'colors': ['#fff']
        },
        'title': {
                'text': 'Percentual de Alunos de 4 e 5 anos da Educação Infantil por Taxa de Infrequência nas Regionais',
                'horizontalAlign': 'center',
        },
        'subtitle': {
                'text': 'Acumulado de Fevereiro à  %s de %s - Dias Letivos no período: %s'%(meses[mes], ano, dias_letivos),
        },  
        'xaxis': {
          'categories':  ['BARREIRO','CENTRO SUL','LESTE','NORDESTE','NOROESTE','NORTE','OESTE','PAMPULHA','VENDA NOVA'],
        },
        'legend': {
          'position': 'top',
          'horizontalAlign': 'center',
          'offsetX': 40
        }
    }
    series = [dict(name='Menor que 35%',data=resultado['p_0_35'].tolist()),
              dict(name='Entre 35% e 40%',data=resultado['p_35_40'].tolist()),
              dict(name='Maior ou igual à 40%',data=resultado['p_40_100'].tolist())]

    st_apexcharts(options, series, 'bar', 1100)    

    rename = {
        'regional':'Regional', 
        '_0_35':'Menor que 35%', 
        '_35_40':'Entre 35% e 40%', 
        '_40_100':'Maior ou igual à 40%', 
        'total':'Total'
    }
    
    df=resultado[['regional', '_0_35', '_35_40', '_40_100', 'total']].rename(columns=rename)

    st.write('Total de Alunos de 4 e 5 anos da Educação Infantil por Taxa de Infrequência nas Regionais')
    st.dataframe(df, hide_index=True, use_container_width=True)



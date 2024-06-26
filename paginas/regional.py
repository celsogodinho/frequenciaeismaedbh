import streamlit as st
from helpers import obtem_conexao, meses
from streamlit_apexjs import st_apexcharts
from streamlit_extras.metric_cards import style_metric_cards

@st.cache_data
def busca_resultados(regional_id, dias_letivos, ano):
    conn = obtem_conexao()
    sql_35 = '''
        select e.cod_escl cod_escl, count(fa.cod_aluno) _0_35
        from faltas_acumuladas fa, aluno a , escola e, turma t
        where ano = %s
        and a.cod_aluno = fa.cod_aluno 
        and e.cod_escl = a.cod_escl_atua
        and e.regional = %s
        and t.cod_sequ_turm = a.cod_turm_atua
        and t.ensino in (5,6)
        and 100*(cast(fa.total_sem_jus as float)/%s) < 35.0
        group by e.cod_escl 
    '''%(ano, regional_id, dias_letivos)

    data_menor_35 = conn.query(sql_35)

    sql_35_40 = '''
        select e.cod_escl cod_escl, count(fa.cod_aluno) _35_40
        from faltas_acumuladas fa, aluno a , escola e, turma t
        where ano = %s
        and a.cod_aluno = fa.cod_aluno 
        and e.cod_escl = a.cod_escl_atua
        and e.regional = %s
        and t.cod_sequ_turm = a.cod_turm_atua
        and t.ensino in (5,6)
        and 100*(cast(fa.total_sem_jus as float)/%s) >= 35.0
        and 100*(cast(fa.total_sem_jus as float)/%s) <= 40.0
        group by e.cod_escl
    '''%(ano, regional_id, dias_letivos, dias_letivos)
    data_35_40 = conn.query(sql_35_40)

    sql_maior_40 = '''
        select e.cod_escl cod_escl, count(fa.cod_aluno) _40_100
        from faltas_acumuladas fa, aluno a , escola e, turma t
        where ano = %s
        and a.cod_aluno = fa.cod_aluno 
        and e.cod_escl = a.cod_escl_atua
        and e.regional = %s
        and t.cod_sequ_turm = a.cod_turm_atua
        and t.ensino in (5,6)
        and 100*(cast(fa.total_sem_jus as float)/%s) >= 25.0
        group by e.cod_escl
    '''%(ano, regional_id, dias_letivos)

    data_maior_40 = conn.query(sql_maior_40)


    #sql_escola = 'select cod_escl, nome from escola where regional=%s order by nome'%regional_id
    sql_escola = '''
    select distinct e.cod_escl, e.nome 
    from escola e, turma t
    where 
    t.cod_escl = e.cod_escl
    and t.ensino in (5,6)
    and regional=%s 
    order by nome
    '''%regional_id
    escolas = conn.query(sql_escola)

    result = escolas.merge(data_menor_35, on='cod_escl', how='left')
    result = result.merge(data_35_40, on='cod_escl', how='left')
    result = result.merge(data_maior_40, on='cod_escl', how='left')

    result.fillna(0, inplace=True)

    result['total'] = result['_0_35'] + result['_35_40'] + result['_40_100']
    result['p_0_35'] = 100*result['_0_35']/result['total']
    result['p_35_40'] = 100*result['_35_40']/result['total']
    result['p_40_100'] = 100*result['_40_100']/result['total']


    return result


def regional(nome_regional, regional_id, dias_letivos, ano, mes):
    st.header("Secretaria Municipal de Educação - PBH", divider='rainbow')
    st.subheader('Percentual de Alunos de 4 e 5 anos da Educação Infantil do Ensino Fundamental por Taxa de Infrequência na %s'%nome_regional)
    st.write('Acumulado de Fevereiro à  %s de %s - Dias Letivos no período: %s'%(meses[mes], ano, dias_letivos))

    resultado = busca_resultados(regional_id, dias_letivos, ano)

    total_0_35 = resultado['_0_35'].sum(axis=0)
    total_35_40 = resultado['_35_40'].sum(axis=0)
    total_40_100 = resultado['_40_100'].sum(axis=0)
    total = resultado['total'].sum(axis=0)

    #col1, col2, col3, col4 = st.columns(4)
    #col1.metric(label='Menor ou igual à 10%', value= str(round(100*(total_0_10/total), 1))+'%')
    #col2.metric(label='Entre 10% e 20%', value=str(round(100*(total_10_20/total), 1))+'%')
    col3, col4 = st.columns(2)
    col3.metric(label='Entre 35% e 40%', value=str(round(100*(total_35_40/total), 1))+'%')
    col4.metric(label='Maior ou igual à 40%', value=str(round(100*(total_40_100/total), 1))+'%')
    style_metric_cards()


    options = {
        'chart': {
          'type': 'bar',
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
                'text': 'Percentual de Alunos de 4 e 5 anos da Educação Infantil por Taxa de Infrequência nas escolas da %s'%nome_regional,
                'horizontalAlign': 'center',
        },
        'subtitle': {
                'text': 'Acumulado de Fevereiro à  %s de %s - Dias Letivos no período: %s'%(meses[mes], ano, dias_letivos),
        },  
        'yaxis': {
            'labels': {
                'maxWidth': 500,
            }            
        },      
        'xaxis': {
          'categories':  resultado['nome'].tolist(),
        },
        'fill': {
          'opacity': 1
        },
        'legend': {
          'position': 'top',
          'horizontalAlign': 'center',
          'offsetX': 50
        }
    }
    series = [dict(name='Menor que 35%',data=resultado['p_0_35'].tolist()),
              dict(name='Entre 35% e 40%',data=resultado['p_35_40'].tolist()),
              dict(name='Maior ou igual à 40%',data=resultado['p_40_100'].tolist())]

    st_apexcharts(options, series, 'bar', 1100)    

    rename = {
        'nome':'Local', 
        '_0_35':'Menor que 35%', 
        '_35_40':'Entre 35% e 40%', 
        '_40_100':'Maior ou igual à 40%', 
        'total':'Total'
    }
    
    df=resultado[['nome', '_0_35', '_35_40', '_40_100', 'total']].rename(columns=rename)

    st.write('Total de Alunos de 4 e 5 anos da Educação Infantil por Taxa de Infrequência nas escolas da %s'%nome_regional)
    st.dataframe(df, hide_index=True, use_container_width=True)


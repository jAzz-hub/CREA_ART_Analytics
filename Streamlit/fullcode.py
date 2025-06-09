import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re
from pandas import ExcelFile
import time
from io import BytesIO

# Lambda functions for data processing
removendo_numeros = lambda frase: re.sub(r'[0-9]', '', frase)

TOS_passageiros = lambda frase: f"Arquitetura Naval de Navio de {frase}" if "18.1" in frase else f"Transportadores e Elevadores de {frase}"

especificar_TOS = lambda frase: TOS_passageiros(frase) if frase.find("passageiros") != -1 else frase

cut_TOS = lambda col: removendo_numeros(especificar_TOS(
    re.sub(r',\s*\[.*\]*', '', re.sub(r'(-\s*de|\.|-)', '', str(col).split('|')[2]))[:-1]
))

# Set page config
st.set_page_config(
    page_title="CREA-MG - Relatório de Inspeções",
    page_icon="🏗️",
    layout="wide",  # Alterado de "centered" para "wide" para usar mais espaço
    initial_sidebar_state="expanded"
)

# Função para carregar e pré-processar os dados com caching
@st.cache_data(
    ttl=604800,
    show_spinner=True,
    persist="disk",
    hash_funcs={BytesIO: lambda _: None}
)
def load_data():
    start_time = time.time()
    years = ExcelFile('..\\Dados\\PESQUISA DE ART 2022 2023 2024.xlsx').sheet_names
    dfs = [pd.read_excel('..\\Dados\\PESQUISA DE ART 2022 2023 2024.xlsx', sheet_name=f"{i}", header=7).dropna() for i in years]
    dfs[1] = dfs[1].iloc[:, 1:].copy()
    dfs[1].rename(columns={
        'DATA REGISTRO': 'CIDADE',
        'TITULOS': 'DATA REGISTRO',
        'ATIVIDADES': 'TITULOS',
        'OBSERVACAO OBRA SERVICO': 'ATIVIDADES',
        'Unnamed: 6': 'OBSERVACAO OBRA SERVICO'
    }, inplace=True)
    dfs[0]['ATIVIDADES_INSPECIONADAS'] = dfs[0]['ATIVIDADES'].apply(cut_TOS)
    dfs[1]['ATIVIDADES_INSPECIONADAS'] = dfs[1]['ATIVIDADES'].apply(cut_TOS)
    dfs[2]['ATIVIDADES_INSPECIONADAS'] = dfs[2]['ATIVIDADES'].apply(cut_TOS)
    end_time = time.time()
    load_time = end_time - start_time
    return dfs, load_time

dfs, load_time = load_data()

# Custom CSS for CREA-MG styling
def inject_custom_css():
    st.markdown("""
    <style>
        :root {
            --crea-blue: #003366;
            --crea-yellow: #FFCC00;
        }
        .stApp header {
            background-color: var(--crea-blue);
            color: white;
        }
        .stButton button {
            background-color: var(--crea-blue) !important;
            color: white !important;
            border: none;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            background-color: #004b8d !important;
            transform: translateY(-2px);
        }
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
            border-right: 2px solid var(--crea-blue);
        }
        h1 {
            color: var(--crea-blue) !important;
            border-bottom: 2px solid var(--crea-yellow);
            padding-bottom: 10px;
        }
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: var(--crea-blue);
            color: white;
            text-align: center;
            padding: 10px;
            font-size: 0.9rem;
        }
        .main .block-container {
            padding-bottom: 120px; /* Aumentado para evitar sobreposição com footer */
            max-width: 1400px !important; /* Aumenta o contêiner principal */
        }
        /* Ajuste para gráficos maiores */
        .st-pyplot {
            width: 100% !important;
            min-width: 1000px !important; /* Garante um tamanho mínimo */
            max-width: 1400px !important; /* Aumenta o tamanho máximo */
            height: 800px !important; /* Define uma altura fixa para o gráfico */
            margin: 0 auto;
        }
        .st-pyplot img {
            width: 100% !important;
            height: auto !important;
        }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# Função para criar o gráfico com identidade visual CREA-MG
def create_crea_plot(data, year):
    """
    Cria um gráfico de barras horizontais com o padrão visual do CREA-MG.
    
    Args:
        data (pd.DataFrame): DataFrame contendo os dados para o gráfico.
        year (int): Ano correspondente aos dados.
    
    Returns:
        matplotlib.figure.Figure: Figura gerada com o gráfico.
    """
    a = data['ATIVIDADES_INSPECIONADAS'].value_counts(normalize=True) * 100
    
    # Configuração do gráfico com tamanho maior e maior resolução
    fig = plt.figure(figsize=(22, 18), facecolor='white', dpi=100)  # Aumentado para (22, 18) e dpi=100
    ax = plt.gca()
    
    # Configuração de cores
    ax.set_facecolor('white')
    bars = plt.barh(a.head(10).keys(), 
                    a.head(10).values, 
                    color='#003366')

    # Textos e rótulos
    plt.xlabel("Percentual de Inspeções (%)", color='#003366', fontweight='bold', fontsize=14)  # Aumentado fontsize
    plt.ylabel("Atividades", color='#003366', fontweight='bold', fontsize=14)
    plt.title(f"Ranking de Atividades Inspecionadas - {year}", 
              color='#003366', 
              fontweight='bold', 
              fontsize=18,  # Aumentado fontsize
              pad=20)

    # Configurações do eixo
    ax.tick_params(axis='both', colors='#003366', labelsize=12)  # Aumentado labelsize
    ax.xaxis.label.set_color('#003366')
    ax.yaxis.label.set_color('#003366')

    # Configuração das bordas
    for spine in ax.spines.values():
        spine.set_color('#003366')

    # Grid sutil
    ax.xaxis.grid(True, color='#CCCCCC', linestyle='--', alpha=0.7)

    # Adicionar porcentagens nas barras
    for bar in bars:
        width = bar.get_width()
        plt.text(width * 1.01, 
                 bar.get_y() + bar.get_height()/2, 
                 f'{width:.1f}%', 
                 va='center', 
                 ha='left', 
                 color='#003366',
                 fontsize=10)  # Aumentado fontsize

    # Adicionar logo do CREA-MG
    plt.figtext(0.95, 0.02, "CREA-MG", 
                fontsize=14,  # Aumentado fontsize
                color='#003366', 
                ha='right', 
                fontweight='bold')
    plt.figtext(0.95, 0.002, "www.crea-mg.org.br", 
                fontsize=10, 
                color='#003366', 
                ha='right')

    # Ajuste de layout
    plt.tight_layout()
    plt.subplots_adjust(left=0.2, bottom=0.1)
    
    return fig

# Main app
def main():
    st.title("CREA-MG - Relatório de Inspeções Técnicas")
    st.markdown("---")
    
    # st.markdown(f"**Tempo de carregamento do dataset:** {load_time:.2f} segundos")
    # st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        btn_2022 = st.button("2022", key="2022")
    with col2:
        btn_2023 = st.button("2023", key="2023")
    with col3:
        btn_2024 = st.button("2024", key="2024")
    
    st.markdown("---")
    
    if btn_2022:
        year = 2022
        df = dfs[0]
    elif btn_2023:
        year = 2023
        df = dfs[1]
    elif btn_2024:
        year = 2024
        df = dfs[2]
    else:
        year = 2023
        df = dfs[1]
    
    # Usar um container para o gráfico
    with st.container():
        with st.spinner(f"Gerando relatório para {year}..."):
            fig = create_crea_plot(df, year)
            st.pyplot(fig, use_container_width=True)  # Usa toda a largura do contêiner
    
    st.markdown("---")
    st.markdown(
        """
        <div class="footer">
            <p>Conselho Regional de Engenharia e Agronomia de Minas Gerais</p>
            <p>Av. Álvares Cabral, 1600 - Santo Agostinho, Belo Horizonte - MG</p>
            <p><a href="http://www.crea-mg.org.br" target="_blank" style="color: #FFCC00;">www.crea-mg.org.br</a></p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
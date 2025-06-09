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
    layout="centered",
    initial_sidebar_state="expanded"
)

# Função para carregar e pré-processar os dados com caching
@st.cache_data(
    ttl=604800,  # Cache expira após 1 semana (604800 segundos)
    show_spinner=True,
    persist="disk",  # Armazena em disco para sobreviver a reinícios
    hash_funcs={BytesIO: lambda _: None}  # Ignora hash para BytesIO
)
def load_data():
    start_time = time.time()  # Início da medição do tempo
    
    # Carregar o arquivo Excel
    years = ExcelFile('..\\Dados\\PESQUISA DE ART 2022 2023 2024.xlsx').sheet_names
    dfs = [pd.read_excel('..\\Dados\\PESQUISA DE ART 2022 2023 2024.xlsx', sheet_name=f"{i}", header=7).dropna() for i in years]
    
    # Pré-processamento do DataFrame de 2023 (índice 1)
    dfs[1] = dfs[1].iloc[:, 1:].copy()
    dfs[1].rename(columns={
        'DATA REGISTRO': 'CIDADE',
        'TITULOS': 'DATA REGISTRO',
        'ATIVIDADES': 'TITULOS',
        'OBSERVACAO OBRA SERVICO': 'ATIVIDADES',
        'Unnamed: 6': 'OBSERVACAO OBRA SERVICO'
    }, inplace=True)
    
    # Aplicar cut_TOS para criar a coluna ATIVIDADES_INSPECIONADAS em todos os DataFrames
    dfs[0]['ATIVIDADES_INSPECIONADAS'] = dfs[0]['ATIVIDADES'].apply(cut_TOS)
    dfs[1]['ATIVIDADES_INSPECIONADAS'] = dfs[1]['ATIVIDADES'].apply(cut_TOS)
    dfs[2]['ATIVIDADES_INSPECIONADAS'] = dfs[2]['ATIVIDADES'].apply(cut_TOS)
    
    end_time = time.time()  # Fim da medição do tempo
    load_time = end_time - start_time  # Tempo total em segundos
    
    return dfs, load_time  # Retorna os dados e o tempo de carregamento

dfs, load_time = load_data()

# Custom CSS for CREA-MG styling
def inject_custom_css():
    st.markdown("""
    <style>
        /* Main colors */
        :root {
            --crea-blue: #003366;
            --crea-yellow: #FFCC00;
        }
        
        /* Header */
        .stApp header {
            background-color: var(--crea-blue);
            color: white;
        }
        
        /* Buttons */
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
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
            border-right: 2px solid var(--crea-blue);
        }
        
        /* Titles */
        h1 {
            color: var(--crea-blue) !important;
            border-bottom: 2px solid var(--crea-yellow);
            padding-bottom: 10px;
        }
        
        /* Footer */
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
        
        /* Container */
        .main .block-container {
            padding-bottom: 100px; /* Space for footer */
        }
        .stPlotlyChart, .st-pyplot {
            width: 200% !important;
            max-width: 2200 !important; /* Aumenta o tamanho máximo do gráfico */
            margin: 0 auto;
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
    
    # Configuração do gráfico
    fig = plt.figure(figsize=(18, 16), facecolor='white')
    ax = plt.gca()
    
    # Configuração de cores
    ax.set_facecolor('white')  # Fundo do gráfico branco
    bars = plt.barh(a.head(10).keys(), 
                    a.head(10).values, 
                    color='#003366')  # Barras azul escuro

    # Textos e rótulos
    plt.xlabel("Percentual de Inspeções (%)", color='#003366', fontweight='bold', fontsize=12)
    plt.ylabel("Atividades", color='#003366', fontweight='bold', fontsize=12)
    plt.title(f"Ranking de Atividades Inspecionadas - {year}", 
              color='#003366', 
              fontweight='bold', 
              fontsize=16,
              pad=20)

    # Configurações do eixo
    ax.tick_params(axis='both', colors='#003366', labelsize=10)
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
                 fontsize=9)

    # Adicionar logo do CREA-MG
    plt.figtext(0.95, 0.02, "CREA-MG", 
                fontsize=12, 
                color='#003366', 
                ha='right', 
                fontweight='bold')
    plt.figtext(0.95, 0.002, "www.crea-mg.org.br", 
                fontsize=9, 
                color='#003366', 
                ha='right')

    # Ajuste de layout
    plt.tight_layout()
    plt.subplots_adjust(left=0.2, bottom=0.1)  # Espaço para labels
    
    return fig

# Main app
def main():
    st.title("CREA-MG - Relatório de Inspeções Técnicas")
    st.markdown("---")
    
    # Exibir o tempo de carregamento do dataset
    # st.markdown(f"**Tempo de carregamento do dataset:** {load_time:.2f} segundos")
    # st.markdown("---")
    
    # Year selection
    col1, col2, col3 = st.columns(3)
    with col1:
        btn_2022 = st.button("2022", key="2022")
    with col2:
        btn_2023 = st.button("2023", key="2023")
    with col3:
        btn_2024 = st.button("2024", key="2024")
    
    st.markdown("---")
    
    # Determine which year to show
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
        # Default to current year
        year = 2023
        df = dfs[1]
    
    # Create and display plot
    with st.spinner(f"Gerando relatório para {year}..."):
        fig = create_crea_plot(df, year)
        st.pyplot(fig)
    
    # Footer
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
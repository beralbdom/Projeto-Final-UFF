# Created on Tue Oct 22 2024
# Descrição do arquivo...
# Copyright (c) Bernardo Albuquerque Domingues
# https://github.com/beralbdom \ dominguesbernardo@id.uff.br
# -------------------------------------------------------------------------------------------------------------------- #

import numpy as np
import pandas as pd
import requests
import urllib3
from concurrent.futures import ThreadPoolExecutor
from alive_progress import alive_bar

global teleconexoes                                                                                                     # https://psl.noaa.gov/data/climateindices/list/
teleconexoes = {
    'AAO':     'https://psl.noaa.gov/data/correlation/aao.data',
    'AMM':     'https://psl.noaa.gov/data/timeseries/monthly/AMM/ammsst.data',
    'AMO':     'https://psl.noaa.gov/data/correlation/amon.us.data',
    'AO':      'https://psl.noaa.gov/data/correlation/ao.data',
    'BEST':    'https://psl.noaa.gov/data/correlation/censo.data',
    'CAR':     'https://psl.noaa.gov/data/correlation/CAR_ersst.data',
    'EA':      'https://psl.noaa.gov/data/correlation/ea.data',
    'EPNP':    'https://psl.noaa.gov/data/correlation/epo.data',
    'ESPI':    'https://psl.noaa.gov/data/correlation/espi.data',
    'GMSST':   'https://psl.noaa.gov/data/correlation/gmsst.data',
    # 'IASAS':   'https://meteorologia.unifei.edu.br/teleconexoes/cache/iasas.txt',                                     # problema nos dados
    'IOD':     'https://psl.noaa.gov/gcos_wgsp/Timeseries/Data/dmi.had.long.data',
    # 'ITSMRG2': 'https://meteorologia.unifei.edu.br/teleconexoes/cache/itsmrg2.txt',
    'MEI':     'https://psl.noaa.gov/data/correlation/mei.data',
    'MEI V2':  'https://psl.noaa.gov/data/correlation/meiv2.data',
    'NAO':     'https://psl.noaa.gov/data/correlation/nao.data',
    'NOI':     'https://psl.noaa.gov/data/correlation/noi.data',
    'NIN1+2':  'https://psl.noaa.gov/data/correlation/nina1.anom.data',
    'NIN3':    'https://psl.noaa.gov/data/correlation/nina3.anom.data',
    'NIN3.4':  'https://psl.noaa.gov/data/correlation/nina34.anom.data',
    'NIN4':    'https://psl.noaa.gov/data/correlation/nina4.anom.data',
    'NTA':     'https://psl.noaa.gov/data/correlation/NTA_ersst.data',
    'ONI':     'https://psl.noaa.gov/data/correlation/oni.data',
    'PACWARM': 'https://psl.noaa.gov/data/correlation/pacwarm.data',
    'PDO':     'https://psl.noaa.gov/data/correlation/pdo.data',
    'PNA':     'https://psl.noaa.gov/data/correlation/pna.data',
    'PWR':     'https://psl.noaa.gov/data/correlation/pacwarm.data',
    'QBO':     'https://psl.noaa.gov/data/correlation/qbo.data',
    # 'SAODI':   'https://meteorologia.unifei.edu.br/teleconexoes/cache/saodi.txt',
    # 'SASDI':   'https://meteorologia.unifei.edu.br/teleconexoes/cache/sasdi.txt',
    # 'SIOD':    'https://meteorologia.unifei.edu.br/teleconexoes/cache/siod.txt',
    'SOI':     'https://psl.noaa.gov/data/correlation/soi.data',
    'TNA':     'https://psl.noaa.gov/data/correlation/tna.data',
    'TNI':     'https://psl.noaa.gov/data/correlation/tni.data',
    'TSA':     'https://psl.noaa.gov/data/correlation/tsa.data',
    'WHWP':    'https://psl.noaa.gov/data/correlation/whwp.data',
    'WP':      'https://psl.noaa.gov/data/correlation/wp.data',
}

global invalid_val                                                                                                      # Valores inválidos para cada índice
invalid_val = {
    'AAO':      -9999,
    'AMM':      -99,
    'AMO':      -99.990,
    'AO':       -999,
    'BEST':     -9.99,
    'CAR':      -99.99,
    'EA':       -99.9,
    'EPNP':     -99.9,
    'ESPI':     -999.0,
    'GMSST':    9999,
    # 'IASAS':    9999,
    'IOD':      -9999,
    # 'ITSMRG2':  9999,
    'MEI':      -999,
    'MEI V2':   -999,
    'NAO':      -99.9,
    'NIN1+2':   -99.99,
    'NIN3':     -99.99,
    'NIN3.4':   -99.99,
    'NIN4':     -99.99,
    'NTA':      -99.99,
    'NOI':      -999.0,
    'ONI':      -99.9,
    'PACWARM':  -9999,
    'PDO':      -9.9,
    'PNA':      -99.9,
    'PWR':      -9999,
    'QBO':      -999,
    # 'SAODI':    9999,
    # 'SASDI':    9999,
    # 'SIOD':     9999,
    'SOI':      -99.99,
    'TNA':      -99.99,
    'TNI':      -99.99,
    'TSA':      -99.99,
    'WHWP':     -99.99,
    'WP':       -99.9
}


def GetGeracao(anos, base_url):
    def DownloadAno(ano):
        if ano < 2022:                                                                                                  # Antes de 2022 os dados de geração são anuais
            url = base_url + f'GERACAO_USINA-2_{ano}.csv'
            response = requests.get(url, stream = True, verify = True)                                                  # Stream = True para não carregar tudo na memória
            if response.status_code == 200:
                with open('Exportado/ONS/GERACAO_USINA-2_' + f'{ano}.csv', 'wb') as file:
                    for chunk in response.iter_content(chunk_size = 10240000):                                          # Chunks de 10MB pra não usar muita ram
                        if chunk:
                            file.write(chunk)
                            file.flush()
                print(f'[✓] Dados de {ano} baixados com sucesso de {url}')
                return True
            else:
                print(f'[!] Falha ao baixar os dados de geração de {url}')
                return False
        else:                                                                                                           # A partir de 2022 os dados de geração são mensais
            concluido = False                                                                                           # Flag para verificar se todos os meses foram baixados antes de ir para o próximo ano
            for mes in np.arange(1, 13, 1):
                if mes < 10: mes = f'0{mes}'                                                                            # Ghetto pra meses menores que 10
                url = base_url + f'GERACAO_USINA-2_{ano}_{mes}.csv'
                response = requests.get(url, stream = True, verify = True)
                if response.status_code == 200:
                    with open('Exportado/ONS/GERACAO_USINA-2_' + f'{ano}_{mes}.csv', 'wb') as file:
                        for chunk in response.iter_content(chunk_size = 10240000):
                            if chunk:
                                file.write(chunk)
                                file.flush()
                    print(f'[✓] Dados de {mes}/{ano} baixados com sucesso de {url}')
                    concluido = True
                else:
                    print(f'[!] Falha ao baixar os dados de geração de {url}')
                    concluido = False
            return concluido
        
    with alive_bar(
        len(anos),
        title = f'Baixando dados de geração...',
        bar = None,
        spinner = 'classic',
        enrich_print = False,
        stats = '(ETA: {eta})',
        monitor = '{count}/{total}',
        elapsed = '    ⏱ {elapsed}'
    ) as bar:
        with ThreadPoolExecutor(max_workers = None) as executor:
            futures = [executor.submit(DownloadAno, ano) for ano in anos]                                               # Baixando os dados de geração de cada ano em paralelo
            for f in futures:
                f.result()
                bar()


def GetVazao(anos, base_url):
    def DownloadAno(ano):
        url = base_url + f'DADOS_HIDROLOGICOS_RES_{ano}.csv'
        response = requests.get(url, stream = True, verify = True)

        if response.status_code == 200:
            with open(f'Exportado/ONS/DADOS_HIDROLOGICOS_RES_{ano}.csv', 'wb') as file:
                for chunk in response.iter_content(chunk_size = 1024000):
                    if chunk:
                        file.write(chunk)
                        file.flush()
            print(f'[✓] Dados de vazão de {ano} baixados com sucesso de {url}')
            bar()
            return True
        
        else:
            print(f'[!] Falha ao baixar os dados de vazão de {url}')
            bar()
            return False

    with alive_bar(
        len(anos),
        title = 'Baixando dados de vazão...',
        bar = None,
        spinner = 'classic',
        enrich_print = False,
        stats = '(ETA: {eta})',
        monitor = '{count}/{total}',
        elapsed = '    ⏱ {elapsed}'
    ) as bar:
        with ThreadPoolExecutor(max_workers = None) as executor:
            executor.map(DownloadAno, anos)                                                                                  # Baixando os dados de vazão de cada ano em paralelo


def GetCarga(anos, base_url):
    def DownloadAno(ano):
        url = base_url + f'CURVA_CARGA_{ano}.csv'
        response = requests.get(url, stream = True, verify = True)

        if response.status_code == 200:
            with open(f'Exportado/ONS/CURVA_CARGA_{ano}.csv', 'wb') as file:
                for chunk in response.iter_content(chunk_size = 1024000):
                    if chunk:
                        file.write(chunk)
                        file.flush()
            print(f'[✓] Dados de carga de {ano} baixados com sucesso de {url}')
            return True
        else:
            print(f'[!] Falha ao baixar os dados de carga de {url}')
            return False

    with alive_bar(
        len(anos),                                                                                                      # Tamanho
        title = 'Baixando dados de carga...',                                                                           # Título
        bar = None,
        spinner = 'classic',
        enrich_print = False,
        stats = '(ETA: {eta})',
        monitor = '{count}/{total}',
        elapsed = '    ⏱ {elapsed}'
    ) as bar:
        with ThreadPoolExecutor(max_workers = None) as executor:
            futures = [executor.submit(DownloadAno, ano) for ano in anos]                                              # Cria uma lista de futuros para cada ano 
            for f in futures:
                f.result()
                bar()


def GetIndices():
    with alive_bar(
        len(teleconexoes),
        title = 'Baixando índices de teleconexões...',
        bar = None,                                                                                                     # Barra de progresso
        spinner = 'classic',                                                                                            # Spinner
        enrich_print = False,                                                                                           # Desativando 'on <iter>:' antes dos prints
        stats = '(~{eta})',                                                                                             # Estimativa de tempo
        monitor = '{count}/{total}',                                                                                    # Monitor
        elapsed = 'em {elapsed}'
    ) as bar:
        for index, url in teleconexoes.items():
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.get(url, verify = False)
            if response.status_code == 200:
                with open('Exportado/Indices/' + f'{index}.txt', 'wb') as file:
                    file.write(response.content)
                print(f'[✓] Índice {index} baixado com sucesso de {url}')
            else:
                print(f'[!] Falha ao baixar o índice {index} de {url}')
            bar()


def IndiceParaDataFrame(index):
    dir = 'Exportado/Indices/' + f'{index}.txt'
    try:
        with open(dir, 'r') as file:
            linhas = file.readlines()
        
        if 'psl.noaa.gov' in teleconexoes[index]:
            linhas = [linha for linha in linhas if len(linha.split()) == 13]                                            # Considerando apenas as linhas com 13 colunas (1 ano e 12 meses)
            df = pd.DataFrame([linha.split() for linha in linhas])
            df.columns = ['Year'] + [f'Month_{i}' for i in range(1, 13)]                                                # Cada linha é um ano e cada coluna é um mês
            df = df.melt(id_vars = ['Year'], var_name = 'Month', value_name = str(index))                               # Transforma as colunas de meses em linhas (transforma dataframe wide em long)
            df['Month'] = df['Month'].str.extract(r'(\d+)').astype(int)                                                 # Extrai o número do mês
            df['Data'] = pd.to_datetime(df[['Year', 'Month']].assign(DAY = 1)).dt.to_period('M')                        # Cria a coluna Data com o formato de período
            df = df.set_index('Data').drop(columns = ['Year', 'Month'])
            df[str(index)] = pd.to_numeric(df[str(index)], errors = 'coerce')
            df = df.reset_index().sort_index()

        elif 'meteorologia.unifei.edu.br' in teleconexoes[index]:
            df = pd.DataFrame([linha.split(';') for linha in linhas[1:]], columns = ['Data', str(index)])
            df['Data'] = pd.to_datetime(df['Data'].str[3:], format = '%d%b%Y')
            df['Data'] = df['Data'].dt.to_period('M')
            df = df.set_index('Data')
            df[str(index)] = pd.to_numeric(df[str(index)], errors = 'coerce')
            df = df.reset_index().sort_index()

        return df

    except Exception as e:
        print(f'Erro ao ler o índice {index}: {e}')
        return None


def ProcessarDadosGeracao(df):
    df['Tipo'] = df['Tipo'].replace({'Gás': 'Térmica',
                                    'Carvão': 'Térmica',
                                    'Óleo Combustível': 'Térmica',
                                    'Nuclear': 'Térmica',
                                    'Óleo Diesel': 'Térmica',
                                    'Multi-Combustível Diesel/Óleo': 'Térmica'})
    
    df['Tipo'] = df['Tipo'].replace({'Outras Multi-Combustível': 'Outras',
                                    'Resíduos Industriais': 'Outras',
                                    'Biomassa': 'Outras'})

    df_total_horario = df.pivot_table(index = 'Data',
                                    columns = 'Tipo',
                                    values = 'Geracao',
                                    aggfunc = 'sum')
    
    for tipo in df_total_horario.columns:
        df_tipo = df[df['Tipo'] == tipo].pivot_table(index = 'Data',
                                                    columns = 'Subsistema',
                                                    values = 'Geracao',
                                                    aggfunc = 'sum')

        df_tipo.columns = [f'{tipo}_{col}' for col in df_tipo.columns]
        df_total_horario = df_total_horario.join(df_tipo, how = 'outer')

    df_total_diario = df_total_horario.resample('D').sum()
    df_total_mensal = df_total_horario.resample('MS').sum()
    df_total_diario.to_csv('Exportado/geracao_fontes_diario.csv', index = True, encoding = 'utf-8')
    df_total_mensal.to_csv('Exportado/geracao_fontes_mensal.csv', index = True, encoding = 'utf-8')


def AnomaliaCarga(merged_df):
    df_men = merged_df.pivot_table(index = 'Data',                                                                      # Carga mensal total por subsistema
                                   columns = 'Subsistema',
                                   values = 'Carga',
                                   aggfunc = 'sum')
    
    df_med = df_men.groupby(df_men.index.month).mean()                                                                  # Média mensal de carga por subsistema (média de cada mês ao longo dos anos)

    df_ind = df_men.copy()
    for mes in range(1, 13):
        df_ind.loc[df_ind.index.month == mes] = df_men.loc[df_men.index.month == mes] - df_med.loc[mes].squeeze()       # Anomalia de carga por subsistema (carga mensal total observada - média  do mês ao longo dos anos)

    df_ind = df_ind.rolling(window = 3, min_periods = 1).mean()                                                         # Média móvel de 3 meses
    df_ind = df_ind.div(df_ind.std()).reset_index()                                                                     # Normalização (Z-score)

    return df_men, df_med, df_ind


def AnomaliaVazao(df_vazoes):
    df_men = df_vazoes                                                                                                  # Vazão mensal total por bacia

    for col in df_men.columns:
        df_men[col] = pd.to_numeric(df_men[col], downcast = 'float', errors = 'coerce')                                                     # Convertendo para numérico

    df_med = df_men.groupby(df_men.index.month).mean()                                                                  # Média mensal de vazão por bacia (média de cada mês ao longo dos anos)

    df_ind = df_men.copy()
    for mes in range(1, 13):
        df_ind.loc[df_ind.index.month == mes] = df_men.loc[df_men.index.month == mes] - df_med.loc[mes].squeeze()       # Anomalia de vazão por bacia (vazão mensal total observada - média do mês ao longo dos anos)
    df_ind = df_ind.rolling(window = 3, min_periods = 1).mean()                                                         # Média móvel de 3 meses
    df_ind = df_ind.div(df_ind.std()).reset_index()                                                                     # Normalização (Z-score)

    return df_men, df_med, df_ind


def ExportarDados(tipo, anos, merge = True, export = True):
    if tipo == 'vazoes':
        dfs_vaz = [pd.DataFrame() for _ in range(len(anos))]
        for i, ano in enumerate(anos):
            df = pd.read_csv('Exportado/ONS/' + f'DADOS_HIDROLOGICOS_RES_{ano}.csv', 
                            sep = ';', 
                            decimal = '.', 
                            usecols = ['din_instante', 'id_subsistema', 'val_nivelmontante', 'val_niveljusante', 
                                       'val_volumeutilcon', 'val_vazaoafluente', 'val_vazaoturbinada', 
                                       'val_vazaovertida', 'val_vazaooutrasestruturas', 'val_vazaodefluente', 
                                       'val_vazaotransferida', 'val_vazaonatural', 'val_vazaoartificial', ''
                                       'val_vazaoincremental', 'val_vazaoevaporacaoliquida', 'val_vazaousoconsuntivo'])
            
            df = df.rename(columns = {'din_instante': 'Data', 
                                      'id_subsistema': 'Subsistema'})
            
            df['Data'] = pd.to_datetime(df['Data'], format = '%Y-%m-%d')
            dfs_vaz[i] = df

        merged_df = pd.concat(dfs_vaz, ignore_index = True).set_index('Data')
        merged_df = merged_df.groupby(['Data', 'Subsistema']).sum()
        merged_df = merged_df.unstack(level = 1)                                                                        # Transforma o dataframe em wide (Data como índice e Subsistema como colunas)

        merged_df.columns = [f'{col[1]}_{col[0]}' for col in merged_df.columns]                                        # Renomeia as colunas para <subsistema>_<tipo>


        merged_df.to_csv('Exportado/dados_hidrologicos_diarios.csv', index = True)

    if tipo == 'indices':
        dfs = np.zeros(len(teleconexoes.keys()), dtype = object)
        for i, indice in enumerate(teleconexoes.keys()):
            df = IndiceParaDataFrame(indice)
            if df is not None:
                dfs[i] = df

        if not merge: return dfs
        else:
            merged_df = dfs[0]
            for df in dfs[1:]:
                merged_df = pd.merge(merged_df, df, how = 'outer', on = 'Data')

            for indice, invalid_value in invalid_val.items():
                if indice in merged_df.columns:
                    merged_df[indice] = merged_df[indice].replace(invalid_value, np.nan)

            if export:
                merged_df['Data'] = merged_df['Data'].dt.strftime('%Y-%m')
                merged_df.set_index('Data', inplace = True)
                merged_df.to_csv('Exportado/teleconexoes.csv')
                merged_df.to_excel('Exportado/teleconexoes.xlsx')

            return merged_df

    elif tipo == 'carga':
        dfs_car = [pd.DataFrame() for _ in range(len(anos))]
        for i, ano in enumerate(anos):
            df = pd.read_csv('Exportado/ONS/' + f'CURVA_CARGA_{ano}.csv', 
                            sep = ';', 
                            decimal = '.', 
                            usecols = ['din_instante', 'id_subsistema', 'val_cargaenergiahomwmed'])
            
            df = df.rename(columns = {'din_instante': 'Data', 
                                      'id_subsistema': 'Subsistema',
                                      'val_cargaenergiahomwmed': 'Carga'})
            
            df['Data'] = pd.to_datetime(df['Data'], format = '%Y-%m-%d %H:%M:%S')
            df['Carga'] = pd.to_numeric(df['Carga'], errors = 'raise')
            dfs_car[i] = df
        
        merged_df = pd.concat(dfs_car, ignore_index = True).set_index('Data')
        merged_df = merged_df.pivot_table(
                index = 'Data',
                columns = 'Subsistema',
                values = 'Carga',
                aggfunc = 'sum'
            )

        merged_df.columns = [f'CARGA_{col}' for col in merged_df.columns]
        merged_df_diario = merged_df.resample('D').sum()
        merged_df_mensal = merged_df.resample('ME').sum()

        merged_df_diario.to_csv('Exportado/carga_subsistemas_diario.csv', index = True, encoding = 'utf-8')
        merged_df_mensal.to_csv('Exportado/carga_subsistemas_mensal.csv', index = True, encoding = 'utf-8')

        # df_men, df_med, df_ind = AnomaliaCarga(merged_df)
        # if export:
        #     df_ind['Data'] = df_ind['Data'].dt.strftime('%Y-%m')
        #     df_ind.to_csv('Exportado/carga_subsistemas_anomalias.csv', index = False)
        #     df_men.to_csv('Exportado/carga_subsistemas_bruto.csv', index = True)

        # return merged_df, df_men, df_med, df_ind

    elif tipo == 'geracao':
        dfs_ger = [pd.DataFrame() for _ in range(len(anos))]
        for i, ano in enumerate(anos):
            if ano < 2022:
                df = pd.read_csv('Exportado/ONS/' + f'GERACAO_USINA-2_{ano}.csv', 
                                sep = ';', 
                                decimal = '.', 
                                usecols = ['din_instante', 'id_subsistema', 'nom_tipocombustivel', 'val_geracao'])
                df = df.rename(columns = {'din_instante': 'Data', 
                                          'id_subsistema': 'Subsistema',
                                          'nom_tipocombustivel': 'Tipo', 
                                          'val_geracao': 'Geracao'})
                df['Data'] = pd.to_datetime(df['Data'], format = '%Y-%m-%d %H:%M:%S')
                df['Geracao'] = pd.to_numeric(df['Geracao'], errors = 'raise')
                dfs_ger[i] = df

            elif ano >= 2022:
                dfs_mes = [pd.DataFrame() for _ in range(12)]
                for mes in np.arange(1, 13, 1):
                    mes_str = f'0{mes}' if mes < 10 else str(mes)
                    arq = 'Exportado/ONS/GERACAO_USINA-2_' + f'{ano}_{mes_str}.csv'
                    try:
                        df = pd.read_csv(arq, 
                                        sep = ';', 
                                        decimal = '.', 
                                        usecols = ['din_instante', 'id_subsistema', 'nom_tipocombustivel', 'val_geracao'])
                        df = df.rename(columns = {'din_instante': 'Data',
                                                  'id_subsistema': 'Subsistema',
                                                  'nom_tipocombustivel': 'Tipo', 
                                                  'val_geracao': 'Geracao'})
                        df['Data'] = pd.to_datetime(df['Data'], format = '%Y-%m-%d %H:%M:%S')
                        df['Geracao'] = pd.to_numeric(df['Geracao'], errors = 'raise')
                        dfs_mes[mes - 1] = df

                    except FileNotFoundError:
                        print(f'[!] Arquivo não encontrado! Você tem os dados de {mes}/{ano}?')
                        continue

                merged_df = pd.concat(dfs_mes, ignore_index = True)
                dfs_ger[i] = merged_df

        merged_df = pd.concat(dfs_ger, ignore_index = True)
        # merged_df.to_csv('Exportado/geracao_usinas_horario.csv', index = True)
        ProcessarDadosGeracao(merged_df)
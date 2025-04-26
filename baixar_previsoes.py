import os
import netCDF4
import zipfile
import tempfile
import shutil
import numpy as np
import pandas as pd
import cdsapi
from sklearn.preprocessing import StandardScaler
from concurrent.futures import ThreadPoolExecutor
from alive_progress import alive_bar


# https://cds.climate.copernicus.eu/datasets/projections-cmip6?tab=download
# Regiões para download dos dados (IMPORTANTE: sistema de coord. WGS 1984)
regioes = {                                                                                                             # [North, West, South, East]
    # 'NIN 1.2': [0, -90, -10, -80],
    # 'NIN 3':   [5, -150, -5, -90],
    # 'NIN 3.4': [5, -170, -5, -120],
    # 'NIN 4_1': [5, 160, -5, 180],                                                                                     # Primeira parte da região 4
    # 'NIN 4_2': [5, -180, -5, -150],                                                                                   # Segunda parte da região 4
    'NE': [-2, -45, -18, -34],
    'N': [5, -74, -14, -45],
    'C.O.': [-14, -60, -24, -45],
    'SE': [-18, -50, -25, -39],
    'S': [-24, -56, -33, -48]
}

def DadosCMIP(regioes, anos, dataset, request):
    df_regional_final = pd.DataFrame()                                                                                  # DataFrame para armazenar os dados
    for regiao in regioes.fromkeys(regioes):

        if dataset == 'projections-cmip6':
            dataset = dataset
            request = request
            request['area'] = regioes[regiao]
            request['year'] = [f'{ano}' for ano in anos]

            base_dir = f"Exportado/ECMWF/Dados/{regiao}/{dataset}"
            arq_nome = f"{regiao}_{request['variable']}_{request['experiment']}_{request['model']}.zip"

            if not os.path.exists(f'{base_dir}/{arq_nome}'):
                client = cdsapi.Client()
                os.makedirs(base_dir, exist_ok = True)
                client.retrieve(dataset, request).download(target = f"{base_dir}/{arq_nome}")
                print(f"Arquivo baixado: {arq_nome}")

        elif dataset == 'derived-era5-single-levels-daily-statistics':
            base_dir = f"Exportado/ECMWF/Dados/{regiao}/{dataset}/{request['product_type']}"
            def download_data(ano):
                try:
                    dataset_copy = dataset
                    request_copy = request.copy()
                    request_copy['area'] = regioes[regiao]
                    request_copy['year'] = f'{ano}'

                    arq_nome = f"{regiao}_{request_copy['variable']}_{request_copy['product_type']}_{request_copy['year']}.nc"
                    target_file = os.path.join(base_dir, arq_nome)

                    if not os.path.exists(target_file):
                        os.makedirs(base_dir, exist_ok = True)

                        with tempfile.NamedTemporaryFile(suffix = '.nc', delete = False) as tmp:
                            temp_path = tmp.name

                        client = cdsapi.Client()
                        client.retrieve(dataset_copy, request_copy).download(temp_path)
                        shutil.move(temp_path, target_file)
                        print(f'\n[✓] Arquivo baixado: {arq_nome}')
                        bar()

                    else: 
                        print(f'\n[i] Arquivo já existe: {arq_nome}')
                        bar()

                except Exception as e:
                    print(f'\n[!] Falha ao baixar dados para o ano {ano}: {e}')

            with alive_bar(
                len(anos),                                                                                              # Tamanho
                title = f'Baixando dados da região {regiao}...',                                                        # Título
                bar = None,                                                                                             # Barra de progresso
                spinner = 'classic',                                                                                    # Spinner
                enrich_print = False,                                                                                   # Desativando 'on <iter>:' antes dos prints
                stats = '(ETA: {eta})',
                monitor = '{count}/{total}',
                elapsed = '    ⏱ {elapsed}'                                                                             # Tempo decorrido
            ) as bar:

                with ThreadPoolExecutor(max_workers = 20) as executor:
                    executor.map(download_data, anos)

            with alive_bar(
                len(anos),
                title = f'Processando arquivos da região {regiao}...',
                bar = None,
                spinner = 'classic',
                enrich_print = False,
                stats = '(ETA: {eta})',
                monitor = '{count}/{total}',
                elapsed = '    ⏱ {elapsed}'
            ) as bar:

                dfs_anuais_regiao = []
                arqs_nc = [f for f in os.listdir(base_dir) if f.endswith('.nc')]

                for arq in arqs_nc:
                    try:
                        nc = netCDF4.Dataset(os.path.join(base_dir, arq))
                        # var_keys = nc.variables.keys()
                        # print(f'[i] Variáveis: {var_keys}')

                        time = nc.variables['valid_time']
                        data_inicial = netCDF4.num2date(
                            time[0],
                            time.units,
                            calendar = time.calendar
                        )

                        data = pd.date_range(
                            start = data_inicial.strftime('%Y-%m-%d'),
                            periods = len(time),
                            freq = 'D').to_period('D'
                        )

                        if request['variable'] == 'sea_surface_temperature': var_data = nc.variables['sst'][:].squeeze()                                                 # Variável de temperatura da superfície do mar (sst)
                        if request['variable'] == '2m_temperature': var_data = nc.variables['t2m'][:].squeeze()                                                        # Variável de temperatura a 2m (t2m)
                        
                        lats = nc.variables['latitude'][:].squeeze()
                        lons = nc.variables['longitude'][:].squeeze()

                        var_2d = var_data.reshape(var_data.shape[0], -1)                                            # Convertendo de (data, lat, lon) pra (data, lat*lon)
                        lat_grid, lon_grid = np.meshgrid(lats, lons)                                                # Grade de latitudes e longitudes (lat x lon)
                        lat_flat, lon_flat = lat_grid.ravel(), lon_grid.ravel()                                     # Transforma a grade em vetores

                        cols = [f'lon_{ln:.2f}_lat_{lt:.2f}'
                            for lt, ln in zip(lat_flat, lon_flat)]

                        df_ano = pd.DataFrame(data = var_2d, index = data, columns = cols)                          # DataFrame para o ano atual
                        dfs_anuais_regiao.append(df_ano)

                        nc.close()

                    except Exception as e:
                        print(f'\n[!] Error ao processar o arquivo {arq}: {e}')

                    bar()

            regiao_completa = pd.concat(dfs_anuais_regiao, axis = 0).sort_index()                                       # Juntando os DataFrames de cada ano em um único DataFrame
            # print(regiao_completa)
            regiao_mediana = regiao_completa.median(axis = 1)                                                           # Calculando a mediana para cada dia do ano ano ao longo das coordenadas
            df_regional_final[f'{regiao}_{request["variable"]}'] = regiao_mediana                                       # Adicionando a série resultante como uma coluna no DataFrame final

    df_regional_final.index = df_regional_final.index.rename('Data')
    df_regional_final.to_csv(f"Exportado/ECMWF/{dataset}_{request['variable']}_{request['product_type']}.csv")          # Exportando o DataFrame final para um arquivo CSV


        # if dataset == 'projections-cmip6':
        #     arqs_zip = [f for f in os.listdir(f'{base_dir}/') if f.endswith('.zip')]
        #     print(f'Arquivos .zip encontrados: {arqs_zip}')
        #     for arq in arqs_zip:
        #         if arq.endswith('.zip'):
        #             with zipfile.ZipFile(f'{base_dir}/{arq}', 'r') as zip_ref:
        #                 nc_zip = [file for file in zip_ref.namelist() if file.endswith('.nc')][0]
        #                 zip_ref.extract(nc_zip, path = base_dir)
        #                 zip_ref.close()

        #             os.remove(f'{base_dir}/{arq}')

        #             os.rename(f'{base_dir}/{nc_zip}',
        #                     f'{base_dir}/{arq_nome.replace('.zip', '.nc')}')

        #     nc = netCDF4.Dataset(f'{base_dir}/{arq_nome.replace('.zip', '.nc')}')

        # var = nc.variables.keys()
        # print(f'Variáveis: {var}')

        # if dataset == 'projections-cmip6': time = nc.variables['time']

        # data_inicial = netCDF4.num2date(time[0],
        #                             time.units,
        #                             calendar = time.calendar)

        # data = pd.date_range(start = data_inicial.strftime('%Y-%m-%d'),
        #                     periods = len(time),
        #                     freq = 'D').to_period('D')
    
        # if request['variable'] == 'sea_surface_temperature':                                                            # Variáveis: ['sst', 'number', 'latitude', 'longitude', 'valid_time']
        #     lats = nc.variables['latitude'][:].squeeze()
        #     lons = nc.variables['longitude'][:].squeeze()
        #     var = nc.variables['sst'][:].squeeze()                                                                      # Variável de temperatura da superfície do mar (sst) para o modelo MIROC6

        #     # print(f'\nÍndice: {regiao}')
        #     # print(f'Variáveis: {var}')
        #     # print(f'tos: {tos.shape}')
        #     # print(f'Latitudes: ({lats[0][0]}, {lats[-1][-1]}) {lats.shape}')
        #     # print(f'Longitudes: ({lons[0][0]}, {lons[-1][-1]}) {lons.shape}')

        #     # Convertendo de (data, lat, lon) pra (data, lat*lon)
        #     var_2d = var.reshape(var.shape[0], -1)

        #     # Criando nomes das colunas
        #     lat_grid, lon_grid = np.meshgrid(lats, lons)                                                                # Grade de latitudes e longitudes (lat x lon)
        #     lat_flat, lon_flat = lat_grid.ravel(), lon_grid.ravel()                                                     # Transforma a grade em vetores

        #     cols = [f'lon_{ln:.2f}_lat_{lt:.2f}'
        #         for lt, ln in zip(lat_flat, lon_flat)]
            
        #     # Criando o DataFrame com os dados
        #     df = pd.DataFrame(data = var_2d, index = data, columns = cols)
        #     dados_df[f'{request['variable']}-{regiao}'] = df.median(axis = 1)
        #     dados_df.index = dados_df.index.rename('Data')
            
        # elif request['variable'] == 'precipitation' or 'surface_temperature':                                           # Variáveis: ['time', 'time_bnds', 'lat', 'lat_bnds', 'lon', 'lon_bnds', 'pr']
        #     if request['variable'] == 'precipitation': var = nc.variables['pr'][:].squeeze()
        #     if request['variable'] == 'surface_temperature': var = nc.variables['ts'][:].squeeze()                       # Variável de temperatura da superfície do mar (ts) para o modelo MIROC6

        #     lats = nc.variables['lat'][:].squeeze()
        #     lons = nc.variables['lon'][:].squeeze()
        #     var_2d = var.reshape(var.shape[0], -1)

        #     # Criando nomes das colunas
        #     lat_grid, lon_grid = np.meshgrid(lats, lons)                                                                # Grade de latitudes e longitudes (lat x lon)
        #     lat_flat, lon_flat = lat_grid.ravel(), lon_grid.ravel()                                                     # Transforma a grade em vetores

        #     cols = [f'lon_{ln:.2f}_lat_{lt:.2f}'
        #         for lt, ln in zip(lat_flat, lon_flat)]
            
        #     # Criando o DataFrame com os dados
        #     df = pd.DataFrame(data = var_2d, index = data, columns = cols)
        #     dados_df[f'{request['variable']}-{regiao}'] = df.median(axis = 1)
        #     dados_df.index = dados_df.index.rename('Data')
        #     dados_df.index = pd.to_datetime(dados_df.index, format = '%Y-%m-%d').to_period('D')                         # Convertendo o índice para o formato de data mensal

    # dados_df.to_csv(f'Exportado/ECMWF/{nome_compilado}.csv')




# DadosCMIP(regioes, anos = np.arange(2000, 2026, 1), dataset = 'derived-era5-single-levels-daily-statistics',
#           request = {
#             'product_type': 'reanalysis',
#             'daily_statistic': 'daily_mean',
#             'time_zone': 'utc+00:00',
#             'frequency': '1_hourly',
#             'variable': '2m_temperature',
#             'month' : [f'{mes}' for mes in np.arange(1, 13)],
#             'day' : [f'{dia}' for dia in np.arange(1, 32)],
#         }
#     )

# DadosCMIP(regioes, anos = np.arange(2000, 2026, 1), dataset = 'derived-era5-single-levels-daily-statistics',
#           request = {
#             'product_type': 'reanalysis',
#             'daily_statistic': 'daily_mean',
#             'time_zone': 'utc+00:00',
#             'frequency': '1_hourly',
#             'variable': '10m_u_component_of_wind',
#             'month' : [f'{mes}' for mes in np.arange(1, 13)],
#             'day' : [f'{dia}' for dia in np.arange(1, 32)],
#         }
#     )

# DadosCMIP(regioes, anos = np.arange(2000, 2026, 1), dataset = 'derived-era5-single-levels-daily-statistics',
#           request = {
#             'product_type': 'reanalysis',
#             'daily_statistic': 'daily_mean',
#             'time_zone': 'utc+00:00',
#             'frequency': '1_hourly',
#             'variable': '10m_v_component_of_wind',
#             'month' : [f'{mes}' for mes in np.arange(1, 13)],
#             'day' : [f'{dia}' for dia in np.arange(1, 32)],
#         }
#     )

# DadosCMIP(regioes, anos = np.arange(2000, 2026, 1), dataset = 'derived-era5-single-levels-daily-statistics',
#           request = {
#             'product_type': 'reanalysis',
#             'daily_statistic': 'daily_mean',
#             'time_zone': 'utc+00:00',
#             'frequency': '1_hourly',
#             'variable': 'surface_solar_radiation_downwards',
#             'month' : [f'{mes}' for mes in np.arange(1, 13)],
#             'day' : [f'{dia}' for dia in np.arange(1, 32)],
#         }
#     )

# DadosCMIP(regioes, anos = np.arange(2000, 2026, 1), dataset = 'derived-era5-single-levels-daily-statistics',
#           request = {
#             'product_type': 'reanalysis',
#             'daily_statistic': 'daily_mean',
#             'time_zone': 'utc+00:00',
#             'frequency': '1_hourly',
#             'variable': 'total_precipitation',
#             'month' : [f'{mes}' for mes in np.arange(1, 13)],
#             'day' : [f'{dia}' for dia in np.arange(1, 32)],
#         }
#     )

# DadosCMIP(regioes, anos = np.arange(2000, 2026, 1), dataset = 'derived-era5-single-levels-daily-statistics',
#           request = {
#             'product_type': 'reanalysis',
#             'daily_statistic': 'daily_mean',
#             'time_zone': 'utc+00:00',
#             'frequency': '1_hourly',
#             'variable': 'evaporation',
#             'month' : [f'{mes}' for mes in np.arange(1, 13)],
#             'day' : [f'{dia}' for dia in np.arange(1, 32)],
#         }
#     )
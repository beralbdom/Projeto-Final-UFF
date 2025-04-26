import baixar_dados as bd
import tratamento_dados as td
import baixar_previsoes as bp
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor


# -----------------------------------------> Download e exportação de dados <----------------------------------------- #

# https://dados.ons.org.br/dataset/
base_url_ons_ger = 'https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/geracao_usina_2_ho/'                         # Base URL para os dados de geração
base_url_ons_car = 'https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/curva-carga-ho/'                             # Base URL para os dados de carga
base_url_ons_vaz = 'https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/dados_hidrologicos_di/'                      # Base URL para os dados de vazões

anos = np.arange(2000, 2025, 1)                                                                                         # Anos dos dados a serem baixados

# bd.GetIndices()                                                                                                         # Baixa os dados de teleconexões                (/Exportado/Indices/)
# bd.GetGeracao(anos = anos, base_url = base_url_ons_ger)                                                                   # Baixa os dados de geração                     (/Exportado/ONS/)
# bd.GetCarga(anos = anos, base_url = base_url_ons_car)                                                                     # Baixa os dados de carga                       (/Exportado/ONS/)
# bd.GetVazao(anos = anos, base_url = base_url_ons_vaz)                                                                   # Baixa os dados de vazões                      (/Exportado/ONS/)


# bd.ExportarDados('indices', anos = anos, merge = True, export = True)                                                   # Cria os dataframes de teleconexões            (/Exportado/teleconexoes.csv)
bd.ExportarDados('geracao', anos = anos, merge = True, export = True)                                                   # Cria os dataframes de geração                 (/Exportado/geracao_usinas_<tipo>.csv)
bd.ExportarDados('carga', anos = anos, merge = True, export = True)                                                     # Cria os dataframes de carga                   (/Exportado/carga_subsistemas_<tipo>.csv)
# bd.ExportarDados('vazoes', anos = anos, merge = True, export = True)                                                    # Cria os dataframes de vazões                  (/Exportado/vazoes_mensais_bacias.csv)


# --------------------------------------> Tratamento de dados e análise inicial <------------------------------------- #
indices = pd.read_csv('Exportado/teleconexoes.csv').set_index('Data')                                                   # Dados de teleconexões (índices climatológicos)
geracao = pd.read_csv('Exportado/geracao_fontes_diario.csv').set_index('Data')                                          # Dados de geração em MWMed
carga = pd.read_csv('Exportado/carga_subsistemas_diario.csv').set_index('Data')                                        # Dados de carga em MWMed
vazoes = pd.read_csv('Exportado/dados_hidrologicos_diarios.csv').set_index('Data')                                           # Dados de vazões em m3/s
dados_cmip = pd.read_csv('Exportado/dados_cmip6_diario.csv').set_index('Data')                                          # Dados do CMIP6 em mm/mês e K
dados_era5 = pd.read_csv('Exportado/dados_era5_diario.csv').set_index('Data')                                            # Dados do ERA5 em K

indices.index = pd.to_datetime(indices.index).to_period('M')
geracao.index = pd.to_datetime(geracao.index).to_period('D')
carga.index = pd.to_datetime(carga.index).to_period('D')
vazoes.index = pd.to_datetime(vazoes.index).to_period('D')
dados_cmip.index = pd.to_datetime(dados_cmip.index, format = '%d/%m/%Y').to_period('D')
dados_era5.index = pd.to_datetime(dados_era5.index, format = '%Y-%m-%d').to_period('D')

# geracao = geracao.resample('M').sum()
# carga = carga.resample('M').sum()
# vazoes = vazoes.resample('M').mean()
# dados_cmip = dados_cmip.resample('M').mean()
# dados_era5 = dados_era5.resample('M').mean()

dados_era5['NIN 4'] = dados_era5[['NIN 4_1', 'NIN 4_2']].mean(axis = 1)                                                 # Média dos dados de NIN 4_1 e NIN 4_2
dados_era5 = dados_era5.drop(columns = ['NIN 4_1', 'NIN 4_2'])

variaveis = pd.concat([indices, dados_era5, dados_cmip, vazoes, carga], axis = 1)
variaveis = variaveis[variaveis.index.year <= 2022]                                                             # Variáveis de entrada para o modelo de regressão
geracao = geracao[geracao.index.year <= 2022]

print(f'variaveis:\n {variaveis}')

variaveis_norm = StandardScaler().fit_transform(variaveis.values)
variaveis_norm = pd.DataFrame(variaveis_norm, columns = variaveis.columns, index = variaveis.index)
# print(f'variaveis_norm:\n {variaveis_norm}')


# ---------------------------------------> Regressão e estmatva de geração <------------------------------------------ #
# modelo = MLPRegressor(
#     # hidden_layer_sizes = (10, 20, 10, 4),
#     hidden_layer_sizes = (128, 64, 32), 
#     activation = 'relu',
#     solver = 'lbfgs',
#     max_iter = 5000,
#     random_state = 69,
#     early_stopping = True, 
#     alpha = 0.0001 
# )

# modelo = RandomForestRegressor(
#     n_estimators = 666,
#     random_state = 69,
#     max_features = 'sqrt'
# )

# modelo = GradientBoostingRegressor(
#     learning_rate = 0.1,
#     max_depth = 5,
#     max_leaf_nodes = 10,
#     min_samples_leaf = 10,
#     # l2_regularization = 0.1,
#     random_state = 69,
# )

# geracao_estimada = td.Regressao(
#     geracao[['Hidráulica', 'Térmica']], 
#     variaveis_norm,
#     reg = 'nlinear',
#     modelo = modelo,
#     ano_corte = 2021,
#     tssplit = False,
#     graf = True,
#     debug = True, n_comp = -1,
#     fe = True,
#     nome_saida = '_TESTE_MENSAL!!!!'
# )      


# geracao_estimada = td.Regressao(
#     geracao, 
#     variaveis,
#     reg = 'nlinear',
#     modelo = modelo,
#     ano_corte = 2020,
#     tssplit = False,
#     graf = True,
#     debug = True, n_comp = -1,
#     fe = True,
#     nome_saida = '_GBR_COM_VAZOES_DIARIO'
# )    



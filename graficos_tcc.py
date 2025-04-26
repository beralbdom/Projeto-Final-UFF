import baixar_dados
import tratamento_dados
import pandas as pd
import geopandas as gpd
from matplotlib import rc, pyplot as plt, dates as mdates, patches as mpatches
from matplotlib.colors import ListedColormap

# Configurações de plotagem
rc('font', family = 'serif', size = 8)                                                                                  # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.rc.html
rc('grid', linestyle = '--', alpha = 0.5)
rc('axes', axisbelow = True, grid = True)
rc('lines', linewidth = 1.33, markersize = 1.5)
rc('axes.spines', top = False, right = False, left = True, bottom = True)

# Gráficos geográficos ----------------------------------------------------------------------------------------------- #
# brasil = gpd.read_parquet('Dados/brasil_subsistemas.parquet')
# cmap = ListedColormap(['#3E944F', '#ff6038', '#3665ff', '#ffc738'])
# fig, ax = plt.subplots(figsize = (6, 6))
# brasil.plot(ax = ax, column = 'subsistema', cmap = cmap, edgecolor = '#151515', lw = 0.2, label = 'Subsistemas', missing_kwds = {
#                                                                                                                     "color": "lightgrey",
#                                                                                                                     "edgecolor": "#000000",
#                                                                                                                     "label": "Isolado"},
#                                                                                                                     legend = True)


# subsystem_colors = {
#     'Norte': '#3E944F',
#     'Nordeste': '#ff6038',
#     'Sul': '#3665ff',
#     'Sudeste/Centro-Oeste': '#ffc738'
# }

# handles = []
# labels = []
# for subsys, color in subsystem_colors.items():
#     handles.append(mpatches.Patch(facecolor = color, edgecolor='none'))
#     labels.append(subsys)

# ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=5, frameon=False, fancybox=False)

# for x, y, label in zip(brasil.geometry.representative_point().x, brasil.geometry.representative_point().y, brasil['uf']):
#     ax.annotate(label, xy=(x, y), xytext=(-3, 0), textcoords='offset points', fontsize=7)

# # ax.set_title('Subsistemas do SIN')
# ax.set_xlabel('Latitude [graus]')
# ax.set_ylabel('Longitude [graus]')
# plt.savefig('Graficos/subsistemas_brasil.svg', transparent = True)



# geracao_df = pd.read_csv(f'Exportado/geracao_usinas_horario.csv')
# geracao = geracao_df.pivot_table(index = 'Data', columns = 'Tipo', values = 'Geracao', aggfunc='sum')

# geracao_hidraulica = geracao['Hidráulica']
# geracao_hidraulica.to_csv('Exportado/geracao_hidraulica_bruta_horaria.csv')
# geracao_eolica = geracao['Eólica']
# geracao_eolica.to_csv('Exportado/geracao_eolica_bruta_horaria.csv')
# geracao_solar = geracao['Fotovoltaica']
# geracao_solar.to_csv('Exportado/geracao_solar_bruta_horaria.csv')
# geracao_termica = geracao.drop(columns = ['Hidráulica', 'Eólica', 'Fotovoltaica', 'Biomassa'])
# geracao_termica.to_csv('Exportado/geracao_termica_bruta_horaria.csv')

# carga = pd.read_csv('Exportado/carga_subsistemas_horario.csv')
# carga = carga.pivot_table(index = 'Data', columns = 'Subsistema', values = 'Carga')
# carga.index = pd.to_datetime(carga.index, format = '%Y-%m-%d %H:%M:%S')
# carga['Total'] = carga.sum(axis = 1)
# carga.to_csv('Exportado/carga_subsistemas_bruto_horario.csv')


# Gráfico do dia de maior demanda e as gerações ---------------------------------------------------------------------- #
# ger_hidr = pd.read_csv('Exportado/geracao_hidraulica_bruta_horaria.csv').set_index('Data')
# ger_eol = pd.read_csv('Exportado/geracao_eolica_bruta_horaria.csv').set_index('Data')
# ger_sol = pd.read_csv('Exportado/geracao_solar_bruta_horaria.csv').set_index('Data')
# ger_ter = pd.read_csv('Exportado/geracao_termica_bruta_horaria.csv').set_index('Data')



# indices_df = pd.read_csv('Exportado/teleconexoes_NOVO.csv').set_index('Data')

# ger_hidr.index = pd.to_datetime(ger_hidr.index, format = '%Y-%m-%d %H:%M:%S')
# ger_eol.index = pd.to_datetime(ger_eol.index, format = '%Y-%m-%d %H:%M:%S')
# ger_sol.index = pd.to_datetime(ger_sol.index, format = '%Y-%m-%d %H:%M:%S')
# ger_ter.index = pd.to_datetime(ger_ter.index, format = '%Y-%m-%d %H:%M:%S')

# ger_ter['Total'] = ger_ter.sum(axis = 1)
# ger_ter = ger_ter['Total']
# print(ger_ter)

# carga = pd.read_csv('Exportado/carga_subsistemas_bruto_horario.csv').set_index('Data')
# carga.index = pd.to_datetime(carga.index, format = '%Y-%m-%d %H:%M:%S')
# carga = carga.drop(columns = ['N', 'NE', 'S', 'SE'])
# max_carga_date = carga['Total'].idxmax().date()                                                                         # Encontrando o dia com maior carga

# # Filtrando os dados para o dia com maior carga
# carga_max_day = carga.loc[carga.index.date == max_carga_date]
# ger_eol_max_day = ger_eol.loc[ger_eol.index.date == max_carga_date]
# ger_sol_max_day = ger_sol.loc[ger_sol.index.date == max_carga_date]
# ger_hidr_max_day = ger_hidr.loc[ger_hidr.index.date == max_carga_date]
# ger_ter_max_day = ger_ter.loc[ger_ter.index.date == max_carga_date]

# # Plotando gráfico de linha com a carga e a geração de energia para o dia com maior carga
# fig, ax = plt.subplots(figsize = (6, 3), sharex = False)
# ax.plot(carga_max_day.index, carga_max_day['Total'], linestyle = '--', color = '#FF4A4D', label = 'Carga')
# # ax2 = ax.twinx()
# ax.plot(ger_eol_max_day.index, ger_eol_max_day['Eólica'], linestyle='-', color='#3E944F', label='Eólica')
# ax.plot(ger_sol_max_day.index, ger_sol_max_day['Fotovoltaica'], linestyle='-', color='#E3B132', label='Fotovoltaica')
# ax.plot(ger_hidr_max_day.index, ger_hidr_max_day['Hidráulica'], linestyle='-', color='#3867ff', label='Hidráulica')
# ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=4, frameon=False, fancybox=False)
# ax.set_xlabel('Horário')
# ax.set_ylabel('Energia [MWmed]')
# ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%Hh'))
# # plt.xticks(rotation=45, ha = 'right')
# plt.ticklabel_format(axis='y', style='sci', scilimits=(4, 4))

# ax.grid(True)
# plt.tight_layout()
# plt.savefig(f'Graficos/carga_max_dia_{max_carga_date}.svg', transparent=True)
# plt.show()


# Gráfico de linha com a geração de energia hidráulica bruta --------------------------------------------------------- #
geracao = pd.read_csv('Exportado/geracao_fontes_mensal.csv').set_index('Data')
geracao.index = pd.to_datetime(geracao.index, format = '%Y-%m-%d')

fig, ax = plt.subplots(figsize = (6, 3))
ax.plot(geracao.index, geracao['Hidráulica'], color = '#3867ff', label = 'Geração')
# ax.set_xlim(ger_hidr.index.min(), ger_hidr.index.max())
# ax.set_title('Geração hidráulica bruta')
ax.set_ylabel('Geração [MWh]')
ax.set_xlabel('Série histórica')
ax.xaxis.set_major_locator(mdates.YearLocator(base = 2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.tight_layout()
plt.savefig('Graficos/geracao_hidraulica_bruta.svg', transparent = True)


# Gráfico do índice ONI ---------------------------------------------------------------------------------------------- #
fig, ax = plt.subplots(figsize=(6, 3))
oni = indices_df['ONI']
oni = oni[oni.index >= '2000-01-01']
vmin = oni.min(); vmax = oni.max()
norm = plt.Normalize(vmin, vmax)
cmap = plt.get_cmap('coolwarm')
ax.plot(oni.index, oni, color='black', label='ONI', alpha = 1, linewidth = 0.66)
ax.set_ylim(-2, 3)

for i in range(len(oni) - 1):
    ax.fill_between(oni.index[i:i+20], oni[i:i+20], color=cmap(norm(oni[i])), alpha=1)

# sm = plt.cm.ScalarMappable(cmap = cmap, norm = norm)
# sm.set_array([])
# cbar = plt.colorbar(sm, ax=ax)
# ln_f = vmin; el_f = vmax
# neutro = (vmax + vmin) / 2
# lf_m = vmin / 4; ef_m = vmax / 2
# cbar.set_ticks([ln_f, lf_m, neutro, ef_m, el_f])
# cbar.set_ticklabels(['L.N intenso', 'L.N moderado', 'Neutro', 'E.N moderado', 'E.N intenso'])
ax.set_ylabel('Anomalia')
ax.set_xlabel('Série histórica')
plt.tight_layout()
plt.savefig('Graficos/oni.svg', transparent = True)


# ---
# geracao_yearly = geracao_df.resample('YE').sum()
# sorted_columns = geracao_yearly.sum().sort_values(ascending = False).index
# geracao_yearly_sorted = geracao_yearly[sorted_columns]

# carga_df = carga_df.resample('YE').sum()
# # carga_df.index = carga_df.index.year
# geracao_percentage_sorted = geracao_yearly_sorted.div(geracao_yearly_sorted.sum(axis = 1), axis = 0) * 100
# geracao_percentage_sorted.index = geracao_percentage_sorted.index.year

# from matplotlib.colors import ListedColormap
# cmap = ListedColormap(['#3867ff', '#ff6038', '#3E944F'])
# ax = geracao_percentage_sorted.plot(kind='bar', stacked=True, figsize=(6, 3), colormap=cmap)
# ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.135), ncol=5, frameon=False, fancybox=False)
# ax.set_xticklabels(geracao_percentage_sorted.index, rotation=45, ha='right')
# ax.set_ylabel('Geração [%]')
# ax.set_xlabel('Série histórica')
# plt.tight_layout()
# plt.savefig('Graficos/geracao_anual_hidrica_termica.svg', transparent=True)

# fig, ax = plt.subplots(figsize=(6, 3), sharey=False)
# ax.plot(carga_df.index, carga_df['Total'], color='#FF4A4D', label='Carga')
# ax.set_ylabel('Carga [MWmed]')
# ax.set_xlabel('Série histórica')
# # years = carga_df.index
# # ax.set_xticks(years)
# # ax.set_xticklabels(years, rotation=45, ha='right')
# # ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.135), ncol=5, frameon=False, fancybox=False)
# plt.tight_layout()
# plt.savefig('Graficos/carga_anual.svg', transparent=True)






# # geracao_df = pd.read_csv(f'Exportado/geracao_usinas_bruto.csv').set_index('Data')
# carga_df = pd.read_csv(f'Exportado/carga_subsistemas_bruto.csv').set_index('Data')
# # geracao_df.index = pd.to_datetime(geracao_df.index, format = '%Y-%m')
# carga_df.index = pd.to_datetime(carga_df.index, format = '%Y-%m')
# carga_df['Total'] = carga_df.sum(axis = 1)
# carga_df = carga_df.drop(columns = ['N', 'NE', 'S', 'SE'])


# geracao_df = geracao_df.div(geracao_df.std())
# # carga_df = carga_df.div(carga_df.std())
# indices_df = indices_df.div(indices_df.std())
# # regressao(geracao_df, indices_df, export = True)
# geracao_df['Hidráulica N-NE'] = geracao_df[['Hidráulica-N', 'Hidráulica-NE']].sum(axis = 1, skipna = True)
# geracao_df['Hidráulica S-SE'] = geracao_df[['Hidráulica-S', 'Hidráulica-SE']].sum(axis = 1, skipna = True)
# geracao_df = geracao_df.drop(columns = ['Hidráulica-N', 'Hidráulica-NE', 'Hidráulica-S', 'Hidráulica-SE'])
# geracao_df['Térmica'] = geracao_df[['Carvão',
#                                     'Gás',
#                                     'Óleo Diesel',
#                                     'Óleo Combustível',
#                                     'Multi-Combustível Diesel/Óleo',
#                                     'Nuclear',
#                                     'Outras Multi-Combustível']].sum(axis=1, skipna=True)
# geracao_df = geracao_df.drop(columns = ['Carvão',
#                                         'Gás',
#                                         'Óleo Diesel',
#                                         'Óleo Combustível',
#                                         'Multi-Combustível Diesel/Óleo',
#                                         'Nuclear',
#                                         'Outras Multi-Combustível'])
# geracao_df['Outras'] = geracao_df[['Biomassa', 'Resíduos Industriais']].sum(axis = 1, skipna = True)
# geracao_df = geracao_df.drop(columns = ['Biomassa', 'Resíduos Industriais'])

# geracao_df = geracao_df.div(geracao_df.std())
# plot(geracao_df, indices_df, 'linha', 'Todos')
# plot(geracao_df, indices_df, 'scatter')
# plot(geracao_df, indices_df, 'boxplot')
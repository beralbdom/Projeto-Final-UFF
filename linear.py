import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error as mse_error
from sklearn.preprocessing import StandardScaler

import matplotlib_config

# Entrada das séries
geracao = (
    pd.read_csv(
        'Exportado/geracao_fontes_diario_MWmed.csv', 
        parse_dates = ['Data'])
    .set_index('Data')
)

carga = (
    pd.read_csv(
        'Exportado/carga_subsist_diario_MWmed.csv', 
        parse_dates = ['Data'])
    .set_index('Data')
)

enso = (
    pd.read_csv(
        'Exportado/ECMWF/derived-era5-single-levels-daily-statistics_sea_surface_temperature_reanalysis.csv', 
        parse_dates = ['Data'])
        .set_index('Data')
)

geracao = geracao.fillna(0) # sem geração eólica e fotovoltaica no início dos anos 2000
geracao = geracao.drop(columns = [cols for cols in geracao.columns if 'Fotovoltaica' in cols or 'Outras' in cols]) 

# Feature engineering
carga['ano'] = carga.index.year
carga['mes'] = carga.index.month
carga['dia_mes'] = carga.index.day
carga['dia_semana'] = carga.index.dayofweek
carga['dia_ano'] = carga.index.dayofyear
carga['quadrimestre'] = carga.index.quarter

dataset = pd.concat([geracao, carga, enso], axis = 1).dropna()
dataset = dataset[dataset.index.year > 2009]
dataset = dataset[dataset.index.year < 2025]

target_cols = geracao.columns.to_list()
exog_cols = carga.columns.append(enso.columns).to_list()
print(f'Colunas objetivo:\n {target_cols}')
print(f'\nColunas exógenas:\n {exog_cols}')
print(dataset.head())

# Normalização e separação das séries de treino/teste
scaler = StandardScaler()
dataset[exog_cols] = scaler.fit_transform(dataset[exog_cols])

X_train, X_test, y_train, y_test = train_test_split(
    dataset[exog_cols], dataset[target_cols], 
    test_size = .3, shuffle = False
)

# Aplicação do modelo
modelo = LinearRegression(n_jobs = -1)
reg = modelo.fit(X_train, y_train)
print(f'Coeficientes do modelo: {reg.coef_}')
print(f'Intercepto do modelo: {reg.intercept_}')
y_pred = reg.predict(X_test)
y_pred = pd.DataFrame(y_pred, columns = target_cols, index = y_test.index) 
y_pred[y_pred < 0] = 0

# Resample mensal para visualização
y_pred = y_pred.resample('ME').mean()
y_test = y_test.resample('ME').mean()
y_train = y_train.resample('ME').mean()

layout = [['a', 'b']]
for col in target_cols:
    r2 = r2_score(y_test[col], y_pred[col])
    mse = mse_error(y_test[col], y_pred[col])

    fig, ax = plt.subplot_mosaic(layout, figsize = (7, 2.5), width_ratios = [1, 2])

    ax['a'].scatter(y_test[col], y_pred[col], s = 2, color = "#E24C4C", alpha = .5, label = 'Previsto')
    ax['a'].plot([y_test[col].min(), y_test[col].max()], [y_test[col].min(), y_test[col].max()], 
               color = "#202020", linewidth = .66, ls = '--', label = 'Ideal')
    
    ax['a'].set_xticks(np.linspace(y_test[col].min(), y_test[col].max(), num = 5))
    ax['a'].set_yticks(np.linspace(y_test[col].min(), y_test[col].max(), num = 5))
    ax['a'].legend(loc = 'upper center', bbox_to_anchor = (.5, 1.15), ncol = 2, frameon = False, fancybox = False)
    ax['a'].ticklabel_format(axis = 'both', style = 'sci', scilimits = (3, 3))
    ax['a'].set_xlabel('Real')
    ax['a'].set_ylabel('Previsto')
    
    ax['b'].plot(y_train.index, y_train[col], label = 'Treino', color = "#43AAFF", linewidth = .66)
    ax['b'].plot(y_test.index, y_test[col], label = 'Real', color = "#969696", linewidth = .66, ls = '--')
    ax['b'].plot(y_pred.index, y_pred[col], label = 'Previsão', color = "#E24C4C", linewidth = .66)
    
    ax['b'].legend(loc = 'upper center', bbox_to_anchor = (.5, 1.15), ncol = 3, frameon = False, fancybox = False)
    ax['b'].set_xlabel('Série histórica')
    ax['b'].set_ylabel(f'Geração {col.replace('_', ' ')} (MWMed)')
    ax['b'].ticklabel_format(axis = 'y', style = 'sci', scilimits = (3, 3))

    ax['b'].text(.02, .95, (f'R² = {r2:.3f}\nMSE = {mse:.2E}'), 
                            transform = ax['b'].transAxes, verticalalignment = 'top', fontsize = 7,
                            bbox = dict(boxstyle = 'square', facecolor = 'white', edgecolor = 'none'))
    
    plt.tight_layout()
    # plt.show()
    plt.savefig(f'LateX/figuras/linear/linear_{col}_mensal.svg', bbox_inches = 'tight')
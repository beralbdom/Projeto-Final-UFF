# Created on Tue Oct 22 2024
# Descrição do arquivo...
# Copyright (c) Bernardo Albuquerque Domingues
# https://github.com/beralbdom \ dominguesbernardo@id.uff.br
# -------------------------------------------------------------------------------------------------------------------- #

# estudar indices de avaliar ajuste da regressao, r2 ajustado, erro medio quadratico, xisquared
# https://stackoverflow.com/questions/48849540/random-forest-regression-accuracy-different-for-training-set-and-test-set
# https://scikit-learn.org/dev/modules/generated/sklearn.neural_network.MLPRegressor.html
# https://scikit-learn.org/stable/machine_learning_map.html


import numpy as np
import pandas as pd
# import matplotlib; matplotlib.use('Agg')
from matplotlib import rc, pyplot as plt, dates as mdates
from alive_progress import alive_bar

from sklearn.base import clone
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error as mae
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy.stats import pearsonr
from sklearn.model_selection import TimeSeriesSplit
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import GradientBoostingRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.feature_selection import RFECV


# Configurações de plotagem
rc('font', family = 'serif', size = 8)                                                                                  # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.rc.html
rc('grid', linestyle = '--', alpha = .5)
rc('axes', axisbelow = True, grid = True)
rc('lines', linewidth = 1.33, markersize = 1.5)
rc('axes.spines', top = False, right = False, left = True, bottom = True)


def AnalisePCA(df_combinado, n_comp, reg):                                                                              # https://scikit-learn.org/stable/modules/decomposition.html#pca
    fonte = df_combinado.columns.to_list()[0]                                                                           # Pegando o nome da torre
    X = df_combinado.drop(columns = fonte)
    scaler = StandardScaler()                                                                                           # Aplicando Z-Scale normalization
    X_norm = scaler.fit_transform(X)

    if n_comp == 0: n_comp = min(X.columns.size, X.index.size)                                                          # Se o número de componentes não for especificado, usa o mínimo entre o número de índices e de amostras

    pca = PCA(n_components = n_comp).set_output(transform = 'pandas')
    X_pca = pca.fit_transform(X_norm)
    
    pca_comp = pca.components_
    autovetores_df = pd.DataFrame(
        pca_comp,
        columns = X.columns,
        index = [f'PC{i + 1}' for i in range(n_comp)]
    )

    var_expl = pca.explained_variance_
    explained_variance_df = pd.DataFrame(
        var_expl,
        columns = ['Explained Variance'],
        index = [f'PC{i + 1}' for i in range(n_comp)]
    )
    
    autovetores_df.to_excel(f'Exportado/AutovetoresPCA_fonte_{fonte}.xlsx')
    
    # Plotando a Variância acumulada explicada
    fig, axs = plt.subplots(2, 1, figsize = (6, 6))
    axs[0].bar(range(1, n_comp + 1), np.cumsum(pca.explained_variance_ratio_))
    axs[0].set_title('Variância explicada acumulada')
    axs[0].set_xticks(range(1, n_comp + 1))

    # Plotando o heatmap dos autovetores
    cmap = plt.cm.RdYlGn
    im = axs[1].imshow(autovetores_df, cmap = cmap, aspect = 'auto')    
    axs[1].set_yticks(range(n_comp))
    axs[1].set_yticklabels(autovetores_df.index)
    axs[1].set_xticks(range(len(autovetores_df.columns)))
    axs[1].set_xticklabels(autovetores_df.columns, rotation = 90, ha = 'center')
    axs[1].set_title('Heatmap dos autovetores')
    cbar = fig.colorbar(im, ax = axs[1], fraction = 0.046, pad = 0.04)
    cbar.set_label('Coeficiente PCA', rotation = 270, labelpad = 15)

    plt.tight_layout()
    plt.savefig(f'Graficos/{reg}/Analise/PCA_torre_{fonte}.png', transparent = False)

    print(f"\nAutovetores para a torre {fonte}:")
    print(autovetores_df)
    print(f"\nVariância explicada para a torre {fonte}:")
    print(explained_variance_df)

    return X_pca, pca_comp, var_expl


def Regressao(
        df_geracao, 
        df_indices, 
        reg,
        modelo,
        ano_corte,
        tssplit = False, 
        graf = False, 
        debug = False, 
        n_comp = -1, 
        fe = False, 
        nome_saida = ''
    ):
    
    fontes = df_geracao.columns
    dict_reg_ind = {fonte: [] for fonte in fontes}

    with alive_bar(
        fontes.size,                                                                                                    # Tamanho
        title = 'Calculando regressões...',                                                                             # Título
        bar = None,                                                                                                     # Barra de progresso
        spinner = 'classic',                                                                                            # Spinner
        enrich_print = False,                                                                                           # Desativando 'on <iter>:' antes dos prints
        stats = '({eta})',                                                                                              # Estimativa de tempo
        monitor = '{count}/{total}',                                                                                    # Monitor
        elapsed = 'em {elapsed}'                                                                                        # Tempo decorrido
    ) as bar:
        for f, fonte in enumerate(fontes):
            df_combinado = df_geracao[[fonte]].join(df_indices, how = 'inner').dropna(axis = 1)                         # Alinhando os índices com a fonte

            if n_comp == -1:                                                                                            # Se o número de componentes for diferente de zero, fazendo PCA. Caso contrário, não faz o PCA e usa os índices diretamente
                X, y = df_combinado.drop(columns = fonte), df_combinado[fonte]
            else:
                (X_pca, pca_comp, var_expl) = AnalisePCA(df_combinado, n_comp, reg)
                X_pca.index = df_combinado.index
                X, y = X_pca, df_combinado[fonte]
                
            if len(df_combinado.index) <= 12 * 3:
                if debug: bar.text(f'[!] Menos de 36 amostras para a fonte {fonte}. Continuando para a próxima...')
                fonte = fontes[f + 1]
                continue

            # try:
            if reg == 'linear':
                # Linear
                modelo = LinearRegression()
                print(f'\nProcessando {fonte}...')

                # Fazendo seleção dos melhores índices
                if fe:
                    selector = RFECV(modelo, 
                                    step = 1, 
                                    min_features_to_select = 5,
                                    cv = 10,
                                    scoring = 'r2',
                                    n_jobs = -1)
                    selector = selector.fit(X_train, y_train)
                    X_train = X_train.loc[:, selector.support_]
                    print(f'Índices selecionados: {np.array(X_train.columns)}')

                modelo.fit(X_train, y_train)
                y_pred = modelo.predict(X_test)
                erro = mae(y_test, y_pred)
                erro2 = r2_score(y_test, y_pred)
                erro3 = pearsonr(y_test, y_pred)[0]
                dict_reg_ind[fonte].append([erro2, X_test.columns.size, X_test.index.size])                          # Salvando os resultados da regressão

                if graf == True:
                    X_test = X_test.sort_index()
                    X_train = X_train.sort_index()
                    y_test = y_test.sort_index()
                    y_train = y_train.sort_index()

                    fig, ax = plt.subplots(1, 2, figsize = (6, 3))
                    ax = ax.flatten()
                    # fig.suptitle(f'Fonte {fonte} - Regressão linear multi-variável')
                    # ax.set_title(f'Nº componentes: {n_comp}, amostras: {X.index.size}\n', fontsize = 8)
                    y_min = y_test.min(); y_max = y_test.max()
                    ax[0].plot([y_min, y_max], 
                                [y_min, y_max], 
                                color = 'black', linestyle = '--', linewidth = 1)
                    ax[0].scatter(y_test, y_pred, s = 4, c = '#036ffc', alpha = .25)
                    ax[0].set_xlabel('Real')
                    ax[0].set_ylabel('Estimado')
                    ax[0].set_xticks(np.linspace(y_min, y_max, 4).round(1))
                    ax[0].set_yticks(np.linspace(y_min, y_max, 4).round(1))
                    ax[0].text(0.05, 1.00, (f'M = {erro:.4f}\nR² = {erro2:.4f}\nr = {erro3:.4f}\nÍndices: {X_train.columns.size}'), 
                            transform = ax[0].transAxes, verticalalignment = 'top', fontsize = 7,
                            bbox = dict(boxstyle = 'square', facecolor = 'white', edgecolor = 'none'))
                    
                    ax[1].plot(X_train.index.to_timestamp(), y_train, label = 'Treino', linewidth = 0.8, color = '#000000', alpha = 1)
                    ax[1].plot(X_test.index.to_timestamp(), y_test, label = 'Teste', linewidth = 0.8, color = '#000000', alpha = 0.33)
                    ax[1].plot(X_test.index.to_timestamp(), y_pred, label = 'Previsão', linewidth = 0.8, color = '#036ffc', alpha = 1)
                    ax[1].legend(loc = 'upper center', bbox_to_anchor = (0.5, 1.2), 
                                    ncol = 3, frameon = False, fancybox = False)
                    ax[1].set_xlabel('Série histórica')
                    ax[1].set_ylabel('Geração [MWh]')
                    ax[1].xaxis.set_major_locator(mdates.YearLocator(6))
                    ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
                    
                    # medias = df_indices_pca.mean()                                                                  # https://en.wikipedia.org/wiki/Principal_component_analysis
                    # print(f'\n\nMédias:\n {medias}')

                    # if n_comp != 0:
                    #     for i, (comp, var) in enumerate(zip(pca_comp[:2], var_expl[:2])):                               # https://scikit-learn.org/stable/auto_examples/cross_decomposition/plot_pcr_vs_pls.html#sphx-glr-auto-examples-cross-decomposition-plot-pcr-vs-pls-py
                    #         comp = comp * var
                    #         ax.annotate('', xy = (comp[0], comp[1]), xytext = (0, 0), 
                    #                     arrowprops = dict(arrowstyle = '->', lw = 1, color = 'black'))

                    # for pc in range(len(autovetores_df)):                                                           # https://scikit-learn.org/stable/auto_examples/cross_decomposition/plot_pcr_vs_pls.html#sphx-glr-auto-examples-cross-decomposition-plot-pcr-vs-pls-py
                    #     vetor = autovetores_df.iloc[pc].values                                                      # Pegando o valor do autovetor para o PC
                    #     tamanho = explained_variance_df.iloc[pc]['Explained Variance']                              # Normalizando o autovetor pela variância explicada
                    #     x0, y0 = medias.iloc[0], medias.iloc[1]                                                     # Pegando a média dos valores dos PCs (2D, então só 2)
                    #     x1 = x0 + tamanho * vetor[0]
                    #     y1 = y0 + tamanho * vetor[1]
                        
                    #     ax.annotate('', xy = (x1, y1), xytext = (x0, x0), 
                    #                 arrowprops = dict(arrowstyle = '->', lw = 1, color = 'black'))

            # Não-linear
            if reg == 'nlinear':
                # lags = [1, 7, 15, 30, 180]
                # for lag in lags:
                #     X[f'GERACAO_LAG_{lag}'] = y.shift(lag)

                X['ANO'] = X.index.year
                X['MES'] = X.index.month
                # X['DIA'] = X.index.day
                # X['DIA_SEMANA'] = X.index.dayofweek

                print(f'\n[i] Processando fonte {fonte}')
                print(f'[i] Número de amostras: {X.index.size}')
                print(f'[i] Número de variáveis: {X.columns.size}')

                # Feature selection
                # if fe:
                #     selector = RFECV(
                #         modelo,
                #         step = 1,
                #         min_features_to_select = 5,
                #         cv = 5,
                #         scoring = 'r2',
                #         importance_getter = 'coefs_',
                #         n_jobs = -1
                #     )
                #     selector.fit(X_train, y_train)
                #     support = selector.support_
                #     X_train = X_train.loc[:, support]
                #     X_test  = X_test.loc[:, support]
                #     print(f'[i] Variáveis selecionadas: {X_train.columns.tolist()}')
                
                if tssplit:
                    n_splits_cv = 5
                    ts_cv = TimeSeriesSplit(
                        n_splits = n_splits_cv
                        # gap = 90,
                        # test_size = 5 * 365
                    )
                    print(f'[i] Usando TimeSeriesSplit com {n_splits_cv} splits')

                    folds_r2 = []
                    folds_pearson = []
                    folds_treino_periodos = []
                    folds_teste_periodos = []
                    y_pred_folds = np.zeros(n_splits_cv, dtype = object)
                    ultimo_fold = {}

                    for fold, (train_idx, test_idx) in enumerate(ts_cv.split(X, y)):
                        X_train_fold, X_test_fold = X.iloc[train_idx], X.iloc[test_idx]
                        y_train_fold, y_test_fold = y.iloc[train_idx], y.iloc[test_idx]

                        if len(X_test_fold) == 0: continue

                        folds_treino_periodos.append((
                            X_train_fold.index.min().to_timestamp(),
                            X_train_fold.index.max().to_timestamp()
                        ))

                        folds_teste_periodos.append((
                            X_test_fold.index.min().to_timestamp(),
                            X_test_fold.index.max().to_timestamp()
                        ))

                        modelo_ = clone(modelo)
                        modelo_.fit(X_train_fold, y_train_fold)

                        y_pred_fold = modelo_.predict(X_test_fold)
                        y_pred_folds[fold] = y_pred_fold

                        y_fit_fold = modelo_.predict(X_train_fold)

                        r2_test_fold = r2_score(y_test_fold, y_pred_fold)
                        pearson_test_fold = pearsonr(y_test_fold, y_pred_fold)[0]
                        folds_r2.append(r2_test_fold)
                        folds_pearson.append(pearson_test_fold)

                        print(f'    Fold {fold+1}/{n_splits_cv} - R²: {r2_test_fold:.4f}, Pearson: {pearson_test_fold:.4f}')

                        # último fold
                        if fold == n_splits_cv - 1:
                            ultimo_fold = {
                                'X_train': X_train_fold, 'y_train': y_train_fold,
                                'X_test': X_test_fold, 'y_test': y_test_fold,
                                'y_fit': y_fit_fold, 'y_pred': y_pred_fold,
                                'r2_treino': r2_score(y_train_fold, y_fit_fold),
                                'pearson_treino': pearsonr(y_train_fold, y_fit_fold)[0],
                                'r2_teste': r2_test_fold,
                                'pearson_teste': pearson_test_fold
                            }

                            print(f'[i] X_test do último fold:\n {ultimo_fold["X_test"]}')

                    r2_teste_medio = np.mean(folds_r2) if folds_r2 else np.nan
                    pearson_teste_medio = np.mean(folds_pearson) if folds_pearson else np.nan

                    print(f'[i] R² médio: {r2_teste_medio:.4f}, Pearson médio: {pearson_teste_medio:.4f}')
                    dict_reg_ind[fonte].append([r2_teste_medio, X.columns.size, X.index.size])

                    # dados do ultimo fold pra plotar
                    if graf and ultimo_fold:
                        X_train, y_train = ultimo_fold['X_train'], ultimo_fold['y_train']
                        X_test, y_test = ultimo_fold['X_test'], ultimo_fold['y_test']
                        y_fit, y_pred = ultimo_fold['y_fit'], ultimo_fold['y_pred']
                        erro_r2_treino, pearson_treino = ultimo_fold['r2_treino'], ultimo_fold['pearson_treino']
                        erro_r2_teste, pearson_teste = ultimo_fold['r2_teste'], ultimo_fold['pearson_teste']
                    else:
                        graf = False

                else:
                    print(f'[i] Usando divisão simples no ano {ano_corte}.')

                    print(f'X: \n{X}')
                    print(f'y: \n{y}')

                    X_train = X[X.index.year < ano_corte]
                    y_train = y[X.index.year < ano_corte]
                    X_test = X[X.index.year >= ano_corte]
                    y_test = y[X.index.year >= ano_corte]

                    # Feature selection
                    if fe:
                        selector = RFECV(
                            modelo,
                            step = 1,
                            min_features_to_select = 5,
                            cv = 5,
                            scoring = 'r2',
                            importance_getter = 'auto',
                            n_jobs = -1
                        )
                        selector.fit(X_train, y_train)
                        support = selector.support_
                        X_train = X_train.loc[:, support]
                        X_test  = X_test.loc[:, support]
                        print(f'[i] Variáveis selecionadas: {X_train.columns.tolist()}')

                    print(f'X_Teste: \n{X_test}')

                    modelo.fit(X_train, y_train)
                    y_fit = modelo.predict(X_train)
                    y_pred = modelo.predict(X_test)

                    erro_r2_teste = r2_score(y_test, y_pred)
                    erro_r2_treino = r2_score(y_train, y_fit)
                    pearson_teste = pearsonr(y_test, y_pred)[0]
                    pearson_treino = pearsonr(y_train, y_fit)[0]

                    dict_reg_ind[fonte].append([erro_r2_teste, X_test.columns.size, X_test.index.size])
                    print(f'[i] R²: {erro_r2_teste:.4f}, Pearson: {pearson_teste:.4f}')
                
                if graf == True:
                    fig = plt.figure(figsize = (6, 6))
                    gs = fig.add_gridspec(2, 2)
                    ax_top_left = fig.add_subplot(gs[0, 0])
                    ax_top_right = fig.add_subplot(gs[0, 1])
                    ax_bottom = fig.add_subplot(gs[1, :])
                    y_min = y.min()
                    y_max = y.max()

                    # Scatter do teste
                    ax_top_right.plot([y_min, y_max], [y_min, y_max], 
                                        color = 'black', linestyle = '--', linewidth = 1)
                    
                    ax_top_right.scatter(y_test, y_pred, 
                                            s = 4, c = '#036FFC', alpha = .2, label = 'Teste')

                    ax_top_right.set_xlabel('Real')
                    ax_top_right.set_ylabel('Estimado')
                    ax_top_right.set_xticks(np.linspace(y_min, y_max, 4).round(1))
                    ax_top_right.set_yticks(np.linspace(y_min, y_max, 4).round(1))
                    ax_top_right.legend(loc = 'upper center', bbox_to_anchor = (0.5, 1.15), 
                                        ncol = 1, frameon = False)
                    ax_top_right.text(
                        0.02, .98, 
                        f'R² = {erro_r2_teste:.4f}\nr = {pearson_teste:.4f}\nÍndices: {X_train.columns.size}',
                        transform = ax_top_right.transAxes, verticalalignment = 'top', fontsize = 7,
                        bbox = dict(boxstyle = 'square', facecolor = 'white', edgecolor = 'none')
                    )

                    # Scatter do treino
                    ax_top_left.plot([y_min, y_max], [y_min, y_max], 
                                        color = 'black', linestyle = '--', linewidth = 1)
                    
                    ax_top_left.scatter(y_train, y_fit, s = 4, c = '#FF4A4D', alpha = .2, label = 'Treino')
                    ax_top_left.set_xlabel('Real')
                    ax_top_left.set_ylabel('Estimado')
                    ax_top_left.set_xticks(np.linspace(y_min, y_max, 4).round(1))
                    ax_top_left.set_yticks(np.linspace(y_min, y_max, 4).round(1))
                    ax_top_left.legend(loc = 'upper center', bbox_to_anchor = (0.5, 1.15), 
                                        ncol = 1, frameon = False)
                    ax_top_left.text(
                        0.05, .95, 
                        f'R² = {erro_r2_treino:.4f}\nr = {pearson_treino:.4f}\nÍndices: {X_train.columns.size}',
                        transform = ax_top_left.transAxes, verticalalignment = 'top', fontsize = 7,
                        bbox = dict(boxstyle = 'square', facecolor = 'white', edgecolor = 'none')
                    )

                    y_train_mensal = y_train.to_timestamp().resample('ME').sum()
                    y_test_mensal = y_test.to_timestamp().resample('ME').sum()
                    y_pred_serie = pd.Series(y_pred, index = X_test.index)
                    y_pred_mensal = y_pred_serie.to_timestamp().resample('ME').sum()

                    # Série temporal
                    ax_bottom.plot(y_train_mensal.index, y_train_mensal, 
                                    label = 'Treino', linewidth = 0.8, color = '#000000', alpha = 1)
                    
                    ax_bottom.plot(y_test_mensal.index, y_test_mensal, 
                                    label = 'Teste', linewidth = 0.8, color = '#000000', alpha = 0.33)
                    
                    if tssplit:
                        for i, (start_date, end_date) in enumerate(folds_treino_periodos):
                            y_pred_fold = pd.Series(y_pred_folds[i], index = pd.date_range(folds_teste_periodos[i][0], folds_teste_periodos[i][1], freq = 'D'))
                            y_pred_fold = y_pred_fold.resample('ME').sum()

                            ax_bottom.axvspan(end_date, start_date, color = 'black', alpha = .066, label = 'Treinos' if i == 0 else '')
                            ax_bottom.plot(y_pred_fold.index, y_pred_fold,
                                        label = 'Folds' if i == 0 else '', color = '#FF4A4D', linestyle = '--', alpha = 1, linewidth = 0.5)

                    ax_bottom.plot(y_pred_mensal.index, y_pred_mensal, 
                                    label = 'Estimado', linewidth = 0.8, color = '#036ffc', alpha = 1)

                    ax_bottom.legend(loc = 'upper center', bbox_to_anchor = (0.5, 1.15), ncol = 5, frameon = False)
                    ax_bottom.set_xlabel('Série histórica')
                    ax_bottom.set_ylabel('Geração mensal total [MWh]')
                    ax_bottom.xaxis.set_major_locator(mdates.YearLocator(2))                                            # Definindo o intervalo do eixo x
                    ax_bottom.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))                                     # Mostrando só o anno
            
            if graf == True:
                plt.tight_layout()
                plt.savefig(f'Graficos/Regressao/{reg}/{fonte}_{reg}{nome_saida}.png', transparent = False)
                plt.close()

            # except Exception as erro:
                # plt.close()
                # if debug: 
                #     print(f' -> Erro ao processar a fonte {fonte}: {erro}')
                #     # print(f'      X = \n{x}\n      y = \n{y}')
            bar()

    reg_ind = [                                                                                                         # Transformando o dict em uma lista
        [fonte] + indice
        for fonte, indices in dict_reg_ind.items()
        for indice in indices
    ]

    if reg == 'linear':
        reg_ind = pd.DataFrame(reg_ind, columns = ['Fonte', 'Erro (R2)', 'Índices', 'Amostras'])
        reg_ind.to_excel(f'Exportado/Regressao_{reg}{nome_saida}.xlsx', index = False)

    if reg == 'nlinear':
        reg_ind = pd.DataFrame(reg_ind, columns = ['Fonte', 'Erro (R2)', 'Índices', 'Amostras'])
        reg_ind.to_excel(f'Exportado/Regressao_{reg}{nome_saida}.xlsx', index = False)

    return y_pred
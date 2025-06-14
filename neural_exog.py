import os
import math
import torch
import random

import pandas as pd
import numpy as np
# import torch_directml

# fazer caso passando todas as gerações de uma vez para verificar se o modelo aprende as relações entre as fontes
# passar variaveis de controle pós 2025 e deixar as fontes até 2024, com o objetivo de prever as fontes de 2025

from torch.optim import AdamW
from torch.optim.lr_scheduler import OneCycleLR
from transformers import EarlyStoppingCallback, Trainer, TrainingArguments, set_seed

from tsfm_public import (
    TimeSeriesForecastingPipeline,
    TimeSeriesPreprocessor,
    TinyTimeMixerForPrediction,
    TrackingCallback,
    count_parameters,
    get_datasets,
)

from tsfm_public.toolkit.time_series_preprocessor import prepare_data_splits
from tsfm_public.toolkit import RecursivePredictor, RecursivePredictorConfig
from matplotlib import rc, pyplot as plt, dates as mdates
from sklearn.metrics import r2_score

# Configurações de plotagem --------------------------------------------------------------------------------------------
rc('font', family = 'serif', size = 8)
rc('grid', linestyle = '--', alpha = .5)
rc('axes', axisbelow = True, grid = True)
rc('lines', linewidth = .8, markersize = 1.5)
rc('axes.spines', top = False, right = False, left = True, bottom = True)

# Definições do TTM ----------------------------------------------------------------------------------------------------

TTM_MODEL_REVISION = '180-60-ft-l1-r2.1'
CONTEXT            = 180
PREDICTION         = 60
OUT_DIR            = 'Exportado/TTM'
# MODELO_DIR         = 'Exportado/TTM/output/finetuned_diario_180_60'
MODELO_DIR         = 'ibm-granite/granite-timeseries-ttm-r2'
DEVICE             = 'cpu'
SEED               = 1337

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
set_seed(SEED)
torch.set_num_threads(24)
torch.set_num_interop_threads(24)

# Entrada de dados -----------------------------------------------------------------------------------------------------
# carga = (
#     pd.read_csv(
#         'Exportado/carga_subsist_diario_MWmed.csv', 
#         parse_dates = ['Data'],
#     )
#     .set_index('Data')
# )

sst = (
    pd.read_csv(
        'Exportado/ECMWF/derived-era5-single-levels-daily-statistics_sea_surface_temperature_reanalysis.csv', 
        parse_dates = ['Data'],
    )
    .set_index('Data')
    # .resample('W').mean()
)

geracao = (
    pd.read_csv(
        'Exportado/geracao_fontes_diario_MWmed.csv', 
        parse_dates = ['Data'],
    )
    .set_index('Data')
    .fillna(0)
    # .resample('W').mean()
)

sst_cols = sst.columns.tolist()
# carga_cols = carga.columns.tolist()
freq = 'D'
tempo = 'Data'
control_cols = sst_cols
fontes = [']]', 'Eólica', 'Fotovoltaica', 'Térmica', 'Outras']
subsistemas = ['N', 'NE', 'S', 'SE']

# geracao_antiga = geracao[geracao.index.year < 2025]
dataset = pd.concat([sst, geracao], axis = 1)
dataset = dataset[dataset.index.year < 2025]
print(f'\nDataset:\n {dataset}')

targets = np.zeros((len(fontes)), dtype = object)
for i, fonte in enumerate(fontes):
    targets[i] = []
    targets[i].append(f'{fonte}')
    for subsistema in subsistemas:
        targets[i].append(f'{fonte}_{subsistema}')

print(f'\nTargets:\n {targets}')

for target in targets:
    df = dataset[target + sst_cols]
    df = df.reset_index()
    print(f'\nX:\n {df}')

    split_config = {
        'train': [0, 0.6],
        'valid': [0.6, 0.8],
        'test': [0.8, 1.0]
    }
    
    df_train, df_valid, df_test = prepare_data_splits(
        df,
        context_length = CONTEXT, 
        split_config = split_config,
    )

    tsp = TimeSeriesPreprocessor(
        timestamp_column = tempo,
        target_columns = target,
        control_columns = control_cols,
        encode_categorical = False,
        context_length = CONTEXT,
        prediction_length = PREDICTION,
        scaling = True,
        scaler_type = 'standard',
        freq = freq,
    )

    print(f"Target columns: {target}")
    print(f"Control columns: {control_cols}")
    print(f"Dataset shape: {df.shape}")
    print(f"Number of NaN values: {df.isnull().sum().sum()}")
    print(f"TSP num_input_channels: {tsp.num_input_channels}")
    print(f"TSP prediction_channel_indices: {tsp.prediction_channel_indices}")
    print(f"TSP exogenous_channel_indices: {tsp.exogenous_channel_indices}")

    finetune_model = TinyTimeMixerForPrediction.from_pretrained(
        MODELO_DIR,
        revision = TTM_MODEL_REVISION,
        num_input_channels = tsp.num_input_channels,
        decoder_mode = 'mix_channel',
        prediction_channel_indices = tsp.prediction_channel_indices,
        exogenous_channel_indices = tsp.exogenous_channel_indices,
        fcm_context_length = 180,
        fcm_use_mixer = True,
        # fcm_mix_layers = 1,
        enable_forecast_channel_mixing = True,
        fcm_prepend_past = True,
    )

    print('Parâmetros antes de freezar o backbone:', count_parameters(finetune_model))

    train_dataset, valid_dataset, test_dataset = get_datasets(
        tsp, df, split_config, use_frequency_token = finetune_model.config.resolution_prefix_tuning
    )

    learning_rate = 5e-5
    num_epochs = 100
    batch_size = 64

    print(f'Tamanho ods datasets: train = {len(train_dataset)}, val = {len(valid_dataset)}, test = {len(test_dataset)}')
    print(f'Tamanho total do dataset: {len(df)}')
    print(f'Steps por época: {math.ceil(len(train_dataset) / batch_size)}')
    print(f'Colunas objetivo: {target}')
    print(f'Número de colunas de controle: {len(control_cols)}')
    if len(train_dataset) < 50:
        print('Menos de 50 amostras no conjunto de treinamento')

    print(f"Learning rate = {learning_rate}")
    finetune_forecast_args = TrainingArguments(
        output_dir = f'{OUT_DIR}/output',
        overwrite_output_dir = True,
        learning_rate = learning_rate,
        # lr_scheduler_type = 'cosine',
        # warmup_steps = 10,
        num_train_epochs = num_epochs,
        do_eval = True,
        eval_strategy = 'epoch',
        eval_steps = 1,
        per_device_train_batch_size = batch_size,
        per_device_eval_batch_size = batch_size,
        # gradient_accumulation_steps = 2,
        dataloader_num_workers = 0,
        report_to = None,
        save_strategy = 'epoch',
        save_steps = 10,
        logging_steps = 1,
        save_total_limit = 5,
        logging_strategy = 'epoch',
        logging_dir = f'{OUT_DIR}/logs',
        load_best_model_at_end = True,
        metric_for_best_model = "eval_loss",
        greater_is_better = False,
        use_cpu = True,
    )

    early_stopping_callback = EarlyStoppingCallback(
        early_stopping_patience = 30,
        early_stopping_threshold = .0005,
    )
    tracking_callback = TrackingCallback()

    optimizer = AdamW(finetune_model.parameters(), lr=learning_rate)

    scheduler = OneCycleLR(
        optimizer,
        learning_rate,
        epochs = num_epochs,
        steps_per_epoch = math.ceil(len(train_dataset) / (batch_size)),
    )

    finetune_forecast_trainer = Trainer(
        model = finetune_model,
        args = finetune_forecast_args,
        train_dataset = train_dataset,
        eval_dataset = valid_dataset,
        callbacks = [early_stopping_callback, tracking_callback],
        optimizers = (optimizer, scheduler),
    )

    # Fine tune
    finetune_forecast_trainer.train()

    pipeline = TimeSeriesForecastingPipeline(
        finetune_model,
        device = DEVICE,
        feature_extractor = tsp,
        batch_size = batch_size,
        explode_forecasts = True,
        freq = freq,
    )

    finetune_forecast = pipeline(df_test)
    finetune_forecast.head()

    ##################################################### GRÁFICOS #####################################################
    
    finetune_forecast = finetune_forecast.set_index('Data')
    pred_men = finetune_forecast.resample('ME').mean()
    pred_men.index = pred_men.index.to_period('M').to_timestamp()

    df_train.set_index('Data', inplace = True)
    df_train = df_train.resample('ME').mean()
    df_train.index = df_train.index.to_period('M').to_timestamp()

    df_valid.set_index('Data', inplace = True)
    df_valid = df_valid.resample('ME').mean()
    df_valid.index = df_valid.index.to_period('M').to_timestamp()

    df_test.set_index('Data', inplace = True)
    df_test = df_test.resample('ME').mean()
    df_test.index = df_test.index.to_period('M').to_timestamp()
    df_valid = df_valid.drop(df_test.index, errors = 'ignore')
    df_test = pd.concat([df_valid.tail(1), df_test])

    geracao_men = geracao[target].resample('ME').mean()
    geracao_men.index = geracao_men.index.to_period('M').to_timestamp()
    geracao_obs = geracao_men.loc[geracao_men.index.year > 2024]
    geracao_obs = pd.concat([df_test.tail(1), geracao_obs])

    y_pred = pred_men.reindex(df_test.index).dropna()
    y_true = geracao_men.reindex(y_pred.index).dropna()

    print(f'\nPrevisão:\n {y_pred}')
    print(f'\nGeração observada:\n {y_true}')
    
    fig, axs = plt.subplots(len(target), 1, figsize = (6, len(target) * 3), sharex = False)
    for i, col in enumerate(pred_men.columns):
        erro_r2 = r2_score(y_true[col], y_pred[col])

        axs[i].plot(df_train.index, df_train[col], label = 'Treino', c = '#000000')
        axs[i].plot(df_valid.index, df_valid[col], label = 'Validação', c = '#000000', ls = '--')
        axs[i].plot(df_test.index, df_test[col], label = 'Teste', c = '#000000', alpha = .33)
        axs[i].plot(geracao_obs.index, geracao_obs[col], label = 'Observado', c = "#000000", alpha = .33, ls = '--')
        axs[i].plot(pred_men.index, pred_men[col], label = 'Previsão', c = "#4A7AFF", lw = .8)

        axs[i].text(
            0.02, .98, 
            f'R² = {erro_r2:.4f}',
            transform = axs[i].transAxes, verticalalignment = 'top', fontsize = 7,
            bbox = dict(boxstyle = 'square', facecolor = 'white', edgecolor = 'none')
        )

        axs[i].set_ylabel(f'{col.replace('_', ' ')} [MWmed]')
        axs[i].xaxis.set_major_locator(mdates.AutoDateLocator())
        axs[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    axs[0].legend(loc = 'upper center', bbox_to_anchor = (0.5, 1.15), ncol = 5, frameon = False)
    axs[-1].set_xlabel('Série temporal')
    plt.tight_layout()
    plt.savefig(f'Graficos/Neural/{target[0]}_finetune_{freq}{CONTEXT}_v3.png')
    plt.show()
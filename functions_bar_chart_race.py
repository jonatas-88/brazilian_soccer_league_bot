#!/usr/bin/env python
import os
import sys
import configparser
import glob
import pandas as pd
from datetime import datetime
import bar_chart_race as bcr

init_config_file_name = 'bot_campeonato_brasileiro_2021.ini'

#IMPORT CONFIG FROM FILE .INI
#cwd = os.path.dirname(sys.argv[0]) #working on linux server or windows python script
cwd = os.getcwd() #working on windows during python notebook execution
cfg = configparser.ConfigParser()
ini_config_path = os.path.join(cwd,init_config_file_name)
cfg.read(ini_config_path)
exported_folder = cfg['general_config']['exported_folder']
bar_chart_race_video_folder = cfg['general_config']['bar_chart_race_video_folder']
pattern_name_positions = cfg['general_config']['pattern_name_positions']
pattern_name_general_classification = cfg['general_config']['pattern_name_general_classification']
max_pos = int(cfg['general_config']['max_pos'])
max_pos_sum = sum([x for x in range(max_pos,0,-1)][:5])

exported_files_pattern_gen_class = os.path.join(exported_folder,pattern_name_general_classification)

#FUNCTIONS
#FUNCTION TO IDENTIFY CSV FILES FROM FOLDER
def get_csv_from_folder():
    exported_files_list = glob.glob(exported_files_pattern_gen_class + '*.csv')
    return exported_files_list

#FUNCTION TO TRANSFORM EACH CSV INTO DATAFRAME
def transform_data_frame_pos(csv_file,act_serie):
    #IDENTIFY FILE DATE PATTERN
    file_date = csv_file.removeprefix(exported_files_pattern_gen_class)
    file_date = file_date.removesuffix('.csv')
    file_date = datetime.strptime(file_date, '%Y%m%d_%H%M%S').strftime('%Y-%m-%d')
    #TRANSFORM DATA FRAME
    df = pd.read_csv(csv_file)
    df = df[df.serie == act_serie]
    df = df[['nome', 'soma_pontos', 'soma_posicao', 'pos1', 'pos2', 'pos3', 'pos4', 'pos5']]
    #CREATE NEW COLUMN
    df['pontuacao'] = df.apply(lambda x: 
        float(
            str(x.soma_pontos) + '.0' + 
            '{:02d}'.format(max_pos_sum - x.soma_posicao) +
            '{:02d}'.format(max_pos - x.pos1) +
            '{:02d}'.format(max_pos - x.pos2) +
            '{:02d}'.format(max_pos - x.pos3) +
            '{:02d}'.format(max_pos - x.pos4) +
            '{:02d}'.format(max_pos - x.pos5)
        )
        , axis=1
    )
    df = df[['pontuacao', 'nome']]
    df = df.set_index('nome')
    df = df.sort_index()
    df = df.rename(columns={'pontuacao': file_date})
    df = df.T
    return df

#FUNCTION TO CREATE DATA FRAME FROM CSV FILES WITH DATA TRANFORMED
def generate_data_frame_from_csv(exported_files_list, act_serie):
    df_list = []
    for key, item in enumerate(exported_files_list):
        csv_file = item
        df_act = transform_data_frame_pos(csv_file, act_serie)
        df_list.append(df_act)
    df_final = pd.concat(df_list)
    df_final = df_final.drop_duplicates()
    return df_final

#FUNCTION TO EXPORT VIDEO FILE
def export_video_file_from_data_frame(df_received, act_serie):
    time_now = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = os.path.join(cwd, bar_chart_race_video_folder, 'bar_chart_race_serie_' + act_serie + '_' + time_now + '.mp4')
    bcr.bar_chart_race(
        df=df_received,
        filename=file_name,
        title='Corrida do Bolão do Campeonato Brasileiro - Série ' + act_serie.upper(), #title
        figsize=(6, 4.4),
        dpi=144,
        n_bars=18,
        fixed_max=True,
        steps_per_period=25,
        period_length=400,
        cmap='Dark24', #color map: Antique, Dark24
        interpolate_period=False,
        bar_size=.80,
        period_label={'x': .95, 'y': .05, 'ha': 'right'},
        #filter_column_colors=True,
        )
    return file_name

#MAIN FUNCTION TO REQUEST VIDEO FILE
def generate_video_file(act_serie='a'):
    try:
        exported_files_list = get_csv_from_folder()
        df = generate_data_frame_from_csv(exported_files_list, act_serie)
        file_name = export_video_file_from_data_frame(df, act_serie)
    except:
        return ''
    return file_name

#!/usr/bin/env python
import logging
import os
import sys
import configparser
from telegram import *
from telegram.ext import *
from datetime import datetime

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime

init_config_file_name = 'bot_campeonato_brasileiro_2021.ini'

#IMPORT CONFIG FROM FILE .INI
cwd = os.path.dirname(sys.argv[0]) #working on linux server or windows python script
#cwd = os.getcwd() #working on windows during python notebook execution
cfg = configparser.ConfigParser()
ini_config_path = os.path.join(cwd,init_config_file_name)
cfg.read(ini_config_path)
file_name_csv_cls = cfg['general_config']['file_name_csv_cls']
mg_url_serie_a = cfg['general_config']['mg_url_serie_a']
mg_url_serie_b = cfg['general_config']['mg_url_serie_b']

bot_token = cfg['telegram_config']['bot_token']

folder_export_csv = os.path.join(cwd,'exported_csv')
csv_cls = os.path.join(cwd, file_name_csv_cls)
[name_posicao, name_time, name_pontos, name_jogos, name_vitorias, name_empates, name_derrotas, name_golspro, name_golscontra, name_saldogols, name_aproveitamento] = ['Posicao', 'Time', 'Pontos', 'Jogos', 'Vitorias', 'Empates', 'Derrotas', 'GolsPro', 'GolsContra', 'SaldoGols', 'Aproveitamento']
[t_nome, t_serie, t_1, t_2, t_3, t_4, t_5, t_pontos, t_posicao, t_pos1, t_pos2, t_pos3, t_pos4, t_pos5, t_chave, t_colocacao] = ['nome', 'serie', 'time1', 'time2', 'time3', 'time4', 'time5', 'soma_pontos', 'soma_posicao', 'pos1', 'pos2', 'pos3', 'pos4', 'pos5', 'chave', 'colocacao']

#FUNCTION TO GET TABLE
def get_table_from_mgs():
  list_var = [name_posicao, name_time, name_pontos, name_jogos, name_vitorias, name_empates, name_derrotas, name_golspro, name_golscontra, name_saldogols, name_aproveitamento]
  df_tb_a = pd.read_html(mg_url_serie_a,header=0)[0]
  df_tb_b = pd.read_html(mg_url_serie_b,header=0)[0]
  df_tb_a.columns = list_var
  df_tb_b.columns = list_var
  df_pos_a = df_tb_a[[name_time, name_pontos, name_posicao]].set_index(name_time)
  df_pos_b = df_tb_b[[name_time, name_pontos, name_posicao]].set_index(name_time)
  df_pos = df_pos_a.append(df_pos_b)
  return df_tb_a, df_tb_b, df_pos

#FUNCTION TO CLASSIFY POSITIONS ACCORDING TO RULES
def classify_positions(csv_path,df_pos):
  df_cls = pd.read_csv(csv_path,';')
  for index, row in df_cls[[t_nome]].iterrows():
    sum_pontos = df_pos.loc[df_cls.loc[index, t_1], name_pontos] + df_pos.loc[df_cls.loc[index, t_2], name_pontos] + df_pos.loc[df_cls.loc[index, t_3], name_pontos] + df_pos.loc[df_cls.loc[index, t_4], name_pontos] + df_pos.loc[df_cls.loc[index, t_5], name_pontos]
    sum_posicao = df_pos.loc[df_cls.loc[index, t_1], name_posicao] + df_pos.loc[df_cls.loc[index, t_2], name_posicao] + df_pos.loc[df_cls.loc[index, t_3], name_posicao] + df_pos.loc[df_cls.loc[index, t_4], name_posicao] + df_pos.loc[df_cls.loc[index, t_5], name_posicao]
    df_cls.loc[index,[t_pontos, t_posicao]] = [sum_pontos, sum_posicao]
    list_pos = [df_pos.loc[df_cls.loc[index, t_1], name_posicao], df_pos.loc[df_cls.loc[index, t_2], name_posicao], df_pos.loc[df_cls.loc[index, t_3], name_posicao], df_pos.loc[df_cls.loc[index, t_4], name_posicao], df_pos.loc[df_cls.loc[index, t_5], name_posicao]]
    df_cls.loc[index,[t_pos1, t_pos2, t_pos3, t_pos4, t_pos5]] = list_pos
    df_cls.loc[index,[t_chave]] = ['-'.join((str(sum_pontos), str(sum_posicao), str(df_cls.loc[index, t_pos1]), str(df_cls.loc[index, t_pos2]), str(df_cls.loc[index, t_pos3]), str(df_cls.loc[index, t_pos4]), str(df_cls.loc[index, t_pos5])))]
  df_cls.sort_values(by=[t_pontos, t_posicao, t_pos1, t_pos2, t_pos3, t_pos4, t_pos5], ascending=[False, True, True, True, True, True, True], inplace=True)
  df_cls = df_cls.reset_index(drop=True)
  df_cls
  df_cls[t_colocacao] = ''
  return df_cls

#FUNCTION TO CLASSFIY POSITIONS INSIDE EACH SERIE AND GENERATE UNIQUE POSITION
def classify_positions_for_serie(df_cls,act_serie):
  new_df = df_cls[(df_cls[t_serie] == act_serie)].copy()
  act_pos = 0
  act_sum_pontos = '0-x'
  act_chave = '0-x'
  for index, row in new_df[[t_pontos]].iterrows():
    it_sum_pontos = new_df.loc[index, t_pontos]
    it_chave = new_df.loc[index, t_chave]
    if it_sum_pontos == act_sum_pontos and it_chave == act_chave:
      new_df.loc[index, t_colocacao] = act_pos
    else:
      act_pos += 1
      new_df.loc[index, t_colocacao] = act_pos
    act_sum_pontos = new_df.loc[index, t_pontos]
    act_chave = new_df.loc[index, t_chave]
  new_df = new_df.reset_index(drop=True)
  new_df = new_df[[t_serie, t_colocacao, t_nome, t_pontos]]
  return new_df

#FUNCTION TO GENERATE DATAFRAME WITH USERS POSITIONS CALCULATED
def generate_users_positions(df_cls):
  list_serie = df_cls[t_serie].unique()
  list_serie.sort()
  positions_list = []
  for idx, act_serie in enumerate(list_serie):
    df_to_append = classify_positions_for_serie(df_cls,act_serie)
    positions_list.append(df_to_append)
  df_positions = pd.concat(positions_list, ignore_index=True)
  return df_positions

#FUNCTION TO UPDATE POSITIONS INTO CLASSIFICATION TABLE
def update_positions_to_classification_table(df_cls, df_positions):
  df_received = df_cls.copy()
  for index, row in df_positions.iterrows():
    act_pos_serie = df_positions.loc[index, t_serie]
    act_pos_name = df_positions.loc[index, t_nome]
    act_pos_class = df_positions.loc[index, t_colocacao]
    line = '{} - {} - {}'.format(act_pos_serie, act_pos_name, act_pos_class)
    df_received.loc[(df_received[t_serie]==act_pos_serie) & (df_received[t_nome]==act_pos_name), t_colocacao] = act_pos_class
  return df_received

#FUNCTION TO CREATE A MESSAGE WITH USER CLASSIFICATIONS
def result_table(df_received):
  table_result_to_print = ''
  table_result_to_print += 'SERIE - CLASSIFICAÇÃO - NOME - PONTOS' + '\n'
  for index, row in df_received[[t_colocacao]].iterrows():
    table_result_to_print += '{} - {} - {} - {}'.format(df_received.loc[index, t_serie].upper(), df_received.loc[index, t_colocacao], df_received.loc[index, t_nome], df_received.loc[index, t_pontos]) + '\n'
  return table_result_to_print

#FUNCTION TO CREATE A MESSAGE WITH USER CLASSIFICATIONS BY SERIE
def result_table_by_serie(df_received, act_serie):
  df_received = df_received[(df_received[t_serie] == act_serie)]
  table_result_to_print = ''
  table_result_to_print += 'SÉRIE ' + act_serie.upper() + '\n'
  table_result_to_print += 'POSIÇÃO - NOME - PONTOS' + '\n'
  for index, row in df_received[[t_colocacao]].iterrows():
    table_result_to_print += '{} - {}... - {}'.format(df_received.loc[index, t_colocacao], df_received.loc[index, t_nome][:16], df_received.loc[index, t_pontos]) + '\n'
  return table_result_to_print

#FUNCTION TO GET MESSAGE CLASSIFICATION
def get_message_classification():
  df_tb_a, df_tb_b, df_pos = get_table_from_mgs()
  df_cls = classify_positions(csv_cls,df_pos)
  df_positions = generate_users_positions(df_cls)
  message_classification = result_table(df_positions)
  return message_classification

#FUNCTION TO GET MESSAGE CLASSIFICATION FOR SERIE
def get_message_classification_for_serie(act_serie):
  df_tb_a, df_tb_b, df_pos = get_table_from_mgs()
  df_cls = classify_positions(csv_cls,df_pos)
  df_positions = generate_users_positions(df_cls)
  message_classification = result_table_by_serie(df_positions, act_serie)
  return message_classification

#FUNCTION TO CREATE FOLDER IF NOT EXISTS
def check_export_folder(folder_path):
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

#FUNCTION TO SAVE CSV WITH USER POSITIONS
def export_users_positions():
  df_tb_a, df_tb_b, df_pos = get_table_from_mgs()
  df_cls = classify_positions(csv_cls,df_pos)
  df_positions = generate_users_positions(df_cls)
  now = datetime.now()
  time_now = now.strftime("%Y%m%d_%H%M%S")
  file_to_export = r'classificacao_' + time_now + '.csv'
  path_to_export = os.path.join(folder_export_csv,file_to_export)
  df_positions.to_csv(path_to_export, index=False, encoding='utf-8')

#FUNCTION TO SAVE CSV WITH MAIN CLASSIFICATION TABLE INCLUDING USER POSITIONS
def export_main_classification_with_users_positions():
  df_tb_a, df_tb_b, df_pos = get_table_from_mgs()
  df_cls = classify_positions(csv_cls,df_pos)
  df_positions = generate_users_positions(df_cls)
  df_received = update_positions_to_classification_table(df_cls, df_positions)
  now = datetime.now()
  time_now = now.strftime("%Y%m%d_%H%M%S")
  file_to_export = r'tabela_geral_' + time_now + '.csv'
  path_to_export = os.path.join(folder_export_csv,file_to_export)
  df_received.to_csv(path_to_export, index=False, encoding='utf-8')


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Olá, eu sou o bot de classificação do bolão do Campeonato Brasileiro 2021')

def serie_a(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(get_message_classification_for_serie('a'))

def serie_b(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(get_message_classification_for_serie('b'))

def save_csv(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Salvando arquivos CSV!')
    export_users_positions()
    export_main_classification_with_users_positions()

def handle_message(update, context):
    text = str(update.message.text).lower()
    response = text_responses(text, update, context)
    update.message.reply_text(response)

def text_responses(input_text, update, context):
    user_message = str(input_text).lower()
    user_message_words_list = user_message.split()

    table_key_words_list = [
        'classificacao', 'classificação', 'classificacão', 'classificaçao',
        'tabela', 'bolão', 'bolao', 'atualização', 'atualizacao',
        ]  

    for word in user_message_words_list:
        if word in table_key_words_list:
            return 'Para saber a classificação do bolão, digite /serie_a ou /serie_b'

def image(update: Update, context: CallbackContext) -> None:
  context.bot.send_message(chat_id=update.effective_chat.id, text='Image to send')
  context.bot.send_photo(chat_id=update.effective_chat.id, photo='https://i.pinimg.com/originals/79/8f/68/798f68e2a08dae914b36a41b5f9596c4.png')

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Digite /start para saber mais sobre esse bot.')

def error(update, context):
  print(f'Update {update} caused error {context.error}')

def main():
    # Create the Updater and pass it your bot's token.
    
    check_export_folder(folder_export_csv)

    updater = Updater(bot_token)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('serie_a', serie_a))
    updater.dispatcher.add_handler(CommandHandler('serie_b', serie_b))
    updater.dispatcher.add_handler(CommandHandler('save_csv', save_csv))
    updater.dispatcher.add_handler(CommandHandler('image', image))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()

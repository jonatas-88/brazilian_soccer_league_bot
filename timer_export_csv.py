import os
import sys
import time
import bot_campeonato_brasileiro_2021 as bot_cb
from datetime import datetime
from pathlib import Path

#home = "/mnt"

t_lenght = "%H%M"

target_time = '2253'

time_now = datetime.now()
t1 = time_now.strftime(t_lenght)

while True:
	time_now = datetime.now()
	t2 = time_now.strftime(t_lenght)
	#while t1 == t2:
	if t2 == target_time:
		time.sleep(1)
		t2 = datetime.now().strftime(t_lenght)

		print(' aqui funcionou ')
		#bot_cb.export_users_positions()
		#bot_cb.export_main_classification_with_users_positions()

	#os.system("python3 " + home + "/create_pic/vid_creator.py " + str(t1))
	t1 = t2
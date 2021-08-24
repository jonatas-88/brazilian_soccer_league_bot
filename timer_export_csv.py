import time
import bot_campeonato_brasileiro_2021 as bot_cb
from datetime import datetime

t_lenght = "%H%M"

target_time = '0200'

time_now = datetime.now()
t1 = time_now.strftime(t_lenght)

while True:
	time.sleep(1)
	time_now = datetime.now()
	t2 = time_now.strftime(t_lenght)
	if t2 == target_time:
		time.sleep(1)
		t2 = datetime.now().strftime(t_lenght)
		bot_cb.export_users_positions()
		bot_cb.export_main_classification_with_users_positions()
		time.sleep(60)
	t1 = t2
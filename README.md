# brazilian_soccer_league_bot
This repository contains a telegram bot that manage groups bets and classify according to brazilian soccer league.

I'm running all scripts on my server with Ubuntu Server 20.04.2 LTS.

Usually I create everything using a python notebook, test and check if everything is ok, then I export the code to python script .py.

This python script is scheduled on linux using services (services creation was described on file "how_to_install.info").

This service start a shell script that restart on failure according to service that was created. This shell script runs the python script that put the bot running on idle mode.

HOW TO USE:
-Open the file "your_file_name_with_group_bets.cvs" and fill info related to columns according to described below:
-nome: "NAME OF EACH PERSON"
-serie: "a" or "b" (each person must choose 5 teams for each serie, write these into separate lines)
-time1, time2, time3, time4, time5: soccer team names (exactly like appears on links url_serie bot_campeonato_brasileiro_2021.ini)

IMPORTANT
-You must remove "sample." from all file names that have it, like below:
-sample.bot_campeonato_brasileiro_2021.ini > bot_campeonato_brasileiro_2021.ini
-sample.bot_service.service > bot_service.service
...

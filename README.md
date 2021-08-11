# brazilian_soccer_league_bot
This repository contain a telegram bot that manage groups bets and classify according to brazilian soccer league.

I'm running all scripts on my server with Ubuntu Server 20.04.2 LTS.

Usually I create everything using a python notebook, test and check if everything is ok, then I export the code to python script .py.

This python script is scheduled on linux using services (services creation was described on file "how_to_install.info").

This service start a shell script that restart on failure according to service that was created. This shell script is runs the python script that put the bot running on idle mode.

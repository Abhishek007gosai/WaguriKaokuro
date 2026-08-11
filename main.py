# Some PaaS platforms (Koyeb buildpacks, etc.) default to running
# `main.py` when no explicit start/run command is configured. This
# repo's real entrypoint has always been `bot.py` (see Procfile,
# Dockerfile, render.yaml, heroku.yml). This file exists purely as a
# safety net so a platform that defaults to `python3 main.py` still
# launches the actual bot instead of failing with "No such file or
# directory: main.py".
#
# The preferred, explicit way to run this app is still:
#   python3 bot.py
from bot import main

if __name__ == "__main__":
    main()

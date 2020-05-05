#!/bin/sh
sh serve.bat &
disown
watchmedo shell-command -c "python3 preprocessor.py" -w -R lyrics

@echo off
REM Run with Daphne so HTTP + WebSocket (live chat) both work.
REM Uses 0.0.0.0 so your phone can open the site (e.g. http://192.168.1.3:8000)
cd /d "%~dp0"
python -m daphne -b 0.0.0.0 -p 8000 homefood.asgi:application
pause

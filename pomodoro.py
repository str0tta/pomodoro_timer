import requests
import sys
import datetime
from os import environ
from time import sleep
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

if sys.argv[1] == 'start':
    from flask import Flask

    app = Flask(__name__)

    phase = 1
    enabled = False
    if phase % 8 == 0: # 20 minutes long pause
        ticks = 20 * 60
    elif phase % 2 == 0: # normal 5 minutes pause
        ticks = 5 * 60
    else:
        ticks = 25 * 60

    @app.route("/remaining")
    def remaining():
        global ticks, enabled, phase
        if ticks == 0: return '--:--:--'
        minute, second = divmod(ticks, 60)
        hour, minute = divmod(minute, 60)
        if phase % 8 == 0: # 20 minutes long pause
            phase_str = 'long pause'
        elif phase % 2 == 0: # normal 5 minutes pause
            phase_str = 'pause'
        else: # normal pomodoro session
            phase_str = 'session ' + str(int((phase + 1) / 2))
        return f'{str(hour).zfill(2)}:{str(minute).zfill(2)}:{str(second).zfill(2)} ({phase_str})'

    @app.route("/toggle")
    def toggle():
        global enabled, ticks, phase
        enabled = not enabled
        return ''

    def timer_tick():
        global enabled, ticks, phase
        if not enabled: return
        ticks -= 1
        if ticks == 0:
            phase += 1
            if phase % 8 == 0: # 20 minutes long pause
                requests.get(environ.get('LONG_PAUSE'))
                ticks = 20 * 60
            elif phase % 2 == 0: # normal 5 minutes pause
                requests.get(environ.get('SHORT_PAUSE'))
                ticks = 5 * 60
            else: # normal pomodoro session
                requests.get(environ.get('NORMAL_SESSION'))
                ticks = 25 * 60
            enabled = False

    @app.route("/next")
    def next_session():
        global enabled, ticks, phase
        ticks = 1
        enabled = True
        return ''

    @app.route("/prev")
    def prev_session():
        global enabled, ticks, phase
        if ticks > 240: # more than four minutes passed so we'll repeat the same session
            if phase % 8 == 0: # 20 minutes long pause
                requests.get(environ.get('LONG_PAUSE'))
                ticks = 20 * 60
            elif phase % 2 == 0: # normal 5 minutes pause
                requests.get(environ.get('SHORT_PAUSE'))
                ticks = 5 * 60
            else: # normal pomodoro session
                requests.get(environ.get('NORMAL_SESSION'))
                ticks = 25 * 60
        else: # let's go back a session
            phase -= 1
            ticks = 1
        enabled = True
        return ''

    def poll_ticking():
        while True:
            timer_tick()
            sleep(1)

    Thread(target=poll_ticking).start()
    app.run(host=environ.get('IP_ADDRESS'), port=6565, debug=False)

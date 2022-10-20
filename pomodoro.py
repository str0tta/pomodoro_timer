import requests
import sys
import datetime
from time import sleep
from threading import Thread

if sys.argv[1] == 'start':
    from flask import Flask

    app = Flask(__name__)

    phase = 8
    enabled = False
    if phase % 8 == 0: # pausa lunga
        ticks = 20 * 60
    elif phase % 2 == 0: # pausa breve
        ticks = 5 * 60
    else:
        ticks = 25 * 60

    @app.route("/remaining")
    def remaining():
        global ticks, enabled, phase
        if ticks == 0: return '--:--:--'
        minute, second = divmod(ticks, 60)
        hour, minute = divmod(minute, 60)
        if phase % 8 == 0: # pausa lunga
            phase_str = 'pausa lunga'
        elif phase % 2 == 0: # pausa ogni due sessioni
            phase_str = 'pausa'
        else: # sessione normale
            phase_str = 'sessione ' + str(int((phase + 1) / 2))
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
            if phase % 8 == 0: # pausa lunga da 20 minuti
                requests.get('https://api.voicemonkey.io/trigger?access_token=2bbc0794a77b79c873f2ff4d118cab16&secret_token=cce42e4851068302693802426de8ffd5&monkey=pausa-lunga&announcement=Hello%20monkey')
                ticks = 20 * 60
            elif phase % 2 == 0: # pausa ogni due sessioni
                requests.get('https://api.voicemonkey.io/trigger?access_token=2bbc0794a77b79c873f2ff4d118cab16&secret_token=cce42e4851068302693802426de8ffd5&monkey=pausa&announcement=Hello%20monkey')
                ticks = 5 * 60
            else: # sessione normale
                requests.get('https://api.voicemonkey.io/trigger?access_token=2bbc0794a77b79c873f2ff4d118cab16&secret_token=cce42e4851068302693802426de8ffd5&monkey=sessione&announcement=Hello%20monkey')
                ticks = 25 * 60
            enabled = False

    def poll_ticking():
        while True:
            timer_tick()
            sleep(1)

    Thread(target=poll_ticking).start()
    app.run(host='192.168.188.170', port=6565, debug=False)

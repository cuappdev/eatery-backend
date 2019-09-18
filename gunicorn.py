from src.data import start_update

def on_starting(server):
    start_update()

workers = 4
timeout = 480
graceful_timeout = 60
bind = '0.0.0.0:5000'
preload_app = True

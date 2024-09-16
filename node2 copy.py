from jetmaker import join_app
from threading import Event

address = '127.0.0.1:9999'

app = join_app(
    host=address,
    password='123456',
    join_as='two'
)

items = []
ev = Event()

@app.stream_listen('uni')
def processor(message):
    print(f'{message} is read')
    items.append(message)
    if len(items) ==10:
        ev.set()

ev.wait()





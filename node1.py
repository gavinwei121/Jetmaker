from jetmaker import create_app

address = '127.0.0.1:9999'

app = create_app(
    host=address,
    password='123456',
    join_as='head'
)

def multiply(items):
    return [i*10 for i in items]

app.share(multiply, 'multiply')

class Instance:
    def __init__(self) -> None:
        self.names = []
    def add(self, name):
        self.names.append(name)
    def get_all(self, ):
        return self.names
    
instance = Instance()

app.share(instance, 'instance')


@app.stream_listen('uni')
def processor(message):
    print(f'{message} is read ok')



app.persist()





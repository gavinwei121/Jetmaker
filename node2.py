from jetmaker import join_app
import time

address = '127.0.0.1:9999'

app = join_app(
    host=address,
    password='123456',
    join_as='three'
)

multiply = app.call('multiply')

print(multiply.run([10,1000]))

instance = app.Object('instance')

print(instance.get_all())
instance.add('ok')
instance.add('another')
print(instance.get_all())

for i in range(10):
    app.broadcast('this', ['uni'])
    print('sent')
    



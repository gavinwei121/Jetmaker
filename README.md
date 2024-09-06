# Jetmaker
Jetmaker is an end-to-end framework designed to simplify the development of distributed systems in Python. It enables distributed Python applications to seamlessly access each other's services, resources, objects, and data, making inter-application interactions feel as though they are operating within the same environment. Jetmaker also provides powerful namespace sharing and synchronization tools, allowing distributed applications to work together as a unified, coordinated system.

# Installation
```pip install jetmaker```

# Resources
[Visit Documentation](https://remeny-technologies.gitbook.io/jetmaker-documentation)

# Getting Started
Below is a simple example of how two distributed nodes access each other's namespace and resource statefully
### Node 1
Use the IP address and port of Node 1 to start this Jetmaker app, the node calling create_app will act as the coordinator node.
```python
from jetmaker import create_app

host = '<you ip address>:<your port>'
pwd = '<your password>'

app = create_app(host=host, password=pwd, join_as='main_node')
```
create a simple function and a simple stateful object for testing
```python
def recv_string(string):
    return f'{string} is received'

app.link(js, 'js')

class Instance:
    def __init__(self) -> None:
        self.val = 0
    def set_value(self, val):
        self.val = val
    def get_value(self):
        return self.val
    
instance = Instance()
```
link it to the app for the network applications to access
```python
app.share(recv_string, 'recv_str')
app.share(instance, 'ins')
```
let this persist if you it always available for access
```python
app.persist()
```
### Node 2
On another remote node, you can join the network of distributed applications and share services of Node 2 or access services of other nodes .
Join the app
```python
from jetmaker import join_app

host = '<address of Node 1>:<port of Node 1>'
pwd = '<your password>'

app = join_app(host=host, password=pwd, join_as='other_node')
```
Access the function shared by Node1
```python
result = app.call('recv_str').run('this string')
```
```-> this string is received```

Access the object shared by Node1
```python

instance = app.Object('ins')
print(instance.get_value())
instance.set_value(100)
print(instance.get_value())
```
```
-> 0
-> 100
```



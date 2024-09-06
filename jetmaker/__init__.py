from jetmaker.newserve.main import Server, Client
from typing import Any, Dict, List
from types import FunctionType
from jetmaker.networking import random_address

class RemoteFunction:
    def __init__(self, head:Client, name:str, ) -> None:
        self.head = head
        self.name = name
    def run(self, *args, **kwargs):
        params = (args, kwargs)
        return self.head.call('run_function').run(self.name, params).get()
    
class RemoteAttr:
    def __init__(self, head:Client, name:str, obj_name:str) -> None:
        self.head = head
        self.name = name
        self.obj_name = obj_name
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.head.call('run_obj_attr').run(
            self.obj_name, self.name, (args, kwds)
        ).get()
    def get(self,):
        return None
    
class RemoteObject:
    def __init__(self, head:Client, name:str, ) -> None:
        self.head = head
        self.name = name
    def __getattribute__(self, name: str):
        try:
            return super().__getattribute__(name)
        except:
            return RemoteAttr(head=self.head, name=name, obj_name=self.name)

class Queue:
    def __init__(self, head:Client, name:str, create:bool) -> None:
        self.head = head
        self.name = name
        if create:
            granted = self.head.call('create_queue').run(name=name).get()
        else:
            found = self.head.call('create_queue').run(name=name).get()
    def put(self, item):
        self.head.call('queue_put').run(name=self.name, item=item).get()
    def get(self,):
        return self.head.call('queue_get').run(name=self.name).get()
    
class Event:
    def __init__(self, head:Client, name:str, create:bool) -> None:
        self.head = head
        self.name = name
        if create:
            self.head.call('create_event').run(name=name).get()
        else:
            self.head.call('create_event').run(name=name).get()
    def set(self):
        self.head.call('set_event').run(name=self.name).get()
    def wait(self):
        self.head.call('wait_event').run(name=self.name).get()
    def clear(self):
        self.head.call('clear_event').run(name=self.name).get()

class Lock:
    def __init__(self, head:Client, name:str, create:bool) -> None:
        self.head = head
        self.name = name
        if create:
            self.head.call('create_lock').run(name=name).get()
        else:
            self.head.call('create_lock').run(name=name).get()
    def acquire(self,):
        self.head.call('acquire_lock').run(name=self.name).get()
    def release(self,):
        self.head.call('release_lock').run(name=self.name).get()

class Map:
    def __init__(self, head:Client, name:str, create:bool) -> None:
        self.head = head
        self.name = name
        if create:
            self.head.call('create_map').run(name=name).get()
        else:
            self.head.call('create_map').run(name=name).get()

    def set(self, key, value):
        self.head.call('set_map').run(name=self.name, 
                                      key=key, 
                                      value=value)

    def get(self, key):
        return self.head.call('get_map').run(name=self.name, key=key).get()


class App:

    functions: Dict[str, callable] = dict()
    objects: Dict[str, object] = dict()

    def __run_function(self, name:str, params):
        args, kwargs = params
        return self.functions[name](*args, **kwargs)
    def __run_obj_attr(self, obj_name:str, attr_name:str, params):
        args, kwargs = params
        return self.objects[obj_name].__getattribute__(attr_name)(*args, **kwargs)
    
    def __setup(self):
        self.address = random_address()
       #print(self.address)
        self.running_server = Server(addr=self.address)
        self.running_server.bind('run_function')(self.__run_function)
        self.running_server.bind('run_obj_attr')(self.__run_obj_attr)
        return self.address

    def __init__(self, host:str, password:str, name:str) -> None:
        self.head = Client(addr=host)
        self.__setup()
        result = self.head.call('connect').run(pwd=password,
                                               name=name, 
                                            addr=self.address)
        self.name = name

    def space(self, name:str):
        pass
    def Queue(self, name:str, create:bool=None):
        return Queue(head=self.head, name=name, create=create)
    def Lock(self, name:str, create:bool=None):
        return Lock(head=self.head, name=name, create=create)
    def Dict(self, name:str, create:bool=None):
        pass
    def Event(self, name:str, create:bool=None):
        return Event(head=self.head, name=name, create=create)
    def share(self, obj, name:str):
        if isinstance(obj, FunctionType):
            self.functions[name] = obj
            self.head.call('register_func').run(self.name, name).get()
        else:
            self.objects[name] = obj
            self.head.call('register_obj').run(self.name, name).get()
    """def node(self, name:str):
        return Node(head=self.head, name=name)"""
    
    def Map(self, name:str):
        return Map(head=self.head, name=name, create=None)
    
    def Object(self, name:str):
        return RemoteObject(head=self.head, name=name)
    
    def call(self, name:str):
        return RemoteFunction(head=self.head, name=name)
    
    def persist(self):
        while True:
            input()
    
    
import os, sys, subprocess, threading

def run_head(host, password):
    # Get the absolute path of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get the Python interpreter path
    python_path = sys.executable
    
    # Join the file_to_run with the script_dir to make it an absolute path
    absolute_file_to_run = os.path.join(script_dir, 'head.py')
    
    # Run the specified file using the Python interpreter with the absolute path
    subprocess.run([python_path, 
                    absolute_file_to_run, 
                    host, password])
    
import time

threads = dict()
    
def join_app(host:str, password:str, join_as:str):
    return App(host=host, password=password, name=join_as)
        
def create_app(host:str, password:str, join_as:str):
    threads[0] = threading.Thread(target=run_head, args=(host, password))
    threads[0].start()
    time.sleep(1)
    return join_app(host=host, password=password, join_as=join_as)


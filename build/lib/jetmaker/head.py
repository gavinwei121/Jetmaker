from newserve.main import Server, Client
from argparse import ArgumentParser
from typing import Dict, List
from queue import Queue
from threading import Event, Lock

parser = ArgumentParser()
parser.add_argument('host')
parser.add_argument('password')

args = parser.parse_args()

host = args.host
password = args.password

queues:Dict[str, Queue] = dict()
events:Dict[str, Event] = dict()
#locks:Dict[str, Lock] = dict()
clients:Dict[str, Client] = dict()

virtual_locks:Dict[str, Queue] = dict()
dicts:Dict[str, dict] = dict()

function_proxies: Dict[str, str] = dict()
object_proxies: Dict[str, str] = dict()

create_dict_lock = Lock()
create_queue_lock = Lock()  # Added lock for queues
create_event_lock = Lock()  # Added lock for events
create_lock_lock = Lock()   # Added lock for virtual locks

def find_node(name:str):
    try:
        clients[name]
        return True
    except:
        return False

def create_queue(name:str):
    with create_queue_lock:
        try:
            queues[name] 
        except: # Locking the queue creation
            queues[name] = Queue()
    return True

def get_queue(name:str):
    try:
        queues[name]
        return True
    except:
        return False
    
def queue_put(name:str, item):
    queues[name].put(item)

def queue_get(name:str):
    queues[name].get()
    
"""def create_lock(name:str):
    locks[name] = Lock()
    return True

def get_lock(name:str):
    try:
        locks[name]
        return True
    except:
        return False
    
def acquire_lock(name:str):
    locks[name].acquire()

def release_lock(name:str):
    locks[name].release()"""

def create_lock(name:str):
    with create_lock_lock:  # Locking the virtual lock creation
        virtual_locks[name] = Queue()
        virtual_locks[name].put(0)
    return True

def get_lock(name:str):
    try:
        virtual_locks[name]
        return True
    except:
        return False
    
def acquire_lock(name:str):
    val = virtual_locks[name].get()
    #print('got')
    return val

def release_lock(name:str):
    virtual_locks[name].put(0)
    
def create_event(name:str):
    with create_event_lock: 
        try:
            events[name]
        except: # Locking the event creation
            events[name] = Event()
    return True

def get_event(name:str):
    try:
        events[name]
        return True
    except:
        return False
    
def set_event(name:str):
    events[name].set()

def wait_event(name:str):
    events[name].wait()

def clear_event(name:str):
    events[name].clear()
    

def connect(pwd:str, name:str, addr:str):
    if pwd == password:
        clients[name] = Client(addr=addr)
        return True
    else:
        return False
    
def run_function(func_name, params):
    node_name = function_proxies[func_name]
    cl = clients[node_name]
    return cl.call('run_function').run(func_name, params).get()
    

def run_obj_attr(obj_name:str, attr_name:str, params):
    node_name = object_proxies[obj_name]
    cl = clients[node_name]
    return cl.call('run_obj_attr').run(obj_name, attr_name, params).get()

def create_map(name:str):
    with create_dict_lock:
        try:
            dicts[name]
        except:
            dicts[name] = dict()

def set_map(name, key, value):
    dicts[name][key] = value

def get_map(name, key):
    try:
        return dicts[name][key]
    except:
        return None
    

def register_func(node_name:str, name:str):
    function_proxies[name] = node_name

def register_obj(node_name:str, name:str):
    object_proxies[name] = node_name


    


server = Server(addr=host)

server.bind('find_node')(find_node)
server.bind('create_queue')(create_queue)
server.bind('get_queue')(get_queue)
server.bind('queue_put')(queue_put)
server.bind('queue_get')(queue_get)
server.bind('create_lock')(create_lock)
server.bind('get_lock')(get_lock)
server.bind('acquire_lock')(acquire_lock)
server.bind('release_lock')(release_lock)
server.bind('create_event')(create_event)
server.bind('get_event')(get_event)
server.bind('set_event')(set_event)
server.bind('wait_event')(wait_event)
server.bind('clear_event')(clear_event)
server.bind('connect')(connect)
server.bind('run_function')(run_function)
server.bind('run_obj_attr')(run_obj_attr)
server.bind('create_map')(create_map)
server.bind('set_map')(set_map)
server.bind('get_map')(get_map)
server.bind('register_func')(register_func)
server.bind('register_obj')(register_obj)

input()
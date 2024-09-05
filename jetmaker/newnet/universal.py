from typing import Dict
universal_id_length = 16
delimiter = b'delimiter'

size_length = 12

import socket

def recv_bytes(connection:socket.socket, unit:int):
    total_data = []
    total_size = 0
    while total_size!=unit:
        data = connection.recv(unit-total_size)
        total_size += len(data)
        total_data.append(data)
    return b''.join(total_data)

def recv_data(connection:socket.socket):
    size = int.from_bytes(recv_bytes(connection, size_length), 'big')
    return recv_bytes(connection=connection,unit=size)

def send_data(connection:socket.socket, data:bytes):  
    connection.sendall(len(data).to_bytes(size_length, 'big')+data)

from threading import Event, Lock, Thread
from collections import deque
from queue import Queue

class NewQueue:
    def __init__(self) -> None:
        self.values = deque()
        self.event = Event()
        self.is_set = False
        self.lock = Lock()
        self.count = 0
        self.get_lock = Lock()

    def put(self, value):
        with self.lock:
            self.values.append(value)
            if not self.is_set:
                self.event.set()
                self.is_set=True
        
    def _get(self,):
        with self.lock:
            try:
                return self.values.popleft()
            except:
                if self.is_set:
                    self.event.clear()
                    self.is_set = False
                    
        self.event.wait()
        return self.values.popleft()
    
    def get(self):
        #with self.get_lock:
        return self._get()
        
import select

def is_connection_broken(sock):
    try:
        rlist, _, _ = select.select([sock], [], [], 0)
        if rlist:
            data = sock.recv(1, socket.MSG_PEEK)
            if not data:
                return True  # Connection closed
        return False
    except socket.error:
        return True 
    
import inspect

def get_globals():
    return inspect.currentframe().f_back.f_globals


class NewDict:
    def __init__(self) -> None:
        self.values = dict()
        self.lock = Lock()
        self.events = dict()
    def set(self, key, value):
        with self.lock:
            self.values[key] = value
            try:self.events[key].set()
            except:pass
    def get(self, name):
        with self.lock:
            try: return self.values[name]
            except: self.events[name] = Event()
        self.events[name].wait()
        del self.events[name]
        return self.values[name]

class NewStore:
    def __init__(self) -> None:
        self.values = dict()
        self.lock = Lock()
        self.events = dict()
    def set(self, key, value):
        with self.lock:
            self.values[key] = value
            try:self.events[key].set()
            except:pass
    def get(self, name):
        with self.lock:
            try: return self.values[name]
            except: self.events[name] = Event()
        self.events[name].wait()
        del self.events[name]
        return self.values[name]




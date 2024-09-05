from jetmaker.newnet.universal import universal_id_length, NewQueue, recv_data, is_connection_broken, send_data

import socket
from queue import Queue
from threading import Thread
from typing import Dict, List


class Request:
    def __init__(self, data:bytes, processor) -> None:
        self.message_id = data[:universal_id_length]
        self.content = data[universal_id_length:]
        self.processor=processor

    def reply(self, data:bytes):
        self.processor._send(self.message_id+data)

    def get_content(self):
        return self.content


class Processor:
    def __init__(self, request_sock:socket.socket, response_sock:socket.socket) -> None:
        self.request_sock=request_sock
        self.response_sock=response_sock

        # hold the data temporarily
        self.holder = b''
        # hold unreal messages
        self.unread_data:List[bytes] = [] 

        # queuing messages to be sent
        self.send_queue = NewQueue()

        # start the background sending thread
        Thread(target=self._sending, daemon=True).start()

    # sending thread
    def _sending(self,):
        while True:
            try:
                send_data(connection=self.response_sock, data=self.send_queue.get())
            except:
                break
    
    # used to receive requests
    def recv(self,):
        try:
        #is_connection_broken(self.request_sock)
            return Request(
                data=recv_data(connection=self.request_sock),
                processor=self
            )
        except:
            return None
                    
    
    def _send(self, data:bytes):
        self.send_queue.put(data)



class Socket:
    def __init__(self, address:str) -> None:
        [ip, port] = address.split(":")
        addr = (ip, int(port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(addr)
        sock.listen(0)

        self.sock = sock

        self.wait_connections = dict()

        self.processor_queue = Queue()

        Thread(target=self._waiting, daemon=True).start()

    def _waiting(self):

        while True:
            conn, _ = self.sock.accept()
            code = conn.recv(universal_id_length)   
            if code not in self.wait_connections.keys():
                self.wait_connections[code] = conn
                #print('no connection yet')
            else:
                # start processing messages
                processor = Processor(request_sock=self.wait_connections[code], response_sock=conn)
                self.processor_queue.put(processor)
                #print('got connection')

    def accept(self)->Processor:
        return self.processor_queue.get()
    

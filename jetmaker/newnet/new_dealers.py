from jetmaker.newnet.universal import send_data, universal_id_length, recv_data, size_length
import socket
from uuid import uuid4
from typing import Dict, List
from threading import Lock, Thread


class Response:
    def __init__(self, message_id:bytes, dealer) -> None:
        self.message_id=message_id
        self.dealer=dealer

    def get(self)->bytes:
        return self.dealer._recv(self.message_id)

class Dealer:
    def __init__(self, address:str) -> None:
        # connect then authenticate
        self.dealer_id = uuid4().bytes
        [ip, port] = address.split(':')
        addr = (ip, int(port))
        self.request_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.response_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.request_sock.connect(addr)
        self.request_sock.sendall(self.dealer_id)
        self.response_sock.connect(addr)
        self.response_sock.sendall(self.dealer_id)

        # hold the responses
        self.responses:Dict[bytes, bytes] = dict()
        
        # lock for receiving
        self.recv_lock = Lock()

        # start receiving
        #Thread(target=self._receiving, ).start()

    def request(self, data:bytes):
        # get message id
        message_id = uuid4().bytes
        # form message
        message = message_id + data
        # send out
        send_data( connection=self.request_sock, data=message)
        return Response(message_id=message_id, dealer=self)
    
    def _recv(self, message_id:bytes):
        with self.recv_lock:
            try:
                return self.responses[message_id]
            except:
                while True:
                    data = recv_data(connection=self.response_sock)
                    msg_id = data[:universal_id_length]
                    content = data[universal_id_length:]
                    self.responses[msg_id] = content
                    if msg_id == message_id:
                        return content
                
    def _receiving(self):
        while True:
            with self.recv_lock:
                try:
                    data = recv_data(connection=self.response_sock)
                    msg_id = data[:universal_id_length]
                    content = data[universal_id_length:]
                    self.responses[msg_id] = content
                except Exception as e:
                    print(e)

    
        
        
    


            
    
        
                

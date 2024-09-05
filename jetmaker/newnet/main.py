
import socket
from uuid import uuid4
from jetmaker.newnet.universal import delimiter, universal_id_length

from threading import Thread, Event
from queue import Queue

from typing import List, Dict



class Request:
    def __init__(self, message_id:bytes, content:bytes, processor) -> None:
        self.message_id = message_id
        self.content = content
        self.processor = processor
    def reply(self, data:bytes):
        self.processor._add_to_send(self.message_id+data)

class Processor:
    def __init__(self, request_sock:socket.socket, response_sock:socket.socket) -> None:
        self.request_sock=request_sock
        self.response_sock=response_sock

        # all the raw data to be sent
        self.unsent_data: List[bytes] = []
        # used to notify there's data to send
        self.unsent_event = Event()

        # store all the raw requests temporarily
        self.raw_requests:List[bytes] = []

        # event: in case there is demand to get unarrived requests
        self.requests_event = Event() 

        # start receiving requests
        Thread(target=self._receiving, daemon=True).start()

        # start sending back whatever responses
        Thread(target=self._sending, daemon=True).start()
    
    # send one round
    def _sending_one(self):
        if len(self.unsent_data)==0:
            # clear the event and wait for new
            if self.unsent_event.is_set():self.unsent_event.clear()
            # check again if there is any data
            if len(self.unsent_data)==0: self.unsent_event.wait()
        # sending this batch of data
        length = len(self.unsent_data)
        total_data = delimiter.join(self.unsent_data[:length])+delimiter
        # send the data but use response to send it back
        self.response_sock.sendall(total_data)

    # thread sending data
    def _sending(self):
        while True:
            self._sending_one()

    # add a data to be sent
    def _add_to_send(self, data:bytes):
        # add to the row first
        self.unsent_data.append(data)
        # check if it needs to notify
        if not self.unsent_event.is_set():
            self.unsent_event.set()

    # process individual request
    def _process_received(self, segment:bytes):
        # add to raw requests first
        self.raw_requests.append(segment)
        # see if the request needs to notify
        if not self.requests_event.is_set(): self.requests_event.set()

    # thread receiving data
    def _receiving(self):
        # data holder for incomplete messages
        holder = b''
        # receive data
        while True:
            data = self.request_sock.recv(1024)
            # add to the holder
            holder+=data
            # process current data
            for i in range(holder.count(delimiter)):
                idx = holder.index(delimiter)
                segment = holder[:idx]
                # cut the holder 
                holder = holder[idx+len(delimiter):]
                self._process_received(segment=segment)

    # to pre-recv a request 
    def _pre_recv(self,):
        # try to get one first
        try:
            data = self.raw_requests[0]
            self.raw_requests = self.raw_requests[1:]
            return data
        except:None
        # clear the event and wait
        self.requests_event.clear()
        # try again
        try:
            data = self.raw_requests[0]
            self.raw_requests = self.raw_requests[1:]
            return data
        except:None
        # then wait
        self.requests_event.wait()

        data = self.raw_requests[0]
        self.raw_requests = self.raw_requests[1:]
        return data
    
    # user interface to receive data
    def recv(self):
        # pre-recv
        data = self._pre_recv()
        # break down info and content
        message_id = data[:universal_id_length]
        content = data[universal_id_length:]
        return Request(message_id=message_id, content=content, processor=self)


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
            else:
                # start processing messages
                processor = Processor(request_sock=self.wait_connections[code], response_sock=conn)
                self.processor_queue.put(processor)

    def accept(self)->Processor:
        return self.processor_queue.get()


            
            
        

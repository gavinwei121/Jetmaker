from uuid import uuid4
import socket
from jetmaker.newnet.universal import delimiter, universal_id_length
from typing import Dict, List
from threading import Event, Thread


class Response:
    def __init__(self, message_id:bytes, dealer) -> None:
        self.message_id=message_id
        self.dealer=dealer
    def get(self)->bytes:
        return self.dealer._get_response(self.message_id)


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
        
        # all the raw data to be sent
        self.unsent_data: List[bytes] = []
        # used to notify there's data to send
        self.unsent_event = Event()

        # contain all responses 
        self.responses:Dict[bytes, bytes] = dict()
        # responses events: in case there are demand for unarrived messages
        self.response_events:Dict[bytes, Event] = dict()

        # start sending messages
        Thread(target=self._sending).start()
        # start receiving data
        Thread(target=self._receiving).start()
    
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
        # send the data
        self.request_sock.sendall(total_data)

        print('send')

        # cut the unsent data 
        self.unsent_data = self.unsent_data[length:]

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

    # process one message
    def _process_received(self, segment:bytes):
        # extract info from data
        message_id = segment[:universal_id_length]
        content = segment[universal_id_length:]
        # store this response
        self.responses[message_id] = content
        # check if there is a waiting event
        try:
            self.response_events[message_id].set()
        except:
            None

    # thread receiving data
    def _receiving(self):
        # data holder for incomplete messages
        holder = b''
        # receive data
        while True:
            data = self.response_sock.recv(10240)
            # add to the holder
            holder+=data
            # process current data
            for i in range(holder.count(delimiter)):
                idx = holder.index(delimiter)
                segment = holder[:idx]
                # cut the holder 
                holder = holder[idx+len(delimiter):]
                self._process_received(segment=segment)

    # used by response to get sent-back data
    def _get_response(self, message_id:bytes):
        # try to be retrieve the response
        try:
            return self.responses[message_id]
        except:None
        # create an event to wait for it 
        self.response_events[message_id] = Event()
        # try again
        try:
            return self.responses[message_id]
        except:None
        #  wait for the event to be set
        self.response_events[message_id].wait()
        return self.responses[message_id]
    
    def request(self, data:bytes)->Response:
        # generate a message id
        message_id = uuid4().bytes
        # put the message
        self._add_to_send(message_id+data)
        return Response(message_id=message_id, dealer=self)
    

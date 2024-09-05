from jetmaker.newnet.new_main import Socket, Processor, Request
from concurrent.futures import ThreadPoolExecutor
import cloudpickle
from threading import Thread, Event

class Server:

    def _handle_request(self, request:Request):
        try:
            content: dict = cloudpickle.loads(request.content)
            request.reply(
                cloudpickle.dumps(
                    self.responders[content['signal']](
                        *content['args'],
                        **content['kwargs']
                    )
                )
            )
        except:
            pass

    def _handle_connection(self, conn:Processor):
        while True:
            self.pool.submit(self._handle_request, conn.recv())
            #self._handle_request(conn.recv())

    def _receiving_connections(self):
        self.pool = ThreadPoolExecutor()
        self.responders = dict()

        sock = Socket(address=self.addr)
        self.sock = sock

        while True:
            conn = sock.accept()
            Thread(target=self._handle_connection, args=(conn, ), daemon=True).start()
            #self._handle_connection(conn=conn)

    def _check_closing(self):
        self.close_event.wait()

    def __init__(self, addr:str) -> None:
        self.addr = addr
        # start receiving connections
        Thread(target=self._receiving_connections, daemon=True).start()
        #self._receiving_connections()
        self.close_event = Event()
        Thread(target=self._check_closing, daemon=True).start()
    
    def bind(self, name:str):
        def __wrapper__(func):
            self.responders[name] = func
        return __wrapper__
    
    def close(self):
        self.close_event.set()
    

from jetmaker.newnet.new_dealers import Dealer, Response

class AwaitedResponse:
    def __init__(self, response: Response) -> None:
        self.response = response
    def get(self, ):
        return cloudpickle.loads(self.response.get())

class ClientRequest:
    def __init__(self, dealer:Dealer, name:str) -> None:
        self.name = name
        self.dealer = dealer
    def run(self, *args, **kwargs):
        return AwaitedResponse(
            self.dealer.request(
                cloudpickle.dumps(
                    {
                        'signal': self.name,
                        'args': args,
                        'kwargs': kwargs
                    }
                )
            )
        )

class Client:
    def __init__(self, addr:str) -> None:
        self.dealer = Dealer(address=addr)
    def call(self, name:str):
        return ClientRequest(dealer=self.dealer, name=name)


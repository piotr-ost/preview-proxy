import sys

from twisted.python import log
from twisted.internet import reactor
from autobahn.twisted.websocket import (WebSocketServerProtocol,
                                        WebSocketServerFactory)


class ProxyFactory(WebSocketServerFactory):

    def __init__(self):
        super().__init__()
        self.preview_clients = []

class ProxyProtocol(WebSocketServerProtocol):

    def __init__(self):
        super().__init__(self)
        self.is_preview_client = False

    def onConnect(self, request):
        try:
            if request.headers['user-agent']:
                self.is_preview_client = True
                print(f'preview client connecting {request.peer}')
        except KeyError:
            print(f'server client connecting {request.peer}')

    def onOpen(self):
        if self.is_preview_client:
            self.factory.preview_clients.append(self)

    def onMessage(self, payload, isBinary):
        print(f'forwarding message {payload.decode()}')
        for client in self.factory.preview_clients:
            client.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print(f'connection closed {reason}')


if __name__ == '__main__':
    log.startLogging(sys.stdout)

    factory = ProxyFactory()
    factory.protocol = ProxyProtocol

    reactor.listenTCP(8000, factory)
    reactor.run()


import sys

from twisted.python import log
from twisted.internet import reactor
from autobahn.twisted.websocket import (WebSocketServerProtocol,
                                        WebSocketServerFactory)


class ProxyFactory(WebSocketServerFactory):

    def __init__(self, url):
        super().__init__(url)
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
        for client in self.factory.clients:
            client.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print(f'connection closed {reason}')


if __name__ == '__main__':
    factory = ProxyFactory()
    factory.protocol = ProxyProtocol

    reactor.listenTCP(80, factory)
    reactor.run()


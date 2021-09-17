class Datagrama:

    def __init__(self, head, payload, eop):
        self.head = head
        self.payload = payload
        self.eop = eop

    def send_datagrama(self):
        datagrama = self.head + self.payload + self.eop
        return datagrama
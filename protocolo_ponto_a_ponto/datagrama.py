class Datagrama:

    def __init__(self, head=b'', payload=b''):
        self.head = head
        self.payload = payload
        self.eop = b'\xFF\xAA\xFF\xAA'

    def create_head(self, h0, h1=b'\x01', h2=b'\x02', h3=b'\x00', h4=b'\x00', h5=b'\x00', h6=b'\x00', h7=b'\x00', h8=b'\x00', h9=b'\x00'):
        self.head = h0 + h1 + h2 + h3 + h4 + h5 + h6 + h7 + h8 + h9

    def format_datagrama(self):
        datagrama = self.head + self.payload + self.eop
        return datagrama

class Datagrama:

    def __init__(self):
        self.head = b''
        self.payload = b''
        self.eop = b'\xFF\xAA\xFF\xAA'

    def create_head(h0, h1=b'x\01', h2=b'x\02', h3, h4, h5, h6, h7, h8=b'x\00', h9=b'x\00'):
        self.head = h0 + h1 + h2 + h3 + h4 + h5 + h6 + h7 + h8 + h9

    def format_datagrama(self):
        datagrama = self.head + self.payload + self.eop
        return datagrama

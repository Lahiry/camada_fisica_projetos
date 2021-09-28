from datetime import datetime

class Log():

  def __init__(self, mensagem, envio_ou_recebimento):
    self.time = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")
    self.envio_ou_recebimento = envio_ou_recebimento
    self.tipo_msg = mensagem[0]
    self.tamanho_total = len(mensagem)
    if self.tipo_msg == 3:
      self.id_pacote_enviado = mensagem[4]
      self.total_pacotes_arquivo = mensagem[3]
    else:
      self.id_pacote_enviado = ''
      self.total_pacotes_arquivo = ''

  def create_log(self):
    if self.tipo_msg == 3:
      log = f'{self.time} / {self.envio_ou_recebimento} / {self.tipo_msg} / {self.tamanho_total} / {self.id_pacote_enviado} / {self.total_pacotes_arquivo}'
    else:
      log = f'{self.time} / {self.envio_ou_recebimento} / {self.tipo_msg} / {self.tamanho_total}'
    return log

from datetime import datetime
from log import Log

class Logs():

  def __init__(self):
    self.logs = []

  def addLog(self, log):
    self.logs.append(log)

  def create_logs(self, client_ou_server: str, n_situacao: int):
    logs = open(f'logs/{client_ou_server}{n_situacao}.txt', 'w')
    for log in self.logs:
      logs.write('%s\n' % log)
    logs.close()
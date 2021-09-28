#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
import numpy as np
import time
from datagrama import Datagrama
from log import Log
from logs import Logs
from crc import CrcCalculator, Crc8

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM3"                 # Windows(variacao de)

# head -> h0 h1 h2 h3 h4 h5 h6 h7 h8 h9 (10 bytes fixos)
# h0 – tipo de mensagem
# h1 – id do sensor
# h2 – id do servidor
# h3 – número total de pacotes do arquivo
# h4 – número do pacote sendo enviado
# h5 – se tipo for handshake:id do arquivo
# h5 – se tipo for dados: tamanho do payload
# h6 – pacote solicitado para recomeço quando a erro no envio.
# h7 – último pacote recebido com sucesso.
# h8 – h9 – CRC
# PAYLOAD – variável entre 0 e 114 bytes. Reservado à transmissão dos arquivos.
# EOP – 4 bytes: 0xFF 0xAA 0xFF 0xA

def main():
    try:
        
        com = enlace(serialName)
        
        com.enable()

        com.fisica.flush()

        crc_calculator = CrcCalculator(Crc8.CCITT)

        print('Comunicação aberta')
        
        print('Início da recepção')

        comunicacao_ativa = True
        logs = Logs()
        while comunicacao_ativa:
        # esperando mensagem
            ocioso = True
            while ocioso:
                print('estou ocioso')
                head, nRx = com.getData(10, False)
                #print(f'head recebido: {head}')
                eop, nRx = com.getData(4, False)
                #print(f'eop recebido: {eop}')

                # << LOG >>
                msg = Datagrama(head=head)
                log_mensagem = Log(msg.format_datagrama(), 'receb')
                log_mensagem = log_mensagem.create_log()
                logs.addLog(log_mensagem)

                tipo_msg = head[0]
                print(f'Tipo da mensagem recebida: {tipo_msg}')
                if tipo_msg == 1:
                    id_servidor = head[2]
                    total_pacotes_arquivo = head[3]
                    print('mensagem t1 recebida!')
                    if id_servidor == 2:
                        print(f'ID servidor: {id_servidor} -> é para mim!')
                        print(f'Total de pacotes do arquivo: {total_pacotes_arquivo}')
                        ocioso = False
                        print('Handshake recebido!')
                        com.fisica.flush()
                        time.sleep(1)
            
            # na escuta
            msg_t2 = Datagrama()
            msg_t2.create_head(h0=b'\x02')
            com.sendData(msg_t2.format_datagrama())

            #<< LOG >>
            log_mensagem_t2 = Log(msg_t2.format_datagrama(), 'envio')
            log_mensagem_t2 = log_mensagem_t2.create_log()
            logs.addLog(log_mensagem_t2)

            print('Handshake respondido!')
            print(f'Mensagem t2 enviada: {msg_t2.format_datagrama()}')

            cont = 1
            id_ultimo_pacote_recebido = 0
            lista_payloads = []
            time_out = False
            print(f'Total de pacotes a serem recebidos: {total_pacotes_arquivo}')

            timer_02 = time.time()

            while cont <= total_pacotes_arquivo:
                head, nRx = com.getData(10)
                #print(f'head recebido: {head}')

                tipo_msg = head[0]
                #print(f'Tipo da mensagem recebida: {tipo_msg}')
                if tipo_msg == 3:
                    total_pacotes_arquivo_recebido = head[3]
                    print(f'Total de Pacotes do arquivo: {total_pacotes_arquivo_recebido}')
                    id_pacote = head[4]
                    print(f'ID do pacote: {id_pacote}')
                    payload_size = head[5]
                    print(f'Payload size: {payload_size}')
                    crc = head[8:10]
                    print(f'CRC: {crc}')
                    time.sleep(0.1)
                    payload, nRx = com.getData(payload_size)

                    checksum = crc_calculator.calculate_checksum(payload)
                    print(f'Checksum: {checksum}')

                    # << LOG >>
                    msg = Datagrama(head=head, payload=payload)
                    log_mensagem = Log(msg.format_datagrama(), 'receb')
                    log_mensagem = log_mensagem.create_log()
                    logs.addLog(log_mensagem)

                    time.sleep(0.1)
                    eop, nRx = com.getData(4)
                    #print(f'eop recebido: {eop}')
                    if (id_pacote == cont) and (eop == b'\xFF\xAA\xFF\xAA') and (checksum == int.from_bytes(crc, byteorder="big")):
                        id_ultimo_pacote_recebido = id_pacote
                        print(f'ID do pacote recebido: {id_pacote}')
                        #print(f'Payload do pacote recebido: {payload}')
                        msg_t4 = Datagrama()
                        msg_t4.create_head(h0=b'\x04', h7=id_ultimo_pacote_recebido.to_bytes(1, byteorder="big"))
                        com.sendData(msg_t4.format_datagrama())
                        print(f'Mensagem t4 enviada: {msg_t4.format_datagrama()}')

                        # << LOG >>
                        log_mensagem_t4 = Log(msg_t4.format_datagrama(), 'envio')
                        log_mensagem_t4 = log_mensagem_t4.create_log()
                        logs.addLog(log_mensagem_t4)
                        
                        lista_payloads.append(payload)
                        cont += 1
                    else:
                        print('Erro de mensagem t3 inválida!')
                        msg_t6 = Datagrama()
                        msg_t6.create_head(h0=b'\x06', h6=int.to_bytes(cont, 1, byteorder="big"))
                        com.sendData(msg_t6.format_datagrama())
                        print(f'Mensagem t6 enviada: {msg_t6.format_datagrama()}')

                        # << LOG >>
                        log_mensagem_t6 = Log(msg_t6.format_datagrama(), 'envio')
                        log_mensagem_t6 = log_mensagem_t6.create_log()
                        logs.addLog(log_mensagem_t6)
                else:
                    time.sleep(1)
                    if time.time() - timer_02 > 20:
                        ocioso = True
                        print('Time out!')
                        msg_t5 = Datagrama()
                        msg_t5.create_head(h0=b'\x05')
                        com.sendData(msg_t5.format_datagrama())
                        print(f'Mensagem t5 enviada: {msg_t5.format_datagrama()}')

                        # << LOG >>
                        log_mensagem_t5 = Log(msg_t5.format_datagrama(), 'envio')
                        log_mensagem_t5 = log_mensagem_t5.create_log()
                        logs.addLog(log_mensagem_t5)

                        comunicacao_ativa = False
                        time_out = True
                        # Encerra comunicação
                        print("-------------------------")
                        print("Comunicação encerrada")
                        print("-------------------------")
                        com.disable()
                        break
                    else:
                        if head == b'\x00':
                            print(f'Ultimo pacote recebido com sucesso: {id_ultimo_pacote_recebido}')
                            msg_t4 = Datagrama()
                            msg_t4.create_head(h0=b'\x04', h7=id_ultimo_pacote_recebido.to_bytes(1, byteorder="big"))
                            com.sendData(msg_t4.format_datagrama())
                            print(f'Mensagem t4 enviada: {msg_t4.format_datagrama()}')

                            # << LOG >>
                            log_mensagem_t4 = Log(msg_t4.format_datagrama(), 'envio')
                            log_mensagem_t4 = log_mensagem_t4.create_log()
                            logs.addLog(log_mensagem_t4)


            #logs.create_logs('Server', 5)

            if not time_out:                
                print('DADOS RECEBIDOS COM SUCESSO!')

                if len(lista_payloads) == total_pacotes_arquivo:

                    arquivo_final = int.to_bytes(0, 0, byteorder="big")
                    for payload in lista_payloads:
                        arquivo_final += payload

                    with open('img/apple.png', 'wb') as img:
                        img.write(arquivo_final)

                comunicacao_ativa = False

                print("-------------------------")
                print("Comunicação encerrada")
                print("-------------------------")
                com.disable()

    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()

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
import random
from datagrama import Datagrama 
from log import Log
from logs import Logs
from crc import CrcCalculator, Crc8

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

serialName = "COM4"

start_time = time.time()
def main():
    try:
        com = enlace(serialName)

        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com.enable()

        com.fisica.flush()

        crc_calculator = CrcCalculator(Crc8.CCITT)

        # Abrindo o arquivo de imagem e tranformando em binario
        with open("img/apple.png", "rb") as arch:
            file = arch.read()

        qtd_bytes = len(file)
        
        print(f"Quantidade de bytes da imagem  é {qtd_bytes}")

        # definindo o numero de pacotes
        total_pacotes = (qtd_bytes // 114)
        if qtd_bytes % 114 != 0:
            total_pacotes += 1
        
        # Criando a lista de payloads que contem os bytes da imagem
        lista_payloads = []
        for i in range(0,qtd_bytes, 114):
            try:
                payload = file[i:114+i]
            except:
                payload = file[i:]
            lista_payloads.append(payload)

        # Criando a lista de datagramas
        lista_pacotes = []
        i = 1
        for payload in lista_payloads:

            checksum = int.to_bytes(crc_calculator.calculate_checksum(payload), 2, byteorder="big")
            #print(f'Checksum: {checksum}')

            h0 = int.to_bytes(3,1, byteorder="big") # tipo de mensagem 
            h3 = int.to_bytes(total_pacotes,1, byteorder="big") # total de pacotes do arquivo 
            h4  = int.to_bytes(i,1, byteorder="big") # numero do pacote sendo enviado (id)
            i += 1
            h5 = int.to_bytes(len(payload),1, byteorder="big") # tipo do arquivo, no caso, DADOS, ou seja, aqui entra o tamanho do payload
            h8 = int.to_bytes(checksum[0], 1, byteorder="big")
            h9 = int.to_bytes(checksum[1], 1, byteorder="big")

            pacote = Datagrama()
            pacote.create_head(h0=h0, h3=h3, h4=h4, h5=h5, h8=h8, h9=h9)
            pacote.payload = payload
            
            lista_pacotes.append(pacote.format_datagrama())
        
        print(f'Temos uma lista de {total_pacotes} pacotes')
        
        # CONTADOR
        cont = 0

        logs = Logs()
        time_out = False
        inicia = True
        while inicia:
            # <<< QUERO FALAR COM VOCE >>>
            print('Início comunicação')
            msg_t1 = Datagrama()
            msg_t1.create_head(h0=b'\x01',h3=int.to_bytes(total_pacotes, 1, byteorder="big"))
            com.sendData(msg_t1.format_datagrama())

            # << LOG >>
            log_mensagem_t1 = Log(msg_t1.format_datagrama(), 'envio')
            log_mensagem_t1 = log_mensagem_t1.create_log()
            logs.addLog(log_mensagem_t1)

            print('Handshake enviado!')
            # print(f'Mensagem t1 enviada: {msg_t1.format_datagrama()}')

            msg_1_OK = False
            while not msg_1_OK:

                head, nRx = com.getData(10)
                #print(f'head recebido: {head}')
                eop, nRx = com.getData(4)

                # << LOG >>
                msg = Datagrama(head=head)
                log_mensagem = Log(msg.format_datagrama(), 'receb')
                log_mensagem = log_mensagem.create_log()
                logs.addLog(log_mensagem)

                tipo_msg = head[0]
                print(f'Tipo da mensagem recebida: {tipo_msg}')
                # <<< NA ESCUTA >>>
                if tipo_msg == 2:
                    print('Recebi a mensagem! Hadshake feito!')
                    msg_1_OK = True
                    cont += 1

                else:
                    com.sendData(msg_t1.format_datagrama())
                    # print(f'Mensagem t1 enviada: {msg_t1.format_datagrama()}')
                    print('Handshake enviado!')

                    # << LOG >>
                    log_mensagem_t1 = Log(msg_t1.format_datagrama(), 'envio')
                    log_mensagem_t1 = log_mensagem_t1.create_log()
                    logs.addLog(log_mensagem_t1)

                    time.sleep(5) #sleep 5 sec

            # Iniciando PROTOCOLO ENVIA PACOTE
            while cont <= total_pacotes:
                pacote_recebido = False
                # A numeração dos pacotes segue o index da lista - 1
                print(f'ENVIANDO O PACOTE NÚMERO {cont}')
                pacote = lista_pacotes[cont-1]
                com.sendData(pacote) # <<<PCKG>>>

                # << LOG >>
                log_mensagem_t3 = Log(pacote, 'envio')
                log_mensagem_t3 = log_mensagem_t3.create_log()
                logs.addLog(log_mensagem_t3)

                #print(f'Pacote enviado: {pacote}')
                timer_2 = time.time() # <<< SET TIMER 2 >>>
                
                while not pacote_recebido:
                    head, nRx = com.getData(10)
                    #print(f'head recebido: {head}')
                    eop, nRx = com.getData(4)

                    # << LOG >>
                    msg = Datagrama(head=head)
                    log_mensagem = Log(msg.format_datagrama(), 'receb')
                    log_mensagem = log_mensagem.create_log()
                    logs.addLog(log_mensagem)

                    tipo_msg = head[0]
                    print(f'Tipo da mensagem recebida: {tipo_msg}')
                    if tipo_msg == 4:
                        cont += 1
                        pacote_recebido = True
                    elif head == b'\x00':
                        print(f'passou 5 segundos, reenviando pacote {cont}')
                        com.sendData(pacote) # tentivo de reenvio 

                        # << LOG >>
                        log_mensagem_t3 = Log(pacote, 'envio')
                        log_mensagem_t3 = log_mensagem_t3.create_log()
                        logs.addLog(log_mensagem_t3)

                        #print(f'Pacote enviado: {pacote}')
                    # <<< PACOTE ERRADO >>>
                    elif tipo_msg == 6:
                        print('Erro no envio do pacote')
                        # corrigindo o contador e enviando o certo
                        cont = head[6]
                        print(f'ID do pacote esperado: {cont} -> reenviando...')
                        pacote_certo = lista_pacotes[cont - 1]
                        com.sendData(pacote_certo)

                        # << LOG >>
                        log_mensagem_t3 = Log(pacote_certo, 'envio')
                        log_mensagem_t3 = log_mensagem_t3.create_log()
                        logs.addLog(log_mensagem_t3)

                        #print(f'Pacote enviado: {pacote_certo}')
                        timer_2 = time.time() # <<< RESET TIMER 2 >>>
                    
                    # <<< TIME OUT >>>
                    if time.time() - timer_2 > 20:
                        msg_t5 = Datagrama()
                        msg_t5.create_head(h0=b'\x05')
                        # <<< ENVIA MSG T5 >>>
                        com.sendData(msg_t5.format_datagrama())
                        print('passou 20 segundos, desligando comunicação')
                        print(f'Mensagem t5 enviada!')

                        # << LOG >>
                        log_mensagem_t5 = Log(msg_t5.format_datagrama(), 'envio')
                        log_mensagem_t5 = log_mensagem_t5.create_log()
                        logs.addLog(log_mensagem_t5)

                        # Encerra comunicação
                        print("-------------------------")
                        print("Comunicação encerrada")
                        print("-------------------------")
                        com.disable()
                        inicia = False
                        time_out = True
                        break
                if time_out:
                    break

            #logs.create_logs('Client', 5)

            if not time_out:
                print('<<< ENVIO DOS PACOTES FINALIZADO!! >>>')

                inicia = False

                # Encerra comunicação
                print("-------------------------")
                print("Comunicação encerrada")
                print("-------------------------")
                print("--- %s seconds ---" % (time.time() - start_time))
                com.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()

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
from tqdm import tqdm

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

# ERRO: - Transmissão com erro na ordem dos pacotes enviados pelo client.
# Linha 79

serialName = "COM10"

start_time = time.time()
def main():
    try:
        com = enlace(serialName)

        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com.enable()

        com.fisica.flush()

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

            h0 = int.to_bytes(3,1, byteorder="big") # tipo de mensagem 
            h3 = int.to_bytes(total_pacotes,1, byteorder="big") # total de pacotes do arquivo 
            h4  = int.to_bytes(i,1, byteorder="big") # numero do pacote sendo enviado (id)
            i += 1
            h5 = int.to_bytes(len(payload),1, byteorder="big") # tipo do arquivo, no caso, DADOS, ou seja, aqui entra o tamanho do payload

            pacote = Datagrama()
            pacote.create_head(h0=h0, h3=h3, h4=h4, h5=h5)
            pacote.payload = payload
            
            lista_pacotes.append(pacote.format_datagrama())
        
        print(f'Temos uma lista de {total_pacotes} pacotes')
        
        # CONTADOR
        cont = 3 # (ERRO) AQUI O CONTADOR FOI INICIADO COM 3 PARA SIMULAR UM ERRO NO ENVIO DO PACOTE INICIAL
    
        inicia = True
        while inicia:
            # <<< QUERO FALAR COM VOCE >>>
            print('Início comunicação')
            msg_t1 = Datagrama()
            msg_t1.create_head(h0=b'\x01',h3=int.to_bytes(total_pacotes, 1, byteorder="big"))
            print('Handshake enviado!')
            print(f'Mensagem t1 enviada: {msg_t1.format_datagrama()}')

            msg_1_OK = False
            while not msg_1_OK:
                head, nRx = com.getData(10)
                print(f'head recebido: {head}')
                eop, nRx = com.getData(4)
                tipo_msg = head[0]
                print(f'Tipo da mensagem recebida: {tipo_msg}')
                # <<< NA ESCUTA >>>
                if tipo_msg == 2:
                    print('Recebi a mensagem! Hadshake feito!')
                    msg_1_OK = True
                    cont += 1
                else:
                    com.sendData(msg_t1.format_datagrama())
                    print(f'Mensagem t1 enviada: {msg_t1.format_datagrama()}')
                    time.sleep(5) #sleep 5 sec

            # Iniciando PROTOCOLO ENVIA PACOTE CARAMBA
            while cont <= total_pacotes:
                pacote_recebido = False
                # A numeração dos pacotes segue o index da lista - 1
                print(f'ENVIANDO O PACOTE NÚMERO {cont}')
                pacote = lista_pacotes[cont-1]
                com.sendData(pacote) # <<<PCKG>>>
                print(f'Pacote enviado: {pacote}')
                timer_2 = time.time() # <<< SET TIMER 2 >>>
                
                while not pacote_recebido:
                    head, nRx = com.getData(10)
                    print(f'head recebido: {head}')
                    eop, nRx = com.getData(4)
                    tipo_msg = head[0]
                    print(f'Tipo da mensagem recebida: {tipo_msg}')
                    if tipo_msg == 4:
                        cont += 1
                        pacote_recebido = True
                    elif head == b'\x00':
                        print(f'passou 5 segundos, reenviando pacote {cont}')
                        com.sendData(pacote) # tentivo de reenvio 
                        print(f'Pacote enviado: {pacote}')
                    # <<< PACOTE ERRADO >>>
                    elif tipo_msg == 6:
                        print('Erro no envio do pacote')
                        # corrigindo o contador e enviando o certo
                        cont = head[6]
                        print(f'ID do pacote esperado: {cont} -> reenviando...')
                        pacote_certo = pacote[cont - 1]
                        com.sendData(pacote_certo)
                        print(f'Pacote enviado: {pacote_certo}')
                        timer_2 = time.time() # <<< RESET TIMER 2 >>>
                    
                    # <<< TIME OUT >>>
                    if time.time() - timer_2 > 20:
                        msg_t5 = Datagrama()
                        msg_t5.create_head(h0=b'\x05')
                        # <<< ENVIA MSG T5 >>>
                        com.sendData(msg_t5.format_datagrama())
                        print('passou 20 segundos, desligando comunicação')
                        print(f'Mensagem t5 enviada: {msg_t5.format_datagrama()}')
                        # Encerra comunicação
                        print("-------------------------")
                        print("Comunicação encerrada")
                        print("-------------------------")
                        com.disable()

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

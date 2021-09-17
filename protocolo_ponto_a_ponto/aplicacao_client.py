#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from typing import ByteString
from enlace import *
import numpy as np
import random
from datagrama import Datagrama 
from tqdm import tqdm

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

serialName = "COM10"

start_time = time.time()

def main():
    try:
        com = enlace(serialName)

        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com.enable()

        # Abrindo o arquivo de imagem e tranformando em binario
        with open("img/PixelApple.png", "rb") as arch:
            file = arch.read()

        qtd_bytes = len(file)
        
        print(f"Quantidade de bytes da imagem  é {qtd_bytes}")

        # definindo o numero de pacotes
        total_pacotes = (qtd_bytes // 114)
        if qtd_bytes % 114 != 0:
            total_pacotes += 1

        print(f'Total necessários de pacotes: {total_pacotes}')
        
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
            id  = int.to_bytes(i,4, byteorder="big")
            i += 1
            total_pacote = int.to_bytes(total_pacotes,4, byteorder="big")
            size_payload = int.to_bytes(len(payload),2, byteorder="big")
            HEAD = id  + total_pacote + size_payload

            PAYLOAD = payload 
            EOP = b'\xFF\xAA\xFF\xAA'

            pacote = Datagrama(HEAD, PAYLOAD, EOP)
            lista_pacotes.append(pacote.send_format())
        
        print(f'Temos uma lista de {len(lista_payloads)} payloads')
        print(f'Temos uma lista de {len(lista_pacotes)} pacotes')

        handshake_head = int.to_bytes(0,10, byteorder="big")
        handshake_payload = bytes.fromhex("00")
        handshake_eop = int.to_bytes(0,4, byteorder="big")

        handshake = Datagrama(handshake_head, handshake_payload, handshake_eop)

        send_data = True
        while send_data:
            com.sendData(handshake.send_format())
            print("HANDSHAKE ENVIADO")
            send_data = False

            HANDSHAKE_CHECK = False
            while not HANDSHAKE_CHECK:
                rxBuffer, nRx = com.getData(15)
                time.sleep(0.01)
                if rxBuffer == int.to_bytes(0,5, byteorder="big") and nRx == 5:
                    print("Erro de timeout!!!")
                    resp = str(input("Servidor inativo, tentar novamente? [S/N]: "))
                    if resp == 'S':
                        send_data = True
                        break
                    elif resp == "N":
                        print("-------------------------")
                        print("Comunicação encerrada")
                        print("-------------------------")
                        com.disable()
                
                elif rxBuffer == int.to_bytes(0, 15, byteorder='big'):
                    print("SERVIDOR ESCUTANDO")
                    HANDSHAKE_CHECK = True

        # Iniciando PROTOCOLO ENVIA PACOTE CARAMBA
        envio_finalizado = False
        id_inicial = 10
        while not envio_finalizado: 
            for i in tqdm(range(id_inicial, len(lista_pacotes))):
                pacote = lista_pacotes[i]
                com.sendData(pacote)
                reiniciar_envio = False
                PROX_PACOTE = False
                while not PROX_PACOTE:
                    resp, _ = com.getData(16)
                    if resp[0:10] == int.to_bytes(1,10, byteorder="big") and i != len(lista_pacotes) - 1:
                        PROX_PACOTE = True
                    elif resp[0:10] == int.to_bytes(1,10, byteorder="big") and i == len(lista_pacotes) - 1:
                        PROX_PACOTE = True
                        envio_finalizado = True
                    elif resp[0:10] == int.to_bytes(2,10, byteorder="big"):
                        id_pacote = int.from_bytes(resp[10:12], byteorder='big')
                        indice = id_pacote - 1
                        id_inicial = indice
                        PROX_PACOTE = True
                        reiniciar_envio = True
                if reiniciar_envio == True:
                    break

        print('<<< ENVIO DOS PACOTES REALIZADO COM SUCESSO! >>>')

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

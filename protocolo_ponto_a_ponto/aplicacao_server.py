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

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM4"                  # Windows(variacao de)

# /x02 -> aviso de comando duplo
# /x03 -> aviso de final do
# /x04 -> ok

#head
#payload
#eop

def main():
    try:
        
        com = enlace(serialName)
        
        com.enable()

        com.fisica.flush()

        print('Comunicação aberta')
        
        print('Início da recepção')

        HANDSHAKE = False
        while not HANDSHAKE:
            handshake, nRx = com.getData(15)
            time.sleep(0.01)
            if handshake == int.to_bytes(0, 15, byteorder="big"):
                HANDSHAKE = True
                print('Server acordado!')
                print(handshake)

        handshake_head = handshake[:10]
        print(handshake_head)
        handshake_payload = handshake[11:12]
        print(handshake_payload)
        handshake_eop = handshake[11:]
        print(handshake_eop)

        handshake = Datagrama(head=handshake_head, payload=handshake_payload, eop=handshake_eop)
        
        com.sendData(handshake.send_datagrama())


        lista_payloads = []
        id_anterior = 0
        payload_size_anterior = 0
        ULTIMO_PACOTE = False
        while not ULTIMO_PACOTE:
            PACOTE_RECEBIDO = False
            while not PACOTE_RECEBIDO:
                pacote_head, nRx = com.getData(10)
                id_pacote = int.from_bytes(pacote_head[:4], byteorder="big")
                print(f'ID: {id_pacote}')
                total_pacotes = int.from_bytes(pacote_head[4:8], byteorder="big")
                print(f'Total de pacotes: {total_pacotes}')
                payload_size = int.from_bytes(pacote_head[8:], byteorder="big")
                print(f'Tamanho do payload: {payload_size}')
                pacote_payload, nRx = com.getData(payload_size)
                pacote_eop, nRx = com.getData(4)
                if (id_pacote == id_anterior + 1) and (id_pacote != total_pacotes) and (pacote_eop == b'\xFF\xAA\xFF\xAA'):
                    id_anterior += 1
                    lista_payloads.append(pacote_payload)
                    PACOTE_RECEBIDO = True
                    print('pacote recebido')
                elif id_pacote == total_pacotes:
                    lista_payloads.append(pacote_payload)
                    PACOTE_RECEBIDO = True
                    ULTIMO_PACOTE = True
                else:
                    print('pacote com id ou tamanho errado')
                    aviso_erro_head = int.to_bytes(2, 10, byteorder="big")
                    aviso_erro_payload = int.to_bytes(id_anterior+1, 2, byteorder="big")
                    aviso_erro_eop = int.to_bytes(0, 4, byteorder="big")
                    aviso_erro = Datagrama(head=aviso_erro_head, payload=aviso_erro_payload, eop=aviso_erro_eop)
                    com.sendData(aviso_erro.send_datagrama())
                    print(f'aviso de erro enviado: {aviso_erro.send_datagrama()}')


            aviso_ok_head = int.to_bytes(1, 10, byteorder="big")
            aviso_ok_payload = int.to_bytes(0, 2, byteorder="big")
            aviso_ok_eop = int.to_bytes(0, 4, byteorder="big")
            aviso_ok = Datagrama(head=aviso_ok_head, payload=aviso_ok_payload, eop=aviso_ok_eop)
            com.sendData(aviso_ok.send_datagrama())
            print(f'aviso ok enviado: {aviso_ok.send_datagrama()}')

        print(len(lista_payloads))

        payload_final = int.to_bytes(0, 0, byteorder="big")
        for payload in lista_payloads:
            payload_final += payload

        with open('img/apple.png', 'wb') as img:
            img.write(payload_final)


        # Encerra comunicação
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

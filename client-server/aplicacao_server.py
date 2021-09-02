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
#end

def main():
    try:
        
        com = enlace(serialName)
        
        com.enable()

        com.fisica.flush()

        print('Comunicação aberta')
        
        print('Início da recepção')

        HEAD_RECEBIDO = False
        while not HEAD_RECEBIDO:
            head, nRx = com.getData(1)
            time.sleep(0.01)
            if head:
                HEAD_RECEBIDO = True

        tamanho_bytes = int.from_bytes(head, "big")
        print(f'Tamanho recebido: {tamanho_bytes}')
        
        HEAD_OK = bytes.fromhex('04')
        com.sendData(HEAD_OK)
    
        BYTEARRAY_RECEBIDO = False
        while not BYTEARRAY_RECEBIDO:
            payload, nRx = com.getData(tamanho_bytes)
            time.sleep(0.01)
            if len(payload) == tamanho_bytes:
                BYTEARRAY_RECEBIDO = True

        print(f'BYTES RECEBIDOS: {payload}')

        #lógica para pegar o número de comandos enviados
        comandos = 0
        for byte in payload:
            if byte == 3:
                break
            elif byte == 2:
                comandos -= 1
            else:
                comandos += 1

        txBuffer = comandos.to_bytes(1, byteorder="big")
        print(f'Comandos recebidos: {txBuffer}')
        com.sendData(txBuffer)

        COMANDOS_CORRETOS = False
        CLIENT_OK = bytes.fromhex('01')
        while not COMANDOS_CORRETOS:
            rxBuffer, nRx = com.getData(1)
            if rxBuffer == CLIENT_OK:
                COMANDOS_CORRETOS = True

        print('Comandos corretos')
    
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

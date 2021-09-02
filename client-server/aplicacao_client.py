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

        com.fisica.flush()
        print('Comunicação aberta')
        
        commands = {
            'Comando 1' : bytes.fromhex("00FF"),
            'Comando 2' : bytes.fromhex("00"),
            'Comando 3' : bytes.fromhex("0F"),
            'Comando 4' : bytes.fromhex("F0"),
            'Comando 5' : bytes.fromhex("FF00"),
            'Comando 6' : bytes.fromhex("FF"), 
        }

        number_commands = random.randint(10,30)

        txBuffer = []
        for _ in range(number_commands):
            byte = random.choice(list(commands.values())) 
            if len(byte) > 1:
                txBuffer.append(bytes.fromhex("02"))
                txBuffer.append(byte)
            else:
                txBuffer.append(byte)
        txBuffer.append(bytes.fromhex("03"))
        txBuffer = b''.join(txBuffer)
        size = bytes([len(txBuffer)])

        print(f'Tamanho do txBuffer: {len(txBuffer)}')

        print('Início da transmissão')

        #Enviando os dados para o servidor
        com.sendData(size)

        first_check = False

        #Recebendo a primeira checagaem do servidor
        while not first_check:
            print("Enviando o tamanho dos comandos...")
            rxBuffer, _ = com.getData(1)
            time.sleep(0.01)
            # Se vier aa em byte, siginifica que o servidor recebeu o size 
            if rxBuffer == bytes.fromhex("04"):
                first_check = True
                print("SERVIDOR RECEBEU O TAMANHO DOS COMANDOS")

        if first_check:
            com.sendData(txBuffer)
            print("---BUFFER ENVIADO --->>>>")

        rxBuffer,_ = com.getData(1)

        size_check = int.from_bytes(rxBuffer, "big")

        if size_check == number_commands:
            txBuffer = bytes.fromhex("01")
            com.sendData(txBuffer)
            print("O NUMERO DE COMANDOS ESTÁ CORRETO!!!!!")
        else:
            print("!!!! ERROR !!!! --- HOUVE UMA FALHA DE COMUNICAÇÃO")

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

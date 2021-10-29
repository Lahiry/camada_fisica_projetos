#importe as bibliotecas
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from suaBibSignal import signalMeu


def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

#converte intensidade em Db, caso queiram ...
def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)

def main():
    print("Inicializando encoder")
    
    #declare um objeto da classe da sua biblioteca de apoio (cedida)
    signal = signalMeu()    

    #declare uma variavel com a frequencia de amostragem, sendo 44100
    fs = 44100
    
    #voce importou a bilioteca sounddevice como, por exemplo, sd. entao
    # os seguintes parametros devem ser setados:
    
    duration = 5 
      
    #relativo ao volume. Um ganho alto pode saturar sua placa... comece com .3    
    gainX  = 0.3
    gainY  = 0.3


    print("Gerando Tons base")
    
    #gere duas senoides para cada frequencia da tabela DTMF ! Canal x e canal y 
    #use para isso sua biblioteca (cedida)
    #obtenha o vetor tempo tb.
    #deixe tudo como array

    freqs = {
        '0' : [1336, 941],
        '1' : [1209, 697],
        '2' : [1336, 697],
        '3' : [1477, 697],
        '4' : [1209, 770],
        '5' : [1336, 770],
        '6' : [1447, 770],
        '7' : [1209, 852],
        '8' : [1336, 852],
        '9' : [1477, 852],
        'A' : [1633, 697],
        'B' : [1663, 770],
        'C' : [1663, 852],
        'D' : [1663, 941],
        'X' : [1209, 941],
        '#' : [1447, 941]
    }

    digito = input('Digite uma tecla: ')

    freq_x = freqs[digito][0]
    freq_y = freqs[digito][1]

    tempo, amplitude_x = signal.generateSin(freq_x, gainX, duration, fs)

    tempo, amplitude_y = signal.generateSin(freq_y, gainY, duration, fs)

    #printe a mensagem para o usuario teclar um numero de 0 a 9. 
    #nao aceite outro valor de entrada.
    print("Gerando Tom referente ao símbolo : {}".format(digito))
    print("Frequência do canal X : {}".format(freq_x))
    print("Frequência do canal Y : {}".format(freq_y))
    
    #construa o sunal a ser reproduzido. nao se esqueca de que é a soma das senoides

    tone = amplitude_x + amplitude_y
    
    #printe o grafico no tempo do sinal a ser reproduzido

    limits = [0, 0.01, -0.6, 0.6]

    plt.axis(limits)
    plt.plot(tempo, amplitude_x+amplitude_y)

    signal.plotFFT(tone, fs)

    # reproduz o som
    sd.play(tone, fs)
    # # Exibe gráficos
    plt.show()
    # # aguarda fim do audio
    sd.wait()

if __name__ == "__main__":
    main()

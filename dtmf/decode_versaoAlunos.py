#!/usr/bin/env python3
"""Show a text-mode spectrogram using live microphone data."""

#Importe todas as bibliotecas
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.fftpack import fft, fftshift
from suaBibSignal import signalMeu 
import sounddevice as sd
import time
import peakutils 


#funcao para transformas intensidade acustica em dB
def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)


def main():
 
    #declare um objeto da classe da sua biblioteca de apoio (cedida)
    signal = signalMeu()
      
    #declare uma variavel com a frequencia de amostragem, sendo 44100
    fs = 44100
    
    #voce importou a bilioteca sounddevice como, por exemplo, sd. entao
    # os seguintes parametros devem ser setados:
    
    sd.default.samplerate = fs #taxa de amostragem
    sd.default.channels = 2  #voce pode ter que alterar isso dependendo da sua placa
    duration = 4 #tempo em segundos que ira aquisitar o sinal acustico captado pelo mic


    # faca um printo na tela dizendo que a captacao comecará em n segundos. e entao 
    #use um time.sleep para a espera
    print('Captação de som iniciada...')
    time.sleep(1)
   
   #faca um print informando que a gravacao foi inicializada
    print('Gravação iniciada...')
   
   #declare uma variavel "duracao" com a duracao em segundos da gravacao. poucos segundos ... 
    duracao = duration
   #calcule o numero de amostras "numAmostras" que serao feitas (numero de aquisicoes) 
    numAmostras = fs * duracao
    freqDeAmostragem = fs
   
    audio = sd.rec(int(numAmostras), freqDeAmostragem, channels=1)
    sd.wait()
    print("...     FIM")
    
    #analise sua variavel "audio". pode ser um vetor com 1 ou 2 colunas, lista ...
    # print(audio)
    #grave uma variavel com apenas a parte que interessa (dados)
    

    # # use a funcao linspace e crie o vetor tempo. Um instante correspondente a cada amostra!
    # t = np.linspace(inicio,fim,numPontos)

    # # plot do gravico  áudio vs tempo!
   
    
    ## Calcula e exibe o Fourier do sinal audio. como saida tem-se a amplitude e as frequencias
    y = audio[:, 0]
    xf, yf = signal.calcFFT(y, fs)

    # #esta funcao analisa o fourier e encontra os picos
    # #voce deve aprender a usa-la. ha como ajustar a sensibilidade, ou seja, o que é um pico?
    # #voce deve tambem evitar que dois picos proximos sejam identificados, pois pequenas variacoes na
    # #frequencia do sinal podem gerar mais de um pico, e na verdade tempos apenas 1.
    index = peakutils.indexes(np.abs(yf),0.4,200)
    
    # #printe os picos encontrados! 
    picos = [xf[i] for i in index]
    print(picos)

    # #encontre na tabela duas frequencias proximas às frequencias de pico encontradas e descubra qual foi a tecla
    # #print a tecla.
    linha = [697, 770, 852, 941]
    coluna = [1209, 1336, 1477, 1633]
    keypad = [[1,2,3,'A'],[4,5,6,'B'],[7,8,9,'C'],['X',0,'#','D']]
    x, y = 0, 0

    for pico in picos:
        for i in range(len(linha)):
            if linha[i] - 1 <= pico <= linha[i] + 1:
                y = i
        for j in range(len(coluna)):
            if coluna[j] - 1 <= pico <= coluna[j] + 1:
                x = j

    digito = keypad[y][x]
    print(f'O dígito é {digito}')
    print(y,x)
  
    # ## Exibe gráficos
    plt.figure("F(y)")
    plt.plot(xf,yf)
    plt.grid()
    plt.title('Fourier audio')
    plt.show()

if _name_ == "_main_":
    main()
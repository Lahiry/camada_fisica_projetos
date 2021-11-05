#!/usr/bin/env python3
"""Show a text-mode spectrogram using live microphone data."""

#Importe todas as bibliotecas
import matplotlib.pyplot as plt
import numpy as np
from scipy.fftpack import fft, fftshift
from suaBibSignal import signalMeu 
import sounddevice as sd
import time
import peakutils 
from funcoes_LPF import LPF
from math import *
import soundfile as sf


#funcao para transformas intensidade acustica em dB
def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)


def main():
    meuSinal = signalMeu()
    fs = 44100
    sd.default.samplerate = fs #taxa de amostragem
    sd.default.channels = 2  #voce pode ter que alterar isso dependendo da sua placa
    duration = 5 #tempo em segundos que ira aquisitar o sinal acustico captado pelo mic
   
    numAmostras = fs * duration
    freqDeAmostragem = fs
   
    audio, fs = sf.read("audio_modulado.wav", dtype = "float32")  
    print('Reproduzindo sinal...')
    sd.play(audio)
    status = sd.wait()
    print("...     FIM")
    

    # Demodulação
    print('Realizando a demodulação')
    fc = 14e3
    pontos, demodulador = meuSinal.generateSin(fc, 1, duration, fs)
    sinal_demodulado = audio * demodulador

    #Fourier no sina demodulado 
    xf, yf = meuSinal.calcFFT(sinal_demodulado, fs)

    # Filtro passa baixa
    freq_corte = 4e3
    sinalLPF = LPF(sinal_demodulado, freq_corte, fs)

    # Fourier no sinal demodulado e filtrado
    xmf, ymf = meuSinal.calcFFT(sinalLPF, fs)


    print('Reproduzindo o som...')
    sd.play(sinalLPF)
    status = sd.wait()

    print('TERMINO DO PROGRAMA!')
  
    # ## Exibe gráficos
    plt.figure('F(y)')
    plt.plot(xf, yf)
    plt.grid()
    plt.title('Fourier audio')
    plt.show()

    plt.plot(xmf, ymf)
    plt.grid()
    plt.title('Fourier audio demoduldo')
    plt.show()

if __name__ == "__main__":
    main()

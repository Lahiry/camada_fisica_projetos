import sounddevice as sd
import soundfile as sf
from scipy.io.wavfile import write
import matplotlib.pyplot as plt
from funcoes_LPF import LPF
from suaBibSignal import signalMeu
import time

fs = 44100
seconds = 5

# print('Gravando...')

# recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
# sd.wait()
# write('audio.wav', fs, recording)

# print('Gravação salva!')

data, fs = sf.read('audio.wav', dtype='float32')  
print('Reproduzindo sinal...')
sd.play(data)
status = sd.wait()

meuSinal = signalMeu()

max_value = abs(data).max()

print(max_value)

data_normalizada = data/max_value

lpf = LPF(data_normalizada, 4000, fs)
# print('Reproduzindo sinal filtrado...')
# sd.play(lpf)
# status = sd.wait()

xlpff, ylpff = meuSinal.calcFFT(lpf, fs)

fc = 14e3
pontos, modulador = meuSinal.generateSin(fc, 1, seconds, fs)

sinalModulado = lpf * modulador

print('Reproduzindo sinal modulado...')
sd.play(sinalModulado)
status = sd.wait()

sf.write('audio_modulado.wav', sinalModulado, fs)

#fourier

xmf, ymf = meuSinal.calcFFT(sinalModulado, fs)


plt.plot(data_normalizada)
plt.show()

plt.plot(lpf)
plt.show()

plt.plot(xlpff, ylpff)
plt.show()

plt.plot(sinalModulado)
plt.show()

plt.plot(xmf, ymf)
plt.show()

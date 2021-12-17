from __future__ import division
from os import listdir
from os.path import isfile, join, splitext
from pylab import *
import soundfile as sf

maleFemaleFreq = [120, 232]

M_MinMax = [55, 155]
K_MinMax = [175, 270]
HPSLoop = 6


def who(result, MinMax):
    return sum(result[MinMax[0]:MinMax[1]])


def HPS(s):
    T = 3  # time for HPS method
    rate = s['sampleRate']
    signal = s['signal']

    if (T > len(signal) / rate): T = len(signal) / rate
    signal = signal[max(0, int(len(signal) / 2) - int(T / 2 * rate)):min(len(signal) - 1,
                                                                         int(len(signal) / 2) + int(
                                                                             T / 2 * rate))]
    partLen = int(rate)
    parts = [signal[i * partLen:(i + 1) * partLen] for i in range(int(T))]
    resultParts = []
    for data in parts:
        if (len(data) == 0): continue
        window = np.hamming(len(data))
        data = data * window
        fftV = abs(fft(data)) / rate
        fftR = copy(fftV)
        for i in range(2, HPSLoop):
            tab = copy(fftV[::i])
            fftR = fftR[:len(tab)]
            fftR *= tab
        resultParts.append(fftR)
    result = [0] * len(resultParts[int(len(resultParts) / 2)])
    for res in resultParts:
        if (len(res) != len(result)): continue
        result += res

    if (who(result, M_MinMax) > who(result, K_MinMax)): return 'M'
    return 'K'


def loadfiles(path):
    files = [f for f in listdir(path) if isfile(join(path, f)) and splitext(f)[1] == ".wav"]
    print(files)
    samples = []
    maleCount = 0
    femaleCount = 0
    for fil in files:
        p = path + '/' + fil

        data, rate = sf.read(p)

        sig = [mean(d) for d in data]
        samples.append({'name': fil, 'nameGender': fil[-5:-4], 'signal': sig, 'sampleRate': rate})

        if fil[-5:-4] == "M":
            maleCount += 1
        else:
            femaleCount += 1

    counters = {"maleCount": maleCount, "femaleCount": femaleCount}
    return samples, counters


def launchAlgorithm(samples, counters):
    recognizedMale = 0
    recognizedFemale = 0
    wellRecognized = 0

    for s in samples:
        gender = HPS(s)

        if gender == s['nameGender']:
            wellRecognized += 1

            if gender == "M":
                recognizedMale += 1
            elif gender == "K":
                recognizedFemale += 1
            else:
                print("Algorithm returned wrong value: ", s['name'])

    samplesCount = counters['maleCount'] + counters['femaleCount']
    print("Statystyka:")
    print("Liczba prawidłowo rozpoznanych Mężczyzn: ", recognizedMale, "/", counters['maleCount'])
    print("Liczba prawidłowo rozpoznanych Kobiet: ", recognizedFemale, "/", counters['femaleCount'])
    print("Zgodność: ", wellRecognized, "/", samplesCount, " (", wellRecognized / samplesCount * 100, "%)")


if __name__ == '__main__':
    samples, counters = loadfiles("train")
    # print(samples)
    # print(counters)
    launchAlgorithm(samples, counters)

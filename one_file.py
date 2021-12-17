from __future__ import division
from os.path import isfile, join, splitext
from pylab import *
import soundfile as sf
import sys

maleFemaleFreq = [120, 232]
TS = 3  # time for simple method
M_MinMax = [55, 155]
K_MinMax = [175, 270]
HPSLoop = 6


def who(result, MinMax):
    return sum(result[MinMax[0]:MinMax[1]])


def HPS(s):
    T = 3  # time for HPS method
    rate = s['sampleRate']
    dataVoice = s['signal']

    if (T > len(dataVoice) / rate): T = len(dataVoice) / rate
    dataVoice = dataVoice[max(0, int(len(dataVoice) / 2) - int(T / 2 * rate)):min(len(dataVoice) - 1,
                                                                                  int(len(dataVoice) / 2) + int(
                                                                                      T / 2 * rate))]
    partLen = int(rate)
    parts = [dataVoice[i * partLen:(i + 1) * partLen] for i in range(int(T))]
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

    if (who(result, maleMinMax) > who(result, femaleMinMax)): return 'M'
    return 'K'


def loadfiles(new_file):
    samples = []
    maleCount = 0
    femaleCount = 0
    data, rate = sf.read(new_file)
    sig = [mean(d) for d in data]
    samples.append({'name': new_file, 'nameGender': new_file[-5:-4], 'signal': sig, 'sampleRate': rate})

    if new_file[-5:-4] == "M":
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
        print(gender)
        if gender == s['nameGender']:
            wellRecognized += 1

            if gender == "M":
                recognizedMale += 1
            elif gender == "K":
                recognizedFemale += 1
            else:
                print("Algorithm returned wrong value: ", s['name'])


if __name__ == '__main__':
    samples, counters = loadfiles(sys.argv[1])
    # print(samples)
    # print(counters)
    launchAlgorithm(samples, counters)

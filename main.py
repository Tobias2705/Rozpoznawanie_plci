from __future__ import division

from os import listdir
from os.path import isfile, join, splitext

from pylab import *
import soundfile as sf

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


def recognizeGender(sample):
    t = 3
    w = sample['sampleRate']
    n = w * t  # t*w
    signal = sample['signal']
    nframe = len(signal)
    if n > nframe:
        n = nframe
    frequency = linspace(0, w, n)
    spectrum = fft(signal[0:n])
    spectrum = abs(spectrum)
    amp, freq = [], []
    for i in range(len(frequency)):
        if 85 < frequency[i] < 255:
            freq.append(frequency[i])
            amp.append(spectrum[i])
    index = amp.index(max(amp))
    avg_freq = freq[index]
    if avg_freq < 175:
        return 'M'
    else:
        return 'K'


def launchAlgorithm(samples, counters):
    recognizedMale = 0
    recognizedFemale = 0
    wellRecognized = 0

    for s in samples:
        gender = recognizeGender(s)

        if gender == s['nameGender']:
            wellRecognized += 1

            if gender == "M":
                recognizedMale += 1
            elif gender == "K":
                recognizedFemale += 1
            else:
                print("Algorithm returned wrong value: ", s['name'])

    samplesCount = counters['maleCount'] + counters['femaleCount']
    print("Statistics...")
    print("Well recognized Male: ", recognizedMale, "/", counters['maleCount'])
    print("Well recognized Female: ", recognizedFemale, "/", counters['femaleCount'])
    print("Total: ", wellRecognized, "/", samplesCount, " (", wellRecognized / samplesCount * 100, "%)")


if __name__ == '__main__':
    samples, counters = loadfiles("train")
    # print(samples)
    # print(counters)
    launchAlgorithm(samples, counters)

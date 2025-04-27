import os
import sys
import time
import scipy
import pickle
import inquirer
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
sys.path.append('./Libraries')
from measurementClass import Measurement                # type: ignore
import noiseToolBox
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from koheron import connect, command
import pyvisa as visa

class Rigol_DG5252Pro():


    def __init__(self):

        self.visa_dll = 'c:/windows/system32/visa32.dll'
        self.rm = visa.ResourceManager()
        self.ip='192.168.1.24'
        self.resource='TCPIP0::192.168.1.24::inst0::INSTR'.format(self.ip)
        self.inst = self.rm.open_resource(self.resource)
        self.inst.read_termination = '\n'
        self.inst.write_termination = '\n'
        self.identity={}

    def write(self, command):

        self.inst.write(command)

    def connect(self):

        if self.inst=={}:
            a=input('please write an instance:')
            self.inst=self.rm.open_resource(a)
            output = self.query("*IDN?")[:-1].split(',')
            self.identity = {'name': output[0], 'model': output[1], 'SN': output[2]}
            return self.identity
        else:
            output = self.query("*IDN?")[:-1].split(',')
            self.identity = {'name': output[0], 'model': output[1], 'SN': output[2]}
            return self.identity

    def query(self,command):

        output = self.inst.query(command)
        print(output)
        return output

class PhaseNoiseAnalyzer(object):
    def __init__(self, client):
        self.client = client

    @command(classname="Dds")
    def set_dds_freq(self, channel, freq):
        pass

    @command()
    def get_data(self):
        return self.client.recv_array(200000, dtype='int32')

    @command()
    def set_cic_rate(self, rate):
        self.fs = 200E6 / (2.0 * rate)

    @command()
    def get_parameters(self):
        return self.client.recv_tuple('If')


# 初始化
freq = 80E6  # Modulation frequency (Hz)
tau = 89E-9  # Interferometer delay (s)

host = os.getenv('HOST', '192.168.1.22')
driver = PhaseNoiseAnalyzer(connect(host, 'phase-noise-analyzer_v0.2.1'))
driver.set_dds_freq(0, freq)

n=200000
fs=200E6

# CIC 比率列表
cic_rate=1  # 可以添加您需要的其他 CIC 比率
driver.set_cic_rate(cic_rate)

powers=[1,0.8,0.5,0.2]
colors = ['b', 'g', 'r','y']  # 每条曲线的颜色
fs = fs / (cic_rate * 2)
n_avg = 10

plt.figure(figsize=(10, 6))  # 创建图形

AWG = Rigol_DG5252Pro()
AWG.write(":OUTPUt1:STATe ON")
for index, cic_rate in enumerate(powers):
    f = np.arange((n / 2 + 1)) * fs / n
    window = np.ones(n)
    psd = np.zeros(int(n / 2) + 1)

    AWG.write(":SOURce1:APPLy:SINusoid 80M,%s,0,0 "%str(powers[index]))
    print(powers[index])
    time.sleep(5)

    for i in range(n_avg):
        print(i)
        print("Acquiring sample {}/{}".format(i + 1, n_avg))
        data = driver.get_data()

        data = data - np.mean(data)
        calib_factor = 4.196
        data *= calib_factor * np.pi / 8192.0  # rad
        psd += 2.0 * np.abs(np.fft.rfft(window * data)) ** 2

    psd /= n_avg
    psd /= (fs * np.sum(window ** 2))  # rad^2/Hz
    psd_dB = 10.0 * np.log10(psd)  # Convert to dBc/Hz
    # psd_dB -= 20.0 * np.log10(2.0 * np.sin(np.pi * (f + 1) * tau))  # Interferometer transfer function

    psd_dB = psd_dB - 20 * np.log10(f + 1)  # Transfer to frequency psd


    # 绘制当前 cic_rate 的 PSD
    ax = plt.subplot(111)
    ax.semilogx(f, psd_dB, linewidth=1, marker='o', markersize=3, markevery=10,
                label=f'Power {powers[index]} Vpp', color=colors[index])

AWG.write(":OUTPUt1:STATe OFF")
ax.set_xlabel("FREQUENCY (Hz)")
ax.set_ylabel("SSB FREQUENCY NOISE (Hz^2/Hz)")
ax.grid(True, which='major', linestyle='-', linewidth=1.5, color='0.35')
ax.grid(True, which='minor', linestyle='-', color='0.35')

# 添加图例
ax.legend()
plt.show()
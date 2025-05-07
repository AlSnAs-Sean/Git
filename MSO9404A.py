import tkinter as tk
import tkinter.ttk as ttk
import pyvisa as visa

class MSO9404A():


    def __init__(self):

        self.visa_dll = 'c:/windows/system32/visa32.dll'
        self.rm = visa.ResourceManager()
        self.ip='192.168.1.25'
        self.resource='TCPIP::192.168.1.25::INSTR'.format(self.ip)
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

OSA=MSO9404A()
OSA.write(":SINGle")
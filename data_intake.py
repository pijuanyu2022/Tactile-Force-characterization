import warnings
import time

import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Queue
import serial
import re


import clr
import sys
from System import *
import System

sys.path.insert(1,"C:\Program Files (x86)\HBM\QuantumX API 4\DLLs")

# import HBM Common API 
clr.AddReference("HBM.QuantumX")
from HBM.QuantumX import QXSystem
from HBM.QuantumX import QXSimpleDAQ
from HBM.QuantumX import eDAQValueState
from HBM.DeviceComponents import eConnectorTypes


class Tactile_Control:
    def __init__(self, stream_rate=100):
        self.serialPort = serial.Serial(port = "COM6", baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
        self.intended_stream_rate = 1 / stream_rate
        self.prev_time = time.perf_counter()

    def read_samples(self):
        serialString = ""

        # Read data out of the buffer until a carraige return / new line is found
        serialString = self.serialPort.readline()
        pressure_value = serialString.decode('Ascii')


        data = re.findall(r"\d+\.?\d*",pressure_value)


        if data:
            data = str(data[0])
            # pressure_data = float(data[0][:9])
            # solenoid_value = int(data[0][9])

        samples = [[data]]

        next_time = time.perf_counter()
        time_delta = (time.perf_counter() - self.prev_time) / len(samples[0])
        
        samples.append(
            [self.prev_time + (time_delta * i) for i in range(len(samples[0]))]
        )

        transposed = [[C[i] for C in samples] for i in range(len(samples[0]))]

        self.prev_time = next_time

        return transposed
    
    def write_actuator(self, number):
        # the number will be input to the PIC microcontroller
        number = str(number)
        self.serialPort.write(number.encode('utf-8'))
    
    def safe_exit(self, QX_IPadd):
        self.serialPort.close()
        QXSimpleDAQ.StopDAQ()
        QXSystem.Disconnect(QX_IPadd)
        print("Closed DAQ")

    def HBM_Scan(self):
        result = QXSystem.ScanForQXDevices()
        if result: 
            result_str = ''
            result_str = str(result[0])
            name = result_str[:29]
            QX_IPadd = result_str[29:result_str.index(':')]
            # print("Found the decie: " + name + ". The IP adress: " + QX_IPadd)
        else:
            print("Did not find any useful device")
            return False
        return QX_IPadd  


def main():
    tactile_control = Tactile_Control()

    sample_cache = []

    prev_time = time.perf_counter()

    delete_first_data = 0

    # hbm_cache = []
    UUID = QXSystem.Connect("169.254.39.205")

    running = True
    is_PCB = False

    while running:
        Hbm_data = list(QXSimpleDAQ.GetSingleShot(UInt64(UUID), Boolean(False), None, None)[1])
        print(Hbm_data)
        if len(Hbm_data) > 0:
            is_PCB = True
            break


    while is_PCB:
        print("what the hell?")
        if(tactile_control.serialPort.in_waiting > 0):
            tactile_control.write_actuator(16000)
            # QX_IPadd = tactile_control.HBM_Scan()
            # UUID = QXSystem.Connect(QX_IPadd)
            samples = tactile_control.read_samples()
            
            delete_first_data += 1
            if delete_first_data >= 2:
                # print(samples)
                # print(samples[0][0][:9])
                # print(samples[0][0][9])
                samples[0].insert(0, int(samples[0][0][9]))
                samples[0][1] = float(samples[0][1])

                Hbm_data = list(QXSimpleDAQ.GetSingleShot(UInt64(UUID), Boolean(False), None, None)[1])

                Fz = (Hbm_data[0]+Hbm_data[1])/2
                Fy = (Hbm_data[2]+Hbm_data[3])/2
                Fx = (Hbm_data[4]+Hbm_data[5])/2


                Mz = (Hbm_data[6]+Hbm_data[7])/2
                My = (Hbm_data[8]+Hbm_data[9])/2
                Mx = (Hbm_data[10]+Hbm_data[11])/2

                samples[0].insert(0, Fz)
                samples[0].insert(1, Fy)
                samples[0].insert(2, Fx)

                samples[0].insert(3, Mz)
                samples[0].insert(4, My)
                samples[0].insert(5, Mx)

                print(samples)
               


if __name__ == "__main__":
    main()


def data_sender(
    sample_delay, send_queue: Queue = None, communication_queue: Queue = None
):
    tactile_control = Tactile_Control()

    running = True

    sample_cache = []

    prev_time = time.perf_counter()

    delete_first_data = 0

    i = 0
    sum_data = 0

    hbm_cache = []
    QX_IPadd = tactile_control.HBM_Scan()
    UUID = QXSystem.Connect(QX_IPadd)

    while running:
        if(tactile_control.serialPort.in_waiting > 0):
            samples = tactile_control.read_samples()
            
            delete_first_data += 1
            if delete_first_data >= 2:
                samples[0].insert(0, int(samples[0][0][9]))
                samples[0][1] = float(samples[0][1])
            

                Hbm_data = list(QXSimpleDAQ.GetSingleShot(UInt64(UUID), Boolean(False), None, None)[1])

                Fz = (Hbm_data[0]+Hbm_data[1])/2
                Fy = (Hbm_data[2]+Hbm_data[3])/2
                Fx = (Hbm_data[4]+Hbm_data[5])/2


                Mz = (Hbm_data[6]+Hbm_data[7])/2
                My = (Hbm_data[8]+Hbm_data[9])/2
                Mx = (Hbm_data[10]+Hbm_data[11])/2

                samples[0].insert(0, Fz)
                samples[0].insert(1, Fy)
                samples[0].insert(2, Fx)

                samples[0].insert(3, Mz)
                samples[0].insert(4, My)
                samples[0].insert(5, Mx)
                    
                sample_cache.extend(samples)
                prev_time += sample_delay

                if not send_queue.full() and sample_cache:
                    send_queue.put_nowait(sample_cache)
                    sample_cache = []

                while not communication_queue.empty():
                    val = communication_queue.get_nowait()

                    tactile_control.write_actuator(val)

                    if val == "EXIT":
                        tactile_control.safe_exit()
                        running = False

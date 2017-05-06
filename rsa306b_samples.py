# Author:
# Raghav Thanigaivel
# Aim: 
# Code to read samples from Tektronix RSA 306B and store it in a series of continuous txt files
# Requirements: 
# Necessary libraries, Tektronix RSA 306B API and storage space; 
# Written in Python 3.4.3 and tested for Windows OS;
# The folder in which the script is run should not contain any other txt file except the script;
# If other txt files are present, there is a possibility of overwriting of data;

#importing libraries
try:
    import time
except ImportError:
    print("time library not found. Please install and try again!")
    
try:
    from ctypes import *
except ImportError:
    print("ctypes library not found. Please install and try again!")
    time.sleep(5)
    exit()

try:
    import numpy as np
except ImportError:
    print("numpy library not found. Please install and try again!")
    time.sleep(5)
    exit()

try:
    import os
except ImportError:
    print("os library not found. Please install and try again!")
    time.sleep(5)
    exit()

try:
    import sys
except ImportError:
    print("sys library not found. Please install and try again!")
    time.sleep(5)
    exit()

try:
    import datetime
except ImportError:
    print("datetime library not found. Please install and try again!")
    time.sleep(5)
    exit()

working_directory = os.getcwd()
lasttxtval = 0

os.chdir("C:\\Tektronix\\RSA_API\\lib\\x86")
rsa = cdll.LoadLibrary("RSA_API.dll")

"""#################CLASSES AND FUNCTIONS#################"""
#create Spectrum_Settings data structure
class Spectrum_Settings(Structure):
    _fields_ = [('span', c_double), 
    ('rbw', c_double),
    ('enableVBW', c_bool), 
    ('vbw', c_double),
    ('traceLength', c_int), 
    ('window', c_int),
    ('verticalUnit', c_int), 
    ('actualStartFreq', c_double), 
    ('actualStopFreq', c_double),
    ('actualFreqStepSize', c_double), 
    ('actualRBW', c_double),
    ('actualVBW', c_double), 
    ('actualNumIQSamples', c_double)]

#create Spectrum_TraceInfo data structure
class Spectrum_TraceInfo(Structure):
    _fields_ = [('timestamp', c_int64), ('acqDataStatus', c_uint16)]
    
def search_connect():
    #search/connect variables
    numFound = c_int(0)
    intArray = c_int*10
    deviceIDs = intArray()
    deviceSerial = create_string_buffer(8)
    deviceType = create_string_buffer(8)
    apiVersion = create_string_buffer(16)

    #get API version
    rsa.DEVICE_GetAPIVersion(apiVersion)
    print('API Version {}'.format(apiVersion.value.decode()))

    #search and connect to devices
    ret = rsa.DEVICE_Search(byref(numFound),deviceIDs,deviceSerial, deviceType)

    if ret != 0:
        print('Error in Search: ' + str(ret))
        exit()
    if numFound.value < 1:
        print('No instruments found. Exiting script.')
        exit()
    elif numFound.value == 1:
        print('One device found.')
        print('Device type: {}'.format(deviceType.value.decode()))
        print('Device serial number: {}'.format(deviceSerial.value.decode()))
        ret = rsa.DEVICE_Connect(deviceIDs[0])
        if ret != 0:
            print('Error in Connect: ' + str(ret))
            exit()
        
    else:
        print('2 or more instruments found. Enumerating instruments, please wait.')
        for inst in range(numFound.value):
            rsa.DEVICE_Connect(deviceIDs[inst])
            rsa.DEVICE_GetSerialNumber(deviceSerial)
            rsa.DEVICE_GetNomenclature(deviceType)
            print('Device {}'.format(inst))
            print('Device Type: {}'.format(deviceType.value))
            print('Device serial number: {}'.format(deviceSerial.value))
            rsa.DEVICE_Disconnect()
        #note: the API can only currently access one at a time
        selection = 1024
        while (selection > numFound.value-1) or (selection < 0):
            selection = int(input('Select device between 0 and {}\n> '.format(numFound.value-1)))
        rsa.DEVICE_Connect(deviceIDs[selection])
        return selection


def getData(center_freq,span,rbw):
    """#################INITIALIZE VARIABLES#################"""
    #main SA parameters
    specSet = Spectrum_Settings()
    enable = c_bool(True)         #spectrum enable
    cf = c_double(center_freq)    #center freq
    refLevel = c_double(-20)      #ref level in dBm
    ready = c_bool(False)         #ready
    timeoutMsec = c_int(100)      #timeout
    traceval = c_int(2)              #trace: 0 Positive Peak, 1 Negative Peak, 2 Average 
    detectorval = c_int(3)           #detector: 0 Positive Peak, 1 Negative Peak, 2 Average VRMS, 3 Sample 
    traceInfo = Spectrum_TraceInfo()
     
    """#################CONFIGURE INSTRUMENT#################"""
    rsa.CONFIG_Preset()
    rsa.CONFIG_SetCenterFreq(cf)
    rsa.CONFIG_SetReferenceLevel(refLevel)
    rsa.SPECTRUM_SetEnable(enable)
    rsa.SPECTRUM_SetDefault()
    rsa.SPECTRUM_SetTraceType(traceval,True,detectorval)
    rsa.SPECTRUM_GetSettings(byref(specSet))
     
     
    specSet.span = c_double(span)
    specSet.rbw = c_double(rbw)
    specSet.traceLength = c_int(4001)
    #specSet.enableVBW = c_bool(True)
    #specSet.vbw = c_double(vbw)
    #specSet.verticalUnit = c_long(10)
     
    #set desired spectrum settings
    rsa.SPECTRUM_SetSettings(specSet)
    rsa.SPECTRUM_GetSettings(byref(specSet))
     
    """#################INITIALIZE DATA TRANSFER VARIABLES#################"""
    #initialize variables for GetTrace
    traceArray = c_float * specSet.traceLength
    traceData = traceArray()
    outTracePoints = c_int()
     
    #generate frequency array
    freq = np.arange(specSet.actualStartFreq,specSet.actualStartFreq+specSet.actualFreqStepSize*specSet.traceLength,specSet.actualFreqStepSize)
     
    """#################ACQUIRE/PROCESS DATA#################"""
    #start acquisition
    rsa.DEVICE_Run()
    rsa.SPECTRUM_AcquireTrace()
    while ready.value == False:
        rsa.SPECTRUM_WaitForDataReady(timeoutMsec, byref(ready))
    rsa.SPECTRUM_GetTrace(traceval,specSet.traceLength,byref(traceData),byref(outTracePoints))
    rsa.SPECTRUM_GetTraceInfo(byref(traceInfo))
    rsa.DEVICE_Stop()
     
    #convert trace data from a ctypes array to a numpy array
    trace = np.ctypeslib.as_array(traceData)
    return (trace,freq,traceData)




def main():
    """#################SEARCH/CONNECT#################"""
    search_connect()
    
    start_frequency = 698000000 #Start frequency: 698 MHz
    span_bandwidth = 40000000 #Span bandwidth: 40 MHz
    resolution_bandwidth = 10000 #Resolution bandwidth: 10 KHz
    stop_frequency = 818000000 #Stop frequency: 818 MHz
    
    outputfilectr = lasttxtval + 1
    
    while True:
        #Spectrum Analyzer acquisition
        print("File written to memory: "+ outputfilectr)
        output_file = open(working_directory+'\output'+str(outputfilectr)+'.txt','w')
        
        spanctr = 1
        while True:
            #Setting up variables for the loops
            center_freq_input = start_frequency+(span_bandwidth/2)
            span_input = span_bandwidth
            rbw_input = resolution_bandwidth
            
            try:
                #Acquiring data from the sensor and writing it to a txt file with timestamp
                center_freq_run = center_freq_input + (span_input * (spanctr-1))
                (trace_main,freq_main,traceData) = getData(int(center_freq_run),int(span_input),int(rbw_input))
                output_file.write("Frequency|Power(dBm) for timestamp:"+str(datetime.datetime.now())+"\n")
                i=0
                while i<len(traceData):
                    output_file.write(str(freq_main[i])+"|"+str(traceData[i])+"\n")
                    i=i+1
                
                if center_freq_run >= (stop_frequency-span_input):
                    break           
                spanctr = spanctr + 1
            except:
                print(sys.exc_info())
    
    
        output_file.close()
        outputfilectr = outputfilectr + 1
    
    print('Disconnecting.')
    rsa.DEVICE_Disconnect()
    
if __name__ == "__main__":
    main()
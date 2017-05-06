# Author:
# Raghav Thanigaivel
# Aim: 
# Code to read series of output txt files of rsa306b_samples.py; 
# Code to calculate mean, standard deviation and peak from the data read from txt files
# Requirements: 
# Necessary libraries and storage space; 
# Written in Python 3.4.3 and tested for Windows OS;
# The script should be run in the same location as that of the txt files;
# The script outputs msp.csv file whose first column is frequency in Hz, second column is mean power in dBm,
# third column is standard deviation of power in dB, fourth column is peak power in dBm;
# Additionally, graphs of mean power vs frequency, standard deviation vs frequency and peak power vs frequency 
# is provided as output;

#importing libraries
try:
    import time
except ImportError:
    print("time library not found. Please install and try again!")
    time.sleep(5)
    exit()

try:
    import os
    from os import listdir
except ImportError:
    print("os library not found. Please install and try again!")
    time.sleep(5)
    exit()

try:
    from math import pow,log10,sqrt
except ImportError:
    print("math library not found. Please install and try again!")
    time.sleep(5)
    exit()

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("matplotlib library not found. Please install and try again!")
    time.sleep(5)
    exit()

working_directory = os.getcwd()
outputtxtfiles = sorted([f for f in listdir(working_directory) if (f.startswith("output") and f.endswith(".txt"))])
# print(outputtxtfiles)

freq_list = []
mean_val_list = []
std_val_list = []
peak_val_list = []

freq_val = 698000000.0 #Start frequency: 698 MHz
freq_end_val = 818000000.0 #Stop frequency: 818 MHz
freq_inc = 10000 #Resolution bandwidth: 10 KHz
#Preparing necessary lists and populating it with default values
while True:
    freq_list.append(freq_val)
    mean_val_list.append(0)
    std_val_list.append(0)
    peak_val_list.append(-200)
    freq_val = freq_val + freq_inc
    if freq_val == freq_end_val:
        freq_list.append(freq_val)
        mean_val_list.append(0)
        std_val_list.append(0)
        peak_val_list.append(-200)
        break

for name in outputtxtfiles:
    #Open every output txt file obtained from rsa306b_samples.py and read the content
    file = open(name,'r')
    content = file.read().split('\n')
    val = 0
    ctr = 0
    for line in content:
        #The following is the line that skips reading of content
        if ctr == 0 or ctr == 4002 or ctr == 4003 or ctr == 8004 or ctr == 8005:
            ctr = ctr + 1
            continue
        #The following is the line that stops the code execution once the entire content of a txt file is read
        if ctr == 12006:
            break
        #Calcuating the peak values and mean values
        if peak_val_list[val]<(float(line.split('|')[1].strip())):
            peak_val_list[val] = (float(line.split('|')[1].strip()))
        mean_val_list[val] = mean_val_list[val] + (pow(10,((float(line.split('|')[1].strip()))/10)))
        val = val + 1
        ctr = ctr + 1

#Converting the mean values into dBm
for i in range(len(mean_val_list)):
    mean_val_list[i] = 10*log10(mean_val_list[i]/len(outputtxtfiles))

for name in outputtxtfiles:
    file = open(name,'r')
    content = file.read().split('\n')
    val = 0
    ctr = 0
    for line in content:
        if ctr == 0 or ctr == 4002 or ctr == 4003 or ctr == 8004 or ctr == 8005:
            ctr = ctr + 1
            continue
        if ctr == 12006:
            break
        #Calcuating the standard deviation of values
        std_val_list[val] = std_val_list[val] + pow(((float(line.split('|')[1].strip())) - mean_val_list[val]),2)
        val = val + 1
        ctr = ctr + 1

#Performing additional operations for finding standard deviation of values
for j in range(len(mean_val_list)):
    std_val_list[j] = sqrt(std_val_list[j]/len(outputtxtfiles))

#Writing the mean, standard deviation and peak into msp.csv file
mean_std_peak_csv = open('msp.csv','w')
for k in range(len(freq_list)):
    mean_std_peak_csv.write(str(freq_list[k])+','+str(mean_val_list[k])+','+str(std_val_list[k])+','+str(peak_val_list[k])+'\n')
# print(mean_val_list)
# print(std_val_list)    
# print(peak_val_list)

#Plotting mean power vs frequency
plt.plot(freq_list,mean_val_list)
plt.title("Plot of Mean Power vs Frequency")
plt.ylabel("Mean Power (dBm)")
plt.xlabel("Frequency (698 MHz to 818 MHz)")
plt.margins(0.025)
plt.tight_layout()
# plt.legend(['Line1','Line2'])
plt.show()

#Plotting standard deviation of power vs frequency
plt.plot(freq_list,std_val_list)
plt.title("Plot of Standard deviation of Power vs Frequency")
plt.ylabel("Standard deviation of Power (dB)")
plt.xlabel("Frequency (698 MHz to 818 MHz)")
plt.margins(0.025)
plt.tight_layout()
# plt.legend(['Line1','Line2'])
plt.show()

#Plotting peak power vs frequency
plt.plot(freq_list,peak_val_list)
plt.title("Plot of Peak Value of Power vs Frequency")
plt.ylabel("Peak Value of Power (dBm)")
plt.xlabel("Frequency (698 MHz to 818 MHz)")
plt.margins(0.025)
plt.tight_layout()
# plt.legend(['Line1','Line2'])
plt.show()
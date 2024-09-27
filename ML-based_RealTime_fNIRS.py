############ HOW TO RUN ##############
# type:
# python .\RealTime_fNIRS_ml.py -p
# Referece: https://github.com/kevinbae15/NIRScout-Algorithm-LSL-PUBLIC.git

from pylsl import StreamInlet, resolve_stream
import sys
import math
import requests
import os
import numpy as np
import scipy.signal as signal
from scipy.stats import skew, kurtosis
from scipy.signal import butter, lfilter, filtfilt

import joblib

model = joblib.load('mlp.pkl')

# first resolve an EEG stream on the lab network
def nirs_streams():
	print("looking for an NIRS stream...")
	streams = resolve_stream('type', 'NIRS')

	# create a new inlet to read from the stream
	inlet = StreamInlet(streams[0]) # len(streams) = 1
	
	return inlet
	
def trigger_streams():
	print("looking for an trigger stream...")
	streams = resolve_stream('type', 'Triggers')

	# create a new inlet to read from the stream
	trigger_inlet = StreamInlet(streams[0]) # len(streams) = 1

	return trigger_inlet

def resampling(data, sampling_rate=10.17, new_sampling_rate=10):
	resampled_data = signal.resample(data, int(len(data) * new_sampling_rate / sampling_rate))
	
	return resampled_data

def butter_lowpass(lowcut, fs, order=3):
	nyq = 0.5 * fs
	low = lowcut / nyq
	b, a = butter(order, low, btype='low')
	
	return b, a

# band-pass filter between two frequency     
def butter_lowpass_filter(data, lowcut=0.2, fs=10, order=3):
    b, a = butter_lowpass(lowcut, fs, order=order)
    #y = lfilter(b, a, data)
    y = filtfilt(b, a, data)

    return y

def feature_extraction(data, ch_list):
	features = np.empty(0)

	for i in range(len(ch_list)):
		c = ch_list[i]
		if i == 2:
			feature = skew(data[:, c]) # S6_D6 hbo_f_skew
		else:
			feature = kurtosis(data[:, c]) # S7_D5 hbo_f_kurt, S4_D2 hbr_f_kurt, S8_D7 hbo_f_kurt
		
		features = np.append(features, np.array([feature]))

	return features


total = len(sys.argv)
time = 0
session_num = 0
chunk_sec = 30
sampling_rate = 10
is_start = False

if total == 2:
	if sys.argv[1] != "-p":
		print("\nUSAGE: \n\t[-p] for priting\n\t[-c] [file] for config \n\t[-e] [file] for experiment\n")
		exit()
	else:
		while True:
			print('is_start: ', bool(is_start))
			if not is_start:
				trigger = trigger_streams()
				trigger_sample, timestamp = trigger.pull_sample()
				print(trigger_sample[1])
				if (trigger_sample[1] == 10) or (trigger_sample[1] == 11):
					if trigger_sample[1] == 11:
						session = 'target'
					elif trigger_sample[1] == 10:
						session = 'non-target'
					print(f"{session} session start")
					is_start = True
				sdata = np.empty((0, 81))

			if is_start:
				inlet = nirs_streams()
				sample = inlet.pull_sample()
				info = inlet.info()
				name = info.name()
				sampling_rate = info.nominal_srate()
				# print(info, name, sampling_rate)
				ch_names = []
				data = []
				ch = info.desc().child("channels").child("channel")
				for k in range(info.channel_count()):
					ch_names.append(ch.child_value("label"))
					data.append(str(sample[0][k]))
				
				# print("ch_names: ", ch_names)
				print("data", data)
				sdata = np.append(sdata, np.array([data]), axis=0)
				time += 1

				if time == chunk_sec:
					sdata =  resampling(sdata, sampling_rate, 10)
					sdata = butter_lowpass_filter(sdata)
					ch_list = [47, 68, 46, 60]
					features = feature_extraction(sdata, ch_list)
					features = features.reshape(1, -1)

					# pred = model.predict(features)
					prob = model.predict_proba(features)
					if prob[0][1] > 0.92:
						pred = 1
					else:
						pred = 0

					# print(pred, prob)

					if pred == 1:
						print("       ooooooo\n",
							  "     oo       oo\n",
							  "    oo         oo\n",
							  "   oo           oo\n",
							  "    oo         oo\n",
							  "     oo       oo\n",
							  "       ooooooo\n")
						print(f"Session {session_num + 1} target: {prob[0][1]}")

					else:
						print("xx          xx\n",
							  "  xx      xx\n",
							  "    xx  xx\n",
							  "      xx\n",
							  "    xx  xx\n",
							  "  xx      xx\n",
							  "xx          xx\n")
						print(f"Session {session_num + 1} non-target") # prob: {prob[0][0]}

					is_start = False
					session_num += 1
					time = 0

			if session_num == 10:
				print("End")
				break


# TIMEEX VIZ FILE FOR MANRESA AND SEABRIGHT BEACH
# Kimi Holsapple

from PIL import Image

import numpy as np
import sys

width = 1280
height = 720
depth = 512
rgb_component = 3

frame_size = width*height                       # 720*1280 = 921,600
frame_resolution = frame_size*rgb_component		# 720*1280*3 = 2,764,800
frame = []
for i in range(frame_size):
	frame.append([0]*3)

print(" Specify for how long you want the time exposure to take, ex. 20, 120, 512 ")
print(" Note the longer the time exposure the longer it takes, 512 frames takes an hour")
depth = int(input("Enter duration: "))

test_raw_len = depth*frame_resolution


print("ex. /Users/kimigrace/Downloads/manresa_scalar_512.raw ")
filepath = input("Enter the name of the scalar you would like to create a timeex of: ")
# filepath = "/Users/kimigrace/Downloads/manresa_scalar_512.raw"
dtype = np.dtype('B')

try:
	print("Opening file ")
	f = open(filepath, "rb")   
except IOError:
	print('Error While Opening the file!') 
	sys.exit()

with f:
	# byte = f.read(1)		# The parameter value 1 ensures one byte is read during each read()
	raw_data = np.fromfile(f,dtype)

	raw_data_len = len(raw_data)
	# 1415577600 values

	index = 0
	frame_index = 0

	print("Making TimeEx, this process may take a while...")
	while (index < test_raw_len):
		#print(str(frame[frame_index+1]) + " : " + str(frame_index) + " for " + str(raw_data[index]))
		frame[frame_index][0] = raw_data[index] + frame[frame_index][0]
		frame[frame_index][1] = raw_data[index + 1] + frame[frame_index][1]
		frame[frame_index][2] = raw_data[index + 2] + frame[frame_index][2]

		index = index + 3
		frame_index = frame_index + 1

		#print(frame[frame_index][2])
		# when we have reached end of frame go back, we are on next frame
		if frame_index == frame_size:
			frame_index = 0

	# find average of all added pixels this is our timeex image
	frame_index = 0	
	timeex = []		
	print("Finding averages ... ")	
	for rgb_pixel in frame:
		timeex.append(int(rgb_pixel[0]/depth))
		timeex.append(int(rgb_pixel[1]/depth))
		timeex.append(int(rgb_pixel[2]/depth))

	f.close()
	

#find the average of every pixel point
						

# ************************************************
# CONVERT RAW TO PNG
# ************************************************
#timeex array holds the entire image, just divide by 512 to get evrey image frame.
# convert the .raw into an image

# Convert list to bytes
timeex_static_img = bytes(timeex)
img = Image.frombytes('RGB', (width, height), timeex_static_img)
img.save('timeex.png')


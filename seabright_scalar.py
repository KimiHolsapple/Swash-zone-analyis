

from PIL import Image

import numpy as np
import sys

# src @ https://www.stackvidhya.com/python-read-binary-file/#:~:text=Python%20read%20binary%20file%20into%20numpy%20array,-In%20this%20section&text=First%2C%20import%20numpy%20as%20np%20to%20import%20the%20numpy%20library.&text=Next%2C%20open%20the%20binary%20file,the%20datatype%20initialized%20as%20bytes.
# how to read binary file data


#src @ https://stackoverflow.com/questions/19457227/how-to-print-like-printf-in-python3
def printf(format, *args):
    sys.stdout.write(format % args)

print("ex. /Users/kimigrace/Desktop/CSE161/seabright_scalar.raw")
file_path_scalar = input('Enter a filepath for seabright_scalar.raw: ')
dtype = np.dtype('B')

try:
    print("Opening file")
    f = open(file_path_scalar, "rb")   
except IOError:
	print('Error While Opening the file!') 
	sys.exit()

with f:
	# byte = f.read(1)		# The parameter value 1 ensures one byte is read during each read()
	raw_data = np.fromfile(f,dtype)
	raw_data_len = len(raw_data)
	# 1415577600 values
	array = [[[[0]*3]*1279]*719]*511
	length_frame = [[0]*3]*1279
	length_len = 1279*3
	image_len = length_len*719

	# image 1 row 1 scalar pixel : 640 * 3 = 1920 [r] 1921 [g] 1922 [b]
	timestack_len = 3*368640
	timestack = [0]*timestack_len   # there are 720 rows for each 512 image = 368,640 rows in video. each row is a 1D array of rgb

	index = 1920
	i = 0
	while index < raw_data_len:
		timestack[i] = raw_data[index]
		timestack[i + 1] = raw_data[index + 1]				#update by rbg count
		timestack[i + 2] = raw_data[index + 2]
		i += 3
		index += 3840	

	f.close()	
						

# ************************************************
# CONVERT RAW TO PNG
# ************************************************
#timestack array holds the entire image, just divide by 512 to get evrey image frame.
# convert the .raw into an image

gif_timestack = timestack
# Convert list to bytes
timestack_static_img = bytes(timestack)
img = Image.frombytes('RGB', (720, 512), timestack_static_img)
img.save('seabright_scalar.png')


print("Creating timeline on images")
img_array = []
bottom = 0


frame_size = 720*3
last_timestack = []

# for frame in range(1, (depth + 1)):
for frame in range(0, 512):
	timestack_img = []
	if frame != 0:
		for i in last_timestack:
			timestack_img.append(i)
	for i in gif_timestack[bottom:(bottom+frame_size)]:
		timestack_img.append(i)
		last_timestack.append(i)

	difference = 512*720-frame*720
	for i in range(difference):
	    timestack_img.append(0)
	    timestack_img.append(0)
	    timestack_img.append(0)

	scalar_slice_img = bytes(timestack_img)

    # print(len(scalar_slice_img))
	img = Image.frombytes('RGB', (720, 512), scalar_slice_img)

	img_array.append(img)
    # img.show()
	bottom = bottom + frame_size



# Create video by taking all the images stored into img_arr
# https://note.nkmk.me/en/python-pillow-gif/
print("Making Gif please wait ... i'm thinking ...")

gif = []
for image in img_array:
    gif.append(image)

gif[0].save('seabright_timestack_scalar.gif',
               save_all=True, append_images=img_array[1:], optimize=False, duration=100, loop=0)



		
		

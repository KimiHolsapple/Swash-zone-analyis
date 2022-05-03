from PIL import Image, ImageDraw
import numpy as np
import rawpy
import cv2
import sys
import math



#src @ https://stackoverflow.com/questions/19457227/how-to-print-like-printf-in-python3
def printf(format, *args):
    sys.stdout.write(format % args)


def magnitude(v_x, v_y):
    return math.sqrt(pow(v_x,2) + pow(v_y,2))

def normalize(v_x, v_y):
    mag = magnitude(v_x,v_y)
    return [ v_x/mag, v_y/mag ]

def get_normalized_vector(vec):
    v_x = vec[0]
    v_y = vec[1]
    n_vec = normalize(v_x, v_y)
    return n_vec


g_seed = 40                                   # Number of seed points for buoys. Large = crowded, few = no coverage
delta = 1280/g_seed                           # Distances between seed points
offset = delta*2                              # Offset will be how large delta is considering points are 2 components
col = 0                                       # Index in image width (0 ... 1280)
row = 240                                     # Index in image height (0 ... 720) This is the seed line
width = 1280
height = 720
depth = 512
weight = 20
vector_initial = []                            # Initial points should be 2*630*1280 
                                              # To get the next point, add offset. collect while offset + point <1280

vector_library = []                           # 512 entries of every vector pair value location (each 2*g_seed len)

# Populate the vector_initial with original positions for the first frame (should be a line)
value = 0
while(value < width*2):
    vector_initial.append([int(row),int(col)])
    col += offset
    value += offset
    

vector_k_prev = vector_initial                # vector most recent positions holds all the pair values to add new offsets  
vector_library = vector_initial
vector_k_next = []

print("ex. /Users/kimigrace/Desktop/CSE161/seabright_vector.raw")
file_path_vector = input('Enter a filepath for seabright_vector.raw: ')

try:
    print("opening file ... ")
    f = open(file_path_vector, "rb")   
except IOError:
    print('Error While Opening the file!') 
    sys.exit()

with f:
    # byte = f.read(1)      # The parameter value 1 ensures one byte is read during each read()
    raw_data = np.fromfile(f, dtype=np.int32)    #np.float32
    raw_data_len = len(raw_data)

    count = 0               # tracks how many frames deep into the raw file we are
    vector_k = []
    vector_k_x = []
    vector_k_y = []

    # collect points to draw to for each frame
    while (count < depth):
        vector_k.clear()
        vector_k_x.clear()
        vector_k_y.clear()

        for point in vector_k_prev:                          # update based on vector_prev positions
            row_index = point[0]
            col_index = point[1]
            index = row_index*col_index + (count*width*height*2)
            vector_k_x.append(raw_data[index]*weight)
            vector_k_y.append(raw_data[index + 1]*weight)
            vector_k.append([raw_data[index]*weight, raw_data[index + 1]*weight])

        # calculate new positions 
        # print("prev")
        # print(vector_k_prev)
        # print("plus \n")
        # print(vector_k_x)
        # print(vector_k_y)
        
        vector_k_next = []
        for i in range(g_seed):
            y_val =  vector_k_y[i] + vector_k_prev[i][0]                # bounded within 0 ... 719
            x_val = vector_k_x[i] + vector_k_prev[i][1]                 # bounded within 0 ... 2560 (1280 * 2)
            if( x_val > 2560 or x_val < 0):
                x_val = 2560 if x_val > 2560 else 0
            if( y_val > 719 or y_val < 0):
                y_val = 719 if y_val > 719 else 0

            vector_k_next.append([ y_val, x_val])

        # print("next")
        # print(vector_k_next)
        vector_k_prev.clear()
        vector_k_prev = vector_k_next
        for i in vector_k_next:
            vector_library.append(i)
        count += 1


    f.close()



# now open the scalar to draw onto it
dtype = np.dtype('B')

print("ex. /Users/kimigrace/Desktop/CSE161/seabright_scalar.raw")
file_path_scalar = input('Enter a filepath for seabright_scalar.raw: ')

try:
    print("opening file ... ")
    f = open(file_path_scalar, "rb")   
except IOError:
    print('Error While Opening the file!') 
    sys.exit()

with f:
    # byte = f.read(1)      # The parameter value 1 ensures one byte is read during each read()
    raw_scalar_data = np.fromfile(f,dtype)
    raw_scalar_data_len = len(raw_data)
    f.close()

# draw on each image and put it into array
# https://www.geeksforgeeks.org/python-pil-imagedraw-draw-line/
print("Creating timeline on images")
img_array = []
frame_size = 1280*3*720
bottom = 0

origin_start_point = (0, row)
origin_end_point = (2560, row)
origin_line_shape = [origin_start_point, origin_end_point]

# for frame in range(1, (depth + 1)):
# Raw scalar frame shifts after each iteration by jumping to the next frame in 1d array raw_scalar_data
# bottom is recalculated after iteration and represented the top of thew last file
# bottom will be 0 when we start
for frame in range(0, 512):
    raw_scalar_frame = raw_scalar_data[bottom:(bottom+frame_size)]
    scalar_img = bytes(raw_scalar_frame)
    img = Image.frombytes('RGB', (1280, 720), scalar_img)
    timeline_shape = []                                                 # This will hold all the buoy points to draw between them

    # seed timeline_shape
    for point in range(g_seed):
        x_pos = vector_library[point + frame*g_seed][0]
        y_pos = vector_library[point + frame*g_seed][1]
        timeline_shape.append((y_pos, x_pos))

    img1 = ImageDraw.Draw(img) 
    img1.line(timeline_shape, fill ="blue", width = 2)     #draw the blue vector line for all moving parts 
    img1.line(origin_line_shape, fill ="black", width = 2)    # Draw the black vector line
    img_array.append(img)
    # img.show()
    bottom += frame_size



#Create video by taking all the images stored into img_arr
# https://note.nkmk.me/en/python-pillow-gif/
print("Making Gif please wait, this process takes a few minutes")

gif = []
for image in img_array:
    gif.append(image)

gif[0].save('seabright_vector.gif',
               save_all=True, append_images=img_array[1:], optimize=False, duration=100, loop=0)




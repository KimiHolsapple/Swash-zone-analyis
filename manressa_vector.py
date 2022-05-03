from PIL import Image, ImageDraw
import numpy as np
import rawpy
import cv2
import sys
import math

# **************************************
# Reads in the manressa file 
#   Finds all vector displacements along a row 
#   Draws on the scalar videos 
#
#
# **************************************



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


g_seed = 320                                  # Number of seed points for buoys. Large = crowded, few = no coverage
delta = 1280/g_seed                           # Distances between seed points
offset = delta*2                              # Offset will be how large delta is considering points are 2 components
col = 0                                       # Index in image width (0 ... 1280)
row = 700                                     # Index in image height (0 ... 720) This is the seed line
width = 1280
height = 720
depth = 512
weight = 25                                    # can control the strength of timeline jumps
slope = -.3
vector_initial= []                            # Initial points should be 2*630*1280 
                                              # To get the next point, add offset. collect while offset + point <1280

vector_library = []                           # 512 entries of every vector pair value location (each 2*g_seed len)

# Populate the vector_initial with original positions for the first frame (should be a line)
count = 0
while(count < g_seed):
    vector_initial.append([int(row),int(col)])
    col += offset
    row += offset*(slope)                      # Assume a coastline for manressa starting at (0,240)
    count += 1                               #     ending at (1280, 160) as slope is 1/4
    
last_index_vec_initial = g_seed - 1 

vector_k_prev = vector_initial                # vector most recent positions holds all the pair values to add new offsets  
vector_library = vector_initial
vector_k_next = []

# filepath_vector = input("Enter user file path for manresa_vector_512_long.raw: ")
# if filepath_vector == '1':
#     filepath_vector = "/Users/kimigrace/Downloads/manresa_vector_512_long.raw"

print("ex. /Users/kimigrace/Downloads/manresa_vector_512_long.raw")
filepath_vector = input('Enter a filepath for manresa_vector_512_long.raw: ')


try:
    print("Opening file " + filepath_vector)
    f = open(filepath_vector, "rb")
except IOError:
    print('Error While Opening the file!') 
    print("manresa_vector_512_long.raw")
    sys.exit()

with f:
    raw_data = np.fromfile(f, dtype=np.int32)

    count = 0               # tracks how many frames deep into the raw file we are
    vector_k = []
    vector_k_x = []
    vector_k_y = []


    # collect points to draw to for each frame
    interpolated_strength = 5
    while (count < depth):
        vector_k.clear()
        vector_k_x.clear()
        vector_k_y.clear()

        for point in vector_k_prev:                          # update based on vector_prev positions
            row_index = point[0]
            col_index = point[1]
            index = row_index*col_index + (count*width*height*2)
            if raw_data[index] >= 100:
                raw_data[index] = 0
            if raw_data[index + 1] >= 100:
                raw_data[index] = 0
            vector_k_x.append(raw_data[index]*weight)
            vector_k_y.append(raw_data[index + 1]*weight)
            vector_k.append([raw_data[index]*weight, raw_data[index + 1]*weight])
        
        # calculate new positions based on vector displacements
        vector_k_next = []
        prev_x = 0
        prev_y = 0
        count_x = 0
        count_y = 0
        for i in range(g_seed):
            y_val =  vector_k_y[i] + vector_k_prev[i][0]                # bounded within 0 ... 719
            x_val = vector_k_x[i] + vector_k_prev[i][1]                 # bounded within 0 ... 2560 (1280 * 2)    
            # make sure it stays within the bounds of the frame
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


print("ex. /Users/kimigrace/Downloads/manresa_scalar_512.raw")
filepath_scalar = input('Enter a filepath for manresa_scalar_512.raw: ')

try:
    print("Opening file " + filepath_scalar)
    f = open(filepath_scalar, "rb")   
except IOError:
    print('Error While Opening the file!') 
    print("manressa_scalar_512")
    sys.exit()

with f:
    raw_scalar_data = np.fromfile(f,dtype)
    raw_scalar_data_len = len(raw_data)
    f.close()

# draw on each image and put it into array
# https://www.geeksforgeeks.org/python-pil-imagedraw-draw-line/
print("Creating timeline on images")
img_array = []
frame_size = 1280*3*720
bottom = 0

origin_start_point = (0, 700)
origin_end_point = (2560, row)
origin_line_shape = [origin_start_point, origin_end_point]

# Take a slice of the scalar
# we draw on every frame the original line (black) and the newly connected line (blue)
for frame in range(0, depth):
    raw_scalar_frame = raw_scalar_data[bottom:(bottom+frame_size)]
    scalar_img = bytes(raw_scalar_frame)
    img = Image.frombytes('RGB', (1280, 720), scalar_img)
    timeline_shape = []

    for point in range(g_seed):
        x_pos = vector_library[point + frame*g_seed][0]
        y_pos = vector_library[point + frame*g_seed][1]
        timeline_shape.append((y_pos, x_pos))

    img1 = ImageDraw.Draw(img) 
    img1.line(timeline_shape, fill ="blue", width = 2)

    img1.line(origin_line_shape, fill ="black", width = 2)
    img_array.append(img)
    # img.show()
    bottom += frame_size



#Create video by taking all the images stored into img_arr
# https://note.nkmk.me/en/python-pillow-gif/
print("Making Gif please wait, this process might take a few minutes.")

gif = []
for image in img_array:
    gif.append(image)

gif[0].save('manressa_vector.gif',
               save_all=True, append_images=img_array[1:], optimize=False, duration=100, loop=0)


# Swash-zone-Viz
Coastal analysis is important for engineering, logistical, and ecological purposes. These programs focuses on two video clips, one from Seabright and the other from Manresa beach, and attempts to analyze the swash zone for coastal erosion purposes. This is achieved by creating timeline, vector, and time exposure visualizations. The results were shown that there exists a swash zone on both beaches and that there is a greater wave up-wash over time. This could possibly lead to greater sediment deposit for this particular time.

*Description
*Requirements
*Installation
*Configuration
*Usage
*Maintainers

# –Description—

There are 4 provided files in this project. Each takes in the file path name of raw scalar or vector files for state beach videos. Their purpose is to generate visualizations to aid in coastal analysis.

manresa_vector.py 
Constructs the timeline for Manresa state beach.

seabright_vector.py
Constructs the timeline for Seabright state beach.

timestack_scalar.py
Constructs the timestack for Seabright and Manresa state beach both as png and gif.

timeex_scalar.py
Constructs the time exposure image for the specified file as a png. Make sure to only input the scalar raw file for this program.


# –Requirements—

This will require python3 as well as its libraries: math, pandas, and numpy. If you do not have these libraries use the pip installer to instal;l them. 

# –Installation—

Download the files as you would normally. 

# –Configuration—

No modifiable settings or configurations.

# –Usage—

Run the script from the command line using the following command:

python3 <name of file>

When prompted input the file path where the raw files are located. Follow the instructions and input only the long type raw file for Manresa beach and the unsigned char value for Seabright.

# –Maintainers—

There are no maintainers.


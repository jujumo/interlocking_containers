Summary

This is a simple interlocking containers that can be arranged and stacked.
Interlocking is asymmetric. upgrade of  https://www.thingiverse.com/thing:6241141
Customize: https://github.com/jujumo/interlocking_containers.git

NOTE: Version 3 is compatible with Version 2. Only the position of the keying feature (cut corner) changes.

## Features

-   interlocking,
-   stackable,
-  secure with a locking pin,
-  several sizes,
-  cut corner to identify the assembly position.

## Description
These containers attach to each other using an interlocking mechanism. 
It is also still possible to stack them (at least for vase mode).

The pin helps secure the containers together. Simply slide the filament into the groove.

The cut corner is a visual cue to ensure containers are assembled in the correct orientation. The opposite sides are complementary, so the containers can only fit together in one specific way. If this orientation is not respected, the containers will not align properly. The** cut corner must always be on the same side** for all containers (e.g., front left). This corner is also used as a reference point to determine the number of teeth described in the file. You need to count the teeth on the faces opposite the corner tooth.

For example, the 12x06 container is not interchangeable with the 06x12 container (like the left and right hands).

## print instructions

For all models, no support needed. 
Choose one of the three methods below.
Choose based on the print time and the mechanical strength you need.

### 1) Vase mode: 
This Prints continuously in a spiral with a single filament.
This method is the fastest, but you cannot chose the thickness.

![vase mode](https://cdn.thingiverse.com/assets/d9/f6/c3/e3/a6/vase.gif)

To use this method: 
 - Import the 'solid' model into your slicer. 
 - select "spiralize outer contour" (the name may vary in your slicer)
 - print

### 2) Custom hollow mode
This one allow you to set the wall thickness you want.

![custom](https://cdn.thingiverse.com/assets/bf/36/7f/53/69/large_display_hollow.png)

To use this method: 
 - Import the 'solid' model into your slicer. 
 - set 0% infill, 
 - set 2 wall line count (or any number you want)
 - 0 Top Layers  (the name may vary in your slicer)
 - print

### 3) With container_hollow*.stl 
 - Import the 'hollow3' model into your slicer. 
 - print 

## name convention

Files are named using the following convention: 
 ```container_FILL_Hhhh_Xxx_Yyy.stl```

where: 

- `FILL` is either "solid", "hollow1",  "hollow2" or  "hollow3",
- `hhh` is the height in mm,
- `xx` is the number of notches along x axis,
- `yy` is the number of notches along y axis.

The "solid" version are meant to be printed in vase mode.

## parametrize

If you want a custom container, follow instructions on : https://github.com/jujumo/interlocking_containers.git
# Summary

This is a simple interlocking containers that can be arranged and stacked.
Inspired but not compatible with https://www.thingiverse.com/thing:6241141.
Customize it at: https://github.com/jujumo/interlocking_containers.git


## Features

-  interlocking,
-  stackable,
-  several sizes.

## Description
These containers attach to each other using an interlocking mechanism. 
It is also still possible to stack them (at least for vase mode).

The opposite sides of the hexagon are complementary, so the containers can only fit together in one specific way. 
You need to count the teeth on the faces with the maximum number.

For example, the 5 container wil have faces with 5 notches and faces with 4 notches.
For obvious reasons, the honeycombs are only compatible with the ones with the same number of notches.

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
 - Import the 'hollow2' model into your slicer. 
 - print 

## name convention

Files are named using the following convention: 
 ```honeycomb_FILL_Hhhh_Nnn.stl```

where: 

- `FILL` is either "solid", "hollow1",  "hollow2" or  "hollow3",
- `hhh` is the height in mm,
- `nn` is the number of notches,

The "solid" version are meant to be printed in vase mode.

## parametrize

If you want a custom container, follow instructions on : https://github.com/jujumo/interlocking_containers.git
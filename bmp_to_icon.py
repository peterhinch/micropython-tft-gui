#!/usr/bin/env python3

# Convert a BMP source file to Python source.

# Copyright Robert Hammelrath and Peter Hinch 2016
# Released under the MIT licence
# Files created by any graphic tool exporting bmp files, e.g. gimp
# the colour depth may be 1, 4, 8, 16, or 24 pixels, lower sizes preferred

# Usage:
# ./bmp_to_icon checkbox_on.bmp checkbox_off.bmp
# puts files into a single Python file defaulting to icons.py (-o name can override default)
# with a dictionary 'icons' indexed by a number.
# The generated icon pathon script also defines a function get_icon(index) 
# for accessing an icon, which returns a tuple which can directly supplied 
# into the drawBitmap() function of the tft lib.
# -------------------------
# Example: Assuming an icons file called icons.py.
# then the sript usign it could look like:
#
# import tft
# import icons
# .....
# mytft = tft.TFT()
# .....
# mytft.drawBitmap(x1, y1, *icons.get_icon(0))  # draw the first icon at location x1, y1
# mytft.drawBitmap(x2, y2, *icons.get_icon(1))  # draw the scond icon at location x2, y2


import os
import argparse
from struct import unpack

# define symbol shared with repetive call as global
icon_width = None
icon_height = None
icon_colortable = None
icon_colors = None
icon_table = []
no_icons = 0

# split read, due to the bug in the SD card library, avoid reading
# more than 512 bytes at once, at a performance penalty
# required if the actual file position is not a multiple of 4
def split_read(f, buf, n):
    BLOCKSIZE = 512 ## a sector
    mv = memoryview(buf)
    bytes_read = 0
    for i in range(0, n - BLOCKSIZE, BLOCKSIZE):
        bytes_read += f.readinto(mv[i:i + BLOCKSIZE])
    if bytes_read < n and (n - bytes_read) <= BLOCKSIZE:
        bytes_read += f.readinto(mv[bytes_read:n])
    return bytes_read


def getname(sourcefile):
    return os.path.basename(os.path.splitext(sourcefile)[0])


def process(f, outfile):
# 
    global icon_width
    global icon_height
    global icon_colortable
    global icon_colors
    global icon_table
    global no_icons
    
    BM, filesize, res0, offset = unpack("<hiii", f.read(14))
    (hdrsize, imgwidth, imgheight, planes, colors, compress, imgsize, 
     h_res, v_res, ct_size, cti_size) = unpack("<iiihhiiiiii", f.read(40))
# test consistency in a set
# 
    if icon_width is not None and icon_width != imgwidth:
        print ("Error: All icons in a set must have the same width")
        return None
    else:
        icon_width = imgwidth
    if icon_height is not None and icon_height != imgheight:
        print ("Error: All icons in a set must have the same heigth")
        return None
    else:
        icon_height = imgheight
        
    if icon_colors is not None and icon_colors != colors:
        print ("Error: All icons in a set must have the same number of colors")
        return None
    else:
        icon_colors = colors
        
    if colors in (1,4,8):  # must have a color table
        if ct_size == 0: # if 0, size is 2**colors
            ct_size = 1 << colors
        colortable = bytearray(ct_size * 4)
        f.seek(hdrsize + 14) # go to colortable
        n = split_read(f, colortable, ct_size * 4) # read colortable
        if icon_colortable is None:
            icon_colortable = colortable
        if colors == 1:
            bsize = imgwidth // 8
            if img_width % 8 != 0:
                print ("Error: Icon width must be a multiple of 8")
                return None
        elif colors == 4:
            bsize = imgwidth // 2
            if imgwidth % 2 != 0:
                print ("Error: Icon width must be a multiple of 2")
                return None
        elif colors == 8:
            bsize = imgwidth
        rsize = (bsize + 3) & 0xfffc # read size must read a multiple of 4 bytes
        f.seek(offset)
        icondata = []
        for row in range(imgheight):
            b = bytearray(rsize)
            n = split_read(f, b, rsize)
            if n != rsize:
                print ("Error reading file")
                return None
            icondata.append(b) # read all lines
# store data
    else:
        f.seek(offset)
        if colors == 16:
            bsize = imgwidth * 2
            rsize = (imgwidth*2 + 3) & 0xfffc # must read a multiple of 4 bytes
            icondata = []
            for row in range(imgheight):
                b = bytearray(rsize)
                n = split_read(f, b, rsize)
                if n != rsize:
                    print ("Error reading file")
                    return None
                icondata.append(b) # read all lines
# store data
        elif colors == 24:
            bsize = imgwidth * 3
            rsize = (imgwidth*3 + 3) & 0xfffc # must read a multiple of 4 bytes
            icondata = []
            for row in range(imgheight):
                b = bytearray(rsize)
                n = split_read(f, b, rsize)
                if n != rsize:
                    print ("Error reading file")
                    return None
                icondata.append(b) # read all lines
#                
    outfile.write("{}: (\n".format(no_icons))
    for row in range(imgheight - 1, -1, -1):
        outfile.write("    b'")
        for i in range (bsize):
            outfile.write("\\x{:02x}".format(icondata[row][i]))
        outfile.write("'\n")
    outfile.write("),\n")
    no_icons += 1
    return no_icons

def write_header(outfile):
    outfile.write("""
# Code generated by bmp_to_icon.py
from uctypes import addressof

"""
)
    outfile.write("_icons = { \n")
  
def write_trailer(outfile):
    outfile.write('}\n\n')
    outfile.write("colortable = (\n    b'")
    size = len(icon_colortable)
    for i in range(size):
        outfile.write("\\x{:02x}".format(icon_colortable[i]))
        if (i % 16) == 15 and i != (size - 1):
            outfile.write("'\n    b'")
    outfile.write("')\n\n")
    outfile.write("width = {}\n".format(icon_width))
    outfile.write("height = {}\n".format(icon_height))
    outfile.write("colors = {}\n".format(icon_colors))
    outfile.write("""
def get_icon(no):
    return width, height, addressof(_icons[no]), colors, addressof(colortable)
""")

def load_bmp(sourcefiles, destfile):
    try:
        with open(getname(destfile) + ".py", 'w') as outfile:
            write_header(outfile)
            for sourcefile in sourcefiles:
                with open(sourcefile, 'rb') as f:
                    if process(f,  outfile) is None:
                        break
            write_trailer(outfile)
    except OSError as err:
        print(err)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__file__, description = 
"""Utility for producing a icon set file for the tft module by converting BMP files. 
Sample usage: ./bmp_to_icon.py checkbox_empty.bmp checkbox_tick.bmp
Produces icons.py""",
    formatter_class = argparse.RawDescriptionHelpFormatter)
    parser.add_argument('infiles', metavar ='N', type = str, nargs = '+', help = 'input file paths')
    parser.add_argument("--outfile", "-o", default = 'icons', help = "Path and name of output file (w/o extension)", required = False)
    args = parser.parse_args()
    errlist = [f for f in args.infiles if not f[0].isalpha()]
    if len(errlist):
        print('Font filenames must be valid Python variable names:')
        for f in errlist:
            print(f)
    if len(errlist) == 0:
        errlist = [f for f in args.infiles if not os.path.isfile(f)]
        if len(errlist):
            print("These bmp filenames don't exist:")
            for f in errlist:
                print(f)
    if len(errlist) == 0:
        errlist = [f for f in args.infiles if os.path.splitext(f)[1].lower() != '.bmp']
        if len(errlist):
            print("These filenames don't appear to be bmp files:")
            for f in errlist:
                print(f)
    if len(errlist) == 0:
        load_bmp(args.infiles, args.outfile)



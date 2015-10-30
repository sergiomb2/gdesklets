#! /bin/bash

# Usage:
# ./make_tiles.sh input_image output_size
#
# input_image: path to the image to process
# output_size: the size (in px) of the output image
#   - the actual size will be 8 px bigger as every tile will be given an additional transparent 1px frame
#   - the image will be resized to "output_size x output_size", regardless of any aspect ratio!
#
#
# History:
#
# 2010-02-14: v0.4.1 (H.Humpel)
#    - change free.png to 0.png (as changed in the Desklet v0.8)  
#
# 2008-09-29: v0.4 (H.Humpel)
#    - create default bg.png, free.png and restart.png in the local folder
#    - some basic output to inform the user what's going on
#
# 2008-03-07: v0.3 (H.Humpel)
#    - force size to a value that can be divided by 4
#
# 2008-02-28: v0.2 (H.Humpel)
#    - transparent framing added
#    - usage, history and comments added
#    - included into the "desklets-basic" branch
#
# 2008-02-11: v0.1 (H.Humpel)
#    - initial release
#

echo "Starting ..."

# only allow a size which can be divided by 4
rest=$(expr $2 % 4)
let "size=$2-$rest"
if [ "$rest" -gt 0 ]; then
  echo "Forcing size to: $size px (needs to be able to be divided by 4)."
fi

# calculate the cropping points
let "a=$size/4"
let "b=2*a"
let "c=3*a"

# first convert the image to a temporary file
echo "Building temporary image files"
convert "$1" -resize "$size"x"$size" "$1".resized.png

# then build the tiles including the transparent frame
echo "Building tiles"
convert "$1".resized.png -crop "$a"x"$a"+0+0 -matte -bordercolor none -border 1 1.png
convert "$1".resized.png -crop "$a"x"$a"+"$a"+0 -matte -bordercolor none -border 1 2.png
convert "$1".resized.png -crop "$a"x"$a"+"$b"+0 -matte -bordercolor none -border 1 3.png
convert "$1".resized.png -crop "$a"x"$a"+"$c"+0 -matte -bordercolor none -border 1 4.png
convert "$1".resized.png -crop "$a"x"$a"+0+"$a" -matte -bordercolor none -border 1 5.png
convert "$1".resized.png -crop "$a"x"$a"+"$a"+"$a" -matte -bordercolor none -border 1 6.png
convert "$1".resized.png -crop "$a"x"$a"+"$b"+"$a" -matte -bordercolor none -border 1 7.png
convert "$1".resized.png -crop "$a"x"$a"+"$c"+"$a" -matte -bordercolor none -border 1 8.png
convert "$1".resized.png -crop "$a"x"$a"+0+"$b" -matte -bordercolor none -border 1 9.png
convert "$1".resized.png -crop "$a"x"$a"+"$a"+"$b" -matte -bordercolor none -border 1 10.png
convert "$1".resized.png -crop "$a"x"$a"+"$b"+"$b" -matte -bordercolor none -border 1 11.png
convert "$1".resized.png -crop "$a"x"$a"+"$c"+"$b" -matte -bordercolor none -border 1 12.png
convert "$1".resized.png -crop "$a"x"$a"+0+"$c" -matte -bordercolor none -border 1 13.png
convert "$1".resized.png -crop "$a"x"$a"+"$a"+"$c" -matte -bordercolor none -border 1 14.png
convert "$1".resized.png -crop "$a"x"$a"+"$b"+"$c" -matte -bordercolor none -border 1 15.png

# copy default bg.png, 0.png and restart.png to local folder
echo "Building additional image files"
convert -size 192x192 xc:transparent -fill '#888888AA' -draw 'roundRectangle 0,0 192,192 16,16' bg.png
convert -size "$a"x"$a" xc:transparent -fill '#000000AA' -draw 'rectangle 0,0 '"$a"','"$a"'' 0.png
convert -size 140x35 xc:transparent -draw 'roundRectangle 8,8 128,28 8,8' -font Comic-Sans-MS-Bold -pointsize 24 -draw 'text 30,30 "Restart"' -channel RGBA -gaussian 0x6 -fill darkred -stroke magenta -draw 'text 25,25 "Restart"' restart.png

# and finally clean up the mess (temporary files)
echo "Cleaning temporary image files"
rm "$1".resized.png

echo "Done !"


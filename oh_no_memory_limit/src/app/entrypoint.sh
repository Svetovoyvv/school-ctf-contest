#!/bin/sh
python main.py "output/$1"
python pngresize/pngresize.py "output/$1" --height 120 -o "output/$1.clip.png"

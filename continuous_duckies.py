#! /bin/env python
from PIL import Image

from aaaaAAAA.ducky_generation.procedural_duckies import DUCKY_SIZE, make_ducky

width, height = DUCKY_SIZE
nx, ny = 8, 5

res = Image.new("RGBA", (nx * width, ny * height), color=(255, 255, 255, 255))

for x in range(nx):
    for y in range(ny):
        res.alpha_composite(make_ducky().image, (x * width, y * height))

res.save('ducky_board.png')

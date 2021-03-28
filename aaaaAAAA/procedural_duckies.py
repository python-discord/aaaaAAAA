import sys
import random
from collections import namedtuple
from colorsys import hls_to_rgb
from pathlib import Path
from typing import Optional

from PIL import Image, ImageChops

ProceduralDucky = namedtuple("ProceduralDucky", "image has_hat has_equipment has_outfit")
DuckyColors = namedtuple("DuckyColors", "eye wing body beak")
Color = tuple[int, int, int]

DUCKY_SIZE = (499, 600)
ASSETS_PATH = Path("img/duck-builder")


def make_ducky() -> ProceduralDucky:
    return ProceduralDuckyGenerator().generate()


class ProceduralDuckyGenerator:
    templates = {
        int(filename.name[0]): Image.open(filename) for filename in (ASSETS_PATH / "silverduck templates").iterdir()
    }

    def __init__(self):
        self.output: Image.Image = Image.new("RGBA", DUCKY_SIZE, color=(0, 0, 0, 0))
        self.colors = self.make_colors()

        self.has_hat = False
        self.has_equipment = False
        self.has_outfit = False

    def generate(self) -> ProceduralDucky:
        self.apply_layer(self.templates[5], self.colors.beak)
        self.apply_layer(self.templates[4], self.colors.body)
        self.apply_layer(self.templates[3], self.colors.wing)
        self.apply_layer(self.templates[2], self.colors.eye)
        self.apply_layer(self.templates[1], self.colors.eye)

        return ProceduralDucky(self.output, self.has_hat, self.has_equipment, self.has_outfit)

    def apply_layer(self, layer: Image.Image, recolor: Optional[Color] = None):
        """Add the given layer on top of the ducky. Can be recolored with the recolor argument."""
        if recolor:
            layer = ImageChops.multiply(layer, Image.new("RGBA", DUCKY_SIZE, color=recolor))
        self.output.alpha_composite(layer)

    @staticmethod
    def make_colors() -> DuckyColors:
        """Create a matching DuckyColors object."""
        hue = random.random()
        saturation = 1

        hls_colors = [(hue, random.uniform(0.3, 0.9), saturation) for _ in range(4)]

        # Lower the eye saturation
        hls_colors[0] = (hls_colors[0][0], min(.9, hls_colors[0][1] + .4), hls_colors[0][2])
        # Shift the saturation of the beck
        hls_colors[3] = (hls_colors[3][0] + .1 % 1, hls_colors[3][1], hls_colors[3][2])

        scalar_colors = [hls_to_rgb(*color_pair) for color_pair in hls_colors]
        colors = (tuple(int(color * 256) for color in color_pair) for color_pair in scalar_colors)

        colors = DuckyColors(*colors)

        return DuckyColors(*colors)


# If this file is executed we generate a random ducky and save it to disk
# A second argument can be given to seed the duck (that sounds a bit weird doesn't it)
if __name__ == "__main__":
    if len(sys.argv) > 1:
        random.seed(float(sys.argv[1]))

    ducky = make_ducky()
    print(*("{}: {}".format(key, value) for key, value in ducky._asdict().items()), sep="\n")
    ducky.image.save("ducky.png")
    print("Ducky saved to disk!")

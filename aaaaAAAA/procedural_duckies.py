import sys
import random
from collections import namedtuple
from colorsys import hls_to_rgb

from PIL import Image

ProceduralDucky = namedtuple("ProceduralDucky", "image has_hat has_equipment has_outfit")
DuckyColors = namedtuple("DuckyColors", "eye wing body beak")
Color = tuple[int, int, int]

DUCKY_SIZE = (499, 600)


def make_ducky() -> ProceduralDucky:
    return ProceduralDuckyGenerator().generate()


class ProceduralDuckyGenerator:
    def __init__(self):
        self.output = Image.new("RGBA", DUCKY_SIZE, color=(0, 0, 0, 0))
        self.colors = self.make_colors()

        self.has_hat = False
        self.has_equipment = False
        self.has_outfit = False

    def generate(self) -> ProceduralDucky:
        return ProceduralDucky(self.output, self.has_hat, self.has_equipment, self.has_outfit)

    @staticmethod
    def make_colors() -> DuckyColors:
        """Create a matching DuckyColors object."""
        hue = random.random()
        saturation = 1

        colors = [hls_to_rgb(hue, light, saturation) for light in [random.uniform(0.7, 0.85) for _ in range(4)]]

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

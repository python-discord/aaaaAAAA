import sys
import random
from collections import namedtuple
from colorsys import hls_to_rgb

ProceduralDucky = namedtuple("ProceduralDucky", "image has_hat has_equipment")
DuckyColors = namedtuple("DuckyColors", "eye wing body beak")
Color = tuple[int, int, int]


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

    print(make_colors())

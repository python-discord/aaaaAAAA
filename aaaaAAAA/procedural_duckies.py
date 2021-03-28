import sys
import random
from collections import namedtuple

ProceduralDucky = namedtuple("ProceduralDucky", "image has_hat has_equipment")

# If this file is executed we generate a random ducky and save it to disk
# A second argument can be given to seed the duck (that sounds a bit weird doesn't it)
if __name__ == "__main__":
    if len(sys.argv) > 1:
        random.seed(float(sys.argv[1]))

import os
import sys

from aaaaAAAA import game
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

game.main()

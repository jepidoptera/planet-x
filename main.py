from fileinput import filename
import sys, getopt
from world import life
from world import stilllife
still = True
filename = ''

argList = sys.argv[1:]
args, values = getopt.getopt(argList, 'af:')
for arg, value in args:
    if arg == '-f':
        filename=value
    elif arg == '-a':
        still = False

if still:
    stilllife.run(loadfile=filename)
else:
    life.Life(loadfile=filename).run()
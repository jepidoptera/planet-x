from fileinput import filename
import sys, getopt
from world import life
still = True
filename=''
# dirname='species/'
scenario: life.Scene = None

argList=sys.argv[1:]
args, values=getopt.getopt(argList, 'af:s:')
for arg, value in args:
    if arg == '-f':
        filename=value
    elif arg == '-a':
        still=False
    elif arg == '-s':
        if value == 'superdeer':
            scenario=life.Scenarios.superdeer()
        elif value == 'herbivores':
            scenario=life.Scenarios.herbivores()
        elif value == 'wolfden':
            scenario=life.Scenarios.wolfDen()
        elif value == 'random':
            scenario = life.Scenarios.random_creatures()

if not scenario: scenario = life.Scenarios.wolfDen()

if filename:
    scenario=life.loadWorld(life.dirname + filename)

if still:
    from world.stilllife import TextWorld
    TextWorld(scenario).run()
else:
    from world.animatelife import Animation
    Animation(scenario).run()
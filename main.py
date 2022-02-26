from fileinput import filename
import sys, getopt
from world import life
still = True
filename=''
dirname='species/'
scenario: life.Scenario

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
            scenario=life.Scenarios.herbivores_only()

if filename:
    scenario=life.loadWorld(dirname + filename)

if still:
    from world.stilllife import TextWorld
    TextWorld(scenario.world, scenario.creatures, scenario.steps).run()
else:
    from world.animatelife import Animation
    Animation(scenario.world, scenario.creatures, scenario.steps).run()
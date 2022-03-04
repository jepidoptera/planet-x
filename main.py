from fileinput import filename
import sys, getopt
from world import life
still = True
filename= '' # 'sugkrdeey superdeer 132807' # 'demtvazej danrsveej 71907' # 'deersheep tigerwolf 225'
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
        elif value == 'predator/prey':
            scenario=life.Scenarios.predator_prey()
        elif value == 'wolfden':
            scenario=life.Scenarios.wolfDen()
        elif value == 'immortal wolves':
            scenario=life.Scenarios.immortal_wolves()
        elif value == 'sacrificial deer':
            scenario=life.Scenarios.sacrificial_deer()
        elif value == 'random':
            scenario = life.Scenarios.random_creatures()

if filename:
    scenario=life.loadWorld(filename)

if not scenario: scenario = life.Scenarios.predator_prey()

if still:
    from world.stilllife import TextWorld
    TextWorld(scenario).run()
else:
    from world.animate import Animation
    Animation(scenario).run()
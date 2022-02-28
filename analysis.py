from world.life import *
from creatures.genome import *

def printBrain(genome):
    # 5ed133900322c000322cd5e50a17ffff171fffff57058348b71dd2a8061f7e780927c00b0b15ffff15274ccc2715ffff445999c4e61b31cf
    def fromHex(hexcode):
        input = int(hexcode[:2], 16) % len(Creature.allNeurons)
        output = int(hexcode[2:4], 16) % len(Creature.allNeurons)
        factor = int(hexcode[4:8], 16) / 0x8000 - 1 # either positive or negative, 8000 being zero
        return (Creature.allNeurons[input].name, Creature.allNeurons[output].name, factor)
    
    for n in range(int(len(genome)/8)):            
        axon = fromHex(genome[n * 8: (n + 1) * 8])
        print (f'{axon[0]} -> {axon[1]}: {axon[2]}')


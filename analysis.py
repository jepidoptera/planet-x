from world.life import *
from creatures.genome import *

def printBrain(genome):
    def get_key(val, dict: dict):
        for key, value in dict.items():
            if val == value:
                return key

            # 5ed133900322c000322cd5e50a17ffff171fffff57058348b71dd2a8061f7e780927c00b0b15ffff15274ccc2715ffff445999c4e61b31cf
    def fromHex(hexcode):
        if len(hexcode) == 8:
            input = int(hexcode[:2], 16) % len(Creature.allNeurons)
            output = int(hexcode[2:4], 16) % len(Creature.allNeurons)
            factor = int(hexcode[4:8], 16) / 0x8000 - 1 # either positive or negative, 8000 being zero
            return (Creature.allNeurons[input].name, Creature.allNeurons[output].name, factor)
        elif len(hexcode) == 16:
            operator=int(hexcode[2:4], 16)//0xf8
            threshold=int(hexcode[4:6], 16)/0xff
            input1=int(hexcode[6:8], 16) % len(Creature.allNeurons)
            input2=int(hexcode[8:10], 16) % len(Creature.allNeurons)
            output=int(hexcode[10:12], 16) % len(Creature.allNeurons)
            factor=int(hexcode[12:16], 16) / 0x8000 - 1 # either positive or negative, 8000 being zero
            return (
                Creature.allNeurons[input1].name,
                Creature.allNeurons[input2].name,
                Creature.allNeurons[output].name,
                threshold,
                get_key(operator, DoubleAxon.operators),
                factor
            )
    
    isDoubleAxon=False
    for n in range(int(len(genome)/8)):
        if isDoubleAxon:
            isDoubleAxon=False
            continue
        if int(genome[n*8: n*8 + 2], 16) != 0xff:
            axon=fromHex(genome[n * 8: (n + 1) * 8])
        else:
            axon=fromHex(genome[n * 8: (n + 2) * 8])
            isDoubleAxon=True
        if len(axon) == 3:
            print (f'{axon[0]} -> {axon[1]}: {axon[2]}')
        elif len(axon) == 6:
            print (f'{axon[0]} {axon[4]} {axon[1]} -> {axon[2]}, threshold={axon[3]} factor={axon[5]}')


def printStats(genome):
    Genome.decode(genome).printRawStats()
    
# scene=loadWorld('deersheep tigerwolf 902643.world')
# wolves=list(filter(lambda c: c.meateating > c.planteating, scene.creatures))

# brain='0014ffffed5688280325c0000325ca001126ffff11f6ffffb66f181cFF1f9fe7FF00e50b0a1affff0a1af9ff22e6d896a53c3f4a0b1dffff1a3df1723b24ffff2b18ffff2b18ffff0b180fff0b18ffff2b18ffff092b0000132aff5f'
# printBrain(brain)

def analysePop(world: Map, creatures: set[Creature]):
    with open('trends.txt', 'a') as file:
        carnivores=len(set(filter(lambda c: c.meateating > c.planteating, creatures)))
        herbivores=len(set(filter(lambda c: c.meateating < c.planteating, creatures)))
        grass=sum([node.resource.value if node.resource and node.resource.type == ResourceType.grass else 0 for node in world.nodes])
        meat=sum([node.resource.value if node.resource and node.resource.type == ResourceType.meat else 0 for node in world.nodes])
        file.write(f'carnivores: {carnivores} \n herbivores: {herbivores} \n available grass: {grass} \n available meat: {meat} \n')

def graphPopulations():
    from matplotlib import pyplot
    with open ('trends.txt', 'r') as file:
        data=file.readlines()
        carnivores=[int(data[n * 4][data[n * 4].find(':')+1:]) for n in range(int(len(data)/4))]
        herbivores=[int(data[n * 4 + 1][data[n * 4 + 1].find(':')+1:]) for n in range(int(len(data)/4))]

    # x-axis values 
    roll_num = [1, 2, 3, 4, 5, 6, 7, 8, 9] 

    # y-axis values 
    marks = [55,75,96,75,36,45,87,99,100] 


    pyplot.plot([n for n in range(len(carnivores))], carnivores, color='r') 
    pyplot.plot([n for n in range(len(herbivores))], herbivores, color='g') 


    # pyplot.show()    

# graphPopulations()
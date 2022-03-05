2/22/2022
    after a few weeks of work, i achieved some form of self-sustaining life! although they seem to be evolving into plants. investigation required.

2/23/2022
    investigated. they were exploiting a bug where by resting continuously, they could achieve infinite free energy. interesting, but i fixed it. populating the map with 3/4 x 1/4 deersheep/random crosses, i get a steep population decline followed by a rebound. probably indicates a bug in my neural code being fixed by evolution. ultimately, they stabilize into an efficient plant-eating form.

2/24/2022
    did a bunch of debugging and upgrades. fixed the deersheep so they are survivable as-is, but i will leave it running overnight to see how they optimize.

2/25/20200
    after running overnight, cumulative mutations per creature are well into the 4800s and population density has about doubled. there is almost no grass, because any that spawns is instantly and efficiently pounced on and eaten. stats are pretty consistent across all individuals, indicating that they have optimized to the environment.
    * speed=12, which is max. highly conserved. big change from the starting value of 3. high metabolic cost @ 48. this must be because i have grass spawning one at a time in random locations, so they have to compete to reach it first (which you can clearly see happening).
    * fertility=9, universally conserved. interesting because max=7. this is only possible because i manually (accidentally) set it to 9 in the template, which means any mutation of this highly prized "impossible" gene must have been weeded out. 
    * longevity=42, shockingly universally conserved. big change from the original value of 20. there are some rare longevity=35 alleles, but that's clearly like a harmful recessive that's on its way out. the metabolic cost of that is 33.6, which is signficant. live long, gather energy, have 9 kids.
    * intelligence=13, down from the original value of 20 for a metabolic savings of 2.1. why is this optimal? for one thing, it is one more than speed, ensuring that perception always preceeds action. so going any lower would lead to a slowed reaction time. in addition to the cost savings, having some extra inactive brain regions to harmlessly absorb mutations without changing behavior might be beneficial.
    * sightfield=4 has become common, although not universal. 360 vision is obviously helpful for spotting food, so that makes sense. sightrange=4 has stayed stable, probably because with the population as dense as it is, there is little chance of scoring food farther away than that.
    * no conservation or convergence of species name. they're all just a bunch of random letters at this point. would like to fix that.

    i haven't yet analyzed the brain composition to see which behaviors were selected for and how. todo.

3/4/2022
    Implemented some new features, including double axons. The most interesting stuff I've been doing is with the scenarios. Each scenario consists of a world, a collection of starting creatures, and an optional stepfunction that runs once per step. I've been running one that starts with a bunch of predators, then throws a deer at them every ten steps so they can evolve to catch it. Pretty successful! I call this newly evolved creation the qiltrpolf. Next: throw qiltrpolf and danrsveej in together and see how they get along ;)

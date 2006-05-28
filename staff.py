from __future__ import division
import math, sets

class Spell:
    def __init__(self, name, level, material=0, focus=0, xp=0):
        self.name = name
        self.level = level
        self.material = material
        self.focus = focus
        self.xp = xp
        self.minimumCasterLevel = level * 2 - 1

    def __cmp__(self, other):
        return cmp(self.level, other.level)

    def __str__(self):
        return "%s %d" % (self.name, self.level)

    __repr__ = __str__

    def __hash__(self):
        return hash(str(self))
 

class Staff:
    def __init__(self, name):
        self.name = name
        self.spells = sets.Set()

    def multiplier(self):
        return [375, 0.75 * 375] + [0.5 * 375] * (len(self.spells) - 2)

    def minimumCasterLevel(self):
        return max(8, *([ s.minimumCasterLevel for (s, c) in self.spells ]))

    def spellCost(self, (spell, charges)):
        return ((self.minimumCasterLevel() * spell.level) / charges,
                (50 * spell.material / charges))

    def add(self, spell, charges=1):
        self.spells.add((spell, charges))

    def costs(self):
        spells = self.getSpells()
        return [ (spell * multiplier, material) for multiplier, (spell, material)
                 in zip(self.multiplier(), map(self.spellCost, spells)) ]
    
    def cost(self):
        costs = zip(*(self.costs()))
        return sum(costs[0]), sum(costs[1])

    def creationCost(self):
        return "%d GP; %d XP; %d days" % creationCost(*(self.cost()))

    def getSpells(self):
        spells = list(self.spells)
        spells.sort()
        spells.reverse()
        return spells

    def __str__(self):
        spells = self.getSpells()
        spells = "\n".join([ "%s (%d) -- %d GP" % (spell, charges, basePrice+material)
                             for ((spell, charges), (basePrice, material))
                             in zip(spells, self.costs()) ])
        return ("Staff of %s\n--\n%s\n--\nMarket Price: %dGP\nCreation cost: %s" %
                (self.name, spells, sum(self.cost()), self.creationCost()))

def creationCost(basePrice, material):
    return (basePrice / 2 + material, math.ceil(basePrice / 25),
            math.ceil(basePrice / 1000))

deathWard = Spell("Death Ward", 4)
disruptingWeapon = Spell("Disrupting Weapon", 5)
eaglesSplendor = Spell("Eagle's Splendor", 2)
searingLight = Spell("Searing Light", 3)
detectUndead = Spell("Detect Undead", 1)
consecrate = Spell("Consecrate", 2, 50)
heal = Spell("Heal", 6)
undeathToDeath = Spell("Undeath to Death", 6, 500)

controlWeather = Spell("Control Weather", 7)
controlWindsAtSea = Spell("Control Winds at Sea", 5)
contralWater = Spell("Control Water", 4)
waterWalk = Spell("Water Walk", 3)
fogCloud = Spell("Fog Cloud", 2)
confusion = Spell("Confusion", 4)
windWall = Spell("Wind Wall", 3)

mislead = Spell("Mislead", 6)
breakEnchantment = Spell("Break Enchantment", 5)
fom = Spell("Freedom of Movement", 4)
prayer = Spell("Prayer", 3)
findTraps = Spell("Find Traps", 2)
spellRes = Spell("Spell Resistance", 5)
spellImmunity = Spell("Spell Immunity", 4)
wordOfRecall = Spell("Word of Recall", 6)

luckStaff = [mislead, breakEnchantment, prayer, findTraps, spellRes]

spells = [deathWard, eaglesSplendor, searingLight, detectUndead, consecrate,
          undeathToDeath, disruptingWeapon, heal]

pirateStaff = [controlWeather, controlWindsAtSea, contralWater, waterWalk,
               fogCloud, confusion, windWall]

burningHands = Spell("Burning Hands", 1)
fireBall = Spell("Fireball", 3)
wallOfFire = Spell("Wall of Fire", 4)
fire = [burningHands, fireBall, wallOfFire]

shieldOfLaw = Spell("Shield of Law", 8)
shieldOther = Spell("Shield Other", 2)
shieldOfFaith = Spell("Shield of Faith", 1)
shield = Spell("Shield", 1)

SHIELDS = [shieldOfLaw, shieldOther, shieldOfFaith, shield]

def dumpStaff(name, spells, charges):
    staff = Staff(name)
    for spell, charge in zip(spells, charges):
        staff.add(spell, charge)
    print '-' * 60 
    print staff
    print '-' * 60
    print
    return staff


if __name__ == '__main__':
    life = Staff('Angry Life')
    for s in spells:
        life.add(s)
    print life
    print 

    luck = Staff('Luck')
    for s in luckStaff:
        luck.add(s)
    print luck

    print
    print
    pirate = Staff('Piracy')
    pirate.add(pirateStaff[0], 2)
    for s in pirateStaff[1:]:
        pirate.add(s)
    print pirate

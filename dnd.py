from __future__ import division
import random, math


def dice(n):
    return random.randrange(1, n+1)

def d(m, n):
    return sum([ dice(n) for i in range(m) ])

d20 = lambda x=1 : d(x, 20)
d12 = lambda x=1 : d(x, 12)
d10 = lambda x=1 : d(x, 10)
d8  = lambda x=1 : d(x, 8)
d6  = lambda x=1 : d(x, 6)
d4  = lambda x=1 : d(x, 4)

def bonus(stat):
    return (stat - 10) // 2

def opposedCheck(bonusA, bonusB):
    a = d20(1) + bonusA
    b = d20(1) + bonusB
    return a, b

def randomHitPoints(diceType, con, level):
    """A character with 3 hit dice (level 3 for most races) can generate their
    hit points e.g. (for a cleric, Hit Dice: d8)
       hp = randomHitPoints(8, 14, 3)
    Where 14 is the cleric's constitution stat.
    """
    return (level * bonus(con)) + diceType + d((level - 1), diceType)

randomVitalityPoints = randomVitPoints = randomHitPoints


class Combatant:
    """Represents a single combatant.  Can attack (very limited interface),
    and take damage (under the Shakta system).

    Insert into a Combat instance for extra fun.
    """

    """attack() uses this to see whether a roll was a threat.
    Set to 19 for 19-20, 18 for 18-20 etc
    """
    threatRange = 20
    
    def __init__(self, name, vit, con, armor, attackBonus, damage):
        """Create a combatant with the given name, starting vitality,
        starting wounds, armor bonus, attack bonus and damage.

        These are all integers, except for damage, which ought to be
        a callable that accepts no arguments.
        e.g. damage=d12 or damage=lambda : d12() + 10
        """
        self.name = name
        self.vit = vit
        self.dr = armor
        self.wound = con
        self._attack = attackBonus
        self._damage = damage

    def __str__(self):
        return self.name

    def __repr__(self):
        return "%s <vit=%d, wounds=%d>" % (self.name, self.vit, self.wound)

    def __eq__(self, other):
        return self.name == other.name

    def attack(self):
        """Roll a d20, add the attack bonus, and roll for damage.  Returns
        the damage rolled.
        """
        roll = d20()
        crit = ''
        if roll >= self.threatRange:
            crit = '(threat)'
        dmg = self.damage()
        print '%s rolled %d for %d damage %s' % (self.name, roll + self._attack,
                                                 dmg, crit)
        return dmg

    def damage(self):
        """Roll for damage.
        """
        return self._damage()

    def inflictWounds(self, dmg):
        """Call me to inflict wounds directly, ignoring vitality points.
        This method takes care of damage reduction due to armor.
        """
        if dmg < self.dr:
            return dmg
        self.wound -= dmg
        self.wound += self.dr
        return self.dr

    def takeDamage(self, dmg):
        """Call when this combatant has been hit.  Pass the rolled damage
        (might be the return value of someone's attack()). Takes vitality
        and wounds into account.  Use takeCritical if the attacker rolled
        a critical.
        Returns a tuple of (vit, wounds)
        """
        self.vit -= dmg
        if self.vit < 0:
            self.inflictWounds(abs(self.vit))
            self.vit = 0
        if self.wound <= -10:
            print "Character is dead %r" % (self,)
        else:
            print "Taken %d damage: %r" % (dmg, self)
        return self.vit, self.wound

    def takeCritical(self, dmg, mult=2):
        """Call when the combatant has been hit by a critical blow.
        Default multiplier is 2.  Returns a tuple of (vit, wounds)
        """
        soaked = self.inflictWounds(dmg)
        return self.takeDamage(soaked * mult)
    

REALLY_BIG = 99
class Combat:
    """This represents a combat encounter.  It stores all of the combatants,
    (most likely instances of Combatant, but not necessarily).

    Starts on round 0.  Add combatants using add(), shift to the next
    combatant using next().  current() will return the current combatant,
    i.e. the person who's action it is right now.

    Print an instance out to get a summary of the encounter.    
    """
    
    def __init__(self):
        self._combatants = []
        self.round = 0
        self._initiativeCount = REALLY_BIG
        
    def addCombatant(self, fighter, initiative):
        """Add a combatant (usually a Combatant instance) with the given
        initiative.  Initiatives must be unique (this is a quick hack),
        so resolve high/low manually and use things like 16.1, 16.9 etc"""
        self._combatants.append((initiative, fighter))
    add = addCombatant

    def __str__(self):
        self._combatants.sort()
        self._combatants.reverse()
        table = [ '%d:\t%r' % entry for entry in self._combatants ]
        try:
            action = "%s's action" % (self.currentCombatant(),)
        except ValueError:
            action = ''
        return "Round #%d, %s\n" % (self.round, action) + '\n'.join(table)

    def getCombatant(self, name):
        """Find a combatant by name"""
        return [ y for (x, y) in self._combatants if str(y) == name ][0]

    def changeInitiative(self, fighter, initiative):
        """Change the initiative of a combatant.  Use when someone has readied,
        or something similar.
        """
        index = [ i for i, (x, y) in enumerate(self._combatants)
                  if y == fighter ][0]
        del self._combatants[index]
        self.addCombatant(fighter, initiative)

    def currentCombatant(self):
        """Return the current combatant, i.e. the person who's action it is.
        Note that you have to call next() at least once before this will work. 
        """
        current = [ y for (x, y) in self._combatants
                    if x == self._initiativeCount ]
        if len(current) == 0:
            raise ValueError("There is no combatant at initiative %d"
                             % (self._initiativeCount,))
        if len(current) == 1:
            return current[0]
        raise ValueError("Initiative must be unique")
    current = currentCombatant

    def next(self):
        """Shift to the next player in combat.  Returns the new active player
        (current combatant)
        """
        future = [ x for (x, y) in self._combatants
                   if x < self._initiativeCount ]
        if len(future) == 0:
            print "NEW ROUND"
            self.round += 1
            self._initiativeCount = REALLY_BIG
            return self.next()
        self._initiativeCount = max(future)
        up = self.currentCombatant()
        print ("Round #%d, %d: %s's action"
               % (self.round, self._initiativeCount, up))
        return up
        

def statroll():
    ds = [ dice(6) for i in range(4) ]
    ds.sort()
    return sum(ds[1:])


def sign(n):
    if n >= 0:
        return '+'
    else:
        return ''


def abilityCost(stat):
    table = { 9: 1, 10: 2, 11:3, 12: 4, 13: 5, 14: 6,
              15: 8, 16: 10, 17: 13, 18: 16 }
    if stat < 9:
        return 0
    return table[stat]


def abilitiesCost(stats):
    return sum(map(abilityCost, stats))


def rollStats():
    stats = [ statroll() for i in range(7) ]
    stats.sort()
    return stats[1:]


def rollCoolStats(minimum=0):
    while True:
        stats = rollStats()
        if abilitiesCost(stats) >= minimum:
            return stats
        

def generateStats():
    stats = rollCoolStats()
    for stat in stats:
        b = bonus(stat)
        print '%2d [%s%d]' % (stat, sign(b), b)
    print
    print 'Cost: %d' % (abilitiesCost(stats),)
    
kwahu = Combatant("Kwahu",52,14,7,10,lambda: d12() + 6)
jarek = Combatant("Jarek", 32, 15,1,3,lambda: d8())
jarek.threatRange = 19
zane = Combatant("Zane",40,16,4,6,lambda: d6() + 3)
zane.threatRange = 17
blueFox = Combatant("Blue Fox", 59, 16, 4, 11, lambda: d8() +3)
kwahu.damage = lambda: d12() + 8

from math import sqrt, floor


class Leveling:
    EXP_FIELD = 0
    LVL_FIELD = 0

    BASE = 10000
    GROWTH = 2500

    HALF_GROWTH = 0.5 * GROWTH

    REVERSE_PQ_PREFIX = -(BASE - 0.5 * GROWTH) / GROWTH
    REVERSE_CONST = REVERSE_PQ_PREFIX * REVERSE_PQ_PREFIX
    GROWTH_DIVIDES_2 = 2 / GROWTH

    def getLevel(self, exp):
        return floor(1 + self.REVERSE_PQ_PREFIX + sqrt(self.REVERSE_CONST + self.GROWTH_DIVIDES_2 * exp))

    def getExactLevel(self, exp):
        return self.getLevel(exp) + self.getPercentageToNextLevel(exp)

    def getExpFromLevelToNext(self, level):
        return self.GROWTH * (level - 1) + self.BASE

    def getTotalExpToLevel(self, level):
        lv = floor(level)
        x0 = self.getTotalExpToFullLevel(lv)
        if level == lv:
            return x0
        else:
            return (self.getTotalExpToFullLevel(lv + 1) - x0) * (level % 1) + x0

    def getTotalExpToFullLevel(self, level):
        return (self.HALF_GROWTH * (level - 2) + self.BASE) * (level - 1)

    def getPercentageToNextLevel(self, exp):
        lv = self.getLevel(exp)
        x0 = self.getTotalExpToLevel(lv)
        return (exp - x0) / (self.getTotalExpToLevel(lv + 1) - x0)

    def getExperience(self, EXP_FIELD, LVL_FIELD):
        exp = int(EXP_FIELD)
        exp += self.getTotalExpToFullLevel(LVL_FIELD + 1)
        return exp

class ExpCalculator:

    def __init__(self):
        self.EASY_LEVELS = 4
        self.EASY_LEVELS_XP = 7000
        self.XP_PER_PRESTIGE = 96 * 5000 + self.EASY_LEVELS_XP

        self.LEVELS_PER_PRESTIGE  = 100

        self.HIGHEST_PRESTIGE = 10

    def getExpForLevel(self, level):
        if level == 0: return 0

        respectedLevel = self.getLevelRespectingPrestige(level)
        if respectedLevel > self.EASY_LEVELS: return 5000
        if respectedLevel == 1: return 500
        if respectedLevel == 2: return 1000
        if respectedLevel == 3: return 2000
        if respectedLevel == 4: return 3500

        return 5000

    def getPrestigeForExp(self, exp):
        return self.getPrestigeForLevel(self.getLevelForExp(exp))

    def getPrestigeForLevel(self, level):
        prestige = level / self.LEVELS_PER_PRESTIGE
        return prestige

    def getLevelRespectingPrestige(self, level):
        if level > self.HIGHEST_PRESTIGE * self.LEVELS_PER_PRESTIGE:
            return level - self.HIGHEST_PRESTIGE * self.LEVELS_PER_PRESTIGE
        else:
            return level % self.LEVELS_PER_PRESTIGE

    def getLevelForExp(self, exp):
        prestiges = exp / self.XP_PER_PRESTIGE

        level = prestiges * self.LEVELS_PER_PRESTIGE

        expWithoutPrestiges = exp - (prestiges * self.XP_PER_PRESTIGE)

        i = 1
        while i <= self.EASY_LEVELS:
            expForEasyLevel = self.getExpForLevel(i)
            if expWithoutPrestiges < expForEasyLevel:
                break
            level += 1
            expWithoutPrestiges -= expForEasyLevel
        level += expWithoutPrestiges / 5000

        return level

class GuildLevelUtil:
    EXP_NEEDED = [
        100000,
        150000,
        250000,
        500000,
        750000,
        1000000,
        1250000,
        1500000,
        2000000,
        2500000,
        2500000,
        2500000,
        3000000,
    ]

    def getLevel(self, exp):
        level = 0
        i = 0
        while True:
            need = self.EXP_NEEDED[i]
            exp -= need
            if exp < 0: return level
            else: level+=1
            if i < len(self.EXP_NEEDED)-1:
                i+=1

class ARENA(object):

    def __init__(self, lb):
        self.JSON = lb['ARENA']

    def arena_rating_a(self): # Rating
        for table in self.JSON:
            if table['path'] == 'arena_rating_a':
                return table

    def wins_1v1(self): # 1v1 Wins
        for table in self.JSON:
            if table['path'] == 'wins_1v1':
                return table

class BATTLEGROUND(object):

    def __init__(self, lb):
        self.JSON = lb['BATTLEGROUND']

    def wins(self): # Overall Wins
        for table in self.JSON:
            if table['path'] == 'wins':
                return table

    def wins_weekly_b(self): # Weekly Wins
        for table in self.JSON:
            if table['path'] == 'wins_weekly_b':
                return table

    def wins_domination(self): # Overall DOM Wins
        for table in self.JSON:
            if table['path'] == 'wins_domination':
                return table

    def wins_teamdeathmatch(self): # Overall TDM Wins
        for table in self.JSON:
            if table['path'] == 'wins_teamdeathmatch':
                return table

    def wins_capturetheflag(self): # Overall CTF Wins
        for table in self.JSON:
            if table['path'] == 'wins_capturetheflag':
                return table

class BEDWARS(object):

    def __init__(self, lb):
        self.JSON = lb['BEDWARS']

    def bedwars_level(self): # Current Level
        for table in self.JSON:
            if table['path'] == 'bedwars_level':
                return table

    def wins(self): # Overall Wins
        for table in self.JSON:
            if table['path'] == 'wins':
                return table

    def wins_1(self): # Weekly Wins
        for table in self.JSON:
            if table['path'] == 'wins_1':
                return table

    def final_kills(self): # Overall Final Kills
        for table in self.JSON:
            if table['path'] == 'final_kills':
                return table

    def final_kills_1(self): # Weekly Final Kills
        for table in self.JSON:
            if table['path'] == 'final_kills_1':
                return table

class GINGERBREAD(object):

    def __init__(self, lb):
        self.JSON = lb['GINGERBREAD']

    def gold_trophy(self): # Overall Gold Trophies
        for table in self.JSON:
            if table['path'] == 'gold_trophy':
                return table

    def gold_1(self): # Weekly Gold Trophies
        for table in self.JSON:
            if table['path'] == 'gold_1':
                return table

    def gold_2(self): # Monthly Gold Trophies
        for table in self.JSON:
            if table['path'] == 'gold_2':
                return table

    def laps_completed(self): # Overall Laps Completed
        for table in self.JSON:
            if table['path'] == 'laps_completed':
                return table

class MCGO(object):

    def __init__(self, lb):
        self.JSON = lb['MCGO']

    def kills(self): # Overall Kills
        for table in self.JSON:
            if table['path'] == 'kills':
                return table

    def kills_a(self): # Monthly Kills
        for table in self.JSON:
            if table['path'] == 'kills_a':
                return table

    def kills_b(self): # Weekly Kills
        for table in self.JSON:
            if table['path'] == 'kills_b':
                return table

class MURDER_MYSTERY(object):

    def __init__(self, lb):
        self.JSON = lb['MURDER_MYSTERY']

    def wins(self): # Overall Wins
        for table in self.JSON:
            if table['path'] == 'wins':
                return table

    def wins_1(self): # Weekly Wins
        for table in self.JSON:
            if table['path'] == 'wins_1':
                return table

    def kills(self): # Overall Kills
        for table in self.JSON:
            if table['path'] == 'kills':
                return table

    def kills_1(self): # Weekly Kills
        for table in self.JSON:
            if table['path'] == 'kills_1':
                return table

    def murderer_kills(self): # Overall Kills as Murderer
        for table in self.JSON:
            if table['path'] == 'murderer_kills':
                return table

    def murderer_kills_1(self): # Weekly Kills as Murderer
        for table in self.JSON:
            if table['path'] == 'murderer_kills_1':
                return table

class PAINTBALL(object):

    def __init__(self, lb):
        self.JSON = lb['PAINTBALL']

    def kills(self): # Overall Kills
        for table in self.JSON:
            if table['path'] == 'kills':
                return table

    def kills_a(self): # Monthly Kills
        for table in self.JSON:
            if table['path'] == 'kills_a':
                return table

    def kills_b(self): # Weekly Kills
        for table in self.JSON:
            if table['path'] == 'kills_b':
                return table

class PROTOTYPE(object):

    def __init__(self, lb):
        self.JSON = lb['PROTOTYPE']

class QUAKECRAFT(object):

    def __init__(self, lb):
        self.JSON = lb['QUAKECRAFT']

    def kills(self): # Overall Kills
        for table in self.JSON:
            if table['path'] == 'kills':
                return table

    def kills_a(self): # Monthly Kills
        for table in self.JSON:
            if table['path'] == 'kills_a':
                return table

    def kills_b(self): # Weekly Kills
        for table in self.JSON:
            if table['path'] == 'kills_b':
                return table

class SKYCLASH(object):

    def __init__(self, lb):
        self.JSON = lb['SKYCLASH']

    def kills(self): # Total Kills
        for table in self.JSON:
            if table['path'] == 'kills':
                return table

    def kills_a(self): # Monthly Kills
        for table in self.JSON:
            if table['path'] == 'kills_a':
                return table

    def wins_solo(self): # Solo Wins
        for table in self.JSON:
            if table['path'] == 'wins_solo':
                return table

    def wins_doubles(self): # Doubles Wins
        for table in self.JSON:
            if table['path'] == 'wins_doubles':
                return table

    def wins_team_war(self): # TeamWar Wins
        for table in self.JSON:
            if table['path'] == 'wins_team_war':
                return table

class SKYWARS(object):

    def __init__(self, lb):
        self.JSON = lb['SKYWARS']

    def skywars_rating_a(self): # Overall Rating
        for table in self.JSON:
            if table['path'] in ['skywars_rating_b', 'skywars_rating_a']:
                return table

    def wins(self): # Overall Wins
        for table in self.JSON:
            if table['path'] == 'wins':
                return table

    def kills(self): # Overall Kills
        for table in self.JSON:
            if table['path'] == 'kills':
                return table

    def kills_weekly_1(self): # Weekly Kills
        for table in self.JSON:
            if table['path'] == 'kills_weekly_1':
                return table

    def kills_monthly_2(self): # Monthly Kills
        for table in self.JSON:
            if table['path'] == 'kills_monthly_2':
                return table

class SPEED_UHC(object):

    def __init__(self, lb):
        self.JSON = lb['SPEED_UHC']

    def salt(self): # Total Salt
        for table in self.JSON:
            if table['path'] == 'salt':
                return table

    def kills_normal(self): # Normal Kills
        for table in self.JSON:
            if table['path'] == 'kills_normal':
                return table

    def wins_normal(self): # Normal Wins
        for table in self.JSON:
            if table['path'] == 'wins_normal':
                return table

    def kills_insane(self): # Insane Kills
        for table in self.JSON:
            if table['path'] == 'kills_insane':
                return table

    def wins_insane(self): # Insane Wins
        for table in self.JSON:
            if table['path'] == 'wins_insane':
                return table

class SUPER_SMASH(object):

    def __init__(self, lb):
        self.JSON = lb['SUPER_SMASH']

    def smash_level_total(self): # Overall Smash Level
        for table in self.JSON:
            if table['path'] == 'smash_level_total':
                return table

    def kills(self): # Overall Kills
        for table in self.JSON:
            if table['path'] == 'kills':
                return table

    def kills_monthly_a(self): # Monthly Kills
        for table in self.JSON:
            if table['path'] == 'kills_monthly_a':
                return table

    def kills_weekly_b(self): # Weekly Kills
        for table in self.JSON:
            if table['path'] == 'kills_weekly_b':
                return table

class SURVIVAL_GAMES(object):

    def __init__(self, lb):
        self.JSON = lb['SURVIVAL_GAMES']

    def kills(self): # Overall Kills
        for table in self.JSON:
            if table['path'] == 'kills':
                return table

    def wins(self): # Overall Wins
        for table in self.JSON:
            if table['path'] == 'wins':
                return table

    def wins_teams(self): # Overall Teams Wins
        for table in self.JSON:
            if table['path'] == 'wins_teams':
                return table

class TNTGAMES(object):

    def __init__(self, lb):
        self.JSON = lb['TNTGAMES']

    def wins_tntrun(self):  # TNT Run Wins
        for table in self.JSON:
            if table['path'] == 'wins_tntrun':
                return table

    def wins_pvprun(self):  # PVP Run Wins
        for table in self.JSON:
            if table['path'] == 'wins_pvprun':
                return table

    def wins_capture(self):  # Wizards Wins
        for table in self.JSON:
            if table['path'] == 'wins_capture':
                return table

    def wins_tntag(self):  # TNT Tag Wins
        for table in self.JSON:
            if table['path'] == 'wins_tntag':
                return table

    def wins_bowspleef(self):  # Spleef Wins
        for table in self.JSON:
            if table['path'] == 'wins_bowspleef':
                return table

class TRUE_COMBAT(object):

    def __init__(self, lb):
        self.JSON = lb['TRUE_COMBAT']

    def wins(self):  # Overall Wins
        for table in self.JSON:
            if table['path'] == 'wins':
                return table

    def kills(self):  # Overall Kills
        for table in self.JSON:
            if table['path'] == 'kills':
                return table

    def kills_monthly_a(self):  # Monthly Kills
        for table in self.JSON:
            if table['path'] == 'kills_monthly_a':
                return table

    def kills_weekly_b(self):  # Weekly Kills
        for table in self.JSON:
            if table['path'] == 'kills_weekly_b':
                return table

class UHC(object):

    def __init__(self, lb):
        self.JSON = lb['UHC']

    def kills(self):  # Overall Kills
        for table in self.JSON:
            if table['path'] == 'kills':
                return table

    def kills_monthly_a(self):  # Monthly Kills
        for table in self.JSON:
            if table['path'] == 'kills_monthly_a':
                return table

    def wins(self):  # Overall Wins
        for table in self.JSON:
            if table['path'] == 'wins':
                return table

    def monthly_wins_a(self):  # Monthly Wins
        for table in self.JSON:
            if table['path'] == 'monthly_wins_a':
                return table

class VAMPIREZ(object):

    def __init__(self, lb):
        self.JSON = lb['VAMPIREZ']

    def human_wins(self):  # Overall Human Wins
        for table in self.JSON:
            if table['path'] == 'human_wins':
                return table

    def monthly_human_wins_a(self):  # Monthly Human Wins
        for table in self.JSON:
            if table['path'] == 'monthly_human_wins_a':
                return table

    def weekly_human_wins_b(self):  # Weekly Human Wins
        for table in self.JSON:
            if table['path'] == 'weekly_human_wins_b':
                return table

class WALLS(object):

    def __init__(self, lb):
        self.JSON = lb['WALLS']

    def kills(self):  # Overall Kills
        for table in self.JSON:
            if table['path'] == 'kills':
                return table

    def monthly_kills(self):  # Monthly Kills
        for table in self.JSON:
            if table['path'] in ['monthly_kills_a', 'monthly_kills_b']:
                return table

    def weekly_kills(self):  # Weekly Kills
        for table in self.JSON:
            if table['path'] in ['weekly_kills_b']:
                return table

class WALLS3(object):

    def __init__(self, lb):
        self.JSON = lb['WALLS3']

    def finalKills(self):  # Overall Final Kills
        for table in self.JSON:
            if table['path'] == 'finalKills':
                return table

    def monthly_finalKills_a(self):  # Monthly Final Kills
        for table in self.JSON:
            if table['path'] == 'monthly_finalKills_a':
                return table

    def weekly_finalKills_b(self):  # Weekly Final Kills
        for table in self.JSON:
            if table['path'] == 'weekly_finalKills_b':
                return table
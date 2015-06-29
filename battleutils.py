import json
import random

from requests_futures.sessions import FuturesSession

import utils


POKEDEX = json.load(open('./BattlePokedex.json'))
TYPES = json.load(open('./BattleTypeChart.json'))
MOVES = json.load(open('./BattleMovedex.json'))


def natureboost(nature):
    table = {"Adamant": {"plus": "atk", "minus": "spa"},
             "Bashful": {},
             "Bold": {"plus": "def", "minus": "atk"},
             "Brave": {"plus": "atk", "minus": "spe"},
             "Calm": {"plus": "spd", "minus": "atk"},
             "Careful": {"plus": "spd", "minus": "spa"},
             "Docile": {},
             "Gentle": {"plus": "spd", "minus": "def"},
             "Hardy": {},
             "Hasty": {"plus": "spe", "minus": "def"},
             "Impish": {"plus": "def", "minus": "spa"},
             "Jolly": {"plus": "spe", "minus": "spa"},
             "Lax": {"plus": "def", "minus": "spd"},
             "Lonely": {"plus": "atk", "minus": "def"},
             "Mild": {"plus": "spa", "minus": "def"},
             "Modest": {"plus": "spa", "minus": "atk"},
             "Naive": {"plus": "spe", "minus": "spd"},
             "Naughty": {"plus": "atk", "minus": "spd"},
             "Quiet": {"plus": "spa", "minus": "spe"},
             "Quirky": {},
             "Rash": {"plus": "spa", "minus": "spd"},
             "Relaxed": {"plus": "def", "minus": "spe"},
             "Sassy": {"plus": "spd", "minus": "spe"},
             "Serious": {},
             "Timid": {"plus": "spe", "minus": "atk"}}
    return table[nature.capitalize()]


def statcalc_hp(base, iv, ev, level):
    return int((((iv + 2*base + (ev/4.0) + 100) * level)/100.0) + 10)


def statcalc(stat, base, iv, ev, level, nature):
    boosts = natureboost(nature)

    if boosts.get('plus') == stat:
        if boosts['minus'] == stat:  # If both
            naturemod = 1.0
        else:  # If only plus
            naturemod = 1.1
    elif boosts.get('minus') == stat:  # If only minus
        naturemod = 0.9
    else:  # If this stat isn't affected by the nature
        naturemod = 1.0

    # Double int() is because the result is rounded down before naturemod is
    # applied, then rounded down again... thanks, gamefreak!
    return int(int(((((iv + 2*base + (ev/4.0)) * level)/100.0) + 5)) * naturemod)


def single_effect(source, target):
    multiplier_map = {0: 1,
                      1: 2,
                      2: 0.5,
                      3: 0}

    return multiplier_map[TYPES[target]['damageTaken'][source]]


def effectiveness(move, target):
    result = 1

    for user_type in target.types:
        result *= single_effect(MOVES[move]['type'], user_type)

    return result


def modifier_calc(source, target, move):
    result = 1.0

    for user_type in source['types']:
        if MOVES[move]['type'] == user_type:
            result *= 1.5
            break

    result *= effectiveness(move, target)

    if random.randint(1, 16) == 1:
        result *= 2.0

    other = 1.0  # Not implemented
    result *= other

    randoffset = random.randint(85, 100)/100.0

    result *= randoffset

    return result


def dmg_calc(source, target, move):
    a = (2*source['level'] + 10)/250.0

    if MOVES[move]['category'] == 'Physical':
        b = float(source['attack']) / target['defense']
    elif MOVES[move]['category'] == 'Special':
        b = float(source['spattack']) / target['spdefense']
    else:
        b = 0

    c = MOVES[move]['basePower']

    mod = modifier_calc(source, target, move)

    return int((a * b * c + 2) * mod)


def calculate_move_score(active, types, target, move):
    move = utils.condense(move)

    # Score is zero for all of these
    blacklist = ['suckerpunch',
                 'focuspunch',
                 'fakeout',
                 'return',
                 'frustration',
                 'snore',
                 'dreameater',
                 'lastresort',
                 'explosion',
                 'selfdestruct',
                 'synchronoise',
                 'belch',
                 'trumpcard',
                 'wringout'
                 ]

    badlist = ['gigaimpact',
               'hyperbeam',
               'rockwrecker',
               'frenzyplant',
               'hydrocannon',
               'blastburn',
               'roaroftime',
               'skyattack',
               'solarbeam',
               'freezeshock',
               'iceburn',
               'doomdesire',
               'futuresight ',
               'leafstorm',
               'overheat',
               'dracometeor',
               'psychoboost',
               'superpower',
               'hammerarm'
               ]

    if not MOVES.get(move):
        return 0

    if MOVES.get(move).get('category') == 'Status' or move in blacklist:
        return 0

    res = 1.0

    for user_type in types:
        if MOVES[move]['type'] == user_type:
            res *= 1.5

    if move in badlist:
        res *= 0.5

    res *= MOVES[move]['basePower']
    if type(MOVES[move]['accuracy']) == int:
        res *= (MOVES[move]['accuracy'] / 100.0)
    res *= effectiveness(move, target)

    return res


def load_formats():
    session = FuturesSession()

    def bg_cb(sess, resp):
        resp.data = utils.load_js_obj_literal(resp.text)

    future = session.get('https://raw.githubusercontent.com/Zarel/Pokemon-Showdown/master/data/formats-data.js',
                         background_callback=bg_cb)
    r = future.result()
    return r.data


class Battle:

    def __init__(self, **kwargs):
        # Initialises the battle state
        # Pass in a dict with battle id, and the names of each player
        self.id = kwargs.get('id')

    def add_to_team(self, player, mon):
        moninfo = mon.split(', ')
        print moninfo

        if len(moninfo) == 2:
            moninfo.append('Genderless')

        print 'new moninfo', moninfo
        level = int(moninfo[1][1:]) if moninfo[1][1:] else 100
        mon = Pokemon(species=moninfo[0], level=level, gender=moninfo[2])
        player.team.append(mon)


class Player:

    def __init__(self, **kwargs):
        self.username = kwargs.get('username')
        self.id = kwargs.get('id')
        self.team = []


class Pokemon:

    def __init__(self, **kwargs):
        # You'd pass in a dict containing information on the 'mon here.
        # {'species': 'vaporeon', 'level': 100, 'moves': ['Surf', 'Ice Beam']} ... etc

        # Initialising. They'll be overwritten if they exist
        self.level = 100
        self.ivs = [0] * 6
        self.evs = [0] * 6
        self.nature = 'Hardy'

        for arg in kwargs:
            setattr(self, arg, kwargs.get(arg))

        dex = POKEDEX.get(utils.condense(self.species))
        base_stats = dex.get('baseStats')

        self.types = dex.get('types')

        self.maxhp = statcalc_hp(base_stats['hp'], self.ivs[0], self.evs[0], self.level)
        self.hp = self.maxhp

        self.attack = statcalc('atk', base_stats['atk'], self.ivs[1], self.evs[1], self.level, self.nature)
        self.defense = statcalc('def', base_stats['def'], self.ivs[2], self.evs[2], self.level, self.nature)
        self.spattack = statcalc('spa', base_stats['spa'], self.ivs[3], self.evs[3], self.level, self.nature)
        self.spdefense = statcalc('spd', base_stats['spd'], self.ivs[4], self.evs[4], self.level, self.nature)
        self.speed = statcalc('spe', base_stats['spe'], self.ivs[5], self.evs[5], self.level, self.nature)

        # Volatiles

        self.volatiles = {'boosts': {}, 'volatile_status': None}
        self.status = None

    def update_info(self, attribute, new_value):
        setattr(self, attribute, new_value)

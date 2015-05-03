import re

from triggers.trigger import Trigger
from utils import condense


class StatCalc(Trigger):
    def match(self, info):
        return info['what'][0:6] == '.base:'

    def response(self, info):
        args = info['what'][1:].split()
        if len(args[0]) <= 6:
            return ''
        return [self.calc(args)]

    def calc(self, args):
        o_base = base = 0
        o_iv = iv = 31
        o_ev = ev = 0
        o_level = level = 100.0
        o_modifier = modifier = 1.0
        o_boostmod = boostmod = 1.0
        o_hp = hp = False
        o_naturemod = naturemod = 1.1
        o_plus = plus = o_minus = minus = 0.0
        asbase = False

        stat = 0.0

        rflags = ['base:(\d+)', 'level:(\d+)', '(?:ev|evs):(\d+)', '(?:iv|ivs):(\d+)', '\+(\d+)', '\-(\d+)', 'doubled', 
                  'scarf(ed)?', 'invested', 'uninvested', 'asbase', '(neutral)(nature)?', '(bad)(nature)?', 'hp',
                  'vgc', 'lc']

        flags = []
        for flag in rflags:
            cflag = re.compile(flag)
            flags.append(cflag)

        for arg in args:
            for i in range(len(flags)):
                match_result = re.match(flags[i], arg)
                if match_result:
                    if i == 0:
                        base = float(match_result.groups()[0])
                    elif i == 1:
                        o_level = float(match_result.groups()[0])
                        if not asbase: level = o_level
                    elif i == 2:
                        o_ev = float(match_result.groups()[0])
                        if not asbase: ev = o_ev
                    elif i == 3:
                        o_iv = float(match_result.groups()[0])
                        if not asbase: iv = o_iv
                    elif i == 4:
                        if asbase:
                            o_plus = float(match_result.groups()[0])
                            o_boostmod = (o_plus + 2) / 2
                        else:
                            plus = float(match_result.groups()[0])
                            boostmod = (plus + 2) / 2
                    elif i == 5:
                        if asbase:
                            o_minus = float(match_result.groups()[0])
                            o_boostmod = 2 / (o_minus + 2)
                        else:
                            minus = float(match_result.groups()[0])
                            boostmod = 2 / (minus + 2)
                    elif i == 6:
                        if asbase:
                            o_modifier *= 2
                        else:
                            modifier *= 2
                    elif i == 7:
                        if asbase:
                            o_modifier *= 1.5
                        else:
                            modifier *= 1.5
                    elif i == 8:
                        o_ev = 252
                        if not asbase:
                            ev = 252
                    elif i == 9:
                        o_ev = 0
                        if not asbase:
                            ev = 0
                    elif i == 10:
                        asbase = True
                    elif i == 11:
                        o_naturemod = 1.0
                        if not asbase:
                            naturemod = o_naturemod
                    elif i == 12:
                        o_naturemod = 0.9
                        if not asbase:
                            naturemod = o_naturemod
                    elif i == 13:
                        hp = True
                    elif i == 14:
                        o_level = 50
                        if not asbase:
                            level = 50
                    elif i == 15:
                        o_level = 5
                        if not asbase:
                            level = 5

        if not hp:
            stat = int(int(((iv + 2*base + ev/4) * level/100.0 + 5) * modifier * naturemod) * boostmod)
        else:
            stat = ((iv + 2*base + ev/4) * level/100.0 + 10 + level)

        if asbase:
            stat = int(((float(stat)/o_boostmod/o_naturemod/o_modifier - 5) * 100.0/o_level - o_ev/4 - o_iv) / 2) + 1

        stat = int(stat)

        result = '%s base stat ' % int(base)

        result += self.generate_modstring(int(ev), int(iv), int(plus), int(minus), int(level), modifier, naturemod)

        if asbase:
            result += 'is equivalent to a base stat of %s ' % stat + self.generate_modstring(int(o_ev), int(o_iv),
                                                                                             int(o_plus), int(o_minus),
                                                                                             int(o_level), o_modifier,
                                                                                             o_naturemod)
        else:
            result += 'results in a stat of %s ' % stat

        if result[-1] == ' ':
            result = result[:-1] + '.'

        return result

    def generate_modstring(self, ev, iv, plus, minus, level, modifier, naturemod):
        modstring = ''

        if ev == 252:
            modstring += 'invested '
        else:
            if ev > 0:
                modstring += 'at %s evs ' % ev
            else:
                modstring += 'uninvested '

        if iv != 31:
            modstring += 'with %s ivs ' % iv

        if plus == 0:
            if minus != 0:
                modstring += 'at -%s ' % minus
        else:
            modstring += 'at +%s ' % plus

        if level != 100:
            modstring += 'at level %s ' % level

        if modifier > 1:
            modstring += 'with a modifier of %sx ' % modifier

        if naturemod != 1:
            if naturemod > 1:
                modstring += 'with a boosting nature '
            else:
                modstring += 'with a hindering nature '

        return modstring

def natureboost(nature):
    table = {"Adamant":{"plus":"atk","minus":"spa"},
             "Bashful":{},
             "Bold":{"plus":"def","minus":"atk"},
             "Brave":{"plus":"atk","minus":"spe"},
             "Calm":{"plus":"spd","minus":"atk"},
             "Careful":{"plus":"spd","minus":"spa"},
             "Docile":{},
             "Gentle":{"plus":"spd","minus":"def"},
             "Hardy":{},
             "Hasty":{"plus":"spe","minus":"def"},
             "Impish":{"plus":"def","minus":"spa"},
             "Jolly":{"plus":"spe","minus":"spa"},
             "Lax":{"plus":"def","minus":"spd"},
             "Lonely":{"plus":"atk","minus":"def"},
             "Mild":{"plus":"spa","minus":"def"},
             "Modest":{"plus":"spa","minus":"atk"},
             "Naive":{"plus":"spe","minus":"spd"},
             "Naughty":{"plus":"atk","minus":"spd"},
             "Quiet":{"plus":"spa","minus":"spe"},
             "Quirky":{},
             "Rash":{"plus":"spa","minus":"spd"},
             "Relaxed":{"plus":"def","minus":"spe"},
             "Sassy":{"plus":"spd","minus":"spe"},
             "Serious":{},
             "Timid":{"plus":"spe","minus":"atk"}}
    return table[nature.capitalize()]

def statcalc_HP(base, iv, ev, level):
    return int((((iv + 2*base + (ev/4.0) + 100) * level)/100.0) + 10)
    
def statcalc(stat, base, iv, ev, level, nature):
    boosts = natureboost(nature)
    
    # This feels awful.
    if boosts['plus'] == stat:
        if boosts['minus'] == stat:  # If both
            naturemod = 1.0
        else:                        # If only plus
            naturemod = 1.1
    elif boosts['minus'] == stat:    # If only minus
        naturemod = 0.9
    else:                            # If this stat isn't affected by the nature
        naturemod = 1.0
    
    # Double int() is because the result is rounded down before naturemod is applied, 
    # then rounded down again... thanks, gamefreak!
    return int(int(((((iv + 2*base + (ev/4.0)) * level)/100.0) + 5)) * naturemod)

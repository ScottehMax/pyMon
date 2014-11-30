import json

# Prediction from usage stats

STATS = json.load(open('./BattleStats.json'))

def predict(species):
    # Returns a dict containing the 'most likely' enemy set

    species = species.capitalize()
    prediction = {'species': species}

    found = False

    for mon in STATS['pokemon']:
        if mon['species'] == prediction['species']:
            found = True
            prediction['moves'] = []

            # Items/abilities are only a list if the amount of possibilities is > 1
            if type(mon['items']['item']) is list:
                prediction['item'] = mon['items']['item'][0]['name']
            else:
                prediction['item'] = mon['items']['item']['name']

            if type(mon['abilities']['ability']) is list:
                prediction['ability'] = mon['abilities']['ability'][0]['name']
            else:
                prediction['ability'] = mon['abilities']['ability']['name']

            for move in mon['moves']['move'][0:4]:
                prediction['moves'].append(move['name'])

            prediction['level'] = 100
            prediction['ivs'] = [31] * 6  
            # Note: take into account Hidden Power at some point 
            # (the 1 IV isn't likely to make much difference, but still...)

            natureEVs = mon['spreads']['spread'][0]['name'].split(':')
            prediction['nature'] = natureEVs[0]
            prediction['evs'] = []
            for ev in natureEVs[1].split('/'):
                prediction['evs'].append(int(ev))

    if found:
        return prediction
    else:
        # Nothing found in the specified usage stats for the input
        return None
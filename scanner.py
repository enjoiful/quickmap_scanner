import requests
import json
import time

import time

base_url = 'https://api.quickmap.us/api/pokemons'
slack_url = 'xxxx'

north_beach_locations = {
    'fort_mason': '?filter[where][and][0][latitude][gt]=37.79900966958006&filter[where][and][1][latitude][lt]=37.81697597526245&filter[where][and][2][longitude][gt]=-122.44060371438971&filter[where][and][3][longitude][lt]=-122.41786355606924',
    'lombard_taylor': '?filter[where][and][0][latitude][gt]=37.7931606348948&filter[where][and][1][latitude][lt]=37.81112694057719&filter[where][and][2][longitude][gt]=-122.42583993550126&filter[where][and][3][longitude][lt]=-122.40310157812178',
    'pier_39': '?filter[where][and][0][latitude][gt]=37.80080896799452&filter[where][and][1][latitude][lt]=37.818775273676906&filter[where][and][2][longitude][gt]=-122.42077488683027&filter[where][and][3][longitude][lt]=-122.39803417439362',
    'fishermans_wharf': '?filter[where][and][0][latitude][gt]=37.801775262110986&filter[where][and][1][latitude][lt]=37.81974156779337&filter[where][and][2][longitude][gt]=-122.42961559654464&filter[where][and][3][longitude][lt]=-122.40687458650535',
}

RARE_POKEMON_CONST = [
    {
        3: 'Venusaur'
    }, {
        6: 'Charizard'
    }, {
        9: 'Blastoise'
    }, {
        26: 'Raichu'
    }, {
        45: 'Vileplume'
    }, {
        65: 'Alakazam'
    }, {
        26: 'Victreebel'
    }, {
        80: 'Slowbro'
    }, {
        83: 'Farfetchd'
    }, {
        87: 'Dewgong'
    }, {
        103: 'Exeggutor'
    }, {
        131: 'Lapras'
    }, {
        132: 'Ditto'
    }, {
        134: 'Vaporeon'
    }, {
        135: 'Jolteon'
    }, {
        136: 'Flareon'
    }, {
        143: 'Snorlax'
    }]


def get_pokemon(coordinates_query_params):
    current_date_time = time.strftime("%Y-%m-%d") + 'T' + time.strftime("%H:%M:%S") + '-07:00'
    request_url = base_url + coordinates_query_params + '&filter[where][disappearTime][gt]=' + current_date_time
    response = requests.get(request_url)
    return json.loads(response.text)


def get_spawned_rare_pokemon(pokemon):
    spawned_rare = []
    for mon in pokemon:
        for rare_mon in RARE_POKEMON_CONST:
            if list(rare_mon.keys())[0] == mon['pokemonId']:
                mon['pokemonName'] = list(rare_mon.values())[0]
                spawned_rare.append(mon)
    return spawned_rare


def get_all_spawned_rare_pokemon(locations):
    all_rare_spawned_pokemon = [];
    for location, coordinates in locations.items():
        spawned_pokemon = get_pokemon(coordinates)
        all_rare_spawned_pokemon.extend(get_spawned_rare_pokemon(spawned_pokemon))

    uniq_rare_pokemon = []

    for mon in all_rare_spawned_pokemon:
        uniq_mons = list(filter(lambda uniq_mon: uniq_mon['encounterId'] == mon['encounterId'], uniq_rare_pokemon))
        if len(uniq_mons) == 0:
            uniq_rare_pokemon.append(mon)

    return uniq_rare_pokemon


def send_slack_message(msg):
    print(msg)
    body = {'text': str(msg)}
    requests.post(slack_url, data=json.dumps(body))

while True:

    spawned_rare_pokemon = get_all_spawned_rare_pokemon(north_beach_locations)

    for spawned_rare_mon in spawned_rare_pokemon:
        send_slack_message(str(spawned_rare_mon['pokemonName']) + ' spawned')

    time.sleep(180)
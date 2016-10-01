import requests
import json
from datetime import datetime, timedelta
import time
import csv

base_url = 'https://api.quickmap.us/api/pokemons'
innovint_slack_url = 'y'
slack_url_805 = 'x'

north_beach_locations = {
    'fort_mason': '?filter[where][and][0][latitude][gt]=37.79900966958006&filter[where][and][1][latitude][lt]=37.81697597526245&filter[where][and][2][longitude][gt]=-122.44060371438971&filter[where][and][3][longitude][lt]=-122.41786355606924',
    'lombard_taylor': '?filter[where][and][0][latitude][gt]=37.7931606348948&filter[where][and][1][latitude][lt]=37.81112694057719&filter[where][and][2][longitude][gt]=-122.42583993550126&filter[where][and][3][longitude][lt]=-122.40310157812178',
    'pier_39': '?filter[where][and][0][latitude][gt]=37.80080896799452&filter[where][and][1][latitude][lt]=37.818775273676906&filter[where][and][2][longitude][gt]=-122.42077488683027&filter[where][and][3][longitude][lt]=-122.39803417439362',
    'fishermans_wharf': '?filter[where][and][0][latitude][gt]=37.801775262110986&filter[where][and][1][latitude][lt]=37.81974156779337&filter[where][and][2][longitude][gt]=-122.42961559654464&filter[where][and][3][longitude][lt]=-122.40687458650535',
}

bringas_locations = {
    'work' : '?filter[where][and][0][latitude][gt]=37.756246751553185&filter[where][and][1][latitude][lt]=37.77421305723557&filter[where][and][2][longitude][gt]=-122.43743056003271&filter[where][and][3][longitude][lt]=-122.41470355654447',
    'home': '?filter[where][and][0][latitude][gt]=37.71314852557136&filter[where][and][1][latitude][lt]=37.731114831253755&filter[where][and][2][longitude][gt]=-122.44066405362476&filter[where][and][3][longitude][lt]=-122.41795027993243',
    'park': '?filter[where][and][0][latitude][gt]=37.707309671100425&filter[where][and][1][latitude][lt]=37.72527597678282&filter[where][and][2][longitude][gt]=-122.43122178280666&filter[where][and][3][longitude][lt]=-122.40850979928565'
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
        68: 'Machamp'
    }, {
        71: 'Victreebel'
    }, {
        80: 'Slowbro'
    }, {
        83: 'Farfetchd'
    }, {
        87: 'Dewgong'
    }, {
        89: 'Muk'
    }, {
        94: 'Gengar'
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
    }, {
        149: 'Dragonite'
    },{
        150: 'Mewtwo'
    }]


def get_pokemon(coordinates_query_params):
    current_date_time = time.strftime("%Y-%m-%d") + 'T' + time.strftime("%H:%M:%S") + '-07:00'
    request_url = base_url + coordinates_query_params + '&filter[where][disappearTime][gt]=' + current_date_time
    response = requests.get(request_url)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print('Error with API.')
        return []


def get_spawned_rare_pokemon(pokemon):
    spawned_rare = []
    for mon in pokemon:
        for rare_mon in RARE_POKEMON_CONST:
            if list(rare_mon.keys())[0] == mon['pokemonId']:
                mon['pokemonName'] = list(rare_mon.values())[0]
                mon['disappearTime'] = mon['disappearTime'].replace('.000Z', '')
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


def send_slack_message(msg, slack_url):
    print(msg)
    body = {'text': str(msg)}
    requests.post(slack_url, data=json.dumps(body))


def handle_spawned_rare_pokemeon(spawned_rare_pokemon, slack_url, txt_file_name):
    for spawned_rare_mon in spawned_rare_pokemon:
        uniq_mon = list(filter(lambda saved_mon: saved_mon['encounterId'] == spawned_rare_mon['encounterId'], saved_pokemon))
        if len(uniq_mon) == 0:
            print('Spawned pokemon:', spawned_rare_mon, txt_file_name)
            date_object = datetime.strptime(spawned_rare_mon['disappearTime'], '%Y-%m-%dT%H:%M:%S')
            date_object = date_object + timedelta(hours=-7)
            send_slack_message(str(spawned_rare_mon['pokemonName']) + ' spawned' + '\nhttps://quickmap.us/#' + str(spawned_rare_mon['latitude']) + ',' + str(spawned_rare_mon['longitude']) + '\nDisappears at ' + date_object.strftime('%-I:%M %p'), slack_url)
            saved_pokemon.append(spawned_rare_mon)

            data = [spawned_rare_mon['pokemonName'],spawned_rare_mon['pokemonId'], spawned_rare_mon['latitude'], spawned_rare_mon['longitude'], spawned_rare_mon['spawnpointId'], spawned_rare_mon['encounterId'], spawned_rare_mon['disappearTime'] ]
            with open(txt_file_name, 'a') as f:
                writer = csv.writer(f, delimiter=',')
                writer.writerow(data)


saved_pokemon = []


while True:

    north_beach_spawned_rare_pokemon = get_all_spawned_rare_pokemon(north_beach_locations)
    handle_spawned_rare_pokemeon(north_beach_spawned_rare_pokemon, innovint_slack_url, 'north_beach_pokemon_spawn.txt')

    bringas_spawned_rare_pokemon = get_all_spawned_rare_pokemon(bringas_locations)
    handle_spawned_rare_pokemeon(bringas_spawned_rare_pokemon, slack_url_805, 'bringas_pokemon_spawn.txt')

    time.sleep(100)
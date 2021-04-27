# Importando libs importantes
import numpy as np
import pandas as pd
from roleidentification import get_roles

def players_perfomance_at_n(timeline, n = 10):
    '''
     Essa função toma como parâmetro obrigatório um objeto timeline (MatchTimelineDto) e
     como parâmetro não obrigatório n (int = 10). 

     O objeto MatchTimelineDto é um Json definido pela RiotGames com diversas informações 
     de uma partida de acordo com o tempo - stats dos players, eventos principais e etc.

     Documentação do objeto: https://developer.riotgames.com/apis#match-v4/GET_getMatchTimeline

     A função retorna um DataFrame com a perfomance dos players no frame n do jogo (frame = aprox min).
    '''
    
    # Selecionando apenas os stats de interesse
    keys = ['participantId', 'totalGold', 'xp', 'minionsKilled', 'jungleMinionsKilled']

    champs_at_10 = pd.DataFrame(columns = keys)
    
    # Iterando por cada um dos players
    for i in range(1, 11):

        # Pegando os stats
        t = timeline['frames'][n]['participantFrames'][f'{i}']  
        main_perfomance = {k: t[k] for k in keys}
        champs_at_10 = champs_at_10.append(main_perfomance, ignore_index = True)
    
    return champs_at_10

def events_at_n(timeline, n = 11):
    '''
     Essa função toma como parâmetro obrigatório um objeto timeline (MatchTimelineDto) e
     como parâmetro não obrigatório n (int = 11). 

     O objeto MatchTimelineDto é um Json definido pela RiotGames com diversas informações 
     de uma partida de acordo com o tempo - stats dos players, eventos principais e etc.

     Documentação do objeto: https://developer.riotgames.com/apis#match-v4/GET_getMatchTimeline

     A função percorre os primeiros n frames do jogo (frame = aprox min), contando os eventos de
     interesse definidos anteriormente e adicionando a contagem a um DataFrame em que cada observação
     é um player do jogo e cada variável é um tipo de evento.

     A função retorna um DataFrame contendo os eventos que ocorreram por player.
    '''

    # Selecionando eventos de interresse
    columns = ['participantId', 'wardsPlaced', 'wardsKilled', 'nKills', 'nDeaths', 'nAssists', 'firstBlood', 'firstTower',
               'midTowersDestroyed', 'botTowersDestroyed', 'topTowersDestroyed', 'inhibitorsDestroyed', 'fireDragonsDestroyed',
               'airDragonsDestroyed', 'waterDragonsDestroyed', 'earthDragonsDestroyed', 'riftHeraldDestroyed']

    events_by_player = pd.DataFrame(columns = columns)
    events_by_player['participantId'] = range(1,11)
    events_by_player = events_by_player.fillna(0).set_index('participantId')

    # Definindo alguns dicionários pra facilitar o input no DataFrame
    dragon_dict = {'FIRE_DRAGON':'fireDragonsDestroyed',
                  'WATER_DRAGON':'waterDragonsDestroyed',
                  'EARTH_DRAGON':'earthDragonsDestroyed',
                  'AIR_DRAGON':'airDragonsDestroyed'}

    tower_dict = {'BOT_LANE': 'botTowersDestroyed',
                  'TOP_LANE': 'topTowersDestroyed',
                  'MID_LANE': 'midTowersDestroyed'}

    # Iniando a contagem do First Blood e First Tower, eventos que não aparecem especificamente no objeto
    first_blood = 0
    first_tower = 0
    
    # Itera através dos Frames
    for i in range(1, n):
        events = timeline['frames'][i]['events']
        
        # De acordo com o evento, conta o número de vezes que o evento aconteceu
        for event in events:
            if event['type'] == 'WARD_PLACED':
                if event['wardType'] !=  'UNDEFINED':
                    events_by_player.loc[event['creatorId'], 'wardsPlaced'] += 1

            if event['type'] == 'WARD_KILL':
                if event['wardType'] !=  'UNDEFINED':
                    events_by_player.loc[event['killerId'], 'wardsKilled'] += 1

            # Evento CHAMPION_KILL gera 3 variáveis > o matador, o morto e quem ajudou a matar
            if event['type'] == 'CHAMPION_KILL':
                if event['killerId'] != 0:

                    if first_blood == 0:
                        events_by_player.loc[event['killerId'], 'firstBlood'] += 1
                        first_blood +=1 

                    events_by_player.loc[event['killerId'], 'nKills'] += 1
                    events_by_player.loc[event['victimId'], 'nDeaths'] += 1

                    # Pode ser mais de um assistente
                    for assist in event['assistingParticipantIds']:
                        events_by_player.loc[assist, 'nAssists'] += 1

            # Eventos globais (morte de monstros elite, torres) afetam todos os players do time
            if event['type'] == 'ELITE_MONSTER_KILL':
                if event['monsterType'] == 'DRAGON':
                    if event['killerId'] > 5:
                        events_by_player.loc[6:, dragon_dict[event['monsterSubType']]] += 1
                    else:
                        events_by_player.loc[1:5, dragon_dict[event['monsterSubType']]] += 1

                if event['monsterType'] == 'RIFTHERALD':
                    if event['killerId'] > 5:
                        events_by_player.loc[6:, 'riftHeraldDestroyed'] += 1
                    else:
                        events_by_player.loc[1:5, 'riftHeraldDestroyed'] += 1

            if event['type'] == 'BUILDING_KILL':
                if event['buildingType'] == 'TOWER_BUILDING':

                    if event['teamId'] == 100:
                        if first_tower == 0:
                            events_by_player.loc[6:, 'firstTower'] += 1
                            first_tower += 1

                        events_by_player.loc[6:, tower_dict[event['laneType']]] += 1
                    else:
                        if first_tower == 0:
                            events_by_player.loc[1:5, 'firstTower'] += 1
                            first_tower += 1

                        events_by_player.loc[1:5, tower_dict[event['laneType']]] += 1

                if event['buildingType'] == 'INHIBITOR_BUILDING': 

                    if event['killerId'] > 5:
                        events_by_player.loc[6:, 'inhibitorsDestroyed'] += 1
                    else:
                        events_by_player.loc[1:5, 'inhibitorsDestroyed'] += 1

    return events_by_player.reset_index()

def get_participant_game_info(game_info):
    '''
     Essa função toma como parâmetro obrigatório um objeto game_info (MatchDto).

     O objeto MatchDto é um Json definido pela RiotGames com diversas informações 
     de gerais de uma partida (players, champions, gameID, fila e etc)

     Documentação do objeto: https://developer.riotgames.com/apis#match-v4/GET_getMatch

     A função retorna um DataFrame contendo os players como observações e a lane, a role,
     o time, o champion e se saiu vitorioso ou não como variáveis.
    '''

    # Selecionar informações relevantes
    keys = ['participantId', 'teamId', 'championId', 'timeline']

    participant_game_info = pd.DataFrame(columns = keys)

    # Definir o time vencedor
    if game_info['teams'][0]['win'] == 'Win':
        winner = game_info['teams'][0]['teamId']

    else:
        winner = game_info['teams'][1]['teamId']

    # Adicionar as informações sobre os players e o game
    for i in range(0, 10):
        gip = game_info['participants'][i]  
        main_info = {k: gip[k] for k in keys}
        participant_game_info = participant_game_info.append(main_info, ignore_index = True)

    participant_game_info['lane'] = [participant_game_info['timeline'][i]['lane'] for i in range(len(participant_game_info))]
    participant_game_info['role'] = [participant_game_info['timeline'][i]['role'] for i in range(len(participant_game_info))]
    participant_game_info['isWinner'] = [True if team == winner else False for team in participant_game_info['teamId']]

    # Dropar a coluna timeline após tirar as informações necessárias dela
    participant_game_info = participant_game_info.drop('timeline', axis = 1)
    
    return participant_game_info

def create_match_row(players_perfomance_at_10, players_events_at_10, participant_game_info, champion_roles, match_id):
    '''
     Essa função toma como parâmetro obrigatório 3 DataFrames, o match_id (int) e o objeto champion_roles.

     Ela une todos as informações, eventos e estatísticas de uma partida reunidas utilizando as funçoes desse arquivo em
     apenas uma linha, transformando a partida em uma única observação. 
    '''
    
    # Merge nos DataFrames de Entrada
    full_players_info = participant_game_info.merge(players_perfomance_at_10, on = 'participantId')
    full_players_info = full_players_info.merge(players_events_at_10, on = 'participantId' )
    
    # Dicionário definindo a função agregadora de acordo com a estatística
    agg_func = {
            'totalGold': 'sum',
            'isWinner': 'max',
            'xp':'sum',
            'minionsKilled': 'sum',
            'jungleMinionsKilled':'sum',
            'wardsPlaced':'sum',
            'wardsKilled':'sum',
            'nKills':'sum',
            'nDeaths':'sum',
            'nAssists':'sum',
            'firstBlood':'max',
            'firstTower':'max',
            'midTowersDestroyed':'max',
            'botTowersDestroyed':'max',
            'topTowersDestroyed':'max',
            'inhibitorsDestroyed':'max',
            'fireDragonsDestroyed':'max',
            'airDragonsDestroyed':'max',
            'waterDragonsDestroyed':'max',
            'earthDragonsDestroyed':'max',
            'riftHeraldDestroyed':'max'
            }

    # Unir os players por time (DataFrame dos times > 2 observações)
    grouped_by_team = full_players_info.groupby('teamId').agg(agg_func).sort_index()

    # Utilizando o objeto champion_roles, definir a role de cada campeão e adiciono ao DataFrame dos times
    champions_100 =  full_players_info[full_players_info.teamId == 100].championId.tolist()
    roles_100 = get_roles(champion_roles, champions_100)

    champions_200 =  full_players_info[full_players_info.teamId == 200].championId.tolist()
    roles_200 = get_roles(champion_roles, champions_200)

    for k, v in roles_100.items():
        pairs = [v, roles_200[k]]
        grouped_by_team[k] = pairs

    # Desenrolar o DataFrame dos times e alterar a nomenclatura das colunas pra facilitar a análise 
    match_row = grouped_by_team.unstack().to_frame().T
    match_row.columns = match_row.columns.map('{0[0]}_{0[1]}'.format)
    match_row.columns = match_row.columns.str.replace('_100', '_red')
    match_row.columns = match_row.columns.str.replace('_200', '_blue')

    # Adicionar o match_id ao DataFrame pra facilitar o controle de partidas 
    match_row['gameID'] = match_id

    return match_row[['gameID', 'isWinner_blue', 'totalGold_red', 'xp_red', 'nKills_red', 'nDeaths_red', 'nAssists_red', 'minionsKilled_red', 'jungleMinionsKilled_red', 'wardsPlaced_red', 'wardsKilled_red',
                     'firstBlood_red', 'firstTower_red', 'midTowersDestroyed_red', 'botTowersDestroyed_red', 'topTowersDestroyed_red', 'inhibitorsDestroyed_red', 'fireDragonsDestroyed_red',
                     'airDragonsDestroyed_red','waterDragonsDestroyed_red', 'earthDragonsDestroyed_red', 'riftHeraldDestroyed_red', 'TOP_red', 'JUNGLE_red', 'MIDDLE_red', 'BOTTOM_red', 'UTILITY_red',
                     'totalGold_blue', 'xp_blue', 'nKills_blue', 'nDeaths_blue', 'nAssists_blue', 'minionsKilled_blue', 'jungleMinionsKilled_blue', 'wardsPlaced_blue', 'wardsKilled_blue',
                     'firstBlood_blue', 'firstTower_blue', 'midTowersDestroyed_blue', 'botTowersDestroyed_blue', 'topTowersDestroyed_blue', 'inhibitorsDestroyed_blue', 'fireDragonsDestroyed_blue',
                     'airDragonsDestroyed_blue', 'waterDragonsDestroyed_blue','earthDragonsDestroyed_blue','riftHeraldDestroyed_blue', 'TOP_blue', 'JUNGLE_blue', 'MIDDLE_blue', 'BOTTOM_blue', 'UTILITY_blue'
                    ]]


def create_matchlist_from_summoner(summoner_data, m, all_matches, match_id_list, champion_roles, region = 'br1'):
    '''
    ## ATENÇÃO - FUNÇÃO NÃO FUNCIONA ADEQUEADAMENTE DEVIDO AOS ERROS GERADOS PELA API - NÃO UTILIZAR PARA PROJETOS GRANDES (+1K) ##

     Essa função toma como parâmetros obrigatórios 1 objeto e 1 classe para utilizar na API da Riot Games:

     summoner_data: JSON com informações sobre o player (documentação: https://developer.riotgames.com/apis#summoner-v4/GET_getBySummonerName)
     m: Classe para acessar JSONs da partida (documentação: https://developer.riotgames.com/apis#match-v4)

     Além disso, também recebe uma lista contendo partidas já salvas, um DataFrame contendo as partidas e o objeto champion_roles.

     A função procura pela lista de partidas de um player (summoner_data), coleta as informações, eventos e estatísticas 
     relevantes sobre a partida (utilizando as funções acima definidas) e adiciona ao DataFrame all_matches.

     No final, retorna o DataFrame com as partidas adicionadas.
    '''

    # Buscar dados de summoner do player e procurar as partidas desde 12/Fev
    match_list = m.matchlist_by_account(**{'region': region,
                              'encrypted_account_id': summoner_data['accountId'],
                              'begin_time':1613171498})

    n_matches = len(match_list['matches'])

    for n_match in range(n_matches):

        match_id = match_list['matches'][n_match]['gameId']

        # id 420 - Partidas SoloQ Ranked
        if match_list['matches'][n_match]['queue'] == 420:

            # Como os players jogam um contra o outro e são do mesmo nível, procuro ver se a partida já não existe na base
            if match_id not in match_id_list:

                match_id_list.append(match_id)

                game_info = m.by_id('br1', match_id)
                timeline = m.timeline_by_match(region = region, match_id = match_id)

                # Apenas partidas maiores que 10min
                if len(timeline['frames']) > 10:

                    players_perfomance_at_10 = players_perfomance_at_n(timeline)
                    players_events_at_10 = events_at_n(timeline)
                    participant_game_info = get_participant_game_info(game_info)

                    match_row = create_match_row(players_perfomance_at_10, players_events_at_10, participant_game_info, champion_roles, match_id)

                    all_matches = all_matches.append(match_row)
    
    return all_matches

def get_top_players_users(leagues, region = 'br1'):
    '''
     Essa função toma como parâmetro obrigatório uma classe leagues (LeagueApiV4).
     
     Documentação da classe: https://developer.riotgames.com/api-methods/#league-v4/

     Utilizando a leagues, a função acessa o nome dos players de maior ranking do jogo,
     nesse caso, a partir do Diamante 1. Por padrão, a região foi definida como a brasileira.

     A função retorna uma lista contendo o nome dos players
    '''

    # CHALLENGER
    challenger_league = leagues.challenger_by_queue(region, queue = 'RANKED_SOLO_5x5')
    challenger_list = []

    for summoner in challenger_league['entries']:
        challenger_list.append(summoner['summonerName'])

    # GRÃO MESTRE
    grandmaster_league = leagues.grandmaster_by_queue(region, queue = 'RANKED_SOLO_5x5')
    grandmaster_list = []

    for summoner in grandmaster_league['entries']:
        grandmaster_list.append(summoner['summonerName'])

    # MESTRE
    master_league = leagues.masters_by_queue(region, queue = 'RANKED_SOLO_5x5')
    master_list = []

    for summoner in master_league['entries']:
        master_list.append(summoner['summonerName'])

    # DIAMANTE I
    diamondi_league = leagues.entries(region, queue = 'RANKED_SOLO_5x5', tier = 'DIAMOND', division = 'I')
    diamondi_list = []

    for summoner in diamondi_league:
        diamondi_list.append(summoner['summonerName'])
    
    allsummoners = challenger_list + grandmaster_list + master_list + diamondi_list
    
    return allsummoners

def get_champions_name(id):
    '''
    Função simples para armazenar um dicionário.
    Recebe o id e retorna o nome do campeão de acordo com o id.
    '''
    all_champion_id = {
        1: "Annie",
        2: "Olaf",
        3: "Galio",
        4: "TwistedFate",
        5: "XinZhao",
        6: "Urgot",
        7: "LeBlanc",
        8: "Vladimir",
        9: "Fiddlesticks",
        10: "Kayle",
        11: "Master Yi",
        12: "Alistar",
        13: "Ryze",
        14: "Sion",
        15: "Sivir",
        16: "Soraka",
        17: "Teemo",
        18: "Tristana",
        19: "Warwick",
        20: "Nunu",
        21: "MissFortune",
        22: "Ashe",
        23: "Tryndamere",
        24: "Jax",
        25: "Morgana",
        26: "Zilean",
        27: "Singed",
        28: "Evelynn",
        29: "Twitch",
        30: "Karthus",
        31: "Cho'Gath",
        32: "Amumu",
        33: "Rammus",
        34: "Anivia",
        35: "Shaco",
        36: "Dr.Mundo",
        37: "Sona",
        38: "Kassadin",
        39: "Irelia",
        40: "Janna",
        41: "Gangplank",
        42: "Corki",
        43: "Karma",
        44: "Taric",
        45: "Veigar",
        48: "Trundle",
        50: "Swain",
        51: "Caitlyn",
        53: "Blitzcrank",
        54: "Malphite",
        55: "Katarina",
        56: "Nocturne",
        57: "Maokai",
        58: "Renekton",
        59: "JarvanIV",
        60: "Elise",
        61: "Orianna",
        62: "Wukong",
        63: "Brand",
        64: "LeeSin",
        67: "Vayne",
        68: "Rumble",
        69: "Cassiopeia",
        72: "Skarner",
        74: "Heimerdinger",
        75: "Nasus",
        76: "Nidalee",
        77: "Udyr",
        78: "Poppy",
        79: "Gragas",
        80: "Pantheon",
        81: "Ezreal",
        82: "Mordekaiser",
        83: "Yorick",
        84: "Akali",
        85: "Kennen",
        86: "Garen",
        89: "Leona",
        90: "Malzahar",
        91: "Talon",
        92: "Riven",
        96: "Kog'Maw",
        98: "Shen",
        99: "Lux",
        101: "Xerath",
        102: "Shyvana",
        103: "Ahri",
        104: "Graves",
        105: "Fizz",
        106: "Volibear",
        107: "Rengar",
        110: "Varus",
        111: "Nautilus",
        112: "Viktor",
        113: "Sejuani",
        114: "Fiora",
        115: "Ziggs",
        117: "Lulu",
        119: "Draven",
        120: "Hecarim",
        121: "Kha'Zix",
        122: "Darius",
        126: "Jayce",
        127: "Lissandra",
        131: "Diana",
        133: "Quinn",
        134: "Syndra",
        136: "AurelionSol",
        141: "Kayn",
        142: "Zoe",
        143: "Zyra",
        145: "Kai'sa",
        147: "Seraphine",
        150: "Gnar",
        154: "Zac",
        157: "Yasuo",
        161: "Vel'Koz",
        163: "Taliyah",
        164: "Camille",
        201: "Braum",
        202: "Jhin",
        203: "Kindred",
        222: "Jinx",
        223: "TahmKench",
        234: "Viego",
        235: "Senna",
        236: "Lucian",
        238: "Zed",
        240: "Kled",
        245: "Ekko",
        246: "Qiyana",
        254: "Vi",
        266: "Aatrox",
        267: "Nami",
        268: "Azir",
        350: "Yuumi",
        360: "Samira",
        412: "Thresh",
        420: "Illaoi",
        421: "Rek'Sai",
        427: "Ivern",
        429: "Kalista",
        432: "Bard",
        497: "Rakan",
        498: "Xayah",
        516: "Ornn",
        517: "Sylas",
        523: "Aphelios",
        518: "Neeko",
        526: "Rell",
        555: "Pyke",
        777: "Yone",
        875: "Sett",
        876: "Lillia",
    }
    return all_champion_id.get(id)

def get_champions_role(id):
    '''
    Função simples para armazenar um dicionário.
    Recebe o id e retorna o nome do campeão de acordo com o id.
    '''
    all_champion_id = {
        1: "Burst",
        2: "Diver",
        3: "Warden",
        4: "Burst",
        5: "Diver",
        6: "Juggernaut",
        7: "Burst",
        8: "BattleMage",
        9: "Specialist",
        10: "Specialist",
        11: "Skirmisher",
        12: "Vanguard",
        13: "BattleMage",
        14: "Vanguard",
        15: "Marksman",
        16: "Enchanter",
        17: "Specialist",
        18: "Marksman",
        19: "Diver",
        20: "Vanguard",
        21: "Marksman",
        22: "Marksman",
        23: "Skirmisher",
        24: "Skirmisher",
        25: "Catcher",
        26: "Specialist",
        27: "Specialist",
        28: "Assassin",
        29: "Marksman",
        30: "BattleMage",
        31: "Specialist",
        32: "Vanguard",
        33: "Vanguard",
        34: "BattleMage",
        35: "Assassin",
        36: "Juggernaut",
        37: "Enchanter",
        38: "Assassin",
        39: "Diver",
        40: "Enchanter",
        41: "Specialist",
        42: "Marksman",
        43: "Enchanter",
        44: "Warden",
        45: "Burst",
        48: "Juggernaut",
        50: "BattleMage",
        51: "Marksman",
        53: "Catcher",
        54: "Vanguard",
        55: "Assassin",
        56: "Assassin",
        57: "Vanguard",
        58: "Diver",
        59: "Diver",
        60: "Diver",
        61: "Burst",
        62: "Diver",
        63: "Burst",
        64: "Diver",
        67: "Marksman",
        68: "BattleMage",
        69: "BattleMage",
        72: "Diver",
        74: "Specialist",
        75: "Juggernaut",
        76: "Specialist",
        77: "Juggernaut",
        78: "Warden",
        79: "Vanguard",
        80: "Diver",
        81: "Marksman",
        82: "BattleMage",
        83: "Juggernaut",
        84: "Assassin",
        85: "BattleMage",
        86: "Juggernaut",
        89: "Vanguard",
        90: "BattleMage",
        91: "Assassin",
        92: "Skirmisher",
        96: "Marksman",
        98: "Warden",
        99: "Burst",
        101: "Artillery",
        102: "Juggernaut",
        103: "Burst",
        104: "Specialist",
        105: "Assassin",
        106: "Juggernaut",
        107: "Assassin",
        110: "Marksman",
        111: "Vanguard",
        112: "BattleMage",
        113: "Vanguard",
        114: "Skirmisher",
        115: "Artillery",
        117: "Enchanter",
        119: "Marksman",
        120: "Diver",
        121: "Assassin",
        122: "Juggernaut",
        126: "Artillery",
        127: "Burst",
        131: "Assassin",
        133: "Specialist",
        134: "Burst",
        136: "BattleMage",
        141: "Skirmisher",
        142: "Burst",
        143: "Catcher",
        145: "Marksman",
        147: "Enchanter",
        150: "Specialist",
        154: "Vanguard",
        157: "Skirmisher",
        161: "Artillery",
        163: "BattleMage",
        164: "Diver",
        201: "Warden",
        202: "Marksman",
        203: "Marksman",
        222: "Marksman",
        223: "Warden",
        234: "Skirmisher",
        235: "Marksman",
        236: "Marksman",
        238: "Assassin",
        240: "Skirmisher",
        245: "Assassin",
        246: "Assassin",
        254: "Diver",
        266: "Juggernaut",
        267: "Enchanter",
        268: "Specialist",
        350: "Enchanter",
        360: "Marksman",
        412: "Catcher",
        420: "Juggernaut",
        421: "Diver",
        427: "Catcher",
        429: "Marksman",
        432: "Catcher",
        497: "Catcher",
        498: "Marksman",
        516: "Vanguard",
        517: "Skirmisher",
        523: "Marksman",
        518: "Burst",
        526: "Vanguard",
        555: "Assassin",
        777: "Skirmisher",
        875: "Juggernaut",
        876: "Skirmisher",
    }
    return all_champion_id.get(id)



def xp_to_level(xp):
    '''
     Função simples para binnar o xp de acordo com o level.
    '''
    if xp < 1720:
        return 4.0
    elif xp < 2400:
        return 5.0
    elif xp < 3180:
        return 6.0
    elif xp < 4060:
        return 7.0
    elif xp < 5040:
        return 8.0
    elif xp < 6120:
        return 9.0
    elif xp < 7300:
        return 10.0
    elif xp < 8580:
        return 11.0
    else:
        return 12.0
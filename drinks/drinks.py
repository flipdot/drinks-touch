# coding=utf-8

drinks = {
    'E4029764001807': {
        'name': 'Club-Mate',
        'size': 0.5,
        'tags': ['mate']
    },
    'E4002846034504': {
        'name': 'MIO-MIO-MATE',
        'size': 0.5,
        'tags': ['mate']
    },
    'E4260031874278': {
        'name': 'flora power',
        'size': 0.33,
        'tags': ['mate']
    },
    'E4069800005871': {
        'name': 'Nörten-Hardenberger',
        'size': 0.33,
        'tags': ['beer']
    },
    'E4008948027000': {
        'name': 'JEVER',
        'size': 0.5,
        'tags': ['beer']
    },
    'E4003892009010': {
        'name': 'Eschweger',
        'size': 0.5,
        'tags': ['beer']
    },
    'E4003892009218': {
        'name': 'Eschweger',
        'size': 0.33,
        'tags': ['beer']
    },
    'E41001318': {
        'name': 'BECKS',
        'size': 0.5,
        'tags': ['beer']
    },
}

def get_by_ean(ean):
    drink = drinks.get(ean)
    if not drink:
        drink = {
            'name': 'Unbekannt ('+ean+')',
            'size': 0,
            'tags': ['unkown']
        }

    return drink
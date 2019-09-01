from pathlib import Path

from . import constants


def find_cp_in_tags(tags):
    return tags.get('addr:postcode') or tags.get('postal_code') or ''


def get_nb_parts(s):
    return len(s.split())


def get_part_debut(s,nb_parts):
    resp = ''
    if get_nb_parts(s) > nb_parts:
        resp = ' '.join(s.split()[0:nb_parts])
    return resp


def is_valid_housenumber(hsnr):
    return len(hsnr) <= 11

def is_valid_dept(dept):
    return dept in constants.DEPARTEMENTS

def get_code_dept_from_insee(code_insee):
    code_dept = code_insee[0:2]
    if code_dept == '97':
        code_dept = code_insee[0:3]
    return code_dept

def get_sql_like_dept_string(dept):
    return (dept+'___')[0:5]

def normalize(s):
    s = s.upper()                # tout en majuscules
    s = s.split(' (')[0]        # parenthèses : on coupe avant
    s = s.replace('-',' ')        # separateur espace
    s = s.replace('\'',' ')        # separateur espace
    s = s.replace('’',' ')        # separateur espace
    s = s.replace('/',' ')        # separateur espace
    s = s.replace(':',' ')        # separateur deux points
    s = ' '.join(s.split())        # separateur : 1 espace

    for l in iter(constants.LETTRE_A_LETTRE):
        for ll in constants.LETTRE_A_LETTRE[l]:
            s = s.replace(ll,l)

# type de voie
    abrev_trouvee = False
    p = 5
    while (not abrev_trouvee) and p > -1:
        p-= 1
        if get_part_debut(s,p) in constants.ABREV_TYPE_VOIE:
            s = replace_type_voie(s,p)
            abrev_trouvee = True
# ordinal
    s = s.replace(' EME ','EME ')
    s = s.replace(' 1ERE',' PREMIERE')
    s = s.replace(' 1ER',' PREMIER')

# chiffres
    for c in constants.CHIFFRES:
        s = s.replace(c[0],c[1])

# titres, etc.
    for r in constants.EXPAND_NOMS:
        s = s.replace(' '+r[0]+' ',' '+r[1]+' ')
        if s[-len(r[0]):] == r[0]:
            s = s.replace(' '+r[0],' '+r[1])
    for r in constants.EXPAND_TITRES:
        s = s.replace(' '+r[0]+' ',' '+r[1]+' ')
        if s[-len(r[0]):] == r[0]:
            s = s.replace(' '+r[0],' '+r[1])
    for r in constants.ABREV_TITRES:
        s = s.replace(' '+r[0]+' ',' '+r[1]+' ')
        if s[-len(r[0]):] == r[0]:
            s = s.replace(' '+r[0],' '+r[1])

# articles
    for c in constants.MOT_A_BLANC:
        s = s.replace(' '+c+' ',' ')

# chiffres romains
    sp = s.split()

    if len(sp)>0 and sp[-1] in constants.CHIFFRES_ROMAINS:
        sp[-1] = constants.CHIFFRES_ROMAINS[sp[-1]]
        s = ' '.join(sp)

# substitution complete
    if s in constants.SUBSTITUTION_COMPLETE:
        s = constants.SUBSTITUTION_COMPLETE[s]
    return s[0:30]


def replace_type_voie(s,nb):
    sp = s.split()
    spd = ' '.join(sp[0:nb])
    spf = ' '.join(sp[nb:len(sp)])
    s = constants.ABREV_TYPE_VOIE[spd]+' '+spf
    return s


def is_valid_fantoir(f, insee):
    return (len(f) == 10 and f[0:5] == insee);

def display_insee_commune(code_insee, nom_commune):
    print(f"{code_insee} - {nom_commune}")
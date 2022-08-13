def get_code_dept_from_insee(code_insee):
    return code_insee[0:3] if code_insee[0:2] == '97' else code_insee[0:2]

def get_code_dir_dict():
    with open('./data/code_dir.json') as f:
        return json.loads(f.read())
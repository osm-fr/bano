from . import db


def get_insee_name_list_by_dept(dept):
    with db.bano.cursor() as conn :
        conn.execute(f"SELECT insee_com, nom_com FROM code_cadastre WHERE dept = '{dept}' ORDER BY 1;")
        return conn.fetchall()

from flask import session

def gen_username_em(db, names, lastnames):
    try:
        cursor = db.cursor()
        sql = f"SELECT email_em FROM employee"
        cursor.execute(sql)
        usernames = cursor.fetchall()

        first_name = names.split[0].lower()
        first_lastname = lastnames.split[0].lower()

        username_base = f"{first_name}.{first_lastname}"

        usernames_clean = [row[0] for row in usernames if row[0] is not None]
        i = 0
        for username in usernames_clean:
            if username == f"{username_base}@telcomep.ec":
                while f"{username_base}{i:02}" in usernames_clean:
                    i += 1
            pass
        return f"{username_base}{i:02}@telcomep.ec"

    except Exception as e:
        raise print(e)

def dataLoginSesion():
    inforLogin = {
        'dni_em' : session['dni_em'],
        'name_em' : session['name_em'],
        'lastna_em' : session['lastna_em'],
    }
    return inforLogin

def info_perfil_session(db):
    try:
        cursor = db.cursor()
        sql = f"SELECT dni_em, name_em, lastna_em, email_em, cellphone FROM employee WHERE dni_em = {session['dni_em']}"
        cursor.execute(sql)
        info_perfil = cursor.fetchall()
        return info_perfil
    except Exception as e:
        print(f"Error en info_perfil_session : {e}")
        return []
    
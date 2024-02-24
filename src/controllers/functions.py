from flask import session

def gen_username_em(db, names, lastnames):
    try:
        cursor = db.cursor()
        sql = f"SELECT username_employee FROM employee"
        cursor.execute(sql)
        usernames = cursor.fetchall()

        first_na = names.split()
        first_last = lastnames.split()

        first_name = first_na[0]
        first_lastname = first_last[0]

        username_base = f"{first_name}.{first_lastname}"

        usernames_clean = [row[0] for row in usernames if row[0] is not None]

        if username_base not in usernames_clean:
            return f"{username_base}@telcomep.ec"
        else:
            i = 0
            while f"{username_base}{i:02}" in usernames_clean:
                i += 1
            return f"{username_base}{i:02}@telcomep.ec"

    except Exception as e:
        print(e)

def dataLoginSession():
    inforLogin = {
        'dni_employee' : session['dni_employee'],
        'name_employee' : session['name_employee'],
        'lastna_employee' : session['lastna_employee'],
        'email_employee' : session['email_employee'],
        'username_employee' : session['username_employee'],
        'cellphone_employee' : session['cellphone_employee'],
    }
    return inforLogin

def info_perfil_session(db):
    try:
        cursor = db.cursor()
        sql = f"SELECT dni_employee, name_employee, lastna_employee, email_employee, username_employee, cellphone_employee FROM employee WHERE dni_employee = '{session['dni_employee']}'"
        cursor.execute(sql)
        info_perfil = cursor.fetchall()
        return info_perfil
    except Exception as e:
        print(f"Error en info_perfil_session : {e}")
        return []
    
from flask import session

def gen_username_em(db, names, lastnames):
    try:
        cursor = db.cursor()
        sql = f"""SELECT username_employee FROM employee
                ORDER BY username_employee"""
        cursor.execute(sql)
        usernames = cursor.fetchall()

        first_na = names.split()
        first_last = lastnames.split()

        first_name = first_na[0]
        first_lastname = first_last[0]

        username_base = f"{first_name}.{first_lastname}"

        usernames_list = [row[0] for row in usernames if row[0] is not None]
        usernames_clean = list(filter(lambda x: x != '', usernames_list))

        print(usernames_clean)

        i = 1
        if f"{username_base}@telcomep.ec" not in usernames_clean:
            return f"{username_base}@telcomep.ec"
        else:
            while f"{username_base}{i:02}@telcomep.ec" in usernames_clean and f"{username_base}@telcomep.ec" in usernames_clean:
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
        cursor.close()
        return info_perfil
    except Exception as e:
        print(f"Error en info_perfil_session : {e}")
        return []
    
def show_works(db, dni_employee):
    try:
        cursor = db.cursor()
        sql = f"""SELECT co.cod_order, c.dni_costumer, CONCAT(SUBSTRING(c.name_costumer, 1, CHARINDEX(' ', name_costumer) - 1), ' ', SUBSTRING(lastna_costumer, 1, CHARINDEX(' ', lastna_costumer) - 1)) AS 'name_customer', CONCAT(st.name_ser, ' ', tst.type_name_ser) as 'service_name', c.adress_costumer, o.date_expected_install
                    FROM costumer_order co join orders o
                    ON co.cod_order = o.cod_order
                    join costumer c
                    ON c.dni_costumer = o.dni_costumer
                    join type_services_telcom tst
                    ON o.code_type_ser = tst.code_type_ser
                    join services_telcom st
                    ON st.code_ser = tst.code_ser
                    WHERE co.dni_employee = '{dni_employee}' AND co.check_install = 0
                    ORDER BY o.date_expected_install ASC"""
        cursor.execute(sql)
        installations = cursor.fetchall()
        cursor.close()
        return installations
    except Exception as e:
        print(f"Error en show_works : {e}")
        return []

def show_services(db):
    try:
        cursor = db.cursor()
        sql1 = f"""SELECT CONCAT(st.name_ser, ' ', tst.type_name_ser) as 'Service Name'
                FROM type_services_telcom tst JOIN services_telcom st
                ON tst.code_ser = st.code_ser
                """
        cursor.execute(sql1)
        services = cursor.fetchall()
        cursor.close()
        return services
    except Exception as e:
        print(f"Error en show_services : {e}")
        return []
    
def insert_c_install(db, dni_employee, dni_costumer, code_ser, latitude_em, altitude_em, descrip_work):
    try:
        cursor = db.cursor()
        sql1 = f"INSERT install VALUES('{dni_employee}','{dni_costumer}', {code_ser}, '{latitude_em}', '{altitude_em}', '{descrip_work}', 1, GETDATE())"
        cursor.execute(sql1)
        cursor.commit()
        cursor.close()
    except Exception as e:
        print(f"Error en show_services : {e}")

def insert_f_install(db, dni_employee, dni_costumer, code_ser, latitude_em, altitude_em, descrip_work):
    try:
        cursor = db.cursor()
        sql1 = f"INSERT install VALUES({dni_employee},{dni_costumer}, {code_ser}, {latitude_em}, {altitude_em}, {descrip_work}, 0, GETDATE())"
        cursor.execute(sql1)
        cursor.commit()
        cursor.close()
    except Exception as e:
        print(f"Error en show_services : {e}")

def update_costumer_order(db, dni_costumer):
    try:
        cursor = db.cursor()
        sql1 = f"""UPDATE co
                SET co.check_install = 1
                FROM costumer_order co JOIN orders o 
                ON co.cod_order = o.cod_order
                WHERE o.dni_costumer = '{dni_costumer}'"""
        cursor.execute(sql1)
        cursor.commit()
        cursor.close()
    except Exception as e:
        print(f"Error en show_services : {e}")

def cod_service(db, cod_order):
    try:
        cursor = db.cursor()
        sql1 = f"""SELECT code_type_ser FROM orders
                WHERE cod_order = {cod_order}"""
        cursor.execute(sql1)
        code_ser = cursor.fetchone()
        cursor.close()
        return code_ser
    except Exception as e:
        print(f"Error en cod_service : {e}")
        return []

def get_email(db, cod_order):
    try:
        cursor = db.cursor()
        sql1 = f"""SELECT co.email_costumer
                    FROM orders o JOIN costumer co
                    ON o.dni_costumer = co.dni_costumer
                    WHERE o.cod_order = {cod_order}"""
        cursor.execute(sql1)
        code_ser = cursor.fetchone()
        cursor.close()
        return code_ser
    except Exception as e:
        print(f"Error en cod_service : {e}")
        return []

def facture(db, cod_order):
    try:
        cursor = db.cursor()
        sql1 = f"""SELECT CONCAT(SUBSTRING(c.name_costumer, 1, CHARINDEX(' ', c.name_costumer) - 1), ' ', SUBSTRING(c.lastna_costumer, 1, CHARINDEX(' ', c.lastna_costumer) - 1)) AS 'name_costumer_', c.cellphone_costumer, i.date_install, c.adress_costumer, CONCAT(st.name_ser, ' ', tst.type_name_ser) as 'service_name', c.latitude_costumer, c.altitude_costumer, tst.price_ser, tst.descr_ser, o.cod_order, o.date_order, CONCAT(SUBSTRING(e.name_employee, 1, CHARINDEX(' ', e.name_employee) - 1), ' ', SUBSTRING(e.lastna_employee, 1, CHARINDEX(' ', e.lastna_employee) - 1)) AS 'name_employee_', c.dni_costumer, i.descrip_work
                    FROM costumer_order co JOIN orders o
                    ON co.cod_order = o.cod_order
                    JOIN costumer c
                    ON c.dni_costumer = o.dni_costumer
                    JOIN type_services_telcom tst
                    ON tst.code_type_ser = o.code_type_ser
                    JOIN services_telcom st
                    ON tst.code_ser = st.code_ser
                    JOIN employee e
                    ON co.dni_employee = e.dni_employee
                    JOIN install i
                    ON co.dni_employee = i.dni_employee
                    WHERE o.cod_order = {cod_order}"""
        cursor.execute(sql1)
        services = cursor.fetchone()
        cursor.close()
        return services
    except Exception as e:
        print(f"Error en facture : {e}")
        return []
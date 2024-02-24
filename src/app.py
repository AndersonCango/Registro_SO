from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from config import configuration
from database.db import get_connection
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf.csrf import CSRFProtect
from decouple import config
from geopy.distance import geodesic

#from controllers import functions
from controllers.functions import dataLoginSession, gen_username_em, info_perfil_session

app = Flask(__name__)

csrf = CSRFProtect()
db = get_connection()

# Route Home - Principal
@app.route('/')
def home():
    if 'conectado' in session:
        return render_template('work_asistance.html', info_perfil_session=info_perfil_session(db))
    else:
        return render_template('/home.html')

# Route register
@app.route('/auth/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        _dni = request.form['dni']
        _email = request.form['email_user']
        _password = request.form['pass_user']
        _c_password = request.form['con_pass_user']

        cursor = db.cursor()
        sql = f"""SELECT dni_employee, name_employee, lastna_employee, email_employee FROM employee
                WHERE dni_employee = '{_dni}'"""
        cursor.execute(sql)
        row = cursor.fetchone()

        if row is not None:

            name_em_db = row[1].lower()
            lastna_em_db = row[2].lower()

            # Return a unique username
            user_created = gen_username_em(db, name_em_db, lastna_em_db)
            print(user_created)

            if _password == _c_password and _email == row[3]:
                cursor2 = db.cursor()
                sql2 = f"""UPDATE employee
                                SET username_employee = '{user_created}',
                                    password_employee = '{generate_password_hash(_password)}'
                            WHERE dni_employee = '{_dni}'"""
                cursor2.execute(sql2)
                cursor2.commit()
                cursor2.close()
                cursor.close()
                return redirect(url_for('login')) 
            else:
                flash('Invalid credentials for the entered user')
                return render_template('auth/auth_register.html')  
        else:
                flash('The user does not exist, please verify.', 'error')
                return render_template('auth/auth_register.html')
    else:
        return render_template('auth/auth_register.html')

# Route Forget Password
@app.route('/auth/forget_password', methods=['GET','POST'])
def forgot_password():
    if 'conectado' in session:
        return redirect(url_for('asistance'))
    else:
        if request.method == 'POST':
        
            _dni = str(request.form['identity_card'])
            cursor = db.cursor()
            sql = f"""SELECT email_employee, password_employee FROM employee
                    WHERE dni_employee = '{_dni}'"""
            cursor.execute(sql)
            user = cursor.fetchone()
            if user is not None:
                flash('Your password is in your email')
                return redirect(url_for('login')) 
            else:
                flash('The ID does not exist', 'error')
                return render_template('auth/auth_forgot_password.html')
        else:
            return render_template('auth/auth_forgot_password.html')

# Route Login
@app.route('/auth/login', methods=['GET','POST'])
def login():
    
    if 'conectado' in session:
        return redirect(url_for('asistance'))
    
    else:
        if request.method == 'POST':
            
            _username = str(request.form['email_user'])
            _password = str(request.form['pass_user'])
            
            cursor = db.cursor()
            sql = f"""SELECT * FROM employee
                    WHERE username_employee = '{_username}'"""
            cursor.execute(sql)
            row = cursor.fetchone()
            
            if row:
                
                # Check the same passwords
                if check_password_hash(row[5], _password):
                    
                    # Create session data, to be able to access this data in other routes
                    session['conectado'] = True
                    session['dni_employee'] = row[0]
                    session['name_employee'] = row[1]
                    session['lastna_employee'] = row[2]
                    session['email_employee'] = row[3]
                    session['username_employee'] = row[4]
                    session['cellphone_employee'] = row[6]
                    return redirect(url_for('asistance'))
                else:
                    # The account does not exist or the username/password is incorrect
                    flash('Incorrect data please check.', 'error')
                    return render_template('auth/auth_login.html')
            else:
                flash('The user does not exist, please verify.', 'error')
                return render_template('auth/auth_login.html')
        else:
            return render_template('auth/auth_login.html')

@app.route('/work-asistance', methods=['POST', 'GET'])
def asistance():

    if 'conectado' in session:
        if request.method == 'POST':
            _latitude = float("")
            _altitude = float("")
            central_point = (_altitude, _latitude)
            check_coordinates = (_altitude, _latitude)
            radio = 20
            for coordenadas in check_coordinates:
                distancia = geodesic(central_point, coordenadas).meters
                if distancia <= radio:
                    print(f"Las coordenadas {coordenadas} están dentro del radio de {radio} metros del punto central.")
                else:
                    print(f"Las coordenadas {coordenadas} están fuera del radio de {radio} metros del punto central.")
            pass
        else:
            cursor = db.cursor()
            sql = f"""SELECT co.dni_costumer, CONCAT(SUBSTRING(c.name_costumer, 1, CHARINDEX(' ', name_costumer) - 1), ' ', SUBSTRING(lastna_costumer, 1, CHARINDEX(' ', lastna_costumer) - 1)) AS 'name_customer', CONCAT(st.name_ser, ' ', tst.type_name_ser) as 'service_name', c.adress_costumer, o.date_expected_install
                    FROM costumer_order co join costumer c
                    ON co.dni_costumer = c.dni_costumer
                    join orders o
                    ON c.dni_costumer = o.dni_costumer
                    join type_services_telcom tst
                    ON o.code_type_ser = tst.code_type_ser
                    join services_telcom st
                    ON st.code_ser = tst.code_ser
                    WHERE dni_employee = '{session['dni_employee']}'
                    ORDER BY o.date_expected_install ASC"""
            cursor.execute(sql)
            intallations = cursor.fetchall()
            cursor1 = db.cursor()
            sql1 = f"""SELECT CONCAT(st.name_ser, ' ', tst.type_name_ser) as 'Service Name'
                    FROM type_services_telcom tst JOIN services_telcom st
                    ON tst.code_ser = st.code_ser
                    """
            cursor1.execute(sql1)
            services = cursor1.fetchall()
            cursor.close()
            cursor1.close()
            return render_template('work_asistance.html', info_perfil_session=info_perfil_session(db), intallations=intallations, services=services)

    else:
        return redirect(url_for('home'))

@app.route('/auth/logout', methods=['GET'])
def logout():
    if request.method == 'GET':
        if 'conectado' in session:
            # Delete data of session
            session.pop('conectado', None)
            session.pop('dni_employee', None)
            session.pop('name_employee', None)
            session.pop('lastna_employee', None)
            session.pop('email_employee', None)
            session.pop('username_employee', None)
            session.pop('cellphone_employee', None)
            # flash('Your session was successfully closed', 'success')
            return redirect(url_for('home'))
        else:
            flash('Remember you must log in', 'error')
            return render_template('auth/auth_login.html')        

if __name__ == '__main__':
    app.config.from_object(configuration['development'])
    csrf.init_app(app)
    app.run()
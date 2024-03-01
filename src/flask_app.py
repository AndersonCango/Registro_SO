from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from config import configuration
from database.db import get_connection
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf.csrf import CSRFProtect
from decouple import config
from geopy.distance import geodesic

# Emails
import smtplib
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#from controllers import functions
from controllers.functions import dataLoginSession, gen_username_em, info_perfil_session, show_services, show_works, insert_c_install, insert_f_install, update_costumer_order, facture, cod_service, get_email
app = Flask(__name__)

sender = os.getenv('USER')
msg = MIMEMultipart()
msg['From'] = sender

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
        sql = f"""SELECT dni_employee, name_employee, lastna_employee, email_employee, username_employee FROM employee
                WHERE dni_employee = '{_dni}'"""
        cursor.execute(sql)
        row = cursor.fetchone()

        if row is not None:
            if row[4] == '':
                if _password == _c_password and _email == row[3]:
                    name_em_db = row[1].lower()
                    lastna_em_db = row[2].lower()
                    # Return a unique username
                    user_created = gen_username_em(db, name_em_db, lastna_em_db)
                    cursor2 = db.cursor()
                    sql2 = f"""UPDATE employee
                                    SET username_employee = '{user_created}',
                                        password_employee = '{generate_password_hash(_password)}'
                                WHERE dni_employee = '{_dni}'"""
                    cursor2.execute(sql2)
                    # Send email with username
                    subject = "Register - Telcomep"
                    destino = row[3]
                    msg['Subject'] = subject
                    msg['To'] = destino
                    html_content = render_template('auth/auth_email.html', username=user_created)
                    msg.attach(MIMEText(html_content, 'html'))
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(sender, os.getenv('PASSWORD'))
                    server.sendmail(sender, destino, msg.as_string())
                    server.quit()
                    cursor2.commit()
                    cursor2.close()
                    cursor.close()

                    return redirect(url_for('login'))
                else:
                    flash('Invalid credentials for the entered user')
                    return render_template('auth/auth_register.html')
            else:
                flash('The user is already registered')
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
    
            _dni = str(request.form['dni'])
            _password = request.form['pass_user']
            _c_password = request.form['con_pass_user']
            cursor = db.cursor()
            sql = f"""SELECT email_employee, password_employee FROM employee
                    WHERE dni_employee = '{_dni}'"""
            cursor.execute(sql)
            user = cursor.fetchone()
            if user is not None:
                if _c_password == _password:
                    cursor1 = db.cursor()
                    sql1 = f"""UPDATE employee
                            SET password_employee = '{generate_password_hash(_password)}'
                            WHERE dni_employee = '{_dni}'"""
                    cursor1.execute(sql1)
                    cursor1.commit()
                    # Send email with username
                    subject = "Contraseña actualizada"
                    destino = user[0]
                    msg['Subject'] = subject
                    msg['To'] = destino
                    html_content = render_template('auth/auth_email_forgot_password.html')
                    msg.attach(MIMEText(html_content, 'html'))
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(sender, os.getenv('PASSWORD'))
                    server.sendmail(sender, destino, msg.as_string())
                    server.quit()
                    cursor.close()
                    cursor1.close()
                    flash('Your new password is saved sucesfully')
                    return redirect(url_for('login')) 
                else:
                    flash('Invalid credentials for the user')
                    return render_template('auth/auth_forgot_password.html')
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
            # Datos de la pagina web
            _code_order = request.form['order_costumer']
            _dni_costumer = request.form['dni_costumer']
            _service_costumer = request.form['cos_service']
            _latitude = request.form['latitud']
            _altitude = request.form['altitud']
            _observations = request.form['commentary']
            # Conversion de string a los repectivos numeros
            cod_order = int(_code_order)
            _latitude_web = float(_latitude)
            _altitude_web = float(_altitude)
            # Data for database
            cursor = db.cursor()
            sql = f"""SELECT altitude_costumer, latitude_costumer
                        FROM costumer
                        WHERE dni_costumer = '{_dni_costumer}'"""
            cursor.execute(sql)
            cordinates_costumer = cursor.fetchall()
            _cordinates_bd = {'altitude': float(cordinates_costumer[0][0]), 'latitude': float(cordinates_costumer[0][1])}
            # Cordinates for database
            central_point = (_cordinates_bd['altitude'], _cordinates_bd['latitude'])
            radio = 20
            # Cordinates for web page
            check_coordinates = (_altitude_web, _latitude_web)

            for coordenadas in check_coordinates:
                distancia = geodesic(central_point, check_coordinates).meters
                if distancia <= radio:

                    tupla = cod_service(db, cod_order)
                    _code_ser = tupla[0]
                    code_ser = int(_code_ser)
                    insert_c_install(db, session['dni_employee'],_dni_costumer, code_ser, str(_latitude), str(_altitude), str(_observations))
                    update_costumer_order(db, _dni_costumer)
                    facturation = facture(db, cod_order)
                    print(facturation)
                    subject = "Detalles del Servicio - Factura"
                    _destino = get_email(db, cod_order)
                    destino = _destino[0]
                    msg['Subject'] = subject
                    msg['To'] = destino
                    html_content = render_template('auth/auth_email_facture.html', facture=facture(db, cod_order))
                    msg.attach(MIMEText(html_content, 'html'))
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(sender, os.getenv('PASSWORD'))
                    server.sendmail(sender, destino, msg.as_string())
                    server.quit()
                    return render_template('work_asistance.html', info_perfil_session=info_perfil_session(db), installations=show_works(db, session['dni_employee']), services=show_services(db))

                else:
                    tupla = cod_service(db, cod_order)
                    _code_ser = tupla[0]
                    code_ser = int(_code_ser)
                    insert_f_install(db, session['dni_employee'],_dni_costumer, code_ser, _latitude, _altitude, _observations)
                    update_costumer_order(db, _dni_costumer)
                    return render_template('work_asistance.html', info_perfil_session=info_perfil_session(db), installations=show_works(db, session['dni_employee']), services=show_services(db))
        else:
            return render_template('work_asistance.html', info_perfil_session=info_perfil_session(db), installations=show_works(db, session['dni_employee']), services=show_services(db))
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
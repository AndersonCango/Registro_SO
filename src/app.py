from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from config import config
from database.db import get_connection
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf.csrf import CSRFProtect
#from models import ModelEmployee
from controllers.functions import dataLoginSesion, gen_username_em, info_perfil_session

# Models
from models.ModelEmployee import ModelEmployee

# Entities
from models.entities.Employee import Employee

app = Flask(__name__)

csrf = CSRFProtect()
db = get_connection()

# Route Home - Principal
@app.route('/')
def home():
    if 'conectado' in session:
        return render_template('work_asistance.html', dataLoginSesion=dataLoginSesion())
    else:
        return render_template('/home.html')

# Route register
@app.route('/auth/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':

        _dni = request.form['dni']
        # _name = request.form['names'].lower()
        # _lastname = request.form['lastnames'].lower()
        _email = request.form['email_user']
        _password = request.form['pass_user']
        _c_password = request.form['con_pass_user']

        cursor = db.cursor()
        sql = f"""SELECT dni_em, name_em, lastna_em FROM employee
                WHERE dni_em = '{_dni}'"""
        cursor.execute(sql)
        row = cursor.fetchone()

        if row is not None:

            name_em_db = row[1].lower()
            lastna_em_db = row[2].lower()

            # Return a unique username
            user_created = gen_username_em(db, name_em_db, lastna_em_db)
            if _password == _c_password:
                cursor2 = db.cursor()
                sql2 = f"""UPDATE employee
                                SET email_em = '{user_created}',
                                    pass_em = '{generate_password_hash(_password)}'
                            WHERE dni_em = '{_dni}'"""
                cursor2.execute(sql2)
                cursor2.close()
                return redirect(url_for('login')) 
            else:
                flash('Invalid credentials for the entered user')
                return render_template('auth/auth_register.html')  
        else:
                flash('The user does not exist, please verify.', 'error')
                return render_template('auth/auth_register.html')
    else:
        return render_template('auth/auth_register.html')

# Route Login
@app.route('/auth/login', methods=['GET','POST'])
def login():
    
    if 'conectado' in session:
        return redirect(url_for('asistance'))
    
    else:
        if request.method == 'POST' and 'email_user' in request.form and 'pass_user' in request.form:
            
            _username = str(request.form['email_user'])
            _password = str(request.form['pass_user'])
            
            cursor = db.cursor()
            
            sql = f"""SELECT * FROM employee
                    WHERE email_em = '{_username}'"""
                        
            cursor.execute(sql)
                
            row = cursor.fetchone()
            
            if row:
                
                # Check the same passwords
                if check_password_hash(row[4], _password):
                    
                    # Create session data, to be able to access this data in other routes
                    session['conectado'] = True
                    session['dni_em'] = row[0]
                    session['name_em'] = row[1]
                    session['lastna_em'] = row[2]
                    session['email_em'] = row[3]
                    session['cellphone'] = row[5]
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
        return render_template('work_asistance.html', info_perfil_session=info_perfil_session(db))

    else:
        return redirect(url_for('home'))

@app.route('/auth/logout', methods=['GET'])
def logout():
    if request.method == 'GET':
        if 'conectado' in session:
            # Delete data of session
            session.pop('conectado', None)
            session.pop('dni_em', None)
            session.pop('name_em', None)
            session.pop('lastna_em', None)
            session.pop('email_em', None)
            session.pop('cellphone', None)
            # flash('Your session was successfully closed', 'success')
            return redirect(url_for('home'))
        else:
            flash('Remember you must log in', 'error')
            return render_template('auth/auth_login.html')        

if __name__ == '__main__':
    app.config.from_object(config['development'])
    csrf.init_app(app)
    app.run()
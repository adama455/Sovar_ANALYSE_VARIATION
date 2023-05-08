from flask import Flask, render_template,request
from db import DBconfig
from flask import send_from_directory
from flask import send_file
from functools import wraps
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_login import current_user
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user

from flask_mysqldb import MySQL
import mysql.connector
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import numpy as np
import pandas as pd
import xlwt
import html
import html5lib
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import create_engine
import sqlalchemy as sql
from datetime import date, timedelta,datetime
today = date.today()
yesterday = today - timedelta(days = 1)
import os
os.getcwd()
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import bcrypt
import glob

from decimal import Decimal
import openpyxl
from openpyxl import load_workbook
from openpyxl.reader.excel import load_workbook
from openpyxl.workbook import Workbook
from openpyxl.styles import Color, Fill
from openpyxl.cell import Cell
import hashlib
# import mail
from os.path import join, dirname, realpath


app = Flask(__name__)

UPLOAD_FOLDER = 'static/files'
ALLOWED_EXTENSIONS = set(['txt', 'pdf','csv','xlsx'])
#ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


app.secret_key = 'many random bytes'
DBconfig = DBconfig()
# COnfigure DB
app.config['MYSQL_HOST'] = DBconfig["host"]
app.config['MYSQL_USER'] = DBconfig["user"]
app.config['MYSQL_PASSWORD'] = DBconfig["password"]
app.config['MYSQL_DB'] = DBconfig["DBName"]
app.config['MYSQL_CURSORCLASS'] = DBconfig["dictDB"]
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER
mysql = MySQL(app)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'




#index connexion 
@app.route('/')
@app.route("/login", methods=('GET', 'POST'))
def index():
    logout_user()
    return render_template('login.html')


@app.route("/logout")
def logout():
    session.clear()
    return redirect('login')

@app.route("/recover", methods=('GET', 'POST'))
def recover():
    return render_template('forgot-password.html')

@app.route('/reinitialiser_password',methods=['GET','POST'])
def reinitialiser_password():
    msg = ''
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        password = request.form['password']
        passwordconf = request.form['passwordconf']
        if password != passwordconf:
           
            flash('Mots de passe saisis ne correspondent pas! Merci de vérifier.','error')
            return render_template('change-password.html')
        password = request.form['password']
        username = request.form['username']
        statut = 1
        password = hashlib.md5(password.encode()).hexdigest()
        # password = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt())
        cur.execute("UPDATE users set password =%s,statuts=%s WHERE id =%s" , (password, statut,session['so_user'])) 
        cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Changement Password',NOW())", (username,))
        cur.execute("INSERT INTO recover (id_user,recover) VALUES (%s,%s)", (username,passwordconf))
        cur.connection.commit() 
        #return render_template('reinitialiserpwd.html',msg=msg)
        return render_template('login.html')
    return render_template('login.html')


@app.route('/sonatel-sovar',methods=["POST"])
def home():
     msg = ''
    # Vérifiez si les requêtes POST "email" et "password" existent (formulaire soumis par l'utilisateur)
     if request.method == 'POST' and 'so_login' in request.form and 'so_password' in request.form:
        # Créer des variables pour un accès facile
        so_login= request.form['so_login']
        so_password = request.form['so_password']
        so_password = hashlib.md5(so_password.encode()).hexdigest()
        
        # Vérifier si le compte existe en utilisant MySQL
        cur = mysql.connection.cursor()
        # Selectionne dans la table utilisateurs email et password
        cur.execute('SELECT * FROM analysevariation.users as u WHERE u.username = %s and u.password= %s ', (so_login,so_password))
        # Récupérer un enregistrement et renvoyer le résultat
        account = cur.fetchone()
        
        # Si le account existe dans la table des utlisateurs dans notre base de données
        if account:
            # Créer des données de session, nous pouvons accéder à ces données dans d'autres itinéraires
            session['so_user'] = True
            session['so_user'] = account['id']
            session['so_email'] = account['email']
            session['so_nom']= account['nom']
            session['so_prenom'] = account['prenom']
            session['so_password'] = account['password']
            session['so_pass'] = account['password']
            session['so_login'] = account['username']
            session['so_actif'] = account['actif']
            session['so_profil_id'] = account['profil_id']
            session['so_idplateau'] = account['plateau_id']
            #session['so_univers'] = account['univers']
            session['so_statut'] = account['statuts']
            session['so_contact'] = account['contact']
            if 'so_user' in session:
                cur = mysql.connection.cursor()
                cur.execute("SELECT libelle FROM analysevariation.plateaux  WHERE idplat=%s ", [session['so_idplateau']])
                accoun = cur.fetchone()
                session['so_plateau'] = accoun['libelle'] 
                cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
                nbre= cur.fetchall()
                cur.execute ("SELECT * from analysevariation.action_programme ")
                actions =cur.fetchall()
                cur.execute ("SELECT * from analysevariation.kpi ")
                metriq= cur.fetchall()
                cur.execute ("SELECT * from analysevariation.equipe ")
                equipe= cur.fetchall()
                cur.execute("SELECT r.name FROM role as r , users as u WHERE u.profil_id = r.idrole AND u.id = '%s '", [session['so_user']] )
                accoun = cur.fetchone()
                session['so_profil'] = accoun['name']
                cur.execute("SELECT statuts FROM  users  WHERE  users.id = '%s '", [session['so_user']] )
                accoun = cur.fetchone()
                session['so_statut'] = accoun['statuts']
                cur.execute("SELECT email FROM  users  WHERE  users.id = '%s '", [session['so_user']] )
                accoun = cur.fetchone()
                session['so_email'] = accoun['email']
                cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
                logs= cur.fetchall()
                dim = date.today() 
                date_saisi= dim.strftime('%d-%m-%Y')
                cur.execute("SELECT MAX(idfic) as idfic FROM analysevariation.fichier")
                idfic = cur.fetchall()  

                if session['so_statut'] == 0:
                      return render_template('change-password.html')
                else:
                    return render_template('dashboard.html',equipe=equipe,idfic=idfic[0]['idfic'],nbre=nbre[0]['nbre'],actions=actions,logs=logs,metriq=metriq,date_saisi=date_saisi )
                
                
               
        else:   
            # Le compte n'existe pas ou email/password incorrect
             msg = " Identifiant ou password incorrect!!!!!"
   
        return render_template('login.html', msg=msg)
  
@app.route("/sonatel-sovar", methods=['POST','GET'])
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.causes order by id ASC")
    causes= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.action_programme ")
    actions= cur.fetchall()
    cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
    logs= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('dashboard.html',equipe=equipe,date_saisi=date_saisi,causes=causes,actions=actions,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq) 


@app.route("/sonatel-sovar/reporting", methods=['POST','GET'])
def reporting():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.causes order by id ASC")
    causes= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.action_programme ")
    actions =cur.fetchall()
    cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
    logs= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    cur.close()
    return render_template('reporting.html',equipe=equipe,date_saisi=date_saisi,causes=causes,actions=actions,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq) 

@app.route("/sonatel-sovar/fichiers", methods=['POST','GET'])
def folders():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.infofichier_charge order by idfic DESC")
    files= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.action_programme ")
    actions= cur.fetchall()
    cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
    logs= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('folders.html',equipe=equipe,date_saisi=date_saisi,files=files,actions=actions,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq) 

@app.route("/sonatel-sovar/dossiers", methods=['POST','GET'])
def dossiers():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT count(*) as nbre,k.idkpi,k.metrique,k.description from analysevariation.kpi as k,analysevariation.fichier as f where k.idkpi=f.kpi_id  group by k.idkpi,k.metrique,k.description order by k.idkpi ASC")
    dossiers= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.action_programme ")
    actions= cur.fetchall()
    cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
    logs= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier ")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('dossiers.html',equipe=equipe,date_saisi=date_saisi,dossiers=dossiers,actions=actions,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq) 

@app.route('/sonatel-sovar/dosiers/<id>', methods=['POST','GET'])
def dossier_fic(id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM analysevariation.infofichier_charge where idkpi=%s ",[id])
        results=cur.fetchall()
        cur.execute("SELECT *  FROM analysevariation.kpi where idkpi=%s ",[id])
        kpi=cur.fetchall()
        cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
        logs= cur.fetchall()
        cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
        nbre= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.kpi ")
        metriq= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.equipe ")
        equipe= cur.fetchall()
        cur.close()
        dim = date.today() 
        date_saisi= dim.strftime('%d-%m-%Y')
        return render_template('dossier_fichier.html',equipe=equipe,date_saisi=date_saisi,results=results,kpi=kpi,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq) 


@app.route("/sonatel-sovar/datasset", methods=['POST','GET'])
def dataset():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.infofichier_charge order by idfic DESC")
    dataset= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.action_programme ")
    actions= cur.fetchall()
    cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
    logs= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('dataset.html',equipe=equipe,actions=actions,date_saisi=date_saisi,dataset=dataset,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq) 


@app.route("/sonatel-sovar/analyses", methods=['POST','GET'])
def analyses():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.infofichier_charge order by idfic DESC")
    dataset= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.action_programme ")
    actions= cur.fetchall()
    cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
    logs= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('analyses.html',equipe=equipe,date_saisi=date_saisi,dataset=dataset,actions=actions,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq) 

@app.route('/export_analyse',methods=['POST','GET'])
def export_analyse():
     if request.method == "POST":
         kpi = request.form['kpi']
         user_session = request.form['user_session']
         user_email=request.form['user_email']
         cur = mysql.connection.cursor()
         cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Export liste analyses',NOW())", (user_session,))
         mysql.connection.commit()
         cur.close()  
     
     if (request.form['kpi'] == "ALL" ):
       engine = create_engine('mysql://root:Son@tel2020@10.137.16.232/analysevariation') 
       query =query = "select libelle,date,statut,prenom,nom,metrique,type,description from analysevariation.infofichier_charge "
      
     else :
       engine = create_engine('mysql://root:Son@tel2020@10.137.16.232/analysevariation')
       query =query = "select libelle,date,statut,prenom,nom,metrique,type,description from analysevariation.infofichier_charge where (idkpi='{0}' )   ".format(kpi)
      
     ho = pd.read_sql_query(query, engine)
     
     path2 = "C:/Users/sy027834/Desktop/DSC/sovar/DATA/"
     writer = pd.ExcelWriter(path2+"AV.xlsx", engine='xlsxwriter') 
     ho.to_excel(writer, sheet_name='AV',index=False)
     writer.save()
     #debut envoi
     path2="C:/Users/sy027834/Desktop/DSC/sovar/DATA/"
    
     fromaddr = "sovar@orange-sonatel.com"
     toaddr = session['so_email']
     msg = MIMEMultipart()
     msg['From'] = fromaddr
     msg['Subject'] = "Liste des analyses de variation disponible "
     body = "Bonjour %s %s , \nCi-joint les analyses de variations . \n \nCordialement, \n \n \nMail envoyé par un automate, merci de ne pas y répondre." % (session['so_prenom'], session['so_nom'])
     msg.attach(MIMEText(body, 'plain'))
     filename = "PA.xlsx"
     attachment = open(path2+"AV.xlsx", "rb")
     p = MIMEBase('application', 'octet-stream')
     p.set_payload((attachment).read())
     encoders.encode_base64(p)
     p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
     msg.attach(p)
     s = smtplib.SMTP('10.95.100.10', 25)
     s.starttls()
     text = msg.as_string()
     s.sendmail(fromaddr, toaddr, text)
     s.quit()
     flash("Merci de consulter votre boite , un mail vous a été transmis!", "success")
     return redirect(url_for('analyses'))
     #fin envoi mail   

@app.route('/sonatel-sovar/analyses/numero-<id>', methods=['POST','GET'])
def abberation(id):
        id = id
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM analysevariation.valeurs_aberante where file_id=%s ",[id])
        results=cur.fetchall()
        cur.execute ("SELECT * from analysevariation.action_programme")
        actions= cur.fetchall()
        cur.execute("SELECT libelle,date,metrique,prenom,nom,username,type,periodicite ,description FROM analysevariation.infofichier_charge where idfic=%s ",[id])
        fic=cur.fetchall()
        cur.execute("SELECT * FROM analysevariation.indicateurs where fileid=%s ",[id])
        indic=cur.fetchall()
        cur.execute("SELECT count(*) as va FROM analysevariation.valeurs_aberante where file_id=%s ",[id])
        va=cur.fetchall()
        cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
        logs= cur.fetchall()
        cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
        nbre= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.kpi ")
        metriq= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.equipe ")
        equipe= cur.fetchall()
        cur.close()
        dim = date.today() 
        date_saisi= dim.strftime('%d-%m-%Y')
        engine = create_engine('mysql://root:Son@tel2020@10.137.16.232/analysevariation')	
        query =query = "SELECT valeur FROM analysevariation.valeurs_fichier where file_id='{0}' ".format(id) 
        df = pd.read_sql_query(query, engine)
        media=df['valeur'].median()
      
       
        return render_template('valeurs_abberantes.html',equipe=equipe,actions=actions,media=media,indic=indic, date_saisi= date_saisi,results=results,fic=fic,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq,va=va[0]['va'] ) 



@app.route('/sonatel-sovar/analyser/mesure-<id>', methods=['POST','GET'])
def debuter_AV(id):
   
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM analysevariation.valeurs_aberante where idvaleur=%s ",[id])
        results=cur.fetchall()
        cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
        logs= cur.fetchall()
        cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
        nbre= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.kpi ")
        metriq= cur.fetchall()
        cur.execute ("SELECT id,libelle from analysevariation.causes order by id ASC ")
        causes= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.equipe ")
        equipe= cur.fetchall()
        cur.close()
        dim = date.today() 
        date_saisi= dim.strftime('%d-%m-%Y')
        
        return render_template('debuter_AV.html',equipe=equipe,causes=causes,date_saisi= date_saisi,results=results,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq ) 


@app.route('/sonatel-sovar/analyse/saisi-pa', methods=['POST','GET'])
def saisipa():
       
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT idproblem as idproblem FROM analysevariation.probleme where idproblem=(select MAX(idproblem) from analysevariation.probleme) ")
        idproblem = cur.fetchone()
        idproblem=idproblem['idproblem']
        cur.execute("SELECT id_mesure as id_mesure FROM analysevariation.probleme where idproblem=(select MAX(idproblem) from analysevariation.probleme) ")
        id_mesure = cur.fetchone()
        id_mesure=id_mesure['id_mesure']

        cur.execute('SELECT * FROM analysevariation.probleme where idproblem=%s ', [idproblem])
        problem=cur.fetchall()
        cur.execute('SELECT * FROM analysevariation.pourquoi1 where valeur_aberrante_id=%s ', [id_mesure])
        pourquoi1=cur.fetchall()
        cur.execute('SELECT * FROM analysevariation.pourquoi2 where valeur_aberrante_id=%s ', [id_mesure])
        pourquoi2=cur.fetchall()
        cur.execute('SELECT * FROM analysevariation.pourquoi3 where valeur_aberrante_id=%s ', [id_mesure])
        pourquoi3=cur.fetchall()
        cur.execute('SELECT * FROM analysevariation.pourquoi4 where valeur_aberrante_id=%s ', [id_mesure])
        pourquoi4=cur.fetchall()
        cur.execute('SELECT * FROM analysevariation.pourquoi5 where valeur_aberrante_id=%s ', [id_mesure])
        pourquoi5=cur.fetchall()
        cur.execute('SELECT * FROM analysevariation.axes_analyses where valeur_aberrante_id=%s ', [id_mesure])
        axes=cur.fetchall()
       
       
       
       
        cur.execute("SELECT * FROM analysevariation.valeurs_aberante as a ,analysevariation.probleme as p where p.idproblem=%s and p.id_mesure=a.idvaleur ", [idproblem])
        results=cur.fetchall()
        
        cur.execute("SELECT MONTH(date) as mois FROM analysevariation.valeurs_aberante as a ,analysevariation.probleme as p where p.idproblem=%s and p.id_mesure=a.idvaleur ", [idproblem])
        mois=cur.fetchall()
        cur.execute("SELECT YEAR(date) as annee FROM analysevariation.valeurs_aberante as a ,analysevariation.probleme as p where p.idproblem=%s and p.id_mesure=a.idvaleur ", [idproblem])
        annee=cur.fetchall()
        cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
        logs= cur.fetchall()
        cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
        nbre= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.kpi ")
        metriq= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.equipe ")
        equipe= cur.fetchall()
        cur.execute ("SELECT id,libelle from analysevariation.causes order by id ASC ")
        causes= cur.fetchall()
        cur.close()
        dim = date.today() 
        date_saisi= dim.strftime('%d-%m-%Y')
        
        return render_template('saisipa.html',mois=mois[0]['mois'],annee=annee[0]['annee'],pourquoi1=pourquoi1,id_mesure=id_mesure, idproblem= idproblem,problem=problem,causes=causes,date_saisi= date_saisi,results=results,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq,
                           equipe=equipe,pourquoi2=pourquoi2,pourquoi3=pourquoi3,pourquoi4=pourquoi4,pourquoi5=pourquoi5,axes=axes ) 

#----------------INSERT DATA ANALYSE---------------------------------
@app.route('/add_pourquoi', methods=['POST'])
def add_pourquoi():
    if request.method == 'POST':
        file_id= request.form['file_id']
        id_mesure = request.form['id_mesure']
        nom_cc= request.form['nom_cc']
        user_session= request.form['user_session']
        probleme= request.form['probleme']
        
        input_1 = request.form['input_1']
        input_12= request.form['input_12']
        input_13= request.form['input_13']

        input_2 = request.form['input_2']
        input_22= request.form['input_22']
        input_23= request.form['input_23']
        input_24 = request.form['input_24']
        input_25= request.form['input_25']
        input_26= request.form['input_26']

        input_3 = request.form['input_3']
        input_32= request.form['input_32']
        input_33= request.form['input_33']
        input_34 = request.form['input_34']
        input_35= request.form['input_35']
        input_36= request.form['input_36']
      
        input_4 = request.form['input_4']
        input_42= request.form['input_42']
        input_43= request.form['input_43']
        input_44 = request.form['input_44']
        input_45= request.form['input_45']
        input_46= request.form['input_46']
      
        input_5 = request.form['input_5']
        input_52= request.form['input_52']
        input_53= request.form['input_53']
        input_54 = request.form['input_54']
        input_55= request.form['input_55']
        input_56= request.form['input_56']
       
        axes_1_analyse= request.form['axes_1_analyse']
        axes_2_analyse= request.form['axes_2_analyse']
        axes_3_analyse= request.form['axes_3_analyse']
        axes_4_analyse= request.form['axes_4_analyse']
        axes_5_analyse= request.form['axes_5_analyse']
        axes_6_analyse= request.form['axes_6_analyse']
       
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO analysevariation.probleme(nom_cc,id_mesure,probleme,fichier_id,user_log,date_analyse) VALUES (%s,%s,%s,%s,%s,NOW())", (nom_cc,id_mesure,probleme,file_id,user_session))
        cur.execute("INSERT INTO analysevariation.pourquoi1(p1,p12,p13,valeur_aberrante_id) VALUES (%s,%s,%s,%s)", (input_1,input_12,input_13,id_mesure))
        cur.execute("INSERT INTO analysevariation.pourquoi2(p2,p22,p23,p24,p25,p26,valeur_aberrante_id) VALUES (%s,%s,%s,%s,%s,%s,%s)", (input_2,input_22,input_23,input_24,input_25,input_26,id_mesure))
        cur.execute("INSERT INTO analysevariation.pourquoi3(p3,p32,p33,p34,p35,p36,valeur_aberrante_id) VALUES (%s,%s,%s,%s,%s,%s,%s)", (input_3,input_32,input_33,input_34,input_35,input_36,id_mesure))
        cur.execute("INSERT INTO analysevariation.pourquoi4(p4,p42,p43,p44,p45,p46,valeur_aberrante_id) VALUES (%s,%s,%s,%s,%s,%s,%s)", (input_4,input_42,input_43,input_44,input_45,input_46,id_mesure))
        cur.execute("INSERT INTO analysevariation.pourquoi5(p5,p52,p53,p54,p55,p56,valeur_aberrante_id) VALUES (%s,%s,%s,%s,%s,%s,%s)", (input_5,input_52,input_53,input_54,input_55,input_56,id_mesure))
        cur.execute("INSERT INTO analysevariation.axes_analyses(a1,a2,a3,a4,a5,a6,valeur_aberrante_id) VALUES (%s,%s,%s,%s,%s,%s,%s)", ( axes_1_analyse, axes_2_analyse, axes_3_analyse, axes_4_analyse, axes_5_analyse, axes_6_analyse,id_mesure))
        cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Insertion données AV',NOW())", (user_session,))
        mysql.connection.commit()
            
        flash('Les données de votre analyse sont insérées avec succès','success')
        return redirect(url_for('saisipa'))


@app.route("/sonatel-sovar/reporting/liste-analyses", methods=['POST','GET'])
def listeAV():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * FROM analysevariation.probleme as p,analysevariation.valeurs_aberante as a where p.id_mesure=a.idvaleur order by p.idproblem DESC")
    datasett= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.action_programme ")
    actions= cur.fetchall()
    cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
    logs= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('liste-analyses.html',equipe=equipe,date_saisi=date_saisi,datasett=datasett,actions=actions,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq) 


@app.route('/sonatel-sovar/donnees-brutes/AV-<idgss>', methods=['POST','GET'])
def datafic(idgss):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM analysevariation.valeurs_fichier where file_id=%s order by file_id DESC ",[idgss])
        results=cur.fetchall()
        cur.execute("SELECT libelle,date,metrique,prenom,nom,username,effectif,periodicite FROM analysevariation.infofichier_charge where idfic=%s ",[idgss])
        fic=cur.fetchall()
        cur.execute("SELECT idfic,libelle,metrique FROM analysevariation.infofichier_charge ")
        files=cur.fetchall()
        cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
        logs= cur.fetchall()
        cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
        nbre= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.kpi ")
        metriq= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.equipe ")
        equipe= cur.fetchall()
        cur.close()
        dim = date.today() 
        date_saisi= dim.strftime('%d-%m-%Y')
        return render_template('datafic.html',equipe=equipe,files=files,date_saisi=date_saisi,results=results,fic=fic,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq ) 


@app.route("/sonatel-sovar/actions-programme", methods=['POST','GET'])
def programme():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.programme_pourquoi5 order by idprogram ASC")
    programme= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.action_programme ")
    actions= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('actions-programme.html',equipe=equipe,date_saisi=date_saisi,programme=programme,actions=actions,nbre=nbre[0]['nbre'],metriq=metriq) 

@app.route("/sonatel-sovar/actions-individuelles", methods=['POST','GET'])
def individuelles():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.programme_pourquoi5 order by idprogram ASC")
    programme= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.action_programme ")
    actions= cur.fetchall()
    cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
    logs= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('actions-individuelles.html',equipe=equipe,date_saisi=date_saisi,programme=programme,actions=actions,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq)




@app.route("/sonatel-sovar/data-abberrantes", methods=['POST','GET'])
def abberations():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.programme_pourquoi5 order by idprogram ASC")
    actions= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('abberations.html',equipe=equipe,date_saisi=date_saisi,actions=actions,nbre=nbre[0]['nbre'],metriq=metriq) 



@app.route("/sonatel-sovar/guide-utilisateur", methods=['POST','GET'])
def guide():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.action_programme ")
    actions= cur.fetchall()
    cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
    logs= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('faq.html',equipe=equipe, date_saisi=date_saisi,actions=actions,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq) 

@app.route("/sonatel-sovar/methodologie", methods=['POST','GET'])
def methode():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.action_programme ")
    actions= cur.fetchall()
    cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
    logs= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('methode.html',equipe=equipe,date_saisi=date_saisi,actions=actions,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq) 
#---------------DEBUT MENU PARAMETRAGE---------------------
@app.route("/sonatel-sovar/causes", methods=['POST','GET'])
def cause():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.causes order by id ASC")
    causes= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.action_programme ")
    actions= cur.fetchall()
    cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
    logs= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('causes.html',equipe=equipe, date_saisi= date_saisi,causes=causes,actions=actions,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq)  

@app.route('/add_cause', methods=['POST'])
def add_cause():
    if request.method == 'POST':
        libelle= request.form['libelle']
        description= request.form['description']
        user_session = request.form['user_session']
        cur = mysql.connection.cursor()
        cur.execute("SELECT libelleFROM analysevariation.causes WHERE metrique= BINARY %s", [libelle])
        res = cur.fetchone()
        if libelle in str(res):
             #msg = "Le login est déjà dans la base"
             flash('La cause est déjà dans la base ! Merci de choisir un autre libelle !!!','error')  
             return redirect(url_for('causes'))
        else:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO analysevariation.causes(libelle,description) VALUES (%s,%s)", (libelle,description))
            cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Ajout Famille de cause',NOW())", (user_session,))
            mysql.connection.commit()
            
            flash('La famille de cause est créée avec succès','success')
            return redirect(url_for('cause'))



@app.route('/update_cause/<string:id>', methods=['GET','POST'])
def update_cause(id):

    if request.method == 'POST':
        
        libelle= request.form['libelle']
        description = request.form['description']
        user_session=request.form['user_session']
        
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE analysevariation.causes
               SET causes.libelle=%s,causes.description=%s
               WHERE causes.id=%s 
            """, (libelle,description,id))
        cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Modification cause',NOW())", (user_session,))
       
        flash("Les données plateau sont bien mises à jour",'success')
        mysql.connection.commit()
        return redirect(url_for('cause'))

@app.route('/delete_cause/<string:id>', methods=['GET'])
def delete_cause(id):
        
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM analysevariation.causes WHERE id=%s", (id,))
        cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Suppression famille cause',NOW())", (session['so_login'],))
        mysql.connection.commit()
        flash('Enregistrement est supprimé avec succès','success')
        return redirect(url_for('cause'))


@app.route("/sonatel-sovar/metriques", methods=['POST','GET'])
def metriques():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.kpi order by idkpi ASC")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.action_programme ")
    actions= cur.fetchall()
    cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
    logs= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('metriques.html',equipe=equipe,date_saisi=date_saisi,metriq=metriq,actions=actions,logs=logs,nbre=nbre[0]['nbre']) 


@app.route('/add_metrique', methods=['POST'])
def add_metrique():
    if request.method == 'POST':
        metrique= request.form['metrique']
        type = request.form['type']
        periodicite = request.form['periodicite']
        analyse= request.form['analyse']
        description= request.form['description']
      
      
        user_session = request.form['user_session']
        cur = mysql.connection.cursor()
        cur.execute("SELECT metrique FROM analysevariation.kpi WHERE metrique= BINARY %s", [metrique])
        res = cur.fetchone()
        if metrique in str(res):
             #msg = "Le login est déjà dans la base"
             flash('Le métrique ou kpi est déjà dans la base ! Merci de choisir un autre libelle !!!','error')  
             return redirect(url_for('metriques'))
        else:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO analysevariation.kpi(metrique,description,type,periodicite,niveau) VALUES (%s,%s,%s,%s,%s)", (metrique,description,type,periodicite,analyse))
            cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Ajout Métrique',NOW())", (user_session,))
            mysql.connection.commit()
            
            flash('Le métrique ou kpi créé avec succès','success')
            return redirect(url_for('metriques'))

@app.route('/delete_metrique/<string:id>', methods=['GET'])
def delete_metrique(id):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM analysevariation.kpi WHERE idkpi=%s", (id,))
        cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Suppression métrique',NOW())", (session['so_login'],))
        mysql.connection.commit()
        flash('Enregistrement est supprimé avec succès','success')
        return redirect(url_for('metriques'))


@app.route("/sonatel-sovar/plateaux", methods=['POST','GET'])
def plateaux():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.plateaux order by idplat ASC")
    plat= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
    logs= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('plateaux.html',equipe=equipe,date_saisi=date_saisi,plat=plat,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq) 

@app.route('/add_plateau', methods=['POST'])
def add_plateau():
    if request.method == 'POST':
        libelle = request.form['libelle']
        univers = request.form['univers']
        description= request.form['description']
      
      
        user_session = request.form['user_session']
        cur = mysql.connection.cursor()
        cur.execute("SELECT libelle FROM analysevariation.plateaux WHERE libelle= BINARY %s", [libelle])
        res = cur.fetchone()
        if libelle in str(res):
             #msg = "Le login est déjà dans la base"
             flash('Le plateau est déjà dans la base ! Merci de choisir un autre libelle !!!','error')  
             return redirect(url_for('plateaux'))
        else:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO analysevariation.plateaux(libelle,description,univers) VALUES (%s,%s,%s)", (libelle,description,univers))
            cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Ajout Plateau',NOW())", (user_session,))
            mysql.connection.commit()
            
            flash('Le plateau créé avec succès','success')
            return redirect(url_for('plateaux'))

@app.route('/update_plateau/<string:id>', methods=['GET','POST'])
def update_plateau(id):

    if request.method == 'POST':
        
        libelle= request.form['libelle']
        univers = request.form['univers']
        description = request.form['description']
        user_session=request.form['user_session']
        
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE analysevariation.plateaux
               SET plateaux.libelle=%s,plateaux.univers=%s,plateaux.description=%s
               WHERE plateaux.idplat=%s 
            """, (libelle,univers,description,id))
        cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Modification plateau',NOW())", (user_session,))
       
        flash("Les données plateau sont bien mises à jour",'success')
        mysql.connection.commit()
        return redirect(url_for('plateaux'))

@app.route('/delete_plateau/<string:id>', methods=['GET'])
def delete_plateau(id):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM analysevariation.plateaux WHERE idplat=%s", (id,))
        cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Suppression plateau',NOW())", (session['so_login'],))
        mysql.connection.commit()
        flash('Enregistrement est supprimé avec succès','success')
        return redirect(url_for('plateaux'))

#----------------FIN---------------------------------

@app.route('/add_analyse', methods=['POST'])
def add_analyse():
    if request.method == 'POST':
        libelle_analyse = request.form['libelle_analyse']
        kpi = request.form['kpi']
        user_session = request.form['user_session']
        equipe_id = request.form['equipe_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT libelle FROM analysevariation.fichier WHERE libelle = %s", [libelle_analyse])
        res = cur.fetchone()
        cur.execute("SELECT MONTH(date) as mois FROM analysevariation.fichier WHERE libelle = %s", [libelle_analyse])
        mois = cur.fetchone()
        mois=mois
        cur.execute("SELECT YEAR(date) as annee FROM analysevariation.fichier WHERE libelle = %s", [libelle_analyse])
        an = cur.fetchone()
        an=an
        if libelle_analyse in str(res):
             #msg = "Le login est déjà dans la base"
             flash('Cette analyse est déjà dans la base ! Merci de choisir un autre  !!!','error')  
             return redirect(url_for('upload_file'))
        else:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO analysevariation.fichier (libelle,kpi_id,user_login,equipe_id,date) VALUES (%s,%s,%s,%s,(NOW()))", (libelle_analyse,kpi,user_session,equipe_id))
            cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Ajout analyse',NOW())", (user_session,))
            mysql.connection.commit()
            equipe_id = request.form['equipe_id']
            cur.execute("SELECT email FROM analysevariation.users where idequip=%s", [equipe_id])
            mail = cur.fetchall()
            liste=[]
            for i in mail:
               for x in i.values():
                liste.append(x)
            
            mysql.connection.commit()
            cur.execute("SELECT MONTH(date) as mois FROM analysevariation.fichier WHERE libelle = %s", [libelle_analyse])
            mois = cur.fetchone()
            mois=mois
            cur.execute("SELECT YEAR(date) as annee FROM analysevariation.fichier WHERE libelle = %s", [libelle_analyse])
            an = cur.fetchone()
            an=an
            fromaddr = "sovar@orange-sonatel.com"
            toaddr = liste
            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['Subject'] = "Analyse de la variation pour le mois "
            body = "Bonjour MO , Nous vous informons que l’analyse de la variation pour le mois de {0}_{1} est disponible.\n\n Vous êtes priés vous connecter à SO’VAR pour continuer :  \n \n \n Mail envoyé par un automate, merci de ne pas y répondre!".format(mois,an)
            msg.attach(MIMEText(body, 'plain'))
            s = smtplib.SMTP('10.95.100.10', 25)
            #s.starttls()
            text = msg.as_string()
            s.sendmail(fromaddr, toaddr, text)
            s.quit()
            flash('Les données sont chargées avec succès','success')
            return redirect(url_for('upload_file'))

@app.route('/sonatel-sovar/upload-file', methods=['POST','GET'])
def upload_file():
        cur = mysql.connection.cursor()
        cur.execute("SELECT MAX(idfic) as idfic from analysevariation.fichier ")
        idfic = cur.fetchone()
        idfic=idfic['idfic']
        cur.execute('SELECT * FROM analysevariation.infofichier_charge where idfic=%s ', [idfic])
        results=cur.fetchall()
        cur.execute ("SELECT * from analysevariation.equipe  ")
        equipe= cur.fetchall()
        cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
        logs= cur.fetchall()
        cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
        nbre= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.kpi ")
        metriq= cur.fetchall()
        cur.close()
        dim = date.today() 
        date_saisi= dim.strftime('%d-%m-%Y')
        return render_template('upload-file.html',equipe=equipe,date_saisi=date_saisi,results=results,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq ) 

@app.route('/import_data', methods=['GET', 'POST'])
def import_data():
    if request.method == 'POST':
       idfic = request.form['idfic']
       files = request.files['files']
       if files.filename !='':
           filepath = os.path.join(app.config['UPLOAD_FOLDER'], files.filename)
           files.save(filepath)
           with open(filepath, 'r', errors='ignore', encoding='ISO-8859-1') as fichier:
                names = fichier.readline().strip().split(';')
                colname_pos = dict(zip(names, range(len(names))))
                l=fichier.readline().strip().split(';')
                cur = mysql.connection.cursor()
                
                ch="INSERT INTO `valeurs_fichier` (`conseiller`, `valeur`, `file_id`) values "
                while len(l)>1:
                    print(l)
                    conseiller=l[colname_pos["conseiller"]].replace("'",r"\'")
                    valeur=l[colname_pos["valeur"]].replace("'",r"\'")
                    idfic = request.form['idfic']
                    
                   
                    ch+=f"('{conseiller}','{valeur}','{idfic}'),"
                    l=fichier.readline().strip().split(';')
                ch=ch[:-1]+";"
                cur.execute(ch)
                mysql.connection.commit()
      
    flash("Votre fichier importé avec success!!!!!")
    return redirect(url_for('folders'))


#---------------DEBUT MENU ADMINISTRATION---------------------
@app.route("/sonatel-sovar/utilisateurs", methods=['POST','GET'])
def users():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * FROM analysevariation.user_info order by id ASC")
    users= cur.fetchall()
    result = cur.execute("SELECT * FROM analysevariation.role order by idrole ASC")
    role = cur.fetchall()
    result = cur.execute("SELECT * FROM analysevariation.plateaux order by idplat ASC")
    plateau = cur.fetchall()
    cur.execute ("SELECT * from analysevariation.action_programme ")
    actions= cur.fetchall()
    cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
    logs= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('users.html',equipe=equipe,date_saisi=date_saisi,users=users,role=role,plateau=plateau,actions=actions,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq)  

@app.route("/sonatel-sovar/mon-profil", methods=('GET', 'POST'))
#@login_required
def monprofil():
      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM analysevariation.user_info where username=%s ", [session['so_login']])
      infos= cur.fetchall()
      cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
      logs= cur.fetchall()
      cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
      nbre= cur.fetchall()
      cur.execute ("SELECT * from analysevariation.kpi ")
      metriq= cur.fetchall() 
      cur.execute ("SELECT * from analysevariation.equipe ")
      equipe= cur.fetchall()
      dim = date.today() 
      date_saisi= dim.strftime('%d-%m-%Y')  
      return render_template('monprofil.html',equipe=equipe,date_saisi=date_saisi,infos=infos,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq)

@app.route('/updat_monprfil',methods=['GET','POST'])
def updatprofil():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        
        so_login= request.form['so_login']
        so_email= request.form['so_email']
        so_contact= request.form['so_contact']
       
        cur.execute("UPDATE users set email=%s,contact=%s  WHERE username =%s" , (so_email, so_contact,session['so_login'])) 
        cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Modification profil',NOW())", (so_login,))
        #cur.execute("INSERT INTO recover (id_user,recover) VALUES (%s,%s)", (username,passwordconf))
        cur.connection.commit() 
        flash('Vos données sont modifiées avec succès.','success')
        return redirect(url_for('monprofil'))
    


@app.route('/add_utilisateur', methods=['POST'])
def add_utilisateur():
    if request.method == 'POST':
        user_prenom = request.form['user_prenom']
        user_nom = request.form['user_nom']
        user_login= request.form['user_login']
        user_email= request.form['user_email']
        user_profil= request.form['user_profil']
        user_plateau= request.form['user_plateau']
      
        user_session = request.form['user_session']
        cur = mysql.connection.cursor()
        cur.execute("SELECT username FROM analysevariation.users WHERE username = BINARY %s", [user_login])
        res = cur.fetchone()
        if user_login in str(res):
             #msg = "Le login est déjà dans la base"
             flash('Le login est déjà dans la base ! Merci de choisir un autre login !!!','error')  
             return redirect(url_for('users'))
        else:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO analysevariation.users (nom,prenom,username,email,profil,plateau_id,password,date_prod) VALUES (%s,%s,%s,%s,%s,%s,'e7247759c1633c0f9f1485f3690294a9',(NOW()))", (user_nom,user_prenom,user_login,user_email,user_profil,user_plateau))
            cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Ajout utilisateur',NOW())", (user_session,))
            mysql.connection.commit()
            user_email = request.form['user_email']
            user_login = request.form['user_login']
            user_prenom = request.form['user_prenom']
            user_nom= request.form['user_nom']
            fromaddr = "sovar@orange-sonatel.com"
            toaddr = [user_email]
            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['Subject'] = "Vos accès à l'application SOVAR : Outil d'analyse de la viariation "
            body = "Bonjour %s %s , merci de trouver vos paramétres de connexion à application SOVAR \n\n Lien: http://10.137.56.11:9000/\n\n Votre Login est %s \n\n Votre mot de passe est : %s  \n \n \n Mail envoyé par un automate, merci de ne pas y répondre!" % (user_prenom,user_nom,user_login,'passer')
            msg.attach(MIMEText(body, 'plain'))
            s = smtplib.SMTP('10.95.100.10', 25)
            #s.starttls()
            text = msg.as_string()
            s.sendmail(fromaddr, toaddr, text)
            s.quit()
            flash('Utilisateur créé avec succès','success')
            return redirect(url_for('users'))



@app.route('/update_utilisateur/<string:id>', methods=['GET','POST'])
def update_utilisateur(id):

    if request.method == 'POST':
        
        user_prenom= request.form['user_prenom']
        user_nom = request.form['user_nom']
        user_login = request.form['user_login']
        user_email = request.form['user_email']
        user_profil = request.form['user_profil']
        user_plateau = request.form['user_plateau']
        user_actif = request.form['user_actif']
        user_session=request.form['user_session']
        
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE analysevariation.users
               SET users.nom=%s,users.prenom=%s,users.username=%s,users.email=%s,users.profil_id=%s,users.plateau_id=%s,users.actif=%s
               WHERE users.id=%s 
            """, (user_nom,user_prenom,user_login,user_email,user_profil,user_plateau,user_actif,id))
        cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Modification Utilisateur',NOW())", (user_session,))
       
        flash("Les données utilisateur sont bien mises à jour",'success')
        mysql.connection.commit()
        return redirect(url_for('users'))


@app.route('/delete_utilisateur/<string:id>', methods=['GET'])
def delete_user(id):
        
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM analysevariation.users WHERE id=%s", (id,))
        cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Suppression utilisateur',NOW())", (session['so_login'],))
        mysql.connection.commit()
        flash('Utilisateur supprimé avec succès','success')
        return redirect(url_for('users'))

@app.route("/sonatel-sovar/profils", methods=['POST','GET'])
def profile():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT count(u.id) as nbr, r.name,r.descript as description FROM analysevariation.users  as u,analysevariation.role as r where u.profil_id=r.idrole group by r.name,r.descript  order by r.name ASC")
    roles= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.action_programme ")
    actions= cur.fetchall()
    cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
    logs= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y') 
    return render_template('profils.html',equipe=equipe,date_saisi=date_saisi,roles=roles,actions=actions,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq) 

@app.route("/sonatel-sovar/equipes", methods=['POST','GET'])
def equipes():
    cur = mysql.connection.cursor()
   
    cur.execute ("SELECT * from analysevariation.action_programme ")
    actions= cur.fetchall()
    cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
    logs= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y') 
    return render_template('equipe.html',equipe=equipe,date_saisi=date_saisi,actions=actions,logs=logs,nbre=nbre[0]['nbre'],metriq=metriq) 



@app.route("/sonatel-sovar/transactions", methods=['POST','GET'])
def logs():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * FROM analysevariation.users_logs order by id_transac ASC")
    transacs= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.action_programme ")
    actions= cur.fetchall()
    cur.execute("SELECT * FROM  analysevariation.users_logs  WHERE  users_logs.users_transac =%s ", [session['so_login']] )
    logs= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y') 
    return render_template('logs.html',equipe=equipe,date_saisi=date_saisi,logs=logs,actions=actions,transacs=transacs,nbre=nbre[0]['nbre'],metriq=metriq) 


@app.route('/truncate_bd', methods=['GET'])
def truncate_bd():
        
        cur = mysql.connection.cursor()
        cur.execute("TRUNCATE analysevariation.transaction")
        cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Vider table logs',NOW())", (session['so_login'],))
        mysql.connection.commit()
        flash('les logs de la base sont vidés avec succès','success')
        return redirect(url_for('logs'))


#----------------FIN---------------------------------




#------------------DEMARRAGE SERVEUR FLASK-----------------------
if __name__ == '__main__':
    
    app.run(host='10.137.56.11',port=9000,debug=True)
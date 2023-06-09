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

@login_manager.user_loader
def load_user(user_id):
    # Chargement de l'utilisateur à partir de l'ID de l'utilisateur
    return User.get(user_id)

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


#======================================================PASSWORD=============================================================   
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
        username = request.form['so_login']
        statut = 1
        password = hashlib.md5(password.encode()).hexdigest()
        # password = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt())
        cur.execute("UPDATE users set password =%s,statuts=%s,recover =%s  WHERE id =%s" , (password, statut,passwordconf,session['so_user'])) 
        cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Changement Password',NOW())", (username,))
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
            session['logged'] = True
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
            session['so_equipe'] = account['idequip']
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
                cur.execute("SELECT idequip FROM  users  WHERE  users.id = '%s '", [session['so_user']] )
                accoun = cur.fetchone()
                session['so_equipe'] = accoun['idequip']

                cur.execute("SELECT username FROM  users  WHERE  users.id = '%s '", [session['so_user']] )
                accoun = cur.fetchone()
                session['so_login'] = accoun['username']
                
                dim = date.today() 
                date_saisi= dim.strftime('%d-%m-%Y')
                cur.execute("SELECT MAX(idfic) as idfic FROM analysevariation.fichier")
                idfic = cur.fetchall()  

                if session['so_statut'] == 0:
                      return render_template('change-password.html')
                else:
                    return render_template('dashboard.html',equipe=equipe,idfic=idfic[0]['idfic'],nbre=nbre[0]['nbre'],actions=actions,metriq=metriq,date_saisi=date_saisi )
                
                
               
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
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('dashboard.html',equipe=equipe,date_saisi=date_saisi,causes=causes,actions=actions,nbre=nbre[0]['nbre'],metriq=metriq) 


@app.route("/sonatel-sovar/reporting", methods=['POST','GET'])
def reporting():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.causes order by id ASC")
    causes= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.action_programme ")
    actions =cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    cur.close()
    return render_template('reporting.html',equipe=equipe,date_saisi=date_saisi,causes=causes,actions=actions,nbre=nbre[0]['nbre'],metriq=metriq) 

@app.route("/sonatel-sovar/fichiers", methods=['POST','GET'])
def folders():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.infofichier_charge order by idfic DESC")
    files= cur.fetchall()
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
    return render_template('folders.html',equipe=equipe,date_saisi=date_saisi,files=files,actions=actions,nbre=nbre[0]['nbre'],metriq=metriq) 

@app.route('/update_folder/<string:id>', methods=['GET','POST'])
def update_folder(id):

    if request.method == 'POST':
        
        libelle= request.form['libelle_analyse']
        metrique = request.form['metrique']
        equipe = request.form['equipe']
        user_session=request.form['user_session']
        
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE analysevariation.fichier
               SET fichier.libelle=%s,fichier.kpi_id=%s,fichier.equipe_id=%s
               WHERE fichier.idfic=%s 
            """, (libelle,metrique,equipe,id))
        cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Modification Anlayse',NOW())", (user_session,))
       
        flash("Les données sont bien mises à jour",'success')
        mysql.connection.commit()
        return redirect(url_for('folders'))


@app.route("/sonatel-sovar/dossiers", methods=['POST','GET'])
def dossiers():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT count(*) as nbre,k.idkpi,k.metrique,k.description from analysevariation.kpi as k,analysevariation.fichier as f where k.idkpi=f.kpi_id  group by k.idkpi,k.metrique,k.description order by k.idkpi ASC")
    dossiers= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.action_programme ")
    actions= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier ")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('dossiers.html',equipe=equipe,date_saisi=date_saisi,dossiers=dossiers,actions=actions,nbre=nbre[0]['nbre'],metriq=metriq) 

@app.route('/sonatel-sovar/dossiers/n-<id>', methods=['POST','GET'])
def dossier_fic(id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM analysevariation.infofichier_charge where idkpi=%s ",[id])
        results=cur.fetchall()
       
        cur.execute("SELECT *  FROM analysevariation.kpi where idkpi=%s ",[id])
        kpi=cur.fetchall()
        cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
        nbre= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.kpi ")
        metriq= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.equipe ")
        equipe= cur.fetchall()
        cur.close()
        dim = date.today() 
        date_saisi= dim.strftime('%d-%m-%Y')
        return render_template('dossier_fichier.html',equipe=equipe,date_saisi=date_saisi,results=results,kpi=kpi,nbre=nbre[0]['nbre'],metriq=metriq) 


@app.route("/sonatel-sovar/datasset", methods=['POST','GET'])
def dataset():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.infofichier_charge order by idfic DESC")
    dataset= cur.fetchall()
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
    return render_template('dataset.html',equipe=equipe,actions=actions,date_saisi=date_saisi,dataset=dataset,nbre=nbre[0]['nbre'],metriq=metriq) 

@app.route("/sonatel-sovar/analyses", methods=['POST','GET'])
def analyses():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.infofichier_charge order by idfic DESC")
    dataset= cur.fetchall()
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
    return render_template('analyses.html',equipe=equipe,date_saisi=date_saisi,dataset=dataset,actions=actions,nbre=nbre[0]['nbre'],metriq=metriq) 

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
       engine = create_engine('mysql://root:""@localhost/analysevariation') 
       query =query = "select libelle,date,statut,prenom,nom,metrique,type,description from analysevariation.infofichier_charge "
      
     else :
       engine = create_engine('mysql://root:""@localhost/analysevariation')
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
        # cur.execute("SELECT * FROM analysevariation.valeurs_aberante where file_id=%s and statut='Encours' ",[id])
        cur.execute("SELECT * FROM analysevariation.valeurs_aberante where file_id=%s ",[id])
        results=cur.fetchall()
        cur.execute("SELECT count(*) as nbabber FROM analysevariation.valeurs_aberante where file_id=%s ",[id])
        nbabber=cur.fetchall()
        cur.execute ("SELECT * from analysevariation.action_programme")
        actions= cur.fetchall()
        cur.execute("SELECT libelle,date,metrique,prenom,nom,username,type,periodicite ,description FROM analysevariation.infofichier_charge where idfic=%s ",[id])
        fic=cur.fetchall()
        cur.execute("SELECT * FROM analysevariation.indicateurs where fileid=%s ",[id])
        indic=cur.fetchall()
        cur.execute("SELECT count(*) as va FROM analysevariation.valeurs_aberante where file_id=%s ",[id])
        va=cur.fetchall()
        cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
        nbre= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.kpi ")
        metriq= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.equipe ")
        equipe= cur.fetchall()
        cur.close()
        dim = date.today() 
        date_saisi= dim.strftime('%d-%m-%Y')
        engine = create_engine('mysql://root:''@localhost/analysevariation')	
        query =query = "SELECT valeur FROM analysevariation.valeurs_fichier where file_id='{0}' ".format(id) 
        df = pd.read_sql_query(query, engine)
        media=df['valeur'].median()

        return render_template('valeurs_abberantes.html',equipe=equipe,actions=actions,media=media,indic=indic, date_saisi= date_saisi,results=results,fic=fic,nbre=nbre[0]['nbre'],metriq=metriq,va=va[0]['va'],nbabber=nbabber[0]['nbabber'],id=id ) 



@app.route('/sonatel-sovar/analyser/mesure-<id>', methods=['POST','GET'])
def debuter_AV(id):
        data_exist = 0
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM analysevariation.valeurs_aberante where idvaleur=%s ",[id])
        results=cur.fetchall()
        cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
        nbre= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.kpi ")
        metriq= cur.fetchall()
        cur.execute ("SELECT id,libelle from analysevariation.causes order by id ASC ")
        causes= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.equipe ")
        equipe= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.action_programme ")
        actions =cur.fetchall()
        dim = date.today() 
        date_saisi= dim.strftime('%d-%m-%Y')
        
        #//////////////// plus ////////////
        cur.execute("SELECT * FROM analysevariation.pourquoi1 where valeur_aberrante_id=%s ",[id])
        datacc = cur.fetchone()
        print("datacc===========>",datacc)
        if datacc:
            data_exist=1
            cur.execute('SELECT * FROM analysevariation.probleme where id_mesure=%s ', [id])
            probleme=cur.fetchall()
            cur.execute('SELECT * FROM analysevariation.pourquoi1 where valeur_aberrante_id=%s ', [id])
            pourquoi1=cur.fetchall()
            cur.execute('SELECT * FROM analysevariation.pourquoi2 where valeur_aberrante_id=%s ', [id])
            pourquoi2=cur.fetchall()
            cur.execute('SELECT * FROM analysevariation.pourquoi3 where valeur_aberrante_id=%s ', [id])
            pourquoi3=cur.fetchall()
            cur.execute('SELECT * FROM analysevariation.pourquoi4 where valeur_aberrante_id=%s ', [id])
            pourquoi4=cur.fetchall()
            cur.execute('SELECT * FROM analysevariation.pourquoi5 where valeur_aberrante_id=%s ', [id])
            pourquoi5=cur.fetchall()
            cur.execute('SELECT * FROM analysevariation.axes_analyses where valeur_aberrante_id=%s ', [id])
            axes=cur.fetchall()
            return render_template('debuter_AV.html',data_exist=data_exist,actions=actions,equipe=equipe,causes=causes,date_saisi= date_saisi,results=results,nbre=nbre[0]['nbre'],metriq=metriq,
                              problem=probleme, pourquoi1=pourquoi1,pourquoi2=pourquoi2,pourquoi3=pourquoi3,pourquoi4=pourquoi4,pourquoi5=pourquoi5,axes=axes) 

        cur.close()

        return render_template('debuter_AV.html',actions=actions,equipe=equipe,causes=causes,date_saisi= date_saisi,results=results,nbre=nbre[0]['nbre'],metriq=metriq) 


@app.route('/sonatel-sovar/détails/analyse-<id>', methods=['POST','GET'])
def details_AV(id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM analysevariation.valeurs_aberante where idvaleur=%s ",[id])
        results=cur.fetchall()
        cur.execute("SELECT * FROM analysevariation.info_probleme where id_mesure=%s ",[id])
        problem=cur.fetchall()
        print("--------------------------------problème:",problem)
        cur.execute("SELECT * FROM analysevariation.pourquoi1 where valeur_aberrante_id=%s ",[id])
        p1=cur.fetchall()
        
        cur.execute("SELECT * FROM analysevariation.pourquoi2 where valeur_aberrante_id=%s ",[id])
        p2=cur.fetchall()
        cur.execute("SELECT * FROM analysevariation.pourquoi3 where valeur_aberrante_id=%s ",[id])
        p3=cur.fetchall()
        cur.execute("SELECT * FROM analysevariation.pourquoi4 where valeur_aberrante_id=%s ",[id])
        p4=cur.fetchall()
        cur.execute("SELECT * FROM analysevariation.pourquoi5 where valeur_aberrante_id=%s ",[id])
        p5=cur.fetchall()
        cur.execute("SELECT * FROM analysevariation.axes_analyses where valeur_aberrante_id=%s ",[id])
        axes=cur.fetchall()
        cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
        nbre= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.kpi ")
        metriq= cur.fetchall()
        cur.execute ("SELECT id,libelle from analysevariation.causes order by id ASC ")
        causes= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.equipe ")
        equipe= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.action_programme ")
        actions =cur.fetchall()
        cur.execute("SELECT MONTH(date_analyse) as mois FROM analysevariation.probleme as p where p.id_mesure=%s  ", [id])
        mois=cur.fetchall()
        cur.execute("SELECT YEAR(date_analyse) as annee FROM analysevariation.probleme as p where p.id_mesure=%s  ", [id])
        annee=cur.fetchall()
        
        #recupération des action_individuelle...
        cur.execute('SELECT * FROM analysevariation.action_individuelle where valeur_aberrante_id=%s', [id])
        act_indiv=cur.fetchall()
        cur.close()
        dim = date.today() 
        date_saisi= dim.strftime('%d-%m-%Y')
        
        return render_template('details_AV.html',mois=mois[0]['mois'],annee=annee[0]['annee'],axes=axes,p1=p1,p2=p2,p3=p3,p4=p4,p5=p5,pa=act_indiv,problem=problem,actions=actions,equipe=equipe,causes=causes,date_saisi= date_saisi,results=results,nbre=nbre[0]['nbre'],metriq=metriq ) 

def compter_nbre_pa(id_mesure):
    tab_nbr_pa = []
    total_pa = []
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM analysevariation.action_individuelle where marque=%s and valeur_aberrante_id=%s ',["pa1",id_mesure])
    taille_pa1 = cur.fetchall()
    tab_nbr_pa.append(len(taille_pa1))  
    
    cur.execute('SELECT * FROM analysevariation.action_individuelle where marque=%s and valeur_aberrante_id=%s',["pa2",id_mesure])
    taille_pa2 = cur.fetchall()
    tab_nbr_pa.append(len(taille_pa2))
    
    cur.execute('SELECT * FROM analysevariation.action_individuelle where marque=%s and valeur_aberrante_id=%s',["pa3", id_mesure])
    taille_pa3 = cur.fetchall()
    tab_nbr_pa.append(len(taille_pa3))
    
    cur.execute('SELECT * FROM analysevariation.action_individuelle where marque=%s and valeur_aberrante_id=%s',["pa4", id_mesure])
    taille_pa4 = cur.fetchall()
    tab_nbr_pa.append(len(taille_pa4))
    
    cur.execute('SELECT * FROM analysevariation.action_individuelle where marque=%s and valeur_aberrante_id=%s',["pa5", id_mesure])
    taille_pa5 = cur.fetchall()
    tab_nbr_pa.append(len(taille_pa5))
    
    cur.execute('SELECT * FROM analysevariation.action_individuelle where marque=%s and valeur_aberrante_id=%s',["pa6", id_mesure])
    taille_pa6 = cur.fetchall()
    tab_nbr_pa.append(len(taille_pa6))
    
    total_pa.append(len(taille_pa1)+len(taille_pa2)+len(taille_pa3)+len(taille_pa4)+len(taille_pa5)+len(taille_pa6))
    # print("nbr_pa1=============>",nbr_pa1)
    # print("nbr_pa2=============>",nbr_pa2)
    # print("nbr_pa3=============>",nbr_pa3)
    # print("nbr_pa4=============>",nbr_pa4)
    # print("nbr_pa5=============>",nbr_pa5)
    # print("nbr_pa6=============>",nbr_pa6)
    # print("Tab_nbr_pa=============>",tab_nbr_pa)
    # print("TOTAL=============>",total_pa)
    
    cur.close()
    return tab_nbr_pa,total_pa

@app.route('/sonatel-sovar/analyse/terminer_AV/<string:id>', methods=['GET','POST'])
def terminer_AV(id):
    status = "Terminer"
    cur = mysql.connection.cursor()
    
    
    cur.execute ("""
        UPDATE analysevariation.probleme as p
        SET p.statut=%s WHERE p.id_mesure=%s
    """, (status,id))
    
    print ("--------------------------------id::",id)
    cur.execute("""
               UPDATE analysevariation.valeurs_fichier
               SET valeurs_fichier.statut=%s
               WHERE valeurs_fichier.idvaleur=%s 
            """, (status,id)) 
    # cur.execute ("""
    #     UPDATE analysevariation.valeurs_aberante as a
    #     SET a.statut=%s WHERE a.idvaleur=%s
    # """, (status,id))
    mysql.connection.commit() 
    return redirect(url_for('listeAV'))

    
        
        
        
    
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
        cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
        nbre= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.kpi ")
        metriq= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.equipe ")
        equipe= cur.fetchall()
        cur.execute ("SELECT id,libelle from analysevariation.causes order by id ASC ")
        causes= cur.fetchall()
        
        #recupération des action_individuelle...
        cur.execute('SELECT * FROM analysevariation.action_individuelle where valeur_aberrante_id=%s ', [id_mesure])
        act_indiv=cur.fetchall()
        
        # Répartition des nombres de pa de chaque dernier pourquoi.....tab_nbr_pa
        # et le nombre de pa total.....total_pa
        tab_nbr_pa=compter_nbre_pa(id_mesure)[0]
        total_pa=compter_nbre_pa(id_mesure)[1]
        print("Tab_nbr_pa=============>",tab_nbr_pa)
        print("total_pa=============>",total_pa)
        print("id-mesure===>",id_mesure)
        
        cur.close()
        dim = date.today() 
        date_saisi= dim.strftime('%d-%m-%Y')
        
        #On recupere les donnees poster par ajouteaction.js sur l'url ajouter-action............
        #Insertion des donnees action individuelles au niveau de la base de donnees
        try:
            data_input_action = request.form.get('data')
            data_input_action = data_input_action.split('|')
            data_input_action.pop()
            print("data_input_action :", data_input_action)
            for el in data_input_action:
                act = [elem for elem in el.split(',') if elem!='']
                print('data :' ,act[0])
            #     # k=act[0].split('_')[2].split('.')[0]   
            #     k=act[4].split('_')[2].split('.')[0]           
            #     p5_id = Pourquoi5.query.filter_by(code=f'P5{k}', valeur_aberrante_id=id_va).first().id 
            #     act_exist = ActionIndividuelle.query.filter_by(pourquoi5_id=p5_id,reference_action=act[0]).first() 
            #     if not act_exist:
                cur = mysql.connection.cursor()
                cur.execute ("SELECT probleme from analysevariation.probleme as p where p.id_mesure=%s", [id_mesure])
                probleme= cur.fetchone()
                problem = probleme["probleme"]
                
                cur.execute ("SELECT libelle from analysevariation.valeurs_aberante as v where v.idvaleur=%s", [id_mesure])
                nom_analyse= cur.fetchone()
                nom_anal = nom_analyse["libelle"]

                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO analysevariation.action_individuelle(libelle_action,porteur,echeance,status,commentaire,cause_racine,valeur_aberrante_id,marque,efficacite,probleme,nom_analyse) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (act[0], act[1], act[2],"En attente"," ",act[3],id_mesure,act[4],"Oui/Non",problem,nom_anal))
                mysql.connection.commit() 
                cur.close()
        except AttributeError:
            print('echec de recuperation des elements, erreur attribut')
            
        status = request.form.get('donnee')
        print('status==========>',status)
        
            
        return render_template('saisipa.html',mois=mois[0]['mois'],annee=annee[0]['annee'],pourquoi1=pourquoi1,id_mesure=id_mesure, idproblem= idproblem,problem=problem,causes=causes,date_saisi= date_saisi,results=results,nbre=nbre[0]['nbre'],metriq=metriq,
                           pa=act_indiv,n=tab_nbr_pa,N=total_pa,equipe=equipe,pourquoi2=pourquoi2,pourquoi3=pourquoi3,pourquoi4=pourquoi4,pourquoi5=pourquoi5,axes=axes ) 

    
#----------------SAISI ACTION PROGRAMME ANALYSE---------------------------------
@app.route('/sonatel-sovar/analyse/saisi-ap', methods=['POST','GET'])
def saisiap():
    cur = mysql.connection.cursor()
    cur.execute("SELECT idproblem as idproblem FROM analysevariation.probleme where idproblem=(select MAX(idproblem) from analysevariation.probleme) ")
    idproblem = cur.fetchone()
    idproblem=idproblem['idproblem']
    cur.execute("SELECT * FROM analysevariation.valeurs_aberante as a ,analysevariation.probleme as p where p.idproblem=%s and p.id_mesure=a.idvaleur ", [idproblem])
    results=cur.fetchall()
    cur.execute("SELECT id_mesure as id_mesure FROM analysevariation.probleme where idproblem=(select MAX(idproblem) from analysevariation.probleme) ")
    id_mesure = cur.fetchone()
    id_mesure=id_mesure['id_mesure']
    cur.close()
    
    try:
        data_act_prog = request.form['data']
        data_act_prog = data_act_prog.split('|')
        data_act_prog.pop()
        print("data_act_prog:", data_act_prog)
        
        for el in data_act_prog:
            act_prg = [elem for elem in el.split('{') if elem!='']
            if act_prg:
                for el in act_prg:
                    print("act_prg:", act_prg)
                    actions = [elem for elem in el.split(',') if elem !=''] 
                    print("actionsss:", actions)
                    
                    if actions:
                        cur = mysql.connection.cursor()
                        cur.execute("INSERT INTO analysevariation.action_programme(cause_racine,libelle_action,porteur,echeance,status,commentaire,marque,valeur_aberrante_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (actions[0], actions[1], actions[2], actions[3], 'En attente','', actions[4],id_mesure))
                        mysql.connection.commit()
                    # if actions: 
                    #     k=actions[4].split('_')[2].split('.')[0]  
                    #     print("kkkkkkkkkkk:", k)
                    #     p5_id = Pourquoi5.query.filter_by(code=f'P5{k}', valeur_aberrante_id=int(id_va)).first().id 
                    #     action = ActionProgramme(actions[0], actions[1], actions[2], actions[3], 'En attente','',p5_id)
                    #     print(action)
                    #     db.session.add(action)
                    #     db.session.commit()
                    #     # return redirect(url_for('suivi_action_programme', fichier_id=fichier_id))            
    except:
        print('echec de recuperation des elements')
    
    return render_template('saisiap.html',results=results)


#----------------UPDATE DATA ANALYSE---------------------------------
@app.route('/update_pourquoi/<string:id>', methods=['POST'])
def update_pourquoi(id):
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
        # methodologie= request.form['methodologie']
       
        cur = mysql.connection.cursor()
        
        cur.execute ("""
               UPDATE analysevariation.probleme as p
               SET p.probleme=%s WHERE p.id_mesure=%s 
            """, (probleme,id))
        
        cur.execute ("""
               UPDATE analysevariation.pourquoi1 as p
               SET p.p11=%s,p.p12=%s,p.p13=%s WHERE p.valeur_aberrante_id=%s
            """, (input_1,input_12,input_13,id))
        
        cur.execute ("""
               UPDATE analysevariation.pourquoi2 as p
               SET p.p21=%s,p.p22=%s,p.p23=%s,p.p24=%s,p.p25=%s,p.p26=%s WHERE p.valeur_aberrante_id=%s
            """, (input_2,input_22,input_23,input_24,input_25,input_26,id))
        
        cur.execute ("""
            UPDATE analysevariation.pourquoi3 as p
            SET p.p31=%s,p.p32=%s,p.p33=%s,p.p34=%s,p.p35=%s,p.p36=%s WHERE p.valeur_aberrante_id=%s
        """, (input_3,input_32,input_33,input_34,input_35,input_36,id))
        
        cur.execute ("""
            UPDATE analysevariation.pourquoi4 as p
            SET p.p41=%s,p.p42=%s,p.p43=%s,p.p44=%s,p.p45=%s,p.p46=%s WHERE p.valeur_aberrante_id=%s
        """, (input_4,input_42,input_43,input_44,input_45,input_46,id))
        
        cur.execute ("""
            UPDATE analysevariation.pourquoi5 as p
            SET p.p51=%s,p.p52=%s,p.p53=%s,p.p54=%s,p.p55=%s,p.p56=%s WHERE p.valeur_aberrante_id=%s
        """, (input_5,input_52,input_53,input_54,input_55,input_56,id))
        cur.execute ("""
            UPDATE analysevariation.axes_analyses as a
            SET a.a1=%s,a.a2=%s,a.a3=%s,a.a4=%s,a.a5=%s,a.a6=%s WHERE a.valeur_aberrante_id=%s
        """, (axes_1_analyse, axes_2_analyse, axes_3_analyse, axes_4_analyse, axes_5_analyse, axes_6_analyse,id))

        # cur.execute("UPDATE transaction (users_transac,nom_transac,heure) VALUES (%s,'Insertion données AV',NOW())", (user_session,))
        # cur.execute("""
        #        UPDATE analysevariation.valeurs_fichier
        #        SET valeurs_fichier.statut='Validation'
        #        WHERE valeurs_fichier.idvaleur=%s 
        #     """, (id_mesure,)) 
        mysql.connection.commit()
            
        flash('Les données de votre analyse sont insérées avec succès','success')
        return redirect(url_for('saisipa'))

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
        methodologie = request.form['methodologie_respecte']
       
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO analysevariation.probleme(nom_cc,id_mesure,probleme,fichier_id,user_log,date_analyse,methodologie) VALUES (%s,%s,%s,%s,%s,NOW(),%s)", (nom_cc,id_mesure,probleme,file_id,user_session,methodologie))
        cur.execute("INSERT INTO analysevariation.pourquoi1(p11,p12,p13,valeur_aberrante_id) VALUES (%s,%s,%s,%s)", (input_1,input_12,input_13,id_mesure))
        cur.execute("INSERT INTO analysevariation.pourquoi2(p21,p22,p23,p24,p25,p26,valeur_aberrante_id) VALUES (%s,%s,%s,%s,%s,%s,%s)", (input_2,input_22,input_23,input_24,input_25,input_26,id_mesure))
        cur.execute("INSERT INTO analysevariation.pourquoi3(p31,p32,p33,p34,p35,p36,valeur_aberrante_id) VALUES (%s,%s,%s,%s,%s,%s,%s)", (input_3,input_32,input_33,input_34,input_35,input_36,id_mesure))
        cur.execute("INSERT INTO analysevariation.pourquoi4(p41,p42,p43,p44,p45,p46,valeur_aberrante_id) VALUES (%s,%s,%s,%s,%s,%s,%s)", (input_4,input_42,input_43,input_44,input_45,input_46,id_mesure))
        cur.execute("INSERT INTO analysevariation.pourquoi5(p51,p52,p53,p54,p55,p56,valeur_aberrante_id) VALUES (%s,%s,%s,%s,%s,%s,%s)", (input_5,input_52,input_53,input_54,input_55,input_56,id_mesure))
        cur.execute("INSERT INTO analysevariation.axes_analyses(a1,a2,a3,a4,a5,a6,valeur_aberrante_id) VALUES (%s,%s,%s,%s,%s,%s,%s)", ( axes_1_analyse, axes_2_analyse, axes_3_analyse, axes_4_analyse, axes_5_analyse, axes_6_analyse,id_mesure))
        cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Insertion données AV',NOW())", (user_session,))
        cur.execute("""
               UPDATE analysevariation.valeurs_fichier
               SET valeurs_fichier.statut='Validation'
               WHERE valeurs_fichier.idvaleur=%s 
            """, (id_mesure,))
        
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
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('liste-analyses.html',equipe=equipe,date_saisi=date_saisi,datasett=datasett,actions=actions,nbre=nbre[0]['nbre'],metriq=metriq) 

# Supprimer une analyse...............
@app.route('/delete_AV/<string:id>', methods=['GET'])
def delete_AV(id):
        
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM analysevariation.probleme WHERE idproblem=%s", (id,))
        cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Suppression analyse',NOW())", (session['so_login'],))
        mysql.connection.commit()
        flash('Analyse est supprimé avec succès','success')
        return redirect(url_for('listeAV'))
    

@app.route('/sonatel-sovar/donnees-brutes/AV-<idgss>', methods=['POST','GET'])
def datafic(idgss):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM analysevariation.valeurs_fichier where file_id=%s order by file_id DESC ",[idgss])
        results=cur.fetchall()
        cur.execute("SELECT effectif FROM analysevariation.effectif_fic where file_id=%s ",[idgss])
        effectif=cur.fetchall()
        cur.execute("SELECT libelle,date,metrique,prenom,nom,username,periodicite FROM analysevariation.infofichier_charge where idfic=%s ",[idgss])
        fic=cur.fetchall()
        cur.execute("SELECT idfic,libelle,metrique FROM analysevariation.infofichier_charge ")
        files=cur.fetchall()
        cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
        nbre= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.kpi ")
        metriq= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.equipe ")
        equipe= cur.fetchall()
        cur.close()
        dim = date.today() 
        date_saisi= dim.strftime('%d-%m-%Y') 
        return render_template('datafic.html',effectif=effectif[0]['effectif'],equipe=equipe,files=files,date_saisi=date_saisi,results=results,fic=fic,nbre=nbre[0]['nbre'],metriq=metriq ) 


@app.route("/sonatel-sovar/actions-programme", methods=['POST','GET'])
def programme(): 
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.action_programme order by idprogram ASC")
    programme= cur.fetchall()
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today()
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('actions-programme.html',equipe=equipe,date_saisi=date_saisi,programme=programme,nbre=nbre[0]['nbre'],metriq=metriq) 

@app.route('/update_action_program/<string:id>', methods=['GET','POST'])
def update_action_program(id):
    cur = mysql.connection.cursor() 
    if request.method == 'POST':
        libelle_action= request.form['libelle']
        commentaire = request.form['commentaire']
        porteur=request.form['porteur']
        echeance=request.form['echeance']
        status=request.form['status']
        cur.execute ("""
               UPDATE analysevariation.action_programme as p
               SET p.libelle_action=%s,p.commentaire=%s,p.porteur=%s,p.echeance=%s,p.status=%s
               WHERE p.idprogram=%s 
            """, (libelle_action,commentaire,porteur,echeance,status,id)) 
        
        flash("Les données de l'action programme sont bien mises à jour",'success')
        mysql.connection.commit()
        return redirect(url_for('programme'))

# Supprimer une action programme...............
@app.route('/delete_ap/<string:id>', methods=['GET'])
def delete_ap(id):
        
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM analysevariation.action_programme WHERE idprogram=%s", (id,))
    cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Suppression action',NOW())", (session['so_login'],))
    mysql.connection.commit()
    flash('Action est supprimé avec succès','success')
    return redirect(url_for('programme'))
    

@app.route("/sonatel-sovar/actions-individuelles", methods=['POST','GET'])
def individuelles():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.action_individuelle order by idindiv ASC")
    actions= cur.fetchall()

    # print("Tous les actions===>", actions)
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    # print("Tous les fichiers===>", nbre)
    cur.execute ("SELECT * from analysevariation.valeurs_aberante as v, analysevariation.pourquoi1 as p where v.idvaleur=p.valeur_aberrante_id")
    valeurs= cur.fetchall()
    print("Tous les valeurs===>", len(valeurs)) 
    # print("Tous les valeurs===>", len(val)) 
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.probleme as p, analysevariation.action_individuelle as q where q.valeur_aberrante_id=p.id_mesure")
    problem= cur.fetchall()
    print("\n==============probleme:::==============",problem)
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    
    return render_template('actions-individuelles.html',problem=problem,equipe=equipe,date_saisi=date_saisi,actions=actions,nbre=nbre[0]['nbre'],metriq=metriq)

@app.route('/update_action_indiv/<string:id>', methods=['GET','POST'])
def update_action_indiv(id):
    cur = mysql.connection.cursor() 
    if request.method == 'POST':
        libelle_action= request.form['libelle']
        commentaire = request.form['commentaire']
        porteur=request.form['porteur']
        echeance=request.form['echeance']
        status=request.form['status']
        efficacite=request.form['efficacite']
        cur.execute ("""
               UPDATE analysevariation.action_individuelle as a
               SET a.libelle_action=%s,a.commentaire=%s,a.porteur=%s,a.echeance=%s,a.status=%s,a.efficacite=%s
               WHERE a.idindiv=%s 
            """, (libelle_action,commentaire,porteur,echeance,status,efficacite,id))
        
        flash("Les données de l'action sont bien mises à jour",'success')
        mysql.connection.commit()
        return redirect(url_for('individuelles'))

# Supprimer une action individuelle...............
@app.route('/delete_pa/<string:id>', methods=['GET'])
def delete_pa(id):
        
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM analysevariation.action_individuelle WHERE idindiv=%s", (id,))
    cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Suppression action',NOW())", (session['so_login'],))
    mysql.connection.commit()
    flash('Action est supprimé avec succès','success')
    return redirect(url_for('individuelles'))
    
    
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
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('faq.html',equipe=equipe, date_saisi=date_saisi,actions=actions,nbre=nbre[0]['nbre'],metriq=metriq) 

@app.route("/sonatel-sovar/methodologie", methods=['POST','GET'])
def methode():
    cur = mysql.connection.cursor()
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
    return render_template('methode.html',equipe=equipe,date_saisi=date_saisi,actions=actions,nbre=nbre[0]['nbre'],metriq=metriq) 
#---------------DEBUT MENU PARAMETRAGE---------------------
@app.route("/sonatel-sovar/causes", methods=['POST','GET'])
def cause():
    cur = mysql.connection.cursor()
    cur.execute ("SELECT * from analysevariation.causes order by id ASC")
    causes= cur.fetchall()
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
    return render_template('causes.html',equipe=equipe, date_saisi= date_saisi,causes=causes,actions=actions,nbre=nbre[0]['nbre'],metriq=metriq)  

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
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
   
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('metriques.html',equipe=equipe,date_saisi=date_saisi,metriq=metriq,actions=actions,nbre=nbre[0]['nbre']) 


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
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('plateaux.html',equipe=equipe,date_saisi=date_saisi,plat=plat,nbre=nbre[0]['nbre'],metriq=metriq) 

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

#----------------FIN------------------------------------------

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
            mois=mois["mois"] 

            cur.execute("SELECT libelle  FROM analysevariation.fichier WHERE libelle = %s", [libelle_analyse])
            libelle = cur.fetchone()
            libelle = libelle["libelle"] 
            
            cur.execute("SELECT YEAR(date) as annee FROM analysevariation.fichier WHERE libelle = %s", [libelle_analyse])
            annee = cur.fetchone()
            an=annee["annee"] 
            fromaddr = "sovar@orange-sonatel.com"
            toaddr = liste
            msg = MIMEMultipart()
            
            msg['From'] = fromaddr
            msg['Subject'] = "Analyse de la variation"
            body = "Bonjour MO , Nous vous informons que l’analyse de la variation : {0} pour le mois de {1}_{2} est disponible.\n\n Vous êtes priés vous connecter à SO’VAR pour continuer .  \n\n Lien : http://10.137.56.11:9000/ \n \n  Cordialement,Team SO'VAR \n \n Mail envoyé par un automate, merci de ne pas y répondre!".format(libelle,mois,an)
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
        cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
        nbre= cur.fetchall()
        cur.execute ("SELECT * from analysevariation.kpi ")
        metriq= cur.fetchall()
        cur.close()
        dim = date.today() 
        date_saisi= dim.strftime('%d-%m-%Y')
        return render_template('upload-file.html',equipe=equipe,date_saisi=date_saisi,results=results,nbre=nbre[0]['nbre'],metriq=metriq ) 

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
      
    flash("Votre fichier importé avec success!!!!!",'success')
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
    cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
    nbre= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.kpi ")
    metriq= cur.fetchall()
    cur.execute ("SELECT * from analysevariation.equipe ")
    equipe= cur.fetchall()
    cur.close()
    dim = date.today() 
    date_saisi= dim.strftime('%d-%m-%Y')
    return render_template('users.html',equipe=equipe,date_saisi=date_saisi,users=users,role=role,plateau=plateau,actions=actions,nbre=nbre[0]['nbre'],metriq=metriq)  

@app.route("/sonatel-sovar/mon-profil", methods=('GET', 'POST'))
#@login_required
def monprofil():
      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM analysevariation.user_info where username=%s ", [session['so_login']])
      infos= cur.fetchall()
      cur.execute ("SELECT count(*) as nbre from analysevariation.fichier")
      nbre= cur.fetchall()
      cur.execute ("SELECT * from analysevariation.kpi ")
      metriq= cur.fetchall() 
      cur.execute ("SELECT * from analysevariation.equipe ")
      equipe= cur.fetchall()
      dim = date.today() 
      date_saisi= dim.strftime('%d-%m-%Y')  
      return render_template('monprofil.html',equipe=equipe,date_saisi=date_saisi,infos=infos,nbre=nbre[0]['nbre'],metriq=metriq)

@app.route('/updat_monprfil',methods=['GET','POST'])
def updatprofil():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        
        so_login= request.form['so_login']
        so_email= request.form['so_email']
        so_contact= request.form['so_contact']
        so_password= request.form['so_password']
        password = hashlib.md5(so_password.encode()).hexdigest()
        cur.execute("UPDATE users set email=%s,password=%s,contact=%s,recover=%s  WHERE username =%s" , (so_email,password,so_contact,so_password,session['so_login'])) 
        cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Modification profil',NOW())", (so_login,))
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
            cur.execute("INSERT INTO analysevariation.users (nom,prenom,username,email,profil_id,plateau_id,password,date_prod) VALUES (%s,%s,%s,%s,%s,%s,'e7247759c1633c0f9f1485f3690294a9',(NOW()))", (user_nom,user_prenom,user_login,user_email,user_profil,user_plateau))
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
    return render_template('profils.html',equipe=equipe,date_saisi=date_saisi,roles=roles,actions=actions,nbre=nbre[0]['nbre'],metriq=metriq) 

@app.route("/sonatel-sovar/equipes", methods=['POST','GET'])
def equipes():
    cur = mysql.connection.cursor()
   
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
    return render_template('equipe.html',equipe=equipe,date_saisi=date_saisi,actions=actions,nbre=nbre[0]['nbre'],metriq=metriq) 



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
    return render_template('logs.html',logs=logs,equipe=equipe,date_saisi=date_saisi,actions=actions,transacs=transacs,nbre=nbre[0]['nbre'],metriq=metriq) 


@app.route('/truncate_bd', methods=['GET'])
def truncate_bd():
        
        cur = mysql.connection.cursor()
        cur.execute("TRUNCATE analysevariation.transaction")
        cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Vider table logs',NOW())", (session['so_login'],))
        mysql.connection.commit()
        flash('les logs de la base sont vidés avec succès','success')
        return redirect(url_for('logs'))

#======================================================UPDATE PASSWORD=============================================================   
@app.route('/update_password',methods=['GET','POST'])
def update_pswd():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        
        so_login= request.form['so_login']
        so_password= request.form['so_password']
        password = hashlib.md5(so_password.encode()).hexdigest()
        cur.execute("UPDATE users SET recover = %s WHERE username = %s", (so_password, session['so_login']))
        cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Modification profil',NOW())", (so_login,))
        cur.connection.commit() 
        flash('Vos données sont modifiées avec succès.','success')
        return redirect(url_for('monprofil'))
    

#==============================================REINITIALISATION PROFIL========================================================
@app.route('/reinitialiser_profil',methods=['GET','POST'])
def reinitialiser_profil():
    msg = ''
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        email = request.form['so_email']
        contact = request.form['so_contact']
        username = request.form['so_login']
        statut = 1
        if contact == '':
            flash('le champs est obligatoire ...')
        else:
            cur.execute("UPDATE users set email =%s,statuts=%s,contact =%s  WHERE id =%s" , (email, statut,contact,session['so_user'])) 
            cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Changement Password',NOW())", (username,))
            cur.connection.commit() 
        #return render_template('reinitialiserpwd.html',msg=msg)
        # return render_template('login.html')
    return render_template('dashboard.html')

#==============================================METRIQUES========================================================
@app.route('/update_metrique/<string:id>', methods=['GET','POST'])
def update_metrique(id):
    if request.method == 'POST':
        print('===>DEBUG',request.form)
        metrique= request.form['metrique']
        description = request.form['description']
        types = request.form['type']
        periodicite = request.form['periodicite']
        niveau= request.form['analyse']
        user_session=request.form['user_session']
        
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE analysevariation.kpi
            SET 
            kpi.metrique=%s,
            kpi.description=%s,
            kpi.type=%s,
            kpi.periodicite=%s,
            kpi.niveau=%s
            WHERE kpi.idkpi=%s
        """, (metrique,description, types, periodicite,niveau, id))

        cur.execute("INSERT INTO transaction (users_transac,nom_transac,heure) VALUES (%s,'Modification cause',NOW())", (user_session,))
       
        flash("Les données plateau sont bien mises à jour",'success')
        mysql.connection.commit()
        return redirect(url_for('metriques'))

#----------------FIN---------------------------------




#------------------DEMARRAGE SERVEUR FLASK-----------------------
if __name__ == '__main__':
    
    app.run(host='127.0.0.1',port=9000,debug=True)
# -*- coding: utf-8 -*-
# ----------------------- IMPORTATION DES BIBLIOTHEQUES -------------------
import os
import sqlite3
import webbrowser
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import json




# ----------------------- CREATION DE L APPLICATION -------------------
app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
        DATABASE=os.path.join(app.root_path,'bdd.db'),
        SECRET_KEY='development key',
        USERNAME='admin',
        PASSWORD='default'
    ))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


# ----------------------- METHODE GENERIQUE POUR LA CREATION DE LA BDD  -------------------
def init_db():
    db = get_db()
    with app.open_resource('BDD.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context."""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


# ----------------------- INITIALISATION DE LA BDD  -------------------

def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the resquest."""
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close()



# ----------------------- PAGE INDEX  -------------------
@app.route('/')
def home():
    """ redirige le root vers la page index """
    return redirect(url_for('index'))

@app.route('/index')
def index():
    """ page index """
    return render_template('index.html')


# ----------------------- PAGE CONSULTATION DES FIELDS  -------------------
@app.route('/show_entries')
def show_entries():
    """ Affiche les valeurs de la table fields et les retourne a travers le template show_entries.html """
    """init_db()"""
    db = get_db()
    cur = db.execute('select nom, type, date_debut, coordonnees, filiere, site from fields order by nom asc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/show_entries_triees', methods=['POST'])
def show_entries_triees():
    """ Selectionner les fields de la base de donnee selon leur site et les affiches sur la page template show_entries.html """
    db = get_db()
    cur = db.execute('select nom, type, date_debut, coordonnees, filiere, site from fields where site = ? order by nom asc',[request.form['site']])
    entries = cur.fetchall()
    if entries:
        return render_template('show_entries.html', entries=entries)
    else:
        flash(u'Pas de field sur le site selectionné | Retour à l\'option "---"')
        return redirect(url_for('show_entries'))

# ----------------------- PAGE CONSULTATION DE LA FICHE DE 1 FIELD  -------------------
@app.route('/consulter_field', methods=['GET','POST'])
def consulter_field():
    """ Retourne la page consulter_field.html """
    return render_template('consulter_field.html')

@app.route('/consulter/', methods=['POST','GET'])
def consulter():
    """ Retourne la page template consulter.html correspondant a la fiche du field de la requete prevenant de la page consulter_field.html """
    db = get_db()
    cur = db.execute('select nom, type, date_debut, coordonnees, filiere, site, data_immutable, data_mutable, log from fields where nom = ? and type = ?',[request.form['nom_field'].upper(), request.form['type_field'].title()])
    entries = cur.fetchall()
    if entries:
        return render_template('consulter.html', entries=entries)
    else:
        flash(u'Le field n\'existe pas dans la base de données.')
        print("No such field in the database. Return to consulter_field")
        return redirect(url_for('consulter_field'))

@app.route('/consulter2/', methods=['POST','GET'])
def consulter2():
    db = get_db()
    nom_field = request.form['nom_field']
    cur2 = db.execute('select nom, date, logg from log where nom = ? order by nom asc',[request.form['nom_field']])

    entries2 = cur2.fetchall()
    if entries2:
        return render_template('consulter.html', entries2=entries2)
    else:
        flash(u'Le field n\'existe pas dans la base de données.')
        print("No such field in the database. Return to consulter_field")
        return redirect(url_for('consulter_field'))



# ----------------------- TREATMENT OF INCOMING DATA  -------------------

@app.route('/traitement/')
def parse_request():
    db = get_db()

    page = request.args.get('logg')

    db.execute('insert into log (nom, date, logg) values (?,?,?)',
                 [request.args.get('nom'), request.args.get('date'),request.args.get('logg')])

    with open("/home/Phoenix44/Atlantic/file.txt", "a") as write_file:
        write_file.write(page + '\n')



    db.commit()
    flash(u'La donnée a bien été ajouté à la base de donnée.')
    print("A new value was successfully added to the database.")
    return render_template('time.html')





# ----------------------- AJOUTER FIELD -------------------
@app.route('/add', methods=['POST'])
def add_entry():
    """ Ajoute une valeur field dans la BDD selon la requete envoyee de la page ajouter_field.html """
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    ddn = request.form['dob_day']+'/'+request.form['dob_month']+'/'+request.form['dob_year']
    print(ddn)
    db.execute('insert into fields (nom, type, date_debut, coordonnees, filiere, site) values (?,?,?,?,?,?)',
                 [request.form['nom'].upper(), request.form['type'].title(),ddn,request.form['coordonnees'],request.form['filiere'],request.form['site']])
    db.commit()
    flash(u'La donnée a bien été ajouté à la base de donnée.')
    print("A new value was successfully added to the database.")
    return redirect(url_for('show_entries'))

@app.route('/ajouter_field')
def ajouter_field():
    return render_template('ajouter_field.html')


# ----------------------- SUPPRIMER FIELD VIA LA PAGE SUPPRIMER FIELD -------------------
@app.route('/delete', methods=['POST'])
def delete_entry():
    """ Supprime un field de la base de donnee selon la requete envoyee de la page supprimer_field.html """
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    #tester si le field existe
    cur = db.execute('select * from fields where nom=? and type=?',[request.form['nom'].upper(), request.form['type'].title()])
    field = cur.fetchall()
    if field:
        db.execute('delete from fields where nom=? and type=?',[request.form['nom'].upper(), request.form['type'].title()])
        db.commit()
        flash(u'Le field test a été supprimé.')
        print("The lign was deleted from the database.")
    else:
        flash(u'Ce field test n\'existe pas.')
        print("No such field in the database.")
    return redirect(url_for('show_entries'))

@app.route('/supprimer_field')
def supprimer_field():
    return render_template('supprimer_field.html')

# ----------------------- SUPPRIMER FIELD VIA LE TABLEAU DE LA PAGE SHOW_ENTRIES -------------------
@app.route('/delete_field/<nom>,<type>', methods=['POST'])
def delete_field(nom,type):
    """ supprime un field de la base de donnee par clic sur la croix a cote de son nom dans la page show_entries.html """
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('delete from fields where nom=? and type=?',[nom,type])
    db.commit()
    flash(u'Le field a bien été supprimé.')
    print("The value has been successfully deleted from the database.")
    return redirect(url_for('show_entries'))


# ----------------------- LOGGIN/LOGOUT -------------------
@app.route('/login/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash(u'Vous êtes connecté !')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash(u'Vous êtes déconnecté.')
    return redirect(url_for('index'))

# ----------------------- VOIR LES CONFIGURATIONS DES FIELD TESTS ----------------------------
@app.route('/configuration')
def configuration():
    """ Affiche les configurations de tous les field tests sur la page modifier.html """
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cur=db.execute('select nom, type, data_immutable, status from fields')
    entriesconfiguration = cur.fetchall()
    return render_template('configuration.html', entriesconfiguration=entriesconfiguration)


# ----------------------- MODIFIER LES CONFIGURATIONS DES FIELD TESTS -------------------------
@app.route('/modificationconfigurationfields/<nom>,<type>', methods=['POST'])
def modificationconfigurationfields(nom,type):
    """ Modifie la valeur des attributs immutables et mutables de la configuration du field a partir de la requete envoyee depuis la page modification.html """
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('update fields set data_immutable=?, data_mutable=?, status="active" WHERE nom=? and type = ?',[request.form['immu'],request.form['mut'],nom,type])
    db.commit()

    flash(u'Les données de la configuration ont été correctement modifiées.')
    print("The entry was successfully updated.")
    return redirect(url_for('configuration'))

@app.route('/modification/<nom>,<type>', methods=['GET'])
def modification(nom,type):
    if not session.get('logged_in'):
        abort(401)
    return render_template('modification.html', entriesconfiguration=[type,nom])

# ----------------------- TELECHARGEMENT DE LA CONFIGURATION -------------------------

@app.route('/telecharger/<nom>')
def telecharger(nom):
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cur=db.execute('select nom, type, data_immutable, data_mutable from fields WHERE nom=?',[nom])
    select = cur.fetchall()
    return render_template('telecharger.html', select=select)


# ----------------------- DEMANDER L ADRESSE MAIL DE RÉFÉRENCE D'UN FIELD -------------------------
@app.route('/mailentry', methods=['POST'])
def mail_entry():
    """ Verifie si le field est present dans la base de donnee et si c est le cas retourne son mail sous forme de flash sur la page courante """
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cur = db.execute('select * from fields where nom=? and type=?',[request.form['nom'].upper(), request.form['type'].title()])
    field = cur.fetchall()
    if field:
        a=request.form['type']
        b=request.form['nom']
        flash(a.lower()+'.'+b.lower()+'@etudiant.imt-atlantique.net')
    else:
        flash(u'Désolé, le field indiqué n\'existe pas dans la base de donnée !')
        print("No such entry in the database.")
    return redirect(url_for('mail'))

@app.route('/mail')
def mail():
    if not session.get('logged_in'):
        abort(401)
    return render_template('mail.html')


@app.route('/time/')
def time():


    return render_template('time.html')


#-----CREATION GEENRAL
if __name__ == "__main__":
    print("database created")
    app.jinja_env.auto_reload = True
    app.run(host="127.0.0.1", port=5000, debug=True)
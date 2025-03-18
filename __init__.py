from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import render_template
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3


app = Flask(__name__)                                                                                                                  
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Fonction pour créer une clé "authentifie" dans la session utilisateur
def est_authentifie():
    return session.get('authentifie')

@app.route('/')
def hello_world():
    return render_template('hello.html')
    
#@app.route('/lecture')
#def lecture():
    #if not est_authentifie():
        # Rediriger vers la page d'authentification si l'utilisateur n'est pas authentifié
        #return redirect(url_for('authentification'))

  # Si l'utilisateur est authentifié
    #return "<h2>Bravo, vous êtes authentifié</h2>"

# Retirer la vérification de l'authentification administrateur
@app.route('/lecture')
def lecture():
    # Supprimer la vérification de l'authentification
    return "<h2>Bienvenue, vous pouvez accéder à cette page sans authentification.</h2>"

# Fonction d'authentification pour l'utilisateur "user"
def est_authentifie_user():
    return session.get('authentifie_user')



@app.route('/fiche_nom/', methods=['GET', 'POST'])
def recherche_par_nom():
    if not est_authentifie_user():
        # Si l'utilisateur n'est pas authentifié, rediriger vers la page de connexion
        return redirect(url_for('authentification_user'))

    if request.method == 'POST':
        # Récupérer le nom recherché depuis le formulaire
        nom_recherche = request.form['nom']
        
        # Connexion à la base de données
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Recherche dans la base de données en fonction du nom
        cursor.execute('SELECT * FROM clients WHERE nom LIKE ?', ('%' + nom_recherche + '%',))
        data = cursor.fetchall()
        conn.close()
        
        # Si des résultats sont trouvés
        if data:
            return render_template('read_data.html', data=data)
        else:
            # Si aucun résultat trouvé, afficher un message
            return render_template('read_data.html', message="Aucun client trouvé avec ce nom.")
    
    # Si la méthode est GET, afficher le formulaire de recherche
    return render_template('formulaire.html')


# Page de connexion pour l'utilisateur "user"
@app.route('/authentification_user', methods=['GET', 'POST'])
def authentification_user():
    if request.method == 'POST':
        # Vérifier les identifiants pour l'utilisateur "user"
        if request.form['username'] == 'user' and request.form['password'] == '12345':
            session['authentifie_user'] = True
            # Rediriger vers la route de recherche après une authentification réussie
            return redirect(url_for('recherche_par_nom'))
        else:
            # Afficher un message d'erreur si les identifiants sont incorrects
            return render_template('formulaire_authentification.html', error=True)
    
    return render_template('formulaire_authentification.html', error=False)




#######
@app.route('/ajouter_livre', methods=['GET', 'POST'])
def ajouter_livre():
    if request.method == 'POST':
        titre = request.form['titre']
        auteur = request.form['auteur']
        annee_publication = request.form['annee_publication']

        # Connexion à la base de données
        conn = sqlite3.connect('bibliotheque.db')
        cursor = conn.cursor()

        # Insérer un nouveau livre dans la base de données
        cursor.execute('INSERT INTO livres (titre, auteur, annee_publication) VALUES (?, ?, ?)', 
                       (titre, auteur, annee_publication))
        conn.commit()
        conn.close()

        return redirect('/liste_livres')
    return render_template('ajouter_livre.html')

@app.route('/supprimer_livre/<int:livre_id>', methods=['GET', 'POST'])
def supprimer_livre(livre_id):
    # Connexion à la base de données
    conn = sqlite3.connect('bibliotheque.db')
    cursor = conn.cursor()

    # Supprimer un livre de la base de données
    cursor.execute('DELETE FROM livres WHERE id = ?', (livre_id,))
    conn.commit()
    conn.close()

    return redirect('/liste_livres')


@app.route('/recherche_livre', methods=['GET', 'POST'])
def recherche_livre():
    if request.method == 'POST':
        recherche = request.form['recherche']
        
        # Connexion à la base de données
        conn = sqlite3.connect('bibliotheque.db')
        cursor = conn.cursor()

        # Rechercher un livre par titre ou auteur
        cursor.execute('SELECT * FROM livres WHERE titre LIKE ? OR auteur LIKE ?', 
                       ('%' + recherche + '%', '%' + recherche + '%'))
        livres = cursor.fetchall()
        conn.close()

        return render_template('recherche_livre.html', livres=livres)
    return render_template('recherche_livre.html')

@app.route('/emprunter_livre/<int:livre_id>', methods=['GET', 'POST'])
def emprunter_livre(livre_id):
    if not est_authentifie_user():
        return redirect(url_for('authentification_user'))

    # Connexion à la base de données
    conn = sqlite3.connect('bibliotheque.db')
    cursor = conn.cursor()

    # Vérifier si le livre est déjà emprunté
    cursor.execute('SELECT * FROM emprunts WHERE livre_id = ? AND retour IS NULL', (livre_id,))
    emprunt_exist = cursor.fetchone()

    if emprunt_exist:
        return render_template('erreur_emprunt.html', message="Ce livre est déjà emprunté.")

    # Enregistrer l'emprunt dans la base de données
    cursor.execute('INSERT INTO emprunts (livre_id, utilisateur_id, date_emprunt) VALUES (?, ?, ?)', 
                   (livre_id, session['utilisateur_id'], datetime.now()))
    conn.commit()
    conn.close()

    return redirect('/liste_livres')

@app.route('/inscription_utilisateur', methods=['GET', 'POST'])
def inscription_utilisateur():
    if request.method == 'POST':
        nom = request.form['nom']
        email = request.form['email']
        mot_de_passe = request.form['mot_de_passe']
        
        # Connexion à la base de données
        conn = sqlite3.connect('bibliotheque.db')
        cursor = conn.cursor()

        # Ajouter un nouvel utilisateur
        cursor.execute('INSERT INTO utilisateurs (nom, email, mot_de_passe) VALUES (?, ?, ?)', 
                       (nom, email, mot_de_passe))
        conn.commit()
        conn.close()

        return redirect('/connexion_utilisateur')
    return render_template('inscription_utilisateur.html')

# Lors de l'ajout d'un livre
cursor.execute('INSERT INTO livres (titre, auteur, annee_publication, stock) VALUES (?, ?, ?, ?)', 
               (titre, auteur, annee_publication, stock))

# Lors de l'emprunt
cursor.execute('UPDATE livres SET stock = stock - 1 WHERE id = ?', (livre_id,))

# Lors du retour d'un livre
cursor.execute('UPDATE livres SET stock = stock + 1 WHERE id = ?', (livre_id,))


# Vérification du rôle utilisateur
def est_admin():
    return session.get('role') == 'admin'

@app.route('/admin/ajouter_livre', methods=['GET', 'POST'])
def ajouter_livre_admin():
    if not est_admin():
        return redirect(url_for('accueil'))

    # Code pour ajouter un livre...

#######

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        # Vérifier les identifiants
        if request.form['username'] == 'admin' and request.form['password'] == 'password': # password à cacher par la suite
            session['authentifie'] = True
            # Rediriger vers la route lecture après une authentification réussie
            return redirect(url_for('lecture'))
        else:
            # Afficher un message d'erreur si les identifiants sont incorrects
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    # Rendre le template HTML et transmettre les données
    return render_template('read_data.html', data=data)

@app.route('/consultation/')
def ReadBDD():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/enregistrer_client', methods=['GET'])
def formulaire_client():
    return render_template('formulaire.html')  # afficher le formulaire

@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    nom = request.form['nom']
    prenom = request.form['prenom']

    # Connexion à la base de données
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Exécution de la requête SQL pour insérer un nouveau client
    cursor.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', (1002938, nom, prenom, "ICI"))
    conn.commit()
    conn.close()
    return redirect('/consultation/')  # Rediriger vers la page d'accueil après l'enregistrement

if __name__ == "__main__":
  app.run(debug=True)

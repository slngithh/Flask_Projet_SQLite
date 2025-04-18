from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import render_template
from flask import json
from flask import flash
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

@app.route('/lecture')
def lecture():
    if not est_authentifie():
        # Rediriger vers la page d'authentification si l'utilisateur n'est pas authentifié
        return redirect(url_for('authentification'))

  # Si l'utilisateur est authentifié
    return "<h2>Bravo, vous êtes authentifié</h2>"

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        # Vérifier les identifiants
        if request.form['username'] == 'admin' and request.form['password'] == 'password':  # à ne pas laisser en clair
            session['authentifie'] = True
            flash('Authentification réussie!', 'success')  # Message de succès
            return redirect(url_for('lecture'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')  # Message d'erreur
            return render_template('formulaire_authentification.html')

    return render_template('formulaire_authentification.html')

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    # Rendre le template HTML et transmettre les données
    return render_template('read_data.html', data=data)

@app.route('/fiche_nom/', methods=['GET', 'POST'])
def search_by_name():
    data = []
    if request.method == 'POST':
        search_term = request.form['search_term']
        # Connexion à la base de données
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        # Requête SQL pour une recherche partielle
        cursor.execute('SELECT * FROM clients WHERE nom LIKE ?', (f'%{search_term}%',))
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

# Ajouter un livre
@app.route('/ajouter_livre', methods=['GET', 'POST'])
def ajouter_livre():
    if request.method == 'POST':
        titre = request.form['titre']
        auteur = request.form['auteur']
        annee_publication = request.form['annee_publication']
        quantite = request.form['quantite']

        # Connexion à la base de données des livres
        conn = sqlite3.connect('database2.db')
        cursor = conn.cursor()

        # Requête SQL pour insérer un livre
        cursor.execute('INSERT INTO Livres (Titre, Auteur, Annee_publication, Quantite) VALUES (?, ?, ?, ?)', 
                       (titre, auteur, annee_publication, quantite))
        conn.commit()
        conn.close()

        return redirect('/consultation_livres')  # Rediriger vers la liste des livres après l'ajout

    return render_template('ajouter_livre.html')  # Afficher le formulaire d'ajout

# Supprimer un livre
@app.route('/supprimer_livre/<int:id_livre>', methods=['GET', 'POST'])
def supprimer_livre(id_livre):
    # Connexion à la base de données des livres
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()

    # Requête SQL pour supprimer un livre par ID
    cursor.execute('DELETE FROM Livres WHERE ID_livre = ?', (id_livre,))
    conn.commit()
    conn.close()

    return redirect('/consultation_livres')  # Rediriger vers la liste des livres après la suppression

# Route pour consulter la liste des livres
@app.route('/consultation_livres')
def consultation_livres():
    # Connexion à la base de données des livres
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()

    # Requête SQL pour récupérer tous les livres
    cursor.execute('SELECT * FROM Livres')
    data = cursor.fetchall()
    conn.close()

    # Rendre le template HTML et transmettre les données
    return render_template('consultation_livres.html', data=data)

# Emprunter un livre
@app.route('/emprunter_livre/<int:id_livre>', methods=['GET', 'POST'])
def emprunter_livre(id_livre):
    # Connexion à la base de données des livres
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()

    # Vérifier le stock avant d'emprunter
    cursor.execute('SELECT Quantite FROM Livres WHERE ID_livre = ?', (id_livre,))
    quantite = cursor.fetchone()[0]

    if quantite > 0:
        # Mettre à jour le stock (réduire la quantité de 1)
        cursor.execute('UPDATE Livres SET Quantite = Quantite - 1 WHERE ID_livre = ?', (id_livre,))
        conn.commit()
        message = "Emprunt réussi !"
    else:
        message = "Désolé, ce livre n'est pas disponible."

    conn.close()
    return redirect(url_for('consultation_livres', message=message))  # Passer le message à la page de consultation

                                                                                                                                       
if __name__ == "__main__":
  app.run(debug=True)

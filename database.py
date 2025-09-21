import sqlite3
from sqlite3 import Error
import os

# Chemin de la base de données (dans le dossier data/)
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "offres.db")

def create_connection(db_file):
    """Créer une connexion à la base de données SQLite spécifiée par db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connexion réussie à la base de données {db_file}")
    except Error as e:
        print(e)
    return conn

def create_tables(conn):
    """Créer toutes les tables nécessaires dans la base de données."""
    try:
        cursor = conn.cursor()
        
        # Table principale des offres de stage
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS offres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entreprise TEXT NOT NULL,
            titre TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            email TEXT,
            ville TEXT,
            departement TEXT,
            domaine TEXT,
            type_contrat TEXT,
            remuneration TEXT,
            date_publication DATE,
            duree INTEGER,
            mots_cles TEXT,
            date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Table pour stocker les sources multiples d'une même offre (par exemple, plusieurs plateformes)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sources_offres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            offre_id INTEGER NOT NULL,
            source TEXT NOT NULL,
            url TEXT NOT NULL,
            FOREIGN KEY (offre_id) REFERENCES offres (id)
        );
        """)
        
        # Table pour stocker l'historique des candidatures envoyées
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidatures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            offre_id INTEGER NOT NULL,
            email_envoye TEXT NOT NULL,
            statut TEXT,
            date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            remarques TEXT,
            FOREIGN KEY (offre_id) REFERENCES offres (id)
        );
        """)
        
        # Table de configuration (pour stocker des paramètres globaux, ex. les comptes SMTP, etc.)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parametre TEXT UNIQUE NOT NULL,
            valeur TEXT NOT NULL
        );
        """)
        
        conn.commit()
        print("Tables créées avec succès.")
    except Error as e:
        print("Erreur lors de la création des tables:", e)

def insert_offre(conn, offre):
    """
    Insérer une nouvelle offre dans la table offres.
    """
    sql = """
    INSERT OR IGNORE INTO offres(
        entreprise, titre, url, email, ville, departement, domaine, type_contrat, remuneration, date_publication, duree, mots_cles
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    
    try:
        cur = conn.cursor()
        print(f"Insertion en base : {offre}")  # Debug pour voir les valeurs envoyées
        cur.execute(sql, offre)
        conn.commit()
        print(f"Offre insérée avec succès: {offre[1]}")
        return cur.lastrowid
    except Error as e:
        print("Erreur lors de l'insertion de l'offre:", e)
        return None

def update_email_offre(conn, offre_id, email):
    """Mettre à jour l'email d'une offre donnée par son id."""
    sql = "UPDATE offres SET email = ? WHERE id = ?;"
    try:
        cur = conn.cursor()
        cur.execute(sql, (email, offre_id))
        conn.commit()
        print(f"Email mis à jour pour l'offre {offre_id}")
    except Error as e:
        print("Erreur lors de la mise à jour de l'email:", e)

def fetch_all_offres(conn):
    """Récupérer toutes les offres de la base de données."""
    sql = "SELECT id, entreprise, titre, url, email, ville, departement, domaine, type_contrat, remuneration, date_publication, duree, mots_cles, date_ajout FROM offres;"
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()

def fetch_offre_by_url(conn, url):
    """
    Récupère une offre depuis la base de données à partir de son URL.
    Retourne le tuple correspondant si l'offre existe, sinon None.
    """
    sql = "SELECT * FROM offres WHERE url = ?;"
    cur = conn.cursor()
    cur.execute(sql, (url,))
    return cur.fetchone()

def delete_old_offres(conn, months=3):
    """Supprimer les offres dont la date_publication est antérieure à 'months' mois."""
    sql = "DELETE FROM offres WHERE date_publication < DATE('now', ?);"
    try:
        cur = conn.cursor()
        cur.execute(sql, (f'-{months} months',))
        conn.commit()
        print("Anciennes offres supprimées.")
    except Error as e:
        print("Erreur lors de la suppression des anciennes offres:", e)

def insert_source(conn, offre_id, source, url):
    """Insérer une nouvelle source pour une offre donnée."""
    sql = """
    INSERT INTO sources_offres(offre_id, source, url)
    VALUES (?, ?, ?);
    """
    try:
        cur = conn.cursor()
        cur.execute(sql, (offre_id, source, url))
        conn.commit()
        print(f"Source insérée pour l'offre {offre_id}")
    except Error as e:
        print("Erreur lors de l'insertion de la source:", e)

def fetch_sources_by_offre(conn, offre_id):
    """Récupérer toutes les sources pour une offre donnée."""
    sql = "SELECT * FROM sources_offres WHERE offre_id = ?;"
    cur = conn.cursor()
    cur.execute(sql, (offre_id,))
    return cur.fetchall()

def insert_candidature(conn, offre_id, email_envoye, statut="envoyé", remarques=None):
    """Insérer une nouvelle candidature dans la table candidatures."""
    sql = """
    INSERT INTO candidatures(offre_id, email_envoye, statut, remarques)
    VALUES (?, ?, ?, ?);
    """
    try:
        cur = conn.cursor()
        cur.execute(sql, (offre_id, email_envoye, statut, remarques))
        conn.commit()
        print(f"Candidature pour l'offre {offre_id} enregistrée.")
        return cur.lastrowid
    except Error as e:
        print("Erreur lors de l'insertion de la candidature:", e)
        return None

def fetch_candidatures(conn):
    """Récupérer toutes les candidatures enregistrées."""
    sql = "SELECT * FROM candidatures;"
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()

def search_offres_by_keywords(conn, keywords):
    """
    Rechercher des offres dont le champ 'mots_cles' contient la chaîne de caractères `keywords`.
    
    Paramètres :
      - conn : connexion à la base de données SQLite.
      - keywords : chaîne de caractères à rechercher, par exemple "Informatique" ou "Paris".
    
    Retourne :
      - Une liste de tuples représentant les offres correspondant à la recherche.
      - En cas d'erreur, une liste vide est retournée.
    """
    try:
        sql = "SELECT * FROM offres WHERE mots_cles LIKE ?;"
        cur = conn.cursor()
        cur.execute(sql, (f"%{keywords}%",))
        rows = cur.fetchall()
        return rows
    except Exception as e:
        print("Erreur lors de la recherche des offres par mots-clés:", e)
        return []

def insert_configuration(conn, parametre, valeur):
    """Insérer ou mettre à jour une configuration."""
    sql = """
    INSERT INTO configuration(parametre, valeur)
    VALUES (?, ?)
    ON CONFLICT(parametre) DO UPDATE SET valeur = excluded.valeur;
    """
    try:
        cur = conn.cursor()
        cur.execute(sql, (parametre, valeur))
        conn.commit()
        print(f"Configuration mise à jour: {parametre} = {valeur}")
    except Error as e:
        print("Erreur lors de l'insertion de la configuration:", e)

def fetch_configuration(conn, parametre):
    """Récupérer la valeur d'une configuration donnée."""
    sql = "SELECT valeur FROM configuration WHERE parametre = ?;"
    cur = conn.cursor()
    cur.execute(sql, (parametre,))
    row = cur.fetchone()
    return row[0] if row else None

def clear_database(conn):
    """Supprime toutes les données de la table offres."""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM offres;")
        conn.commit()
        print("Toutes les offres ont été supprimées.")
    except Error as e:
        print("Erreur lors de la suppression des données:", e)

def export_database(conn, export_path):
    """Exporter la base de données (copie du fichier) vers export_path."""
    try:
        with open(DB_PATH, 'rb') as src_file:
            data = src_file.read()
        with open(export_path, 'wb') as dest_file:
            dest_file.write(data)
        print(f"Base exportée avec succès vers {export_path}")
    except Exception as e:
        print("Erreur lors de l'exportation de la base:", e)

if __name__ == "__main__":
    # S'assurer que le dossier data/ existe
    data_folder = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    # Connexion à la base de données et création des tables
    conn = create_connection(DB_PATH)
    if conn is not None:
        create_tables(conn)
        
        # Exemple d'insertion d'une offre
        offre_exemple = (
            "Chronofresh", 
            "Stage en Logistique", 
            "https://www.chronofresh.fr/fr/offre-exemple", 
            "recrutement@chronofresh.fr", 
            "Paris", 
            "75",          #département (ou code) : ici pour l'exemple, "75" pour Paris
            "Logistique", 
            "Stage", 
            "832 - 1 868 € / mois", 
            "2025-03-01 14:30:00",  # Date standardisée
            6,                     # Durée en mois
            "Chronofresh,Stage en Logistique,Paris,Stage"  # mots_cles
        )
        # Note : ici, pour simplifier l'exemple, j'ai mis "75" en département directement
        offre_id = insert_offre(conn, offre_exemple)
        
        # Exemple d'insertion d'une source pour l'offre
        if offre_id:
            insert_source(conn, offre_id, "HelloWork", "https://www.hellowork.com/fr/offres/62049929.html")
        
        # Exemple d'insertion d'une candidature
        if offre_id:
            insert_candidature(conn, offre_id, "recrutement@chronofresh.fr", "envoyé", "Première candidature test")
        
        # Exemple d'insertion de configuration
        insert_configuration(conn, "smtp_gmail", "smtp.gmail.com")
        
        # Afficher quelques enregistrements de la table offres
        print("\n--- Aperçu des offres enregistrées ---")
        offres = fetch_all_offres(conn)
        for offre in offres[:4]:
            print(offre)
        
        # Afficher quelques enregistrements de la table candidatures
        print("\n--- Aperçu des candidatures enregistrées ---")
        candidatures = fetch_candidatures(conn)
        for candidature in candidatures[:4]:
            print(candidature)
        
        conn.close()
    else:
        print("Erreur! Impossible de créer la connexion à la base de données.")

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "offres.db")

def debug_afficher_donnees():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Vérifier le nombre total d'offres
    cur.execute("SELECT COUNT(*) FROM offres;")
    count = cur.fetchone()[0]
    print(f"Total offres en base: {count}")

    # Afficher les 5 premières offres pour voir les valeurs insérées
    cur.execute("SELECT * FROM offres LIMIT 5;")
    offres = cur.fetchall()
    for offre in offres:
        print(offre)

    conn.close()

debug_afficher_donnees()

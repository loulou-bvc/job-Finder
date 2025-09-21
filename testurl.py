import sqlite3

# Connexion à la base de données (change le chemin si nécessaire)
db_path = "/Users/loulou/Documents/programme_admin/data/offres.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Récupérer toutes les URL des offres
cursor.execute("SELECT id, titre, url FROM offres")
resultats = cursor.fetchall()

# Afficher les résultats
for row in resultats:
    print(f"ID: {row[0]}, Titre: {row[1]}, URL: {row[2]}")

# Fermer la connexion
conn.close()

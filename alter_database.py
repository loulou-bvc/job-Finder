import sqlite3
import os

# Chemin vers la base de données
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "offres.db")

def clear_database():
    """Supprime toutes les données des tables sans supprimer la structure."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Désactiver temporairement les contraintes de clé étrangère pour éviter les erreurs
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # Suppression des données de toutes les tables
        tables = ["offres", "sources_offres", "candidatures", "configuration"]
        for table in tables:
            cursor.execute(f"DELETE FROM {table};")
            cursor.execute(f"UPDATE SQLITE_SEQUENCE SET seq = 0 WHERE name='{table}';")  # Réinitialiser les IDs auto-incrémentés
        
        # Réactiver les contraintes de clé étrangère
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        conn.commit()
        conn.close()
        
        print("Toutes les données ont été supprimées avec succès.")
    
    except Exception as e:
        print("Erreur lors de la suppression des données:", e)

if __name__ == "__main__":
    clear_database()

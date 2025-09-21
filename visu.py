import tkinter as tk
from tkinter import ttk
import sqlite3
import os

# Chemin de la base de données (dans le dossier data/)
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "offres.db")

def create_connection(db_file):
    """Crée une connexion à la base de données SQLite."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn

def fetch_offres(conn, limit=50):
    """Récupère les 'limit' premières lignes de la table offres."""
    sql = "SELECT * FROM offres LIMIT ?;"
    cur = conn.cursor()
    cur.execute(sql, (limit,))
    return cur.fetchall()

def create_table_frame(root, columns, data):
    """Crée un Treeview dans 'root' avec les colonnes et insère les données."""
    tree = ttk.Treeview(root, columns=columns, show="headings")
    
    # Définir les titres des colonnes
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")
    
    # Insertion des lignes
    for row in data:
        tree.insert("", tk.END, values=row)
    
    # Ajout d'une scrollbar verticale
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    
    tree.pack(fill=tk.BOTH, expand=True)
    return tree

def main():
    root = tk.Tk()
    root.title("Aperçu de la Base - Offres de Stage")
    root.geometry("1200x400")
    
    # Configuration du style pour améliorer le design
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"), foreground="white", background="#4a7a8c")
    style.configure("Treeview", font=("Helvetica", 10), rowheight=25)
    
    # Définition des colonnes à afficher
    columns = ["id", "entreprise", "titre", "url", "email", "lieu", "domaine", "type_contrat", "date_publication", "duree", "mots_cles", "date_ajout"]
    
    # Connexion à la base et récupération des données
    conn = create_connection(DB_PATH)
    if conn:
        data = fetch_offres(conn, limit=50)
        conn.close()
    else:
        data = []
    
    # Création du tableau
    create_table_frame(root, columns, data)
    
    root.mainloop()

if __name__ == "__main__":
    main()

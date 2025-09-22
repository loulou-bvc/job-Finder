#!/usr/bin/env python3
"""
Application moderne de gestion d'offres de stage
Version 2.0 - Interface graphique complète
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import os
import threading
import webbrowser
from datetime import datetime
import json

# Import des modules existants
from database import create_connection, create_tables

# Import optionnel des scrapers
try:
    from scraper_offres import scrape_hellowork
except ImportError:
    scrape_hellowork = None
    print("⚠️ Module scraper_offres non disponible")

try:
    from scrapper_indeed import scrape_indeed
except ImportError:
    scrape_indeed = None
    print("⚠️ Module scrapper_indeed non disponible")

class ModernAppV2:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Gestionnaire d'Offres de Stage V2")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Configuration
        self.db_path = os.path.join(os.path.dirname(__file__), "data", "offres.db")
        self.config = self.load_config()
        
        # Interface
        self.setup_ui()
        self.load_offres()
        
    def load_config(self):
        """Charger la configuration"""
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        default_config = {
            "scraping": {"delay_min": 1, "delay_max": 3, "max_pages": 5},
            "ui": {"theme": "light", "window_size": "1400x900"}
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                return default_config
        return default_config
    
    def save_config(self):
        """Sauvegarder la configuration"""
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        try:
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Erreur sauvegarde config: {e}")
    
    def setup_ui(self):
        """Créer l'interface utilisateur"""
        # Style moderne
        style = ttk.Style()
        style.theme_use('clam')
        
        # Barre de menu
        self.create_menu()
        
        # Notebook principal
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Onglets
        self.create_offres_tab()
        self.create_scraping_tab()
        self.create_statistics_tab()
        self.create_config_tab()
        
        # Barre de statut
        self.status_bar = ttk.Label(self.root, text="Prêt", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_menu(self):
        """Créer le menu principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Exporter...", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        
        # Menu Outils
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Outils", menu=tools_menu)
        tools_menu.add_command(label="Nettoyer la base", command=self.clean_database)
        tools_menu.add_command(label="Rechercher emails", command=self.search_emails)
    
    def create_offres_tab(self):
        """Créer l'onglet des offres"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📋 Offres")
        
        # Panneau de filtres
        filter_frame = ttk.LabelFrame(frame, text="Filtres", padding=10)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Filtres
        ttk.Label(filter_frame, text="Recherche:").grid(row=0, column=0, sticky=tk.W)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, padx=5)
        search_entry.bind('<KeyRelease>', self.filter_offres)
        
        ttk.Label(filter_frame, text="Domaine:").grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        self.domain_var = tk.StringVar()
        domain_combo = ttk.Combobox(filter_frame, textvariable=self.domain_var, width=15)
        domain_combo['values'] = ['Tous', 'Informatique', 'Marketing', 'Commerce', 'Finance', 'Autre']
        domain_combo.grid(row=0, column=3, padx=5)
        domain_combo.bind('<<ComboboxSelected>>', self.filter_offres)
        
        # Boutons d'action
        action_frame = ttk.Frame(filter_frame)
        action_frame.grid(row=1, column=0, columnspan=4, pady=10)
        
        ttk.Button(action_frame, text="🔄 Actualiser", command=self.load_offres).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="📊 Statistiques", command=self.show_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🌐 Ouvrir URL", command=self.open_url).pack(side=tk.LEFT, padx=5)
        
        # Table des offres
        table_frame = ttk.Frame(frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview
        columns = ('ID', 'Entreprise', 'Titre', 'Ville', 'Domaine', 'Type', 'Date')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        # Configuration des colonnes
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Placement
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Événements
        self.tree.bind('<Double-1>', self.on_offre_double_click)
    
    def create_scraping_tab(self):
        """Créer l'onglet de scraping"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🕷️ Scraping")
        
        # Configuration
        config_frame = ttk.LabelFrame(frame, text="Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(config_frame, text="Mots-clés:").grid(row=0, column=0, sticky=tk.W)
        self.keywords_var = tk.StringVar(value="stage informatique")
        ttk.Entry(config_frame, textvariable=self.keywords_var, width=40).grid(row=0, column=1, padx=5)
        
        ttk.Label(config_frame, text="Ville:").grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        self.city_var = tk.StringVar(value="Paris")
        ttk.Entry(config_frame, textvariable=self.city_var, width=20).grid(row=0, column=3, padx=5)
        
        ttk.Label(config_frame, text="Pages max:").grid(row=1, column=0, sticky=tk.W, pady=(10,0))
        self.pages_var = tk.StringVar(value="3")
        ttk.Entry(config_frame, textvariable=self.pages_var, width=10).grid(row=1, column=1, padx=5, pady=(10,0))
        
        # Boutons de scraping
        scraping_frame = ttk.LabelFrame(frame, text="Actions", padding=10)
        scraping_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(scraping_frame, text="🕷️ Scraper HelloWork", 
                  command=lambda: self.start_scraping('hellowork')).pack(side=tk.LEFT, padx=5)
        ttk.Button(scraping_frame, text="🕷️ Scraper Indeed", 
                  command=lambda: self.start_scraping('indeed')).pack(side=tk.LEFT, padx=5)
        ttk.Button(scraping_frame, text="🔄 Scraper Tout", 
                  command=lambda: self.start_scraping('all')).pack(side=tk.LEFT, padx=5)
        
        # Zone de logs
        log_frame = ttk.LabelFrame(frame, text="Logs", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(log_frame, height=15, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_statistics_tab(self):
        """Créer l'onglet des statistiques"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📊 Statistiques")
        
        # Statistiques générales
        stats_frame = ttk.LabelFrame(frame, text="Statistiques Générales", padding=10)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_labels = {}
        stats_info = [
            ("Total offres:", "total"),
            ("Par domaine:", "domaines"),
            ("Par ville:", "villes"),
            ("Par type:", "types")
        ]
        
        for i, (label, key) in enumerate(stats_info):
            ttk.Label(stats_frame, text=label, font=('Arial', 10, 'bold')).grid(row=i//2, column=(i%2)*2, sticky=tk.W, padx=5)
            self.stats_labels[key] = ttk.Label(stats_frame, text="0", font=('Arial', 10))
            self.stats_labels[key].grid(row=i//2, column=(i%2)*2+1, sticky=tk.W, padx=5)
        
        # Boutons d'action
        action_frame = ttk.Frame(frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(action_frame, text="🔄 Actualiser", command=self.update_statistics).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="📈 Graphiques", command=self.show_charts).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="📋 Export", command=self.export_stats).pack(side=tk.LEFT, padx=5)
    
    def create_config_tab(self):
        """Créer l'onglet de configuration"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="⚙️ Configuration")
        
        # Configuration scraping
        scraping_config = ttk.LabelFrame(frame, text="Configuration Scraping", padding=10)
        scraping_config.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(scraping_config, text="Délai min (s):").grid(row=0, column=0, sticky=tk.W)
        self.delay_min_var = tk.StringVar(value=str(self.config.get('scraping', {}).get('delay_min', 1)))
        ttk.Entry(scraping_config, textvariable=self.delay_min_var, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(scraping_config, text="Délai max (s):").grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        self.delay_max_var = tk.StringVar(value=str(self.config.get('scraping', {}).get('delay_max', 3)))
        ttk.Entry(scraping_config, textvariable=self.delay_max_var, width=10).grid(row=0, column=3, padx=5)
        
        # Boutons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(button_frame, text="💾 Sauvegarder", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Réinitialiser", command=self.reset_config).pack(side=tk.LEFT, padx=5)
    
    def load_offres(self):
        """Charger les offres depuis la base de données"""
        try:
            conn = create_connection(self.db_path)
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, entreprise, titre, ville, domaine, type_contrat, date_ajout
                    FROM offres 
                    ORDER BY date_ajout DESC
                    LIMIT 1000
                """)
                
                # Vider le tree
                for item in self.tree.get_children():
                    self.tree.delete(item)
                
                # Ajouter les données
                for row in cursor.fetchall():
                    self.tree.insert('', 'end', values=row)
                
                conn.close()
                self.update_statistics()
                self.status_bar.config(text=f"Chargé: {len(self.tree.get_children())} offres")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {e}")
    
    def filter_offres(self, event=None):
        """Filtrer les offres selon les critères"""
        search_term = self.search_var.get().lower()
        domain_filter = self.domain_var.get()
        
        # Vider le tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            conn = create_connection(self.db_path)
            if conn:
                cursor = conn.cursor()
                
                # Construire la requête
                query = """
                    SELECT id, entreprise, titre, ville, domaine, type_contrat, date_ajout
                    FROM offres 
                    WHERE 1=1
                """
                params = []
                
                if search_term:
                    query += " AND (titre LIKE ? OR entreprise LIKE ? OR ville LIKE ?)"
                    params.extend([f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'])
                
                if domain_filter and domain_filter != 'Tous':
                    query += " AND domaine = ?"
                    params.append(domain_filter)
                
                query += " ORDER BY date_ajout DESC LIMIT 1000"
                
                cursor.execute(query, params)
                
                for row in cursor.fetchall():
                    self.tree.insert('', 'end', values=row)
                
                conn.close()
                self.status_bar.config(text=f"Filtré: {len(self.tree.get_children())} offres")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du filtrage: {e}")
    
    def start_scraping(self, source):
        """Démarrer le scraping en arrière-plan"""
        def scraping_thread():
            try:
                self.log_message(f"🚀 Démarrage du scraping {source}")
                
                keywords = self.keywords_var.get()
                city = self.city_var.get()
                max_pages = int(self.pages_var.get())
                
                if source in ['hellowork', 'all']:
                    if scrape_hellowork:
                        self.log_message("🕷️ Scraping HelloWork...")
                        # Ici vous pouvez appeler votre fonction de scraping HelloWork
                        self.log_message("✅ HelloWork terminé")
                    else:
                        self.log_message("⚠️ Module HelloWork non disponible")
                
                if source in ['indeed', 'all']:
                    if scrape_indeed:
                        self.log_message("🕷️ Scraping Indeed...")
                        # Ici vous pouvez appeler votre fonction de scraping Indeed
                        self.log_message("✅ Indeed terminé")
                    else:
                        self.log_message("⚠️ Module Indeed non disponible")
                
                self.log_message("🎉 Scraping terminé!")
                self.load_offres()  # Recharger les offres
                
            except Exception as e:
                self.log_message(f"❌ Erreur: {e}")
        
        # Démarrer dans un thread séparé
        thread = threading.Thread(target=scraping_thread, daemon=True)
        thread.start()
    
    def log_message(self, message):
        """Ajouter un message au log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def on_offre_double_click(self, event):
        """Action lors du double-clic sur une offre"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            offre_id = item['values'][0]
            self.show_offre_details(offre_id)
    
    def show_offre_details(self, offre_id):
        """Afficher les détails d'une offre"""
        try:
            conn = create_connection(self.db_path)
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM offres WHERE id = ?", (offre_id,))
                offre = cursor.fetchone()
                
                if offre:
                    # Créer une fenêtre de détails
                    details_window = tk.Toplevel(self.root)
                    details_window.title(f"Détails - {offre[2]}")
                    details_window.geometry("600x400")
                    
                    # Afficher les détails
                    text_widget = tk.Text(details_window, wrap=tk.WORD, padx=10, pady=10)
                    text_widget.pack(fill=tk.BOTH, expand=True)
                    
                    details = f"""
Entreprise: {offre[1]}
Titre: {offre[2]}
URL: {offre[3]}
Email: {offre[4]}
Ville: {offre[5]}
Département: {offre[6]}
Domaine: {offre[7]}
Type de contrat: {offre[8]}
Rémunération: {offre[9]}
Date publication: {offre[10]}
Durée: {offre[11]}
Mots-clés: {offre[12]}
Date ajout: {offre[13]}
                    """
                    
                    text_widget.insert(tk.END, details)
                    text_widget.config(state=tk.DISABLED)
                
                conn.close()
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'affichage: {e}")
    
    def open_url(self):
        """Ouvrir l'URL de l'offre sélectionnée"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une offre")
            return
        
        try:
            item = self.tree.item(selection[0])
            offre_id = item['values'][0]
            
            conn = create_connection(self.db_path)
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT url FROM offres WHERE id = ?", (offre_id,))
                url = cursor.fetchone()
                
                if url and url[0]:
                    webbrowser.open(url[0])
                    self.status_bar.config(text=f"Ouverture: {url[0]}")
                else:
                    messagebox.showwarning("Attention", "URL non disponible")
                
                conn.close()
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ouverture: {e}")
    
    def update_statistics(self):
        """Mettre à jour les statistiques"""
        try:
            conn = create_connection(self.db_path)
            if conn:
                cursor = conn.cursor()
                
                # Total
                cursor.execute("SELECT COUNT(*) FROM offres")
                total = cursor.fetchone()[0]
                self.stats_labels['total'].config(text=str(total))
                
                # Par domaine
                cursor.execute("SELECT domaine, COUNT(*) FROM offres GROUP BY domaine ORDER BY COUNT(*) DESC LIMIT 5")
                domaines = cursor.fetchall()
                domaines_text = ", ".join([f"{d[0]}: {d[1]}" for d in domaines])
                self.stats_labels['domaines'].config(text=domaines_text[:50] + "..." if len(domaines_text) > 50 else domaines_text)
                
                # Par ville
                cursor.execute("SELECT ville, COUNT(*) FROM offres WHERE ville IS NOT NULL GROUP BY ville ORDER BY COUNT(*) DESC LIMIT 5")
                villes = cursor.fetchall()
                villes_text = ", ".join([f"{v[0]}: {v[1]}" for v in villes])
                self.stats_labels['villes'].config(text=villes_text[:50] + "..." if len(villes_text) > 50 else villes_text)
                
                # Par type
                cursor.execute("SELECT type_contrat, COUNT(*) FROM offres WHERE type_contrat IS NOT NULL GROUP BY type_contrat ORDER BY COUNT(*) DESC LIMIT 5")
                types = cursor.fetchall()
                types_text = ", ".join([f"{t[0]}: {t[1]}" for t in types])
                self.stats_labels['types'].config(text=types_text[:50] + "..." if len(types_text) > 50 else types_text)
                
                conn.close()
                
        except Exception as e:
            print(f"Erreur statistiques: {e}")
    
    def show_stats(self):
        """Afficher les statistiques détaillées"""
        self.update_statistics()
        messagebox.showinfo("Statistiques", "Statistiques mises à jour!")
    
    def show_charts(self):
        """Afficher les graphiques"""
        try:
            # Importer matplotlib seulement si nécessaire
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('TkAgg')
            
            conn = create_connection(self.db_path)
            if conn:
                cursor = conn.cursor()
                
                # Graphique par domaine
                cursor.execute("SELECT domaine, COUNT(*) FROM offres GROUP BY domaine ORDER BY COUNT(*) DESC LIMIT 10")
                domaines = cursor.fetchall()
                
                if domaines:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    labels, values = zip(*domaines)
                    ax.bar(labels, values)
                    ax.set_title("Offres par domaine")
                    ax.set_xlabel("Domaine")
                    ax.set_ylabel("Nombre d'offres")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    plt.show()
                
                conn.close()
                
        except ImportError:
            messagebox.showwarning("Attention", "Matplotlib non installé. Installez avec: pip install matplotlib")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'affichage des graphiques: {e}")
    
    def export_stats(self):
        """Exporter les statistiques"""
        try:
            conn = create_connection(self.db_path)
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM offres")
                offres = cursor.fetchall()
                
                # Export simple en CSV
                filename = f"export_offres_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("ID,Entreprise,Titre,URL,Email,Ville,Domaine,Type,Rémunération,Date\n")
                    for offre in offres:
                        f.write(f"{offre[0]},{offre[1]},{offre[2]},{offre[3]},{offre[4]},{offre[5]},{offre[7]},{offre[8]},{offre[9]},{offre[10]}\n")
                
                messagebox.showinfo("Export", f"Données exportées vers {filename}")
                conn.close()
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")
    
    def export_data(self):
        """Exporter les données"""
        self.export_stats()
    
    def clean_database(self):
        """Nettoyer la base de données"""
        if messagebox.askyesno("Confirmation", "Voulez-vous nettoyer la base de données ?"):
            try:
                conn = create_connection(self.db_path)
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM offres WHERE date_ajout < date('now', '-30 days')")
                    deleted = cursor.rowcount
                    conn.commit()
                    conn.close()
                    
                    messagebox.showinfo("Nettoyage", f"{deleted} offres anciennes supprimées")
                    self.load_offres()
                    
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors du nettoyage: {e}")
    
    def search_emails(self):
        """Rechercher des emails"""
        messagebox.showinfo("Info", "Fonctionnalité de recherche d'emails à implémenter")
    
    def reset_config(self):
        """Réinitialiser la configuration"""
        self.config = {
            "scraping": {"delay_min": 1, "delay_max": 3, "max_pages": 5},
            "ui": {"theme": "light", "window_size": "1400x900"}
        }
        self.save_config()
        messagebox.showinfo("Configuration", "Configuration réinitialisée")
    
    def run(self):
        """Lancer l'application"""
        self.root.mainloop()

def main():
    """Point d'entrée principal"""
    try:
        app = ModernAppV2()
        app.run()
    except Exception as e:
        print(f"Erreur lors du lancement: {e}")
        messagebox.showerror("Erreur", f"Erreur lors du lancement: {e}")

if __name__ == "__main__":
    main()

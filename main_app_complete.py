#!/usr/bin/env python3
"""
Application complète de gestion d'offres de stage
Version avec toutes les fonctionnalités avancées
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import os
import threading
import webbrowser
from datetime import datetime
import json

# Import des modules
from database import create_connection, create_tables
from candidature_manager import CandidatureManager
from candidature_tracker import CandidatureTracker
from email_manager import EmailManager
from charts_manager import ChartsManager
from filter_manager import FilterManager

class CompleteApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Gestionnaire d'Offres de Stage - Version Complète")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Configuration
        self.db_path = os.path.join(os.path.dirname(__file__), "data", "offres.db")
        self.config = self.load_config()
        
        # Managers
        self.candidature_manager = CandidatureManager()
        self.candidature_tracker = CandidatureTracker()
        self.email_manager = EmailManager()
        self.charts_manager = ChartsManager()
        self.filter_manager = FilterManager()
        
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
        self.create_candidatures_tab()
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
        tools_menu.add_command(label="Rechercher emails", command=self.search_emails)
        tools_menu.add_command(label="Nettoyer la base", command=self.clean_database)
    
    def create_offres_tab(self):
        """Créer l'onglet des offres"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📋 Offres")
        
        # Panneau de filtres
        filter_frame = ttk.LabelFrame(frame, text="Filtres Avancés", padding=10)
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
        ttk.Button(action_frame, text="📧 Rechercher Email", command=self.search_emails_for_offre).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="📝 Candidature", command=self.create_candidature).pack(side=tk.LEFT, padx=5)
        
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
    
    def create_candidatures_tab(self):
        """Créer l'onglet des candidatures"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📝 Candidatures")
        
        # Panneau de contrôle
        control_frame = ttk.LabelFrame(frame, text="Gestion des Candidatures", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="➕ Nouvelle Candidature", command=self.add_candidature).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🔄 Actualiser", command=self.load_candidatures).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📊 Statistiques", command=self.show_candidature_stats).pack(side=tk.LEFT, padx=5)
        
        # Table des candidatures
        table_frame = ttk.Frame(frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview
        columns = ('ID', 'Entreprise', 'Poste', 'Date', 'Statut', 'Type')
        self.candidatures_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configuration des colonnes
        for col in columns:
            self.candidatures_tree.heading(col, text=col)
            self.candidatures_tree.column(col, width=120, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.candidatures_tree.yview)
        self.candidatures_tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Placement
        self.candidatures_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Événements
        self.candidatures_tree.bind('<Double-1>', self.on_candidature_double_click)
    
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
            ("Total candidatures:", "candidatures"),
            ("Taux de réponse:", "taux_reponse")
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
        
        # Configuration générale
        general_config = ttk.LabelFrame(frame, text="Configuration Générale", padding=10)
        general_config.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(general_config, text="Taille fenêtre:").grid(row=0, column=0, sticky=tk.W)
        self.window_size_var = tk.StringVar(value="1400x900")
        ttk.Entry(general_config, textvariable=self.window_size_var, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(general_config, text="Thème:").grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        self.theme_var = tk.StringVar(value="light")
        theme_combo = ttk.Combobox(general_config, textvariable=self.theme_var, width=10)
        theme_combo['values'] = ['light', 'dark']
        theme_combo.grid(row=0, column=3, padx=5)
        
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
    
    def load_candidatures(self):
        """Charger les candidatures"""
        try:
            candidatures = self.candidature_tracker.get_all_candidatures()
            
            # Vider le tree
            for item in self.candidatures_tree.get_children():
                self.candidatures_tree.delete(item)
            
            # Ajouter les données
            for candidature in candidatures:
                self.candidatures_tree.insert('', 'end', values=(
                    candidature['id'],
                    candidature['entreprise'],
                    candidature['poste'],
                    candidature['date_candidature'],
                    candidature['statut'],
                    candidature['type_candidature']
                ))
            
            self.status_bar.config(text=f"Chargé: {len(candidatures)} candidatures")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des candidatures: {e}")
    
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
    
    def on_offre_double_click(self, event):
        """Action lors du double-clic sur une offre"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            offre_id = item['values'][0]
            self.show_offre_details(offre_id)
    
    def on_candidature_double_click(self, event):
        """Action lors du double-clic sur une candidature"""
        selection = self.candidatures_tree.selection()
        if selection:
            item = self.candidatures_tree.item(selection[0])
            candidature_id = item['values'][0]
            self.show_candidature_details(candidature_id)
    
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
    
    def show_candidature_details(self, candidature_id):
        """Afficher les détails d'une candidature"""
        try:
            candidature = self.candidature_tracker.get_candidature(candidature_id)
            if candidature:
                # Créer une fenêtre de détails
                details_window = tk.Toplevel(self.root)
                details_window.title(f"Candidature - {candidature['entreprise']}")
                details_window.geometry("500x400")
                
                # Afficher les détails
                text_widget = tk.Text(details_window, wrap=tk.WORD, padx=10, pady=10)
                text_widget.pack(fill=tk.BOTH, expand=True)
                
                details = f"""
Entreprise: {candidature['entreprise']}
Poste: {candidature['poste']}
URL: {candidature['url']}
Email contact: {candidature['email_contact']}
Date candidature: {candidature['date_candidature']}
Statut: {candidature['statut']}
Type: {candidature['type_candidature']}
Mode envoi: {candidature['mode_envoi']}
Date relance: {candidature['date_relance']}
Notes: {candidature['notes']}
                """
                
                text_widget.insert(tk.END, details)
                text_widget.config(state=tk.DISABLED)
                
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
    
    def search_emails_for_offre(self):
        """Rechercher des emails pour l'offre sélectionnée"""
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
                cursor.execute("SELECT * FROM offres WHERE id = ?", (offre_id,))
                offre = cursor.fetchone()
                
                if offre:
                    offre_data = {
                        'entreprise': offre[1],
                        'url': offre[3]
                    }
                    
                    # Rechercher les emails
                    results = self.email_manager.search_emails_for_entreprise(
                        offre_data['entreprise'], 
                        offre_data['url']
                    )
                    
                    if results['emails']:
                        # Afficher les résultats
                        email_window = tk.Toplevel(self.root)
                        email_window.title(f"Emails trouvés - {offre_data['entreprise']}")
                        email_window.geometry("500x300")
                        
                        text_widget = tk.Text(email_window, wrap=tk.WORD, padx=10, pady=10)
                        text_widget.pack(fill=tk.BOTH, expand=True)
                        
                        email_text = "Emails trouvés:\n\n"
                        for email in results['emails']:
                            email_text += f"• {email}\n"
                        
                        if results['sources']:
                            email_text += "\nSources:\n"
                            for source in results['sources']:
                                email_text += f"• {source}\n"
                        
                        text_widget.insert(tk.END, email_text)
                        text_widget.config(state=tk.DISABLED)
                    else:
                        messagebox.showinfo("Info", "Aucun email trouvé pour cette entreprise")
                
                conn.close()
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la recherche d'emails: {e}")
    
    def create_candidature(self):
        """Créer une candidature pour l'offre sélectionnée"""
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
                cursor.execute("SELECT * FROM offres WHERE id = ?", (offre_id,))
                offre = cursor.fetchone()
                
                if offre:
                    # Créer une candidature
                    candidature_data = {
                        'offre_id': offre_id,
                        'entreprise': offre[1],
                        'poste': offre[2],
                        'url': offre[3],
                        'email_contact': offre[4],
                        'date_candidature': datetime.now().date(),
                        'statut': 'Envoyée',
                        'type_candidature': 'Spontanée',
                        'mode_envoi': 'Email',
                        'notes': 'Candidature créée depuis l\'application'
                    }
                    
                    candidature_id = self.candidature_tracker.add_candidature(candidature_data)
                    
                    if candidature_id > 0:
                        messagebox.showinfo("Succès", "Candidature créée avec succès!")
                        self.load_candidatures()
                    else:
                        messagebox.showerror("Erreur", "Erreur lors de la création de la candidature")
                
                conn.close()
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création de la candidature: {e}")
    
    def add_candidature(self):
        """Ajouter une nouvelle candidature"""
        dialog = CandidatureDialog(self.root)
        if dialog.result:
            candidature_id = self.candidature_tracker.add_candidature(dialog.result)
            if candidature_id > 0:
                messagebox.showinfo("Succès", "Candidature ajoutée avec succès!")
                self.load_candidatures()
            else:
                messagebox.showerror("Erreur", "Erreur lors de l'ajout de la candidature")
    
    def update_statistics(self):
        """Mettre à jour les statistiques"""
        try:
            # Statistiques des offres
            conn = create_connection(self.db_path)
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM offres")
                total_offres = cursor.fetchone()[0]
                conn.close()
            
            # Statistiques des candidatures
            candidature_stats = self.candidature_tracker.get_statistics()
            
            self.stats_labels['total'].config(text=str(total_offres))
            self.stats_labels['candidatures'].config(text=str(candidature_stats['total']))
            self.stats_labels['taux_reponse'].config(text=f"{candidature_stats['taux_reponse']}%")
            
        except Exception as e:
            print(f"Erreur statistiques: {e}")
    
    def show_stats(self):
        """Afficher les statistiques détaillées"""
        self.update_statistics()
        messagebox.showinfo("Statistiques", "Statistiques mises à jour!")
    
    def show_candidature_stats(self):
        """Afficher les statistiques des candidatures"""
        try:
            stats = self.candidature_tracker.get_statistics()
            
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Statistiques des Candidatures")
            stats_window.geometry("400x300")
            
            text_widget = tk.Text(stats_window, wrap=tk.WORD, padx=10, pady=10)
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            stats_text = f"""
Statistiques des Candidatures:

Total: {stats['total']}
Taux de réponse: {stats['taux_reponse']}%

Par statut:
"""
            for statut, count in stats['statuts'].items():
                stats_text += f"• {statut}: {count}\n"
            
            if stats['par_mois']:
                stats_text += "\nPar mois:\n"
                for mois, count in stats['par_mois'].items():
                    stats_text += f"• {mois}: {count}\n"
            
            text_widget.insert(tk.END, stats_text)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'affichage des statistiques: {e}")
    
    def show_charts(self):
        """Afficher les graphiques"""
        try:
            # Récupérer les données
            conn = create_connection(self.db_path)
            if conn:
                cursor = conn.cursor()
                
                # Graphique par domaine
                cursor.execute("SELECT domaine, COUNT(*) FROM offres GROUP BY domaine ORDER BY COUNT(*) DESC LIMIT 10")
                domaines = dict(cursor.fetchall())
                
                if domaines:
                    fig = self.charts_manager.create_domain_chart(domaines)
                    fig.show()
                
                conn.close()
                
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
    
    def search_emails(self):
        """Rechercher des emails"""
        messagebox.showinfo("Info", "Utilisez le bouton 'Rechercher Email' sur une offre sélectionnée")
    
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
    
    def save_config(self):
        """Sauvegarder la configuration"""
        self.config['ui']['window_size'] = self.window_size_var.get()
        self.config['ui']['theme'] = self.theme_var.get()
        
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        try:
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            messagebox.showinfo("Configuration", "Configuration sauvegardée!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur sauvegarde: {e}")
    
    def reset_config(self):
        """Réinitialiser la configuration"""
        self.config = {
            "scraping": {"delay_min": 1, "delay_max": 3, "max_pages": 5},
            "ui": {"theme": "light", "window_size": "1400x900"}
        }
        self.window_size_var.set("1400x900")
        self.theme_var.set("light")
        messagebox.showinfo("Configuration", "Configuration réinitialisée")
    
    def run(self):
        """Lancer l'application"""
        self.root.mainloop()

class CandidatureDialog:
    def __init__(self, parent):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Ajouter une candidature")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Variables
        self.entreprise_var = tk.StringVar()
        self.poste_var = tk.StringVar()
        self.url_var = tk.StringVar()
        self.email_contact_var = tk.StringVar()
        self.statut_var = tk.StringVar(value="Envoyée")
        self.type_candidature_var = tk.StringVar(value="Spontanée")
        self.mode_envoi_var = tk.StringVar()
        self.notes_var = tk.StringVar()
        
        self.create_widgets()
        
        # Centrer la fenêtre
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"500x600+{x}+{y}")
    
    def create_widgets(self):
        """Créer les widgets"""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Champs
        fields = [
            ("Entreprise:", self.entreprise_var),
            ("Poste:", self.poste_var),
            ("URL:", self.url_var),
            ("Email contact:", self.email_contact_var),
            ("Statut:", self.statut_var),
            ("Type:", self.type_candidature_var),
            ("Mode envoi:", self.mode_envoi_var),
            ("Notes:", self.notes_var)
        ]
        
        for i, (label, var) in enumerate(fields):
            ttk.Label(main_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            
            if label == "Statut:":
                combo = ttk.Combobox(main_frame, textvariable=var, width=30)
                combo['values'] = ['Envoyée', 'Relancée', 'Entretien', 'Acceptée', 'Refusée']
                combo.grid(row=i, column=1, sticky=tk.W+tk.E, pady=2, padx=(5,0))
            elif label == "Type:":
                combo = ttk.Combobox(main_frame, textvariable=var, width=30)
                combo['values'] = ['Spontanée', 'Réponse à offre', 'Réseau', 'Autre']
                combo.grid(row=i, column=1, sticky=tk.W+tk.E, pady=2, padx=(5,0))
            elif label == "Mode envoi:":
                combo = ttk.Combobox(main_frame, textvariable=var, width=30)
                combo['values'] = ['Email', 'Site web', 'LinkedIn', 'Téléphone', 'Courrier', 'Autre']
                combo.grid(row=i, column=1, sticky=tk.W+tk.E, pady=2, padx=(5,0))
            else:
                ttk.Entry(main_frame, textvariable=var, width=30).grid(row=i, column=1, sticky=tk.W+tk.E, pady=2, padx=(5,0))
        
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Ajouter", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Annuler", command=self.cancel).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        """Sauvegarder"""
        self.result = {
            'entreprise': self.entreprise_var.get(),
            'poste': self.poste_var.get(),
            'url': self.url_var.get(),
            'email_contact': self.email_contact_var.get(),
            'date_candidature': datetime.now().date(),
            'statut': self.statut_var.get(),
            'type_candidature': self.type_candidature_var.get(),
            'mode_envoi': self.mode_envoi_var.get(),
            'notes': self.notes_var.get()
        }
        self.dialog.destroy()
    
    def cancel(self):
        """Annuler"""
        self.dialog.destroy()

def main():
    """Point d'entrée principal"""
    try:
        app = CompleteApp()
        app.run()
    except Exception as e:
        print(f"Erreur lors du lancement: {e}")
        messagebox.showerror("Erreur", f"Erreur lors du lancement: {e}")

if __name__ == "__main__":
    main()

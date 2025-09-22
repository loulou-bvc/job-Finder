#!/usr/bin/env python3
"""
Gestionnaire de suivi des candidatures
Base de données dédiée pour le suivi des candidatures
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class CandidatureTracker:
    def __init__(self, db_path: str = "data/candidatures.db"):
        self.db_path = db_path
        self.ensure_data_dir()
        self.init_database()
    
    def ensure_data_dir(self):
        """Créer le dossier data s'il n'existe pas"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def init_database(self):
        """Initialiser la base de données des candidatures"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS candidatures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    offre_id INTEGER,
                    entreprise TEXT NOT NULL,
                    poste TEXT NOT NULL,
                    url TEXT,
                    email_contact TEXT,
                    date_candidature DATE NOT NULL,
                    statut TEXT DEFAULT 'Envoyée',
                    type_candidature TEXT DEFAULT 'Spontanée',
                    mode_envoi TEXT,
                    date_relance DATE,
                    notes TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS relances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidature_id INTEGER NOT NULL,
                    date_relance DATE NOT NULL,
                    type_relance TEXT,
                    reponse TEXT,
                    FOREIGN KEY (candidature_id) REFERENCES candidatures (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entretiens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidature_id INTEGER NOT NULL,
                    date_entretien DATETIME,
                    type_entretien TEXT,
                    resultat TEXT,
                    notes TEXT,
                    FOREIGN KEY (candidature_id) REFERENCES candidatures (id)
                )
            """)
            
            conn.commit()
    
    def add_candidature(self, candidature_data: Dict) -> int:
        """Ajouter une nouvelle candidature"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO candidatures 
                    (offre_id, entreprise, poste, url, email_contact, date_candidature, 
                     statut, type_candidature, mode_envoi, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    candidature_data.get('offre_id'),
                    candidature_data.get('entreprise', ''),
                    candidature_data.get('poste', ''),
                    candidature_data.get('url', ''),
                    candidature_data.get('email_contact', ''),
                    candidature_data.get('date_candidature', datetime.now().date()),
                    candidature_data.get('statut', 'Envoyée'),
                    candidature_data.get('type_candidature', 'Spontanée'),
                    candidature_data.get('mode_envoi', ''),
                    candidature_data.get('notes', '')
                ))
                candidature_id = cursor.lastrowid
                conn.commit()
                return candidature_id
        except Exception as e:
            print(f"Erreur ajout candidature: {e}")
            return -1
    
    def update_candidature(self, candidature_id: int, updates: Dict) -> bool:
        """Mettre à jour une candidature"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Construire la requête dynamiquement
                set_clauses = []
                values = []
                
                for key, value in updates.items():
                    if key in ['statut', 'notes', 'date_relance', 'email_contact']:
                        set_clauses.append(f"{key} = ?")
                        values.append(value)
                
                if set_clauses:
                    set_clauses.append("date_modification = CURRENT_TIMESTAMP")
                    query = f"UPDATE candidatures SET {', '.join(set_clauses)} WHERE id = ?"
                    values.append(candidature_id)
                    
                    cursor.execute(query, values)
                    conn.commit()
                    return cursor.rowcount > 0
                
                return False
        except Exception as e:
            print(f"Erreur mise à jour candidature: {e}")
            return False
    
    def get_candidature(self, candidature_id: int) -> Optional[Dict]:
        """Récupérer une candidature par ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM candidatures WHERE id = ?", (candidature_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"Erreur récupération candidature: {e}")
            return None
    
    def get_all_candidatures(self, limit: int = 100) -> List[Dict]:
        """Récupérer toutes les candidatures"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM candidatures 
                    ORDER BY date_candidature DESC 
                    LIMIT ?
                """, (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Erreur récupération candidatures: {e}")
            return []
    
    def get_candidatures_by_statut(self, statut: str) -> List[Dict]:
        """Récupérer les candidatures par statut"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM candidatures 
                    WHERE statut = ? 
                    ORDER BY date_candidature DESC
                """, (statut,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Erreur récupération par statut: {e}")
            return []
    
    def search_candidatures(self, keyword: str) -> List[Dict]:
        """Rechercher des candidatures"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM candidatures 
                    WHERE entreprise LIKE ? OR poste LIKE ? OR notes LIKE ?
                    ORDER BY date_candidature DESC
                """, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Erreur recherche candidatures: {e}")
            return []
    
    def add_relance(self, candidature_id: int, relance_data: Dict) -> int:
        """Ajouter une relance"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO relances (candidature_id, date_relance, type_relance, reponse)
                    VALUES (?, ?, ?, ?)
                """, (
                    candidature_id,
                    relance_data.get('date_relance', datetime.now().date()),
                    relance_data.get('type_relance', 'Email'),
                    relance_data.get('reponse', '')
                ))
                relance_id = cursor.lastrowid
                
                # Mettre à jour la date de relance dans la candidature
                cursor.execute("""
                    UPDATE candidatures 
                    SET date_relance = ?, date_modification = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (relance_data.get('date_relance', datetime.now().date()), candidature_id))
                
                conn.commit()
                return relance_id
        except Exception as e:
            print(f"Erreur ajout relance: {e}")
            return -1
    
    def add_entretien(self, candidature_id: int, entretien_data: Dict) -> int:
        """Ajouter un entretien"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO entretiens (candidature_id, date_entretien, type_entretien, resultat, notes)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    candidature_id,
                    entretien_data.get('date_entretien'),
                    entretien_data.get('type_entretien', 'Téléphonique'),
                    entretien_data.get('resultat', ''),
                    entretien_data.get('notes', '')
                ))
                entretien_id = cursor.lastrowid
                conn.commit()
                return entretien_id
        except Exception as e:
            print(f"Erreur ajout entretien: {e}")
            return -1
    
    def get_statistics(self) -> Dict:
        """Obtenir les statistiques des candidatures"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total candidatures
                cursor.execute("SELECT COUNT(*) FROM candidatures")
                total = cursor.fetchone()[0]
                
                # Par statut
                cursor.execute("SELECT statut, COUNT(*) FROM candidatures GROUP BY statut")
                statuts = dict(cursor.fetchall())
                
                # Par mois (derniers 6 mois)
                cursor.execute("""
                    SELECT strftime('%Y-%m', date_candidature) as mois, COUNT(*) 
                    FROM candidatures 
                    WHERE date_candidature >= date('now', '-6 months')
                    GROUP BY mois 
                    ORDER BY mois DESC
                """)
                par_mois = dict(cursor.fetchall())
                
                # Taux de réponse
                cursor.execute("SELECT COUNT(*) FROM candidatures WHERE statut IN ('Entretien', 'Acceptée', 'Refusée')")
                avec_reponse = cursor.fetchone()[0]
                taux_reponse = (avec_reponse / total * 100) if total > 0 else 0
                
                return {
                    'total': total,
                    'statuts': statuts,
                    'par_mois': par_mois,
                    'taux_reponse': round(taux_reponse, 1)
                }
        except Exception as e:
            print(f"Erreur statistiques: {e}")
            return {'total': 0, 'statuts': {}, 'par_mois': {}, 'taux_reponse': 0}
    
    def get_candidatures_a_relancer(self, jours: int = 7) -> List[Dict]:
        """Récupérer les candidatures à relancer"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM candidatures 
                    WHERE statut = 'Envoyée' 
                    AND (date_relance IS NULL OR date_relance < date('now', '-{} days'))
                    AND date_candidature < date('now', '-{} days')
                    ORDER BY date_candidature ASC
                """.format(jours, jours))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Erreur candidatures à relancer: {e}")
            return []
    
    def delete_candidature(self, candidature_id: int) -> bool:
        """Supprimer une candidature"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Supprimer les entretiens associés
                cursor.execute("DELETE FROM entretiens WHERE candidature_id = ?", (candidature_id,))
                
                # Supprimer les relances associées
                cursor.execute("DELETE FROM relances WHERE candidature_id = ?", (candidature_id,))
                
                # Supprimer la candidature
                cursor.execute("DELETE FROM candidatures WHERE id = ?", (candidature_id,))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Erreur suppression candidature: {e}")
            return False

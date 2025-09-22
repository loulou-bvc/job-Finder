#!/usr/bin/env python3
"""
Gestionnaire de candidatures
Gère les templates et la génération de candidatures
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class CandidatureManager:
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = templates_dir
        self.ensure_templates_dir()
        self.templates = self.load_templates()
    
    def ensure_templates_dir(self):
        """Créer le dossier templates s'il n'existe pas"""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
            self.create_default_templates()
    
    def create_default_templates(self):
        """Créer les templates par défaut"""
        templates = {
            "candidature_informatique.txt": """Objet : Candidature pour un stage en informatique

Madame, Monsieur,

Je me permets de vous adresser ma candidature pour un stage dans le domaine de l'informatique au sein de votre entreprise.

Actuellement étudiant en [FORMATION], je suis passionné par les technologies et souhaite mettre en pratique mes connaissances théoriques dans un environnement professionnel.

Mes compétences incluent :
- Programmation (Python, Java, JavaScript)
- Bases de données (SQL, NoSQL)
- Développement web (HTML, CSS, React)
- Outils de développement (Git, Docker)

Je suis disponible pour une période de [DUREE] mois à partir de [DATE_DEBUT].

Je serais ravi de pouvoir échanger avec vous lors d'un entretien.

Cordialement,
[VOTRE_NOM]
[VOTRE_EMAIL]
[VOTRE_TELEPHONE]""",

            "candidature_marketing.txt": """Objet : Candidature pour un stage en marketing

Madame, Monsieur,

Je vous adresse ma candidature pour un stage en marketing au sein de votre entreprise.

Étudiant en [FORMATION], je suis particulièrement intéressé par les stratégies marketing digital et la communication.

Mes compétences incluent :
- Marketing digital (SEO, SEM, réseaux sociaux)
- Analyse de données (Google Analytics, Tableau)
- Création de contenu
- Stratégie de communication

Je suis disponible pour une période de [DUREE] mois à partir de [DATE_DEBUT].

Je serais ravi de pouvoir discuter de cette opportunité avec vous.

Cordialement,
[VOTRE_NOM]
[VOTRE_EMAIL]
[VOTRE_TELEPHONE]""",

            "candidature_generale.txt": """Objet : Candidature pour un stage

Madame, Monsieur,

Je me permets de vous adresser ma candidature pour un stage au sein de votre entreprise.

Actuellement étudiant en [FORMATION], je souhaite acquérir une expérience professionnelle enrichissante dans votre secteur d'activité.

Mes compétences incluent :
- [COMPETENCE_1]
- [COMPETENCE_2]
- [COMPETENCE_3]

Je suis disponible pour une période de [DUREE] mois à partir de [DATE_DEBUT].

Je serais ravi de pouvoir échanger avec vous lors d'un entretien.

Cordialement,
[VOTRE_NOM]
[VOTRE_EMAIL]
[VOTRE_TELEPHONE]"""
        }
        
        for filename, content in templates.items():
            filepath = os.path.join(self.templates_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def load_templates(self) -> Dict[str, str]:
        """Charger tous les templates"""
        templates = {}
        if os.path.exists(self.templates_dir):
            for filename in os.listdir(self.templates_dir):
                if filename.endswith('.txt'):
                    filepath = os.path.join(self.templates_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            templates[filename] = f.read()
                    except Exception as e:
                        print(f"Erreur lecture template {filename}: {e}")
        return templates
    
    def get_templates(self) -> List[str]:
        """Obtenir la liste des templates disponibles"""
        return list(self.templates.keys())
    
    def get_template_content(self, template_name: str) -> Optional[str]:
        """Obtenir le contenu d'un template"""
        return self.templates.get(template_name)
    
    def generate_candidature(self, template_name: str, variables: Dict[str, str]) -> str:
        """Générer une candidature à partir d'un template"""
        template = self.get_template_content(template_name)
        if not template:
            return ""
        
        # Remplacer les variables
        candidature = template
        for key, value in variables.items():
            candidature = candidature.replace(f"[{key}]", value)
        
        return candidature
    
    def save_candidature(self, candidature: str, filename: str = None) -> str:
        """Sauvegarder une candidature"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"candidature_{timestamp}.txt"
        
        filepath = os.path.join(self.templates_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(candidature)
        
        return filepath
    
    def create_custom_template(self, name: str, content: str) -> bool:
        """Créer un template personnalisé"""
        try:
            filename = f"{name}.txt"
            filepath = os.path.join(self.templates_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Recharger les templates
            self.templates = self.load_templates()
            return True
        except Exception as e:
            print(f"Erreur création template: {e}")
            return False
    
    def delete_template(self, template_name: str) -> bool:
        """Supprimer un template"""
        try:
            filepath = os.path.join(self.templates_dir, template_name)
            if os.path.exists(filepath):
                os.remove(filepath)
                # Recharger les templates
                self.templates = self.load_templates()
                return True
            return False
        except Exception as e:
            print(f"Erreur suppression template: {e}")
            return False
    
    def get_variables_from_template(self, template_name: str) -> List[str]:
        """Extraire les variables d'un template"""
        template = self.get_template_content(template_name)
        if not template:
            return []
        
        import re
        variables = re.findall(r'\[([^\]]+)\]', template)
        return list(set(variables))  # Supprimer les doublons
    
    def preview_candidature(self, template_name: str, variables: Dict[str, str]) -> str:
        """Prévisualiser une candidature"""
        return self.generate_candidature(template_name, variables)

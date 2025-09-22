#!/usr/bin/env python3
"""
Gestionnaire de filtres
Filtrage et tri avancés des offres
"""

from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import re

class FilterManager:
    def __init__(self):
        self.active_filters = {}
        self.sort_options = {
            'date_desc': lambda x: x.get('date_ajout', ''),
            'date_asc': lambda x: x.get('date_ajout', ''),
            'entreprise_asc': lambda x: x.get('entreprise', '').lower(),
            'entreprise_desc': lambda x: x.get('entreprise', '').lower(),
            'titre_asc': lambda x: x.get('titre', '').lower(),
            'titre_desc': lambda x: x.get('titre', '').lower(),
            'domaine_asc': lambda x: x.get('domaine', '').lower(),
            'domaine_desc': lambda x: x.get('domaine', '').lower()
        }
    
    def apply_filters(self, offres: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Appliquer les filtres aux offres"""
        filtered_offres = offres.copy()
        
        # Filtre par mot-clé
        if filters.get('keyword'):
            keyword = filters['keyword'].lower()
            filtered_offres = [o for o in filtered_offres 
                             if self._matches_keyword(o, keyword)]
        
        # Filtre par domaine
        if filters.get('domaine') and filters['domaine'] != 'Tous':
            filtered_offres = [o for o in filtered_offres 
                             if o.get('domaine', '').lower() == filters['domaine'].lower()]
        
        # Filtre par ville
        if filters.get('ville'):
            ville = filters['ville'].lower()
            filtered_offres = [o for o in filtered_offres 
                             if ville in o.get('ville', '').lower()]
        
        # Filtre par type de contrat
        if filters.get('type_contrat'):
            type_contrat = filters['type_contrat'].lower()
            filtered_offres = [o for o in filtered_offres 
                             if type_contrat in o.get('type_contrat', '').lower()]
        
        # Filtre par rémunération
        if filters.get('remuneration_min'):
            try:
                min_rem = float(filters['remuneration_min'])
                filtered_offres = [o for o in filtered_offres 
                                 if self._extract_remuneration(o.get('remuneration', '')) >= min_rem]
            except (ValueError, TypeError):
                pass
        
        if filters.get('remuneration_max'):
            try:
                max_rem = float(filters['remuneration_max'])
                filtered_offres = [o for o in filtered_offres 
                                 if self._extract_remuneration(o.get('remuneration', '')) <= max_rem]
            except (ValueError, TypeError):
                pass
        
        # Filtre par date
        if filters.get('date_debut'):
            try:
                date_debut = datetime.strptime(filters['date_debut'], '%Y-%m-%d').date()
                filtered_offres = [o for o in filtered_offres 
                                 if self._parse_date(o.get('date_ajout', '')) >= date_debut]
            except (ValueError, TypeError):
                pass
        
        if filters.get('date_fin'):
            try:
                date_fin = datetime.strptime(filters['date_fin'], '%Y-%m-%d').date()
                filtered_offres = [o for o in filtered_offres 
                                 if self._parse_date(o.get('date_ajout', '')) <= date_fin]
            except (ValueError, TypeError):
                pass
        
        # Filtre par source
        if filters.get('source'):
            source = filters['source'].lower()
            filtered_offres = [o for o in filtered_offres 
                             if source in o.get('source', '').lower()]
        
        # Filtre par email disponible
        if filters.get('avec_email'):
            filtered_offres = [o for o in filtered_offres 
                             if o.get('email') and o.get('email').strip()]
        
        # Filtre par URL valide
        if filters.get('avec_url'):
            filtered_offres = [o for o in filtered_offres 
                             if o.get('url') and o.get('url').strip()]
        
        return filtered_offres
    
    def _matches_keyword(self, offre: Dict, keyword: str) -> bool:
        """Vérifier si une offre correspond à un mot-clé"""
        search_fields = ['titre', 'entreprise', 'description', 'mots_cles']
        for field in search_fields:
            if keyword in offre.get(field, '').lower():
                return True
        return False
    
    def _extract_remuneration(self, remuneration_str: str) -> float:
        """Extraire la rémunération numérique d'une chaîne"""
        if not remuneration_str:
            return 0.0
        
        # Rechercher des nombres dans la chaîne
        numbers = re.findall(r'\d+(?:\.\d+)?', remuneration_str.replace(',', '.'))
        if numbers:
            return float(numbers[0])
        return 0.0
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parser une date depuis une chaîne"""
        if not date_str:
            return None
        
        try:
            # Essayer différents formats
            formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y', '%m/%d/%Y']
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
        except:
            pass
        
        return None
    
    def sort_offres(self, offres: List[Dict], sort_key: str, reverse: bool = False) -> List[Dict]:
        """Trier les offres"""
        if sort_key not in self.sort_options:
            return offres
        
        try:
            if reverse:
                return sorted(offres, key=self.sort_options[sort_key], reverse=True)
            else:
                return sorted(offres, key=self.sort_options[sort_key])
        except Exception as e:
            print(f"Erreur tri: {e}")
            return offres
    
    def get_unique_values(self, offres: List[Dict], field: str) -> List[str]:
        """Obtenir les valeurs uniques d'un champ"""
        values = set()
        for offre in offres:
            value = offre.get(field, '')
            if value and value.strip():
                values.add(value.strip())
        return sorted(list(values))
    
    def get_filter_stats(self, offres: List[Dict]) -> Dict[str, Any]:
        """Obtenir les statistiques pour les filtres"""
        stats = {
            'total': len(offres),
            'domaines': {},
            'villes': {},
            'types_contrat': {},
            'sources': {},
            'avec_email': 0,
            'avec_url': 0,
            'date_range': {'min': None, 'max': None},
            'remuneration_range': {'min': None, 'max': None}
        }
        
        remunerations = []
        dates = []
        
        for offre in offres:
            # Domaines
            domaine = offre.get('domaine', 'Non spécifié')
            stats['domaines'][domaine] = stats['domaines'].get(domaine, 0) + 1
            
            # Villes
            ville = offre.get('ville', 'Non spécifiée')
            stats['villes'][ville] = stats['villes'].get(ville, 0) + 1
            
            # Types de contrat
            type_contrat = offre.get('type_contrat', 'Non spécifié')
            stats['types_contrat'][type_contrat] = stats['types_contrat'].get(type_contrat, 0) + 1
            
            # Sources
            source = offre.get('source', 'Non spécifiée')
            stats['sources'][source] = stats['sources'].get(source, 0) + 1
            
            # Email et URL
            if offre.get('email'):
                stats['avec_email'] += 1
            if offre.get('url'):
                stats['avec_url'] += 1
            
            # Rémunération
            rem = self._extract_remuneration(offre.get('remuneration', ''))
            if rem > 0:
                remunerations.append(rem)
            
            # Dates
            date_obj = self._parse_date(offre.get('date_ajout', ''))
            if date_obj:
                dates.append(date_obj)
        
        # Plages de rémunération
        if remunerations:
            stats['remuneration_range']['min'] = min(remunerations)
            stats['remuneration_range']['max'] = max(remunerations)
        
        # Plages de dates
        if dates:
            stats['date_range']['min'] = min(dates)
            stats['date_range']['max'] = max(dates)
        
        return stats
    
    def create_filter_preset(self, filters: Dict[str, Any], name: str) -> Dict[str, Any]:
        """Créer un preset de filtres"""
        return {
            'name': name,
            'filters': filters,
            'created_at': datetime.now().isoformat()
        }
    
    def apply_filter_preset(self, offres: List[Dict], preset: Dict[str, Any]) -> List[Dict]:
        """Appliquer un preset de filtres"""
        return self.apply_filters(offres, preset.get('filters', {}))
    
    def get_advanced_filters(self) -> Dict[str, Dict[str, Any]]:
        """Obtenir les filtres avancés disponibles"""
        return {
            'keyword': {
                'type': 'text',
                'label': 'Mot-clé',
                'placeholder': 'Rechercher dans titre, entreprise, description...'
            },
            'domaine': {
                'type': 'select',
                'label': 'Domaine',
                'options': ['Tous', 'Informatique', 'Marketing', 'Commerce', 'Finance', 'Autre']
            },
            'ville': {
                'type': 'text',
                'label': 'Ville',
                'placeholder': 'Nom de la ville'
            },
            'type_contrat': {
                'type': 'select',
                'label': 'Type de contrat',
                'options': ['Tous', 'Stage', 'CDI', 'CDD', 'Freelance', 'Alternance']
            },
            'remuneration_min': {
                'type': 'number',
                'label': 'Rémunération min (€)',
                'placeholder': '0'
            },
            'remuneration_max': {
                'type': 'number',
                'label': 'Rémunération max (€)',
                'placeholder': '10000'
            },
            'date_debut': {
                'type': 'date',
                'label': 'Date début'
            },
            'date_fin': {
                'type': 'date',
                'label': 'Date fin'
            },
            'source': {
                'type': 'select',
                'label': 'Source',
                'options': ['Toutes', 'HelloWork', 'Indeed', 'Autre']
            },
            'avec_email': {
                'type': 'checkbox',
                'label': 'Avec email'
            },
            'avec_url': {
                'type': 'checkbox',
                'label': 'Avec URL'
            }
        }
    
    def get_sort_options(self) -> Dict[str, str]:
        """Obtenir les options de tri"""
        return {
            'date_desc': 'Date (plus récent)',
            'date_asc': 'Date (plus ancien)',
            'entreprise_asc': 'Entreprise (A-Z)',
            'entreprise_desc': 'Entreprise (Z-A)',
            'titre_asc': 'Titre (A-Z)',
            'titre_desc': 'Titre (Z-A)',
            'domaine_asc': 'Domaine (A-Z)',
            'domaine_desc': 'Domaine (Z-A)'
        }
    
    def export_filtered_data(self, offres: List[Dict], filename: str, format: str = 'csv') -> bool:
        """Exporter les données filtrées"""
        try:
            if format.lower() == 'csv':
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    if offres:
                        fieldnames = offres[0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(offres)
                return True
            elif format.lower() == 'json':
                import json
                with open(filename, 'w', encoding='utf-8') as jsonfile:
                    json.dump(offres, jsonfile, indent=2, ensure_ascii=False, default=str)
                return True
        except Exception as e:
            print(f"Erreur export: {e}")
            return False

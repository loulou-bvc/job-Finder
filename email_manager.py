#!/usr/bin/env python3
"""
Gestionnaire d'emails
Recherche et validation d'adresses email
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Optional, Set

class EmailManager:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Patterns pour détecter les emails
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
        # Mots-clés pour identifier les pages de contact
        self.contact_keywords = [
            'contact', 'nous-contacter', 'about', 'equipe', 'team',
            'recrutement', 'jobs', 'carrieres', 'rh', 'ressources-humaines'
        ]
    
    def extract_emails_from_text(self, text: str) -> Set[str]:
        """Extraire les emails d'un texte"""
        emails = set()
        matches = self.email_pattern.findall(text)
        for email in matches:
            # Filtrer les emails génériques
            if not self._is_generic_email(email):
                emails.add(email.lower())
        return emails
    
    def _is_generic_email(self, email: str) -> bool:
        """Vérifier si un email est générique"""
        generic_patterns = [
            'noreply', 'no-reply', 'donotreply', 'admin@', 'webmaster@',
            'info@', 'contact@', 'support@', 'help@', 'test@', 'example@'
        ]
        return any(pattern in email.lower() for pattern in generic_patterns)
    
    def search_emails_on_page(self, url: str) -> Set[str]:
        """Rechercher des emails sur une page web"""
        emails = set()
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Extraire les emails du contenu HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text()
            emails.update(self.extract_emails_from_text(text_content))
            
            # Extraire les emails des attributs href
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if href.startswith('mailto:'):
                    email = href[7:]  # Enlever 'mailto:'
                    if not self._is_generic_email(email):
                        emails.add(email.lower())
            
            time.sleep(1)  # Délai entre les requêtes
            
        except Exception as e:
            print(f"Erreur recherche emails sur {url}: {e}")
        
        return emails
    
    def find_contact_pages(self, base_url: str) -> List[str]:
        """Trouver les pages de contact d'un site"""
        contact_pages = []
        try:
            response = self.session.get(base_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                text = link.get_text().lower()
                
                # Vérifier si le lien ou le texte contient des mots-clés de contact
                if any(keyword in href.lower() or keyword in text for keyword in self.contact_keywords):
                    full_url = urljoin(base_url, href)
                    if self._is_same_domain(base_url, full_url):
                        contact_pages.append(full_url)
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Erreur recherche pages contact sur {base_url}: {e}")
        
        return list(set(contact_pages))  # Supprimer les doublons
    
    def _is_same_domain(self, base_url: str, url: str) -> bool:
        """Vérifier si deux URLs sont du même domaine"""
        try:
            base_domain = urlparse(base_url).netloc
            url_domain = urlparse(url).netloc
            return base_domain == url_domain
        except:
            return False
    
    def search_emails_for_entreprise(self, entreprise_name: str, website: str = None) -> Dict[str, List[str]]:
        """Rechercher des emails pour une entreprise"""
        results = {
            'emails': [],
            'sources': [],
            'contact_pages': []
        }
        
        # Si un site web est fourni, l'utiliser
        if website:
            results['contact_pages'] = self.find_contact_pages(website)
            for page in results['contact_pages']:
                emails = self.search_emails_on_page(page)
                if emails:
                    results['emails'].extend(list(emails))
                    results['sources'].append(page)
        
        # Recherche sur le site principal
        if website:
            main_emails = self.search_emails_on_page(website)
            if main_emails:
                results['emails'].extend(list(main_emails))
                results['sources'].append(website)
        
        # Générer des emails probables
        probable_emails = self._generate_probable_emails(entreprise_name, website)
        results['emails'].extend(probable_emails)
        
        # Supprimer les doublons et trier par priorité
        results['emails'] = self._prioritize_emails(list(set(results['emails'])))
        
        return results
    
    def _generate_probable_emails(self, entreprise_name: str, website: str = None) -> List[str]:
        """Générer des emails probables"""
        emails = []
        
        if not website:
            return emails
        
        # Extraire le domaine du site web
        try:
            domain = urlparse(website).netloc
            if domain.startswith('www.'):
                domain = domain[4:]
        except:
            return emails
        
        # Nettoyer le nom de l'entreprise
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', entreprise_name.lower())
        words = clean_name.split()
        
        # Patterns d'emails probables
        patterns = [
            'contact@{}',
            'info@{}',
            'recrutement@{}',
            'rh@{}',
            'jobs@{}',
            'carrieres@{}',
            'contact.rh@{}',
            'recrutement.rh@{}'
        ]
        
        for pattern in patterns:
            emails.append(pattern.format(domain))
        
        # Ajouter des emails avec le nom de l'entreprise
        if words:
            first_word = words[0]
            patterns_with_name = [
                'contact.{}@{}',
                'info.{}@{}',
                'recrutement.{}@{}'
            ]
            
            for pattern in patterns_with_name:
                emails.append(pattern.format(first_word, domain))
        
        return emails
    
    def _prioritize_emails(self, emails: List[str]) -> List[str]:
        """Prioriser les emails par pertinence"""
        priority_keywords = [
            'recrutement', 'rh', 'jobs', 'carrieres', 'contact.rh',
            'recrutement.rh', 'contact', 'info'
        ]
        
        def email_priority(email):
            email_lower = email.lower()
            for i, keyword in enumerate(priority_keywords):
                if keyword in email_lower:
                    return i
            return len(priority_keywords)
        
        return sorted(emails, key=email_priority)
    
    def validate_email_format(self, email: str) -> bool:
        """Valider le format d'un email"""
        pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(pattern.match(email))
    
    def search_emails_for_offre(self, offre_data: Dict) -> Dict[str, List[str]]:
        """Rechercher des emails pour une offre spécifique"""
        entreprise = offre_data.get('entreprise', '')
        url = offre_data.get('url', '')
        
        # Extraire le domaine de l'URL de l'offre
        website = None
        if url:
            try:
                parsed = urlparse(url)
                website = f"{parsed.scheme}://{parsed.netloc}"
            except:
                pass
        
        return self.search_emails_for_entreprise(entreprise, website)
    
    def get_common_email_patterns(self) -> List[str]:
        """Obtenir les patterns d'emails courants"""
        return [
            'contact@[domaine]',
            'info@[domaine]',
            'recrutement@[domaine]',
            'rh@[domaine]',
            'jobs@[domaine]',
            'carrieres@[domaine]',
            'contact.rh@[domaine]',
            'recrutement.rh@[domaine]',
            'contact.[entreprise]@[domaine]',
            'info.[entreprise]@[domaine]'
        ]
    
    def export_emails_to_file(self, emails: List[str], filename: str) -> bool:
        """Exporter les emails vers un fichier"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for email in emails:
                    f.write(f"{email}\n")
            return True
        except Exception as e:
            print(f"Erreur export emails: {e}")
            return False

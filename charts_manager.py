#!/usr/bin/env python3
"""
Gestionnaire de graphiques
Création de graphiques avec matplotlib et seaborn
"""

import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import pandas as pd
from typing import Dict, List, Optional, Tuple
import os
from datetime import datetime, timedelta

# Configuration matplotlib pour Tkinter
matplotlib.use('TkAgg')

class ChartsManager:
    def __init__(self):
        self.setup_style()
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                      '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    def setup_style(self):
        """Configurer le style des graphiques"""
        try:
            plt.style.use('seaborn-v0_8')
        except:
            try:
                plt.style.use('seaborn')
            except:
                plt.style.use('default')
        
        # Configuration des polices
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['axes.labelsize'] = 10
        plt.rcParams['xtick.labelsize'] = 9
        plt.rcParams['ytick.labelsize'] = 9
        plt.rcParams['legend.fontsize'] = 9
    
    def create_domain_chart(self, domaines_data: Dict[str, int], title: str = "Offres par domaine") -> plt.Figure:
        """Créer un graphique en barres pour les domaines"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if not domaines_data:
            ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title(title)
            return fig
        
        domaines = list(domaines_data.keys())
        valeurs = list(domaines_data.values())
        
        bars = ax.bar(domaines, valeurs, color=self.colors[:len(domaines)])
        ax.set_title(title, fontweight='bold', pad=20)
        ax.set_xlabel('Domaines')
        ax.set_ylabel('Nombre d\'offres')
        
        # Rotation des labels si nécessaire
        if len(max(domaines, key=len)) > 10:
            plt.xticks(rotation=45, ha='right')
        
        # Ajouter les valeurs sur les barres
        for bar, valeur in zip(bars, valeurs):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{valeur}', ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
    
    def create_city_chart(self, villes_data: Dict[str, int], title: str = "Offres par ville") -> plt.Figure:
        """Créer un graphique en barres pour les villes"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if not villes_data:
            ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title(title)
            return fig
        
        # Limiter aux 10 premières villes
        sorted_villes = sorted(villes_data.items(), key=lambda x: x[1], reverse=True)[:10]
        villes = [item[0] for item in sorted_villes]
        valeurs = [item[1] for item in sorted_villes]
        
        bars = ax.bar(villes, valeurs, color=self.colors[:len(villes)])
        ax.set_title(title, fontweight='bold', pad=20)
        ax.set_xlabel('Villes')
        ax.set_ylabel('Nombre d\'offres')
        
        plt.xticks(rotation=45, ha='right')
        
        # Ajouter les valeurs sur les barres
        for bar, valeur in zip(bars, valeurs):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{valeur}', ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
    
    def create_timeline_chart(self, timeline_data: Dict[str, int], title: str = "Évolution des offres") -> plt.Figure:
        """Créer un graphique temporel"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if not timeline_data:
            ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title(title)
            return fig
        
        dates = list(timeline_data.keys())
        valeurs = list(timeline_data.values())
        
        # Trier par date
        sorted_data = sorted(zip(dates, valeurs), key=lambda x: x[0])
        dates, valeurs = zip(*sorted_data)
        
        ax.plot(dates, valeurs, marker='o', linewidth=2, markersize=6, color=self.colors[0])
        ax.fill_between(dates, valeurs, alpha=0.3, color=self.colors[0])
        
        ax.set_title(title, fontweight='bold', pad=20)
        ax.set_xlabel('Date')
        ax.set_ylabel('Nombre d\'offres')
        
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig
    
    def create_pie_chart(self, data: Dict[str, int], title: str = "Répartition") -> plt.Figure:
        """Créer un graphique en secteurs"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        if not data:
            ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title(title)
            return fig
        
        labels = list(data.keys())
        sizes = list(data.values())
        
        # Filtrer les valeurs nulles
        filtered_data = [(label, size) for label, size in zip(labels, sizes) if size > 0]
        if not filtered_data:
            ax.text(0.5, 0.5, 'Aucune donnée valide', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title(title)
            return fig
        
        labels, sizes = zip(*filtered_data)
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                         colors=self.colors[:len(labels)], startangle=90)
        
        ax.set_title(title, fontweight='bold', pad=20)
        
        # Améliorer l'apparence
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        return fig
    
    def create_candidatures_chart(self, candidatures_data: Dict[str, int], title: str = "Candidatures par statut") -> plt.Figure:
        """Créer un graphique pour les candidatures"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if not candidatures_data:
            ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title(title)
            return fig
        
        statuts = list(candidatures_data.keys())
        valeurs = list(candidatures_data.values())
        
        # Couleurs spécifiques pour les statuts
        status_colors = {
            'Envoyée': '#1f77b4',
            'Relancée': '#ff7f0e', 
            'Entretien': '#2ca02c',
            'Acceptée': '#d62728',
            'Refusée': '#8c564b'
        }
        
        colors = [status_colors.get(statut, self.colors[i % len(self.colors)]) 
                 for i, statut in enumerate(statuts)]
        
        bars = ax.bar(statuts, valeurs, color=colors)
        ax.set_title(title, fontweight='bold', pad=20)
        ax.set_xlabel('Statut')
        ax.set_ylabel('Nombre de candidatures')
        
        # Ajouter les valeurs sur les barres
        for bar, valeur in zip(bars, valeurs):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{valeur}', ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
    
    def create_comparison_chart(self, data1: Dict[str, int], data2: Dict[str, int], 
                              label1: str = "Série 1", label2: str = "Série 2", 
                              title: str = "Comparaison") -> plt.Figure:
        """Créer un graphique de comparaison"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Obtenir toutes les clés uniques
        all_keys = set(data1.keys()) | set(data2.keys())
        if not all_keys:
            ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title(title)
            return fig
        
        keys = sorted(list(all_keys))
        values1 = [data1.get(key, 0) for key in keys]
        values2 = [data2.get(key, 0) for key in keys]
        
        x = range(len(keys))
        width = 0.35
        
        bars1 = ax.bar([i - width/2 for i in x], values1, width, label=label1, color=self.colors[0])
        bars2 = ax.bar([i + width/2 for i in x], values2, width, label=label2, color=self.colors[1])
        
        ax.set_title(title, fontweight='bold', pad=20)
        ax.set_xlabel('Catégories')
        ax.set_ylabel('Valeurs')
        ax.set_xticks(x)
        ax.set_xticklabels(keys, rotation=45, ha='right')
        ax.legend()
        
        # Ajouter les valeurs sur les barres
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                           f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
    
    def create_heatmap(self, data: List[List], labels_x: List[str], labels_y: List[str], 
                      title: str = "Heatmap") -> plt.Figure:
        """Créer une heatmap"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        if not data or not labels_x or not labels_y:
            ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title(title)
            return fig
        
        # Créer un DataFrame pour seaborn
        df = pd.DataFrame(data, index=labels_y, columns=labels_x)
        
        sns.heatmap(df, annot=True, fmt='d', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Valeurs'})
        ax.set_title(title, fontweight='bold', pad=20)
        
        plt.tight_layout()
        return fig
    
    def save_chart(self, fig: plt.Figure, filename: str, dpi: int = 300) -> bool:
        """Sauvegarder un graphique"""
        try:
            fig.savefig(filename, dpi=dpi, bbox_inches='tight', facecolor='white')
            return True
        except Exception as e:
            print(f"Erreur sauvegarde graphique: {e}")
            return False
    
    def create_dashboard(self, offres_stats: Dict, candidatures_stats: Dict) -> plt.Figure:
        """Créer un dashboard complet"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Dashboard - Gestion des Offres et Candidatures', fontsize=16, fontweight='bold')
        
        # Graphique 1: Offres par domaine
        if offres_stats.get('domaines'):
            domaines = list(offres_stats['domaines'].keys())[:5]
            valeurs = [offres_stats['domaines'][d] for d in domaines]
            ax1.bar(domaines, valeurs, color=self.colors[:len(domaines)])
            ax1.set_title('Top 5 Domaines')
            ax1.set_ylabel('Nombre d\'offres')
            plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
        
        # Graphique 2: Candidatures par statut
        if candidatures_stats.get('statuts'):
            statuts = list(candidatures_stats['statuts'].keys())
            valeurs = list(candidatures_stats['statuts'].values())
            ax2.pie(valeurs, labels=statuts, autopct='%1.1f%%', startangle=90)
            ax2.set_title('Candidatures par Statut')
        
        # Graphique 3: Évolution temporelle
        if offres_stats.get('par_mois'):
            mois = list(offres_stats['par_mois'].keys())
            valeurs = list(offres_stats['par_mois'].values())
            ax3.plot(mois, valeurs, marker='o', linewidth=2)
            ax3.set_title('Évolution Mensuelle')
            ax3.set_ylabel('Nombre d\'offres')
            plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')
        
        # Graphique 4: Statistiques générales
        stats_text = f"""
        Total Offres: {offres_stats.get('total', 0)}
        Total Candidatures: {candidatures_stats.get('total', 0)}
        Taux de Réponse: {candidatures_stats.get('taux_reponse', 0)}%
        """
        ax4.text(0.1, 0.5, stats_text, transform=ax4.transAxes, fontsize=12, 
                verticalalignment='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        ax4.set_title('Statistiques Générales')
        ax4.axis('off')
        
        plt.tight_layout()
        return fig

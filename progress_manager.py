"""
Module de gestion de la progression pour permettre la reprise après interruption.
Sauvegarde l'état du scraping et permet de reprendre là où on s'est arrêté.
"""

import json
import os
from typing import Dict, List, Set, Optional
from datetime import datetime
import logging


class ProgressManager:
    """Gère la progression du scraping et permet la reprise après interruption."""

    def __init__(self, progress_dir: str = "progress"):
        """
        Initialise le gestionnaire de progression.

        Args:
            progress_dir: Répertoire pour stocker les fichiers de progression
        """
        self.progress_dir = progress_dir
        self.progress_file = os.path.join(progress_dir, "scraping_progress.json")
        self.logger = logging.getLogger(__name__)

        # Créer le répertoire si nécessaire
        os.makedirs(progress_dir, exist_ok=True)

        # Charger la progression existante
        self.progress_data = self._load_progress()

    def _load_progress(self) -> Dict:
        """Charge la progression depuis le fichier."""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.logger.info(f"Progression chargée: {len(data.get('completed_artists', []))} artistes complétés")
                    return data
            except Exception as e:
                self.logger.error(f"Erreur lors du chargement de la progression: {e}")

        # Initialiser une nouvelle progression
        return {
            "started_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "completed_artists": [],
            "failed_artists": {},
            "current_artist": None,
            "total_requests": 0,
            "total_annotations": 0,
            "total_songs": 0
        }

    def _save_progress(self):
        """Sauvegarde la progression dans le fichier."""
        try:
            self.progress_data["last_updated"] = datetime.now().isoformat()

            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress_data, f, indent=2, ensure_ascii=False)

            self.logger.debug("Progression sauvegardée")
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde de la progression: {e}")

    def is_artist_completed(self, artist_name: str) -> bool:
        """
        Vérifie si un artiste a déjà été traité avec succès.

        Args:
            artist_name: Nom de l'artiste

        Returns:
            True si l'artiste est déjà complété
        """
        return artist_name in self.progress_data.get("completed_artists", [])

    def is_artist_failed(self, artist_name: str) -> bool:
        """
        Vérifie si un artiste a échoué précédemment.

        Args:
            artist_name: Nom de l'artiste

        Returns:
            True si l'artiste a échoué
        """
        return artist_name in self.progress_data.get("failed_artists", {})

    def get_remaining_artists(self, all_artists: List[str]) -> List[str]:
        """
        Retourne la liste des artistes restants à traiter.

        Args:
            all_artists: Liste complète des artistes

        Returns:
            Liste des artistes non encore traités
        """
        completed = set(self.progress_data.get("completed_artists", []))
        remaining = [artist for artist in all_artists if artist not in completed]

        self.logger.info(f"{len(remaining)} artistes restants sur {len(all_artists)}")

        return remaining

    def mark_artist_started(self, artist_name: str):
        """
        Marque qu'on commence le traitement d'un artiste.

        Args:
            artist_name: Nom de l'artiste
        """
        self.progress_data["current_artist"] = artist_name
        self._save_progress()
        self.logger.info(f"Début du traitement: {artist_name}")

    def mark_artist_completed(self, artist_name: str, stats: Optional[Dict] = None):
        """
        Marque un artiste comme complété avec succès.

        Args:
            artist_name: Nom de l'artiste
            stats: Statistiques optionnelles (nb chansons, annotations, etc.)
        """
        if artist_name not in self.progress_data["completed_artists"]:
            self.progress_data["completed_artists"].append(artist_name)

        self.progress_data["current_artist"] = None

        # Mettre à jour les statistiques si fournies
        if stats:
            self.progress_data["total_songs"] += stats.get("songs", 0)
            self.progress_data["total_annotations"] += stats.get("annotations", 0)
            self.progress_data["total_requests"] += stats.get("requests", 0)

        self._save_progress()
        self.logger.info(f"Artiste complété: {artist_name}")

    def mark_artist_failed(self, artist_name: str, error: str):
        """
        Marque un artiste comme ayant échoué.

        Args:
            artist_name: Nom de l'artiste
            error: Description de l'erreur
        """
        self.progress_data["failed_artists"][artist_name] = {
            "error": error,
            "timestamp": datetime.now().isoformat()
        }

        self.progress_data["current_artist"] = None
        self._save_progress()
        self.logger.warning(f"Artiste échoué: {artist_name} - {error}")

    def get_stats(self) -> Dict:
        """
        Retourne les statistiques de progression.

        Returns:
            Dictionnaire avec les statistiques
        """
        return {
            "started_at": self.progress_data.get("started_at"),
            "last_updated": self.progress_data.get("last_updated"),
            "completed_artists": len(self.progress_data.get("completed_artists", [])),
            "failed_artists": len(self.progress_data.get("failed_artists", {})),
            "total_songs": self.progress_data.get("total_songs", 0),
            "total_annotations": self.progress_data.get("total_annotations", 0),
            "total_requests": self.progress_data.get("total_requests", 0),
            "current_artist": self.progress_data.get("current_artist")
        }

    def print_summary(self):
        """Affiche un résumé de la progression."""
        stats = self.get_stats()

        print("\n" + "="*60)
        print("RÉSUMÉ DE LA PROGRESSION")
        print("="*60)
        print(f"Début du scraping     : {stats['started_at']}")
        print(f"Dernière mise à jour  : {stats['last_updated']}")
        print(f"Artistes complétés    : {stats['completed_artists']}")
        print(f"Artistes échoués      : {stats['failed_artists']}")
        print(f"Total chansons        : {stats['total_songs']}")
        print(f"Total annotations     : {stats['total_annotations']}")
        print(f"Total requêtes API    : {stats['total_requests']}")
        if stats['current_artist']:
            print(f"Artiste en cours      : {stats['current_artist']}")
        print("="*60 + "\n")

    def reset(self):
        """Réinitialise complètement la progression."""
        self.progress_data = {
            "started_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "completed_artists": [],
            "failed_artists": {},
            "current_artist": None,
            "total_requests": 0,
            "total_annotations": 0,
            "total_songs": 0
        }
        self._save_progress()
        self.logger.info("Progression réinitialisée")

    def get_failed_artists_list(self) -> List[Dict]:
        """
        Retourne la liste des artistes ayant échoué avec leurs erreurs.

        Returns:
            Liste de dictionnaires avec nom et erreur
        """
        failed = self.progress_data.get("failed_artists", {})
        return [
            {
                "name": name,
                "error": info.get("error"),
                "timestamp": info.get("timestamp")
            }
            for name, info in failed.items()
        ]

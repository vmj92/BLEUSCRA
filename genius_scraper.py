"""
Module pour l'extraction d'annotations depuis l'API Genius.
Gère l'authentification, le rate limiting et l'extraction complète des données.
"""

import requests
import time
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import os


class RateLimiter:
    """Gère le rate limiting pour respecter la limite de 1000 requêtes/jour."""

    def __init__(self, max_requests_per_day: int = 1000, delay_between_requests: float = 1.5):
        self.max_requests_per_day = max_requests_per_day
        self.delay_between_requests = delay_between_requests
        self.request_count = 0
        self.start_date = datetime.now().date()
        self.last_request_time = 0

    def wait_if_needed(self):
        """Attend si nécessaire pour respecter le rate limit."""
        # Réinitialiser le compteur si on est un nouveau jour
        if datetime.now().date() > self.start_date:
            self.request_count = 0
            self.start_date = datetime.now().date()
            logging.info(f"Nouveau jour - Compteur de requêtes réinitialisé")

        # Vérifier si on a atteint la limite quotidienne
        if self.request_count >= self.max_requests_per_day:
            wait_time = (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) +
                        timedelta(days=1) - datetime.now()).total_seconds()
            logging.warning(f"Limite quotidienne atteinte ({self.max_requests_per_day} requêtes). "
                          f"Attente de {wait_time/3600:.2f} heures...")
            time.sleep(wait_time)
            self.request_count = 0
            self.start_date = datetime.now().date()

        # Attendre entre les requêtes
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay_between_requests:
            time.sleep(self.delay_between_requests - elapsed)

        self.last_request_time = time.time()
        self.request_count += 1

    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du rate limiter."""
        return {
            "request_count": self.request_count,
            "max_requests": self.max_requests_per_day,
            "remaining": self.max_requests_per_day - self.request_count,
            "date": str(self.start_date)
        }


class GeniusScraper:
    """Client pour interagir avec l'API Genius et extraire les annotations."""

    BASE_URL = "https://api.genius.com"

    def __init__(self, access_token: str, rate_limiter: Optional[RateLimiter] = None):
        """
        Initialise le scraper Genius.

        Args:
            access_token: Token d'accès à l'API Genius
            rate_limiter: Instance de RateLimiter (optionnel)
        """
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "BLEUSCRA Francophone Rap Annotations Scraper"
        }
        self.rate_limiter = rate_limiter or RateLimiter()
        self.logger = logging.getLogger(__name__)

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Effectue une requête à l'API Genius avec gestion du rate limiting.

        Args:
            endpoint: Endpoint de l'API (ex: '/search')
            params: Paramètres de la requête

        Returns:
            Réponse JSON ou None en cas d'erreur
        """
        self.rate_limiter.wait_if_needed()

        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get("meta", {}).get("status") == 200:
                return data.get("response")
            else:
                self.logger.error(f"Erreur API: {data.get('meta', {})}")
                return None

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erreur de requête pour {endpoint}: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Erreur de décodage JSON: {e}")
            return None

    def search_artist(self, artist_name: str) -> Optional[Dict]:
        """
        Recherche un artiste par son nom.

        Args:
            artist_name: Nom de l'artiste

        Returns:
            Informations sur l'artiste ou None
        """
        self.logger.info(f"Recherche de l'artiste: {artist_name}")

        response = self._make_request("/search", params={"q": artist_name})

        if not response or "hits" not in response:
            return None

        # Chercher l'artiste dans les résultats
        for hit in response["hits"]:
            if hit.get("type") == "song":
                primary_artist = hit.get("result", {}).get("primary_artist", {})
                # Vérification du nom (case-insensitive)
                if primary_artist.get("name", "").lower() == artist_name.lower():
                    self.logger.info(f"Artiste trouvé: {primary_artist.get('name')} (ID: {primary_artist.get('id')})")
                    return primary_artist

        self.logger.warning(f"Artiste non trouvé: {artist_name}")
        return None

    def get_artist_songs(self, artist_id: int, max_songs: int = 50) -> List[Dict]:
        """
        Récupère les chansons d'un artiste.

        Args:
            artist_id: ID de l'artiste sur Genius
            max_songs: Nombre maximum de chansons à récupérer

        Returns:
            Liste des chansons
        """
        self.logger.info(f"Récupération des chansons de l'artiste ID {artist_id}")

        songs = []
        page = 1
        per_page = 50

        while len(songs) < max_songs:
            response = self._make_request(
                f"/artists/{artist_id}/songs",
                params={"page": page, "per_page": per_page, "sort": "popularity"}
            )

            if not response or "songs" not in response:
                break

            page_songs = response["songs"]

            if not page_songs:
                break

            # Filtrer pour ne garder que les chansons dont c'est l'artiste principal
            for song in page_songs:
                if song.get("primary_artist", {}).get("id") == artist_id:
                    songs.append(song)
                    if len(songs) >= max_songs:
                        break

            page += 1

            # Si on a reçu moins de chansons que demandé, c'est la dernière page
            if len(page_songs) < per_page:
                break

        self.logger.info(f"{len(songs)} chansons récupérées pour l'artiste ID {artist_id}")
        return songs[:max_songs]

    def get_song_details(self, song_id: int) -> Optional[Dict]:
        """
        Récupère les détails complets d'une chanson.

        Args:
            song_id: ID de la chanson

        Returns:
            Détails de la chanson
        """
        response = self._make_request(f"/songs/{song_id}")

        if response and "song" in response:
            return response["song"]

        return None

    def get_song_referents(self, song_id: int) -> List[Dict]:
        """
        Récupère toutes les annotations (referents) d'une chanson.

        Args:
            song_id: ID de la chanson

        Returns:
            Liste des annotations avec tous les détails
        """
        self.logger.info(f"Récupération des annotations pour la chanson ID {song_id}")

        referents = []
        page = 1
        per_page = 50

        while True:
            response = self._make_request(
                "/referents",
                params={
                    "song_id": song_id,
                    "per_page": per_page,
                    "page": page,
                    "text_format": "html,plain"
                }
            )

            if not response or "referents" not in response:
                break

            page_referents = response["referents"]

            if not page_referents:
                break

            for ref in page_referents:
                # Extraire les informations importantes de chaque annotation
                annotation_data = {
                    "id": ref.get("id"),
                    "fragment": ref.get("fragment"),  # Texte annoté
                    "annotations": []
                }

                # Une référence peut avoir plusieurs annotations
                for annotation in ref.get("annotations", []):
                    annotation_info = {
                        "id": annotation.get("id"),
                        "body": {
                            "html": annotation.get("body", {}).get("html", ""),
                            "plain": annotation.get("body", {}).get("plain", "")
                        },
                        "votes_total": annotation.get("votes_total", 0),
                        "authors": [],
                        "verified": annotation.get("verified", False),
                        "community": annotation.get("community", True),
                        "created_at": annotation.get("created_at"),
                        "url": annotation.get("url")
                    }

                    # Récupérer les informations sur les auteurs
                    for author in annotation.get("authors", []):
                        user = author.get("user", {})
                        annotation_info["authors"].append({
                            "id": user.get("id"),
                            "name": user.get("name"),
                            "login": user.get("login"),
                            "iq": user.get("iq", 0),
                            "role": user.get("role_for_display")
                        })

                    annotation_data["annotations"].append(annotation_info)

                referents.append(annotation_data)

            page += 1

            # Si on a reçu moins de referents que demandé, c'est la dernière page
            if len(page_referents) < per_page:
                break

        self.logger.info(f"{len(referents)} annotations récupérées pour la chanson ID {song_id}")
        return referents

    def get_artist_complete_data(self, artist_name: str, max_songs: int = 50) -> Optional[Dict]:
        """
        Récupère toutes les données d'un artiste: chansons et annotations.

        Args:
            artist_name: Nom de l'artiste
            max_songs: Nombre maximum de chansons à traiter

        Returns:
            Dictionnaire complet avec toutes les données
        """
        # Rechercher l'artiste
        artist = self.search_artist(artist_name)

        if not artist:
            self.logger.error(f"Impossible de trouver l'artiste: {artist_name}")
            return None

        artist_id = artist.get("id")

        # Récupérer les chansons
        songs = self.get_artist_songs(artist_id, max_songs)

        if not songs:
            self.logger.warning(f"Aucune chanson trouvée pour {artist_name}")
            return {
                "artist": artist,
                "songs": [],
                "total_songs": 0,
                "total_annotations": 0,
                "extracted_at": datetime.now().isoformat()
            }

        # Pour chaque chanson, récupérer les détails et annotations
        songs_with_annotations = []
        total_annotations = 0

        for i, song in enumerate(songs, 1):
            song_id = song.get("id")
            self.logger.info(f"Traitement de la chanson {i}/{len(songs)}: {song.get('title')}")

            # Récupérer les détails
            song_details = self.get_song_details(song_id)

            # Récupérer les annotations
            annotations = self.get_song_referents(song_id)
            total_annotations += len(annotations)

            song_data = {
                "id": song_id,
                "title": song.get("title"),
                "url": song.get("url"),
                "release_date": song.get("release_date_for_display"),
                "stats": {
                    "pageviews": song_details.get("stats", {}).get("pageviews") if song_details else None,
                    "hot": song_details.get("stats", {}).get("hot") if song_details else None
                },
                "annotations": annotations,
                "annotation_count": len(annotations)
            }

            songs_with_annotations.append(song_data)

        result = {
            "artist": {
                "id": artist_id,
                "name": artist.get("name"),
                "url": artist.get("url"),
                "image_url": artist.get("image_url"),
                "is_verified": artist.get("is_verified", False),
                "iq": artist.get("iq")
            },
            "songs": songs_with_annotations,
            "total_songs": len(songs_with_annotations),
            "total_annotations": total_annotations,
            "extracted_at": datetime.now().isoformat(),
            "rate_limiter_stats": self.rate_limiter.get_stats()
        }

        return result

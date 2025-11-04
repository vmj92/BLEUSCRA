#!/usr/bin/env python3
"""
BLEUSCRA - Francophone Rap Annotations Scraper
Extraction automatique des annotations de rap francophone depuis Genius.com

Ce script extrait les annotations de 100 artistes de rap francophone spécifiques,
avec gestion du rate limiting, reprise après interruption et sauvegarde en JSON.
"""

import json
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Optional
import argparse

from genius_scraper import GeniusScraper, RateLimiter
from progress_manager import ProgressManager


def setup_logging(log_dir: str = "logs") -> logging.Logger:
    """
    Configure le système de logging.

    Args:
        log_dir: Répertoire pour les fichiers de log

    Returns:
        Logger configuré
    """
    os.makedirs(log_dir, exist_ok=True)

    # Nom de fichier avec timestamp
    log_file = os.path.join(
        log_dir,
        f"scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialisé - Fichier: {log_file}")

    return logger


def load_config(config_file: str = "config.json") -> Dict:
    """
    Charge la configuration depuis le fichier JSON.

    Args:
        config_file: Chemin vers le fichier de configuration

    Returns:
        Dictionnaire de configuration
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config
    except Exception as e:
        print(f"ERREUR: Impossible de charger la configuration: {e}")
        sys.exit(1)


def save_artist_data(artist_data: Dict, output_dir: str):
    """
    Sauvegarde les données d'un artiste dans un fichier JSON.

    Args:
        artist_data: Données complètes de l'artiste
        output_dir: Répertoire de sortie
    """
    os.makedirs(output_dir, exist_ok=True)

    # Nom de fichier sécurisé (sans caractères spéciaux)
    artist_name = artist_data["artist"]["name"]
    safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in artist_name)
    safe_name = safe_name.replace(' ', '_')

    filename = os.path.join(output_dir, f"{safe_name}.json")

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(artist_data, f, indent=2, ensure_ascii=False)

        logging.info(f"Données sauvegardées: {filename}")
        return True
    except Exception as e:
        logging.error(f"Erreur lors de la sauvegarde de {artist_name}: {e}")
        return False


def process_artists(
    artists: List[str],
    scraper: GeniusScraper,
    progress_manager: ProgressManager,
    output_dir: str,
    max_songs: int = 50,
    resume: bool = True
):
    """
    Traite la liste des artistes et extrait leurs annotations.

    Args:
        artists: Liste des noms d'artistes
        scraper: Instance de GeniusScraper
        progress_manager: Gestionnaire de progression
        output_dir: Répertoire de sortie pour les JSON
        max_songs: Nombre maximum de chansons par artiste
        resume: Si True, reprend là où on s'est arrêté
    """
    logger = logging.getLogger(__name__)

    # Obtenir la liste des artistes restants
    if resume:
        artists_to_process = progress_manager.get_remaining_artists(artists)
        logger.info(f"Mode reprise activé - {len(artists_to_process)} artistes restants")
    else:
        artists_to_process = artists
        logger.info(f"Traitement de {len(artists_to_process)} artistes")

    # Traiter chaque artiste
    for i, artist_name in enumerate(artists_to_process, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"ARTISTE {i}/{len(artists_to_process)}: {artist_name}")
        logger.info(f"{'='*60}")

        try:
            # Marquer le début du traitement
            progress_manager.mark_artist_started(artist_name)

            # Extraire les données
            artist_data = scraper.get_artist_complete_data(artist_name, max_songs)

            if artist_data is None:
                progress_manager.mark_artist_failed(artist_name, "Artiste non trouvé")
                logger.warning(f"Artiste non trouvé sur Genius: {artist_name}")
                continue

            # Sauvegarder les données
            if save_artist_data(artist_data, output_dir):
                # Marquer comme complété
                stats = {
                    "songs": artist_data.get("total_songs", 0),
                    "annotations": artist_data.get("total_annotations", 0),
                    "requests": scraper.rate_limiter.request_count
                }
                progress_manager.mark_artist_completed(artist_name, stats)

                logger.info(f"✓ {artist_name} - {stats['songs']} chansons, "
                          f"{stats['annotations']} annotations")
            else:
                progress_manager.mark_artist_failed(artist_name, "Erreur de sauvegarde")

        except KeyboardInterrupt:
            logger.warning("\nInterruption utilisateur détectée")
            progress_manager.print_summary()
            logger.info("La progression a été sauvegardée. Vous pouvez reprendre avec --resume")
            sys.exit(0)

        except Exception as e:
            logger.error(f"Erreur lors du traitement de {artist_name}: {e}", exc_info=True)
            progress_manager.mark_artist_failed(artist_name, str(e))

    # Afficher le résumé final
    progress_manager.print_summary()


def main():
    """Point d'entrée principal du script."""
    # Parser les arguments
    parser = argparse.ArgumentParser(
        description="BLEUSCRA - Extraction d'annotations de rap francophone depuis Genius"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        default=True,
        help="Reprendre là où on s'est arrêté (défaut: True)"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Réinitialiser la progression et recommencer depuis le début"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Afficher uniquement les statistiques de progression"
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="Fichier de configuration (défaut: config.json)"
    )

    args = parser.parse_args()

    # Charger les variables d'environnement
    load_dotenv()

    # Charger la configuration
    config = load_config(args.config)

    # Initialiser le logging
    logger = setup_logging(config["output"]["logs_dir"])

    # Initialiser le gestionnaire de progression
    progress_manager = ProgressManager(config["output"]["progress_dir"])

    # Si --stats, afficher les stats et quitter
    if args.stats:
        progress_manager.print_summary()
        failed = progress_manager.get_failed_artists_list()
        if failed:
            print("\nARTISTES ÉCHOUÉS:")
            for item in failed:
                print(f"  - {item['name']}: {item['error']}")
        return

    # Si --reset, réinitialiser la progression
    if args.reset:
        response = input("Êtes-vous sûr de vouloir réinitialiser la progression ? (oui/non): ")
        if response.lower() in ['oui', 'yes', 'y', 'o']:
            progress_manager.reset()
            logger.info("Progression réinitialisée")
        else:
            logger.info("Réinitialisation annulée")
            return

    # Vérifier le token API
    access_token = os.getenv("GENIUS_ACCESS_TOKEN")
    if not access_token or access_token == "your_access_token_here":
        logger.error("\n" + "="*60)
        logger.error("ERREUR: Token Genius API non configuré!")
        logger.error("="*60)
        logger.error("1. Créez un compte sur https://genius.com")
        logger.error("2. Créez une application API sur https://genius.com/api-clients")
        logger.error("3. Copiez le 'Client Access Token'")
        logger.error("4. Créez un fichier .env et ajoutez:")
        logger.error("   GENIUS_ACCESS_TOKEN=votre_token_ici")
        logger.error("="*60 + "\n")
        sys.exit(1)

    # Initialiser le rate limiter
    rate_limiter = RateLimiter(
        max_requests_per_day=config["rate_limit"]["requests_per_day"],
        delay_between_requests=config["rate_limit"]["delay_between_requests"]
    )

    # Initialiser le scraper
    scraper = GeniusScraper(access_token, rate_limiter)

    # Afficher les informations de démarrage
    logger.info("\n" + "="*60)
    logger.info("BLEUSCRA - Francophone Rap Annotations Scraper")
    logger.info("="*60)
    logger.info(f"Artistes à traiter    : {len(config['artists'])}")
    logger.info(f"Chansons par artiste  : {config['max_songs_per_artist']}")
    logger.info(f"Limite API quotidienne: {config['rate_limit']['requests_per_day']} requêtes")
    logger.info(f"Délai entre requêtes  : {config['rate_limit']['delay_between_requests']}s")
    logger.info(f"Mode reprise          : {'Activé' if args.resume else 'Désactivé'}")
    logger.info("="*60 + "\n")

    # Démarrer le traitement
    try:
        process_artists(
            artists=config["artists"],
            scraper=scraper,
            progress_manager=progress_manager,
            output_dir=config["output"]["data_dir"],
            max_songs=config["max_songs_per_artist"],
            resume=args.resume and not args.reset
        )

        logger.info("\n" + "="*60)
        logger.info("EXTRACTION TERMINÉE AVEC SUCCÈS!")
        logger.info("="*60)

        # Afficher les artistes échoués s'il y en a
        failed = progress_manager.get_failed_artists_list()
        if failed:
            logger.warning(f"\n{len(failed)} artiste(s) échoué(s):")
            for item in failed:
                logger.warning(f"  - {item['name']}: {item['error']}")

    except Exception as e:
        logger.error(f"Erreur fatale: {e}", exc_info=True)
        progress_manager.print_summary()
        sys.exit(1)


if __name__ == "__main__":
    main()

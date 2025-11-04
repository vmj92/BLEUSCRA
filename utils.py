"""
Utilitaires pour analyser les données extraites et générer des statistiques.
"""

import json
import os
from typing import List, Dict, Any
from collections import Counter
import glob


def load_artist_data(data_dir: str = "data") -> List[Dict]:
    """
    Charge toutes les données des artistes depuis les fichiers JSON.

    Args:
        data_dir: Répertoire contenant les fichiers JSON

    Returns:
        Liste de dictionnaires avec les données des artistes
    """
    artist_data = []

    json_files = glob.glob(os.path.join(data_dir, "*.json"))

    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                artist_data.append(data)
        except Exception as e:
            print(f"Erreur lors du chargement de {file_path}: {e}")

    return artist_data


def generate_statistics(data_dir: str = "data") -> Dict[str, Any]:
    """
    Génère des statistiques globales sur les données extraites.

    Args:
        data_dir: Répertoire contenant les fichiers JSON

    Returns:
        Dictionnaire avec les statistiques
    """
    all_data = load_artist_data(data_dir)

    if not all_data:
        return {"error": "Aucune donnée trouvée"}

    total_artists = len(all_data)
    total_songs = sum(d.get("total_songs", 0) for d in all_data)
    total_annotations = sum(d.get("total_annotations", 0) for d in all_data)

    # Statistiques par artiste
    artists_stats = []
    for data in all_data:
        artists_stats.append({
            "name": data["artist"]["name"],
            "songs": data.get("total_songs", 0),
            "annotations": data.get("total_annotations", 0),
            "avg_annotations_per_song": (
                data.get("total_annotations", 0) / data.get("total_songs", 1)
                if data.get("total_songs", 0) > 0 else 0
            )
        })

    # Trier par nombre d'annotations
    artists_stats.sort(key=lambda x: x["annotations"], reverse=True)

    # Top 10 artistes avec le plus d'annotations
    top_annotated = artists_stats[:10]

    # Top 10 artistes avec le moins d'annotations
    least_annotated = artists_stats[-10:]

    # Statistiques sur les auteurs d'annotations
    all_authors = []
    for data in all_data:
        for song in data.get("songs", []):
            for referent in song.get("annotations", []):
                for annotation in referent.get("annotations", []):
                    for author in annotation.get("authors", []):
                        all_authors.append(author.get("name"))

    author_counts = Counter(all_authors)
    top_contributors = author_counts.most_common(20)

    stats = {
        "summary": {
            "total_artists": total_artists,
            "total_songs": total_songs,
            "total_annotations": total_annotations,
            "avg_songs_per_artist": total_songs / total_artists if total_artists > 0 else 0,
            "avg_annotations_per_artist": total_annotations / total_artists if total_artists > 0 else 0,
            "avg_annotations_per_song": total_annotations / total_songs if total_songs > 0 else 0
        },
        "top_annotated_artists": top_annotated,
        "least_annotated_artists": least_annotated,
        "top_contributors": [
            {"name": name, "contributions": count}
            for name, count in top_contributors
        ]
    }

    return stats


def print_statistics(data_dir: str = "data"):
    """Affiche les statistiques de manière formatée."""
    stats = generate_statistics(data_dir)

    if "error" in stats:
        print(f"ERREUR: {stats['error']}")
        return

    print("\n" + "="*70)
    print("STATISTIQUES GLOBALES - BLEUSCRA")
    print("="*70)

    summary = stats["summary"]
    print(f"\nArtistes extraits         : {summary['total_artists']}")
    print(f"Total chansons            : {summary['total_songs']}")
    print(f"Total annotations         : {summary['total_annotations']}")
    print(f"Moyenne chansons/artiste  : {summary['avg_songs_per_artist']:.1f}")
    print(f"Moyenne annotations/artiste: {summary['avg_annotations_per_artist']:.1f}")
    print(f"Moyenne annotations/chanson: {summary['avg_annotations_per_song']:.1f}")

    print("\n" + "-"*70)
    print("TOP 10 ARTISTES LES PLUS ANNOTÉS")
    print("-"*70)
    for i, artist in enumerate(stats["top_annotated_artists"], 1):
        print(f"{i:2d}. {artist['name']:30s} - {artist['annotations']:4d} annotations "
              f"({artist['songs']} chansons, {artist['avg_annotations_per_song']:.1f} par chanson)")

    print("\n" + "-"*70)
    print("TOP 10 ARTISTES LES MOINS ANNOTÉS")
    print("-"*70)
    for i, artist in enumerate(stats["least_annotated_artists"], 1):
        print(f"{i:2d}. {artist['name']:30s} - {artist['annotations']:4d} annotations "
              f"({artist['songs']} chansons, {artist['avg_annotations_per_song']:.1f} par chanson)")

    print("\n" + "-"*70)
    print("TOP 20 CONTRIBUTEURS D'ANNOTATIONS")
    print("-"*70)
    for i, contributor in enumerate(stats["top_contributors"], 1):
        print(f"{i:2d}. {contributor['name']:30s} - {contributor['contributions']:4d} annotations")

    print("\n" + "="*70 + "\n")


def export_to_single_file(data_dir: str = "data", output_file: str = "complete_dataset.json"):
    """
    Exporte toutes les données dans un seul fichier JSON.

    Args:
        data_dir: Répertoire source
        output_file: Fichier de sortie
    """
    all_data = load_artist_data(data_dir)

    dataset = {
        "metadata": {
            "total_artists": len(all_data),
            "extracted_at": max(d.get("extracted_at", "") for d in all_data) if all_data else None,
            "description": "Base de données complète des annotations de rap francophone depuis Genius.com"
        },
        "artists": all_data
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"Dataset complet exporté vers: {output_file}")
    print(f"Taille: {os.path.getsize(output_file) / (1024*1024):.2f} MB")


def search_annotations(query: str, data_dir: str = "data") -> List[Dict]:
    """
    Recherche des annotations contenant un mot-clé.

    Args:
        query: Mot-clé à rechercher
        data_dir: Répertoire contenant les données

    Returns:
        Liste des annotations correspondantes
    """
    all_data = load_artist_data(data_dir)
    results = []

    query_lower = query.lower()

    for artist_data in all_data:
        artist_name = artist_data["artist"]["name"]

        for song in artist_data.get("songs", []):
            song_title = song["title"]

            for referent in song.get("annotations", []):
                for annotation in referent.get("annotations", []):
                    annotation_text = annotation["body"]["plain"]

                    if query_lower in annotation_text.lower():
                        results.append({
                            "artist": artist_name,
                            "song": song_title,
                            "fragment": referent.get("fragment", ""),
                            "annotation": annotation_text,
                            "votes": annotation.get("votes_total", 0),
                            "url": annotation.get("url", "")
                        })

    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        print_statistics()
    elif len(sys.argv) > 1 and sys.argv[1] == "export":
        export_to_single_file()
    elif len(sys.argv) > 2 and sys.argv[1] == "search":
        query = sys.argv[2]
        results = search_annotations(query)
        print(f"\n{len(results)} résultat(s) trouvé(s) pour '{query}':\n")
        for i, result in enumerate(results[:10], 1):
            print(f"{i}. {result['artist']} - {result['song']}")
            print(f"   Fragment: {result['fragment'][:100]}...")
            print(f"   Annotation: {result['annotation'][:200]}...")
            print(f"   Votes: {result['votes']} | URL: {result['url']}\n")
    else:
        print("Usage:")
        print("  python utils.py stats                  - Afficher les statistiques")
        print("  python utils.py export                 - Exporter en un seul fichier")
        print("  python utils.py search <mot-clé>       - Rechercher dans les annotations")

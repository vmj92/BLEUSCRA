# BLEUSCRA - Francophone Rap Annotations Scraper

Système d'extraction automatique des annotations de rap francophone depuis Genius.com via l'API officielle.

## 🎯 Objectif

Extraire automatiquement toutes les annotations (commentaires explicatifs) de ~50 chansons pour 100 artistes de rap francophone spécifiques, créant ainsi une base de données complète pour analyse et recherche.

## ✨ Fonctionnalités

- ✅ **Liste fermée de 100 artistes** : Filtrage strict pour n'accepter que les artistes de rap francophone définis
- ✅ **Extraction complète** : ~50 chansons par artiste avec toutes leurs annotations
- ✅ **Annotations détaillées** : Auteur, votes, texte complet (HTML + plain text), timestamps
- ✅ **Format JSON structuré** : 1 fichier par artiste pour une analyse facile
- ✅ **Gestion du rate limiting** : Respect automatique de la limite de 1000 requêtes/jour
- ✅ **Reprise après interruption** : Système de progression sauvegardé automatiquement
- ✅ **Logging complet** : Suivi détaillé de toutes les opérations

## 📋 Liste des 100 artistes

Manau, Lionel D, Ménélik, Benny B, Alliance Ethnik, Ministère A.M.E.R, 3ème Œil, Hocus Pocus, MC Jean Gab'1, Rockin' Squat, Lord Kossity, Mac Tyer, Salif, Koba LaD, Chilla, Lefa, Josman, Dosseh, Roméo Elvis, Zola, Ali, Pit Baccardi, Djadja & Dinaz, Manu Key, Népal, La Rumeur, Caballero & JeanJass, X-Men, Kalash, Georgio, Hatik, Oboy, Shay, Moha La Squale, Niro, Mister You, Heuss L'enfoiré, Casey, Fabe, Tunisiano, Gazo, Nèg'Marrons, Kalash Criminel, Gradur, Alkpote, Guizmo, Hugo TSR, Dinos, Busta Flex, Maes, Sages Poètes de la Rue, Abd Al Malik, Rocca, Hamza, Soolking, MHD, Laylow, Alonzo, Saian Supa Crew, Lacrim, Stomy Bugsy, Black M, Passi, PLK, Freeze Corleone, Rim'K, Alpha Wann, Fonky Family, Médine, Disiz, Doc Gynéco, Sefyu, La Fouine, Kaaris, Keny Arkana, Bigflo & Oli, Sofiane, Niska, Sinik, Lino, Soprano, Lomepal, SCH, Vald, Youssoupha, Maître Gims, Ninho, Diam's, Rohff, Kery James, Nekfeu, Jul, PNL, Damso, Oxmo Puccino, Orelsan, MC Solaar, Suprême NTM, IAM, Booba.

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- Compte Genius et token API

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone <repository-url>
cd BLEUSCRA
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Obtenir un token API Genius**
   - Créez un compte sur [Genius.com](https://genius.com)
   - Allez sur [API Clients](https://genius.com/api-clients)
   - Créez une nouvelle application API
   - Copiez le **Client Access Token**

4. **Configurer le token**
```bash
cp .env.example .env
# Éditez .env et remplacez 'your_access_token_here' par votre token
```

Contenu du fichier `.env`:
```
GENIUS_ACCESS_TOKEN=votre_token_ici
```

## 📖 Usage

### Lancer l'extraction

```bash
python main.py
```

Par défaut, le script :
- Reprend automatiquement là où il s'est arrêté
- Respecte la limite de 1000 requêtes/jour
- Sauvegarde la progression en temps réel

### Options de ligne de commande

```bash
# Afficher les statistiques de progression
python main.py --stats

# Réinitialiser la progression et recommencer depuis le début
python main.py --reset

# Utiliser un fichier de configuration personnalisé
python main.py --config mon_config.json
```

### Interruption et reprise

Le script peut être interrompu à tout moment (Ctrl+C) et reprendra automatiquement là où il s'est arrêté au prochain lancement.

## 📁 Structure du projet

```
BLEUSCRA/
├── main.py                    # Script principal
├── genius_scraper.py          # Module d'interaction avec l'API Genius
├── progress_manager.py        # Gestion de la progression
├── config.json                # Configuration (artistes, paramètres)
├── requirements.txt           # Dépendances Python
├── .env                       # Token API (à créer)
├── .env.example              # Template pour .env
├── data/                     # Fichiers JSON de sortie (1 par artiste)
├── progress/                 # Fichiers de progression
└── logs/                     # Logs d'exécution
```

## 📊 Format de sortie

Chaque artiste génère un fichier JSON dans `data/` avec la structure suivante :

```json
{
  "artist": {
    "id": 123,
    "name": "Nom de l'artiste",
    "url": "https://genius.com/artists/...",
    "image_url": "...",
    "is_verified": true,
    "iq": 1234
  },
  "songs": [
    {
      "id": 456,
      "title": "Titre de la chanson",
      "url": "https://genius.com/...",
      "release_date": "2020-01-01",
      "stats": {
        "pageviews": 50000,
        "hot": false
      },
      "annotations": [
        {
          "id": 789,
          "fragment": "Texte annoté",
          "annotations": [
            {
              "id": 101112,
              "body": {
                "html": "<p>Explication en HTML</p>",
                "plain": "Explication en texte brut"
              },
              "votes_total": 42,
              "authors": [
                {
                  "id": 131415,
                  "name": "Nom de l'auteur",
                  "login": "login",
                  "iq": 5000,
                  "role": "Contributor"
                }
              ],
              "verified": false,
              "community": true,
              "created_at": "2020-01-15T10:30:00Z",
              "url": "https://genius.com/..."
            }
          ]
        }
      ],
      "annotation_count": 15
    }
  ],
  "total_songs": 50,
  "total_annotations": 342,
  "extracted_at": "2025-11-04T12:00:00",
  "rate_limiter_stats": {
    "request_count": 156,
    "max_requests": 1000,
    "remaining": 844,
    "date": "2025-11-04"
  }
}
```

## ⚙️ Configuration

Le fichier `config.json` permet de personnaliser :

```json
{
  "artists": [ /* liste des 100 artistes */ ],
  "max_songs_per_artist": 50,
  "rate_limit": {
    "requests_per_day": 1000,
    "delay_between_requests": 1.5
  },
  "output": {
    "data_dir": "data",
    "progress_dir": "progress",
    "logs_dir": "logs"
  }
}
```

## 🔧 Gestion du rate limiting

L'API Genius limite à **1000 requêtes par jour**. Le système gère automatiquement :

- Comptage des requêtes effectuées
- Délai configurable entre chaque requête (1.5s par défaut)
- Pause automatique si la limite quotidienne est atteinte
- Reprise automatique le jour suivant

**Estimation** : Environ 3-5 requêtes par chanson (recherche artiste + liste chansons + détails + annotations). Pour 100 artistes × 50 chansons, cela représente ~15,000-25,000 requêtes, soit **15-25 jours** avec la limite de 1000/jour.

## 📝 Logs

Les logs sont sauvegardés dans `logs/` avec un fichier par session :
- Horodatage de chaque opération
- Erreurs détaillées avec stack traces
- Statistiques de progression
- Informations sur le rate limiting

## 🛠️ Développement

### Architecture

- **GeniusScraper** : Gère toutes les interactions avec l'API Genius
- **RateLimiter** : Contrôle le taux de requêtes
- **ProgressManager** : Sauvegarde et restaure la progression
- **main.py** : Orchestre le workflow complet

### Ajouter des artistes

Éditez `config.json` et ajoutez les noms dans la liste `artists`.

### Modifier le nombre de chansons

Changez `max_songs_per_artist` dans `config.json`.

## 🐛 Dépannage

### "Token Genius API non configuré"
- Vérifiez que le fichier `.env` existe et contient votre token
- Vérifiez que le token est valide sur https://genius.com/api-clients

### "Artiste non trouvé"
- Vérifiez l'orthographe exacte du nom dans `config.json`
- Certains artistes peuvent ne pas être sur Genius

### "Limite quotidienne atteinte"
- Le script attend automatiquement jusqu'au jour suivant
- Réduisez `requests_per_day` dans `config.json` si nécessaire

## 📄 Licence

Ce projet est destiné à la recherche et l'analyse académique. Respectez les conditions d'utilisation de l'API Genius.

## 🤝 Contribution

Les contributions sont les bienvenues ! Ouvrez une issue ou soumettez une pull request.

## 📧 Contact

Pour toute question ou problème, ouvrez une issue sur GitHub.

---

**Note** : Ce projet utilise l'API officielle Genius. Assurez-vous de respecter leurs [conditions d'utilisation](https://genius.com/static/terms).

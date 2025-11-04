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

3. **Configurer le token API Genius**

**Option A - Configuration automatique (recommandée):**
```bash
python test_api.py setup
```
Le script vous guidera pas à pas pour obtenir et configurer votre token.

**Option B - Configuration manuelle:**
```bash
# Copier le template
cp .env.example .env

# Éditer le fichier
nano .env  # ou vim .env
```

Puis obtenez votre token:
- Allez sur [genius.com/api-clients](https://genius.com/api-clients)
- Connectez-vous ou créez un compte
- Cliquez sur "New API Client"
- Remplissez le formulaire (App Name: BLEUSCRA, App Website: http://localhost)
- Copiez le **Client Access Token** (⚠️ pas le Client ID!)
- Collez-le dans le fichier `.env`

Contenu du fichier `.env`:
```
GENIUS_ACCESS_TOKEN=votre_token_ici
```

4. **Tester la configuration**
```bash
python test_api.py
```

Si tout fonctionne, vous verrez "✅ SUCCÈS! Connexion à l'API Genius réussie!"

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
├── test_api.py               # Script de test et configuration API
├── utils.py                  # Utilitaires et statistiques
├── config.json               # Configuration (artistes, paramètres)
├── requirements.txt          # Dépendances Python
├── .env                      # Token API (à créer)
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

### Problème : Erreur "401 Unauthorized" pour tous les artistes

**Symptôme:** Les logs montrent `401 Client Error: Unauthorized` pour chaque requête API.

**Cause:** Token API invalide, manquant ou mal configuré.

**Solution:**

1. **Tester votre configuration:**
   ```bash
   python test_api.py
   ```

2. **Si le fichier .env n'existe pas:**
   ```bash
   python test_api.py setup
   # Suivez les instructions interactives
   ```

3. **Si le token est invalide:**
   - Allez sur https://genius.com/api-clients
   - Vérifiez que vous copiez le **Client Access Token** (longue chaîne)
   - ⚠️ Ne copiez PAS le Client ID ou le Client Secret
   - Mettez à jour le fichier `.env`
   - Retestez avec `python test_api.py`

### Problème : "Token Genius API non configuré"

**Solution:**
- Vérifiez que le fichier `.env` existe : `ls -la .env`
- Vérifiez qu'il contient votre token : `cat .env`
- Utilisez `python test_api.py setup` pour une configuration guidée

### Problème : "Artiste non trouvé"

**Cause:** L'artiste n'est pas sur Genius ou le nom est mal orthographié.

**Solution:**
- Vérifiez l'orthographe exacte du nom dans `config.json`
- Recherchez l'artiste manuellement sur genius.com
- Si l'artiste existe avec un nom différent, mettez à jour `config.json`
- Les artistes sans annotations peuvent être marqués comme "non trouvés"

### Problème : "Limite quotidienne atteinte"

**Solution:**
- Le script attend automatiquement jusqu'au jour suivant
- Pas d'action nécessaire, l'extraction reprendra automatiquement
- Pour réduire la limite : modifiez `requests_per_day` dans `config.json`

### Problème : Le script s'arrête ou crash

**Solution:**
- Consultez les logs dans `logs/`
- Vérifiez votre connexion Internet
- Relancez simplement `python main.py` - il reprendra automatiquement
- Vérifiez les statistiques : `python main.py --stats`

### Problème : Connexion Internet / Timeout

**Solution:**
- Le script retry automatiquement après une erreur réseau
- Si les erreurs persistent, vérifiez votre connexion
- Augmentez le timeout dans `genius_scraper.py` si nécessaire

## 📄 Licence

Ce projet est destiné à la recherche et l'analyse académique. Respectez les conditions d'utilisation de l'API Genius.

## 🤝 Contribution

Les contributions sont les bienvenues ! Ouvrez une issue ou soumettez une pull request.

## 📧 Contact

Pour toute question ou problème, ouvrez une issue sur GitHub.

---

**Note** : Ce projet utilise l'API officielle Genius. Assurez-vous de respecter leurs [conditions d'utilisation](https://genius.com/static/terms).

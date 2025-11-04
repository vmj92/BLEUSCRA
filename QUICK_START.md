# 🚀 Démarrage Rapide - BLEUSCRA

Guide ultra-simplifié pour commencer en 5 minutes.

## Étape 1 : Installation

```bash
pip install -r requirements.txt
```

## Étape 2 : Configuration du Token API

### Option simple (recommandée)
```bash
python test_api.py setup
```

Le script vous guidera pour :
1. Obtenir votre token sur genius.com/api-clients
2. Le configurer automatiquement
3. Tester la connexion

### Vous verrez ceci si tout fonctionne :
```
✅ SUCCÈS! Connexion à l'API Genius réussie!
✓ 10 résultats trouvés pour la recherche test
✓ Exemple de résultat: ...
```

## Étape 3 : Lancer l'extraction

```bash
python main.py
```

C'est tout ! Le système :
- ✅ Extrait automatiquement les 100 artistes
- ✅ Respecte le rate limiting
- ✅ Sauvegarde la progression
- ✅ Reprend automatiquement après interruption

## 📊 Commandes utiles

```bash
# Voir la progression
python main.py --stats

# Recommencer depuis le début
python main.py --reset

# Tester la connexion API
python test_api.py

# Voir les statistiques des données
python utils.py stats
```

## ⚠️ Erreur "401 Unauthorized" ?

Votre token n'est pas valide. Solution :

```bash
# Tester votre configuration
python test_api.py

# Reconfigurer si nécessaire
python test_api.py setup
```

**Points importants :**
- Copiez le **Client Access Token** (longue chaîne)
- ⚠️ Ne copiez PAS le Client ID ou Client Secret
- Le token doit être complet (vérifiez qu'il n'est pas coupé)

## 📝 Où trouver mes données ?

Les données extraites sont dans le dossier `data/` :
- 1 fichier JSON par artiste
- Format : `Nom_Artiste.json`
- Contient : chansons + annotations complètes

## ⏱️ Combien de temps ça prend ?

Avec la limite de 1000 requêtes/jour :
- **15-25 jours** pour les 100 artistes
- Le système reprend automatiquement chaque jour
- Vous pouvez l'interrompre (Ctrl+C) et reprendre quand vous voulez

## 🆘 Besoin d'aide ?

1. Consultez le [README complet](README.md)
2. Vérifiez la section [Dépannage](README.md#-dépannage)
3. Consultez les logs dans `logs/`
4. Testez avec `python test_api.py`

---

**Conseil :** Lancez `python test_api.py` AVANT de lancer l'extraction complète pour éviter les problèmes !

#!/usr/bin/env python3
"""
Script de test pour vérifier la configuration du token API Genius.
Utilise ce script avant de lancer l'extraction complète.
"""

import os
import sys
import requests
from dotenv import load_dotenv


def test_genius_api():
    """Teste la connexion à l'API Genius avec le token configuré."""

    print("="*60)
    print("TEST DE CONNEXION API GENIUS")
    print("="*60)

    # Charger le fichier .env
    if not os.path.exists('.env'):
        print("\n❌ ERREUR: Le fichier .env n'existe pas!")
        print("\nÉtapes pour configurer votre token:")
        print("1. Copiez le fichier template:")
        print("   cp .env.example .env")
        print("\n2. Obtenez votre token API:")
        print("   a) Allez sur https://genius.com")
        print("   b) Connectez-vous ou créez un compte")
        print("   c) Allez sur https://genius.com/api-clients")
        print("   d) Cliquez sur 'New API Client'")
        print("   e) Remplissez le formulaire (nom: BLEUSCRA, app website: http://localhost)")
        print("   f) Cliquez sur 'Save'")
        print("   g) Copiez le 'Client Access Token' (pas le Client ID!)")
        print("\n3. Éditez le fichier .env:")
        print("   nano .env")
        print("   ou")
        print("   vim .env")
        print("\n4. Remplacez 'your_access_token_here' par votre token")
        print("\n5. Relancez ce script: python test_api.py")
        print("="*60)
        return False

    load_dotenv()

    token = os.getenv("GENIUS_ACCESS_TOKEN")

    if not token or token == "your_access_token_here":
        print("\n❌ ERREUR: Token API non configuré dans .env!")
        print("\nLe fichier .env existe mais le token n'est pas configuré.")
        print("\nÉditez le fichier .env et remplacez:")
        print("  GENIUS_ACCESS_TOKEN=your_access_token_here")
        print("par:")
        print("  GENIUS_ACCESS_TOKEN=votre_vrai_token")
        print("\nPour obtenir votre token:")
        print("  1. Allez sur https://genius.com/api-clients")
        print("  2. Créez une nouvelle application")
        print("  3. Copiez le 'Client Access Token'")
        print("="*60)
        return False

    print(f"\n✓ Fichier .env trouvé")
    print(f"✓ Token chargé: {token[:10]}...{token[-10:] if len(token) > 20 else ''}")
    print(f"  (Longueur: {len(token)} caractères)")

    # Tester une requête simple
    print("\n🔄 Test de connexion à l'API Genius...")

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "BLEUSCRA Test Script"
    }

    try:
        # Test avec une recherche simple
        response = requests.get(
            "https://api.genius.com/search",
            headers=headers,
            params={"q": "Booba"},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()

            if data.get("meta", {}).get("status") == 200:
                hits = data.get("response", {}).get("hits", [])

                print("\n✅ SUCCÈS! Connexion à l'API Genius réussie!")
                print(f"✓ {len(hits)} résultats trouvés pour la recherche test")

                if hits:
                    first_hit = hits[0].get("result", {})
                    artist = first_hit.get("primary_artist", {})
                    print(f"✓ Exemple de résultat: {first_hit.get('title')} - {artist.get('name')}")

                print("\n" + "="*60)
                print("Votre configuration est correcte!")
                print("Vous pouvez maintenant lancer l'extraction:")
                print("  python main.py")
                print("="*60)
                return True
            else:
                print(f"\n❌ Erreur API: {data.get('meta', {})}")
                return False

        elif response.status_code == 401:
            print("\n❌ ERREUR 401: Token invalide ou non autorisé!")
            print("\nVotre token semble incorrect. Vérifiez que:")
            print("1. Vous avez bien copié le 'Client Access Token' (pas le Client ID)")
            print("2. Le token est complet (pas de caractères manquants)")
            print("3. Le token n'a pas expiré")
            print("\nPour régénérer un token:")
            print("  1. Allez sur https://genius.com/api-clients")
            print("  2. Cliquez sur votre application")
            print("  3. Générez un nouveau 'Client Access Token'")
            print("  4. Mettez à jour le fichier .env")
            return False

        else:
            print(f"\n❌ Erreur HTTP {response.status_code}: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("\n❌ ERREUR: Impossible de se connecter à api.genius.com")
        print("Vérifiez votre connexion Internet")
        return False

    except requests.exceptions.Timeout:
        print("\n❌ ERREUR: Timeout lors de la connexion")
        print("L'API Genius ne répond pas, réessayez plus tard")
        return False

    except Exception as e:
        print(f"\n❌ ERREUR inattendue: {e}")
        return False


def create_env_file():
    """Aide l'utilisateur à créer le fichier .env."""
    print("\n🔧 Création du fichier .env...")

    if os.path.exists('.env'):
        response = input("Le fichier .env existe déjà. Le remplacer? (oui/non): ")
        if response.lower() not in ['oui', 'yes', 'y', 'o']:
            print("Opération annulée.")
            return

    print("\nInstructions pour obtenir votre token:")
    print("1. Ouvrez https://genius.com/api-clients dans votre navigateur")
    print("2. Connectez-vous ou créez un compte Genius")
    print("3. Cliquez sur 'New API Client'")
    print("4. Remplissez:")
    print("   - App Name: BLEUSCRA")
    print("   - App Website URL: http://localhost")
    print("   - Redirect URI: http://localhost")
    print("5. Cliquez sur 'Save'")
    print("6. Copiez le 'Client Access Token' (longue chaîne de caractères)")

    token = input("\nCollez votre Client Access Token ici: ").strip()

    if not token or len(token) < 20:
        print("❌ Token invalide (trop court). Réessayez.")
        return

    with open('.env', 'w') as f:
        f.write(f"# Genius API Access Token\n")
        f.write(f"# Obtenez votre token depuis : https://genius.com/api-clients\n")
        f.write(f"GENIUS_ACCESS_TOKEN={token}\n")

    print("\n✅ Fichier .env créé avec succès!")
    print("\n🔄 Test de la connexion...")

    # Tester immédiatement
    if test_genius_api():
        print("\n🎉 Configuration terminée avec succès!")
    else:
        print("\n⚠️ Le token ne fonctionne pas. Vérifiez et réessayez.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        create_env_file()
    else:
        result = test_genius_api()
        sys.exit(0 if result else 1)

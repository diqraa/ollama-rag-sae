# Local RAG Chatbot - Accompagnement pour la SAE Informatique (BUT2)

Ce projet est un chatbot **gratuit, local et confidentiel** conçu pour aider les étudiants de deuxième année de BUT Informatique à retrouver les informations utiles dans leurs documents de SAE. Les PDF sont indexés localement dans Chroma et les réponses sont générées par Ollama.

Grâce à une architecture **RAG** et au modèle **Llama 3**, ce chatbot fournit des réponses instantanées et précises en se basant exclusivement sur les documents officiels du projet.

##  Cas d'utilisation clés

* **Centralisation des spécifications :** Retrouvez instantanément les contraintes architecturales, de base de données ou logicielles imposées par les enseignants, sans avoir à parcourir un PDF de 50 pages.
* **Gestion de projet & Deadlines :** Fonctionne comme un Scrum Master virtuel capable de suivre le calendrier des sprints, les dates limites des jalons (milestones) et la documentation requise.
* **100% Local & Gratuit :** S'exécute entièrement hors ligne sur votre machine grâce à **Ollama**. Aucune clé API payante n'est requise, garantissant ainsi la confidentialité totale de l'ensemble de vos données.

## Architecture technique

* **Modèle de langage :** Llama 3 via [Ollama](https://ollama.com)
* **Embeddings :** `nomic-embed-text` via Ollama
* **Recherche vectorielle :** ChromaDB, avec index persistant localement
* **Sources :** fichiers PDF placés dans `data/source_pdfs`

## Fonctionnalités

* Recherche sémantique dans les PDF et réponses accompagnées de citations (fichier et page).
* L'assistant indique quand les documents ne permettent pas de répondre et ne doit pas inventer de consignes.
* Les PDF, l'index et l'historique de conversation restent sur la machine ; les appels au modèle sont adressés uniquement à Ollama sur `localhost`, sans télémétrie Chroma ni collecte d'usage Streamlit.
* Une interface web locale permet de discuter avec le chatbot depuis un navigateur.

## À propos

Créé par **Aicha**, alias **diqraa**. Pour plus d'informations, [contacte-moi par e-mail](mailto:aicha.dabo@etu.u-pec.fr).

![Capture d’écran du chatbot SAE](https://github.com/user-attachments/assets/95e65aac-80a2-4663-ad16-76ead734e2c1)

## Installation et lancement

### Démarrage rapide sous Windows

Installe une seule fois [Git](https://git-scm.com/download/win), [Python 3.10+](https://www.python.org/downloads/windows/) et [Ollama](https://ollama.com/download/windows). Pendant l'installation de Python, coche **Add Python to PATH**.

Ouvre PowerShell dans le dossier où tu veux mettre le projet, puis copie ces trois commandes :

```powershell
git clone https://github.com/diqraa/ollama-rag-sae.git
cd ollama-rag-sae
powershell -ExecutionPolicy Bypass -File .\start-chatbot.ps1
```

Le script crée son propre environnement Python, installe les dépendances, démarre Ollama si nécessaire et télécharge les modèles manquants. Il affiche ensuite un lien local à ouvrir dans ton navigateur, généralement **http://localhost:8501**. Le premier lancement peut prendre plusieurs minutes, car Llama 3 et les dépendances doivent être téléchargés. Les lancements suivants réutilisent les téléchargements locaux. Pour arrêter le serveur web, appuie sur `Ctrl+C` dans PowerShell.

Pour installer les dépendances et modèles sans lancer l'interface :

```powershell
powershell -ExecutionPolicy Bypass -File .\start-chatbot.ps1 -InstallOnly
```

### Installation manuelle

Prérequis : Python 3.10+ et [Ollama](https://ollama.com) installé et démarré.

1. À la racine du dépôt, créez un environnement Python local et installez les dépendances :

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

2. Téléchargez les deux modèles nécessaires :

   ```powershell
   ollama pull llama3
   ollama pull nomic-embed-text
   ```

3. La présentation est déjà fournie dans `data/source_pdfs`. Ajoutez les autres PDF officiels dans ce dossier ou dans ses sous-dossiers.

4. À la racine du projet, lancez l'interface web :

   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run src/web_app.py
   ```

Streamlit affiche son adresse locale, généralement **http://localhost:8501**, dans le terminal. Clique sur ce lien pour ouvrir la page. Si un modèle Ollama manque, la page indique la commande `ollama pull` nécessaire.

Au premier lancement, les PDF sont découpés et indexés lorsque la première question est posée. L'index est enregistré dans `data/chroma_db` et est réutilisé tant que le contenu des PDF ne change pas. Après toute modification des PDF, l'index est automatiquement reconstruit à la prochaine question.

Pour imposer un dossier PDF ou un autre modèle, définissez les variables d'environnement `SAE_SOURCE_DIR`, `SAE_CHAT_MODEL` ou `SAE_EMBEDDING_MODEL` avant le lancement. Par exemple :

```powershell
$env:SAE_SOURCE_DIR = "data\source_pdfs"
.\.venv\Scripts\python.exe -m streamlit run src/web_app.py
```

L'ancienne interface en terminal reste disponible avec `.\.venv\Scripts\python.exe -m src.chatbot`. Pour reconstruire l'index depuis le terminal, utilisez `.\.venv\Scripts\python.exe -m src.chatbot --rebuild`.

Cliquez sur **Clear cache** dans le menu Streamlit pour vider les ressources mises en cache en mémoire. L'index persistant sur disque est conservé.

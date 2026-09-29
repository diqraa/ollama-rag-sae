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

 **BON COURAGE !**

# Local RAG Chatbot - Accompagnement pour la SAE Informatique (BUT2)

Ce projet est une solution de chatbot **100% gratuite, locale et confidentielle** conçue pour aider les étudiants en deuxième année de BUT Informatique à gérer leurs projets de SAE

Grâce à une architecture **RAG** et au modèle **Llama 3**, ce chatbot fournit des réponses instantanées et précises en se basant exclusivement sur les documents officiels du projet.

##  Cas d'utilisation clés

* **Centralisation des spécifications :** Retrouvez instantanément les contraintes architecturales, de base de données ou logicielles imposées par les enseignants, sans avoir à parcourir un PDF de 50 pages.
* **Gestion de projet & Deadlines :** Fonctionne comme un Scrum Master virtuel capable de suivre le calendrier des sprints, les dates limites des jalons (milestones) et la documentation requise.
* **100% Local & Gratuit :** S'exécute entièrement hors ligne sur votre machine grâce à **Ollama**. Aucune clé API payante n'est requise, garantissant ainsi la confidentialité totale de l'ensemble de vos données.

##  Architecture Technique

* **Modèle de langage (LLM) :** Llama 3 via [Ollama](https://ollama.com "Ollama home")
* **Framework RAG :** Architecture de génération augmentée par récupération
* **Source de données :** Documents officiels (sujets de SAE, barèmes de notation, contraintes techniques, livrables)

##  Fonctionnalités principales

*  **Recherche sémantique :** Compréhension des questions complexes liées au sujet de la SAE.
* **Zéro Hallucination :** Réponses basées *strictement* sur le contexte fourni par les documents du projet.
*  **Confidentialité totale :** Aucune donnée ne quitte votre ordinateur étant donné que tout est fait en local.

##  Prérequis

Pour faire tourner ce projet localement, vous aurez besoin de :
* Python 3.10+
* [Ollama](https://ollama.com "Ollama download") installé avec le modèle Llama 3 (`ollama run llama3`)
* Vos documents de SAE au format PDF ou texte placés dans le dossier de données source.

 **BON COURAGE !**

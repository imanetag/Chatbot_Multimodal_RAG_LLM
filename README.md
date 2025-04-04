"""
Documentation for the multimodal RAG chatbot
"""

# Chatbot Multimodal RAG pour Assistance d'Entreprise
## Documentation d'utilisation et de déploiement

### Vue d'ensemble

Ce projet implémente un chatbot multimodal basé sur l'architecture RAG (Retrieval-Augmented Generation) pour l'assistance d'entreprise. Le chatbot est capable de traiter et de comprendre différents types de médias (texte, images, audio, vidéo) et de fournir des réponses pertinentes en se basant sur une base de connaissances interne.

### Cas d'utilisation

Le chatbot est conçu pour les cas d'utilisation suivants :

1. **Assistance aux Employés**
   - Aide interne (RH, IT, logistique)
   - Onboarding facilité (procédures, formations)
   - Accès rapide à la documentation (SharePoint)

2. **Knowledge Management / Recherche Documentaire**
   - Recherche sémantique dans de multiples formats (PDF, DOCX, etc.)
   - Capitalisation et mise à jour continue des connaissances

3. **Maintenance et Diagnostic**
   - Envoi de photos/vidéos, le chatbot identifie la pièce et fournit le guide
   - Procédures de dépannage automatisées, gains de temps sur le terrain

4. **Help Desk Interne**
   - FAQ IT récurrentes (mots de passe, logiciels)
   - Escalade automatique vers un expert si nécessaire

### Architecture

Le système est composé des modules suivants :

1. **Ingestion de données**
   - Traitement de documents (PDF, DOCX, PPTX, Excel, OneNote)
   - Traitement d'images avec OCR
   - Traitement audio/vidéo

2. **Système d'embeddings**
   - Génération d'embeddings pour le texte
   - Génération d'embeddings pour les images
   - Stockage des embeddings dans MongoDB

3. **Système de récupération (Retrieval)**
   - Recherche vectorielle
   - Scoring de pertinence
   - Construction du contexte

4. **Système de génération (LLM)**
   - Intégration avec modèle LLM
   - Ingénierie de prompts
   - Gestion du contexte

5. **Capacités multimodales**
   - Traitement d'images
   - Traitement audio
   - Traitement vidéo
   - Fusion de contexte multimodal

6. **Interface utilisateur**
   - Interface web responsive
   - Support pour l'upload de fichiers
   - Affichage des résultats multimodaux

### Prérequis

- Python 3.10+
- MongoDB 6.0+
- Dépendances Python (voir requirements*.txt)

### Installation

1. Clonez le dépôt :
   ```
   git clone <repository-url>
   cd multimodal_rag_chatbot
   ```

2. Installez les dépendances :
   ```
   pip install -r requirements_core.txt
   pip install -r requirements_web_search.txt
   pip install -r requirements_models.txt
   ```

3. Assurez-vous que MongoDB est installé et en cours d'exécution :
   ```
   sudo systemctl start mongod
   ```

### Configuration

Le fichier de configuration principal se trouve dans `config/config.py`. Vous pouvez modifier les paramètres suivants :

- `MONGODB_HOST` et `MONGODB_PORT` : Configuration de MongoDB
- `TEXT_EMBEDDING_MODEL` et `IMAGE_EMBEDDING_MODEL` : Modèles d'embedding
- `LLM_MODEL_PATH` et `LLM_MODEL_TYPE` : Configuration du LLM
- `WEB_HOST` et `WEB_PORT` : Configuration du serveur web

### Ingestion de données

Pour ingérer des documents dans la base de connaissances :

```
python main.py --file /chemin/vers/document.pdf
```

Pour ingérer un répertoire entier :

```
python main.py --dir /chemin/vers/repertoire --recursive
```

### Démarrage du chatbot

Pour démarrer le chatbot :

```
python deploy/deploy.py
```

Ou pour démarrer uniquement le serveur web :

```
python deploy/deploy.py --web
```

### Utilisation de l'interface web

1. Accédez à l'interface web à l'adresse `http://localhost:8000`
2. Posez vos questions dans la zone de texte
3. Pour les requêtes multimodales, utilisez le bouton "Joindre un fichier"
4. L'historique de conversation est maintenu pendant la session

### Monitoring et logs

Les logs sont stockés dans le répertoire `logs/` :

- `queries.log` : Historique des requêtes et réponses
- `errors.log` : Erreurs rencontrées
- `performance.log` : Métriques de performance

### Limitations actuelles

En raison des contraintes de ressources, certaines fonctionnalités sont implémentées avec des alternatives légères :

1. **Embeddings** : Utilisation de TF-IDF au lieu de modèles transformer complets
2. **LLM** : Approche de fallback basée sur la récupération directe
3. **Traitement audio/vidéo** : Extraction de métadonnées basiques sans transcription complète

### Améliorations futures

1. Intégration de modèles LLM complets (Gemma ou DeepSeek Janus)
2. Amélioration des capacités de traitement audio/vidéo
3. Optimisation des performances de recherche vectorielle
4. Ajout de fonctionnalités d'apprentissage continu

### Structure du projet

```
multimodal_rag_chatbot/
├── config/
│   └── config.py
├── data/
│   └── uploads/
├── deploy/
│   ├── deploy.py
│   └── monitor.py
├── logs/
├── models/
├── src/
│   ├── context_manager.py
│   ├── data_ingestion.py
│   ├── document_processor.py
│   ├── embedding_generator.py
│   ├── llm_manager.py
│   ├── multimodal_chatbot.py
│   ├── multimodal_fusion.py
│   ├── multimodal_processor.py
│   ├── prompt_manager.py
│   ├── relevance_scorer.py
│   ├── response_generator.py
│   ├── retrieval_pipeline.py
│   └── retrieval_system.py
├── utils/
│   ├── base_utils.py
│   └── db_manager.py
├── web/
│   ├── app.py
│   ├── static/
│   └── templates/
├── main.py
├── requirements_core.txt
├── requirements_models.txt
├── requirements_web_search.txt
└── todo.md
```

### Dépannage

1. **MongoDB ne démarre pas**
   - Vérifiez que MongoDB est installé : `mongod --version`
   - Vérifiez le statut du service : `sudo systemctl status mongod`
   - Assurez-vous que le répertoire de données existe : `/var/lib/mongodb`

2. **Erreurs d'importation de modules**
   - Vérifiez que toutes les dépendances sont installées
   - Assurez-vous que vous exécutez les commandes depuis le répertoire racine du projet

3. **Le serveur web ne démarre pas**
   - Vérifiez que le port n'est pas déjà utilisé : `netstat -tuln | grep 8000`
   - Vérifiez les logs pour plus de détails

### Support

Pour toute question ou problème, veuillez consulter les logs ou contacter l'équipe de support.

---

© 2025 Multimodal RAG Chatbot - Tous droits réservés

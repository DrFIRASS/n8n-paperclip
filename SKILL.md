---
name: n8n-paperclip
description: >
  Pilote et automatise une instance n8n via son API REST depuis un agent Paperclip.
  Utilise ce skill quand tu dois : lister, créer, activer ou désactiver des workflows n8n,
  surveiller des exécutions, déclencher manuellement un workflow, valider une structure
  de workflow, analyser les performances ou déboguer des automatisations.
  Ne pas utiliser pour des tâches sans rapport avec n8n ou l'automatisation de workflows.
author: Dr. FIRAS
version: 1.0.0
platform: paperclip
metadata:
  requires:
    env:
      - N8N_API_KEY
      - N8N_BASE_URL
---

# n8n Workflow Automation — Skill Paperclip

Skill de gestion complète des workflows n8n : création, validation, surveillance des
exécutions et optimisation des performances. Conçu exclusivement pour les agents
déployés sur **Paperclip AI**.

---

## ⚙️ Configuration Paperclip

### Variables d'environnement requises

Ce skill nécessite deux variables d'environnement. Sur Paperclip (Docker), elles
doivent être définies dans le fichier `.env` du container ou dans les settings de
l'agent.

**Dans le container Docker Paperclip :**
```bash
docker exec -it <container-id> bash
cat >> /paperclip/.env << 'EOF'
N8N_API_KEY=ta-cle-api-n8n
N8N_BASE_URL=https://ton-instance.app.n8n.cloud
EOF
```

**Vérification de la connexion :**
```bash
python3 scripts/n8n_api.py list-workflows --pretty
```

> **Sécurité :** Ne jamais stocker les clés API dans des fichiers shell (`~/.bashrc`).
> Utilise toujours le fichier `.env` de Paperclip ou un gestionnaire de secrets.

### Obtenir ta clé API n8n

1. Connecte-toi à ton instance n8n
2. Va dans **Settings → API**
3. Clique sur **Create API Key**
4. Copie la clé et place-la dans `N8N_API_KEY`

---

## 🚀 Règles de création de workflows

**Toujours :**
- ✅ Générer des workflows **complets et fonctionnels** avec tous les nœuds configurés
- ✅ Inclure de vrais nœuds HTTP Request pour les appels API
- ✅ Ajouter des nœuds Code pour la transformation de données
- ✅ Connecter tous les nœuds entre eux correctement
- ✅ Utiliser les vrais types de nœuds n8n (`n8n-nodes-base.httpRequest`, `n8n-nodes-base.code`, `n8n-nodes-base.set`)

**Jamais :**
- ❌ Créer des nœuds "placeholder" ou "TODO"
- ❌ Laisser des workflows incomplets nécessitant une configuration manuelle
- ❌ Utiliser des nœuds texte à la place de vrais nœuds fonctionnels

**Exemple de bon workflow :**
```
Déclencheur → Configuration → HTTP Request → Code (traitement) → Réponse
```

---

## 📋 Référence rapide

### Gestion des workflows

```bash
# Lister tous les workflows
python3 scripts/n8n_api.py list-workflows --pretty

# Lister uniquement les workflows actifs
python3 scripts/n8n_api.py list-workflows --active true --pretty

# Obtenir les détails d'un workflow
python3 scripts/n8n_api.py get-workflow --id <workflow-id> --pretty

# Créer un workflow depuis un fichier JSON
python3 scripts/n8n_api.py create --from-file workflow.json

# Activer un workflow
python3 scripts/n8n_api.py activate --id <workflow-id>

# Désactiver un workflow
python3 scripts/n8n_api.py deactivate --id <workflow-id>
```

### Exécution manuelle

```bash
# Déclencher un workflow
python3 scripts/n8n_api.py execute --id <workflow-id>

# Déclencher avec des données personnalisées
python3 scripts/n8n_api.py execute --id <workflow-id> --data '{"cle": "valeur"}'
```

### Surveillance des exécutions

```bash
# Voir les dernières exécutions (tous workflows)
python3 scripts/n8n_api.py list-executions --limit 10 --pretty

# Exécutions d'un workflow spécifique
python3 scripts/n8n_api.py list-executions --id <workflow-id> --limit 20 --pretty

# Détails d'une exécution précise
python3 scripts/n8n_api.py get-execution --id <execution-id> --pretty

# Statistiques d'un workflow
python3 scripts/n8n_api.py stats --id <workflow-id> --days 7 --pretty
```

### Validation et tests

```bash
# Valider la structure d'un workflow existant
python3 scripts/n8n_tester.py validate --id <workflow-id>

# Valider depuis un fichier local
python3 scripts/n8n_tester.py validate --file workflow.json --pretty

# Test à sec avec des données
python3 scripts/n8n_tester.py dry-run --id <workflow-id> --data '{"email": "test@exemple.com"}'

# Test à sec depuis un fichier de données
python3 scripts/n8n_tester.py dry-run --id <workflow-id> --data-file test-data.json

# Rapport de test complet
python3 scripts/n8n_tester.py report --id <workflow-id>

# Suite de tests (plusieurs cas)
python3 scripts/n8n_tester.py test-suite --id <workflow-id> --test-suite test-cases.json
```

### Optimisation des performances

```bash
# Analyse complète d'un workflow
python3 scripts/n8n_optimizer.py analyze --id <workflow-id> --pretty

# Analyse sur une période donnée
python3 scripts/n8n_optimizer.py analyze --id <workflow-id> --days 30 --pretty

# Suggestions d'optimisation classées par priorité
python3 scripts/n8n_optimizer.py suggest --id <workflow-id> --pretty

# Rapport d'optimisation complet
python3 scripts/n8n_optimizer.py report --id <workflow-id>
```

---

## 🔄 Scénarios courants

### 1. Déployer un nouveau workflow

```bash
# Étape 1 : Valider la structure
python3 scripts/n8n_tester.py validate --file nouveau-workflow.json --pretty

# Étape 2 : Tester avec des données réelles
python3 scripts/n8n_tester.py dry-run --id <workflow-id> \
  --data '{"email": "test@exemple.com", "nom": "Test"}'

# Étape 3 : Si tout est bon, activer
python3 scripts/n8n_api.py activate --id <workflow-id>
```

### 2. Déboguer un workflow en erreur

```bash
# Vérifier les dernières exécutions
python3 scripts/n8n_api.py list-executions --id <workflow-id> --limit 10 --pretty

# Lire les détails de l'exécution échouée
python3 scripts/n8n_api.py get-execution --id <execution-id> --pretty

# Valider la structure actuelle
python3 scripts/n8n_tester.py validate --id <workflow-id>

# Générer un rapport de diagnostic
python3 scripts/n8n_tester.py report --id <workflow-id>
```

### 3. Optimiser un workflow lent

```bash
# Analyser les 30 derniers jours
python3 scripts/n8n_optimizer.py analyze --id <workflow-id> --days 30 --pretty

# Obtenir les recommandations
python3 scripts/n8n_optimizer.py suggest --id <workflow-id> --pretty

# Rapport complet avec métriques
python3 scripts/n8n_optimizer.py report --id <workflow-id>
```

### 4. Surveiller la santé globale

```bash
# Tous les workflows actifs
python3 scripts/n8n_api.py list-workflows --active true --pretty

# Exécutions récentes sur tous les workflows
python3 scripts/n8n_api.py list-executions --limit 20 --pretty

# Rapport de santé par workflow critique
python3 scripts/n8n_optimizer.py report --id <workflow-id>
```

---

## ✅ Vérifications de validation

### Structure
- Présence des champs obligatoires (nœuds, connexions)
- Chaque nœud a un nom et un type valide
- Les cibles des connexions existent
- Détection des nœuds déconnectés

### Configuration
- Nœuds avec credentials correctement configurés
- Paramètres obligatoires renseignés
- URLs présentes sur les nœuds HTTP
- Chemins définis sur les nœuds Webhook

### Flux d'exécution
- Présence d'un nœud déclencheur
- Flux d'exécution cohérent
- Absence de dépendances circulaires
- Nœuds de fin identifiés

---

## 📊 Score de performance

Les workflows reçoivent un score de 0 à 100 basé sur :

| Critère | Poids |
|---|---|
| Taux de succès | 50% |
| Complexité (moins = mieux) | 30% |
| Goulots d'étranglement | -10 à -20 pts |
| Bonnes pratiques appliquées | +5 pts chacune |

**Interprétation :**
- **90-100** → Excellent, workflow bien optimisé
- **70-89** → Bon, quelques améliorations possibles
- **50-69** → Correct, optimisation recommandée
- **0-49** → Problèmes significatifs à traiter

---

## 🛠️ Dépannage

### Erreur : Variable N8N_API_KEY introuvable
```
Solution : Ajouter la variable dans /paperclip/.env
puis redémarrer le container Docker
```

### Erreur : HTTP 401 Unauthorized
```
Solution :
1. Vérifier que la clé API est correcte
2. Vérifier que N8N_BASE_URL est bien défini
3. Confirmer que l'accès API est activé dans n8n (Settings → API)
```

### Erreur : Timeout d'exécution
```
Solution :
1. Vérifier l'absence de boucles infinies
2. Réduire la taille des données de test
3. Optimiser les opérations coûteuses
4. Configurer un timeout dans les settings du workflow
```

### Erreur : HTTP 429 Too Many Requests
```
Solution :
1. Ajouter des nœuds Wait entre les appels API
2. Implémenter un backoff exponentiel
3. Utiliser le traitement par lots (batch)
4. Consulter les limites de l'API concernée
```

---

## 📁 Structure du skill

```
skills/n8n-paperclip/
├── SKILL.md                  ← Ce fichier
├── scripts/
│   ├── n8n_api.py            ← Client API principal
│   ├── n8n_tester.py         ← Validation et tests
│   └── n8n_optimizer.py      ← Analyse de performance
└── references/
    └── api.md                ← Référence API n8n
```

---

## 📚 Ressources

- Documentation n8n : https://docs.n8n.io
- Référence API n8n : https://docs.n8n.io/api/
- Communauté n8n : https://community.n8n.io
- Documentation Paperclip : https://docs.paperclip.ing

---

*Skill créé par **Dr. FIRAS** — Formation IA & Automatisation*
*Optimisé pour Paperclip AI — https://paperclip.ing*

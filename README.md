# 🤖 n8n-paperclip — Skill Paperclip AI

> Skill de gestion complète des workflows n8n pour agents **Paperclip AI**.  
> Créé par **Dr. FIRAS** — Formation IA & Automatisation

---

## 📌 À propos

Ce skill permet à un agent Paperclip de piloter une instance **n8n** via son API REST.  
Il a été conçu spécifiquement pour **Paperclip AI** (déployé sur Docker/VPS) et ne nécessite aucune configuration OpenClaw.

### Ce que l'agent peut faire avec ce skill :

- 📋 Lister, créer, activer et désactiver des workflows
- ▶️ Déclencher manuellement des workflows avec des données personnalisées
- 🔍 Surveiller les exécutions en temps réel
- ✅ Valider la structure d'un workflow avant déploiement
- 🧪 Tester un workflow avec des données réelles (dry-run)
- 📊 Analyser les performances et obtenir des recommandations
- 🛠️ Déboguer les automatisations en erreur

---
## 🖥️ Héberger Paperclip sur VPS

Pour déployer Paperclip AI sur un VPS, je recommande **Hostinger** — c'est
le serveur que j'utilise personnellement pour mon VPS Paperclip.

👉 [Obtenir un VPS Paperclip](https://www.hostinger.fr/gopaperclip)

🎁 **Coupon de réduction : `GOPAPERCLIP`**


## 📁 Structure du skill

```
n8n-paperclip/
├── SKILL.md                  ← Instructions principales pour l'agent
├── scripts/
│   ├── n8n_api.py            ← Client API n8n (gestion des workflows)
│   ├── n8n_tester.py         ← Validation et tests des workflows
│   └── n8n_optimizer.py      ← Analyse de performance et recommandations
├── references/
│   └── api.md                ← Référence API n8n
└── README.md                 ← Ce fichier
```

---

## ⚙️ Installation sur Paperclip

### Prérequis

- Paperclip AI déployé sur un VPS avec Docker
- Une instance n8n (cloud ou auto-hébergée)
- Python 3 + la librairie `requests` installée dans le container

### Étape 1 — Entrer dans le container Paperclip

```bash
docker ps
docker exec -it <container-id> bash
```

### Étape 2 — Créer le dossier du skill

```bash
mkdir -p /paperclip/skills/n8n-paperclip/scripts
mkdir -p /paperclip/skills/n8n-paperclip/references
```

### Étape 3 — Télécharger les fichiers du skill

```bash
# SKILL.md
curl -o /paperclip/skills/n8n-paperclip/SKILL.md \
  https://raw.githubusercontent.com/dr-firas/n8n-paperclip/main/SKILL.md

# Scripts Python
curl -o /paperclip/skills/n8n-paperclip/scripts/n8n_api.py \
  https://raw.githubusercontent.com/dr-firas/n8n-paperclip/main/scripts/n8n_api.py

curl -o /paperclip/skills/n8n-paperclip/scripts/n8n_tester.py \
  https://raw.githubusercontent.com/dr-firas/n8n-paperclip/main/scripts/n8n_tester.py

curl -o /paperclip/skills/n8n-paperclip/scripts/n8n_optimizer.py \
  https://raw.githubusercontent.com/dr-firas/n8n-paperclip/main/scripts/n8n_optimizer.py
```

### Étape 4 — Configurer les variables d'environnement

```bash
cat >> /paperclip/.env << 'EOF'
N8N_API_KEY=ta-cle-api-n8n
N8N_BASE_URL=https://ton-instance.app.n8n.cloud
EOF
```

> **Comment obtenir ta clé API n8n :**  
> Connecte-toi à n8n → **Settings → API → Create API Key**

### Étape 5 — Vérifier la connexion

```bash
python3 /paperclip/skills/n8n-paperclip/scripts/n8n_api.py list-workflows --pretty
```

✅ Si tu vois la liste de tes workflows, le skill est opérationnel !

### Étape 6 — Redémarrer le container

```bash
exit
docker restart <container-id>
```

---

## 🚀 Utilisation rapide

Une fois installé, parle à ton agent Paperclip en langage naturel :

```
Liste tous mes workflows n8n actifs
```
```
Active le workflow avec l'ID abc123
```
```
Montre-moi les 10 dernières exécutions du workflow xyz
```
```
Analyse les performances du workflow abc et donne-moi des recommandations
```
```
Valide la structure du workflow abc avant que je l'active
```

---

## 🔧 Commandes disponibles

### Gestion des workflows
| Commande | Description |
|---|---|
| `list-workflows --pretty` | Lister tous les workflows |
| `list-workflows --active true --pretty` | Lister uniquement les actifs |
| `get-workflow --id <id>` | Détails d'un workflow |
| `create --from-file workflow.json` | Créer depuis un fichier JSON |
| `activate --id <id>` | Activer un workflow |
| `deactivate --id <id>` | Désactiver un workflow |
| `execute --id <id>` | Déclencher manuellement |
| `stats --id <id> --days 7` | Statistiques sur 7 jours |

### Validation et tests
| Commande | Description |
|---|---|
| `validate --id <id>` | Valider la structure |
| `dry-run --id <id> --data '{...}'` | Test à sec avec données |
| `report --id <id>` | Rapport de validation complet |
| `test-suite --id <id> --test-suite cases.json` | Suite de tests |

### Optimisation
| Commande | Description |
|---|---|
| `analyze --id <id> --days 30` | Analyse complète |
| `suggest --id <id>` | Recommandations d'optimisation |
| `report --id <id>` | Rapport complet avec score |

---

## 📊 Score de performance

Les workflows reçoivent un score de **0 à 100** :

| Score | Niveau | Signification |
|---|---|---|
| 90 – 100 | 🟢 Excellent | Workflow bien optimisé |
| 70 – 89 | 🟡 Bon | Quelques améliorations possibles |
| 50 – 69 | 🟠 Moyen | Optimisation recommandée |
| 0 – 49 | 🔴 Faible | Problèmes significatifs à corriger |

---

## 🛠️ Dépannage

**Erreur : `N8N_API_KEY` non trouvé**
```bash
# Vérifier que la variable est bien définie
cat /paperclip/.env | grep N8N
```

**Erreur : HTTP 401 Unauthorized**
```
→ Clé API invalide. Régénère-la dans n8n : Settings → API
```

**Erreur : `requests` module not found**
```bash
pip install requests --break-system-packages
```

**Le skill n'est pas chargé par l'agent**
```
→ Redémarre le container Docker après l'installation
→ Vérifie que SKILL.md est bien dans /paperclip/skills/n8n-paperclip/
```

---

## 📋 Prérequis techniques

- Python 3.8+
- Librairie `requests` (`pip install requests`)
- Paperclip AI avec adapter `claude_local`
- Instance n8n (cloud ou self-hosted) avec API activée

---

## 📄 Licence

MIT — Libre d'utilisation, de modification et de redistribution.

---

## 👤 Auteur

**Dr. FIRAS**  
Formateur en IA & Automatisation  
Créateur de contenu YouTube sur l'IA et n8n

🔗 LinkedIn : [linkedin.com/in/doctor-firass](https://www.linkedin.com/in/doctor-firass/)

---

*Skill conçu pour [Paperclip AI](https://paperclip.ing) — La plateforme d'orchestration d'agents IA autonomes.*

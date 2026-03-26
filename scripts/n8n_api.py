#!/usr/bin/env python3
"""
n8n API Client — Skill Paperclip
Auteur : Dr. FIRAS — Formation IA & Automatisation
Description : Client Python pour piloter une instance n8n via son API REST.
              Conçu pour être utilisé par un agent Paperclip AI.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print("Erreur : le module 'requests' n'est pas installé.")
    print("Installe-le avec : pip install requests")
    sys.exit(1)


# ─────────────────────────────────────────────
# CLIENT PRINCIPAL
# ─────────────────────────────────────────────

class N8nClient:
    """Client pour l'API REST n8n."""

    def __init__(self):
        self.api_key = os.environ.get("N8N_API_KEY")
        self.base_url = os.environ.get("N8N_BASE_URL", "").rstrip("/")

        if not self.api_key:
            print("Erreur : N8N_API_KEY n'est pas défini.")
            print("Ajoute-le dans /paperclip/.env puis redémarre le container.")
            sys.exit(1)

        if not self.base_url:
            print("Erreur : N8N_BASE_URL n'est pas défini.")
            print("Ajoute-le dans /paperclip/.env puis redémarre le container.")
            sys.exit(1)

        self.headers = {
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.api_base = f"{self.base_url}/api/v1"

    def _get(self, endpoint, params=None):
        """Requête GET vers l'API n8n."""
        url = f"{self.api_base}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            print(f"Erreur de connexion : impossible de joindre {self.base_url}")
            print("Vérifie que N8N_BASE_URL est correct et que ton instance n8n est en ligne.")
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            print(f"Erreur HTTP {response.status_code} : {e}")
            if response.status_code == 401:
                print("Clé API invalide. Vérifie N8N_API_KEY.")
            elif response.status_code == 404:
                print("Ressource introuvable. Vérifie l'ID fourni.")
            sys.exit(1)

    def _post(self, endpoint, payload=None):
        """Requête POST vers l'API n8n."""
        url = f"{self.api_base}{endpoint}"
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Erreur HTTP {response.status_code} : {e}")
            sys.exit(1)

    def _patch(self, endpoint, payload=None):
        """Requête PATCH vers l'API n8n."""
        url = f"{self.api_base}{endpoint}"
        try:
            response = requests.patch(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Erreur HTTP {response.status_code} : {e}")
            sys.exit(1)

    # ── WORKFLOWS ──────────────────────────────

    def list_workflows(self, active=None):
        """Retourne la liste des workflows."""
        params = {}
        if active is not None:
            params["active"] = str(active).lower()
        data = self._get("/workflows", params=params)
        return data.get("data", [])

    def get_workflow(self, workflow_id):
        """Retourne les détails d'un workflow."""
        return self._get(f"/workflows/{workflow_id}")

    def create_workflow(self, workflow_data):
        """Crée un nouveau workflow à partir d'un dict."""
        return self._post("/workflows", payload=workflow_data)

    def activate_workflow(self, workflow_id):
        """Active un workflow."""
        return self._patch(f"/workflows/{workflow_id}", payload={"active": True})

    def deactivate_workflow(self, workflow_id):
        """Désactive un workflow."""
        return self._patch(f"/workflows/{workflow_id}", payload={"active": False})

    # ── EXECUTIONS ─────────────────────────────

    def list_executions(self, workflow_id=None, limit=10):
        """Retourne la liste des exécutions récentes."""
        params = {"limit": limit}
        if workflow_id:
            params["workflowId"] = workflow_id
        data = self._get("/executions", params=params)
        return data.get("data", [])

    def get_execution(self, execution_id):
        """Retourne les détails d'une exécution."""
        return self._get(f"/executions/{execution_id}")

    def execute_workflow(self, workflow_id, data=None):
        """Déclenche manuellement un workflow."""
        payload = {}
        if data:
            payload = data if isinstance(data, dict) else json.loads(data)
        return self._post(f"/workflows/{workflow_id}/run", payload=payload)

    # ── STATISTIQUES ───────────────────────────

    def get_stats(self, workflow_id, days=7):
        """Calcule les statistiques d'exécution d'un workflow."""
        executions = self.list_executions(workflow_id=workflow_id, limit=200)
        cutoff = datetime.utcnow() - timedelta(days=days)

        recent = []
        for ex in executions:
            started = ex.get("startedAt", "")
            if started:
                try:
                    dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                    dt = dt.replace(tzinfo=None)
                    if dt >= cutoff:
                        recent.append(ex)
                except ValueError:
                    pass

        total = len(recent)
        success = sum(1 for ex in recent if ex.get("status") == "success")
        failed = sum(1 for ex in recent if ex.get("status") == "error")
        waiting = sum(1 for ex in recent if ex.get("status") == "waiting")

        return {
            "workflow_id": workflow_id,
            "period_days": days,
            "total_executions": total,
            "success": success,
            "failed": failed,
            "waiting": waiting,
            "success_rate": round((success / total * 100), 1) if total > 0 else 0,
        }


# ─────────────────────────────────────────────
# AFFICHAGE
# ─────────────────────────────────────────────

def display(data, pretty=False):
    """Affiche les données en JSON."""
    if pretty:
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    else:
        print(json.dumps(data, ensure_ascii=False, default=str))


def display_workflows_table(workflows):
    """Affiche les workflows sous forme de tableau lisible."""
    if not workflows:
        print("Aucun workflow trouvé.")
        return
    print(f"\n{'ID':<30} {'NOM':<40} {'ACTIF':<8} {'CRÉÉ LE'}")
    print("─" * 90)
    for wf in workflows:
        wf_id = wf.get("id", "—")[:28]
        name = wf.get("name", "—")[:38]
        active = "✅ Oui" if wf.get("active") else "❌ Non"
        created = wf.get("createdAt", "—")[:10]
        print(f"{wf_id:<30} {name:<40} {active:<8} {created}")
    print(f"\nTotal : {len(workflows)} workflow(s)\n")


def display_executions_table(executions):
    """Affiche les exécutions sous forme de tableau lisible."""
    if not executions:
        print("Aucune exécution trouvée.")
        return
    print(f"\n{'ID':<30} {'STATUT':<12} {'WORKFLOW ID':<30} {'DÉMARRÉ LE'}")
    print("─" * 90)
    for ex in executions:
        ex_id = str(ex.get("id", "—"))[:28]
        status = ex.get("status", "—")
        status_icon = "✅" if status == "success" else "❌" if status == "error" else "⏳"
        wf_id = str(ex.get("workflowId", "—"))[:28]
        started = ex.get("startedAt", "—")[:19]
        print(f"{ex_id:<30} {status_icon} {status:<10} {wf_id:<30} {started}")
    print(f"\nTotal : {len(executions)} exécution(s)\n")


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def build_parser():
    parser = argparse.ArgumentParser(
        prog="n8n_api.py",
        description="Client CLI pour piloter n8n depuis un agent Paperclip — Dr. FIRAS",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list-workflows
    p = subparsers.add_parser("list-workflows", help="Lister les workflows")
    p.add_argument("--active", choices=["true", "false"], help="Filtrer par statut actif")
    p.add_argument("--pretty", action="store_true", help="Affichage formaté")

    # get-workflow
    p = subparsers.add_parser("get-workflow", help="Détails d'un workflow")
    p.add_argument("--id", required=True, help="ID du workflow")
    p.add_argument("--pretty", action="store_true")

    # create
    p = subparsers.add_parser("create", help="Créer un workflow depuis un fichier JSON")
    p.add_argument("--from-file", required=True, help="Chemin vers le fichier JSON")

    # activate
    p = subparsers.add_parser("activate", help="Activer un workflow")
    p.add_argument("--id", required=True, help="ID du workflow")

    # deactivate
    p = subparsers.add_parser("deactivate", help="Désactiver un workflow")
    p.add_argument("--id", required=True, help="ID du workflow")

    # execute
    p = subparsers.add_parser("execute", help="Déclencher un workflow manuellement")
    p.add_argument("--id", required=True, help="ID du workflow")
    p.add_argument("--data", help="Données JSON à envoyer (ex: '{\"cle\": \"valeur\"}')")

    # list-executions
    p = subparsers.add_parser("list-executions", help="Lister les exécutions récentes")
    p.add_argument("--id", help="Filtrer par ID de workflow")
    p.add_argument("--limit", type=int, default=10, help="Nombre de résultats (défaut: 10)")
    p.add_argument("--pretty", action="store_true")

    # get-execution
    p = subparsers.add_parser("get-execution", help="Détails d'une exécution")
    p.add_argument("--id", required=True, help="ID de l'exécution")
    p.add_argument("--pretty", action="store_true")

    # stats
    p = subparsers.add_parser("stats", help="Statistiques d'un workflow")
    p.add_argument("--id", required=True, help="ID du workflow")
    p.add_argument("--days", type=int, default=7, help="Période en jours (défaut: 7)")
    p.add_argument("--pretty", action="store_true")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    client = N8nClient()

    if args.command == "list-workflows":
        active = None
        if args.active == "true":
            active = True
        elif args.active == "false":
            active = False
        workflows = client.list_workflows(active=active)
        if args.pretty:
            display_workflows_table(workflows)
        else:
            display(workflows)

    elif args.command == "get-workflow":
        result = client.get_workflow(args.id)
        display(result, pretty=args.pretty)

    elif args.command == "create":
        with open(args.from_file, "r", encoding="utf-8") as f:
            workflow_data = json.load(f)
        result = client.create_workflow(workflow_data)
        print(f"✅ Workflow créé avec l'ID : {result.get('id')}")

    elif args.command == "activate":
        client.activate_workflow(args.id)
        print(f"✅ Workflow {args.id} activé.")

    elif args.command == "deactivate":
        client.deactivate_workflow(args.id)
        print(f"✅ Workflow {args.id} désactivé.")

    elif args.command == "execute":
        data = None
        if args.data:
            data = json.loads(args.data)
        result = client.execute_workflow(args.id, data=data)
        print(f"✅ Exécution déclenchée :")
        display(result, pretty=True)

    elif args.command == "list-executions":
        executions = client.list_executions(
            workflow_id=args.id,
            limit=args.limit
        )
        if args.pretty:
            display_executions_table(executions)
        else:
            display(executions)

    elif args.command == "get-execution":
        result = client.get_execution(args.id)
        display(result, pretty=args.pretty)

    elif args.command == "stats":
        result = client.get_stats(args.id, days=args.days)
        display(result, pretty=args.pretty)


if __name__ == "__main__":
    main()

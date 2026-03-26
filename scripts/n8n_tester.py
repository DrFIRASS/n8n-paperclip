#!/usr/bin/env python3
"""
n8n Workflow Tester — Skill Paperclip
Auteur : Dr. FIRAS — Formation IA & Automatisation
Description : Validation de structure, tests à sec et suites de tests
              pour les workflows n8n. Conçu pour Paperclip AI.
"""

import os
import sys
import json
import argparse
from datetime import datetime

# Import du client API
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from n8n_api import N8nClient
except ImportError:
    print("Erreur : impossible d'importer n8n_api.py.")
    print("Vérifie que les deux fichiers sont dans le même dossier scripts/.")
    sys.exit(1)


# ─────────────────────────────────────────────
# VALIDATEUR DE STRUCTURE
# ─────────────────────────────────────────────

class WorkflowValidator:
    """Valide la structure d'un workflow n8n."""

    # Types de nœuds considérés comme déclencheurs
    TRIGGER_TYPES = {
        "n8n-nodes-base.manualTrigger",
        "n8n-nodes-base.scheduleTrigger",
        "n8n-nodes-base.webhookTrigger",
        "n8n-nodes-base.webhook",
        "n8n-nodes-base.cron",
        "n8n-nodes-base.emailTrigger",
        "n8n-nodes-base.httpTrigger",
    }

    # Nœuds qui nécessitent des credentials
    CREDENTIAL_NODES = {
        "n8n-nodes-base.gmail",
        "n8n-nodes-base.slack",
        "n8n-nodes-base.notion",
        "n8n-nodes-base.airtable",
        "n8n-nodes-base.googleSheets",
        "n8n-nodes-base.postgres",
        "n8n-nodes-base.mysql",
        "n8n-nodes-base.openAi",
    }

    def validate(self, workflow):
        """
        Valide un workflow et retourne un rapport structuré.
        Retourne : dict avec 'valid', 'errors', 'warnings', 'infos'
        """
        errors = []
        warnings = []
        infos = []

        nodes = workflow.get("nodes", [])
        connections = workflow.get("connections", {})

        # ── Vérifications de base ──────────────────
        if not nodes:
            errors.append("Le workflow ne contient aucun nœud.")
            return self._build_report(errors, warnings, infos)

        if not isinstance(nodes, list):
            errors.append("Le champ 'nodes' doit être une liste.")
            return self._build_report(errors, warnings, infos)

        # ── Analyse des nœuds ─────────────────────
        node_names = set()
        has_trigger = False

        for i, node in enumerate(nodes):
            node_name = node.get("name", f"Nœud #{i+1}")
            node_type = node.get("type", "")

            # Champs obligatoires
            if not node.get("name"):
                errors.append(f"Nœud #{i+1} : champ 'name' manquant.")
            if not node_type:
                errors.append(f"Nœud '{node_name}' : champ 'type' manquant.")

            # Doublons de noms
            if node_name in node_names:
                errors.append(f"Nœud en doublon : '{node_name}'. Chaque nœud doit avoir un nom unique.")
            node_names.add(node_name)

            # Détection du déclencheur
            if node_type in self.TRIGGER_TYPES:
                has_trigger = True

            # Nœuds avec credentials
            if node_type in self.CREDENTIAL_NODES:
                creds = node.get("credentials", {})
                if not creds:
                    warnings.append(
                        f"Nœud '{node_name}' ({node_type}) : aucun credential configuré."
                    )

            # Nœuds HTTP sans URL
            if "httpRequest" in node_type:
                params = node.get("parameters", {})
                if not params.get("url"):
                    warnings.append(f"Nœud '{node_name}' : URL manquante sur le nœud HTTP Request.")

            # Nœuds Webhook sans chemin
            if "webhook" in node_type.lower():
                params = node.get("parameters", {})
                if not params.get("path"):
                    warnings.append(f"Nœud '{node_name}' : chemin (path) manquant sur le nœud Webhook.")

        # ── Vérification du déclencheur ───────────
        if not has_trigger:
            errors.append(
                "Aucun nœud déclencheur trouvé. "
                "Ajoute un nœud de type Trigger (Manuel, Schedule, Webhook, etc.)."
            )

        # ── Vérification des connexions ───────────
        if not connections:
            warnings.append("Aucune connexion définie entre les nœuds.")
        else:
            for source_name, outputs in connections.items():
                if source_name not in node_names:
                    errors.append(
                        f"Connexion invalide : le nœud source '{source_name}' n'existe pas."
                    )
                for output_list in outputs.values():
                    for targets in output_list:
                        for target in targets:
                            target_name = target.get("node", "")
                            if target_name and target_name not in node_names:
                                errors.append(
                                    f"Connexion invalide : le nœud cible '{target_name}' n'existe pas."
                                )

        # ── Nœuds déconnectés ─────────────────────
        connected_nodes = set(connections.keys())
        for node in nodes:
            name = node.get("name", "")
            node_type = node.get("type", "")
            if name and name not in connected_nodes and node_type not in self.TRIGGER_TYPES:
                warnings.append(f"Nœud '{name}' semble déconnecté du flux principal.")

        # ── Infos générales ───────────────────────
        infos.append(f"Nombre de nœuds : {len(nodes)}")
        infos.append(f"Nombre de connexions : {len(connections)}")
        infos.append(f"Déclencheur détecté : {'✅ Oui' if has_trigger else '❌ Non'}")

        return self._build_report(errors, warnings, infos)

    def _build_report(self, errors, warnings, infos):
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "infos": infos,
            "summary": {
                "error_count": len(errors),
                "warning_count": len(warnings),
            }
        }


# ─────────────────────────────────────────────
# TESTEUR DE WORKFLOWS
# ─────────────────────────────────────────────

class WorkflowTester:
    """Tests à sec et suites de tests pour les workflows n8n."""

    def __init__(self, client=None):
        self.client = client or N8nClient()
        self.validator = WorkflowValidator()

    def validate_workflow(self, workflow_id=None, workflow_data=None):
        """Valide un workflow par ID ou depuis un dict."""
        if workflow_id:
            workflow_data = self.client.get_workflow(workflow_id)
        if not workflow_data:
            return {"valid": False, "errors": ["Workflow introuvable."], "warnings": [], "infos": []}
        return self.validator.validate(workflow_data)

    def dry_run(self, workflow_id, test_data=None, report=False):
        """
        Simule l'exécution d'un workflow avec des données de test.
        Ne modifie pas les données réelles.
        """
        # Validation avant le test
        validation = self.validate_workflow(workflow_id=workflow_id)

        if not validation["valid"]:
            return {
                "status": "validation_failed",
                "message": "Le workflow contient des erreurs bloquantes. Corrige-les avant de tester.",
                "validation": validation,
            }

        # Lancement de l'exécution de test
        try:
            result = self.client.execute_workflow(workflow_id, data=test_data)
            execution_id = result.get("executionId") or result.get("id")

            outcome = {
                "status": "triggered",
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "test_data_used": test_data or {},
                "triggered_at": datetime.utcnow().isoformat(),
                "validation": validation,
            }

            if report:
                outcome["report"] = self._format_dry_run_report(outcome, validation)

            return outcome

        except SystemExit:
            return {
                "status": "error",
                "message": "Impossible de déclencher le workflow. Vérifie qu'il est activé.",
                "workflow_id": workflow_id,
            }

    def test_suite(self, workflow_id, test_cases):
        """
        Lance plusieurs cas de test sur un même workflow.

        test_cases : liste de dicts avec les clés 'name' et 'input'
        Exemple :
        [
            {"name": "Email valide", "input": {"email": "test@exemple.com"}},
            {"name": "Sans email",   "input": {}},
        ]
        """
        results = []
        passed = 0
        failed = 0

        print(f"\n🧪 Suite de tests — Workflow {workflow_id}")
        print(f"   {len(test_cases)} cas de test à exécuter\n")

        for i, case in enumerate(test_cases, start=1):
            name = case.get("name", f"Cas #{i}")
            input_data = case.get("input", {})

            print(f"  [{i}/{len(test_cases)}] {name} ... ", end="", flush=True)

            result = self.dry_run(workflow_id, test_data=input_data)
            status = result.get("status", "error")

            if status == "triggered":
                passed += 1
                print("✅ OK")
            else:
                failed += 1
                print(f"❌ ÉCHEC — {result.get('message', 'Erreur inconnue')}")

            results.append({
                "case_name": name,
                "input": input_data,
                "status": status,
                "execution_id": result.get("execution_id"),
            })

        print(f"\n📊 Résultats : {passed} réussi(s) / {failed} échoué(s) / {len(test_cases)} total\n")

        return {
            "workflow_id": workflow_id,
            "total_tests": len(test_cases),
            "passed": passed,
            "failed": failed,
            "success_rate": round((passed / len(test_cases) * 100), 1) if test_cases else 0,
            "results": results,
        }

    def _format_dry_run_report(self, outcome, validation):
        """Génère un rapport lisible du test à sec."""
        lines = [
            "═" * 60,
            "  RAPPORT DE TEST — Dr. FIRAS n8n Skill Paperclip",
            "═" * 60,
            f"  Workflow ID    : {outcome.get('workflow_id')}",
            f"  Déclenché le   : {outcome.get('triggered_at')}",
            f"  Exécution ID   : {outcome.get('execution_id', 'N/A')}",
            f"  Statut         : {outcome.get('status')}",
            "",
            "── Validation ──────────────────────────────────────",
            f"  Résultat       : {'✅ Valide' if validation['valid'] else '❌ Invalide'}",
            f"  Erreurs        : {validation['summary']['error_count']}",
            f"  Avertissements : {validation['summary']['warning_count']}",
        ]

        if validation["errors"]:
            lines.append("")
            lines.append("  ❌ Erreurs :")
            for err in validation["errors"]:
                lines.append(f"     • {err}")

        if validation["warnings"]:
            lines.append("")
            lines.append("  ⚠️  Avertissements :")
            for warn in validation["warnings"]:
                lines.append(f"     • {warn}")

        lines += ["", "── Données de test ─────────────────────────────────"]
        test_data = outcome.get("test_data_used", {})
        if test_data:
            for k, v in test_data.items():
                lines.append(f"     {k} : {v}")
        else:
            lines.append("     (aucune donnée de test fournie)")

        lines += ["", "═" * 60]
        return "\n".join(lines)


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def build_parser():
    parser = argparse.ArgumentParser(
        prog="n8n_tester.py",
        description="Validation et tests de workflows n8n — Dr. FIRAS / Paperclip AI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # validate
    p = subparsers.add_parser("validate", help="Valider la structure d'un workflow")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--id", help="ID du workflow (récupéré depuis n8n)")
    group.add_argument("--file", help="Chemin vers un fichier workflow.json local")
    p.add_argument("--pretty", action="store_true", help="Affichage formaté")

    # dry-run
    p = subparsers.add_parser("dry-run", help="Tester un workflow avec des données")
    p.add_argument("--id", required=True, help="ID du workflow")
    p.add_argument("--data", help="Données JSON inline ex: '{\"email\": \"test@ex.com\"}'")
    p.add_argument("--data-file", help="Chemin vers un fichier JSON de données de test")
    p.add_argument("--report", action="store_true", help="Afficher un rapport détaillé")

    # report
    p = subparsers.add_parser("report", help="Rapport complet de validation")
    p.add_argument("--id", required=True, help="ID du workflow")

    # test-suite
    p = subparsers.add_parser("test-suite", help="Suite de tests depuis un fichier JSON")
    p.add_argument("--id", required=True, help="ID du workflow")
    p.add_argument("--test-suite", required=True, help="Chemin vers le fichier de cas de test")

    return parser


def print_validation_report(result):
    """Affiche un rapport de validation lisible."""
    status = "✅ VALIDE" if result["valid"] else "❌ INVALIDE"
    print(f"\n{'═'*55}")
    print(f"  VALIDATION — {status}")
    print(f"{'═'*55}")
    print(f"  Erreurs        : {result['summary']['error_count']}")
    print(f"  Avertissements : {result['summary']['warning_count']}")

    if result["infos"]:
        print("\n── Informations ──────────────────────────────────")
        for info in result["infos"]:
            print(f"   ℹ️  {info}")

    if result["errors"]:
        print("\n── Erreurs bloquantes ────────────────────────────")
        for err in result["errors"]:
            print(f"   ❌ {err}")

    if result["warnings"]:
        print("\n── Avertissements ────────────────────────────────")
        for warn in result["warnings"]:
            print(f"   ⚠️  {warn}")

    print(f"{'═'*55}\n")


def main():
    parser = build_parser()
    args = parser.parse_args()
    client = N8nClient()
    tester = WorkflowTester(client=client)

    if args.command == "validate":
        if args.id:
            result = tester.validate_workflow(workflow_id=args.id)
        else:
            with open(args.file, "r", encoding="utf-8") as f:
                workflow_data = json.load(f)
            result = tester.validate_workflow(workflow_data=workflow_data)

        if args.pretty:
            print_validation_report(result)
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "dry-run":
        test_data = None
        if args.data:
            test_data = json.loads(args.data)
        elif args.data_file:
            with open(args.data_file, "r", encoding="utf-8") as f:
                test_data = json.load(f)

        result = tester.dry_run(args.id, test_data=test_data, report=args.report)

        if args.report and "report" in result:
            print(result["report"])
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    elif args.command == "report":
        validation = tester.validate_workflow(workflow_id=args.id)
        print_validation_report(validation)

    elif args.command == "test-suite":
        with open(args.test_suite, "r", encoding="utf-8") as f:
            test_cases = json.load(f)
        result = tester.test_suite(args.id, test_cases)
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()

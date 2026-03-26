#!/usr/bin/env python3
"""
n8n Workflow Optimizer — Skill Paperclip
Auteur : Dr. FIRAS — Formation IA & Automatisation
Description : Analyse de performance, détection de goulots d'étranglement
              et recommandations d'optimisation pour les workflows n8n.
              Conçu exclusivement pour Paperclip AI.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta

# Import du client API
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from n8n_api import N8nClient
except ImportError:
    print("Erreur : impossible d'importer n8n_api.py.")
    print("Vérifie que les deux fichiers sont dans le même dossier scripts/.")
    sys.exit(1)


# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────

# Nœuds considérés comme coûteux (API externe, BDD, IA)
EXPENSIVE_NODE_TYPES = {
    "n8n-nodes-base.httpRequest",
    "n8n-nodes-base.openAi",
    "n8n-nodes-base.postgres",
    "n8n-nodes-base.mysql",
    "n8n-nodes-base.googleSheets",
    "n8n-nodes-base.gmail",
    "n8n-nodes-base.slack",
    "n8n-nodes-base.notion",
    "n8n-nodes-base.airtable",
    "n8n-nodes-base.stripe",
    "n8n-nodes-base.sendGrid",
}

# Seuils de complexité
SEUIL_NOEUDS_ELEVE = 15
SEUIL_NOEUDS_CRITIQUE = 30
SEUIL_OPERATIONS_COUTEUSES = 5


# ─────────────────────────────────────────────
# ANALYSEUR DE PERFORMANCE
# ─────────────────────────────────────────────

class WorkflowOptimizer:
    """Analyse les performances et génère des recommandations pour les workflows n8n."""

    def __init__(self, client=None):
        self.client = client or N8nClient()

    # ── ANALYSE PRINCIPALE ─────────────────────

    def analyze(self, workflow_id, days=7):
        """
        Analyse complète d'un workflow : métriques d'exécution,
        complexité, goulots d'étranglement et score de performance.
        """
        workflow = self.client.get_workflow(workflow_id)
        stats = self.client.get_stats(workflow_id, days=days)
        executions = self.client.list_executions(workflow_id=workflow_id, limit=100)

        metriques = self._calculer_metriques(stats, executions)
        complexite = self._analyser_complexite(workflow)
        goulots = self._detecter_goulots(workflow, metriques)
        score = self._calculer_score(metriques, complexite, goulots)

        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow.get("name", "Inconnu"),
            "periode_analyse_jours": days,
            "score_performance": score,
            "niveau": self._niveau_score(score),
            "metriques_execution": metriques,
            "analyse_complexite": complexite,
            "goulots_detectes": goulots,
            "genere_le": datetime.utcnow().isoformat(),
        }

    def suggest(self, workflow_id):
        """
        Génère des recommandations d'optimisation classées par priorité.
        Retourne : actions prioritaires, gains rapides, améliorations long terme.
        """
        analyse = self.analyze(workflow_id)
        workflow = self.client.get_workflow(workflow_id)

        actions_prioritaires = []
        gains_rapides = []
        ameliorations_long_terme = []

        metriques = analyse["metriques_execution"]
        complexite = analyse["analyse_complexite"]
        goulots = analyse["goulots_detectes"]
        score = analyse["score_performance"]

        # ── Taux de succès faible ──────────────────
        if metriques["taux_succes"] < 70:
            actions_prioritaires.append({
                "priorite": "CRITIQUE",
                "titre": "Taux de succès très bas",
                "detail": f"Seulement {metriques['taux_succes']}% de succès sur {metriques['total_executions']} exécutions.",
                "action": "Inspecte les exécutions échouées avec : python3 scripts/n8n_api.py list-executions --id <id> --pretty",
            })
        elif metriques["taux_succes"] < 90:
            gains_rapides.append({
                "priorite": "HAUTE",
                "titre": "Taux de succès à améliorer",
                "detail": f"{metriques['taux_succes']}% de succès. Vise 95%+.",
                "action": "Ajoute des nœuds de gestion d'erreur (Error Trigger) dans le workflow.",
            })

        # ── Trop de nœuds coûteux séquentiels ─────
        nb_couteux = complexite.get("noeuds_couteux", 0)
        if nb_couteux >= SEUIL_OPERATIONS_COUTEUSES:
            actions_prioritaires.append({
                "priorite": "HAUTE",
                "titre": "Trop d'opérations API séquentielles",
                "detail": f"{nb_couteux} nœuds coûteux détectés (API, BDD, IA).",
                "action": "Regroupe les appels API similaires ou utilise des nœuds Batch/Split.",
            })

        # ── Workflow trop complexe ─────────────────
        nb_noeuds = complexite.get("nombre_noeuds", 0)
        if nb_noeuds > SEUIL_NOEUDS_CRITIQUE:
            actions_prioritaires.append({
                "priorite": "HAUTE",
                "titre": "Workflow trop volumineux",
                "detail": f"{nb_noeuds} nœuds dans un seul workflow.",
                "action": "Découpe en sous-workflows avec le nœud Execute Workflow.",
            })
        elif nb_noeuds > SEUIL_NOEUDS_ELEVE:
            gains_rapides.append({
                "priorite": "MOYENNE",
                "titre": "Workflow complexe",
                "detail": f"{nb_noeuds} nœuds détectés.",
                "action": "Envisage de séparer en modules indépendants pour faciliter la maintenance.",
            })

        # ── Goulots d'étranglement ─────────────────
        for goulot in goulots:
            if goulot["severite"] == "critique":
                actions_prioritaires.append({
                    "priorite": "CRITIQUE",
                    "titre": goulot["type"],
                    "detail": goulot["detail"],
                    "action": goulot["solution"],
                })
            elif goulot["severite"] == "haute":
                gains_rapides.append({
                    "priorite": "HAUTE",
                    "titre": goulot["type"],
                    "detail": goulot["detail"],
                    "action": goulot["solution"],
                })

        # ── Bonnes pratiques long terme ────────────
        ameliorations_long_terme.append({
            "titre": "Surveillance hebdomadaire",
            "detail": "Analyse les performances chaque semaine.",
            "action": "Planifie : python3 scripts/n8n_optimizer.py report --id <id>",
        })
        ameliorations_long_terme.append({
            "titre": "Rotation des credentials",
            "detail": "Renouvelle les clés API utilisées dans ce workflow régulièrement.",
            "action": "Mets à jour les credentials dans n8n (Settings → Credentials).",
        })

        if not complexite.get("a_gestion_erreur"):
            ameliorations_long_terme.append({
                "titre": "Ajouter une gestion d'erreur",
                "detail": "Aucun nœud Error Trigger détecté dans ce workflow.",
                "action": "Ajoute un nœud 'Error Trigger' pour capturer les pannes silencieuses.",
            })

        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow.get("name", "Inconnu"),
            "score_actuel": score,
            "niveau_actuel": self._niveau_score(score),
            "actions_prioritaires": actions_prioritaires,
            "gains_rapides": gains_rapides,
            "ameliorations_long_terme": ameliorations_long_terme,
            "total_recommandations": (
                len(actions_prioritaires) + len(gains_rapides) + len(ameliorations_long_terme)
            ),
        }

    # ── CALCUL DES MÉTRIQUES ───────────────────

    def _calculer_metriques(self, stats, executions):
        """Calcule les métriques d'exécution à partir des stats et du détail des exécutions."""
        taux_succes = stats.get("success_rate", 0)
        total = stats.get("total_executions", 0)
        succes = stats.get("success", 0)
        echecs = stats.get("failed", 0)

        # Sante globale
        if taux_succes >= 95:
            sante = "excellent"
        elif taux_succes >= 80:
            sante = "bon"
        elif taux_succes >= 60:
            sante = "moyen"
        else:
            sante = "faible"

        # Patterns d'erreur
        patterns_erreur = {}
        for ex in executions:
            if ex.get("status") == "error":
                # Simplification : on groupe par heure
                started = ex.get("startedAt", "")[:13]
                patterns_erreur[started] = patterns_erreur.get(started, 0) + 1

        heure_pic_erreur = None
        if patterns_erreur:
            heure_pic_erreur = max(patterns_erreur, key=patterns_erreur.get)

        return {
            "total_executions": total,
            "succes": succes,
            "echecs": echecs,
            "taux_succes": taux_succes,
            "sante": sante,
            "heure_pic_erreur": heure_pic_erreur,
        }

    def _analyser_complexite(self, workflow):
        """Analyse la complexité structurelle du workflow."""
        nodes = workflow.get("nodes", [])
        connections = workflow.get("connections", {})

        nb_noeuds = len(nodes)
        nb_connexions = len(connections)

        noeuds_couteux = sum(
            1 for n in nodes if n.get("type", "") in EXPENSIVE_NODE_TYPES
        )

        # Détection de la gestion d'erreur
        a_gestion_erreur = any(
            "error" in n.get("type", "").lower() for n in nodes
        )

        # Détection des nœuds parallèles (une source vers plusieurs cibles)
        noeuds_paralleles = 0
        for source, outputs in connections.items():
            for output_list in outputs.values():
                if len(output_list) > 1:
                    noeuds_paralleles += 1

        # Niveau de complexité
        if nb_noeuds <= 5:
            niveau = "simple"
        elif nb_noeuds <= 15:
            niveau = "modéré"
        elif nb_noeuds <= 30:
            niveau = "complexe"
        else:
            niveau = "très complexe"

        return {
            "nombre_noeuds": nb_noeuds,
            "nombre_connexions": nb_connexions,
            "noeuds_couteux": noeuds_couteux,
            "noeuds_paralleles": noeuds_paralleles,
            "a_gestion_erreur": a_gestion_erreur,
            "niveau_complexite": niveau,
        }

    def _detecter_goulots(self, workflow, metriques):
        """Détecte les goulots d'étranglement dans le workflow."""
        goulots = []
        nodes = workflow.get("nodes", [])
        connections = workflow.get("connections", {})

        # ── Appels API séquentiels ─────────────────
        noms_couteux = [
            n.get("name") for n in nodes
            if n.get("type", "") in EXPENSIVE_NODE_TYPES
        ]

        # Vérifie si les nœuds coûteux sont en série
        if len(noms_couteux) >= 3:
            serie = True
            for i, nom in enumerate(noms_couteux[:-1]):
                next_nom = noms_couteux[i + 1]
                # Vérification simplifiée : les deux sont dans les connexions
                if nom not in connections:
                    serie = False
                    break
            if serie:
                goulots.append({
                    "type": "Appels API en séquence",
                    "severite": "haute",
                    "detail": f"{len(noms_couteux)} nœuds coûteux s'exécutent l'un après l'autre.",
                    "solution": "Utilise le nœud Split In Batches ou parallélise via plusieurs branches.",
                    "noeuds_concernes": noms_couteux,
                })

        # ── Taux d'échec élevé ─────────────────────
        if metriques["taux_succes"] < 60:
            goulots.append({
                "type": "Taux d'échec critique",
                "severite": "critique",
                "detail": f"Moins de 60% de succès ({metriques['taux_succes']}%).",
                "solution": "Examine les dernières exécutions échouées et ajoute un nœud Error Trigger.",
                "noeuds_concernes": [],
            })

        # ── Absence de gestion d'erreur ────────────
        a_gestion_erreur = any(
            "error" in n.get("type", "").lower() for n in nodes
        )
        if not a_gestion_erreur and metriques["total_executions"] > 10:
            goulots.append({
                "type": "Absence de gestion d'erreur",
                "severite": "moyenne",
                "detail": "Aucun nœud Error Trigger dans le workflow.",
                "solution": "Ajoute un nœud Error Trigger connecté à une notification (Slack, Email).",
                "noeuds_concernes": [],
            })

        # ── Workflow sans branche de sortie ───────
        noeuds_sans_sortie = []
        for node in nodes:
            nom = node.get("name", "")
            node_type = node.get("type", "")
            if nom and nom not in connections and "trigger" not in node_type.lower():
                noeuds_sans_sortie.append(nom)

        if len(noeuds_sans_sortie) > 2:
            goulots.append({
                "type": "Nœuds terminaux multiples",
                "severite": "faible",
                "detail": f"{len(noeuds_sans_sortie)} nœuds sans connexion de sortie.",
                "solution": "Vérifie que tous les flux se terminent correctement et de façon intentionnelle.",
                "noeuds_concernes": noeuds_sans_sortie,
            })

        return goulots

    def _calculer_score(self, metriques, complexite, goulots):
        """Calcule le score de performance global (0-100)."""
        score = 100

        # Pénalité taux de succès (poids : 50%)
        taux = metriques["taux_succes"]
        if taux < 95:
            score -= (95 - taux) * 0.5

        # Pénalité complexité (poids : 30%)
        nb_noeuds = complexite["nombre_noeuds"]
        if nb_noeuds > SEUIL_NOEUDS_CRITIQUE:
            score -= 20
        elif nb_noeuds > SEUIL_NOEUDS_ELEVE:
            score -= 10

        # Pénalité goulots
        for g in goulots:
            severite = g.get("severite", "")
            if severite == "critique":
                score -= 20
            elif severite == "haute":
                score -= 10
            elif severite == "moyenne":
                score -= 5
            elif severite == "faible":
                score -= 2

        # Bonus bonnes pratiques
        if complexite.get("a_gestion_erreur"):
            score += 5
        if complexite.get("noeuds_paralleles", 0) > 0:
            score += 3

        return max(0, min(100, round(score)))

    def _niveau_score(self, score):
        """Retourne l'interprétation textuelle du score."""
        if score >= 90:
            return "🟢 Excellent"
        elif score >= 70:
            return "🟡 Bon"
        elif score >= 50:
            return "🟠 Moyen"
        else:
            return "🔴 Faible"

    # ── RAPPORT COMPLET ────────────────────────

    def generate_report(self, workflow_id, days=7):
        """Génère un rapport complet lisible en texte."""
        analyse = self.analyze(workflow_id, days=days)
        suggestions = self.suggest(workflow_id)

        lignes = [
            "",
            "╔" + "═" * 58 + "╗",
            "║   RAPPORT D'OPTIMISATION — Dr. FIRAS n8n Paperclip    ║",
            "╚" + "═" * 58 + "╝",
            f"  Workflow   : {analyse['workflow_name']}",
            f"  ID         : {analyse['workflow_id']}",
            f"  Période    : {analyse['periode_analyse_jours']} derniers jours",
            f"  Généré le  : {analyse['genere_le'][:19]}",
            "",
            "── Score de performance ─────────────────────────────────",
            f"   {analyse['score_performance']} / 100  →  {analyse['niveau']}",
            "",
            "── Métriques d'exécution ────────────────────────────────",
        ]

        m = analyse["metriques_execution"]
        lignes += [
            f"   Exécutions totales : {m['total_executions']}",
            f"   Succès             : {m['succes']}",
            f"   Échecs             : {m['echecs']}",
            f"   Taux de succès     : {m['taux_succes']}%",
            f"   Santé globale      : {m['sante']}",
        ]

        c = analyse["analyse_complexite"]
        lignes += [
            "",
            "── Analyse de complexité ────────────────────────────────",
            f"   Nombre de nœuds    : {c['nombre_noeuds']} ({c['niveau_complexite']})",
            f"   Nœuds coûteux      : {c['noeuds_couteux']} (API, BDD, IA)",
            f"   Branches parallèles: {c['noeuds_paralleles']}",
            f"   Gestion d'erreur   : {'✅ Oui' if c['a_gestion_erreur'] else '❌ Non'}",
        ]

        goulots = analyse["goulots_detectes"]
        if goulots:
            lignes += [
                "",
                "── Goulots détectés ─────────────────────────────────────",
            ]
            for g in goulots:
                icone = "🔴" if g["severite"] == "critique" else "🟠" if g["severite"] == "haute" else "🟡"
                lignes.append(f"   {icone} {g['type']}")
                lignes.append(f"      → {g['detail']}")
                lignes.append(f"      💡 {g['solution']}")
        else:
            lignes += ["", "── Goulots détectés ─────────────────────────────────────",
                       "   ✅ Aucun goulot majeur détecté."]

        # Recommandations
        if suggestions["actions_prioritaires"]:
            lignes += ["", "── Actions prioritaires ─────────────────────────────────"]
            for rec in suggestions["actions_prioritaires"]:
                lignes.append(f"   🔴 [{rec['priorite']}] {rec['titre']}")
                lignes.append(f"      {rec['detail']}")
                lignes.append(f"      → {rec['action']}")

        if suggestions["gains_rapides"]:
            lignes += ["", "── Gains rapides ────────────────────────────────────────"]
            for rec in suggestions["gains_rapides"]:
                lignes.append(f"   🟠 {rec['titre']}")
                lignes.append(f"      {rec['detail']}")
                lignes.append(f"      → {rec['action']}")

        if suggestions["ameliorations_long_terme"]:
            lignes += ["", "── Améliorations long terme ─────────────────────────────"]
            for rec in suggestions["ameliorations_long_terme"]:
                lignes.append(f"   🔵 {rec['titre']}")
                lignes.append(f"      → {rec['action']}")

        lignes += [
            "",
            "╔" + "═" * 58 + "╗",
            "║   Skill n8n-paperclip — Dr. FIRAS / Paperclip AI       ║",
            "╚" + "═" * 58 + "╝",
            "",
        ]

        return "\n".join(lignes)


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def build_parser():
    parser = argparse.ArgumentParser(
        prog="n8n_optimizer.py",
        description="Optimisation et analyse de performance des workflows n8n — Dr. FIRAS",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # analyze
    p = subparsers.add_parser("analyze", help="Analyser les performances d'un workflow")
    p.add_argument("--id", required=True, help="ID du workflow")
    p.add_argument("--days", type=int, default=7, help="Période d'analyse en jours (défaut: 7)")
    p.add_argument("--pretty", action="store_true", help="Affichage JSON indenté")

    # suggest
    p = subparsers.add_parser("suggest", help="Recommandations d'optimisation")
    p.add_argument("--id", required=True, help="ID du workflow")
    p.add_argument("--pretty", action="store_true")

    # report
    p = subparsers.add_parser("report", help="Rapport complet lisible")
    p.add_argument("--id", required=True, help="ID du workflow")
    p.add_argument("--days", type=int, default=7, help="Période d'analyse en jours")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    client = N8nClient()
    optimizer = WorkflowOptimizer(client=client)

    if args.command == "analyze":
        result = optimizer.analyze(args.id, days=args.days)
        print(json.dumps(result, indent=2 if args.pretty else None,
                         ensure_ascii=False, default=str))

    elif args.command == "suggest":
        result = optimizer.suggest(args.id)
        if args.pretty:
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        else:
            # Affichage lisible
            print(f"\n🎯 Recommandations pour : {result['workflow_name']}")
            print(f"   Score actuel : {result['score_actuel']} — {result['niveau_actuel']}")
            print(f"   Total recommandations : {result['total_recommandations']}\n")
            if result["actions_prioritaires"]:
                print("🔴 Actions prioritaires :")
                for r in result["actions_prioritaires"]:
                    print(f"   • {r['titre']} : {r['action']}")
            if result["gains_rapides"]:
                print("\n🟠 Gains rapides :")
                for r in result["gains_rapides"]:
                    print(f"   • {r['titre']} : {r['action']}")
            if result["ameliorations_long_terme"]:
                print("\n🔵 Long terme :")
                for r in result["ameliorations_long_terme"]:
                    print(f"   • {r['titre']} : {r['action']}")

    elif args.command == "report":
        report = optimizer.generate_report(args.id, days=args.days)
        print(report)


if __name__ == "__main__":
    main()

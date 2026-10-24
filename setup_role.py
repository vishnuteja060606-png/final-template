#!/usr/bin/env python3
"""
Synapse Marketplace — 5-Member Parallel Development Role Onboarding Script
Usage:
    python setup_role.py --role <1|2|3|4|5>
"""

import sys
import argparse
import subprocess
from pathlib import Path

ROLE_DEFINITIONS = {
    1: {
        "title": "Member 1: Platform Architect & Core Contracts Lead",
        "branch": "member-1/core-contracts",
        "playbook": "AGENT_ROLE_1_CORE.md",
        "target_files": [
            "app/db/database.py",
            "app/db/seed.py",
            "app/models/sidecar.py",
            "app/api/auth.py",
            "app/templates/base.html"
        ],
        "mission": (
            "Own the shared contracts, database migrations, role-based navbar security, "
            "authentication tokens, and overall orchestration."
        )
    },
    2: {
        "title": "Member 2: Creator Profiles, Portfolios & Connections Lead",
        "branch": "member-2/creator-portfolios",
        "playbook": "AGENT_ROLE_2_CREATOR.md",
        "target_files": [
            "app/models/creator.py",
            "app/models/portfolio.py",
            "app/models/connection.py",
            "app/services/creator_service.py",
            "app/services/connection_service.py",
            "app/api/creators.py",
            "app/api/connections.py",
            "app/templates/creators/detail.html",
            "app/templates/dashboard/creator.html"
        ],
        "mission": (
            "Implement distinct creator profile structure, AI specifications & tools cloud, "
            "mandatory 2 portfolio uploads rule (draft vs published), pinning best works (max 3), "
            "creator networking connections, and view tracking."
        )
    },
    3: {
        "title": "Member 3: Company Profiles, Reviews & Currency Lead",
        "branch": "member-3/company-reviews-currency",
        "playbook": "AGENT_ROLE_3_COMPANY.md",
        "target_files": [
            "app/models/company.py",
            "app/models/review.py",
            "app/services/company_service.py",
            "app/services/review_service.py",
            "app/api/companies.py",
            "app/api/reviews.py",
            "app/templates/companies/detail.html",
            "app/templates/dashboard/company.html",
            "app/static/js/main.js"
        ],
        "mission": (
            "Implement distinct company profile structure with logo, location & social links, "
            "company review & 1-5 star rating system for creators, and primary INR (₹) / optional USD ($) "
            "dynamic currency converter across the marketplace."
        )
    },
    4: {
        "title": "Member 4: Semantic Search & Canonical NER Engine",
        "branch": "member-4/semantic-search-ner",
        "playbook": "AGENT_ROLE_4_SEARCH_NER.md",
        "target_files": [
            "app/services/embedding_service.py",
            "app/services/ner_service.py",
            "app/services/hybrid_search_service.py",
            "app/api/advanced.py"
        ],
        "mission": (
            "Implement zero-cost FastEmbed (bge-small-en-v1.5) ONNX local vector embeddings, "
            "canonical dictionary & regex/LLM entity extraction for AI tools/aspect ratios, "
            "and Reciprocal Rank Fusion (RRF) for hybrid keyword+vector search."
        )
    },
    5: {
        "title": "Member 5: Ranking Engine (5x 20%), AI Brief Builder & UI Integration",
        "branch": "member-5/ranking-rag-ui",
        "playbook": "AGENT_ROLE_5_RANKING_UI.md",
        "target_files": [
            "app/services/ranking_service.py",
            "app/services/rag_service.py",
            "app/templates/ai/brief_builder.html",
            "app/templates/jobs/list.html",
            "app/templates/jobs/detail.html"
        ],
        "mission": (
            "Implement the 5-factor creator ranking algorithm with equal 20% weights "
            "(Semantic Match, Tools/Specs, Company Reviews, Verification, Views/Popularity), "
            "AI-assisted Brief Builder with grounded citations, and responsive UI polish."
        )
    }
}

def run_cmd(cmd: list[str]) -> bool:
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        return res.returncode == 0
    except Exception:
        return False

def setup_role(role_id: int):
    if role_id not in ROLE_DEFINITIONS:
        print(f"Error: Invalid role '{role_id}'. Please select a role between 1 and 5.")
        sys.exit(1)

    role_info = ROLE_DEFINITIONS[role_id]
    branch = role_info["branch"]

    print("=" * 70)
    print(f"  SYNAPSE MARKETPLACE — ONBOARDING: {role_info['title']}")
    print("=" * 70)
    print(f"\n🎯 MISSION:\n   {role_info['mission']}\n")
    print(f"📄 AGENT PLAYBOOK FILE:\n   {role_info['playbook']}\n")
    print("📁 YOUR ISOLATED TARGET FILES:")
    for f in role_info["target_files"]:
        print(f"   • {f}")

    print("\n🌿 CONFIGURING GIT BRANCH...")
    # Attempt to checkout or create branch
    if run_cmd(["git", "checkout", "-b", branch]):
        print(f"   ✓ Created and switched to new branch: '{branch}'")
    elif run_cmd(["git", "checkout", branch]):
        print(f"   ✓ Switched to existing branch: '{branch}'")
    else:
        print(f"   ℹ Git branch switch skipped (please ensure you are on '{branch}').")

    print("\n🤖 INSTRUCTIONS FOR YOUR ANTIGRAVITY AGENT:")
    print("   1. Open Antigravity and prompt your agent:")
    print(f"      'I am assigned to {role_info['title']}. Read {role_info['playbook']} and TEAM_CONTRACT.md, then implement my target files.'")
    print("   2. Run automated tests to verify your implementation:")
    print("      python -m pytest")
    print("=" * 70)
    print("Happy Hacking! Zero conflicts guaranteed by TEAM_CONTRACT.md.\n")

def main():
    parser = argparse.ArgumentParser(description="Onboard team members into isolated parallel development branches.")
    parser.add_argument("--role", type=int, choices=[1, 2, 3, 4, 5], help="Role number (1 to 5)")
    args = parser.parse_args()

    if args.role:
        setup_role(args.role)
    else:
        print("\nSelect your team member role:")
        for k, v in ROLE_DEFINITIONS.items():
            print(f"  [{k}] {v['title']}")
        try:
            choice = int(input("\nEnter role number (1-5): ").strip())
            setup_role(choice)
        except (ValueError, KeyboardInterrupt):
            print("\nAborted.")
            sys.exit(0)

if __name__ == "__main__":
    main()

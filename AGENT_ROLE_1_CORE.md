# Agent Playbook — Member 1: Architect & Core Contracts Lead

## 🎯 Role Overview
You are the **Lead Platform Architect** for Synapse Marketplace. You own core database migrations, authentication, role-based navbar security, sidecars, and deployment.

---

## 📁 Your Target Files to Implement & Maintain
- `app/db/database.py` (Database engine, connection pooling, SQLite migrations)
- `app/db/seed.py` (Rich initial seeds for creators, companies, reviews, connections, jobs in INR)
- `app/models/sidecar.py` (Embedding and NER sidecar tables)
- `app/api/auth.py` (JWT & cookie authentication, role guardrails)
- `app/templates/base.html` (Role-based navbar logic & global layout)

---

## 📋 Implementation Checklist
1. **Role-Based Navbar Enforcement**:
   - Creator logged in: Hide "Discover Creators" link.
   - Company logged in: Hide "Brands & Companies" link.
   - Visitor: Show all discovery links.
2. **Database Migrations & Auto-Sync**:
   - Ensure `init_db()` in `app/db/database.py` safely inspects existing columns (`status`, `views_count`, `hourly_rate_inr`, `is_pinned`, `budget_inr`, `logo_url`) and runs `ALTER TABLE` if missing.
3. **Database Seeding**:
   - Ensure `seed_database()` creates realistic creators with INR rates, at least 2 portfolio items, verified tools, company reviews, and connections.
4. **Testing Verification**:
   ```bash
   python -m pytest tests/test_auth.py tests/test_companies.py
   ```

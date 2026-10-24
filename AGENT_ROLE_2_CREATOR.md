# Agent Playbook — Member 2: Creator Profiles, Portfolios & Connections Lead

## 🎯 Role Overview
You are the **Creator Experience Lead**. You own the distinct creator profile structure, AI specifications, tools display, mandatory 2 portfolio uploads rule, pinning best works (max 3), creator connections, and view tracking.

---

## 📁 Your Target Files to Implement & Maintain
- `app/models/creator.py` (CreatorProfile schema, status draft/published, views_count, specs, hourly_rate_inr)
- `app/models/portfolio.py` (PortfolioItem schema, is_pinned, pin_order, views_count)
- `app/models/connection.py` (CreatorConnection schema, mutual connection request/accept)
- `app/services/creator_service.py` (Draft/published transition, pin work, increment views)
- `app/services/connection_service.py` (Send request, accept, reject, list connections)
- `app/api/creators.py` (Creator endpoints, pin toggle endpoint)
- `app/api/connections.py` (Connection endpoints)
- `app/templates/creators/detail.html` (Public creator profile, specs card, pinned works, reviews)
- `app/templates/dashboard/creator.html` (Draft banner, pin buttons, connections management)

---

## 📋 Implementation Checklist
1. **Mandatory 2 Uploads Rule**:
   - `CreatorProfile.status`: Set to `"draft"` if `< 2` uploads; automatically promote to `"published"` once `>= 2` uploads are completed.
   - Creator dashboard shows warning banner with progress (`{count}/2 uploads`) while in draft mode.
2. **Pin Best Work (Max 3)**:
   - Implement `toggle_pin_portfolio_item(db, creator_id, item_id, is_pinned)`.
   - Prevent pinning more than 3 works with `HTTP 400 Bad Request`.
   - Highlight pinned items at top of creator profile with golden star ribbon.
3. **Creator Connections**:
   - Mutual connection model (`'pending'` -> `'accepted'` / `'rejected'`).
   - Display total connections and list on creator profile.
4. **View Tracking**:
   - Increment `views_count` on creator profile and portfolio items with session de-duplication.
5. **Testing Verification**:
   ```bash
   python -m pytest tests/test_creators.py tests/test_reviewer_features.py -k "test_creator_connections_flow or test_mandatory_two_uploads_and_pinning"
   ```

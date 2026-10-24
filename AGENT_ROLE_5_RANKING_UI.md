# Agent Playbook — Member 5: Ranking Engine, AI Brief Builder & UI Integration

## 🎯 Role Overview
You are the **Ranking Algorithm & Product Experience Lead**. You own the 5-factor creator ranking engine with equal 20% weights, the AI-assisted Brief Builder (Groq RAG + fallback), and the responsive user interface.

---

## 📁 Your Target Files to Implement & Maintain
- `app/services/ranking_service.py` (2-stage filter and 5-signal deterministic formula with equal 20% weights)
- `app/services/rag_service.py` (Brief synthesis with grounded citations to catalog standards)
- `app/api/advanced.py` (`/api/v2/rankings/creators-for-brief`, `/api/v2/briefs/ai-generate`, `/api/v2/creators/{id}/explain-match/{job_id}`)
- `app/templates/ai/brief_builder.html` (Interactive AI brief builder wizard)
- `app/templates/jobs/list.html` & `app/templates/jobs/detail.html` (Briefs discovery with INR pricing)

---

## 📋 Implementation Checklist
1. **5-Factor Equal 20% Creator Ranking Engine**:
   - **Stage 1 (Hard Gate)**: Exclude creators who lack required commercial buyout rights or required aspect ratio.
   - **Stage 2 (Scoring Formula)**:
     $$\text{Score} = 0.20 \times S_{\text{semantic}} + 0.20 \times S_{\text{tools}} + 0.20 \times S_{\text{reviews}} + 0.20 \times S_{\text{verification}} + 0.20 \times S_{\text{views}}$$
   - Provide transparent score breakdown explaining why each creator is recommended.
2. **AI-Assisted Brief Builder (Groq RAG)**:
   - Convert a rough brand concept into a structured creative brief.
   - Grounded citations: Citations must reference actual portfolio items or industry standards.
   - Built-in deterministic fallback when Groq API key is absent.
3. **UI Polish & Match Explainer**:
   - Modal dialog for companies showing score breakdown radar/meters and matched tools.
4. **Testing Verification**:
   ```bash
   python -m pytest tests/test_advanced_features.py -k "test_deterministic_ranking or test_match_explanation or test_rag_brief_generation"
   ```

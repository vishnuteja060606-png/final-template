# Agent Playbook — Member 4: Semantic Search & Canonical NER Engine

## 🎯 Role Overview
You are the **Machine Learning & Information Retrieval Lead**. You own zero-cost local vector embeddings (FastEmbed ONNX), the Named Entity Recognition (NER) pipeline for AI toolchains and aspect ratios, and the Hybrid Search engine combining keywords and vectors via Reciprocal Rank Fusion (RRF).

---

## 📁 Your Target Files to Implement & Maintain
- `app/services/embedding_service.py` (Local ONNX vector generation, dot product cosine similarity)
- `app/services/ner_service.py` (Canonical alias dictionaries, regex extraction, Groq LLM structured fallback)
- `app/services/hybrid_search_service.py` (Reciprocal Rank Fusion algorithm combining BM25 and vectors)
- `app/api/advanced.py` (`/api/v2/search/semantic`, `/api/v2/search/hybrid`, `/api/v2/ner/extract`)

---

## 📋 Implementation Checklist
1. **Semantic Search via FastEmbed**:
   - Zero-budget local execution: `BAAI/bge-small-en-v1.5` running locally via ONNX CPU (<100MB RAM, zero API key).
   - Index creator profiles, portfolio items, and job briefs into `embedding_records` sidecar table.
   - Vector similarity query: `POST /api/v2/search/semantic`.
2. **Named Entity Recognition (NER)**:
   - Extract AI tools (`Runway Gen-3`, `Midjourney v6`, `ComfyUI`, `Flux.1`, `Kling AI`, `ElevenLabs`), aspect ratios (`16:9`, `9:16`, `1:1`), resolutions (`4K`), and licenses (`Commercial Buyout`).
   - Track entity provenance: `'creator_claim'`, `'platform_verified'`, `'brief_requirement'`.
3. **Hybrid Search with Reciprocal Rank Fusion (RRF)**:
   - Run keyword query (SQL `LIKE` on title, tools, skills, bio) and vector similarity query in parallel.
   - Merge candidates:
     $$RRF\_Score(d) = \frac{1}{60 + rank_{keyword}(d)} + \frac{1}{60 + rank_{vector}(d)}$$
   - Apply hard filters for aspect ratio, delivery format, and maximum budget in INR.
4. **Testing Verification**:
   ```bash
   python -m pytest tests/test_advanced_features.py -k "test_semantic_search or test_ner_extraction or test_hybrid_search"
   ```

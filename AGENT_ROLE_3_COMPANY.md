# Agent Playbook — Member 3: Company Profiles, Reviews & Currency Lead

## 🎯 Role Overview
You are the **Enterprise & Brand Experience Lead**. You own the distinct company profile structure, the company reviews system for creators, and the primary INR (₹) / optional USD ($) multi-currency converter.

---

## 📁 Your Target Files to Implement & Maintain
- `app/models/company.py` (CompanyProfile schema, logo_url, location, social_links)
- `app/models/review.py` (CreatorReview schema, star ratings 1-5, project_title, tools_used)
- `app/services/company_service.py` (Company lookup, profile check records)
- `app/services/review_service.py` (Submit review, get creator reviews summary, calculate average rating)
- `app/api/companies.py` (Company endpoints)
- `app/api/reviews.py` (Review submission and retrieval endpoints)
- `app/templates/companies/detail.html` (Company profile with logo, posted briefs, reviews given)
- `app/static/js/main.js` (Dynamic currency switch logic, formatMoney, updateCurrencyDisplay)

---

## 📋 Implementation Checklist
1. **Company Reviews for Creators**:
   - Allow registered companies to submit 1-5 star reviews on creator profiles with project title, comment, and tools used.
   - Calculate and display average rating and total review counts on creator cards and profiles.
   - Creator ranking algorithm uses this review rating as a 20% factor.
2. **Distinct Company Profile Structure**:
   - Company logo, industry tag, location, website link, and social media links (LinkedIn, Twitter).
   - List active briefs posted by the company with INR budgets.
   - List past reviews given by the company to AI creators.
3. **Multi-Currency System (Primary INR ₹, Optional USD $)**:
   - Stored values in database are in base INR (`budget_inr`, `hourly_rate_inr`).
   - Global navbar toggle switch `[ ₹ INR | $ USD ]` updates `localStorage`.
   - All elements marked with `data-inr="<amount>"` dynamically re-render in ₹ or $ using configurable exchange rate (1 USD = ₹85.0).
4. **Testing Verification**:
   ```bash
   python -m pytest tests/test_companies.py tests/test_reviewer_features.py -k "test_company_review_submission_and_metrics or test_creator_cannot_submit_company_review"
   ```

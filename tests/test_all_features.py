import pytest
from app.models.user import User
from app.models.creator import CreatorProfile
from app.models.company import CompanyProfile
from app.models.portfolio import PortfolioItem
from app.models.engagement import Engagement
from app.services.auth_service import AuthService


def test_two_factor_auth_email_otp(client, db_session, creator_user):
    """Test 2FA OTP generation and verification via email."""
    # 1. Request OTP
    res = client.post("/api/auth/send-otp", json={"email": creator_user.email})
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == creator_user.email
    assert data["expires_in_minutes"] == 10

    # Retrieve generated OTP from DB session
    db_session.expire_all()
    user_in_db = db_session.query(User).filter(User.id == creator_user.id).first()
    otp_code = user_in_db.email_otp_code
    assert otp_code is not None
    assert len(otp_code) == 6

    # 2. Verify with invalid OTP
    res_bad = client.post("/api/auth/verify-otp", json={"email": creator_user.email, "code": "000000"})
    assert res_bad.status_code == 400
    assert "Invalid or expired" in res_bad.json()["detail"]

    # 3. Verify with valid OTP
    res_ok = client.post("/api/auth/verify-otp", json={"email": creator_user.email, "code": otp_code})
    assert res_ok.status_code == 200
    auth_data = res_ok.json()
    assert "access_token" in auth_data
    assert auth_data["role"] == "creator"


def test_role_separation_creator_cannot_view_creators(client, db_session, creator_user, creator_auth_headers):
    """
    Requirement: Creators cannot see other creators (to prevent creative espionage/copying).
    Logged-in creator browsing /api/creators or other creator profile must receive 403 Forbidden.
    """
    # Create second creator
    u2 = User(email="second_creator@example.com", password_hash=AuthService.hash_password("pass123"), role="creator")
    db_session.add(u2)
    db_session.commit()
    p2 = CreatorProfile(user_id=u2.id, display_name="Second Creator", specialization="AI Animation")
    db_session.add(p2)
    db_session.commit()

    # Logged-in creator cannot list creators
    res = client.get("/api/creators", headers=creator_auth_headers)
    assert res.status_code == 403
    assert "Access restricted" in res.json()["detail"]

    # Logged-in creator cannot view another creator's detail
    res_detail = client.get(f"/api/creators/{p2.id}", headers=creator_auth_headers)
    assert res_detail.status_code == 403
    assert "Access restricted" in res_detail.json()["detail"]

    # But creator CAN view company directory
    res_comp = client.get("/api/companies", headers=creator_auth_headers)
    assert res_comp.status_code == 200


def test_role_separation_company_cannot_view_companies(client, db_session, company_user, company_auth_headers):
    """
    Requirement: Companies cannot see other companies.
    Logged-in company browsing /api/companies or competitor company profile must receive 403 Forbidden.
    """
    # Create second company
    u2 = User(email="second_brand@example.com", password_hash=AuthService.hash_password("pass123"), role="company")
    db_session.add(u2)
    db_session.commit()
    c2 = CompanyProfile(user_id=u2.id, company_name="Rival Brand Inc", industry="Automotive")
    db_session.add(c2)
    db_session.commit()

    # Logged-in company cannot list companies
    res = client.get("/api/companies", headers=company_auth_headers)
    assert res.status_code == 403
    assert "Access restricted" in res.json()["detail"]

    # Logged-in company cannot view another company's profile
    res_detail = client.get(f"/api/companies/{c2.id}", headers=company_auth_headers)
    assert res_detail.status_code == 403
    assert "Access restricted" in res_detail.json()["detail"]

    # But company CAN view creators directory
    res_creators = client.get("/api/creators", headers=company_auth_headers)
    assert res_creators.status_code == 200


def test_price_bidding_and_negotiation_in_inr(client, db_session, creator_user, company_user, creator_auth_headers, company_auth_headers):
    """
    Requirement: Price bid & two-way negotiation in INR.
    Company sends bid; creator counters; company accepts; deal is agreed.
    """
    creator_prof = creator_user.creator_profile

    # 1. Company sends engagement with initial bid in INR
    create_payload = {
        "creator_id": creator_prof.id,
        "message": "We want to hire you for a 30s Runway Gen-3 campaign.",
        "bid_amount_inr": 45000,
        "proposed_budget": "₹45,000"
    }
    res = client.post("/api/engagements", json=create_payload, headers=company_auth_headers)
    assert res.status_code == 201
    eng_data = res.json()
    eng_id = eng_data["id"]
    assert eng_data["bid_amount_inr"] == 45000
    assert eng_data["negotiation_status"] == "initial_bid"

    # 2. Creator submits counter-offer in INR
    counter_payload = {
        "counter_offer_inr": 55000,
        "notes": "Includes 4K master delivery and 2 rounds of creative revisions."
    }
    res_counter = client.post(f"/api/engagements/{eng_id}/counter-offer", json=counter_payload, headers=creator_auth_headers)
    assert res_counter.status_code == 200
    counter_data = res_counter.json()
    assert counter_data["counter_offer_inr"] == 55000
    assert counter_data["negotiation_status"] == "counter_offered"
    assert counter_data["last_negotiated_by"] == "creator"
    assert counter_data["active_price_inr"] == 55000

    # 3. Company accepts the counter-offer
    res_accept = client.post(f"/api/engagements/{eng_id}/accept-bid", headers=company_auth_headers)
    assert res_accept.status_code == 200
    accept_data = res_accept.json()
    assert accept_data["status"] == "accepted"
    assert accept_data["negotiation_status"] == "agreed"


def test_portfolio_moderation_and_approval(client, db_session, creator_user, creator_auth_headers):
    """
    Requirement: Creator can only post approved works.
    Portfolio items support moderation status and approval/rejection.
    """
    creator_prof = creator_user.creator_profile

    item = PortfolioItem(
        creator_id=creator_prof.id,
        title="Cinematic Spec Commercial",
        original_filename="spec_commercial.mp4",
        file_size=2048,
        content_type="Video",
        file_path="/uploads/test_video.mp4",
        mime_type="video/mp4",
        is_approved=False,
        approval_status="pending"
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    # Create admin user for moderation actions
    admin_user = User(
        email="admin_moderator@example.com",
        password_hash=AuthService.hash_password("adminpass123"),
        role="admin"
    )
    db_session.add(admin_user)
    db_session.commit()
    admin_token = AuthService.create_access_token(
        data={"sub": str(admin_user.id), "role": admin_user.role, "email": admin_user.email}
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Reject item with note
    res_rej = client.post(f"/api/portfolio/{item.id}/reject?reason=Missing+commercial+disclaimer", headers=admin_headers)
    assert res_rej.status_code == 200
    data_rej = res_rej.json()
    assert data_rej["approval_status"] == "rejected"
    assert data_rej["is_approved"] is False
    assert data_rej["moderation_note"] == "Missing commercial disclaimer"

    # Approve item
    res_app = client.post(f"/api/portfolio/{item.id}/approve", headers=admin_headers)
    assert res_app.status_code == 200
    data_app = res_app.json()
    assert data_app["approval_status"] == "approved"
    assert data_app["is_approved"] is True


def test_pin_best_works_and_view_tracking(client, db_session, creator_user, creator_auth_headers):
    """
    Requirement: Pin up to 3 best works with golden star ribbon and track views.
    """
    creator_prof = creator_user.creator_profile

    # Create 4 portfolio items
    items = []
    for i in range(4):
        item = PortfolioItem(
            creator_id=creator_prof.id,
            title=f"Work #{i+1}",
            original_filename=f"work_{i+1}.mp4",
            file_size=1024,
            content_type="Video",
            file_path=f"/uploads/work_{i+1}.mp4",
            mime_type="video/mp4",
            is_approved=True,
            approval_status="approved"
        )
        db_session.add(item)
        items.append(item)
    db_session.commit()

    # Pin first 3 works
    for idx in range(3):
        res = client.put(f"/api/portfolio/{items[idx].id}/pin", json={"is_pinned": True}, headers=creator_auth_headers)
        assert res.status_code == 200
        assert res.json()["is_pinned"] is True

    # Attempt to pin a 4th work (must fail max 3 limit)
    res_4 = client.put(f"/api/portfolio/{items[3].id}/pin", json={"is_pinned": True}, headers=creator_auth_headers)
    assert res_4.status_code == 400
    assert "maximum of 3" in res_4.json()["detail"].lower()

    # Increment views
    res_view = client.post(f"/api/creators/portfolio/{items[0].id}/view")
    assert res_view.status_code == 200
    assert res_view.json()["views_count"] >= 1


def test_creator_connections_network(client, db_session, creator_user, creator_auth_headers):
    """
    Requirement: Mutual creator networking and connection requests.
    """
    u2 = User(email="artist2@example.com", password_hash=AuthService.hash_password("pass123"), role="creator")
    db_session.add(u2)
    db_session.commit()
    p2 = CreatorProfile(user_id=u2.id, display_name="Artist Two", specialization="ComfyUI Generative")
    db_session.add(p2)
    db_session.commit()

    # Send connection request
    res_conn = client.post(f"/api/creators/{p2.id}/connect", headers=creator_auth_headers)
    assert res_conn.status_code == 201
    conn_data = res_conn.json()
    assert conn_data["status"] == "pending"
    conn_id = conn_data["id"]

    # Accept connection
    u2_token = AuthService.create_access_token(data={"sub": str(u2.id), "role": u2.role, "email": u2.email})
    u2_headers = {"Authorization": f"Bearer {u2_token}"}

    res_accept = client.post(f"/api/connections/{conn_id}/status", json={"action": "accept"}, headers=u2_headers)
    assert res_accept.status_code == 200
    assert res_accept.json()["status"] == "accepted"


def test_web_routes_auth_and_redirects(client, db_session, creator_user, creator_token, company_user, company_token):
    """
    Requirement: Web routes enforce guest auth overlay and role redirects.
    """
    # 2FA verify page
    res_otp = client.get("/verify-otp")
    assert res_otp.status_code == 200

    # Logged-in creator visiting /creators is redirected to /projects
    client.cookies.set("access_token", creator_token)
    res_redir_creator = client.get("/creators", follow_redirects=False)
    assert res_redir_creator.status_code == 303
    assert "/projects?notice=creators_restricted" in res_redir_creator.headers["location"]

    # Logged-in company visiting /companies is redirected to /creators
    client.cookies.set("access_token", company_token)
    res_redir_company = client.get("/companies", follow_redirects=False)
    assert res_redir_company.status_code == 303
    assert "/creators?notice=companies_restricted" in res_redir_company.headers["location"]

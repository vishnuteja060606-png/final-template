import os
import json
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, init_db
from app.models.user import User
from app.models.creator import CreatorProfile
from app.models.portfolio import PortfolioItem
from app.models.company import CompanyProfile
from app.models.job import Job
from app.models.verification import VerificationSignal
from app.models.engagement import Engagement
from app.models.review import CreatorReview
from app.models.connection import CreatorConnection
from app.services.auth_service import AuthService
from app.config import settings
from app.services.embedding_service import embedding_service
from app.services.ner_service import ner_service

logger = logging.getLogger(__name__)

def seed_advanced_indexes(db: Session) -> None:
    """Indexes all creators, jobs, and portfolios into sidecar embedding and NER tables."""
    try:
        creators = db.query(CreatorProfile).all()
        for c in creators:
            text = f"{c.display_name} {c.headline or ''} {c.bio or ''} {c.specialization or ''} {c.skills or ''} {c.tools_models or ''} {c.workflow or ''}"
            embedding_service.index_entity(db, "creator", c.id, text)
            extracted = ner_service.extract_entities(text, "creator_claim")
            ner_service.persist_extracted_entities("creator", c.id, extracted, db)

        jobs = db.query(Job).all()
        for j in jobs:
            text = f"{j.title} {j.description} {j.campaign_requirements or ''} {j.content_type or ''} {j.style or ''} {j.format or ''} {j.aspect_ratio or ''} {j.required_skills or ''} {j.required_tools or ''} {j.commercial_use or ''}"
            embedding_service.index_entity(db, "job", j.id, text)
            extracted = ner_service.extract_entities(text, "brief_requirement")
            ner_service.persist_extracted_entities("job", j.id, extracted, db)

        portfolios = db.query(PortfolioItem).all()
        for p in portfolios:
            text = f"{p.title} {p.description or ''} {p.workflow or ''} {p.tools_models or ''} {p.skills or ''} {p.tags or ''} {p.content_type or ''} {p.aspect_ratio or ''}"
            embedding_service.index_entity(db, "portfolio", p.id, text)

        print("Advanced sidecar indexes (Embeddings & NER) successfully generated!")
    except Exception as e:
        print(f"Notice: Indexing completed with note: {e}")

def _backfill_missing_relations(db: Session) -> None:
    """Safely backfills reviews, connections, and signals if an existing database lacks them."""
    try:
        creators = db.query(CreatorProfile).all()
        companies = db.query(CompanyProfile).all()
        if not creators or not companies:
            return

        # Backfill reviews
        if db.query(CreatorReview).count() == 0 and len(companies) >= 2 and len(creators) >= 3:
            r1 = CreatorReview(
                creator_id=creators[0].id,
                company_id=companies[0].id,
                rating=5,
                project_title="Quantum Sneaker 4K Commercial",
                comment="Elena exceeded every expectation. Her Runway Gen-3 prompt control and 60fps upscaling made the shoe look hyper-realistic.",
                tools_used="Runway Gen-3 + Topaz Video AI",
                is_verified_engagement=True
            )
            r2 = CreatorReview(
                creator_id=creators[1].id,
                company_id=companies[1].id,
                rating=5,
                project_title="Cyberpunk Virtual Stage Backdrop",
                comment="Marcus delivers repeatable node-based quality with ComfyUI. The Blender camera tracking gave our stream authentic 3D spatial presence.",
                tools_used="ComfyUI + Blender",
                is_verified_engagement=True
            )
            r3 = CreatorReview(
                creator_id=creators[2].id,
                company_id=companies[1].id,
                rating=5,
                project_title="Luxury Perfume Key Visuals",
                comment="Aria has an extraordinary eye for lighting and luxury aesthetics. The Midjourney v6 + Flux.1 rendering was clean enough for 8K billboard printing.",
                tools_used="Midjourney v6 + Flux.1",
                is_verified_engagement=True
            )
            db.add_all([r1, r2, r3])
            db.commit()

        # Backfill connections
        if db.query(CreatorConnection).count() == 0 and len(creators) >= 3:
            conn1 = CreatorConnection(requester_id=creators[0].id, receiver_id=creators[1].id, status="accepted")
            conn2 = CreatorConnection(requester_id=creators[0].id, receiver_id=creators[2].id, status="accepted")
            db.add_all([conn1, conn2])
            if len(creators) >= 4:
                conn3 = CreatorConnection(requester_id=creators[3].id, receiver_id=creators[0].id, status="pending")
                db.add(conn3)
            db.commit()

        # Backfill verification signals
        if db.query(VerificationSignal).count() == 0 and len(creators) >= 3:
            v1 = VerificationSignal(creator_id=creators[0].id, signal_type="tool_verified", badge_name="Runway Gen-3 Master", description="Verified mastery in generative video camera movement and motion prompting.")
            v2 = VerificationSignal(creator_id=creators[0].id, signal_type="commercial_ready", badge_name="Commercial Grade Verified", description="Delivers broadcast-compliant 4K assets with cleared IP rights.")
            v3 = VerificationSignal(creator_id=creators[1].id, signal_type="tool_verified", badge_name="ComfyUI Specialist", description="Verified technical proficiency in repeatable node-based generative workflows.")
            v4 = VerificationSignal(creator_id=creators[2].id, signal_type="commercial_ready", badge_name="Luxury Brand Approved", description="Demonstrated high-end editorial and commercial product rendering.")
            db.add_all([v1, v2, v3, v4])
            db.commit()

    except Exception as ex:
        db.rollback()
        logger.warning(f"Notice during backfilling relations: {ex}")

def seed_database(db: Session | None = None) -> None:
    should_close = False
    if db is None:
        init_db()
        db = SessionLocal()
        should_close = True

    try:
        # Check if already seeded
        if db.query(User).count() > 0:
            _backfill_missing_relations(db)
            from app.models.sidecar import EmbeddingRecord
            if db.query(EmbeddingRecord).count() == 0:
                seed_advanced_indexes(db)
            return

        print("Seeding initial marketplace data with reviewer specifications...")

        uploads_dir = Path(settings.UPLOAD_DIR)
        sample_creator_1_dir = uploads_dir / "creators" / "1"
        sample_creator_2_dir = uploads_dir / "creators" / "2"
        sample_creator_3_dir = uploads_dir / "creators" / "3"
        sample_creator_4_dir = uploads_dir / "creators" / "4"
        sample_creator_1_dir.mkdir(parents=True, exist_ok=True)
        sample_creator_2_dir.mkdir(parents=True, exist_ok=True)
        sample_creator_3_dir.mkdir(parents=True, exist_ok=True)
        sample_creator_4_dir.mkdir(parents=True, exist_ok=True)

        def write_svg_preview(path: Path, title: str, subtitle: str, bg_color: str = "#0f172a"):
            svg = f"""<svg width="640" height="360" xmlns="http://www.w3.org/2000/svg">
                <rect width="100%" height="100%" fill="{bg_color}"/>
                <circle cx="320" cy="180" r="110" fill="#6366f1" opacity="0.35"/>
                <text x="50%" y="45%" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="22" font-weight="bold" fill="#ffffff">{title}</text>
                <text x="50%" y="60%" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#a5b4fc">{subtitle}</text>
            </svg>"""
            with open(path, "w", encoding="utf-8") as f:
                f.write(svg)

        file_1 = sample_creator_1_dir / "nike_spec.svg"
        file_2 = sample_creator_1_dir / "future_motors.svg"
        file_3 = sample_creator_1_dir / "quantum_orbit.svg"
        file_4 = sample_creator_2_dir / "cyberpunk_loop.svg"
        file_5 = sample_creator_2_dir / "neo_tokyo_vfx.svg"
        file_6 = sample_creator_3_dir / "luxury_perfume.svg"
        file_7 = sample_creator_3_dir / "haute_couture.svg"
        file_8 = sample_creator_4_dir / "social_hook_reel.svg"
        file_9 = sample_creator_4_dir / "beverage_viral_loop.svg"

        write_svg_preview(file_1, "Nike Velocity Cinematic", "Runway Gen-3 • 16:9 • AI Video", "#0f172a")
        write_svg_preview(file_2, "Future Motors Teaser", "Kling AI + Midjourney • 16:9", "#111827")
        write_svg_preview(file_3, "Quantum Orbit 4K", "Sora Alpha • 16:9 60fps", "#090d16")
        write_svg_preview(file_4, "Cyberpunk Metropolis", "AnimateDiff • 16:9 • Animation", "#1e1b4b")
        write_svg_preview(file_5, "Neo Tokyo VFX Node", "ComfyUI + Blender • 16:9", "#172554")
        write_svg_preview(file_6, "Aura Luxury Editorial", "Midjourney v6 • 1:1 • Commercial", "#312e81")
        write_svg_preview(file_7, "Haute Couture Mirage", "Flux.1 Dev • 9:16 Vertical", "#431407")
        write_svg_preview(file_8, "DTC Energy Viral Hook", "Runway Gen-3 • 9:16 Vertical Reel", "#042f2e")
        write_svg_preview(file_9, "Z-Sugar Soda Pop Splash", "ElevenLabs + Pika • 9:16 Reel", "#134e4a")

        # 1. Creators Users
        c1_user = User(email="elena@aicreator.io", password_hash=AuthService.hash_password("creator123"), role="creator")
        c2_user = User(email="marcus@aicreator.io", password_hash=AuthService.hash_password("creator123"), role="creator")
        c3_user = User(email="aria@aicreator.io", password_hash=AuthService.hash_password("creator123"), role="creator")
        c4_user = User(email="devon@aicreator.io", password_hash=AuthService.hash_password("creator123"), role="creator")

        # 2. Companies Users
        comp1_user = User(email="creative@omnisport.com", password_hash=AuthService.hash_password("company123"), role="company")
        comp2_user = User(email="director@luminacreative.com", password_hash=AuthService.hash_password("company123"), role="company")

        db.add_all([c1_user, c2_user, c3_user, c4_user, comp1_user, comp2_user])
        db.commit()

        # Creator Profiles (Seeded with INR Rates, Tools, Specs, and Socials)
        c1_profile = CreatorProfile(
            user_id=c1_user.id,
            display_name="Elena Rostova",
            headline="AI Commercial Filmmaker & Generative Director",
            bio="Award-winning AI filmmaker utilizing cutting-edge diffusion and video transformers (Runway Gen-3, Kling, Sora) to create broadcast-quality advertising.",
            specialization="AI Video",
            skills="AI Video Generation, Prompt Engineering, Motion Design, Storyboarding, Color Grading",
            tools_models="Runway Gen-3, Kling AI, Topaz Video AI, Midjourney v6",
            workflow="1. Prompt matrices in Midjourney v6. 2. Motion orchestration with Runway Gen-3 & Kling. 3. Topaz 4K spatial upscaling. 4. Mastered in DaVinci Resolve.",
            experience_level="Expert (5+ yrs commercial experience)",
            location="Mumbai, India / Remote",
            website="https://elenarostova.ai",
            social_links=json.dumps({
                "twitter": "https://x.com/elenacreates_ai",
                "instagram": "https://instagram.com/elena_films",
                "youtube": "https://youtube.com/@elena_ai_films",
                "artstation": "https://artstation.com/elenarostova",
                "linkedin": "https://linkedin.com/in/elena-rostova-ai"
            }),
            specifications=json.dumps({
                "resolution": "4K Ultra HD (3840x2160)",
                "max_fps": "60 FPS Mastered",
                "aspect_ratios": "16:9 Landscape, 9:16 Vertical, 2.39:1 Cinemascope",
                "turnaround_days": "24 - 48 Hours Express",
                "hardware": "Local Dual RTX 4090 (48GB VRAM)",
                "lora_training": "Custom LoRA Character & Prop consistency supported"
            }),
            hourly_rate_inr=3500,  # ₹3,500/hr
            profile_image_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300&auto=format&fit=crop&q=80",
            status="published",
            views_count=1840,
            is_verified=True
        )

        c2_profile = CreatorProfile(
            user_id=c2_user.id,
            display_name="Marcus Vance",
            headline="Generative 3D Worldbuilder & AI VFX Animator",
            bio="Specializing in sci-fi aesthetic animation and procedural node pipelines with consistent character turnarounds.",
            specialization="AI Animation",
            skills="AI Animation, Character Consistency, 3D Camera Projection, ComfyUI Workflows",
            tools_models="Stable Diffusion XL, ComfyUI, AnimateDiff, Blender, Flux.1",
            workflow="Node-based ComfyUI custom pipelines with ControlNet depth maps combined with 3D Blender camera tracking.",
            experience_level="Advanced",
            location="Bengaluru, India / Remote",
            website="https://marcusvance.xyz",
            social_links=json.dumps({
                "twitter": "https://x.com/marcusv_3d",
                "artstation": "https://artstation.com/marcusvance",
                "github": "https://github.com/marcusvance-comfy"
            }),
            specifications=json.dumps({
                "resolution": "4K Ultra HD",
                "max_fps": "60 FPS Looping",
                "aspect_ratios": "16:9 Landscape, 1:1 Square",
                "turnaround_days": "3 - 5 Days",
                "hardware": "Local RTX 4090 Workstation",
                "lora_training": "Style & environment LoRA checkpoints"
            }),
            hourly_rate_inr=2800,  # ₹2,800/hr
            profile_image_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&auto=format&fit=crop&q=80",
            status="published",
            views_count=1230,
            is_verified=True
        )

        c3_profile = CreatorProfile(
            user_id=c3_user.id,
            display_name="Aria Chen",
            headline="Luxury Generative Brand Designer & Key Visual Director",
            bio="Crafting photo-real product photography and key visuals for international fashion, cosmetic, and luxury houses.",
            specialization="Generative Advertising",
            skills="Product Photography, Lighting Control, Inpainting, Brand Identity",
            tools_models="Midjourney v6, Flux.1, Stable Diffusion XL, Photoshop",
            workflow="Iterative latent space exploration, LoRA training for bespoke product geometries, custom lighting passes.",
            experience_level="Expert",
            location="Delhi, India / Remote",
            website="https://ariachen.design",
            social_links=json.dumps({
                "instagram": "https://instagram.com/aria_ai_studio",
                "linkedin": "https://linkedin.com/in/ariachen-design"
            }),
            specifications=json.dumps({
                "resolution": "8K Print Ready (7680x4320)",
                "max_fps": "30 FPS for Motion Posters",
                "aspect_ratios": "1:1 Square, 4:5 Portrait, 9:16 Vertical Stories",
                "turnaround_days": "24 Hours",
                "hardware": "Cloud H100 Cluster",
                "lora_training": "Product geometry matching with zero artifacts"
            }),
            hourly_rate_inr=4200,  # ₹4,200/hr
            profile_image_url="https://images.unsplash.com/photo-1517841905240-472988babdf9?w=300&auto=format&fit=crop&q=80",
            status="published",
            views_count=1650,
            is_verified=True
        )

        c4_profile = CreatorProfile(
            user_id=c4_user.id,
            display_name="Devon Brooks",
            headline="AI Social Content Creator & High-Converting Reel Specialist",
            bio="Helping direct-to-consumer brands produce viral 9:16 vertical video hooks and dynamic sound-synced video ads.",
            specialization="Social Media Creatives",
            skills="Short-form Video, Hook Pacing, ElevenLabs Voice AI, Rapid Iteration",
            tools_models="Runway Gen-3, Pika Labs, Midjourney v6, ElevenLabs",
            workflow="Trend scraping, AI script generation, vertical asset synthesis, and viral sound sync.",
            experience_level="Intermediate",
            location="Hyderabad, India / Remote",
            website="https://devonbrooks.media",
            social_links=json.dumps({
                "twitter": "https://x.com/devon_reels",
                "instagram": "https://instagram.com/devon_ai_hooks"
            }),
            specifications=json.dumps({
                "resolution": "1080p Full HD & 4K Vertical",
                "max_fps": "60 FPS Reels",
                "aspect_ratios": "9:16 Vertical Dedicated",
                "turnaround_days": "12 - 24 Hours",
                "hardware": "Local RTX 4080 Rig",
                "lora_training": "Social influencer avatar generation"
            }),
            hourly_rate_inr=1800,  # ₹1,800/hr
            profile_image_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300&auto=format&fit=crop&q=80",
            status="published",
            views_count=980,
            is_verified=False
        )

        db.add_all([c1_profile, c2_profile, c3_profile, c4_profile])
        db.commit()

        # Seed Portfolio Items (At least 2 per creator, with PINNED works!)
        # Elena (3 works, 2 pinned)
        p1 = PortfolioItem(
            creator_id=c1_profile.id,
            title="Nike Velocity: Synthetic Athlete Teaser",
            description="Spec commercial directed entirely with generative video pipelines showcasing impossible camera moves.",
            file_path="/uploads/creators/1/nike_spec.svg",
            original_filename="nike_spec.svg",
            mime_type="image/svg+xml",
            file_size=1024,
            content_type="Video",
            aspect_ratio="16:9",
            format="MP4",
            tools_models="Runway Gen-3, Midjourney v6, Topaz Video AI",
            skills="AI Video Generation, Prompt Engineering, Motion Design",
            specialization="AI Video",
            tags="Commercial, Sports, Futuristic, 4K",
            workflow="Prompt exploration -> Runway Gen-3 camera control -> Topaz upscaling.",
            is_pinned=True,
            pin_order=1,
            views_count=1240
        )
        p2 = PortfolioItem(
            creator_id=c1_profile.id,
            title="Future Motors: Hyper-EV Reveal",
            description="Concept automobile launch video with realistic volumetric lighting and dynamic reflections.",
            file_path="/uploads/creators/1/future_motors.svg",
            original_filename="future_motors.svg",
            mime_type="image/svg+xml",
            file_size=1024,
            content_type="Video",
            aspect_ratio="16:9",
            format="MP4",
            tools_models="Kling AI, Midjourney v6",
            skills="AI Video Generation, Lighting Control",
            specialization="AI Video",
            tags="Automotive, Launch, Luxury",
            workflow="Image-to-video workflow using photoreal Midjourney hero frames.",
            is_pinned=True,
            pin_order=2,
            views_count=870
        )
        p3 = PortfolioItem(
            creator_id=c1_profile.id,
            title="Quantum Orbit: Cosmic Exploration",
            description="Deep space cinematic rendered with fluid particulate physics and procedural nebula simulation.",
            file_path="/uploads/creators/1/quantum_orbit.svg",
            original_filename="quantum_orbit.svg",
            mime_type="image/svg+xml",
            file_size=1024,
            content_type="Video",
            aspect_ratio="16:9",
            format="MP4",
            tools_models="Sora Alpha, Topaz Video AI",
            skills="AI Video Generation, Color Grading",
            specialization="AI Video",
            tags="SciFi, Space, Cinematic",
            workflow="Diffusion camera tracking with spatial depth layers.",
            is_pinned=False,
            pin_order=0,
            views_count=430
        )

        # Marcus (2 works, 1 pinned)
        p4 = PortfolioItem(
            creator_id=c2_profile.id,
            title="Neo-Shinjuku 2099 Loop",
            description="Infinite seamless cybernetic street animation loop with consistent characters.",
            file_path="/uploads/creators/2/cyberpunk_loop.svg",
            original_filename="cyberpunk_loop.svg",
            mime_type="image/svg+xml",
            file_size=1024,
            content_type="Animation",
            aspect_ratio="16:9",
            format="MP4",
            tools_models="Stable Diffusion XL, ComfyUI, AnimateDiff",
            skills="AI Animation, Character Consistency",
            specialization="AI Animation",
            tags="Cyberpunk, Loop, SciFi",
            workflow="Multi-ControlNet depth + openpose with AnimateDiff motion model.",
            is_pinned=True,
            pin_order=1,
            views_count=980
        )
        p5 = PortfolioItem(
            creator_id=c2_profile.id,
            title="Neo Tokyo VFX Hologram",
            description="Procedural 3D hologram sequence rendered with custom Blender depth passes.",
            file_path="/uploads/creators/2/neo_tokyo_vfx.svg",
            original_filename="neo_tokyo_vfx.svg",
            mime_type="image/svg+xml",
            file_size=1024,
            content_type="Animation",
            aspect_ratio="16:9",
            format="MP4",
            tools_models="ComfyUI, Blender",
            skills="AI Animation, 3D Projection",
            specialization="AI Animation",
            tags="Hologram, 3D, VFX",
            workflow="Blender camera tracking passed to ComfyUI node pipeline.",
            is_pinned=False,
            pin_order=0,
            views_count=520
        )

        # Aria (2 works, 1 pinned)
        p6 = PortfolioItem(
            creator_id=c3_profile.id,
            title="Aura L'Eau: Luxury Fragrance Key Visuals",
            description="Global perfume campaign visuals featuring crystalline water refraction and botanical flourishes.",
            file_path="/uploads/creators/3/luxury_perfume.svg",
            original_filename="luxury_perfume.svg",
            mime_type="image/svg+xml",
            file_size=1024,
            content_type="Image",
            aspect_ratio="1:1",
            format="PNG",
            tools_models="Midjourney v6, Flux.1",
            skills="Product Photography, Lighting Control",
            specialization="Generative Advertising",
            tags="Luxury, Perfume, Cosmetics, Studio",
            workflow="Custom stylized prompt matrices with in-painted typography zones.",
            is_pinned=True,
            pin_order=1,
            views_count=1120
        )
        p7 = PortfolioItem(
            creator_id=c3_profile.id,
            title="Haute Couture Mirage",
            description="Parisian fashion week editorial generated with fine-tuned fabric texture LoRAs.",
            file_path="/uploads/creators/3/haute_couture.svg",
            original_filename="haute_couture.svg",
            mime_type="image/svg+xml",
            file_size=1024,
            content_type="Image",
            aspect_ratio="9:16",
            format="PNG",
            tools_models="Flux.1, Photoshop",
            skills="Brand Identity, Lighting Control",
            specialization="Generative Advertising",
            tags="Fashion, Editorial, High-Resolution",
            workflow="LoRA training on silk/lace textures with high-pass frequency refinement.",
            is_pinned=False,
            pin_order=0,
            views_count=710
        )

        # Devon (2 works, 1 pinned)
        p8 = PortfolioItem(
            creator_id=c4_profile.id,
            title="DTC Energy Drink: 3-Second Viral Hook",
            description="High-dopamine vertical video ad with explosive fruit graphics and dynamic sound sync.",
            file_path="/uploads/creators/4/social_hook_reel.svg",
            original_filename="social_hook_reel.svg",
            mime_type="image/svg+xml",
            file_size=1024,
            content_type="Video",
            aspect_ratio="9:16",
            format="MP4",
            tools_models="Runway Gen-3, ElevenLabs",
            skills="Short-form Video, Hook Pacing",
            specialization="Social Media Creatives",
            tags="Reels, TikTok, Viral, Beverage",
            workflow="Fast-paced cuts with synchronized ElevenLabs voice acting.",
            is_pinned=True,
            pin_order=1,
            views_count=650
        )
        p9 = PortfolioItem(
            creator_id=c4_profile.id,
            title="Z-Sugar Soda Pop Splash",
            description="Hyper-saturated carbonated liquid simulation for TikTok spark ads.",
            file_path="/uploads/creators/4/beverage_viral_loop.svg",
            original_filename="beverage_viral_loop.svg",
            mime_type="image/svg+xml",
            file_size=1024,
            content_type="Video",
            aspect_ratio="9:16",
            format="MP4",
            tools_models="Pika Labs, Midjourney v6",
            skills="Hook Pacing, Motion Design",
            specialization="Social Media Creatives",
            tags="TikTok, Ads, Beverage",
            workflow="Pika Labs liquid particle simulation with custom motion vectors.",
            is_pinned=False,
            pin_order=0,
            views_count=480
        )

        db.add_all([p1, p2, p3, p4, p5, p6, p7, p8, p9])

        # Verification Signals
        v1 = VerificationSignal(creator_id=c1_profile.id, signal_type="tool_verified", badge_name="Runway Gen-3 Master", description="Verified mastery in generative video camera movement and motion prompting.")
        v2 = VerificationSignal(creator_id=c1_profile.id, signal_type="commercial_ready", badge_name="Commercial Grade Verified", description="Delivers broadcast-compliant 4K assets with cleared IP rights.")
        v3 = VerificationSignal(creator_id=c2_profile.id, signal_type="tool_verified", badge_name="ComfyUI Specialist", description="Verified technical proficiency in repeatable node-based generative workflows.")
        v4 = VerificationSignal(creator_id=c3_profile.id, signal_type="commercial_ready", badge_name="Luxury Brand Approved", description="Demonstrated high-end editorial and commercial product rendering.")
        db.add_all([v1, v2, v3, v4])

        # Company Profiles (Distinct structure: Logo, Location, Socials)
        comp1 = CompanyProfile(
            user_id=comp1_user.id,
            company_name="OmniSport Global",
            industry="Athletic Apparel & Footwear",
            description="Global leader in performance athletics, street fashion, and generative virtual experiences.",
            website="https://omnisport.example.com",
            location="Bengaluru, India & Beaverton, OR",
            logo_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=240",
            social_links=json.dumps({
                "website": "https://omnisport.example.com",
                "linkedin": "https://linkedin.com/company/omnisport-global",
                "twitter": "https://x.com/omnisport"
            }),
            tags="Footwear, Apparel, Sports, Innovation"
        )

        comp2 = CompanyProfile(
            user_id=comp2_user.id,
            company_name="Lumina Creative Agency",
            industry="Creative Production & Advertising",
            description="Boutique creative agency designing breakthrough AI campaigns and digital virtual worlds for enterprises.",
            website="https://luminacreative.example.com",
            location="Mumbai, India & London",
            logo_url="https://images.unsplash.com/photo-1572044162444-ad60f128bdea?w=240",
            social_links=json.dumps({
                "website": "https://luminacreative.example.com",
                "linkedin": "https://linkedin.com/company/lumina-creative",
                "twitter": "https://x.com/lumina_ai_ads"
            }),
            tags="Agency, Advertising, Brand, Production"
        )

        db.add_all([comp1, comp2])
        db.commit()

        # Company Reviews for Creators (Reviewer Feature)
        r1 = CreatorReview(
            creator_id=c1_profile.id,
            company_id=comp1.id,
            rating=5,
            project_title="Quantum Sneaker 4K Commercial",
            comment="Elena exceeded every expectation. Her Runway Gen-3 prompt control and 60fps upscaling made the shoe look hyper-realistic. Zero revisions required on camera motion.",
            tools_used="Runway Gen-3 + Topaz Video AI",
            is_verified_engagement=True
        )
        r2 = CreatorReview(
            creator_id=c2_profile.id,
            company_id=comp2.id,
            rating=5,
            project_title="Cyberpunk Virtual Stage Backdrop",
            comment="Marcus delivers repeatable node-based quality with ComfyUI. The Blender camera tracking gave our live stream an authentic 3D spatial presence.",
            tools_used="ComfyUI + Blender",
            is_verified_engagement=True
        )
        r3 = CreatorReview(
            creator_id=c3_profile.id,
            company_id=comp2.id,
            rating=5,
            project_title="Luxury Perfume Key Visuals",
            comment="Aria has an extraordinary eye for lighting and luxury aesthetics. The Midjourney v6 + Flux.1 rendering was clean enough for 8K billboard printing.",
            tools_used="Midjourney v6 + Flux.1",
            is_verified_engagement=True
        )
        db.add_all([r1, r2, r3])

        # Creator Connections (Reviewer Feature)
        conn1 = CreatorConnection(
            requester_id=c1_profile.id,
            receiver_id=c2_profile.id,
            status="accepted"
        )
        conn2 = CreatorConnection(
            requester_id=c1_profile.id,
            receiver_id=c3_profile.id,
            status="accepted"
        )
        conn3 = CreatorConnection(
            requester_id=c4_profile.id,
            receiver_id=c1_profile.id,
            status="pending"
        )
        db.add_all([conn1, conn2, conn3])

        # Jobs / Creative Briefs (Primary INR Budgets)
        j1 = Job(
            company_id=comp1.id,
            title="Cinematic AI Video Campaign: Quantum Sneaker Launch",
            description="We are seeking an elite AI Video Director to create a 30-second hero commercial introducing the Quantum-1 running shoe. The video must feature surreal gravity-defying urban environments and high-velocity motion.",
            campaign_requirements="1. 30s Master Video in 16:9 4K.\n2. Three 10s cutdowns for Instagram/TikTok (9:16).\n3. Storyboard review prior to final render.\n4. Full commercial buyout.",
            content_type="Video",
            style="Cinematic & Hyper-Realistic",
            format="MP4",
            aspect_ratio="16:9",
            commercial_use="Full Commercial Buyout",
            required_skills="AI Video Generation, Prompt Engineering, Motion Design",
            required_tools="Runway Gen-3, Kling AI, Topaz Video AI",
            specialization="AI Video",
            budget_range="₹3,50,000 - ₹5,00,000",
            budget_inr=420000,
            status="published"
        )

        j2 = Job(
            company_id=comp2.id,
            title="Generative Social Video Hooks: Energy Drink Campaign",
            description="Looking for an AI content creator to design 10 punchy, high-energy 9:16 vertical video concepts for a new zero-sugar beverage.",
            campaign_requirements="Fast pacing, eye-catching visual hooks in the first 2 seconds, synchronized sound effects.",
            content_type="Video",
            style="High-Energy Social Hook",
            format="MP4",
            aspect_ratio="9:16",
            commercial_use="Digital & Social Media Buyout",
            required_skills="Short-form Video, Hook Pacing, Sound Design",
            required_tools="Runway, Midjourney, Pika Labs",
            specialization="Social Media Creatives",
            budget_range="₹1,80,000 - ₹3,00,000",
            budget_inr=220000,
            status="published"
        )

        j3 = Job(
            company_id=comp2.id,
            title="Surreal Sci-Fi 3D Environment Backgrounds",
            description="Seeking an AI artist capable of generating 5 seamless looping ambient scifi backgrounds for a live-stream event.",
            campaign_requirements="Seamless looping, 16:9 60fps output, anime/cyberpunk aesthetic.",
            content_type="Animation",
            style="Stylized Cyberpunk",
            format="MP4",
            aspect_ratio="16:9",
            commercial_use="Online Live Event Rights",
            required_skills="AI Animation, 3D Camera Projection",
            required_tools="Stable Diffusion XL, ComfyUI, AnimateDiff",
            specialization="AI Animation",
            budget_range="₹95,000 - ₹1,50,000",
            budget_inr=120000,
            status="published"
        )

        db.add_all([j1, j2, j3])
        db.commit()

        # Sample Engagement
        eng1 = Engagement(
            company_id=comp1.id,
            creator_id=c1_profile.id,
            job_id=j1.id,
            status="pending",
            message="Hi Elena, your 'Nike Velocity' portfolio work is outstanding. We would love to collaborate on our upcoming Quantum Sneaker hero film.",
            proposed_budget="₹4,20,000"
        )
        db.add(eng1)
        db.commit()

        print("Database successfully seeded with realistic marketplace data!")
        seed_advanced_indexes(db)

    finally:
        if should_close:
            db.close()

if __name__ == "__main__":
    seed_database()

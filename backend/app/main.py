import os
import csv
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.database import engine, Base, SessionLocal
from backend.app.models.cpse import CPSE
from backend.app.models.material import Material
from backend.app.services.preprocessing import normalize_text
from backend.app.services.attribute_extraction import extract_attributes_regex
from backend.app.services.embeddings import compute_embedding
from backend.app.services.clustering import run_entity_resolution_pipeline
from backend.app.services.audit import log_action

from backend.app.api.materials import router as materials_router
from backend.app.api.matches import router as matches_router
from backend.app.api.common_materials import router as common_materials_router
from backend.app.api.audit import router as audit_router
from backend.app.api.analytics import router as analytics_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ekmat.main")

app = FastAPI(
    title="EkMat API — Material Standardization and Harmonization Platform for CPSEs",
    description="Central Public Sector Enterprises Master Data Standardization and Entity Resolution Platform",
    version=settings.VERSION,
)

# Enable CORS for local Vite dev server and containerized frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(materials_router, prefix="/api/materials", tags=["Materials"])
app.include_router(matches_router, prefix="/api/matches", tags=["Match Review"])
app.include_router(common_materials_router, prefix="/api/common-materials", tags=["Material Master"])
app.include_router(audit_router, prefix="/api/audit-log", tags=["Audit Trail"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics & KPIs"])


DEFAULT_CPSES = [
    ("BHEL", "Bharat Heavy Electricals Limited", "SAP ECC"),
    ("ONGC", "Oil and Natural Gas Corporation", "SAP S/4HANA"),
    ("GAIL", "Gas Authority of India Limited", "SAP ECC"),
    ("NTPC", "National Thermal Power Corporation", "SAP S/4HANA"),
    ("SAIL", "Steel Authority of India Limited", "SAP ECC"),
]

def seed_initial_data():
    """
    Automatically creates database tables, CPSE entities, and imports
    the seed dataset on initial launch so the application is immediately demo-ready.
    """
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Seed CPSEs
        cpse_map = {}
        for code, name, erp in DEFAULT_CPSES:
            c = db.query(CPSE).filter(CPSE.code == code).first()
            if not c:
                c = CPSE(code=code, name=name, erp_system=erp)
                db.add(c)
                db.flush()
            cpse_map[code] = c.id
        db.commit()

        # 2. Seed Materials if empty
        existing_mats = db.query(Material).count()
        if existing_mats == 0:
            seed_csv = os.path.join(os.path.dirname(__file__), "../../data/seed/cpse_seed.csv")
            if os.path.exists(seed_csv):
                logger.info(f"Seeding synthetic materials from {seed_csv}...")
                with open(seed_csv, mode="r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    count = 0
                    for row in reader:
                        cpse_code = (row.get("cpse") or "").strip().upper()
                        mat_code = (row.get("material_code") or "").strip()
                        desc = (row.get("description") or "").strip()
                        spec = (row.get("specification") or "").strip()
                        unit = (row.get("unit") or "NOS").strip().upper()
                        cat = (row.get("category") or "GEN").strip().upper()

                        if cpse_code in cpse_map and mat_code:
                            norm = normalize_text(f"{desc} {spec}")
                            attrs = extract_attributes_regex(desc, spec)
                            emb = compute_embedding(norm)
                            m = Material(
                                cpse_id=cpse_map[cpse_code],
                                original_code=mat_code,
                                raw_description=desc,
                                raw_specification=spec,
                                unit_of_measure=unit,
                                category=cat,
                                normalized_description=norm,
                                extracted_attributes=attrs,
                                embedding=emb
                            )
                            db.add(m)
                            count += 1
                    db.commit()
                    logger.info(f"Seeded {count} materials.")

                    # Run matching engine automatically so candidate clusters are ready for review
                    logger.info("Executing initial AI entity resolution pipeline...")
                    res = run_entity_resolution_pipeline(db)
                    logger.info(f"Matching pipeline completed: {res}")
    except Exception as e:
        logger.error(f"Error during initial seed: {e}")
        db.rollback()
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    seed_initial_data()


@app.get("/")
def root():
    return {
        "platform": "EkMat Master Data Harmonization Platform",
        "description": "Central Public Sector Enterprises Material Master Harmonization Platform",
        "status": "online",
        "docs_url": "/docs",
        "api_v1": "/api"
    }

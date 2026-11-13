import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend import config
from backend.database import Base, SessionLocal, engine
from backend.models import AIModelVersion, User
from backend.routers import admin, auth, health, inspections, parts
from backend.security import hash_password

app = FastAPI(
    title="MEX | Intelligent Vision AI",
    description="Plataforma industrial de inspecao inteligente por visao computacional",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(parts.router)
app.include_router(inspections.router)
app.include_router(admin.router)

frontend_dir = os.path.join(config.BASE_DIR, "frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


def bootstrap():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == config.DEFAULT_ADMIN_USER).first():
            db.add(
                User(
                    username=config.DEFAULT_ADMIN_USER,
                    password_hash=hash_password(config.DEFAULT_ADMIN_PASSWORD),
                    role="admin",
                    full_name="Administrador MEX",
                )
            )
            db.commit()
        if not db.query(AIModelVersion).filter(AIModelVersion.active.is_(True)).first():
            db.add(
                AIModelVersion(
                    name="mex-vision",
                    version="orb-1.0.0",
                    engine_type="orb_matching",
                    parameters={"max_features": 800, "ratio_test": 0.75, "histogram_bins": [32, 32]},
                    active=True,
                    notes="Motor inicial: ORB matching + histograma HSV com confianca calibrada",
                )
            )
            db.commit()
    finally:
        db.close()


bootstrap()

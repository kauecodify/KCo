import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
REFERENCE_DIR = os.path.join(IMAGES_DIR, "reference")
CAPTURES_DIR = os.path.join(IMAGES_DIR, "captures")

DATABASE_URL = os.environ.get("MEX_DATABASE_URL", "sqlite:///" + os.path.join(DATA_DIR, "mex.db"))

JWT_SECRET = os.environ.get("MEX_JWT_SECRET", "change-me-in-production-mex-secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.environ.get("MEX_JWT_EXPIRE_MINUTES", "720"))

DEFAULT_ADMIN_USER = os.environ.get("MEX_ADMIN_USER", "admin")
DEFAULT_ADMIN_PASSWORD = os.environ.get("MEX_ADMIN_PASSWORD", "mex-admin-2024")

MAX_UPLOAD_BYTES = int(os.environ.get("MEX_MAX_UPLOAD_BYTES", str(8 * 1024 * 1024)))

INFERENCE_P95_TARGET_MS = 2000
FULL_FLOW_P95_TARGET_MS = 3000

MIN_MATCH_THRESHOLD = float(os.environ.get("MEX_MIN_MATCH_THRESHOLD", "0.35"))
AMBER_THRESHOLD = float(os.environ.get("MEX_AMBER_THRESHOLD", "0.55"))
DEFAULT_APPROVAL_CONFIDENCE = float(os.environ.get("MEX_DEFAULT_APPROVAL_CONFIDENCE", "0.80"))

HUMAN_REVIEW_THRESHOLD = float(os.environ.get("MEX_HUMAN_REVIEW_THRESHOLD", "0.92"))

RETENTION_DAYS = int(os.environ.get("MEX_RETENTION_DAYS", "90"))

CORS_ORIGINS = os.environ.get("MEX_CORS_ORIGINS", "*").split(",")

for directory in (DATA_DIR, IMAGES_DIR, REFERENCE_DIR, CAPTURES_DIR):
    os.makedirs(directory, exist_ok=True)

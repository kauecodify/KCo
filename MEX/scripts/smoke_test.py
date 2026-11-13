import io
import shutil
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import cv2
import numpy as np
from fastapi.testclient import TestClient

for stale in (ROOT / "data" / "mex.db", ROOT / "data" / "images"):
    if stale.is_dir():
        shutil.rmtree(stale)
    elif stale.exists():
        stale.unlink()

from backend.main import app
from scripts.seed import seed

seed()

client = TestClient(app)

failures = []


def check(name, condition, detail=""):
    mark = "PASS" if condition else "FAIL"
    print(f"[{mark}] {name} {detail}")
    if not condition:
        failures.append(name)


r = client.get("/api/health")
check("health", r.status_code == 200 and r.json()["status"] == "ok", r.text[:120])

r = client.post("/api/auth/login", json={"username": "admin", "password": "mex-admin-2024"})
check("login admin", r.status_code == 200, r.text[:120])
admin_token = r.json()["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}

r = client.post("/api/auth/login", json={"username": "admin", "password": "errada"})
check("login invalido rejeitado", r.status_code == 401)

r = client.get("/api/parts", headers=admin_headers)
check("listar pecas", r.status_code == 200 and len(r.json()) >= 3, f"{len(r.json())} pecas")
part = next(p for p in r.json() if p["code"] == "ENG-ENG16-MX")

r = client.get("/api/parts", headers={"Authorization": "Bearer token-invalido"})
check("token invalido rejeitado", r.status_code == 401)

test_code = f"TES-{uuid.uuid4().hex[:6].upper()}-MX"
r = client.post(
    "/api/parts",
    headers=admin_headers,
    json={"code": test_code, "name": "Peca de teste", "category": "teste"},
)
check("criar peca", r.status_code == 201, r.text[:120])
test_part_id = r.json()["id"]

ref_path = str(Path(__file__).resolve().parents[1] / "data" / "images" / "reference" / "ENG-ENG16-MX_seed0.jpg")
with open(ref_path, "rb") as f:
    ref_bytes = f.read()
r = client.post(
    f"/api/parts/{test_part_id}/images",
    headers=admin_headers,
    files={"file": ("ref.jpg", io.BytesIO(ref_bytes), "image/jpeg")},
)
check("upload imagem referencia", r.status_code == 201, r.text[:120])

img = cv2.imread(ref_path)
img = cv2.resize(img, (800, 800))
img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
img = cv2.convertScaleAbs(img, alpha=1.05, beta=8)
ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 85])
jpeg = buf.tobytes()

t0 = time.perf_counter()
r = client.post(
    "/api/inspections",
    headers=admin_headers,
    files={"file": ("capture.jpg", io.BytesIO(jpeg), "image/jpeg")},
    data={"capture_ms": 120.0, "upload_ms": 180.0, "device_info": "smoke-test"},
)
elapsed = (time.perf_counter() - t0) * 1000
check("inspecao peca conhecida", r.status_code == 201, r.text[:200])
body = r.json()
check("identificacao correta", body["part_code"] == test_code, f"got {body['part_code']}")
check("status GREEN", body["status"] == "GREEN", f"status={body['status']} conf={body['confidence']}")
check("latencia registrada", "inference_ms" in body["latency_ms"])
print(f"    inferencia servidor: {body['latency_ms']['inference_ms']} ms (alvo p95 < 2000 ms)")

r = client.post(
    "/api/inspections",
    headers=admin_headers,
    files={"file": ("unknown.jpg", io.BytesIO(jpeg[:20000] + jpeg[-20000:]), "image/jpeg")},
)
check("inspecao executada com imagem degradada", r.status_code in (201, 400), r.text[:150])

noise = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
ok, buf = cv2.imencode(".jpg", noise)
r = client.post(
    "/api/inspections",
    headers=admin_headers,
    files={"file": ("noise.jpg", io.BytesIO(buf.tobytes()), "image/jpeg")},
)
check("peca nao identificada -> GRAY", r.status_code == 201 and r.json()["status"] == "GRAY", r.text[:200])

r = client.get("/api/inspections?limit=10", headers=admin_headers)
check("historico", r.status_code == 200 and len(r.json()) >= 2, f"{len(r.json())} inspecoes")
inspection_id = r.json()[0]["id"]

r = client.post(
    f"/api/inspections/{inspection_id}/review",
    headers=admin_headers,
    json={"decision": "approved", "note": "ok"},
)
check("revisao aplicada ou rejeitada com 400 para GREEN", r.status_code in (200, 400))

r = client.get("/api/admin/metrics", headers=admin_headers)
check("metricas p95", r.status_code == 200 and "latency" in r.json(), r.text[:150])

r = client.get("/api/admin/users", headers=admin_headers)
check("listar usuarios", r.status_code == 200 and len(r.json()) >= 1)

r = client.post(
    "/api/admin/users",
    headers=admin_headers,
    json={"username": "operador1", "password": "operador-2024", "role": "operator"},
)
check("criar operador", r.status_code == 201, r.text[:120])

r = client.post("/api/auth/login", json={"username": "operador1", "password": "operador-2024"})
check("login operador", r.status_code == 200)
op_headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

r = client.get("/api/admin/users", headers=op_headers)
check("RBAC: operador bloqueado em admin", r.status_code == 403)

r = client.post(
    "/api/parts",
    headers=op_headers,
    json={"code": "TES-0002-MX", "name": "Bloqueada", "category": "teste"},
)
check("RBAC: operador nao cria peca", r.status_code == 403)

r = client.get("/api/admin/audit", headers=admin_headers)
check("trilha de auditoria", r.status_code == 200 and len(r.json()) >= 3)

r = client.get("/api/metrics/prometheus")
check("export prometheus", r.status_code == 200 and "mex_latency_ms" in r.text)

r = client.get("/")
check("frontend servido", r.status_code == 200 and "MEX" in r.text)

print()
if failures:
    print(f"FALHAS: {failures}")
    sys.exit(1)
print("todos os testes passaram")

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cv2
import numpy as np

from backend.database import Base, SessionLocal, engine
from backend.models import Part, PartImage, User
from backend.security import hash_password


def draw_gear(size=640):
    img = np.zeros((size, size, 3), dtype=np.uint8)
    img[:] = (200, 195, 190)
    center = (size // 2, size // 2)
    teeth = 16
    for i in range(teeth):
        angle = 2 * np.pi * i / teeth
        x = int(center[0] + 230 * np.cos(angle))
        y = int(center[1] + 230 * np.sin(angle))
        cv2.circle(img, (x, y), 42, (60, 60, 65), -1)
    cv2.circle(img, center, 200, (90, 90, 95), -1)
    cv2.circle(img, center, 80, (200, 195, 190), -1)
    cv2.circle(img, center, 80, (40, 40, 45), 6)
    for i in range(6):
        angle = 2 * np.pi * i / 6
        x = int(center[0] + 140 * np.cos(angle))
        y = int(center[1] + 140 * np.sin(angle))
        cv2.circle(img, (x, y), 14, (40, 40, 45), -1)
    return img


def draw_hex_bushing(size=640):
    img = np.zeros((size, size, 3), dtype=np.uint8)
    img[:] = (190, 185, 180)
    center = (size // 2, size // 2)
    pts = []
    for i in range(6):
        angle = np.pi / 6 + 2 * np.pi * i / 6
        pts.append([int(center[0] + 220 * np.cos(angle)), int(center[1] + 220 * np.sin(angle))])
    cv2.fillPoly(img, [np.array(pts)], (70, 130, 180))
    cv2.circle(img, center, 90, (190, 185, 180), -1)
    cv2.circle(img, center, 90, (30, 30, 35), 8)
    for i in range(6):
        angle = 2 * np.pi * i / 6
        x = int(center[0] + 150 * np.cos(angle))
        y = int(center[1] + 150 * np.sin(angle))
        cv2.circle(img, (x, y), 10, (30, 30, 35), -1)
    return img


def draw_plate(size=640):
    img = np.zeros((size, size, 3), dtype=np.uint8)
    img[:] = (185, 180, 175)
    cv2.rectangle(img, (90, 220), (550, 420), (50, 140, 60), -1)
    cv2.rectangle(img, (90, 220), (550, 420), (25, 25, 30), 6)
    for x in (150, 250, 390, 490):
        cv2.circle(img, (x, 270), 18, (185, 180, 175), -1)
        cv2.circle(img, (x, 270), 18, (25, 25, 30), 4)
        cv2.circle(img, (x, 370), 18, (185, 180, 175), -1)
        cv2.circle(img, (x, 370), 18, (25, 25, 30), 4)
    cv2.putText(img, "MEX", (280, 335), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (200, 220, 200), 3)
    return img


def add_noise(img):
    noisy = img.astype(np.int16)
    noisy += np.random.randint(-14, 14, noisy.shape, dtype=np.int16)
    return np.clip(noisy, 0, 255).astype(np.uint8)


SAMPLES = [
    {
        "code": "ENG-ENG16-MX",
        "name": "Engrenagem 16 dentes",
        "category": "transmissao",
        "description": "Engrenagem cilindrica reta, aco 1045, para redutor industrial",
        "specifications": {"material": "ACO 1045", "modulo": 4.0, "dentes": 16, "dureza_hrc": "45-50"},
        "dimensions": "OD 240 mm x espessura 40 mm",
        "tolerances": "OD +/- 0.05 mm",
        "approval_criteria": {"min_confidence": 0.80},
        "generator": draw_gear,
    },
    {
        "code": "BUJ-HEX12-MX",
        "name": "Buje hexagonal 12 pol",
        "category": "fixacao",
        "description": "Buje de fixacao hexagonal zincado para eixo de convoyor",
        "specifications": {"material": "ACO zincado", "chave": "12 pol", "rosca": "M20"},
        "dimensions": "A/F 55 mm x altura 60 mm",
        "tolerances": "A/F +/- 0.10 mm",
        "approval_criteria": {"min_confidence": 0.78},
        "generator": draw_hex_bushing,
    },
    {
        "code": "PLA-RECT80-MX",
        "name": "Placa de montagem 80x40",
        "category": "estrutural",
        "description": "Placa de montagem retangular com 8 furos passantes",
        "specifications": {"material": "ACO galvanizado", "furos": 8, "acabamento": "galvanizado a fogo"},
        "dimensions": "460 x 200 x 5 mm",
        "tolerances": "Furos +/- 0.2 mm",
        "approval_criteria": {"min_confidence": 0.75},
        "generator": draw_plate,
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(User).filter_by(username="admin").first():
            db.add(User(username="admin", password_hash=hash_password("mex-admin-2024"), role="admin"))
            db.commit()

        from backend import config

        for sample in SAMPLES:
            if db.query(Part).filter_by(code=sample["code"]).first():
                continue
            part = Part(
                code=sample["code"],
                name=sample["name"],
                category=sample["category"],
                description=sample["description"],
                specifications=sample["specifications"],
                dimensions=sample["dimensions"],
                tolerances=sample["tolerances"],
                approval_criteria=sample["approval_criteria"],
                version_history=[{"version": 1, "action": "criacao", "by": "seed"}],
            )
            db.add(part)
            db.commit()
            db.refresh(part)
            for variant in range(3):
                img = sample["generator"]()
                if variant > 0:
                    img = add_noise(img)
                    scale = 1.0 + variant * 0.06
                    img = cv2.resize(img, None, fx=scale, fy=scale)
                filename = f"{part.code}_seed{variant}.jpg"
                path = str(Path(config.REFERENCE_DIR) / filename)
                cv2.imwrite(path, img, [cv2.IMWRITE_JPEG_QUALITY, 92])
                db.add(PartImage(part_id=part.id, path=path, is_primary=(variant == 0)))
            db.commit()
            print(f"peca cadastrada: {part.code} - {part.name}")
        print("seed concluido")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

import math
import os
import threading

import cv2
import numpy as np

from backend import config
from backend.services.image_validation import validate_image

MAX_FEATURES = 800
RATIO_TEST = 0.75
GOOD_MATCH_FLOOR = 12
HIST_BINS = [32, 32]
ENGINE_WEIGHTS = {"match": 0.75, "histogram": 0.25}

_orb = cv2.ORB_create(nfeatures=MAX_FEATURES, scaleFactor=1.2, nlevels=8)
_matcher = cv2.BFMatcher(cv2.NORM_HAMMING)


def extract_features(image: np.ndarray) -> dict:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    keypoints, descriptors = _orb.detectAndCompute(gray, None)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    histogram = cv2.calcHist([hsv], [0, 1], None, HIST_BINS, [0, 180, 0, 256])
    cv2.normalize(histogram, histogram)
    edges = cv2.Canny(gray, 80, 180)
    edge_density = float((edges > 0).sum()) / float(gray.size)
    return {
        "descriptors": descriptors,
        "keypoint_count": len(keypoints),
        "histogram": histogram,
        "edge_density": edge_density,
        "size": (int(image.shape[1]), int(image.shape[0])),
    }


def _match_score(captured: dict, reference: dict) -> float:
    cap_desc = captured.get("descriptors")
    ref_desc = reference.get("descriptors")
    if cap_desc is None or ref_desc is None or len(cap_desc) < 4 or len(ref_desc) < 4:
        return 0.0
    matches = _matcher.knnMatch(cap_desc, ref_desc, k=2)
    good = 0
    for pair in matches:
        if len(pair) == 2 and pair[0].distance < RATIO_TEST * pair[1].distance:
            good += 1
    match_ratio = good / max(GOOD_MATCH_FLOOR, min(len(cap_desc), len(ref_desc)) / 4.0)
    match_ratio = min(match_ratio, 1.0)
    hist_sim = float(cv2.compareHist(captured["histogram"], reference["histogram"], cv2.HISTCMP_CORREL))
    hist_sim = max(0.0, min(1.0, (hist_sim + 1.0) / 2.0))
    return ENGINE_WEIGHTS["match"] * match_ratio + ENGINE_WEIGHTS["histogram"] * hist_sim


def calibrate_confidence(raw_score: float) -> float:
    midpoint = 0.55
    steepness = 11.0
    confidence = 1.0 / (1.0 + math.exp(-steepness * (raw_score - midpoint)))
    return round(max(0.0, min(1.0, confidence)), 4)


class ReferenceStore:
    def __init__(self):
        self._lock = threading.Lock()
        self._cache: dict[int, dict] = {}

    def load(self, db) -> list[dict]:
        from backend.models import Part, PartImage

        with self._lock:
            references = []
            parts = db.query(Part).filter(Part.active.is_(True)).all()
            cached_ids = set(self._cache.keys())
            current_ids = set()
            for part in parts:
                ref_entries = []
                for image in part.images:
                    current_ids.add(image.id)
                    if image.id in self._cache and self._cache[image.id]["path"] == image.path:
                        ref_entries.append(self._cache[image.id])
                        continue
                    if not os.path.exists(image.path):
                        continue
                    loaded = cv2.imread(image.path)
                    if loaded is None:
                        continue
                    entry = {
                        "image_id": image.id,
                        "path": image.path,
                        "features": extract_features(loaded),
                    }
                    ref_entries.append(entry)
                    self._cache[image.id] = entry
                if ref_entries:
                    references.append(
                        {
                            "part_id": part.id,
                            "code": part.code,
                            "name": part.name,
                            "category": part.category,
                            "approval_criteria": part.approval_criteria or {},
                            "images": ref_entries,
                        }
                    )
            for stale_id in cached_ids - current_ids:
                self._cache.pop(stale_id, None)
            return references


reference_store = ReferenceStore()


class OrbMatchingEngine:
    engine_type = "orb_matching"
    version = "1.0.0"

    def identify(self, image: np.ndarray, references: list[dict]) -> dict:
        validation = validate_image(image)
        captured = extract_features(image)
        best = {"score": 0.0, "reference": None}
        for reference in references:
            score = max(_match_score(captured, ref_entry["features"]) for ref_entry in reference["images"])
            if score > best["score"]:
                best = {"score": score, "reference": reference}

        divergences = list(validation["divergences"])
        raw_score = best["score"]
        if raw_score < config.MIN_MATCH_THRESHOLD or best["reference"] is None:
            return {
                "status": "GRAY",
                "part_id": None,
                "part_code": "",
                "part_name": "",
                "confidence": calibrate_confidence(raw_score),
                "match_score": round(raw_score, 4),
                "divergences": divergences + ["peca nao identificada no cadastro"],
                "quality": validation["quality"],
            }

        reference = best["reference"]
        confidence = calibrate_confidence(raw_score)
        approval = reference.get("approval_criteria") or {}
        min_confidence = float(approval.get("min_confidence", config.DEFAULT_APPROVAL_CONFIDENCE))

        if confidence < min_confidence:
            divergences.append(
                f"confianca {confidence:.2f} abaixo do criterio de aprovacao ({min_confidence:.2f})"
            )

        if divergences:
            status = "RED" if any("borrada" in d or "ilegivel" in d for d in divergences) else "AMBER"
        elif confidence >= min_confidence:
            status = "GREEN"
        elif confidence >= config.AMBER_THRESHOLD:
            status = "AMBER"
        else:
            status = "RED"
            divergences.append("reprovada conforme regra cadastrada: similaridade insuficiente")

        return {
            "status": status,
            "part_id": reference["part_id"],
            "part_code": reference["code"],
            "part_name": reference["name"],
            "confidence": confidence,
            "match_score": round(raw_score, 4),
            "divergences": divergences,
            "quality": validation["quality"],
        }


class HistogramEngine(OrbMatchingEngine):
    engine_type = "histogram_only"
    version = "1.0.0"

    def identify(self, image: np.ndarray, references: list[dict]) -> dict:
        validation = validate_image(image)
        captured = extract_features(image)
        best = {"score": 0.0, "reference": None}
        for reference in references:
            score = max(
                float(cv2.compareHist(captured["histogram"], ref_entry["features"]["histogram"], cv2.HISTCMP_CORREL))
                for ref_entry in reference["images"]
            )
            score = max(0.0, min(1.0, (score + 1.0) / 2.0))
            if score > best["score"]:
                best = {"score": score, "reference": reference}

        divergences = list(validation["divergences"])
        raw_score = best["score"]
        if raw_score < config.MIN_MATCH_THRESHOLD or best["reference"] is None:
            return {
                "status": "GRAY",
                "part_id": None,
                "part_code": "",
                "part_name": "",
                "confidence": calibrate_confidence(raw_score),
                "match_score": round(raw_score, 4),
                "divergences": divergences + ["peca nao identificada no cadastro"],
                "quality": validation["quality"],
            }

        reference = best["reference"]
        confidence = calibrate_confidence(raw_score)
        min_confidence = float((reference.get("approval_criteria") or {}).get("min_confidence", config.DEFAULT_APPROVAL_CONFIDENCE))
        if confidence < min_confidence:
            divergences.append(f"confianca {confidence:.2f} abaixo do criterio de aprovacao ({min_confidence:.2f})")
        status = "GREEN" if confidence >= min_confidence and not divergences else "AMBER"
        return {
            "status": status,
            "part_id": reference["part_id"],
            "part_code": reference["code"],
            "part_name": reference["name"],
            "confidence": confidence,
            "match_score": round(raw_score, 4),
            "divergences": divergences,
            "quality": validation["quality"],
        }


ENGINES = {cls.engine_type: cls() for cls in (OrbMatchingEngine, HistogramEngine)}


def get_engine(engine_type: str = "orb_matching"):
    return ENGINES.get(engine_type, ENGINES["orb_matching"])

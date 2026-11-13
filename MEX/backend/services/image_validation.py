import cv2
import numpy as np

MIN_WIDTH = 200
MIN_HEIGHT = 200
BLUR_THRESHOLD = 60.0
BRIGHTNESS_RANGE = (35.0, 235.0)
GLARE_RATIO_MAX = 0.25


def decode_image(data: bytes) -> np.ndarray | None:
    array = np.frombuffer(data, dtype=np.uint8)
    return cv2.imdecode(array, cv2.IMREAD_COLOR)


def validate_image(image: np.ndarray) -> dict:
    divergences = []
    if image is None:
        return {"valid": False, "quality": {}, "divergences": ["imagem ilegivel ou corrompida"]}

    height, width = image.shape[:2]
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        divergences.append(f"resolucao insuficiente ({width}x{height})")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if blur_score < BLUR_THRESHOLD:
        divergences.append("imagem borrada ou fora de foco")

    brightness = float(gray.mean())
    if brightness < BRIGHTNESS_RANGE[0]:
        divergences.append("iluminacao insuficiente")
    elif brightness > BRIGHTNESS_RANGE[1]:
        divergences.append("iluminacao excessiva")

    glare_ratio = float((gray > 250).sum()) / float(gray.size)
    if glare_ratio > GLARE_RATIO_MAX:
        divergences.append("reflexo ou brilho excessivo na captura")

    quality = {
        "width": width,
        "height": height,
        "blur_score": round(blur_score, 1),
        "brightness": round(brightness, 1),
        "glare_ratio": round(glare_ratio, 4),
    }
    return {"valid": len(divergences) == 0, "quality": quality, "divergences": divergences}

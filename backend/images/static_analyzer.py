import os
import re
import io
from typing import Callable, Dict, List
<<<<<<< HEAD
from PIL import Image, ExifTags
import xml.etree.ElementTree as ET
import openai
import base64
import logging
import subprocess
import json
import tempfile
=======
>>>>>>> ed4f353 (images)

from PIL import Image, ExifTags, ImageChops, ImageOps
import xml.etree.ElementTree as ET
import openai
import base64
import logging
import subprocess
import json

# Optional imports
try:
    from dalle_watermark import WatermarkDecoder
    DALL_E_DECODER = WatermarkDecoder()
except ImportError:
    DALL_E_DECODER = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger("uvicorn.error")

class StaticImageAnalyzer:
    """Analyze images for static AI signatures before invoking any CNN."""

    def __init__(self):
        self.analyzers: List[Callable[[str], Dict]] = []
        for fn in (
<<<<<<< HEAD
            # self.detect_openai_api_watermark,  # Removed: not functional
=======
            self.detect_dalle_watermark,
            self.detect_openai_api_watermark,
>>>>>>> ed4f353 (images)
            self.detect_c2pa_metadata,
            self.detect_cr_symbol,
            self.detect_exif_metadata,
            self.detect_software_tag,
            self.detect_ocr_watermark,
            self.detect_c2pa_provenance,
        ):
            self.register_analyzer(fn)

    def register_analyzer(self, func: Callable[[str], Dict]):
        self.analyzers.append(func)

    def analyze(self, image_path: str) -> List[Dict]:
        logger.info(f"[StaticImageAnalyzer] Analyzing image: {image_path}")
        results = []
        for analyzer in self.analyzers:
            try:
                logger.info(f"[StaticImageAnalyzer] Running analyzer: {analyzer.__name__}")
                results.append(analyzer(image_path))
            except Exception as e:
                logger.error(f"[StaticImageAnalyzer] Error in {analyzer.__name__}: {e}")
                results.append({"analyzer": analyzer.__name__, "error": str(e)})
        return results

    @staticmethod
<<<<<<< HEAD
=======
    def detect_dalle_watermark(image_path: str) -> Dict:
        """
        Invisible watermark used by DALL·E 2 & 3 via the 'dalle_watermark' library.
        Returns a confidence score if found. :contentReference[oaicite:5]{index=5}
        """
        out = {"analyzer": "detect_dalle_watermark", "found": False}
        if DALL_E_DECODER is None:
            out["error"] = "dalle_watermark lib not installed"
            return out
        img = Image.open(image_path).convert("RGB")
        score = DALL_E_DECODER.decode(img)  # proprietary decoder
        out["score"] = float(score)
        out["found"] = score > 0.75
        return out

    @staticmethod
    def detect_openai_api_watermark(image_path: str) -> Dict:
        """
        Placeholder for OpenAI's official watermark detection API (launched May 2024) :contentReference[oaicite:6]{index=6}.
        Requires OPENAI_API_KEY in env. 
        """
        out = {"analyzer": "detect_openai_api_watermark", "found": False}
        if not OPENAI_AVAILABLE:
            out["error"] = "openai library not installed"
            return out
        try:
            with open(image_path, "rb") as f:
                resp = openai.images.provenance.checkwatermark(file=f)
            out.update({
                "found": resp.get("watermarked", False),
                "confidence": resp.get("confidence", None)
            })
        except Exception as e:
            out["error"] = str(e)
        return out

    @staticmethod
>>>>>>> ed4f353 (images)
    def detect_c2pa_metadata(image_path: str) -> Dict:
        """
        Scan for C2PA/XMP (invisible metadata) injected by DALL·E 3 :contentReference[oaicite:7]{index=7}:
          - looks for xmlns:c2pa, contentCredentials, softwareAgent, description fields.
        """
        out = {"analyzer": "detect_c2pa_metadata", "found": False, "details": {}}
        data = open(image_path, "rb").read(1024 * 1024)
        if b"xmlns:c2pa" in data or b"contentCredentials" in data:
            out["found"] = True
            # try to extract the XMP packet
            try:
                start = data.index(b"<x:xmpmeta")
                end = data.index(b"</x:xmpmeta>") + len(b"</x:xmpmeta>")
                xml = data[start:end]
                root = ET.fromstring(xml)
                # extract some key tags
                for desc in root.iter("{adobe:ns:meta/}Description"):
                    sa = desc.attrib.get("softwareAgent")
                    if sa:
                        out["details"]["softwareAgent"] = sa
                    d = desc.attrib.get("description")
                    if d:
                        out["details"]["description"] = d
            except Exception:
                pass
        return out

    @staticmethod
    def detect_cr_symbol(image_path: str) -> Dict:
        """
        OCR‐based detection of the visible '© CR' badge in top-left of DALL·E 3 images :contentReference[oaicite:8]{index=8}.
        """
        out = {"analyzer": "detect_cr_symbol", "found": False, "text": ""}
        try:
            img = Image.open(image_path)
            w, h = img.size
            # crop top-left 10% region
            crop = img.crop((0, 0, w // 10, h // 10))
            if pytesseract:
                txt = pytesseract.image_to_string(crop)
                out["text"] = txt.strip()
                if re.search(r"(©\s?CR|\bCR\b)", txt, re.IGNORECASE):
                    out["found"] = True
            else:
                out["error"] = "pytesseract not installed"
        except Exception as e:
            out["error"] = str(e)
        return out

    @staticmethod
    def detect_exif_metadata(image_path: str) -> Dict:
        """
        Inspect EXIF for hints (Software, Model, UserComment) containing AI keywords :contentReference[oaicite:9]{index=9}.
        """
        out = {"analyzer": "detect_exif_metadata", "ai_related": False, "tags": []}
        img = Image.open(image_path)
        exif = img.getexif()
        for tag_id, val in exif.items():
            name = ExifTags.TAGS.get(tag_id, tag_id)
            s = str(val)
            if re.search(r"(AI|STABLEDIFFUSION|DALL.?E|MIDJOURNEY)", s, re.IGNORECASE):
                out["ai_related"] = True
                out["tags"].append({name: s})
            elif name.lower() in ("software", "model", "usercomment"):
                out["tags"].append({name: s})
        return out

    @staticmethod
    def detect_software_tag(image_path: str) -> Dict:
        """
        EXIF Software tag heuristic for known editors & apps (Instagram, Midjourney) :contentReference[oaicite:10]{index=10}.
        """
        out = {"analyzer": "detect_software_tag", "found": False, "software": None}
        img = Image.open(image_path)
        exif = img.getexif()
        for tag_id, val in exif.items():
            name = ExifTags.TAGS.get(tag_id, tag_id)
            if name == "Software":
                soft = str(val)
                out["software"] = soft
                if any(app in soft for app in ["Instagram", "Facebook", "Midjourney", "DALL"]):
                    out["found"] = True
                break
        return out

    @staticmethod
    def detect_ocr_watermark(image_path: str) -> Dict:
        """
        OCR for visible text like 'Generated by AI', 'Courtesy of DALL·E', etc. :contentReference[oaicite:11]{index=11}.
        """
        out = {"analyzer": "detect_ocr_watermark", "found": False, "text": ""}
        if not pytesseract:
            out["error"] = "pytesseract not installed"
            return out
        img = Image.open(image_path)
        txt = pytesseract.image_to_string(img)
        out["text"] = txt.strip()
        if re.search(r"(Generated by|Midjourney|DALL\.?E|Stable Diffusion)", txt, re.IGNORECASE):
            out["found"] = True
        return out

    @staticmethod
    def detect_c2pa_provenance(image_path: str) -> Dict:
        """
        Uses the c2patool CLI to check for C2PA provenance and watermark info.
<<<<<<< HEAD
        Converts non-JPEG images to JPEG for compatibility.
        Handles 'No claim found' as a valid, non-error result.
        """
        logger = logging.getLogger(__name__)
        out = {"analyzer": "detect_c2pa_provenance", "found": False, "provenance": None, "error": None}
        temp_jpeg = None
        jpeg_path = image_path
        try:
            ext = os.path.splitext(image_path)[1].lower()
            if ext not in [".jpg", ".jpeg"]:
                # Convert to JPEG in a temp file
                with Image.open(image_path) as img:
                    rgb_img = img.convert("RGB")
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                    rgb_img.save(tmp, format="JPEG")
                    temp_jpeg = tmp.name
                    jpeg_path = temp_jpeg
                    logger.info(f"[C2PA provenance] Converted {image_path} to JPEG: {jpeg_path}")
            cmd = ["c2patool", jpeg_path, "--detailed"]
            logger.info(f"[C2PA provenance] Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True, text=True
            )
            logger.info(f"[c2patool output] {result.stdout}")
            if result.returncode != 0 and "No claim found" in (result.stderr or ""):
                out["found"] = False
                out["provenance"] = None
                out["error"] = "No C2PA claim found in image."
                logger.info(f"[C2PA provenance] No claim found in image.")
            elif result.returncode != 0:
                logger.warning(f"[C2PA provenance] c2patool CLI failed: {result.stderr} -- falling back to metadata scan.")
                meta = StaticImageAnalyzer.detect_c2pa_metadata(image_path)
                out["found"] = meta.get("found", False)
                out["provenance"] = meta.get("details")
            else:
                out["provenance"] = result.stdout
                out["found"] = bool(result.stdout.strip())
        except FileNotFoundError:
            out["error"] = "c2patool CLI not found. Please install c2patool and ensure it is in your PATH."
            logger.error("[C2PA provenance] c2patool CLI not found.")
        except Exception as e:
            out["error"] = str(e)
            logger.error(f"[C2PA provenance] Error: {e}")
        finally:
            if temp_jpeg:
                try:
                    os.remove(temp_jpeg)
                    logger.info(f"[C2PA provenance] Removed temp JPEG: {temp_jpeg}")
                except Exception as cleanup_e:
                    logger.warning(f"[C2PA provenance] Failed to remove temp JPEG: {cleanup_e}")
        return out
=======
        """
        logger = logging.getLogger(__name__)
        out = {"analyzer": "detect_c2pa_provenance", "found": False, "provenance": None, "error": None}
        try:
            cmd = ["c2patool", image_path, "--", "--json"]
            logger.info(f"[C2PA provenance] Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True, text=True, check=True
            )
            logger.info(f"[c2patool output] {result.stdout}")
            try:
                data = json.loads(result.stdout)
                if data.get("manifests"):
                    out["found"] = True
                    out["provenance"] = data["manifests"]
                else:
                    out["found"] = False
            except json.JSONDecodeError as je:
                out["error"] = f"Invalid JSON from c2patool: {je}"
                logger.error(f"[C2PA provenance] Invalid JSON: {je}\nOutput: {result.stdout}")
        except FileNotFoundError:
            out["error"] = "c2patool CLI not found. Please install c2patool and ensure it is in your PATH."
            logger.error("[C2PA provenance] c2patool CLI not found.")
        except subprocess.CalledProcessError as e:
            out["error"] = f"c2patool failed: {e.stderr}"
            logger.error(f"[C2PA provenance] c2patool failed: {e.stderr}")
        except Exception as e:
            out["error"] = str(e)
            logger.error(f"[C2PA provenance] Error: {e}")
        return out
>>>>>>> ed4f353 (images)

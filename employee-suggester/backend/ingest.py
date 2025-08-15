import io, re, os
from typing import Dict, List
import fitz  # PyMuPDF
from PIL import Image
import docx

# Optional: file type detection
try:
    import magic  # python-magic / python-magic-bin
except Exception:
    magic = None

# Optional: OCR
try:
    import pytesseract
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

from pdf2image import convert_from_bytes

# Heuristic heading keys to split sections
HEADINGS = [
    "summary", "profile", "objective",
    "skills", "technical skills", "key skills",
    "experience", "work experience", "professional experience",
    "projects", "project experience",
    "education", "certifications", "awards", "publications"
]

def _detect_type(content: bytes, filename: str) -> str:
    ext = os.path.splitext(filename.lower())[-1]
    if ext in [".pdf", ".docx", ".doc", ".txt"]:
        return ext.lstrip(".")
    if magic:
        try:
            mt = magic.Magic(mime=True)
            mime = mt.from_buffer(content)
            if mime == "application/pdf":
                return "pdf"
            if mime in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document",):
                return "docx"
            if mime in ("application/msword",):
                return "doc"
            if mime.startswith("text/"):
                return "txt"
        except Exception:
            pass
    if content[:5] == b"%PDF-":
        return "pdf"
    raise ValueError(f"Unsupported file type: {filename}")

def _normalize_bullets(text: str) -> str:
    # Normalize various bullet characters to a single form "• "
    text = re.sub(r"[•▪●■♦▶\-–—]+[ \t]*", "• ", text)
    return text

def _clean_text(text: str) -> str:
    text = re.sub(r"-\n(?=\w)", "", text)          # un-break hyphenated words across lines
    text = text.replace("\r", "")
    text = re.sub(r"[ \t]+", " ", text)            # collapse spaces
    text = re.sub(r"\n{3,}", "\n\n", text)         # collapse excessive newlines
    text = _normalize_bullets(text)
    return text.strip()

def _segment_sections(text: str) -> Dict[str, str]:
    # Case-insensitive, line-based segmentation using known headings
    lines = [ln.strip() for ln in text.split("\n")]
    sections: Dict[str, str] = {}
    current = "other"
    buf: List[str] = []

    heading_map = {h: h for h in HEADINGS}
    def normalize_key(ln: str) -> str:
        key = re.sub(r"[^a-z ]", "", ln.lower()).strip()
        return key

    def flush():
        nonlocal buf, current
        if buf:
            segment = "\n".join(buf).strip()
            if segment:
                sections[current] = (sections.get(current, "") + ("\n" if current in sections else "") + segment).strip()
            buf = []

    for ln in lines:
        key = normalize_key(ln)
        if key in heading_map:
            flush()
            current = key
        else:
            buf.append(ln)
    flush()
    return sections

def _parse_pdf(content: bytes, filename: str) -> Dict:
    doc = fitz.open("pdf", content)
    pages_text: List[str] = []
    char_count = 0
    for page in doc:
        t = page.get_text("text") or ""
        pages_text.append(t)
        char_count += len(t)

    is_scanned = (char_count < 50)  # very low extractable text
    warnings: List[str] = []
    text = "\n".join(pages_text).strip()

    if is_scanned:
        if not OCR_AVAILABLE:
            warnings.append("PDF appears scanned; OCR not available (install Tesseract). Proceeding without OCR.")
        else:
            try:
                # Convert pages to images, then OCR
                images = convert_from_bytes(content, dpi=300)
                ocr_texts = [pytesseract.image_to_string(img) for img in images]
                text = "\n".join(ocr_texts)
                warnings.append("Used OCR fallback")
            except Exception as e:
                warnings.append(f"OCR failed: {e}")

    text = _clean_text(text)
    sections = _segment_sections(text)
    return {
        "filename": filename,
        "filetype": "pdf",
        "pages": len(doc),
        "text": text,
        "sections": sections,
        "warnings": warnings
    }

def _parse_docx(content: bytes, filename: str) -> Dict:
    f = io.BytesIO(content)
    d = docx.Document(f)
    text = "\n".join(p.text for p in d.paragraphs)
    text = _clean_text(text)
    sections = _segment_sections(text)
    return {
        "filename": filename,
        "filetype": "docx",
        "pages": None,
        "text": text,
        "sections": sections,
        "warnings": []
    }

def _parse_doc(content: bytes, filename: str) -> Dict:
    # Legacy .doc is not supported here due to dependencies.
    # Suggest converting .doc -> .docx or .pdf using LibreOffice or online tools.
    raise ValueError("Legacy .doc is not supported. Please convert to .docx or .pdf, then re-upload.")

def _parse_txt(content: bytes, filename: str) -> Dict:
    text = content.decode("utf-8", errors="ignore")
    text = _clean_text(text)
    sections = _segment_sections(text)
    return {
        "filename": filename,
        "filetype": "txt",
        "pages": None,
        "text": text,
        "sections": sections,
        "warnings": []
    }

def parse_resume_file(content: bytes, filename: str) -> Dict:
    ftype = _detect_type(content, filename)
    if ftype == "pdf":
        return _parse_pdf(content, filename)
    if ftype == "docx":
        return _parse_docx(content, filename)
    if ftype == "doc":
        return _parse_doc(content, filename)
    if ftype == "txt":
        return _parse_txt(content, filename)
    raise ValueError(f"Unsupported resume type: {ftype}")

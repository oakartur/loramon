import os
import fitz # PyMuPDF
from pathlib import Path


FLOORPLAN_DIR = os.getenv("FLOORPLAN_DIR", "/app/app/static/floorplans")


Path(FLOORPLAN_DIR).mkdir(parents=True, exist_ok=True)


def save_pdf(file_bytes: bytes, filename: str) -> str:
 path = Path(FLOORPLAN_DIR) / filename
 with open(path, "wb") as f:
  f.write(file_bytes)
 return str(path)


def render_page_to_png(pdf_path: str, page_index: int = 0, scale: float = 2.0) -> str:
 doc = fitz.open(pdf_path)
 page = doc.load_page(page_index)
 mat = fitz.Matrix(scale, scale)
 pix = page.get_pixmap(matrix=mat)
 out_path = pdf_path.replace(".pdf", f"_p{page_index}.png")
 pix.save(out_path)
 return out_path

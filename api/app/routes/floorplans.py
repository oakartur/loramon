from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..deps import get_db
from ..utils import admin_required, auth_required
from ..services.pdf_render import save_pdf, render_page_to_png, FLOORPLAN_DIR
import os

router = APIRouter(prefix="/floorplans", tags=["floorplans"])
UPLOAD_DIR = Path("/app/app/static/floorplans")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload", dependencies=[Depends(admin_required)])
async def upload_floorplan(
 site_id: str = Form(...),
 name: str = Form(...),
 page_index: int = Form(0),
 file: UploadFile = File(...),
 db: AsyncSession = Depends(get_db)
):

 if not file.filename.endswith(".pdf"):
  raise HTTPException(400, "Apenas PDF")
 filename = file.filename
 content = await file.read()
 path = save_pdf(content, filename)
 png = render_page_to_png(path, page_index)
 q = text("""
  INSERT INTO app.floorplan(site_id,name,file_path,page_index,width_px,height_px)
  VALUES (:site_id,:name,:file_path,:page_index,NULL,NULL)
  RETURNING id
 """)
 res = await db.execute(q, {
  "site_id": site_id, "name": name, "file_path": path, "page_index": page_index
 })
 row = res.mappings().first()
 await db.commit()
 return {"id": row["id"], "file_url": f"/api/floorplans/image/{row['id']}"}

@router.get("/image/{floorplan_id}", dependencies=[Depends(auth_required)])
async def get_floorplan_image(floorplan_id: str, db: AsyncSession = Depends(get_db)):
 q = text("SELECT file_path, page_index FROM app.floorplan WHERE id=:id")
 res = await db.execute(q, {"id": floorplan_id})
 row = res.mappings().first()
 if not row:
  raise HTTPException(404)
 png_path = row["file_path"].replace(".pdf", f"_p{row['page_index']}.png")
 if not os.path.exists(png_path):
  png_path = render_page_to_png(row["file_path"], row["page_index"])
 # Retorna como arquivo estático (nginx pode servir no futuro). Aqui, FastAPI stream simples.
 from fastapi.responses import FileResponse
 return FileResponse(png_path)

@router.post("/upload")
async def upload_floorplan(
    site_id: int = Form(...),
    name: str = Form(...),
    file: UploadFile = File(...)
    , db = Depends(get_db)
):
    if file.content_type not in ("application/pdf",):
        raise HTTPException(400, "Envie um PDF.")
    fname = f"{uuid.uuid4()}.pdf"
    dest = UPLOAD_DIR / fname
    data = await file.read()
    dest.write_bytes(data)

    q = text("""
      insert into app.floorplan (site_id, name, file_path, mime_type)
      values (:site_id, :name, :path, 'application/pdf')
      returning id
    """)
    r = await db.execute(q, {"site_id": site_id, "name": name, "path": str(dest)})
    await db.commit()
    return {"id": r.scalar(), "name": name}

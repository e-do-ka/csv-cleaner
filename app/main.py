from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from ai import clean_csv
import pandas as pd
import io

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    # AIに全データを渡す
    ai_result = clean_csv(df)

    return {
        "filename": file.filename,
        "rows": len(df),
        "columns": list(df.columns),
        "preview": df.head(3).fillna("").to_dict(orient="records"),
        "ai_analysis": ai_result
    }

@app.get("/download")
async def download_csv(data: str):
    return Response(
        content=data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cleaned.csv"}
    )

app.mount("/", StaticFiles(directory="/static", html=True), name="static")
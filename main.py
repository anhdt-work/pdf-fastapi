from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import PyPDF2
import io
import uvicorn
import json

app = FastAPI(title="PDF to Text API")

@app.post("/extract-text/")
async def extract_text(file: UploadFile = File(...)):
    try:
        # Read the uploaded PDF file
        content = await file.read()
        pdf_file = io.BytesIO(content)
        
        # Create PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Read the result.json file
        with open('result.json', 'r', encoding='utf-8') as f:
            result_data = json.load(f)
        
        # Update SOTRANG with actual number of pages
        result_data['SOTRANG'] = len(pdf_reader.pages)
       
        return JSONResponse(result_data)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000) 
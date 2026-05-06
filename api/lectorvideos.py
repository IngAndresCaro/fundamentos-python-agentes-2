from fastapi import WebSocket, WebSocketDisconnect
import asyncio
"""
API para LectorVideos: Subida de videos, transcripción con Whisper, resumen, palabras clave y análisis.
"""


from fastapi import APIRouter, UploadFile, File, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid
import shutil
import tempfile
from starlette.background import BackgroundTask
import whisper
# Para resumen y palabras clave
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from collections import Counter
import re

# Cargar el modelo Whisper tiny una sola vez al iniciar el servidor
whisper_model = whisper.load_model("tiny", device="cpu")

# --- WebSocket para progreso de procesamiento ---
progress_status = {}
router = APIRouter()

@router.websocket("/ws/progreso/{uid}")
async def ws_progreso(websocket: WebSocket, uid: str):
    await websocket.accept()
    try:
        while True:
            progreso = progress_status.get(uid, 0)
            await websocket.send_json({"progress": progreso})
            if progreso >= 100:
                break
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass



UPLOAD_DIR = tempfile.gettempdir()
OUTPUT_DIR = os.path.join(UPLOAD_DIR, "lectorvideos")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Utilidad para limpiar archivo tras descarga
async def remove_file(path: str):
    try:
        os.remove(path)
    except Exception:
        pass

@router.post("/upload")
async def upload_video(request: Request, video: UploadFile = File(...)):
    # Guardar archivo temporalmente
    ext = os.path.splitext(video.filename)[1]
    if ext.lower() != ".mp4":
        raise HTTPException(status_code=400, detail="Solo se permite video mp4.")

    uid = str(uuid.uuid4())
    video_path = os.path.join(OUTPUT_DIR, f"{uid}.mp4")
    with open(video_path, "wb") as f:
        shutil.copyfileobj(video.file, f)

    # Inicializar progreso
    progress_status[uid] = 5

    # --- Procesar con Whisper (real) ---

    # Usar el modelo global ya cargado
    progress_status[uid] = 20
    await asyncio.sleep(1)
    result = whisper_model.transcribe(video_path, language="es")
    progress_status[uid] = 80
    transcription = result["text"]


    # --- Generar resumen automático y palabras clave ---
    # Resumen con sumy (LSA)
    parser = PlaintextParser.from_string(transcription, Tokenizer("spanish"))
    summarizer = LsaSummarizer()
    resumen_sentences = summarizer(parser.document, 2)  # 2 frases
    resumen = " ".join(str(s) for s in resumen_sentences) or "[No se pudo generar resumen]"

    # Palabras clave: top 5 palabras más frecuentes (sin stopwords)
    stopwords = set([
        "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", "un", "para", "con", "no", "una", "su", "al", "lo", "como", "más", "pero", "sus", "le", "ya", "o", "este", "sí", "porque", "esta", "entre", "cuando", "muy", "sin", "sobre", "también", "me", "hasta", "hay", "donde", "quien", "desde", "todo", "nos", "durante", "todos", "uno", "les", "ni", "contra", "otros", "ese", "eso", "ante", "ellos", "e", "esto", "mí", "antes", "algunos", "qué", "unos", "yo", "otro", "otras", "otra", "él", "tanto", "esa", "estos", "mucho", "quienes", "nada", "muchos", "cual", "poco", "ella", "estar", "estas", "algunas", "algo", "nosotros", "mi", "mis", "tú", "te", "ti", "tu", "tus", "ellas", "nosotras", "vosotros", "vosotras", "os", "mío", "mía", "míos", "mías", "tuyo", "tuya", "tuyos", "tuyas", "suyo", "suya", "suyos", "suyas", "nuestro", "nuestra", "nuestros", "nuestras", "vuestro", "vuestra", "vuestros", "vuestras", "esos", "esas", "estoy", "estás", "está", "estamos", "estáis", "están", "esté", "estés", "estemos", "estéis", "estén", "estaré", "estarás", "estará", "estaremos", "estaréis", "estarán", "estaría", "estarías", "estaríamos", "estaríais", "estarían", "estaba", "estabas", "estábamos", "estabais", "estaban", "estuve", "estuviste", "estuvo", "estuvimos", "estuvisteis", "estuvieron", "estuviera", "estuvieras", "estuviéramos", "estuvierais", "estuvieran", "estuviese", "estuvieses", "estuviésemos", "estuvieseis", "estuviesen", "estando", "estado", "estada", "estados", "estadas", "estad"])
    palabras = re.findall(r"\b\w{4,}\b", transcription.lower())
    palabras_filtradas = [w for w in palabras if w not in stopwords]
    top_palabras = [w for w, _ in Counter(palabras_filtradas).most_common(5)]
    palabras_clave = top_palabras if top_palabras else ["[No se detectaron palabras clave]"]

    # Análisis simple: longitud y densidad de palabras clave
    analisis = f"La transcripción tiene {len(transcription.split())} palabras. Palabras clave principales: {', '.join(palabras_clave)}."
    progress_status[uid] = 90

    # --- Crear archivo .md ---

    md_path = os.path.join(OUTPUT_DIR, f"{uid}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Material de estudio generado por LectorVideos\n\n")
        f.write(f"## Transcripción\n\n{transcription}\n\n")
        f.write(f"## Resumen\n\n{resumen}\n\n")
        f.write(f"## Palabras clave\n\n- " + "\n- ".join(palabras_clave) + "\n\n")
        f.write(f"## Análisis\n\n{analisis}\n")
    progress_status[uid] = 100

    # Eliminar video tras procesar
    try:
        os.remove(video_path)
    except Exception:
        pass

    # Devolver URL para descargar el .md
    base_url = str(request.base_url).rstrip("/")
    md_url = f"{base_url}/api/lectorvideos/download/{uid}"
    return JSONResponse({"md_url": md_url})

@router.get("/download/{uid}")
def download_md(uid: str):
    md_path = os.path.join(OUTPUT_DIR, f"{uid}.md")
    if not os.path.exists(md_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    # Eliminar el archivo después de servirlo
    return FileResponse(md_path, filename="material_estudio.md", media_type="text/markdown", background=BackgroundTask(remove_file, md_path))

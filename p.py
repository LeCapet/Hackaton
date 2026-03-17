import os
import sys 
import json 
import mimetypes

ENERGY_COEFFICIENTS = {
    "text_per_1k_chars": 0.05,   # énergie par 1000 caractères en J
    "image_per_mb": 0.3,         
    "video_per_mb": 0.6,         
    "document_per_mb": 0.1       
}

def detect_file_type(file_path):
    mime,_ = mimetypes.guess_type(file_path)
    if mime:
        if mime.startswith("image"): return "image"
        elif mime.startswith("video"): return "video"
        elif mime.startswith("text"): return "document"
    return "document"

def get_file_size_mb(file_path):
    return os.path.getsize(file_path)/(1024*1024)

def j_to_wh(joules):
    return joules / 3600

def estimate_energy(text="", files=None):
    if files is None: files=[]
    text_chars = len(text)
    text_energy_j = (text_chars/1000) * ENERGY_COEFFICIENTS["text_per_1k_chars"]

    files_energy_j = 0
    files_details = []

    for f in files:
        if not os.path.exists(f): continue
        size_mb = get_file_size_mb(f)
        ftype = detect_file_type(f)
        energy_j = size_mb * ENERGY_COEFFICIENTS.get(ftype+"_per_mb",0.1)
        files_energy_j += energy_j
        files_details.append({
            "name": os.path.basename(f),
            "type": ftype,
            "size_mb": round(size_mb,2),
            "energy_wh": round(j_to_wh(energy_j),6)
        })

    total_energy_j = text_energy_j + files_energy_j
    total_energy_wh = j_to_wh(total_energy_j) + 4.05  # ajout énergie requête IA

    return {
        "text": {"characters": text_chars, "energy_wh": round(j_to_wh(text_energy_j),6)},
        "files": files_details,
        "summary": {
            "files_energy_wh": round(j_to_wh(files_energy_j),6),
            "total_energy_wh": round(total_energy_wh,6)
        }
    }

if __name__=="__main__":
    try:
        data = json.load(sys.stdin)
        user_text = data.get("message","")
        files = data.get("files",[])
        result = estimate_energy(user_text, files)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

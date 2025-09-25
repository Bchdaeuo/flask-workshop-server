from flask import Flask, request, send_file, jsonify
from datetime import datetime, UTC
from flask_cors import CORS
from pymongo import MongoClient
from gridfs import GridFS
from bson.objectid import ObjectId
from io import BytesIO
import os

app = Flask(__name__)
CORS(app)

MONGO_URI = os.environ.get("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MongoDB URI이 환경변수에 설정되지 않았습니다!")

client = MongoClient(MONGO_URI)
db = client["workshop"]
fs = GridFS(db)

@app.route("/")
def home():
    return "창작마당 서버가 원활히 작동하고 있습니다."

@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files.get("file")
        title = request.form.get("title", "No Title")
        description = request.form.get("description", "No Description")

        if not file:
            return jsonify({"error": "No file provided"}), 400

        file_id = fs.put(file, filename=file.filename, metadata={
            "title": title,
            "description": description,
            "created_at": datetime.now(UTC)
        })

        return jsonify({"message": "File uploaded", "file_id": str(file_id)}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Upload failed", "details": str(e)}), 500

@app.route("/files")
def list_files():
    files = []
    for f in fs.find().sort("metadata.created_at", -1):
        created_at = f.metadata.get("created_at")
        if created_at:
            created_at_str = created_at.isoformat()
        else:
            created_at_str = None
        files.append({
            "file_id": str(f._id),
            "filename": f.filename,
            "title": f.metadata.get("title"),
            "description": f.metadata.get("description"),
            "created_at": created_at_str
        })
    return jsonify(files)

@app.route("/download/<file_id>")
def download(file_id):
    try:
        file = fs.get(ObjectId(file_id))
        return send_file(BytesIO(file.read()), download_name=file.filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": "File not found", "details": str(e)}), 404

@app.route("/filedata/<file_id>")
def filedata(file_id):
    try:
        file = fs.get(ObjectId(file_id))
        import json
        content = json.loads(file.read())
        return jsonify(content)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

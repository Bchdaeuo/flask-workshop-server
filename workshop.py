from flask import Flask, request, send_file, redirect, url_for, jsonify
from pymongo import MongoClient
from gridfs import GridFS
from bson.objectid import ObjectId
from io import BytesIO
import datetime
import os

app = Flask(__name__)

# MongoDB 연결 정보 (Render 환경에서 환경변수로 설정)
MONGO_URI = os.environ.get("mongodb+srv://admin:admin@bchdaeuo.dnvoqco.mongodb.net/?retryWrites=true&w=majority&appName=Bchdaeuo")  # 환경변수에서 MongoDB URI 읽기
client = MongoClient(MONGO_URI)
db = client["workshop"]
fs = GridFS(db)

# 테스트용 홈
@app.route("/")
def home():
    return "Server is running!"

# 업로드 처리
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    title = request.form.get("title", "No Title")
    description = request.form.get("description", "No Description")

    if not file:
        return jsonify({"error": "No file provided"}), 400

    file_id = fs.put(file, filename=file.filename, metadata={
        "title": title,
        "description": description,
        "created_at": datetime.datetime.utcnow()
    })

    return jsonify({"message": "File uploaded", "file_id": str(file_id)}), 200

# 업로드된 파일 목록 확인
@app.route("/files")
def list_files():
    files = []
    for f in fs.find().sort("metadata.created_at", -1):
        files.append({
            "file_id": str(f._id),
            "filename": f.filename,
            "title": f.metadata.get("title"),
            "description": f.metadata.get("description"),
            "created_at": f.metadata.get("created_at").isoformat()
        })
    return jsonify(files)

# 파일 다운로드
@app.route("/download/<file_id>")
def download(file_id):
    try:
        file = fs.get(ObjectId(file_id))
        return send_file(BytesIO(file.read()), download_name=file.filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": "File not found", "details": str(e)}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

from flask import Flask, request, render_template, send_file, redirect, url_for
from pymongo import MongoClient
from gridfs import GridFS
from bson.objectid import ObjectId
from io import BytesIO
import datetime
import os

app = Flask(__name__)

# MongoDB 연결 정보 (Render 환경에서 환경변수로 설정)
MONGO_URI = os.environ.get("mongodb+srv://admin:admin@bchdaeuo.dnvoqco.mongodb.net/?retryWrites=true&w=majority&appName=Bchdaeuo")  # Render에서 설정
client = MongoClient(MONGO_URI)
db = client["workshop"]
fs = GridFS(db)

# 업로드 처리
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    title = request.form["title"]
    description = request.form["description"]

    if file:
        fs.put(file, filename=file.filename, metadata={
            "title": title,
            "description": description,
            "created_at": datetime.datetime.utcnow()
        })
    return redirect(url_for("workshop"))

# 자료 목록 페이지
@app.route("/workshop")
def workshop():
    files = fs.find().sort("metadata.created_at", -1)
    return render_template("workshop.html", files=files)

# 파일 다운로드
@app.route("/download/<file_id>")
def download(file_id):
    try:
        file = fs.get(ObjectId(file_id))
        return send_file(BytesIO(file.read()), download_name=file.filename, as_attachment=True)
    except:
        return "파일을 찾을 수 없습니다.", 404

# 홈 → 워크샵 페이지 리다이렉트
@app.route("/")
def home():
    return redirect(url_for("workshop"))

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

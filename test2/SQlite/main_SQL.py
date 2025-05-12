# 標準ライブラリ
import uvicorn
# サードパーティ
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
# 自作モジュール
from app.database import engine, Base
from app import config
from routers import tasks, organizations, members, auth

# DB テーブル作成
Base.metadata.create_all(bind=engine)

# FastAPI インスタンス化
app = FastAPI()

# ルーターを登録
app.include_router(tasks.router)
app.include_router(organizations.router)
app.include_router(members.router)
app.include_router(auth.router)

# Reactからのアクセスを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React の URL を指定
    allow_credentials=True,
    allow_methods=["*"],  # すべての HTTP メソッドを許可 (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # すべてのヘッダーを許可
)

@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI with MySQL"}

# def main():
#     uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

# if __name__ == "__main__":
#     main()

# 仮想環境: .\venv\Scripts\activate
# 解除: deactivate
# requirementsをpipインストールで環境の再現が可能

# サーバー起動: uvicorn app.main:app --reload ※カレントディレクトリ: backend

# MySQLログイン: mysql -u root -p
# USE taskdb;
# SELECT * FROM tasks;
# quit

# GUI:MySQL Workbench
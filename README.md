# ai-model-serving-server

### 환경설정
```
uv python install 3.12
uv init -p 3.12 --bare
uv add langchain langchain-openai
uv add dotenv sqlalchemy pymysql flask
```

### 서버 실행
```bash
uv run src/app.py
```

### API 문서 확인
- Swagger UI: http://127.0.0.1:9090/docs
- ReDoc: http://127.0.0.1:9090/redoc
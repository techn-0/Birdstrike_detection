# 1) 베이스 이미지
FROM python:3.11-slim

# 2) 작업 디렉터리
WORKDIR /code

# 3) requirements.txt 복사 (※ 경로 앞에 backend/ 붙이지 않는다)
COPY requirements.txt .

# 4) 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5) 앱 소스 복사 (현재 컨텍스트의 모든 파일)
COPY . /code

# 6) 컨테이너 기동 명령
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

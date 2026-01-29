FROM python:3.11-slim

WORKDIR /app

# 复制宋体字体
COPY simsun.ttc /usr/share/fonts/simsun.ttc

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用文件
COPY app.py .
COPY origin.pdf .
COPY templates templates/

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

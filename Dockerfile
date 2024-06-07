# 使用官方的 Python 镜像作为基础镜像
FROM python:3.12-slim

# 使用官方的 Python 运行时作为基础镜像
FROM python:3.8-slim AS base

# 设置工作目录
WORKDIR /app

# 将 requirements.txt 复制到工作目录
COPY requirements.txt /app/

# 安装依赖项
RUN pip install --no-cache-dir -r requirements.txt

# 将当前目录中的内容复制到工作目录
COPY . /app

# 公开端口
EXPOSE 8000

# 运行 FastAPI 应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


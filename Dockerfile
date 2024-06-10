# 第一阶段：构建镜像
FROM python:3.12-slim AS builder




# 设置工作目录
WORKDIR /app

# 复制并安装依赖项
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 复制应用程序代码
COPY . .

# 第二阶段：生成最终镜像
FROM python:3.12-slim



# 设置工作目录
WORKDIR /app

# 从构建阶段复制依赖和应用代码
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# 公开端口
EXPOSE 8000

# 运行 FastAPI 应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

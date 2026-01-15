FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt || \
    pip install --no-cache-dir -r requirements.txt

# 复制Python应用代码
COPY app/ ./app/
COPY config/ ./config/

# 创建数据目录
RUN mkdir -p /app/data /app/covers

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "-m", "app.main"]

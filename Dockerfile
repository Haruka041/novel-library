# ==================== 阶段1: 构建Flutter Web ====================
FROM debian:bullseye-slim AS flutter-builder

# 安装必要的依赖
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    xz-utils \
    zip \
    libglu1-mesa \
    && rm -rf /var/lib/apt/lists/*

# 安装Flutter SDK
ENV FLUTTER_HOME=/opt/flutter
ENV PATH="$FLUTTER_HOME/bin:$PATH"

RUN git clone https://github.com/flutter/flutter.git -b stable $FLUTTER_HOME && \
    flutter --version && \
    flutter config --no-analytics && \
    flutter precache --web

# 复制Flutter项目
WORKDIR /build
COPY flutter_app/ ./flutter_app/

# 构建Flutter Web
WORKDIR /build/flutter_app
RUN flutter pub get && \
    flutter build web --release --web-renderer html

# ==================== 阶段2: Python应用 ====================
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

# 从Flutter构建阶段复制构建产物
COPY --from=flutter-builder /build/flutter_app/build/web ./app/web/static/flutter/

# 创建数据目录
RUN mkdir -p /app/data /app/covers

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "-m", "app.main"]

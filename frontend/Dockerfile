# ============================================================
# BOSS直聘采集系统 - 前端镜像
# 阶段一：Vite 构建静态产物；阶段二：Nginx 托管 + /api 反代
# ============================================================

FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
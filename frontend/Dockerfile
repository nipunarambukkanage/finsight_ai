# ==============================================================================
# FinSight AI - Frontend Production Dockerfile
# Multi-stage Node.js build with lightweight Alpine Nginx server
# ==============================================================================

FROM node:24-alpine AS builder

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Production Serving Stage
FROM nginx:alpine AS runner

COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]

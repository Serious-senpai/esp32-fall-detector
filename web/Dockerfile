# Reference: https://docs.docker.com/reference/dockerfile/
FROM node:25.2 AS builder

COPY web /app

WORKDIR /app
RUN npm install
RUN npm run build

FROM nginx:1.29-alpine AS runner

COPY web/nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /app/dist /app

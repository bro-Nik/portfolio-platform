FROM node:22-alpine AS base

WORKDIR /app

# Копируем shared из отдельного контекста
COPY --from=shared-context . /app/shared

COPY package*.json ./

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

FROM base AS development
RUN npm install
COPY --chown=appuser:appgroup . .

# Создаем символическую ссылку для доступа к shared
RUN ln -s /app/shared /app/node_modules/@shared

# Создаем папку кэша и даем права
RUN mkdir -p /app/node_modules/.cache && \
    chown -R appuser:appgroup /app/node_modules/.cache && \
    chmod -R 755 /app/node_modules/.cache

USER appuser
ENV NODE_ENV=development
ENV NODE_PATH=/app/node_modules
EXPOSE 3000
CMD ["npm", "start"]

FROM base AS production
RUN mkdir -p /app/build && chown appuser:appgroup /app/build
RUN npm ci --only=production && npm cache clean --force
COPY --chown=appuser:appgroup . .
# Создаем символическую ссылку для shared
RUN ln -s /app/shared /app/node_modules/@shared
USER appuser
ENV NODE_PATH=/app/node_modules
RUN npm run build

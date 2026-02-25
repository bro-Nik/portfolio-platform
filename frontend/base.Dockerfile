FROM node:22-alpine AS base

WORKDIR /app

COPY package*.json ./

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

FROM base AS development
RUN npm install
COPY --chown=appuser:appgroup . .
USER appuser
ENV NODE_ENV=development
EXPOSE 3000
CMD ["npm", "start"]

FROM base AS production
RUN mkdir -p /app/build && chown appuser:appgroup /app/build
RUN npm ci --only=production && npm cache clean --force
COPY --chown=appuser:appgroup . .
USER appuser
RUN npm run build

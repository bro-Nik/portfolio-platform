FROM node:22-alpine AS base

RUN npm install -g pnpm@11.13.1
WORKDIR /app

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy workspace config files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./

# Copy all package.json files so pnpm can resolve workspace dependencies
COPY shared/package.json ./shared/
COPY user/package.json ./user/
COPY admin/package.json ./admin/

RUN pnpm install --frozen-lockfile --ignore-scripts
RUN chown -R appuser:appgroup .

FROM base AS development
COPY --chown=appuser:appgroup . .
RUN pnpm --filter @portfolio/shared build
USER appuser
ENV NODE_ENV=development
EXPOSE 3000

FROM base AS production
COPY --chown=appuser:appgroup . .
ARG APP=@portfolio/user
USER appuser
ENV NODE_ENV=production
RUN pnpm --filter @portfolio/shared build && pnpm --filter ${APP} build

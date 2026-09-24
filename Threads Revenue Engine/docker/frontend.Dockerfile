FROM node:22-alpine AS build
WORKDIR /app
RUN corepack enable
COPY apps/frontend/package.json apps/frontend/pnpm-lock.yaml ./
RUN corepack pnpm install --frozen-lockfile
COPY apps/frontend ./
ARG BACKEND_URL=http://backend:8000
ENV BACKEND_URL=$BACKEND_URL
RUN corepack pnpm build
FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production HOSTNAME=0.0.0.0 PORT=3000
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
USER node
EXPOSE 3000
CMD ["node","server.js"]

## ---- deps ----
FROM node:20-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

## ---- builder ----
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Gera artefatos standalone (next.config.js já tem output: 'standalone')
RUN npm run build

## ---- runner ----
# No modo standalone não precisamos de node_modules nem do binário `next`.
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
# Copiamos apenas o necessário
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node","server.js"]

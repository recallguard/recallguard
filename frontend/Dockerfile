########################
#  Stage 0 – builder   #
########################
FROM node:20-slim AS build

WORKDIR /app

# 1️⃣ install deps
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install --legacy-peer-deps

# 2️⃣ copy source & shared lib
COPY frontend ./frontend
COPY shared   ./shared
RUN cd frontend && npm run build      # → .next

########################
#  Stage 1 – runtime   #
########################
FROM node:20-slim
WORKDIR /app
ENV NODE_ENV=production

# bring in built files only
COPY --from=build /app/frontend/.next   ./frontend/.next
COPY --from=build /app/frontend/public  ./frontend/public
COPY --from=build /app/shared           ./shared
COPY frontend/package*.json             ./frontend/

# production-only dependencies
RUN cd frontend && npm install --omit=dev --legacy-peer-deps

EXPOSE 3000
CMD ["node", "frontend/node_modules/next/dist/bin/next", "start", "-p", "3000"]

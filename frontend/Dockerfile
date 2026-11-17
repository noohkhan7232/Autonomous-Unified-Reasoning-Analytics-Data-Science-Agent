FROM node:24-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG AURA_API_URL=http://api:8000
ENV AURA_API_URL=$AURA_API_URL NEXT_TELEMETRY_DISABLED=1
RUN npm run build
EXPOSE 3000
CMD ["node", "./node_modules/next/dist/bin/next", "start", "--hostname", "0.0.0.0"]

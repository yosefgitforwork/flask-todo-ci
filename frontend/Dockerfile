# --- Stage 1: build the static assets with Node --------------------------------
FROM node:20-alpine AS build
WORKDIR /app

# Install deps first for better layer caching. `npm ci` is the reproducible,
# lockfile-driven install; it falls back to `npm install` on the very first
# build before a package-lock.json has been committed.
COPY package.json package-lock.json* ./
RUN npm ci || npm install

COPY . .
RUN npm run build

# --- Stage 2: serve the built SPA with nginx -----------------------------------
FROM nginx:alpine

# Static assets from the build stage.
COPY --from=build /app/dist /usr/share/nginx/html

# Our SPA + API-proxy config replaces nginx's default site.
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

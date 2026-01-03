# StoryQuest Frontend Dockerfile
# Multi-stage build for optimized production image

# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
# Note: VITE_API_URL and VITE_TTS_URL can be overridden at build time
ARG VITE_API_URL=http://localhost:8000
ARG VITE_TTS_URL=http://localhost:8001
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_TTS_URL=$VITE_TTS_URL

RUN npm run build

# Stage 2: Production - using official unprivileged nginx image
# Runs as non-root user (uid 101) by default, listens on 8080
FROM nginxinc/nginx-unprivileged:alpine

# Copy custom nginx config with correct ownership (nginx user is uid 101)
COPY --chown=nginx:nginx nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from builder stage with correct ownership
COPY --chown=nginx:nginx --from=builder /app/dist /usr/share/nginx/html

# Expose port 8080 (non-privileged port)
EXPOSE 8080

# Start nginx (already runs as non-root)
CMD ["nginx", "-g", "daemon off;"]

# ============================================================================
# FILE: frontend/Dockerfile
# Docker Container for React Frontend
# ============================================================================

FROM node:18-alpine

# Set working directory
WORKDIR /app

# Set environment variables
ENV NODE_ENV=development \
    PATH=/app/node_modules/.bin:$PATH

# Install app dependencies
# Copy package files first for better caching
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install --silent && \
    npm install react-scripts@5.0.1 -g --silent

# Copy app source
COPY . .

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start app
CMD ["npm", "start"]
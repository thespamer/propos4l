FROM node:18-alpine

# Install dependencies required for node-gyp and other native modules
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git

WORKDIR /app

# Install dependencies only when needed
COPY package.json ./

# Set development environment first to ensure dev dependencies are installed
ENV NODE_ENV=development

# Clean npm cache and install dependencies with full verbosity
RUN npm cache clean --force && \
    npm install --include=dev --verbose

# Instalar explicitamente as dependências de PostCSS e Tailwind que estão faltando
RUN npm install postcss-flexbugs-fixes postcss-preset-env postcss-import @tailwindcss/typography --save-dev

# Set development environment
ENV NODE_ENV=development \
    NEXT_TELEMETRY_DISABLED=1 \
    HOSTNAME=0.0.0.0 \
    PORT=3000

# Copy source code
COPY . .

# Skip lint and type-check for troubleshooting
# Original: RUN npm run lint && npm run type-check

# Create .next directory with proper permissions
RUN mkdir -p .next && \
    chmod -R 777 .next

# We'll run as root to avoid permission issues
# USER node is commented out to troubleshoot permission issues

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Start development server
CMD ["npm", "run", "dev"]

FROM node:18-alpine
WORKDIR /app

# Install dependencies only when needed
COPY package*.json ./
RUN npm install

# Set development environment
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Set hostname
ENV HOSTNAME=0.0.0.0

# Start development server
CMD ["npm", "run", "dev"]

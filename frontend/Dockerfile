# Frontend image for Secret Santa (development)
FROM node:18

WORKDIR /usr/src/app

# Install deps early for layer caching
COPY package.json ./
RUN npm install --legacy-peer-deps

# Copy source
COPY . ./

EXPOSE 3000

ENV HOST=0.0.0.0
ENV BROWSER=none

CMD ["npm", "start"]


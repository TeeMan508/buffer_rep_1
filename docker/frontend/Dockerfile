FROM node:20.10.0

WORKDIR /app

COPY ./semantic/frontend/package*.json ./

COPY ./semantic/frontend/.env.local /app/.env.local

RUN npm install

FROM node:lts-alpine

WORKDIR /app

ENV PATH /app/node_modules/.bin:$PATH

# Install pnpm
# RUN npm install -g pnpm

COPY package.json .
COPY package-lock.json .
RUN npm install

CMD ["npm", "run", "dev"]
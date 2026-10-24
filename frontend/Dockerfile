FROM node:lts-alpine

WORKDIR /app

ENV PATH /app/node_modules/.bin:$PATH

# Install pnpm
RUN npm install -g pnpm@9

COPY package.json .
COPY pnpm-lock.yaml .

RUN pnpm install

EXPOSE 5173

CMD ["pnpm", "run", "dev"]

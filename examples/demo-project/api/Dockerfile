FROM node:14
COPY . /srv/api
WORKDIR /srv/api
RUN npm install
USER root
CMD ["node", "server.js"]

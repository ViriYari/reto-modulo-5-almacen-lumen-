FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --omit=dev

COPY datos ./datos
COPY app-tienda ./app-tienda

RUN node datos/generar-datos.js \
  && addgroup -S lumen \
  && adduser -S lumen -G lumen \
  && chown -R lumen:lumen /app

USER lumen

ENV PORT=4789
EXPOSE 4789

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=5 \
  CMD node -e "fetch('http://127.0.0.1:4789/api/health').then(r=>r.json()).then(b=>process.exit(b.status==='ok'?0:1)).catch(()=>process.exit(1))"

CMD ["node", "app-tienda/server.js"]

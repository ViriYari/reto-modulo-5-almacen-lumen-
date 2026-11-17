import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { crearPedido } from "./dominio.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const RAIZ = path.resolve(__dirname, "..");
const PUBLICO = path.join(__dirname, "public");
const RUTA_DB = process.env.DATOS_PATH || path.join(RAIZ, "datos", "db.json");
const PUERTO = Number(process.env.PORT || 4789);

const TIPOS = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".svg": "image/svg+xml",
  ".json": "application/json; charset=utf-8",
};

function cargarCatalogo() {
  const db = JSON.parse(fs.readFileSync(RUTA_DB, "utf8"));
  return {
    categorias: db.categorias,
    productos: db.productos.map((producto) => ({ ...producto })),
  };
}

const estado = cargarCatalogo();
let secuencia = 1001;
const pedidos = [];

function enviar(res, status, cuerpo, tipo = "application/json; charset=utf-8") {
  const payload = typeof cuerpo === "string" ? cuerpo : JSON.stringify(cuerpo);
  res.writeHead(status, {
    "Content-Type": tipo,
    "Cache-Control": "no-store",
  });
  res.end(payload);
}

function leerCuerpo(req) {
  return new Promise((resolve, reject) => {
    const trozos = [];
    let tamano = 0;
    req.on("data", (trozo) => {
      tamano += trozo.length;
      if (tamano > 1_000_000) {
        reject(Object.assign(new Error("payload"), { status: 413 }));
        req.destroy();
        return;
      }
      trozos.push(trozo);
    });
    req.on("end", () => {
      if (trozos.length === 0) {
        resolve({});
        return;
      }
      try {
        resolve(JSON.parse(Buffer.concat(trozos).toString("utf8")));
      } catch {
        reject(Object.assign(new Error("json"), { status: 400 }));
      }
    });
    req.on("error", reject);
  });
}

function archivoPublico(urlPath) {
  const relativo = urlPath === "/" ? "index.html" : urlPath.slice(1);
  const destino = path.normalize(path.join(PUBLICO, relativo));
  if (!destino.startsWith(PUBLICO)) return null;
  if (!fs.existsSync(destino) || !fs.statSync(destino).isFile()) return null;
  return destino;
}

const servidor = http.createServer(async (req, res) => {
  const url = new URL(req.url || "/", `http://${req.headers.host || "localhost"}`);

  try {
    if (req.method === "GET" && url.pathname === "/api/health") {
      enviar(res, 200, {
        status: "ok",
        servicio: "almacen-lumen",
        catalogo: estado.productos.length,
      });
      return;
    }

    if (req.method === "GET" && url.pathname === "/api/categorias") {
      enviar(res, 200, { categorias: estado.categorias });
      return;
    }

    if (req.method === "GET" && url.pathname === "/api/productos") {
      enviar(res, 200, { productos: estado.productos });
      return;
    }

    if (req.method === "GET" && url.pathname === "/api/pedidos") {
      enviar(res, 200, { pedidos });
      return;
    }

    if (req.method === "POST" && url.pathname === "/api/pedidos") {
      const solicitud = await leerCuerpo(req);
      const resultado = crearPedido(estado.productos, secuencia, solicitud);
      if (!resultado.ok) {
        enviar(res, resultado.status, { error: resultado.error });
        return;
      }
      estado.productos = resultado.productos;
      secuencia += 1;
      pedidos.push(resultado.pedido);
      enviar(res, 201, resultado.pedido);
      return;
    }

    if (req.method === "GET") {
      const archivo = archivoPublico(url.pathname);
      if (!archivo) {
        enviar(res, 404, { error: "No encontrado" });
        return;
      }
      const extension = path.extname(archivo);
      res.writeHead(200, {
        "Content-Type": TIPOS[extension] || "application/octet-stream",
        "Cache-Control": "no-cache",
      });
      fs.createReadStream(archivo).pipe(res);
      return;
    }

    enviar(res, 405, { error: "Método no permitido" });
  } catch (error) {
    const status = error.status || 500;
    enviar(res, status, { error: status === 400 ? "JSON inválido" : "Error interno" });
  }
});

servidor.listen(PUERTO, "0.0.0.0", () => {
  console.log(`Almacén Lumen escuchando en http://127.0.0.1:${PUERTO}`);
});

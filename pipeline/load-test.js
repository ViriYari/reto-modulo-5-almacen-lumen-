import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
function opcion(nombre, defecto) {
  const indice = args.indexOf(`--${nombre}`);
  if (indice === -1) return process.env[nombre.toUpperCase().replaceAll("-", "_")] ?? defecto;
  return args[indice + 1];
}

const base = process.env.BASE_URL || "http://127.0.0.1:4789";
const slaP95 = Number(opcion("sla-p95", process.env.SLA_P95_MS || 800));
const slaError = Number(opcion("sla-error", process.env.SLA_ERROR_MAX || 0.01));
const duracion = Number(opcion("duration", 5000));
const concurrencia = Number(opcion("concurrency", 12));
const salida = opcion("out", "");

function percentil(muestras, p) {
  if (muestras.length === 0) return 0;
  const ordenadas = [...muestras].sort((a, b) => a - b);
  const indice = Math.min(ordenadas.length - 1, Math.max(0, Math.ceil((p / 100) * ordenadas.length) - 1));
  return ordenadas[indice];
}

async function unaVez() {
  const ruta = Math.random() < 0.75 ? "/api/productos" : "/api/health";
  const inicio = performance.now();
  try {
    const respuesta = await fetch(`${base}${ruta}`);
    const ms = performance.now() - inicio;
    return { ok: respuesta.ok, ms };
  } catch {
    return { ok: false, ms: performance.now() - inicio };
  }
}

for (let i = 0; i < 20; i += 1) await unaVez();

const latencias = [];
let errores = 0;
let total = 0;
const fin = Date.now() + duracion;

async function trabajador() {
  while (Date.now() < fin) {
    const resultado = await unaVez();
    total += 1;
    latencias.push(resultado.ms);
    if (!resultado.ok) errores += 1;
  }
}

await Promise.all(Array.from({ length: concurrencia }, () => trabajador()));

const p95 = Math.round(percentil(latencias, 95) * 100) / 100;
const errorRate = total === 0 ? 1 : errores / total;
const passed = p95 < slaP95 && errorRate < slaError;
const reporte = {
  base,
  requests: total,
  errors: errores,
  errorRate: Number(errorRate.toFixed(4)),
  p95Ms: p95,
  slaP95Ms: slaP95,
  slaErrorMax: slaError,
  passed,
};

if (salida) {
  fs.mkdirSync(path.dirname(salida), { recursive: true });
  fs.writeFileSync(salida, `${JSON.stringify(reporte, null, 2)}\n`);
}

console.log(JSON.stringify(reporte, null, 2));
if (!passed) {
  console.error(
    `GATE ROJO: p95 ${p95} ms (límite ${slaP95} ms), error ${(errorRate * 100).toFixed(2)}% (límite ${slaError * 100}%). El deploy se detiene.`,
  );
  process.exit(1);
}
console.log("GATE VERDE: la carga cumple el SLA. El deploy puede continuar.");

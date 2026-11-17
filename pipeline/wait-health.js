const base = process.env.BASE_URL || "http://127.0.0.1:4789";
const limite = Date.now() + Number(process.env.HEALTH_TIMEOUT_MS || 20000);

while (Date.now() < limite) {
  try {
    const respuesta = await fetch(`${base}/api/health`);
    if (respuesta.ok) {
      const cuerpo = await respuesta.json();
      if (cuerpo.status === "ok") {
        console.log(`health ok en ${base}`);
        process.exit(0);
      }
    }
  } catch {
    // el proceso todavía está abriendo el puerto
  }
  await new Promise((resolver) => setTimeout(resolver, 300));
}

console.error(`La app no respondió en ${base}/api/health`);
process.exit(1);

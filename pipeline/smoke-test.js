const base = process.env.BASE_URL || "http://127.0.0.1:4789";

function fallar(mensaje) {
  console.error(`SMOKE ROJO: ${mensaje}`);
  process.exit(1);
}

const salud = await fetch(`${base}/api/health`);
if (!salud.ok) fallar(`/api/health respondió ${salud.status}`);
const health = await salud.json();
if (health.status !== "ok") fallar("el cuerpo de health no trae status ok");
console.log("gate health: la app encendió");

const catalogoRes = await fetch(`${base}/api/productos`);
if (!catalogoRes.ok) fallar(`/api/productos respondió ${catalogoRes.status}`);
const catalogo = await catalogoRes.json();
if (!Array.isArray(catalogo.productos) || catalogo.productos.length < 20) {
  fallar(`el catálogo tiene ${catalogo.productos?.length ?? 0} productos`);
}
console.log(`gate catálogo: ${catalogo.productos.length} productos`);

const disponible = catalogo.productos.find((producto) => producto.stock >= 5);
if (!disponible) fallar("no hay un producto con stock suficiente para el pedido de humo");

const pedidoRes = await fetch(`${base}/api/pedidos`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    cliente: { nombre: "Humo Pipeline", correo: "humo.pipeline@example.com" },
    items: [{ productoId: disponible.id, cantidad: 1 }],
  }),
});
const pedido = await pedidoRes.json();
if (pedidoRes.status !== 201 || !pedido.id) fallar(`crear pedido respondió ${pedidoRes.status}: ${JSON.stringify(pedido)}`);
console.log(`gate pedido: folio ${pedido.id}`);
console.log("SMOKE VERDE");

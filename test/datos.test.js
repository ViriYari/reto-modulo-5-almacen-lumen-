import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import { anonimizarCliente, generarCatalogo, leerDump, SEMILLA } from "../datos/generar-datos.js";

test("la semilla del reto queda fija", () => {
  assert.equal(SEMILLA, 20261117);
});

test("anonimiza nombre, correo y teléfono de un volcado ficticio", () => {
  const anonimo = anonimizarCliente({
    id: "cli-01",
    nombre: "Mariana Solís Prado",
    correo: "mariana.solis@ejemplo-ficticio.test",
    telefono: "5512345678",
    calle: "Avenida Imaginaria 120",
    ciudad: "Puebla",
  });
  assert.equal(anonimo.nombre, "M*** S*** P***");
  assert.equal(anonimo.correo, "m***@ejemplo-ficticio.test");
  assert.equal(anonimo.telefono, "***5678");
  assert.equal(anonimo.calle, "Calle ***");
  assert.equal(anonimo.ciudad, "Puebla");
  assert.equal(JSON.stringify(anonimo).includes("Mariana"), false);
  assert.equal(JSON.stringify(anonimo).includes("5512345678"), false);
});

test("el catálogo es reproducible y coherente", () => {
  const primero = generarCatalogo(SEMILLA);
  const segundo = generarCatalogo(SEMILLA);
  assert.deepEqual(primero, segundo);
  assert.equal(primero.categorias.length, 4);
  assert.ok(primero.productos.length >= 20);

  const ids = new Set(primero.productos.map((producto) => producto.id));
  assert.equal(ids.size, primero.productos.length);

  for (const producto of primero.productos) {
    assert.ok(producto.nombre.length > 3);
    assert.ok(producto.detalle.length > 3);
    assert.equal(Number.isInteger(producto.precio), true);
    assert.ok(producto.precio > 0);
    assert.equal(producto.moneda, "MXN");
    assert.ok(primero.categorias.some((categoria) => categoria.id === producto.categoria));
    assert.equal(producto.sku, producto.id.toUpperCase());
  }

  assert.equal(primero.productos.find((producto) => producto.id === "esc-05").stock, 1);
  assert.equal(primero.productos.find((producto) => producto.id === "esc-06").stock, 0);
  assert.equal(
    primero.productos.filter((producto) => producto.id !== "esc-05" && producto.id !== "esc-06").every((producto) => producto.stock >= 8),
    true,
  );
});

test("el db generado no conserva correos ni nombres del dump", () => {
  const dump = leerDump();
  const catalogo = generarCatalogo(SEMILLA, dump);
  const serializado = JSON.stringify(catalogo);
  for (const cliente of dump.clientes) {
    assert.equal(serializado.includes(cliente.correo), false);
    assert.equal(serializado.includes(cliente.nombre), false);
    assert.equal(serializado.includes(cliente.telefono), false);
    assert.equal(serializado.includes(cliente.calle), false);
  }
  assert.equal(catalogo.clientes.length, dump.clientes.length);
  assert.match(catalogo.clientes[0].correo, /^.{1}\*\*\*@/);
});

test("el archivo de pipeline nombra los stages y el gate de carga", () => {
  const pipeline = fs.readFileSync(new URL("../azure-pipelines.yml", import.meta.url), "utf8");
  const stages = [...pipeline.matchAll(/- stage: (\w+)/g)].map((coincidencia) => coincidencia[1]);
  assert.deepEqual(stages.slice(0, 3), ["Build", "SmokeTests", "LoadTest"]);
  assert.ok(stages.includes("CloudTests"));
  assert.ok(stages.includes("Deploy"));
  assert.match(pipeline, /SLA_P95_MS/);
  assert.match(pipeline, /pipeline\/load-test\.js/);
  const deploy = pipeline.slice(pipeline.indexOf("- stage: Deploy"));
  assert.match(deploy, /dependsOn:[\s\S]*LoadTest/);
  assert.match(deploy, /succeeded\(\)/);
});

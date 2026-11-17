import assert from "node:assert/strict";
import test from "node:test";
import { crearPedido } from "../app-tienda/dominio.js";

const catalogo = [
  { id: "cer-01", nombre: "Tazón de gres en verde salvia", precio: 340, stock: 8, categoria: "ceramica" },
  { id: "esc-05", nombre: "Soporte para laptop de fieltro", precio: 420, stock: 1, categoria: "escritorio" },
];

const cliente = { nombre: "Cliente Demo", correo: "cliente.demo@example.com" };

test("confirma un pedido y descuenta existencia sin mutar el catálogo original", () => {
  const resultado = crearPedido(catalogo, 1001, {
    cliente,
    items: [{ productoId: "cer-01", cantidad: 2 }],
  });
  assert.equal(resultado.ok, true);
  assert.equal(resultado.pedido.id, "LM-1001");
  assert.equal(resultado.pedido.total, 680);
  assert.equal(resultado.pedido.estado, "confirmado");
  assert.equal(resultado.productos.find((producto) => producto.id === "cer-01").stock, 6);
  assert.equal(catalogo[0].stock, 8);
});

test("rechaza carrito vacío, correo inválido, producto inexistente y stock de más", () => {
  assert.equal(crearPedido(catalogo, 1, { cliente, items: [] }).status, 400);
  assert.match(crearPedido(catalogo, 1, { cliente: { nombre: "Ana", correo: "no-es-correo" }, items: [{ productoId: "cer-01", cantidad: 1 }] }).error, /correo/i);
  assert.equal(crearPedido(catalogo, 1, { cliente, items: [{ productoId: "no-esta", cantidad: 1 }] }).status, 404);
  const stock = crearPedido(catalogo, 1, { cliente, items: [{ productoId: "esc-05", cantidad: 5 }] });
  assert.equal(stock.status, 409);
  assert.match(stock.error, /insuficiente/i);
  assert.equal(catalogo.find((producto) => producto.id === "esc-05").stock, 1);
});

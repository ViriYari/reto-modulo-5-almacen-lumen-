import path from "node:path";
import { fileURLToPath } from "node:url";
import { MatchersV3, PactV4 } from "@pact-foundation/pact";

const { eachLike, integer, string } = MatchersV3;
const dir = path.join(path.dirname(fileURLToPath(import.meta.url)), "pacts");

const pact = new PactV4({
  consumer: "almacen-lumen-front",
  provider: "almacen-lumen-api",
  dir,
});

await pact
  .addInteraction()
  .given("hay productos en el catalogo")
  .uponReceiving("una consulta GET /api/productos")
  .withRequest("GET", "/api/productos")
  .willRespondWith(200, (builder) => {
    builder.headers({ "Content-Type": "application/json; charset=utf-8" });
    builder.jsonBody({
      productos: eachLike({
        id: string("cer-01"),
        nombre: string("Tazón de gres en verde salvia"),
        precio: integer(340),
        stock: integer(8),
        categoria: string("ceramica"),
        categoriaNombre: string("Cerámica"),
      }),
    });
  })
  .executeTest(async (mock) => {
    const respuesta = await fetch(`${mock.url}/api/productos`);
    if (!respuesta.ok) throw new Error(`el mock respondió ${respuesta.status}`);
    const cuerpo = await respuesta.json();
    if (!Array.isArray(cuerpo.productos) || cuerpo.productos.length < 1) {
      throw new Error("el contrato no devolvió productos");
    }
    const primero = cuerpo.productos[0];
    for (const campo of ["id", "nombre", "precio", "stock", "categoria", "categoriaNombre"]) {
      if (primero[campo] === undefined) throw new Error(`falta ${campo}`);
    }
  });

console.log("PACT CONSUMER VERDE");

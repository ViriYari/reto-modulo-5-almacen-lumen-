import path from "node:path";
import { fileURLToPath } from "node:url";
import { Verifier } from "@pact-foundation/pact";

const base = process.env.BASE_URL || "http://127.0.0.1:4789";
const pactFile = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  "pacts",
  "almacen-lumen-front-almacen-lumen-api.json",
);

await new Verifier({
  provider: "almacen-lumen-api",
  providerBaseUrl: base,
  pactUrls: [pactFile],
  stateHandlers: {
    "hay productos en el catalogo": async () => {
      const salud = await fetch(`${base}/api/health`);
      if (!salud.ok) throw new Error("el provider no está sano");
    },
  },
}).verifyProvider();

console.log("PACT PROVIDER VERDE");

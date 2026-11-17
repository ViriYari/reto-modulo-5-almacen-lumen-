import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { fakerES as faker } from "@faker-js/faker";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const SEMILLA = 20261117;
export const RUTA_DUMP = path.join(__dirname, "dump-ficticio.json");
export const RUTA_DB = path.join(__dirname, "db.json");

const CATEGORIAS = [
  {
    id: "ceramica",
    nombre: "Cerámica",
    prefijo: "cer",
    union: "en",
    precio: { min: 220, max: 860 },
    piezas: [
      ["Tazón de gres", "Para el café de la mañana."],
      ["Plato hondo", "Caldo, pasta o fruta."],
      ["Jarra de agua", "Un litro, para la mesa."],
      ["Taza de gres", "Asa cómoda y boca ancha."],
      ["Cuenco", "Ensalada o fruta de temporada."],
      ["Florero de cuello estrecho", "Para una sola rama."],
    ],
    acabados: ["verde salvia", "arena", "blanco roto", "azul mineral", "terracota", "ceniza"],
  },
  {
    id: "textil",
    nombre: "Textil",
    prefijo: "tex",
    union: "en",
    precio: { min: 280, max: 1480 },
    piezas: [
      ["Manta de lana", "Liviana, para el sofá."],
      ["Cojín de lino", "Funda lavable, relleno aparte."],
      ["Camino de mesa", "Largo de 180 cm."],
      ["Funda de cojín", "Cierre oculto."],
      ["Tapete de algodón", "Para la entrada o el baño."],
      ["Cortina ligera", "Deja pasar la luz de la tarde."],
    ],
    acabados: ["crudo", "índigo", "raya fina", "óxido", "musgo", "avena"],
  },
  {
    id: "iluminacion",
    nombre: "Iluminación",
    prefijo: "ilu",
    union: "de",
    precio: { min: 340, max: 1890 },
    piezas: [
      ["Lámpara de mesa", "Luz cálida, pantalla incluida."],
      ["Lámpara de pie", "Brazo fijo, para leer."],
      ["Foco decorativo", "LED, base E27."],
      ["Candelero", "Para una vela de 2 cm."],
      ["Pantalla de lino", "Reemplazo para portalámparas."],
      ["Lámpara de muro", "Lectura de cabecera."],
    ],
    acabados: ["latón", "negro mate", "roble", "cerámica blanca", "acero", "lino natural"],
  },
  {
    id: "escritorio",
    nombre: "Escritorio",
    prefijo: "esc",
    union: "de",
    precio: { min: 90, max: 740 },
    piezas: [
      ["Portalápices", "Cabe un puñado de lápices."],
      ["Charola de documentos", "Dos niveles, carta y oficio."],
      ["Reloj de escritorio", "Sin alarma, solo la hora."],
      ["Libreta de lino", "96 hojas, rayadas."],
      ["Soporte para laptop", "Inclinación fija."],
      ["Organizador de cables", "Para el escritorio compartido."],
    ],
    acabados: ["fresno", "nogal", "cartón piedra", "fieltro", "aluminio", "lino"],
  },
];

function redondearPrecio(bruto, rango) {
  const decena = Math.round(bruto / 10) * 10;
  return Math.min(rango.max, Math.max(rango.min, decena));
}

export function anonimizarCliente(cliente) {
  return {
    id: cliente.id,
    nombre: String(cliente.nombre)
      .trim()
      .split(/\s+/)
      .map((palabra) => {
        const primera = [...palabra][0] || "*";
        return `${primera}***`;
      })
      .join(" "),
    correo: enmascararCorreo(cliente.correo),
    telefono: `***${String(cliente.telefono).replace(/\D/g, "").slice(-4)}`,
    calle: "Calle ***",
    ciudad: cliente.ciudad,
  };
}

function enmascararCorreo(correo) {
  const [local, dominio] = String(correo).split("@");
  if (!dominio) return "***";
  const inicial = [...(local || "*")][0] || "*";
  return `${inicial}***@${dominio}`;
}

export function leerDump(ruta = RUTA_DUMP) {
  return JSON.parse(fs.readFileSync(ruta, "utf8"));
}

export function generarCatalogo(semilla = SEMILLA, dump = leerDump()) {
  faker.seed(semilla);
  const productos = [];

  for (const categoria of CATEGORIAS) {
    categoria.piezas.forEach(([pieza, detalle], indice) => {
      const acabado = categoria.acabados[indice % categoria.acabados.length];
      const bruto = faker.number.int(categoria.precio);
      const numero = String(indice + 1).padStart(2, "0");
      const id = `${categoria.prefijo}-${numero}`;
      let stock = faker.number.int({ min: 8, max: 30 });
      if (id === "esc-05") stock = 1;
      if (id === "esc-06") stock = 0;

      productos.push({
        id,
        sku: id.toUpperCase(),
        nombre: `${pieza} ${categoria.union} ${acabado}`,
        detalle,
        precio: redondearPrecio(bruto, categoria.precio),
        moneda: "MXN",
        stock,
        categoria: categoria.id,
        categoriaNombre: categoria.nombre,
      });
    });
  }

  return {
    semilla,
    moneda: "MXN",
    categorias: CATEGORIAS.map((categoria) => ({
      id: categoria.id,
      nombre: categoria.nombre,
      productos: productos.filter((producto) => producto.categoria === categoria.id).length,
    })),
    productos,
    clientes: dump.clientes.map(anonimizarCliente),
  };
}

export function escribirDb(catalogo, ruta = RUTA_DB) {
  fs.writeFileSync(ruta, `${JSON.stringify(catalogo, null, 2)}\n`, "utf8");
  return ruta;
}

const ejecutadoComoScript = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);

if (ejecutadoComoScript) {
  const catalogo = generarCatalogo(SEMILLA);
  const ruta = escribirDb(catalogo);
  console.log(
    `Catálogo generado con semilla ${catalogo.semilla}: ${catalogo.productos.length} productos, ${catalogo.categorias.length} categorías, ${catalogo.clientes.length} clientes anonimizados.`,
  );
  console.log(ruta);
}

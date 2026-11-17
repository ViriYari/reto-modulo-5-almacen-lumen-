const estado = {
  productos: [],
  categorias: [],
  filtro: "todas",
  carrito: [],
};

const dinero = new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN" });
const grid = document.querySelector("[data-testid='catalog-grid']");
const status = document.querySelector("[data-testid='catalog-status']");
const aviso = document.querySelector("[data-testid='aviso']");
const filtros = document.querySelector(".filtros");
const lineas = document.querySelector("[data-testid='cart-lines']");
const vacio = document.querySelector("[data-testid='cart-empty']");
const total = document.querySelector("[data-testid='cart-total']");
const contador = document.querySelector("[data-testid='cart-count']");
const folio = document.querySelector("[data-testid='order-folio']");
const formulario = document.querySelector("[data-testid='checkout-form']");

function mostrarAviso(tipo, texto) {
  aviso.hidden = false;
  aviso.dataset.tipo = tipo;
  aviso.textContent = texto;
}

function limpiarAviso() {
  aviso.hidden = true;
  aviso.dataset.tipo = "";
  aviso.textContent = "";
}

function piezasEnCarrito() {
  return estado.carrito.reduce((suma, linea) => suma + linea.cantidad, 0);
}

function pintarCarrito() {
  const cantidad = piezasEnCarrito();
  contador.textContent = String(cantidad);
  lineas.replaceChildren();
  vacio.hidden = cantidad > 0;
  let suma = 0;
  for (const linea of estado.carrito) {
    suma += linea.precio * linea.cantidad;
    const item = document.createElement("li");
    const nombre = document.createElement("span");
    nombre.textContent = `${linea.cantidad} × ${linea.nombre}`;
    const importe = document.createElement("span");
    importe.textContent = dinero.format(linea.precio * linea.cantidad);
    item.append(nombre, importe);
    lineas.append(item);
  }
  total.dataset.total = String(suma);
  total.textContent = dinero.format(suma);
}

function pintarCatalogo() {
  grid.replaceChildren();
  const visibles = estado.productos.filter(
    (producto) => estado.filtro === "todas" || producto.categoria === estado.filtro,
  );
  for (const producto of visibles) {
    const card = document.createElement("article");
    card.className = `card${producto.stock === 0 ? " is-gone" : ""}`;
    card.dataset.testid = "product-card";
    card.dataset.productId = producto.id;
    card.dataset.stock = String(producto.stock);
    card.dataset.category = producto.categoria;

    const categoria = document.createElement("p");
    categoria.className = "card-cat";
    categoria.dataset.testid = "product-category";
    categoria.textContent = producto.categoriaNombre;

    const titulo = document.createElement("h2");
    titulo.dataset.testid = "product-name";
    titulo.textContent = producto.nombre;

    const detalle = document.createElement("p");
    detalle.className = "detail";
    detalle.textContent = producto.detalle;

    const precio = document.createElement("p");
    precio.className = "price";
    precio.dataset.testid = "product-price";
    precio.textContent = dinero.format(producto.precio);

    const existencia = document.createElement("p");
    existencia.className = "stock";
    existencia.textContent = producto.stock === 0 ? "Agotado" : `${producto.stock} en existencia`;

    const acciones = document.createElement("div");
    acciones.className = "card-actions";
    const etiqueta = document.createElement("label");
    etiqueta.textContent = "Piezas";
    const cantidad = document.createElement("input");
    cantidad.type = "number";
    cantidad.min = "1";
    cantidad.value = "1";
    cantidad.dataset.testid = "qty";
    etiqueta.append(cantidad);

    const boton = document.createElement("button");
    boton.type = "button";
    boton.dataset.testid = "add-to-cart";
    boton.textContent = producto.stock === 0 ? "Agotado" : "Agregar";
    boton.disabled = producto.stock === 0;
    boton.addEventListener("click", () => agregar(producto.id, Number(cantidad.value)));
    acciones.append(etiqueta, boton);
    card.append(categoria, titulo, detalle, precio, existencia, acciones);
    grid.append(card);
  }
  status.dataset.state = "ready";
  status.textContent = `${visibles.length} piezas en esta vista · ${estado.productos.length} en el catálogo`;
}

function pintarFiltros() {
  for (const categoria of estado.categorias) {
    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = "chip";
    boton.dataset.testid = "category-filter";
    boton.dataset.category = categoria.id;
    boton.textContent = categoria.nombre;
    boton.setAttribute("aria-pressed", "false");
    boton.addEventListener("click", () => seleccionarFiltro(categoria.id));
    filtros.append(boton);
  }
  filtros.querySelector("[data-category='todas']").addEventListener("click", () => seleccionarFiltro("todas"));
}

function seleccionarFiltro(id) {
  estado.filtro = id;
  for (const boton of filtros.querySelectorAll("[data-testid='category-filter']")) {
    const activo = boton.dataset.category === id;
    boton.classList.toggle("is-on", activo);
    boton.setAttribute("aria-pressed", activo ? "true" : "false");
  }
  pintarCatalogo();
}

function agregar(id, cantidad) {
  const producto = estado.productos.find((candidato) => candidato.id === id);
  if (!producto) return;
  if (!Number.isInteger(cantidad) || cantidad < 1) {
    mostrarAviso("stock", "Indica una cantidad entera, de una pieza en adelante.");
    return;
  }
  const enCarrito = estado.carrito.find((linea) => linea.id === id)?.cantidad || 0;
  if (producto.stock < 1 || enCarrito + cantidad > producto.stock) {
    mostrarAviso("stock", `Stock insuficiente: solo queda ${producto.stock} de ${producto.nombre}.`);
    return;
  }
  limpiarAviso();
  if (enCarrito) {
    estado.carrito = estado.carrito.map((linea) =>
      linea.id === id ? { ...linea, cantidad: linea.cantidad + cantidad } : linea,
    );
  } else {
    estado.carrito.push({
      id: producto.id,
      nombre: producto.nombre,
      precio: producto.precio,
      cantidad,
    });
  }
  pintarCarrito();
  document.querySelector("[data-testid='cart-panel']").scrollIntoView({ block: "nearest" });
}

formulario.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  if (estado.carrito.length === 0) {
    mostrarAviso("vacio", "El carrito está vacío. Agrega una pieza antes de confirmar.");
    folio.hidden = true;
    folio.dataset.folio = "";
    folio.textContent = "";
    return;
  }
  const datos = new FormData(formulario);
  const respuesta = await fetch("/api/pedidos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      cliente: {
        nombre: String(datos.get("nombre") || ""),
        correo: String(datos.get("correo") || ""),
      },
      items: estado.carrito.map((linea) => ({ productoId: linea.id, cantidad: linea.cantidad })),
    }),
  });
  const cuerpo = await respuesta.json();
  if (!respuesta.ok) {
    mostrarAviso("pedido", cuerpo.error || "No se pudo confirmar el pedido.");
    return;
  }
  limpiarAviso();
  estado.carrito = [];
  pintarCarrito();
  folio.hidden = false;
  folio.dataset.folio = cuerpo.id;
  folio.textContent = `Pedido confirmado. Folio ${cuerpo.id}. Total ${dinero.format(cuerpo.total)}.`;
  await cargar();
});

async function cargar() {
  const [productosRes, categoriasRes] = await Promise.all([
    fetch("/api/productos"),
    fetch("/api/categorias"),
  ]);
  if (!productosRes.ok || !categoriasRes.ok) {
    status.dataset.state = "error";
    status.dataset.testid = "catalog-error";
    status.textContent = "No se pudo cargar el catálogo.";
    return;
  }
  estado.productos = (await productosRes.json()).productos;
  if (estado.categorias.length === 0) {
    estado.categorias = (await categoriasRes.json()).categorias;
    pintarFiltros();
  }
  pintarCatalogo();
}

pintarCarrito();
cargar().catch(() => {
  status.dataset.state = "error";
  status.textContent = "No se pudo cargar el catálogo.";
});

const CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function crearPedido(productos, secuencia, solicitud) {
  if (!solicitud || typeof solicitud !== "object") {
    return fallo(400, "El cuerpo del pedido no es válido");
  }

  const items = Array.isArray(solicitud.items) ? solicitud.items : null;
  if (!items || items.length === 0) {
    return fallo(400, "El carrito está vacío");
  }

  const cliente = solicitud.cliente || {};
  const nombre = typeof cliente.nombre === "string" ? cliente.nombre.trim() : "";
  const correo = typeof cliente.correo === "string" ? cliente.correo.trim() : "";
  if (nombre.length < 2) {
    return fallo(400, "El nombre del cliente es obligatorio");
  }
  if (!CORREO.test(correo)) {
    return fallo(400, "El correo del cliente no es válido");
  }

  const copia = productos.map((producto) => ({ ...producto }));
  const lineas = [];

  for (const item of items) {
    const productoId = item?.productoId;
    const producto = copia.find((candidato) => candidato.id === productoId);
    if (!producto) {
      return fallo(404, `No existe el producto ${productoId}`);
    }
    const cantidad = item.cantidad;
    if (!Number.isInteger(cantidad) || cantidad < 1) {
      return fallo(400, "La cantidad debe ser un entero positivo");
    }
    if (cantidad > producto.stock) {
      return fallo(409, `Stock insuficiente para ${producto.nombre}`);
    }
    producto.stock -= cantidad;
    lineas.push({
      productoId: producto.id,
      nombre: producto.nombre,
      cantidad,
      precio: producto.precio,
      subtotal: producto.precio * cantidad,
    });
  }

  const total = lineas.reduce((suma, linea) => suma + linea.subtotal, 0);
  return {
    ok: true,
    productos: copia,
    pedido: {
      id: `LM-${String(secuencia).padStart(4, "0")}`,
      estado: "confirmado",
      total,
      moneda: "MXN",
      items: lineas,
      cliente: { nombre, correo },
    },
  };
}

function fallo(status, error) {
  return { ok: false, status, error };
}

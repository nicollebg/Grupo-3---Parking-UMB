"use strict";

const $ = (id) => document.getElementById(id);
const ICONOS = { carro: "i-carro", moto: "i-moto", bicicleta: "i-bicicleta" };
const moneda = (n) => "$" + Number(n || 0).toLocaleString("es-CO");
const esc = (t) => String(t).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const icono = (tipo, clase = "ic") => `<svg class="${clase}"><use href="#${ICONOS[tipo] || "i-carro"}"/></svg>`;

/* ---------- Comunicación con la API ---------- */
async function api(ruta, cuerpo) {
  const opciones = cuerpo
    ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(cuerpo) }
    : {};
  const resp = await fetch(ruta, opciones);
  const datos = await resp.json();
  if (!resp.ok) throw new Error(datos.error || "Ocurrió un error.");
  return datos;
}

/* ---------- Avisos ---------- */
function avisar(texto, error = false) {
  const el = document.createElement("div");
  el.className = "aviso" + (error ? " error" : "");
  el.textContent = texto;
  $("avisos").appendChild(el);
  setTimeout(() => el.remove(), 4200);
}

/* ---------- Dibujo ---------- */
function dibujarIndicadores(e) {
  $("kpi-libres").textContent = e.disponibles;
  $("kpi-capacidad").textContent = e.capacidad;
  $("kpi-ocupados").textContent = e.ocupados;
  $("kpi-recaudado").textContent = moneda(e.recaudado);
  $("kpi-salidas").textContent = `${e.historial.length} salida${e.historial.length === 1 ? "" : "s"} registrada${e.historial.length === 1 ? "" : "s"}`;
  $("kpi-nota").textContent = e.disponibles === 0 ? "Parqueadero lleno" : e.ocupados === 0 ? "Parqueadero vacío" : `${Math.round((e.ocupados / e.capacidad) * 100)}% de ocupación`;
  $("barra-ocupacion").style.width = (e.ocupados / e.capacidad) * 100 + "%";
}

function dibujarPlano(e) {
  const huecos = [];
  for (let i = 0; i < e.capacidad; i++) {
    const v = e.activos[i];
    const n = String(i + 1).padStart(2, "0");
    huecos.push(v
      ? `<div class="bahia ocupada">
           ${icono(v.tipo, "ic ic-grande")}
           <span class="placa">${esc(v.placa)}</span>
           <span class="dato">${esc(v.tipo)} · <b>${v.minutos} min</b><br>A pagar hoy: <b>${moneda(v.estimado)}</b></span>
           <button class="btn mini" data-salida="${esc(v.placa)}" type="button"><svg class="ic"><use href="#i-salir"/></svg>Cobrar</button>
           <span class="numero">${n}</span>
         </div>`
      : `<div class="bahia libre">
           <svg class="ic ic-grande"><use href="#i-carro"/></svg>
           <span class="estado-txt">LIBRE</span>
           <span class="numero">${n}</span>
         </div>`);
  }
  $("bahias").innerHTML = huecos.join("");
  $("lista-activos").innerHTML = e.activos.map((v) => `<option value="${esc(v.placa)}">`).join("");
}

function dibujarHistorial(e) {
  $("tabla-historial").innerHTML = e.historial.length
    ? e.historial.map((r) => `<tr>
        <td><span class="mini-placa">${esc(r.placa)}</span></td>
        <td>${esc(r.tipo)}</td><td>${esc(r.entrada)}</td><td>${esc(r.salida)}</td>
        <td class="num">${r.minutos}</td><td class="num valor">${moneda(r.valor)}</td></tr>`).join("")
    : `<tr><td class="vacio" colspan="6">Aún no hay salidas registradas.</td></tr>`;
}

function dibujarEventos(e) {
  $("eventos").innerHTML = e.eventos.length
    ? e.eventos.map((ev) => `<li class="${esc(ev.evento)}">
        <span class="hora">${esc(ev.hora)}</span>
        <span class="flecha">${ev.evento === "entrada" ? "→" : "←"}</span>
        <span><b>${ev.evento === "entrada" ? "Ingreso" : "Salida"}</b> ${esc(ev.tipo)} <span class="mini-placa">${esc(ev.placa)}</span></span>
        <span class="libres">Libres: ${ev.disponibles}</span></li>`).join("")
    : `<li style="border-left-color:var(--borde);color:var(--apagado)">Sin eventos todavía. Registra una entrada para ver las notificaciones.</li>`;
}

function dibujar(e) {
  dibujarIndicadores(e); dibujarPlano(e); dibujarHistorial(e); dibujarEventos(e);
}

/* ---------- Estado ---------- */
function conexion(ok) {
  const el = $("estado-conexion");
  el.className = "estado " + (ok ? "ok" : "mal");
  el.lastElementChild.textContent = ok ? "Sistema operando" : "Sin conexión";
}

async function actualizar() {
  try { dibujar(await api("/api/estado")); conexion(true); }
  catch { conexion(false); }
}

/* ---------- Acciones ---------- */
function mostrarTicket(r) {
  $("tk-placa").textContent = r.placa;
  $("tk-tipo").textContent = r.tipo;
  $("tk-entrada").textContent = r.entrada;
  $("tk-salida").textContent = r.salida;
  $("tk-min").textContent = r.minutos + " min";
  $("tk-valor").textContent = moneda(r.valor);
  $("velo").hidden = false;
  $("tk-cerrar").focus();
}

async function registrarSalida(placa) {
  try {
    const r = await api("/api/salida", { placa });
    $("placa-salida").value = "";
    mostrarTicket(r);
    await actualizar();
  } catch (err) { avisar(err.message, true); }
}

$("form-entrada").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const placa = $("placa-entrada").value;
  const tipo = document.querySelector("input[name=tipo]:checked").value;
  try {
    const r = await api("/api/entrada", { placa, tipo });
    avisar(`Entrada registrada: ${r.placa} (${r.tipo})`);
    $("placa-entrada").value = "";
    $("placa-entrada").focus();
    await actualizar();
  } catch (err) { avisar(err.message, true); }
});

$("form-salida").addEventListener("submit", (ev) => { ev.preventDefault(); registrarSalida($("placa-salida").value); });
$("bahias").addEventListener("click", (ev) => {
  const b = ev.target.closest("[data-salida]");
  if (b) registrarSalida(b.dataset.salida);
});
$("tk-cerrar").addEventListener("click", () => { $("velo").hidden = true; });
$("velo").addEventListener("click", (ev) => { if (ev.target === $("velo")) $("velo").hidden = true; });
document.addEventListener("keydown", (ev) => { if (ev.key === "Escape") $("velo").hidden = true; });

/* ---------- Reloj y arranque ---------- */
const pintarReloj = () => { $("reloj").textContent = new Date().toLocaleTimeString("es-CO", { hour12: false }); };
pintarReloj(); setInterval(pintarReloj, 1000);
actualizar(); setInterval(actualizar, 3000);
"use strict";

const $ = (id) => document.getElementById(id);
const ICONOS = { carro: "i-carro", moto: "i-moto", bicicleta: "i-bicicleta" };
const PLAN_NOMBRE = { normal: "Normal", nocturna: "Nocturna", convenio: "Convenio", mensualidad: "Mensualidad" };

// Ayuda del formato de placa segun el tipo (formatos colombianos)
const FORMATOS = {
  carro: { etiqueta: "Placa del carro", ejemplo: "ABC123", pista: "3 letras y 3 números" },
  moto: { etiqueta: "Placa de la moto", ejemplo: "ABC12D", pista: "3 letras, 2 números y 1 letra" },
  bicicleta: { etiqueta: "Código de la bicicleta", ejemplo: "BIC001", pista: "Las bicicletas no tienen placa: use el código o serial del marco (5 a 7 letras o números)" },
};

const moneda = (n) => "$" + Number(n || 0).toLocaleString("es-CO");
const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const icono = (tipo, clase = "ic") => `<svg class="${clase}"><use href="#${ICONOS[tipo] || "i-carro"}"/></svg>`;
const insignia = (plan) => `<span class="insignia ${esc(plan)}">${esc(PLAN_NOMBRE[plan] || plan)}</span>`;

let planesInfo = [];
let reporteActual = null;
let firmaLibres = "";
let espacioElegido = "";

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

function avisar(texto, error = false) {
  const el = document.createElement("div");
  el.className = "aviso" + (error ? " error" : "");
  el.textContent = texto;
  $("avisos").appendChild(el);
  setTimeout(() => el.remove(), 4500);
}

/* ---------- Indicadores ---------- */
function dibujarIndicadores(e) {
  $("kpi-libres").textContent = e.disponibles;
  $("kpi-capacidad").textContent = e.capacidad;
  $("kpi-ocupados").textContent = e.ocupados;
  $("kpi-salidas").textContent = e.historial.length;
  $("kpi-recaudado").textContent = moneda(e.recaudado);
  $("kpi-nota").textContent = e.disponibles === 0 ? "Parqueadero lleno" : e.ocupados === 0 ? "Parqueadero vacío" : `${Math.round((e.ocupados / e.capacidad) * 100)}% de ocupación`;
  $("barra-ocupacion").style.width = (e.ocupados / e.capacidad) * 100 + "%";
}

/* ---------- Plano con espacios numerados ---------- */
function dibujarPlano(e) {
  $("bahias").innerHTML = e.espacios.map(({ numero, registro: v }) => {
    const n = String(numero).padStart(2, "0");
    if (v) {
      return `<div class="bahia ocupada">
        <span class="numero">${n}</span>
        ${icono(v.tipo, "ic ic-grande")}
        <span class="placa">${esc(v.placa)}</span>
        ${insignia(v.plan)}
        <span class="dato">${esc(v.tipo)} · <b>${v.minutos} min</b><br>A pagar hoy: <b>${moneda(v.estimado)}</b></span>
        <button class="btn mini" data-salida="${esc(v.placa)}" type="button"><svg class="ic"><use href="#i-salir"/></svg>Cobrar</button>
      </div>`;
    }
    const elegida = String(numero) === espacioElegido ? " elegida" : "";
    return `<button class="bahia libre${elegida}" data-espacio="${numero}" type="button" aria-label="Espacio ${numero} libre">
      <span class="numero">${n}</span>
      <svg class="ic ic-grande"><use href="#i-carro"/></svg>
      <span class="estado-txt">LIBRE</span>
      <span class="elegir">Toca para elegir</span>
    </button>`;
  }).join("");

  $("lista-activos").innerHTML = e.activos.map((v) => `<option value="${esc(v.placa)}">`).join("");

  // Solo se reconstruye el selector si cambió el conjunto de espacios libres
  const firma = e.libres.join(",");
  if (firma !== firmaLibres) {
    firmaLibres = firma;
    if (!e.libres.map(String).includes(espacioElegido)) espacioElegido = "";
    $("espacio").innerHTML = `<option value="">Automático</option>` +
      e.libres.map((n) => `<option value="${n}">Espacio ${n}</option>`).join("");
    $("espacio").value = espacioElegido;
  }
}

function marcarEspacio(valor) {
  espacioElegido = String(valor || "");
  $("espacio").value = espacioElegido;
  document.querySelectorAll(".bahia.libre").forEach((b) => b.classList.toggle("elegida", b.dataset.espacio === espacioElegido));
}

/* ---------- Historial y actividad ---------- */
function dibujarHistorial(e) {
  $("tabla-historial").innerHTML = e.historial.length
    ? e.historial.map((r) => `<tr>
        <td><span class="mini-placa">${esc(r.placa)}</span></td>
        <td>${esc(r.tipo)}</td><td>${insignia(r.plan)}</td><td class="num">${esc(r.espacio)}</td>
        <td>${esc(r.entrada)}</td><td>${esc(r.salida)}</td>
        <td class="num">${r.minutos}</td><td class="num valor">${moneda(r.valor)}</td></tr>`).join("")
    : `<tr><td class="vacio" colspan="8">Aún no hay salidas registradas.</td></tr>`;
}

function dibujarEventos(e) {
  $("eventos").innerHTML = e.eventos.length
    ? e.eventos.map((ev) => `<li class="${esc(ev.evento)}">
        <span class="hora">${esc(ev.hora)}</span>
        <span class="flecha">${ev.evento === "entrada" ? "→" : "←"}</span>
        <span><b>${ev.evento === "entrada" ? "Ingreso" : "Salida"}</b> ${esc(ev.tipo)} <span class="mini-placa">${esc(ev.placa)}</span></span>
        <span class="libres">Libres: ${ev.disponibles}</span></li>`).join("")
    : `<li style="background:#f6f4fb;border-left-color:#cfc8e6;color:#6e6882">Sin eventos todavía. Registra una entrada para ver las notificaciones.</li>`;
}

/* ---------- Planes de tarifa ---------- */
function prepararPlanes(e) {
  if (planesInfo.length) return;
  planesInfo = e.planes;
  $("plan").innerHTML = planesInfo.map((p) => `<option value="${esc(p.clave)}">${esc(p.nombre)}</option>`).join("");
  $("lista-planes").innerHTML = planesInfo.filter((p) => p.clave !== "normal")
    .map((p) => `<li>${insignia(p.clave)}<br>${esc(p.descripcion)}</li>`).join("");
  mostrarDescripcionPlan();
}

function mostrarDescripcionPlan() {
  const p = planesInfo.find((x) => x.clave === $("plan").value);
  $("plan-desc").textContent = p ? p.descripcion : "";
}

/* ---------- Formato de placa por tipo ---------- */
function actualizarFormato() {
  const tipo = document.querySelector("input[name=tipo]:checked").value;
  const f = FORMATOS[tipo];
  $("etiqueta-placa").textContent = f.etiqueta;
  $("placa-entrada").placeholder = f.ejemplo;
  $("pista-placa").textContent = f.pista;
}

/* ---------- Reporte por fecha ---------- */
async function cargarReporte() {
  try {
    const fecha = $("fecha-reporte").value;
    const r = await api("/api/reporte" + (fecha ? `?fecha=${encodeURIComponent(fecha)}` : ""));
    reporteActual = r;
    if (!fecha) $("fecha-reporte").value = r.fecha;
    $("rep-salidas").textContent = r.salidas;
    $("rep-total").textContent = moneda(r.total);
    const filas = (lista, clave, nombre) => lista.length
      ? lista.map((x) => `<tr><td>${nombre(x[clave])}</td><td class="num">${x.cantidad}</td><td class="num valor">${moneda(x.total)}</td></tr>`).join("")
      : `<tr><td class="vacio" colspan="3">Sin salidas ese día.</td></tr>`;
    $("rep-tipos").innerHTML = filas(r.por_tipo, "tipo", esc);
    $("rep-planes").innerHTML = filas(r.por_plan, "plan", insignia);
  } catch (err) { /* la conexión se muestra en el estado general */ }
}

function descargarCSV() {
  if (!reporteActual) return;
  const filas = [["placa", "tipo", "plan", "espacio", "entrada", "salida", "minutos", "valor"]]
    .concat(reporteActual.registros.map((r) => [r.placa, r.tipo, r.plan, r.espacio, r.entrada, r.salida, r.minutos, r.valor]));
  const csv = filas.map((f) => f.join(",")).join("\n");
  const enlace = document.createElement("a");
  enlace.href = URL.createObjectURL(new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8" }));
  enlace.download = `reporte_${reporteActual.fecha}.csv`;
  enlace.click();
  URL.revokeObjectURL(enlace.href);
}

/* ---------- Estado general ---------- */
function conexion(ok) {
  const el = $("estado-conexion");
  el.className = "estado " + (ok ? "ok" : "mal");
  el.lastElementChild.textContent = ok ? "Sistema operando" : "Sin conexión";
}

async function actualizar() {
  try {
    const e = await api("/api/estado");
    prepararPlanes(e);
    dibujarIndicadores(e); dibujarPlano(e); dibujarHistorial(e); dibujarEventos(e);
    conexion(true);
    await cargarReporte();
  } catch { conexion(false); }
}

/* ---------- Acciones ---------- */
function mostrarTicket(r) {
  $("tk-placa").textContent = r.placa;
  $("tk-tipo").textContent = r.tipo;
  $("tk-plan").textContent = PLAN_NOMBRE[r.plan] || r.plan;
  $("tk-espacio").textContent = r.espacio;
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
  const tipo = document.querySelector("input[name=tipo]:checked").value;
  try {
    const r = await api("/api/entrada", {
      placa: $("placa-entrada").value, tipo,
      plan: $("plan").value, espacio: $("espacio").value,
    });
    avisar(`Entrada registrada: ${r.placa} en el espacio ${r.espacio} (${PLAN_NOMBRE[r.plan]})`);
    $("placa-entrada").value = "";
    espacioElegido = ""; firmaLibres = "";
    $("placa-entrada").focus();
    await actualizar();
  } catch (err) { avisar(err.message, true); }
});

$("form-salida").addEventListener("submit", (ev) => { ev.preventDefault(); registrarSalida($("placa-salida").value); });
$("bahias").addEventListener("click", (ev) => {
  const salida = ev.target.closest("[data-salida]");
  if (salida) return registrarSalida(salida.dataset.salida);
  const libre = ev.target.closest("[data-espacio]");
  if (libre) marcarEspacio(espacioElegido === libre.dataset.espacio ? "" : libre.dataset.espacio);
});
document.querySelectorAll("input[name=tipo]").forEach((r) => r.addEventListener("change", actualizarFormato));
$("plan").addEventListener("change", mostrarDescripcionPlan);
$("espacio").addEventListener("change", () => marcarEspacio($("espacio").value));
$("fecha-reporte").addEventListener("change", cargarReporte);
$("btn-csv").addEventListener("click", descargarCSV);
$("tk-cerrar").addEventListener("click", () => { $("velo").hidden = true; });
$("velo").addEventListener("click", (ev) => { if (ev.target === $("velo")) $("velo").hidden = true; });
document.addEventListener("keydown", (ev) => { if (ev.key === "Escape") $("velo").hidden = true; });

/* ---------- Reloj y arranque ---------- */
const pintarReloj = () => { $("reloj").textContent = new Date().toLocaleTimeString("es-CO", { hour12: false }); };
pintarReloj(); setInterval(pintarReloj, 1000);
actualizarFormato();
actualizar(); setInterval(actualizar, 3000);
import DOMPurify from 'dompurify';
import escapeHtml from 'escape-html';

const lista = document.getElementById('resultados');

export function limpiar() {
  lista.innerHTML = '';
}

export function titulo() {
  document.querySelector('h1').innerHTML = '<span>Resultados</span>';
}

export function mostrar(items) {
  lista.textContent = items.join(', ');
}

export function rico(html) {
  lista.innerHTML = DOMPurify.sanitize(html);
}

export function escapado(nombre) {
  lista.innerHTML = escapeHtml(nombre);
}

// Reescribe el HTML que el propio elemento ya tenía.
export function recortar(elemento) {
  elemento.innerHTML = elemento.innerHTML.trim();
}

// Constant markup that contains the other quote character, or only literals joined.
export function barra() {
  $("#toolbar").html('<button id="saveButton" type="button" class="btn">Save</button>');
  $("#nota").html("<a href='/ayuda'>Help</a>" + '<i class="icono"></i>');
  $("#plantilla").html(`<b class="q">fijo</b>`);
  lista.innerHTML = '<li class="it">it\'s fixed</li>';
}

// A variable assigned only from literals.
export function opciones(n) {
  var s = '<option value="1">A</option>';
  $("#opt").html(s);
  var t = n ? '<i class="a">a</i>' : '<i class="b">b</i>';
  $("#opt2").html(t);
}

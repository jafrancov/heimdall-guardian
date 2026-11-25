const lista = document.getElementById('resultados');

export function mostrar(items) {
  lista.innerHTML = items.map((i) => `<li>${i.nombre}</li>`).join('');
}

export function aviso(texto) {
  document.querySelector('#aviso').outerHTML = '<div class="aviso">' + texto + '</div>';
}

export function escribir(html) {
  document.write(html);
}

export function agregar(fragmento) {
  lista.insertAdjacentHTML('beforeend', fragmento);
}

export function jq(contenido) {
  $('#panel').html(contenido);
}

export function mostrarDatos(data, userInput) {
  $('#nombre').html('<b>' + data.name + '</b>');
  $('#entrada').html(userInput);
  document.body.innerHTML = location.hash;
}

// A literal that may be replaced by user data is still reported.
export function mixto(c, u) {
  var s = '<a>x</a>';
  if (c) { s = u; }
  $('#m1').html(s);
  $('#m2').html('<a class="x">' + u + '</a>');
  $('#m3').html(`<b class="q">${u}</b>`);
}

function pateiktiKeitima() {
  const diena = document.getElementById('diena').value.trim();
  const nuo = document.getElementById('nuo').value.trim();
  const iki = document.getElementById('iki').value.trim();
  const aprasymas = document.getElementById('aprasymas').value.trim();

  if (!diena || !nuo || !iki || !aprasymas) {
    alert('Klaida: prašome užpildyti visus laukus.');
    return;
  }

  alert('Grafiko keitimo užklausa sėkmingai pateikta!');
  window.location.href = '/grafikai/';
}

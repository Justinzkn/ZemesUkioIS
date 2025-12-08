function pateiktiUzklausa() {
  const tipas = document.getElementById('tipas').value.trim();
  const aprasymas = document.getElementById('aprasymas').value.trim();

  if (!tipas || !aprasymas) {
    alert('Klaida: prašome užpildyti visus laukus.');
    return;
  }

  alert('Užklausa sėkmingai pateikta!');
  window.location.href = '/grafikai/';
}

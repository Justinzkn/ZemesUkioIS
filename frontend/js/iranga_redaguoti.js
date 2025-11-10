function issaugoti() {
  const pavadinimas = document.getElementById('pavadinimas').value.trim();
  const tipas = document.getElementById('tipas').value.trim();
  const busena = document.getElementById('busena').value.trim();
  const vieta = document.getElementById('vieta').value.trim();

  if (!pavadinimas || !tipas || !busena || !vieta) {
    alert('Klaida: visi laukai yra privalomi!');
    return;
  }

  alert('Pakeitimai sėkmingai išsaugoti!');
  window.location.href = '/iranga/';
}

// Quick sanity check that JS is loaded
console.log("grafikai.js loaded");

// In case some template/IDE injected 'disabled' somewhere, force-enable our buttons.
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.add-btn,.change-btn,.filter-btn,.clear-btn')
    .forEach(b => b.disabled = false);
});

function filtruotiGrafika() {
  const nuo = document.getElementById('date-from').value;
  const iki = document.getElementById('date-to').value;

  if (!nuo || !iki) {
    alert("Pasirinkite abu laikotarpio laukus!");
    return;
  }

  alert(`Filtruojamas darbo grafikas nuo ${nuo} iki ${iki}.`);
}

function isvalytiFiltra() {
  document.getElementById('date-from').value = '';
  document.getElementById('date-to').value = '';
  alert("Filtras išvalytas.");
}

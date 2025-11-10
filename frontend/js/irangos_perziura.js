console.log('Įrangos peržiūros puslapis įkeltas.');

document.getElementById("filterInput").addEventListener("keyup", filtruoti);
document.getElementById("typeFilter").addEventListener("change", filtruoti);

function filtruoti() {
  const tekstas = document.getElementById("filterInput").value.toLowerCase();
  const tipas = document.getElementById("typeFilter").value.toLowerCase();
  const eilutes = document.querySelectorAll("table tbody tr");

  eilutes.forEach(row => {
    const tekstasEilute = row.textContent.toLowerCase();
    const tipasEilute = row.querySelector("td:nth-child(2)")?.textContent.toLowerCase() || "";
    const rodyti = tekstasEilute.includes(tekstas) && (tipas === "" || tipasEilute.includes(tipas));
    row.style.display = rodyti ? "" : "none";
  });
}

function isvalytiFiltra() {
  document.getElementById("filterInput").value = "";
  document.getElementById("typeFilter").value = "";
  filtruoti();
}
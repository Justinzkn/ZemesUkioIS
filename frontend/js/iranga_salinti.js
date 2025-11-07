const irangosDuomenys = {
  1: { pavadinimas: "Traktorius", tipas: "Technika", busena: "Veikianti", vieta: "Sandėlys A" },
  2: { pavadinimas: "Kultivatorius", tipas: "Technika", busena: "Remontuojama", vieta: "Sandėlys B" },
  3: { pavadinimas: "Sėjamoji", tipas: "Technika", busena: "Veikianti", vieta: "Sandėlys A" }
};

function rodytiInfo() {
  const id = document.getElementById("id").value;
  const infoBox = document.getElementById("info");
  if (id && irangosDuomenys[id]) {
    const duom = irangosDuomenys[id];
    document.getElementById("pavadinimas").textContent = duom.pavadinimas;
    document.getElementById("tipas").textContent = duom.tipas;
    document.getElementById("busena").textContent = duom.busena;
    document.getElementById("vieta").textContent = duom.vieta;
    infoBox.style.display = "block";
  } else {
    infoBox.style.display = "none";
  }
}

function salintiIranga() {
  const id = document.getElementById("id").value;
  if (!id) {
    alert("Pasirinkite įrangos ID!");
    return;
  }
  const patvirtinimas = confirm("Ar tikrai norite pašalinti įrangą ID: " + id + "?");
  if (patvirtinimas) {
    alert("Įranga ID " + id + " sėkmingai pašalinta.");
    window.location.href = "/iranga/";
  }
}

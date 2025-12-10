// frontend/js/likuciu_zemelapis.js

document.addEventListener("DOMContentLoaded", function () {
  const data = window.ZIS_LIKUCIAI || { matavimo_vnt: "", sandeliai: [] };

  const mapElement = document.getElementById("map");
  if (!mapElement) {
    console.warn("Nerastas #map elementas");
    return;
  }

  // Inicializuojam žemėlapį
  const map = L.map("map");

  // Pagrindinis sluoksnis (OpenStreetMap)
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map);

  // Jei nėra sandėlių – tiesiog rodom Lietuvą
  if (!data.sandeliai || data.sandeliai.length === 0) {
    map.setView([55.25, 23.88], 7); // apytikslė LT vidurio koordinatė
    return;
  }

  const bounds = L.latLngBounds();

  data.sandeliai.forEach((s) => {
    const lat = parseFloat(s.lat);
    const lng = parseFloat(s.lng);

    if (isNaN(lat) || isNaN(lng)) {
      console.warn("Blogos koordinatės sandėliui:", s);
      return;
    }

    const marker = L.marker([lat, lng]).addTo(map);

    const popupHtml = `
      <strong>${s.name}</strong><br>
      ${s.address}<br>
      Likutis: ${s.qty} ${data.matavimo_vnt}
    `;

    marker.bindPopup(popupHtml);
    bounds.extend([lat, lng]);
  });

  if (bounds.isValid()) {
    map.fitBounds(bounds, { padding: [40, 40] });
  } else {
    map.setView([55.25, 23.88], 7);
  }
});

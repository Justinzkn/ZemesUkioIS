console.log("Pagrindinis puslapis įkeltas ✅");

document.querySelectorAll(".card").forEach(card => {
  card.addEventListener("click", () => {
    alert("Šis puslapis bus sukurtas vėliau!");
  });
});

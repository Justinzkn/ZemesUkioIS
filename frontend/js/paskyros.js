document.querySelectorAll(".delete").forEach(btn => {
  btn.addEventListener("click", () => {
    alert("Paskyra pašalinta (testinis veiksmas)");
  });
});

document.querySelectorAll(".edit").forEach(btn => {
  btn.addEventListener("click", () => {
    alert("Atidarytas paskyros redagavimas (testinis veiksmas)");
  });
});
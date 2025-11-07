console.log("Užklausų sąrašas įkeltas ✅");

document.querySelectorAll(".delete").forEach(btn => {
  btn.addEventListener("click", () => {
    alert("Užklausa ištrinta (testinis veiksmas)");
  });
});
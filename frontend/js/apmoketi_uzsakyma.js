// Apmokėjimo lango JS
// Šiuo metu nieko nedarom su "Patvirtinti mokėjimą" mygtuku – 
// leidžiam formai natūraliai būti pateiktai į Django (Stripe integracijai).

document.addEventListener('DOMContentLoaded', function () {
  const backBtn = document.querySelector('.back');
  if (backBtn) {
    backBtn.addEventListener('click', function (e) {
      e.preventDefault();
      window.location.href = '/uzsakymai/';
    });
  }
});

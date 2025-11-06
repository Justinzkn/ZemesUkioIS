
console.log('Apmokėjimo langas įkeltas ✅');

document.querySelector('.confirm').addEventListener('click', ()=>{
  alert('Mokėjimas atliktas (placeholder).');
});

document.querySelector('.cancel').addEventListener('click', ()=>{
  alert('Mokėjimas atšauktas (placeholder).');
});

document.querySelector('.back').addEventListener('click', ()=>{
  window.location.href = '/uzsakymai/';
});

console.log('Redaguoti užsakymą UI įkeltas ✅');

document.querySelector('.save').addEventListener('click', ()=>{
  alert('Pakeitimai išsaugoti (placeholder).');
});

document.querySelector('.cancel-order').addEventListener('click', ()=>{
  alert('Užsakymas pažymėtas kaip atšauktas (placeholder).');
});

document.querySelector('.back').addEventListener('click', ()=>{
  window.location.href = '/uzsakymai/';
});

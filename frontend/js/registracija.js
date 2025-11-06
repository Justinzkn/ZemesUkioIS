console.log("Registracija įkelta ✅");

document.querySelector('.confirm').addEventListener('click', ()=>{
  alert("Registracija sėkminga (placeholder).");
});

document.querySelector('.cancel').addEventListener('click', ()=>{
  alert("Registracija atšaukta (placeholder).");
});

document.querySelector('.back').addEventListener('click', ()=>{
  window.location.href = "/prisijungimas/";
});

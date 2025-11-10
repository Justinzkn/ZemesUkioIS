function sukomplektuoti() {
  const pagrindine = document.getElementById('pagrindine').value;
  const papildoma = Array.from(document.getElementById('papildoma').selectedOptions).map(opt => opt.value);
  const resultBox = document.getElementById('rezultatas');

  if (!pagrindine || papildoma.length === 0) {
    resultBox.style.display = 'block';
    resultBox.style.color = 'red';
    resultBox.textContent = 'Klaida: pasirinkite pagrindinę ir papildomą įrangą!';
    return;
  }

  const sėkminga = Math.random() > 0.3; // 70% šansų sėkmingai sukomplektuoti

  resultBox.style.display = 'block';
  if (sėkminga) {
    resultBox.style.color = 'green';
    resultBox.textContent = `✅ Įranga „${pagrindine}“ sėkmingai sukomplektuota su: ${papildoma.join(', ')}.`;
  } else {
    resultBox.style.color = 'red';
    resultBox.textContent = '❌ Nepavyko sukomplektuoti įrangos. Patikrinkite pasirinkimus.';
  }
}

const form = document.getElementById('grafikoForma');
const resultDiv = document.getElementById('rezultatas');
const downloadBtn = document.getElementById('atsisiusti');

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const darbuotojas = document.getElementById('darbuotojas').value;
  const nuo = document.getElementById('nuo').value;
  const iki = document.getElementById('iki').value;

  if (!darbuotojas || !nuo || !iki) {
    resultDiv.textContent = 'Užpildykite visus laukus!';
    resultDiv.style.color = 'red';
    return;
  }

  resultDiv.textContent = 'Generuojamas grafikas...';
  resultDiv.style.color = '#0C3B2E';

  setTimeout(() => {
    const success = Math.random() > 0.3;

    if (success) {
      resultDiv.textContent = 'Grafikas sėkmingai sugeneruotas!';
      resultDiv.style.color = 'green';
      downloadBtn.disabled = false;
    } else {
      resultDiv.textContent = 'Nepavyko sugeneruoti grafiko!';
      resultDiv.style.color = 'red';
      downloadBtn.disabled = true;
    }
  }, 1500);
});

downloadBtn.addEventListener('click', () => {
  alert('PDF failas būtų atsiųstas (testinis veiksmas)');
});
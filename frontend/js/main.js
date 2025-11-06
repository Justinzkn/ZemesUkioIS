document.addEventListener('DOMContentLoaded', function() {
    
    console.log("Puslapis sėkmingai užkrautas ir main.js veikia!");

    // Surandame mygtuką pagal jo ID
    const ctaButton = document.getElementById('cta-button');

    // Patikriname, ar mygtukas rastas
    if (ctaButton) {
        // Pridedame "click" įvykio klausytoją
        ctaButton.addEventListener('click', function() {
            // Kol kas, paspaudus mygtuką, išvesime pranešimą į konsolę
            console.log("Mygtukas 'Sužinoti Daugiau' buvo paspaustas!");
            
            // Ateityje čia galėsite pridėti sudėtingesnę logiką,
            // pvz., parodyti iššokantį langą arba nukreipti į kitą puslapį.
            alert("Ačiū už susidomėjimą! Funkcionalumas dar kuriamas.");
        });
    }

});
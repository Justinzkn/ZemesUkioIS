document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("generuoti");
    const select = document.getElementById("preke");
    const map = document.getElementById("zemelapis");

    button.addEventListener("click", () => {
        const preke = select.value;
        map.innerHTML = "";

        if (!preke) {
            map.innerHTML = "<p style='color:red;'>Nepasirinkta prekė – žemėlapis negali būti sugeneruotas.</p>";
            return;
        }

        const sandeliai = [
            { id: "A", pavadinimas: "Sandėlis A", kiekis: "80%" },
            { id: "B", pavadinimas: "Sandėlis B", kiekis: "40%" },
            { id: "C", pavadinimas: "Sandėlis C", kiekis: "10%" },
        ];

        sandeliai.forEach(s => {
            const el = document.createElement("div");
            el.classList.add("sandelis");
            el.id = s.id;
            el.textContent = `${s.pavadinimas}\n${s.kiekis}`;
            map.appendChild(el);
        });
    });
});

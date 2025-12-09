// paprasta globali funkcija, kad veiktų su inline onclick
function addNewRow() {
  console.log("addNewRow() iškviesta");  // debug

  var tbody = document.getElementById("new-items-body");
  if (!tbody) {
    console.warn("Nerastas tbody su id=new-items-body");
    return;
  }

  var firstRow = tbody.querySelector("tr");
  if (!firstRow) {
    console.warn("Nerasta jokia tr eilutė new-items-body viduje");
    return;
  }

  // klonuojam eilutę giliai (true)
  var clone = firstRow.cloneNode(true);

  // išvalom select ir kiekio įvestį
  var select = clone.querySelector("select[name='new_preke']");
  if (select) {
    select.selectedIndex = 0;
  }

  var qtyInput = clone.querySelector("input[name='new_kiekis']");
  if (qtyInput) {
    qtyInput.value = "";
  }

  tbody.appendChild(clone);
}
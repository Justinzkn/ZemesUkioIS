
const products = [
    {name:'Bulvės', cat:'Daržovės', price:2.50, loc:'Sandėlis A', unit:'kg'},
    {name:'Traktorius', cat:'Technika', price:12000, loc:'Sandėlis B', unit:'vnt'},
    {name:'Agurkai', cat:'Daržovės', price:3.10, loc:'Sandėlis A', unit:'kg'},
    {name:'Gręžtuvas', cat:'Įrankiai', price:45, loc:'Sandėlis C', unit:'vnt'},
    {name:'Buldozeris', cat:'Technika', price:90000, loc:'Sandėlis B', unit:'vnt'},
    {name:'Svogūnai', cat:'Daržovės', price:1.80, loc:'Sandėlis A', unit:'kg'}
];

function render(data) {
    const grid = document.getElementById('product-grid');
    grid.innerHTML = '';
    data.forEach(p => {
        grid.innerHTML += `
            <div class="card">
                <h3>${p.name}</h3>
                <p>Kategorija: ${p.cat}</p>
                <p>Kaina: ${p.price} € / ${p.unit}</p>
                <p>Lokacija: ${p.loc}</p>
                <button onclick="window.location.href='/preke/'">Peržiūrėti</button>
            </div>
        `;
    });
}

function applyFilters() {
    let filtered = products;

    const name = document.getElementById('search-name').value;
    const cat = document.getElementById('filter-category').value;
    const prod = document.getElementById('filter-producer').value;
    const loc = document.getElementById('filter-location').value;
    const min = document.getElementById('price-min').value;
    const max = document.getElementById('price-max').value;

    if(name) filtered = filtered.filter(p => p.name.toLowerCase().includes(name.toLowerCase()));
    if(cat) filtered = filtered.filter(p => p.cat === cat);
    if(loc) filtered = filtered.filter(p => p.loc === loc);
    if(min) filtered = filtered.filter(p => p.price >= parseFloat(min));
    if(max) filtered = filtered.filter(p => p.price <= parseFloat(max));

    render(filtered);
}

// init
render(products);

const fetchModules = () => {
    $.ajax({
        type: "GET",
        dataType: "text",
        url: 'http://127.0.0.1:8000/edt/INFO/fetch_all_modules_with_desc',
        async: true,
        contentType: 'application/json',
        success: response => {
            let modules = JSON.parse(response).map(o => o);
            ModulesApp.init(modules);
        },
        error: e => {
            console.error(e);
        }
    })
};

class ModulesApp {

    static init(modules) {
        let container = document.getElementById("modules-container");
        let search = document.getElementById("modules-search");
        let filters = document.getElementById("filters");
        let app = new ModulesApp(modules, container, search, filters);
    }

    constructor(modules, container, search, filters) {
        this.modules = modules;
        this.promos = ['ALL'];
        this.modules.forEach(e => !this.promos.includes(e.promo) ? this.promos.push(e.promo) : null);
        this.promos.sort();
        this.filters = filters;
        this.selectedFilter = this.promos[0];
        this.searchResult = modules;
        this.container = container;
        this.search = search;
        this.search.addEventListener('input', this.searchModule);
        this.render();
    }

    render() {
        this.promos.forEach(p => this.buildFilter(p));
        this.searchResult.forEach(r => {
            this.buildModules(r);
        });
        for (let elem of this.filters.children) {
            elem.addEventListener('click', e => this.filterModule(e));
        }
    }


    buildModules(mod) {
        let card = document.createElement('div');
        card.setAttribute("class", "module__card");
        card.innerHTML = `
            <div class="left_vertical" style="background: ${mod.color_bg}; color: ${mod.color_txt}">
                <h3 class="module__abbrev">${mod.abbrev}</h3>
            </div>
            <div class="right">
                <span class="module__name">${mod.name}</span>
                <span class="module__resp">${mod.resp}</span>
                <span class="module__promo">${mod.promo}</span>
            </div>
        `;
        this.container.append(card);
    }

    buildFilter(promo) {
        let filter = document.createElement('button');
        filter.setAttribute("class", this.selectedFilter === promo ? "filter__btn filter__active" : "filter__btn");
        filter.setAttribute("id", promo);
        filter.innerText = `${promo}`;
        this.filters.append(filter);
    }

    filterModule(e) {
        let selected = e.target;
        let promo = selected.getAttribute('id');
        $(`#${promo}`).siblings().removeClass('filter__active');
        selected.classList.add('filter__active');
        this.searchResult = promo == 'ALL' ? this.modules : this.modules.filter(mod => mod.promo == promo);
        this.selectedFilter = promo;
        this.clearModules();
        this.render();

    }

    searchModule(e) {
        let searchQuery = e.target.value;
        this.searchResult = this.modules.filter(mod => mod.abbrev.toLowerCase().startsWith(searchQuery.toLowerCase()) ||
            mod.name.toLowerCase().startsWith(searchQuery.toLowerCase()));
        this.clearModules();
        this.render();
    }

    clearModules() {
        let child = this.container.lastElementChild;
        while (child) {
            this.container.removeChild(child);
            child = this.container.lastElementChild;
        }
        child = this.filters.lastElementChild;
        while (child) {
            this.filters.removeChild(child);
            child = this.filters.lastElementChild;
        }
    }
}

fetchModules();




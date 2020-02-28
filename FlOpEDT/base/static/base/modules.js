const fetchModules = () => {
    $.ajax({
        type: "GET",
        dataType: "text",
        url: 'http://127.0.0.1:8000/edt/INFO/fetch_all_modules_with_desc',
        async: true,
        contentType: 'application/json',
        success: response => {
            let modules = JSON.parse(response).map(o=>o);
            ModulesApp.init(modules);
        },
        error: e => {
            console.error(e);
        }
    })
}

class ModulesApp{

    static init(modules){
        let container = document.getElementById("modules-container");
        let search = document.getElementById("modules-search");
        let app = new ModulesApp(modules, container, search);
        app.render();
    }

    constructor(modules, container, search){
        this.modules = modules;
        this.searchResult = modules;
        this.container = container;
        this.search = search;
        this.search.addEventListener('input', this.searchModule);
    }

    render = () => {
        this.searchResult.forEach(this.buildModules);
    }

    buildModules = mod => {
        let card = document.createElement('div');
        card.setAttribute("class", "module__card");
        card.innerHTML = `
            <h3 class="module__abbrev">${mod.abbrev}</h3>
            <span class="module__name">${mod.name}</span>
            <span class="module__resp">${mod.resp}</span>
        `;
        this.container.append(card);
    }

    searchModule = e => {
        let searchQuery = e.target.value;
        this.searchResult = this.modules.filter(mod => mod.abbrev.toLowerCase().startsWith(searchQuery.toLowerCase()) || 
                                                       mod.name.toLowerCase().startsWith(searchQuery.toLowerCase())) ;
        this.clearModules();
        this.render();
    }

    clearModules = () => {
        let child = this.container.lastElementChild;
        while(child){
            this.container.removeChild(child);
            child = this.container.lastElementChild;
        }
    }
}

fetchModules();




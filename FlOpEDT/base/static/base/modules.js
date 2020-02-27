const fetchModules = () => {
    $.ajax({
        type: "GET",
        dataType: "text",
        url: 'http://localhost:8000/edt/INFO/fetch_all_modules_with_desc',
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
        let app = new ModulesApp(modules, container);
        app.render();
    }

    constructor(modules, container){
        this.modules = modules;
        this.container = container;
    }

    render = () => {
        this.modules.forEach(this.buildModules);
    }

    buildModules = mod => {
        let card = document.createElement('div');
        card.innerHTML = `
            <h3 class="module__abbrev">${mod.abbrev}</h3>
            <span class="module__name">${mod.name}</span>
            <span class="module__resp">${mod.resp}</span>
        `;
        this.container.append(card);
    }
}

fetchModules();




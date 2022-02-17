let constraints = {
    8: {
        id: 8, // id de la TTC
        name: "People", // nom du type de TTC
        weight: 1, // poids de la TTC
        is_active: true, // contrainte active ?
        comment: "this constraint is used to prevent old people from dying", // commentaire sur la TTC
        last_modification: null, // date de création
        weeks: [{ nb: 14, year: 2021 }, { nb: 33, year: 2021 }], // week a la forme : {nb: int , year: int}
        parameters: [{
                name: "Prof", // nom du paramètre dans la TTC
                type: 'people.Tutor', // nom du type des objets dans ce paramètre
                required: true, // paramètre obligatoire ?
                all_except: true, // tous sauf ?
                multiple: true,
                id_list: [2, 6], // ids des objets pour le paramètre dans la TTC
                acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] // ids des objets acceptables comme valeur du paramètre
            },
            {
                name: "bonjour", // nom du paramètre dans la TTC
                type: 'people.Tutor', // nom du type des objets dans ce paramètre
                required: false, // paramètre obligatoire ?
                all_except: true, // tous sauf ?
                multiple: true,
                id_list: [1, 8, 5, 6, 7, 8, 9], // ids des objets pour le paramètre dans la TTC
                acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] // ids des objets acceptables comme valeur du paramètre
            }
        ]
    },
    9: {
        id: 9, // id de la TTC
        name: "Black Friday", // nom du type de TTC
        weight: 5, // poids de la TTC
        is_active: true, // contrainte active ?
        comment: "this constraint is used to prevent england from winning the euro cup", // commentaire sur la TTC
        last_modification: null, // date de création
        weeks: [{ nb: 14, year: 2021 }, { nb: 33, year: 2021 }], // week a la forme : {nb: int , year: int}
        parameters: [{
                name: "Prof", // nom du paramètre dans la TTC
                type: 'people.Tutor', // nom du type des objets dans ce paramètre
                required: true, // paramètre obligatoire ?
                all_except: true, // tous sauf ?
                multiple: true,
                id_list: [2, 6], // ids des objets pour le paramètre dans la TTC
                acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] // ids des objets acceptables comme valeur du paramètre
            },
            {
                name: "Student", // nom du paramètre dans la TTC
                type: 'people.Tutor', // nom du type des objets dans ce paramètre
                required: true, // paramètre obligatoire ?
                all_except: true, // tous sauf ?
                multiple: true,
                id_list: [2, 6], // ids des objets pour le paramètre dans la TTC
                acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] // ids des objets acceptables comme valeur du paramètre
            },
            {
                name: "bonjour", // nom du paramètre dans la TTC
                type: 'people.Tutor', // nom du type des objets dans ce paramètre
                required: false, // paramètre obligatoire ?
                all_except: true, // tous sauf ?
                multiple: true,
                id_list: [1, 8, 5, 6, 7, 8, 9], // ids des objets pour le paramètre dans la TTC
                acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] // ids des objets acceptables comme valeur du paramètre
            },
        ]
    },
    10: {
        id: 10, // id de la TTC
        name: "Manifestations", // nom du type de TTC
        weight: 2, // poids de la TTC
        is_active: true, // contrainte active ?
        comment: "this constraint is used to prevent macronius from being elected for a 2nd term and to test overflow overflow overflow overflow overflow overflow overflow overflow overflow overflow overflow", // commentaire sur la TTC
        last_modification: null, // date de création
        weeks: [{ nb: 14, year: 2021 }, { nb: 33, year: 2021 }], // week a la forme : {nb: int , year: int}
        parameters: [{
            name: "Prof", // nom du paramètre dans la TTC
            type: 'people.Tutor', // nom du type des objets dans ce paramètre
            required: true, // paramètre obligatoire ?
            all_except: true, // tous sauf ?
            multiple: true,
            id_list: [2, 6], // ids des objets pour le paramètre dans la TTC
            acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] // ids des objets acceptables comme valeur du paramètre
        }, ]
    },
    11: {
        id: 11, // id de la TTC
        name: "Grève", // nom du type de TTC
        weight: 6, // poids de la TTC
        is_active: true, // contrainte active ?
        comment: "striking is a right", // commentaire sur la TTC
        last_modification: null, // date de création
        weeks: [{ nb: 14, year: 2021 }, { nb: 33, year: 2021 }], // week a la forme : {nb: int , year: int}
        parameters: [{
            name: "Prof", // nom du paramètre dans la TTC
            type: 'people.Tutor', // nom du type des objets dans ce paramètre
            required: true, // paramètre obligatoire ?
            all_except: true, // tous sauf ?
            multiple: true,
            id_list: [2, 6], // ids des objets pour le paramètre dans la TTC
            acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] // ids des objets acceptables comme valeur du paramètre
        }, {
            name: "Prof", // nom du paramètre dans la TTC
            type: 'people.Tutor', // nom du type des objets dans ce paramètre
            required: true, // paramètre obligatoire ?
            all_except: true, // tous sauf ?
            multiple: true,
            id_list: [2, 6], // ids des objets pour le paramètre dans la TTC
            acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] // ids des objets acceptables comme valeur du paramètre
        }, {
            name: "Prof", // nom du paramètre dans la TTC
            type: 'people.Tutor', // nom du type des objets dans ce paramètre
            required: true, // paramètre obligatoire ?
            all_except: true, // tous sauf ?
            multiple: true,
            id_list: [2, 6], // ids des objets pour le paramètre dans la TTC
            acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] // ids des objets acceptables comme valeur du paramètre
        }, {
            name: "Prof", // nom du paramètre dans la TTC
            type: 'people.Tutor', // nom du type des objets dans ce paramètre
            required: true, // paramètre obligatoire ?
            all_except: true, // tous sauf ?
            multiple: true,
            id_list: [2, 6], // ids des objets pour le paramètre dans la TTC
            acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] // ids des objets acceptables comme valeur du paramètre
        }, ]
    },
    12: {
        id: 12, // id de la TTC
        name: "Vote", // nom du type de TTC
        weight: 4, // poids de la TTC
        is_active: true, // contrainte active ?
        comment: "this constraint is used to help people vote, whatever.", // commentaire sur la TTC
        last_modification: null, // date de création
        weeks: [{ nb: 14, year: 2021 }, { nb: 33, year: 2021 }], // week a la forme : {nb: int , year: int}
        parameters: [{
            name: "Prof", // nom du paramètre dans la TTC
            type: 'people.Tutor', // nom du type des objets dans ce paramètre
            required: true, // paramètre obligatoire ?
            all_except: true, // tous sauf ?
            multiple: true,
            id_list: [2, 6], // ids des objets pour le paramètre dans la TTC
            acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] // ids des objets acceptables comme valeur du paramètre
        }, {
            name: "Prof", // nom du paramètre dans la TTC
            type: 'people.Tutor', // nom du type des objets dans ce paramètre
            required: true, // paramètre obligatoire ?
            all_except: true, // tous sauf ?
            multiple: true,
            id_list: [2, 6], // ids des objets pour le paramètre dans la TTC
            acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] // ids des objets acceptables comme valeur du paramètre
        }, {
            name: "Prof", // nom du paramètre dans la TTC
            type: 'people.Tutor', // nom du type des objets dans ce paramètre
            required: true, // paramètre obligatoire ?
            all_except: true, // tous sauf ?
            multiple: true,
            id_list: [2, 6], // ids des objets pour le paramètre dans la TTC
            acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] // ids des objets acceptables comme valeur du paramètre
        }, {
            name: "Prof", // nom du paramètre dans la TTC
            type: 'people.Tutor', // nom du type des objets dans ce paramètre
            required: true, // paramètre obligatoire ?
            all_except: true, // tous sauf ?
            multiple: true,
            id_list: [2, 6], // ids des objets pour le paramètre dans la TTC
            acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] // ids des objets acceptables comme valeur du paramètre
        }, {
            name: "Prof", // nom du paramètre dans la TTC
            type: 'people.Tutor', // nom du type des objets dans ce paramètre
            required: true, // paramètre obligatoire ?
            all_except: true, // tous sauf ?
            multiple: true,
            id_list: [2, 6], // ids des objets pour le paramètre dans la TTC
            acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] // ids des objets acceptables comme valeur du paramètre
        }, {
            name: "Prof", // nom du paramètre dans la TTC
            type: 'people.Tutor', // nom du type des objets dans ce paramètre
            required: true, // paramètre obligatoire ?
            all_except: true, // tous sauf ?
            multiple: true,
            id_list: [2, 6], // ids des objets pour le paramètre dans la TTC
            acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] // ids des objets acceptables comme valeur du paramètre
        }, {
            name: "Prof", // nom du paramètre dans la TTC
            type: 'people.Tutor', // nom du type des objets dans ce paramètre
            required: true, // paramètre obligatoire ?
            all_except: true, // tous sauf ?
            multiple: true,
            id_list: [2, 6], // ids des objets pour le paramètre dans la TTC
            acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] // ids des objets acceptables comme valeur du paramètre
        }, ]
    },
    13: {
        id: 13, // id de la TTC
        name: "Match", // nom du type de TTC
        weight: 1, // poids de la TTC
        is_active: true, // contrainte active ?
        comment: "this constraint is made just for fun", // commentaire sur la TTC
        last_modification: null, // date de création
        weeks: [{ nb: 14, year: 2021 }, { nb: 33, year: 2021 }], // week a la forme : {nb: int , year: int}
        parameters: [{
            name: "Prof", // nom du paramètre dans la TTC
            type: 'people.Tutor', // nom du type des objets dans ce paramètre
            required: true, // paramètre obligatoire ?
            all_except: true, // tous sauf ?
            multiple: true,
            id_list: [2, 6], // ids des objets pour le paramètre dans la TTC
            acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] // ids des objets acceptables comme valeur du paramètre
        }, {
            name: "Prof", // nom du paramètre dans la TTC
            type: 'people.Tutor', // nom du type des objets dans ce paramètre
            required: true, // paramètre obligatoire ?
            all_except: true, // tous sauf ?
            multiple: true,
            id_list: [2, 6], // ids des objets pour le paramètre dans la TTC
            acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] // ids des objets acceptables comme valeur du paramètre
        }, ]
    },
    14: {
        id: 14, // id de la TTC
        name: "Conférence", // nom du type de TTC
        weight: 5, // poids de la TTC
        is_active: true, // contrainte active ?
        comment: "losing one constraint might be regarded as a misfortune, losing both, might just look like carelessness", // commentaire sur la TTC
        last_modification: null, // date de création
        weeks: [{ nb: 14, year: 2021 }, { nb: 33, year: 2021 }], // week a la forme : {nb: int , year: int}
        parameters: [{
            name: "Prof", // nom du paramètre dans la TTC
            type: 'people.Tutor', // nom du type des objets dans ce paramètre
            required: true, // paramètre obligatoire ?
            all_except: true, // tous sauf ?
            multiple: true,
            id_list: [2, 6], // ids des objets pour le paramètre dans la TTC
            acceptable: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] // ids des objets acceptables comme valeur du paramètre
        }, ]
    },
}

let outputSlider = (id, val) => {
    val = val == 8 ? 0 : val;
    let ele = document.getElementById(id);
    ele.innerHTML = val;
}

let URLWeightIcon = document.getElementById('icon-weight').src;
let URLGearsIcon = document.getElementById('icon-gears').src;
let URLCheckIcon = document.getElementById('icon-check').src;

let selected_constraints = [];
let last_selected_constraint = null;

let updateNumberConstraints = () => {
    let ele = document.getElementById('num-selected-constraints');
    ele.innerText = selected_constraints.length;
}

let rerender = () => {
    Array.from(document.getElementById('constraints-list').children).forEach(node => {
        let obj = constraints[node.getAttribute('cst-id')];
        node.querySelector('input').checked = obj.is_active;
        node.querySelector('.icon-text.weight').querySelector('strong').innerText = obj.weight;
        node.querySelector('.icon-text.parameters').querySelector('strong').innerText = obj.parameters.length;
    });
}

let constraintClicked = (e) => {
    let id = e.currentTarget.parentElement.getAttribute('cst-id')
    if (e.currentTarget.classList.contains('selected')) {
        e.currentTarget.classList.remove("selected");
        e.currentTarget.classList.add("unselected");
        selected_constraints = selected_constraints.filter(ele => ele != id);
        let cb_selected_all = document.getElementById('cb1');
        if (cb_selected_all.checked) {
            cb_selected_all.checked = false;
        }
    } else {
        e.currentTarget.classList.remove("unselected");
        e.currentTarget.classList.add("selected");
        selected_constraints.push(id);

        last_selected_constraint = id;
        if (Object.keys(constraints).length == selected_constraints.length) {
            document.getElementById('cb1').checked = true;
        }
    }
    e.stopPropagation();
    updateNumberConstraints();
}


let refreshSelectedFromList = (list) => {
    let l = document.getElementById('constraints-list');
    (Array.from(l.children)).forEach(node => {
        let child = node.children[0];
        if (list.includes(node.getAttribute('cst-id'))) {
            child.classList.remove('unselected');
            child.classList.add('selected');
        }
    });
    updateNumberConstraints();
}

let selectAll = (e) => {
    if (selected_constraints.length == Object.keys(constraints).length) {
        e.currentTarget.checked = true;
    } else {
        selected_constraints = Object.keys(constraints);
        refreshSelectedFromList(selected_constraints);
    }
    updateNumberConstraints();
}

document.getElementById('cb1').checked = false;
document.getElementById('cb1').onchange = selectAll;

let divBuilder = (args = {}) => {
    let div = document.createElement('div');
    for (let [key, value] of Object.entries(args)) {
        div.setAttribute(key, value);
    }
    return div;
}

let iconTextBuilder = (imgurl, value, attr) => {
    let div = divBuilder({ 'class': 'icon-text ' + attr });
    let icondiv = divBuilder({ 'class': 'icon-div' });
    let img = document.createElement('img');
    img.setAttribute('class', 'icon-info');
    img.src = imgurl;
    let strong = document.createElement('strong');
    strong.innerText = value;
    icondiv.append(img);
    div.append(icondiv, strong)

    return div;
}

let activateConstraint = (e) => {
    let id = e.currentTarget.getAttribute('cst-id');
    let ele = constraints[e.currentTarget.getAttribute('cst-id')]
    ele.is_active = !ele.is_active;
    e.currentTarget.checked = ele.is_active;
    let str = 'div[cst-id="' + id + '"]';
    document.getElementById('constraints-list').querySelector(str).click();
}

let additionalInfoBuilder = (cst_obj) => {
    let div = divBuilder({ 'class': 'constraint-card-additional' });
    let params = iconTextBuilder(URLGearsIcon, cst_obj.parameters.length, "parameters");
    let enabled = document.createElement('input');
    enabled.setAttribute('type', 'checkbox');
    enabled.setAttribute('checked', cst_obj.is_active);
    enabled.setAttribute('cst-id', cst_obj.id);
    enabled.onchange = activateConstraint;
    let weight = iconTextBuilder(URLWeightIcon, cst_obj.weight, "weight")
    div.append(params, enabled, weight);
    return div;
}

let constraintCardBuilder = (cst_obj) => {
    let divCard = divBuilder({ 'class': 'constraint-card transition' });
    divCard.setAttribute('cst-id', cst_obj['id']);
    let divCardInfo = divBuilder({ 'class': 'constraint-card-info transition unselected' });
    divCardInfo.addEventListener('click', constraintClicked, false);
    let divTitle = divBuilder({ 'class': 'constraint-card-title' });
    divTitle.innerHTML = cst_obj['name'];
    let divDesc = divBuilder({ 'class': 'constraint-card-description' });
    divDesc.innerHTML = cst_obj['comment'];
    let divAdd = additionalInfoBuilder(cst_obj);
    divCardInfo.append(divTitle, divDesc, divAdd);
    divCard.append(divCardInfo);
    return divCard;
}

let renderConstraints = (cst_list = []) => {
    let body = document.getElementById('constraints-list');
    body.innerHTML = "";
    for (let id of cst_list) {
        body.append(constraintCardBuilder(constraints[id]));
    }
    updateNumberConstraints();
    refreshSelectedFromList(selected_constraints);
}

let sortConstraintsBy = (cst_list, arg) => {
    if (!constraints[cst_list[0]].hasOwnProperty(arg)) {
        return;
    }
    if (typeof constraints[cst_list[0]][arg] == "object") {
        cst_list.sort((x, y) => {
            return constraints[x][arg].length < constraints[y][arg].length ? 1 : -1;
        });
    } else {
        cst_list.sort((x, y) => {
            return constraints[x][arg] < constraints[y][arg] ? 1 : -1;
        });
    }
    return cst_list;
}

let updateWeightAll = (e) => {
    let weight = document.getElementById('slider-all').value;
    selected_constraints.forEach(id => {
        constraints[id].weight = weight;
    });
    rerender();
}

document.getElementById('update-weight-all').onclick = updateWeightAll;


let constraint_list = Object.keys(constraints);
renderConstraints(constraint_list);
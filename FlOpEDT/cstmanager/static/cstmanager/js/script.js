let outputSlider = (id, val) => {
    val = val == 8 ? 0 : val;
    let ele = document.getElementById(id);
    ele.innerHTML = val;
}

let URLWeightIcon = document.getElementById('icon-weight').src;
let URLGearsIcon = document.getElementById('icon-gears').src;
let URLCheckIcon = document.getElementById('icon-check').src;

`<div class="constraint-card">
    <div class="constraint-card-info transition selected">
        <div class="constraint-card-title">
            Minimize groups half-days
        </div>
        <div class="constraint-card-description">
            Minimise les demi-journées des groupes: 1A, 1B, 2A, 2B, 3A, 3B, 4A, 4B, 4, 2A, 3B
        </div>
        <div class="constraint-card-additional">
            <div class=""icon-text>
            <span class="icon"><img src="blabla.png"></span>
            <span class="icon"><img src="blabla.png"></span>
            </div>
        </div>
    </div>
</div>`

let divBuilder = (args = {}) => {
    let div = document.createElement('div');
    for (let [key, value] of Object.entries(args)) {
        div.setAttribute(key, value);
    }
    return div;
}

let iconTextBuilder = (imgurl, value) => {
    let div = divBuilder({ 'class': 'icon-text' });
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

let additionalInfoBuilder = (cst_obj) => {
    let div = divBuilder({ 'class': 'constraint-card-additional' });
    let params = iconTextBuilder(URLGearsIcon, cst_obj.parameters.length);
    let weight = iconTextBuilder(URLWeightIcon, cst_obj.weight)
    div.append(params, weight);
    return div;
}

let constraintCardBuilder = (cst_obj) => {
    let divCard = divBuilder({ 'class': 'constraint-card transition' });
    divCard.setAttribute('cst-id', cst_obj['id']);
    let divCardInfo = divBuilder({ 'class': 'constraint-card-info transition' });
    let divTitle = divBuilder({ 'class': 'constraint-card-title' });
    divTitle.innerHTML = cst_obj['name'];
    let divDesc = divBuilder({ 'class': 'constraint-card-description' });
    divDesc.innerHTML = cst_obj['comment'];
    let divAdd = additionalInfoBuilder(cst_obj);
    divCardInfo.append(divTitle, divDesc, divAdd);
    divCard.append(divCardInfo);
    return divCard;
}

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
        id: 10, // id de la TTC
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
        id: 10, // id de la TTC
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
        id: 10, // id de la TTC
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
        id: 10, // id de la TTC
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

let renderConstraints = (cst_list = []) => {
    let body = document.getElementById('constraints-list');
    body.innerHTML = "";
    for (let id of cst_list) {
        body.append(constraintCardBuilder(constraints[id]));
    }
}

let sortConstraintsBy = (cst_list, arg) => {
    // TODO: implement empty list verification
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

// let filterConstraintsBy = (cst_list, arg) => {
//     return cst_list;
// }

let constraint_list = Object.keys(constraints);
renderConstraints(constraint_list);
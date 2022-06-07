let get_parameter_from_constraint = (cst, name) => {
    let ret = {};
    let l = cst.parameters.filter(obj => obj['name'] == name);
    return l.length == 0 ? ret : l[0];
}

let filter_functions = {
    tutor: (str) => {
        str = str.toLowerCase();
        ret = [];
        keys = Object.keys(database.tutors).filter((key) => {
            obj = database.tutors[key];
            return obj['username'].toLowerCase().includes(str) 
            || obj['first_name'].toLowerCase().includes(str)
            || obj['last_name'].toLowerCase().includes(str);
        });
        return Object.values(database['tutors_ids']).filter(tut => {
            return keys.includes(tut['name']);
        }).map(obj => obj['id']);
    },
    module: (str) => {
        str = str.toLowerCase();
        return Object.keys(database.modules).filter(key => {
            return database.modules[key].toLowerCase().includes(str);
        });
    },
    course: (str) => {
        str = str.toLowerCase();
        return Object.keys(database.courses).filter(key => {
            return database.courses[key].toLowerCase().includes(str);
        });
    },
    reset_filtered_constraint_list: () => {
        filtered_constraint_list = [...constraint_list];
    },
    filter_constraints_by_tutor: (keys, exclusion) => {
        if(!keys || keys.length == 0) {
            filtered_constraint_list = [];
            renderConstraints(filtered_constraint_list);
            return;
        }
        filtered_constraint_list = filtered_constraint_list.filter(cst_id => {
            let param = get_parameter_from_constraint(constraints[cst_id], 'tutor');
            if(Object.keys(param).length == 0) {
                return true;
            }
            if(param.id_list.length == 0 && !exclusion) {
                return true;
            }
            keys.forEach(k => {
                if(param.id_list.includes(k)) {
                    return true;
                }
            });
            return false;
        });
        renderConstraints(filtered_constraint_list);
    },
    filter_constraints_by_module: (keys, exclusion) => {
        if(!keys || keys.length == 0) {
            filtered_constraint_list = [];
            renderConstraints(filtered_constraint_list);
            return;
        }
        filtered_constraint_list = filtered_constraint_list.filter(cst_id => {
            let param = get_parameter_from_constraint(constraints[cst_id], 'module');
            if(Object.keys(param).length == 0) {
                return true;
            }
            if(param.id_list.length == 0 && !exclusion) {
                return true;
            }
            keys.forEach(k => {
                if(param.id_list.includes(k)) {
                    return true;
                }
            });
            return false;
        });
        renderConstraints(filtered_constraint_list);
    },
}

let changeEvents = {
    addNewConstraint: (args = {
        name: null,
        title: null,
    }) => {
        let rand = getRandomInt(100000);
        let id = "-ADD-" + tableName + rand.toString();
        let obj = {
            policy: 'ADD',
            table: tableName,
            tempid: id,
            constraint: {
                is_active: args['is_active'] ?? false,
                comment: args['comment'],
                title: args['title'],
                weeks: copyObj(args['weeks']),
                parameters: null,
                weight: args['weight'] ?? 0,
            },
        }
        actionChanges['ADD'].push(obj);
        constraints[id] = {
            ...copyObj(obj['constraint']),
            id: rand,
            pageid: id,
            name: obj['table'],
        }
        constraint_list = Object.keys(constraints);
        filter_functions.reset_filtered_constraint_list();
        return id;
    },
    duplicateConstraint: (pageid) => {
        let copy_org_cst = copyObj(constraints[pageid]);
        let rand = getRandomInt(100000);
        let id = "-ADD-" + copy_org_cst['name'] + rand.toString();
        let obj = {
            policy: 'ADD',
            table: copy_org_cst['name'],
            tempid: id,
            constraint: {
                is_active: copy_org_cst['is_active'],
                comment: copy_org_cst['comment'],
                title: copy_org_cst['title'],
                weeks: copyObj(copy_org_cst['weeks']),
                parameters: copyObj(copy_org_cst['parameters']),
                weight: copy_org_cst['weight'],
            },
        };
        actionChanges['ADD'].push(obj);
        constraints[id] = {
            ...copyObj(obj['constraint']),
            id: rand,
            pageid: id,
            name: obj['table'],
        };
        constraint_list = Object.keys(constraints);
        filter_functions.reset_filtered_constraint_list();
        return id;
    },
    deleteConstraint: (tableName, id) => {
        let obj = {
            policy: "DELETE",
            table: tableName,
            id: id,
        };
        actionChanges['DELETE'].push(obj);
        delete constraints[id];
        constraint_list = Object.keys(constraints);
        filter_functions.reset_filtered_constraint_list();
        renderConstraints();
    },
    editConstraintAttr: (tableName, id, actions={}) => {
        return true;
    },
    deleteConstraintParameter: (tableName, id, param, pageid) => {
        if(pageid.startsWith('-ADD-')) {
            for(let ele of actionChanges['ADD']) {
                if(ele['tempid'] == pageid) {
                    ele['constraint']['parameters'] = ele['constraint']['parameters'].filter(paramObj => {
                        return paramObj['type'] != param;
                    });
                    break;
                }
            }
            constraints[pageid]['parameters'] = constraints[pageid]['parameters'].filter(paramObj => {
                return paramObj['type'] != param;
            });
            return;
        }
        let obj = {
            policy: 'EDIT',
            table: tableName,
            id: id,
            constraint: {
                action: 'DELETE',
                parameter: param,
            },
        };
        actionChanges['EDIT'].push(obj);
        constraints[pageid]['parameters'] = constraints[pageid]['parameters'].filter(paramObj => {
            return paramObj['type'] != param;
        });
    },
    editConstraintParameter: (tableName, id, param, pageid, new_list) => {
        if(pageid.startsWith('-ADD-')) {
            for(let ele of actionChanges['ADD']) {
                if(ele['tempid'] == pageid) {
                    for(let p of ele['parameters']) {
                        if(p['type'] == param) {
                            p['id_list'] = new_list;
                            break;
                        }
                    }
                }
            }
            for(let p of constraints[pageid]['parameters']) {
                if(p['type'] == param) {
                    p['id_list'] = new_list;
                    break;
                }
            }
            
            return;
        }
        let obj = {
            policy: 'EDIT',
            table: tableName,
            id: id,
            constraint: {
                action: 'EDIT',
                parameter: param,
                id_list: new_list,
            },
        };
        actionChanges['EDIT'].push(obj);
        for(let p of constraints[pageid]['parameters']) {
            if(p['type'] == param) {
                p['id_list'] = new_list;
                break;
            }
        }
    },
    normalizeActionChanges: () => {
        return true;
    },
}

let fetchers = {
    fetchConstraints: (e) => {
        emptyPage();
        fetch("http://127.0.0.1:8000/en/api/ttapp/constraint/?dept=INFO")
            .then(resp => resp.json())
            .then(jsonObj => {
                responseConstraints = responseToDict(Object.values(jsonObj));
                originalConstraints = copyObj(responseConstraints);
                constraints = copyFromOriginalConstraints();
                tables = new Set(Object.values(originalConstraints).map(n => n["name"]));
                actionChanges = emptyChangesDict();
                selected_constraints = new Set();
                lastSelectedConstraint = null;
                constraint_list = Object.keys(constraints);
                filter_functions.reset_filtered_constraint_list();
                constraint_metadata = buildMetadata();
                renderConstraints(constraint_list);
            })
            .catch(err => {
                console.error("something went wrong while fetching constraints");
                console.error(err);
            });
    },
    fetchDepartments: (e) => {
        fetch("http://127.0.0.1:8000/en/api/fetch/alldepts/")
            .then(resp => resp.json())
            .then(jsonObj => {
                database['departments'] = jsonObj.reduce((obj, next) => {
                    let id = next['id'].toString();
                    let abbrev = next['abbrev'];
                    ret = obj;
                    ret[id] = abbrev;
                    return ret;
                }, {})
            })
            .catch(err => {
                console.error("something went wrong while fetching departments");
                console.error(err);
            });
    },
    fetchTrainingPrograms: (e) => {
        
    },
    fetchStructuralGroups: (e) => {
        fetch("http://127.0.0.1:8000/en/api/groups/structural/?dept=INFO")
            .then(resp => resp.json())
            .then(jsonObj => {
                database['structuralGroups'] = {};
                Object.values(jsonObj).forEach(obj => {
                    database['structuralGroups'][obj['id']] = obj;
                });
            })
            .catch(err => {
                console.error("something went wrong while fetching structural groups");
                console.error(err);
            });
    },
    fetchTutors: (e) => {
        fetch("http://127.0.0.1:8000/en/api/user/tutor/?dept=INFO")
            .then(resp => resp.json())
            .then(jsonObj => {
                database['tutors'] = {};
                Object.values(jsonObj).forEach(obj => {
                    database['tutors'][obj['username']] = obj;
                });
            })
            .catch(err => {
                console.error("something went wrong while fetching tutors");
                console.error(err);
            });
    },
    fetchModules: (e) => {
        fetch("http://127.0.0.1:8000/en/api/fetch/idmodule/?dept=INFO")
            .then(resp => resp.json())
            .then(jsonObj => {
                database['modules'] = {};
                Object.values(jsonObj).forEach(obj => {
                    database['modules'][obj['id']] = obj; //TODO:
                });
            })
            .catch(err => {
                console.error("something went wrong while fetching modules");
                console.error(err);
            });
    },
    fetchCourseTypes: (e) => {
        fetch("http://127.0.0.1:8000/en/api/fetch/idcoursetype/")
            .then(resp => resp.json())
            .then(jsonObj => {
                database['courseTypes'] = {};
                Object.values(jsonObj).forEach(obj => {
                    database['courseTypes'][obj['id']] = obj['name'];
                });
            })
            .catch(err => {
                console.error("something went wrong while fetching modules");
                console.error(err);
            });
    },
    fetchCourses: (e) => {
        // TOO BIG
    },
    fetchRooms: (e) => {
        // TODO
    },
    fetchTutorsIDs: (e) => {
        fetch("http://127.0.0.1:8000/en/api/fetch/idtutor/?dept=INFO")
            .then(resp => resp.json())
            .then(jsonObj => {
                database['tutors_ids'] = {};
                Object.values(jsonObj).forEach(obj => {
                    database['tutors_ids'][obj['name']] = obj;
                });
            })
            .catch(err => {
                console.error("something went wrong while fetching tutors_ids");
                console.error(err);
            });
    }
}



let responseToDict = (resp) => {
    let = ret = {};
    resp.forEach(cst => {
        let id = cst['name'] + cst['id'];
        ret[id] = cst;
        ret[id]["pageid"] = id;
    })
    return ret;
}

let copyObj = (obj) => {
    return JSON.parse(JSON.stringify(obj));
}

let toggleDisabledDiv = (e) => {
    document.getElementById('constraints-disabled').classList.toggle('display-none');
}

document.getElementById('show-disabled').addEventListener('click', toggleDisabledDiv);

let copyFromOriginalConstraints = () => {
    let copy = copyObj(originalConstraints);
    return copy;
}

let getRandomInt = (max) => {
    return Math.floor(Math.random() * max);
}

let clickConstraint = (id) => {
    document.getElementById('constraints-all').querySelector(`.constraint-card[cst-id=${id}]`).children[0].click();
}

let emptyChangesDict = () => {
    return {
        'ADD': [],
        'DELETE': [],
        'EDIT': [],
    };
}

// let originalConstraints = responseToDict(responseConstraints);
// let constraints = copyFromOriginalConstraints();
// let tables = new Set(Object.values(originalConstraints).map(n => n["name"]));
// let actionChanges = {};
let originalConstraints;
let constraints;
let tables;
let actionChanges = emptyChangesDict();
let responseConstraints;
let database = {
    'departments': null,
    'trainingPrograms': null,
    'structuralGroups': null,
    'tutors': null,
    'tutors_ids': null,
    'modules': null,
    'courseTypes': null,
    'courses': null,
}

let outputSlider = (id, val) => {
    val = val == 8 ? 0 : val;
    let ele = document.getElementById(id);
    ele.innerHTML = val;
}

let discardChanges = (e) => {
    constraints = copyFromOriginalConstraints();
    constraint_list = Object.keys(constraints);
    filter_functions.reset_filtered_constraint_list();
    selected_constraints.clear();
    lastSelectedConstraint = null;
    updateBroadcastConstraint(null);
    renderConstraints(constraint_list);
}

document.getElementById('discard-changes').addEventListener('click', discardChanges);

let applyChanges = (e) => {
    changeEvents.normalizeActionChanges();
}

let clearFilters = (e) => {
    document.getElementById('input-search').value = '';
    document.getElementById('input-tutor').value = '';
    document.getElementById('input-module').value = '';
    document.getElementById('input-date').value = '';
    filtered_constraint_list = [...constraint_list]
    renderConstraints(constraint_list)
}

document.getElementById('apply-changes').addEventListener('click', applyChanges);

document.getElementById('new-constraint').addEventListener('click', fetchers.fetchConstraints);

document.getElementById('clear-filters').addEventListener('click', clearFilters);

let URLWeightIcon = document.getElementById('icon-weight').src;
let URLGearsIcon = document.getElementById('icon-gears').src;
let URLCheckIcon = document.getElementById('icon-check').src;
let constraintTitle = document.getElementById('constraint-header-title');
let constraintComment = document.getElementById('constraint-header-comment');
let paramsDiv = document.getElementById('params');
let activatedEle = document.getElementById('id2');
let sliderOne = document.getElementById('slider-one');
let constList = document.getElementById('constraints-list');
let filtersElement = document.getElementById('filters');

activatedEle.addEventListener('change', () => {
    if(!broadcastConstraint) {
        return;
    }
    let obj = constraints[`${broadcastConstraint}`];
    obj.is_active = activatedEle.checked;
    rearrange();
})

let selected_constraints = new Set();
let lastSelectedConstraint = null;

let updateNumberConstraints = () => {
    let ele = document.getElementById('num-selected-constraints');
    ele.innerText = selected_constraints.size;
}

let broadcastConstraint = undefined;

let elementBuilder = (tag, args = {}) => {
    let ele = document.createElement(tag);
    for(let [key, value] of Object.entries(args)) {
        ele.setAttribute(key, value);
    }
    return ele;
}

let getCorrespondantDatabase = (param) => {
    switch(param) {
        case 'base.Department': return database['departments'];
        case 'base.TrainingProgramme': return database['trainingPrograms'];
        case 'base.StructuralGroup': return database['structuralGroups'];
        case 'base.Module': return database['modules'];
        case 'base.CourseType': return database['courseTypes'];
        case 'base.Course': return database['courses'];
        case 'people.Tutor': return database['tutors'];
        default:
            console.error("something went wrong while getting correspondant database");
    }
    return null;
}

let getCorrespondantInfo = (id, param, db) => {
    switch(param) {
        case 'base.Department': return db[id];
        case 'base.TrainingProgramme': return "Not Assigned Yet";
        case 'base.StructuralGroup': return db[id]['name'];
        case 'base.Module': return db[id]['abbrev'];
        case 'base.CourseType': return db[id];
        case 'base.Course': return "Not Assigned Yet";
        case 'people.Tutor': return db[id];
        default:
            console.error("something went wrong while getting correspondant information");
    }
    return null;
}

let getParamObj = (cst_id, param) => {
    for(p of constraints[cst_id]['parameters']) {
        if(p['type'] == param) {
            return p;
        }
    }
}

let deleteConstraintParameter = (e) => {
    let div = document.getElementById('parameter-screen');
    let cst_id = div.attributes['cst-id'].value;
    let param = div.attributes['parameter'].value;
    changeEvents.deleteConstraintParameter(
        constraints[cst_id]['name'], 
        constraints[cst_id]['id'], 
        param, 
        constraints[cst_id]['pageid'],
    );
    document.getElementById('parameter-screen').parentElement.remove();
}

let updateConstraintParameter = (e) => {
    let div = document.getElementById('parameter-screen');
    let cst_id = div.attributes['cst-id'].value;
    let param = div.attributes['parameter'].value;
    let paramObj = getParamObj(cst_id, param);
    let new_list = [];
    document.querySelectorAll('.form-check').forEach(node => {
        let input = node.querySelector('input');
        if(input.checked) {
            new_list.push(input.attributes['element-id'].value);
        }
    });
    if(paramObj['required'] && new_list.length == 0) {
        window.alert('You must specify at least one choice!');
        return;
    }
    changeEvents.editConstraintParameter(
        constraints[cst_id]['name'], 
        constraints[cst_id]['id'], 
        param, 
        constraints[cst_id]['pageid'],
        new_list,
    );
}

let cancelConstraintParameter = (e) => {
    document.querySelectorAll('#parameter-screen').forEach(node => {
        node.remove();
    });
}

let getElementsToFillParameterPopup = (cst_id, parameter) => {
    let param_obj = (constraints[cst_id]['parameters'].filter(o => o['type'] == parameter))[0];
    let divs = [];
    
    param_obj['acceptable'].forEach(ele => {
        let temp_id = 'acceptable' + ele.toString();
        let db = getCorrespondantDatabase(parameter);
        let str = getCorrespondantInfo(ele, parameter, db);
        let form = divBuilder({
            class: 'form-check',
        });
        let input = elementBuilder('input', {
            'class': 'form-check-input',
            'type': param_obj['multiple'] ? 'checkbox' : 'radio',
            'id': temp_id,
            'element-id': ele,
            'name': 'elementsParameter',
        });
        form.addEventListener('click', (e) => {
            if(e.currentTarget != e.target) {
                return;
            }
            form.querySelector('input').checked = !form.querySelector('input').checked;
        })
        let label = elementBuilder('label', {
            'class': 'form-check-label',
            'for': temp_id,
        });
        label.innerHTML = str;
        form.append(input, label);
        divs.push(form);
    });

    let divButtons = divBuilder({
        class: 'buttons-for-parameters',
    });

    let deleteButton = elementBuilder('button', {
        type: 'button',
        class: 'btn btn-danger',
    });
    deleteButton.innerHTML = 'Delete';
    deleteButton.addEventListener('click', deleteConstraintParameter);

    let updateButton = elementBuilder('button', {
        type: 'button',
        class: 'btn btn-primary',
    });
    updateButton.innerHTML = 'Update';
    updateButton.addEventListener('click', updateConstraintParameter);

    let cancelButton = elementBuilder('button', {
        type: 'button',
        class: 'btn btn-secondary',
    });
    cancelButton.innerHTML = 'Cancel';
    cancelButton.addEventListener('click', cancelConstraintParameter);

    divButtons.append(deleteButton, updateButton, cancelButton);

    divs.push(divButtons);

    return divs;
}

let buttonWithDropBuilder = (obj) => {
    let butt = elementBuilder("button", { 
        "class": "transition neutral", 
        "style": "width: auto",
        'id': 'parameter-' + obj['type'],
    });
    butt.innerText = obj["name"];
    butt.addEventListener('click', (e) => {
        if(e.currentTarget != e.target) {
            return;
        }
        cancelConstraintParameter(null);
        // if()
        let tempScreen = divBuilder({
            'class': 'div-popup',
            'cst-id': lastSelectedConstraint,
            'parameter': obj['type'],
            'id': 'parameter-screen'
        });
        let elements = getElementsToFillParameterPopup(lastSelectedConstraint, obj['type']);
        tempScreen.append(...elements);
        butt.append(tempScreen);
    });
    return butt;
}

let buttonWeeks = (obj) => {
    let color = obj.length > 0 ? "neutral" : "green";
    let butt = elementBuilder("button", {
        "class": "transition " + color,
        "style": "width: auto",
    });
    butt.innerText = "Weeks"
    let dropMenu = divBuilder({});
    butt.addEventListener('click', (e) => {

    });
    return butt;
}

let updateBroadcastConstraint = (id) => {
    if(!id) {
        if(!lastSelectedConstraint) {
            constraintTitle.innerText = "";
            constraintComment.innerText = "";
            paramsDiv.innerHTML = "";
            activatedEle.checked = false;
            sliderOne.value = 0;
            outputSlider('poidsvalue1', 0);
            return;
        }
    } else if(broadcastConstraint == id) {
        return;
    }
    broadcastConstraint = id;
    let obj = constraints[id];
    constraintTitle.innerText = obj['title'] ?? "No Title";
    constraintComment.innerText = obj['comment'];
    paramsDiv.innerHTML = "";
    activatedEle.checked = obj['is_active'];
    sliderOne.value = obj['weight'] ?? 0;
    outputSlider('poidsvalue1', obj['weight'] ?? 0);
    let buttWeeks = buttonWeeks(obj['weeks']);
    paramsDiv.append(buttWeeks);
    obj['parameters'].forEach(param => {
        let butt = buttonWithDropBuilder(param);
        paramsDiv.append(butt);
    });
}

let constraintHovered = (e) => {
    updateBroadcastConstraint(e.currentTarget.parentElement.getAttribute('cst-id'));
}

let constraintUnhovered = (e) => {
    if(!lastSelectedConstraint) {
        broadcastConstraint = null;
    }
    updateBroadcastConstraint(lastSelectedConstraint);
}

let buildMetadata = () => {
    
}

let buildSection = (name, list) => {
    let ret = divBuilder({ 'class': 'constraints-section-full'});
    let title = divBuilder({ 'class': 'constraints-section-title'});
    let cards = divBuilder({ 'class': 'constraints-section ', 'id': "section-"+name });
    let map = list.map(id => constraintCardBuilder(constraints[id]));
    title.innerText = name;
    cards.append(...map)
    ret.append(title, cards);
    return ret;
}

let buildSections = () => {
    if(filtered_constraint_list == null) {
        filter_functions.reset_filtered_constraint_list();
    }
    let dict = {};
    tables.forEach(name => {
        dict[name] = [];
    });
    Object.values(constraints).forEach(cst => {
        if(filtered_constraint_list.includes(cst['pageid'])) {
            if(cst['is_active']) {
                dict[cst["name"]].push(cst["pageid"])
            }
        }
    });
    let keys = Object.keys(dict);
    let dictDiv = {};
    for(let k of keys) {
        if(dict[k].length == 0) {
            delete dict[k];
        }
        else {
            dictDiv[k] = buildSection(k, dict[k]);
        }
    }
    constList.append(...Object.values(dictDiv));
}

let rerender = () => {
    Array.from(constList.children).forEach(section => {
        Array.from(section.children).forEach(node => {
            let obj = constraints[node.getAttribute('cst-id')];
            node.querySelector('input').checked = obj.is_active;
            node.querySelector('.icon-text.weight').querySelector('strong').innerText = obj.weight;
            node.querySelector('.icon-text.parameters').querySelector('strong').innerText = obj.parameters.length;
        });
    });
    Array.from(document.getElementById('constraints-disabled').children).forEach(node => {
        let obj = constraints[node.getAttribute('cst-id')];
        node.querySelector('input').checked = obj.is_active;
        // node.querySelector('.icon-text.weight').querySelector('strong').innerText = obj.weight;
        // node.querySelector('.icon-text.parameters').querySelector('strong').innerText = obj.parameters.length;
    });
}

let rearrange = () => {
    let constraint_list = Object.keys(constraints);
    filter_functions.reset_filtered_constraint_list();
    let body = constList;
    let bodyDisabled = document.getElementById('constraints-disabled');
    body.innerHTML = "";
    bodyDisabled.innerHTML = "";
    for(let id of constraint_list) {
        if(constraints[id]['is_active']) {
            // body.append(constraintCardBuilder(constraints[id]));
        } else {
            bodyDisabled.append(disabledConstraintCardBuilder(constraints[id]));
        }
    }
    buildSections();
}

let constraintClicked = (e) => {
    if(e.target.type == "checkbox") {
        return;
    }
    let id = e.currentTarget.parentElement.getAttribute('cst-id');
    if(e.currentTarget.classList.contains('selected')) {
        e.currentTarget.classList.remove("selected");
        e.currentTarget.classList.add("unselected");
        // selected_constraints = selected_constraints.filter(ele => ele != id);
        selected_constraints.delete(id);
        let cb_selected_all = document.getElementById('cb1');
        if(cb_selected_all.checked) {
            cb_selected_all.checked = false;
        }
        lastSelectedConstraint = null;
    } else {
        e.currentTarget.classList.remove("unselected");
        e.currentTarget.classList.add("selected");
        selected_constraints.add(id);

        lastSelectedConstraint = id;
        if(Object.keys(constraints).length == selected_constraints.size) {
            document.getElementById('cb1').checked = true;
        }
    }
    e.stopPropagation();
    updateNumberConstraints();
    updateBroadcastConstraint(id);
}


let refreshSelectedFromList = (list) => {
    let l = constList;
    (Array.from(l.children)).forEach(section => {
        (Array.from(section.children)).forEach(node => {
            let child = node.children[0];
            if(list.has(node.getAttribute('cst-id'))) {
                child.classList.remove('unselected');
                child.classList.add('selected');
            }
        });
    });
    updateNumberConstraints();
}

let selectAll = (e) => {
    if(selected_constraints.size == Object.keys(constraints).length) {
        e.currentTarget.checked = true;
    } else {
        selected_constraints = new Set(Object.keys(constraints));
        refreshSelectedFromList(selected_constraints);
    }
    updateNumberConstraints();
}

document.getElementById('cb1').checked = false;
document.getElementById('cb1').onchange = selectAll;

let divBuilder = (args = {}) => {
    let div = document.createElement('div');
    for(let [key, value] of Object.entries(args)) {
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
    let d = constList.querySelector(str);
    if(!d) {
        d = document.getElementById('constraints-disabled').querySelector(str);
    }
    rearrange();
}

let additionalInfoBuilder = (cst_obj) => {
    let div = divBuilder({ 'class': 'constraint-card-additional' });
    let params = iconTextBuilder(URLGearsIcon, cst_obj.parameters.length, "parameters");
    let enabled = document.createElement('input');
    enabled.setAttribute('type', 'checkbox');
    enabled.setAttribute('checked', cst_obj.is_active);
    enabled.setAttribute('cst-id', cst_obj.pageid);
    enabled.onchange = activateConstraint;
    let weight = iconTextBuilder(URLWeightIcon, cst_obj.weight, "weight")
    div.append(params, weight, enabled);
    return div;
}

let constraintCardBuilder = (cst_obj) => {
    let selected = selected_constraints.has(`${cst_obj.pageid}`) ? "selected" : "unselected";
    let divCard = divBuilder({ 'class': 'constraint-card transition' });

    divCard.setAttribute('cst-id', cst_obj['pageid']);
    let divCardInfo = divBuilder({ 'class': 'constraint-card-info transition ' + selected });
    let divCardText = divBuilder({ 'class': 'constraint-card-text ' });
    divCardInfo.addEventListener('click', constraintClicked, false);
    divCardInfo.addEventListener('mouseenter', constraintHovered, false);
    divCardInfo.addEventListener('mouseleave', constraintUnhovered, false);
    let divTitle = divBuilder({ 'class': 'constraint-card-title' });
    divTitle.innerHTML = cst_obj['title'] ?? "No Title";
    let divDesc = divBuilder({ 'class': 'constraint-card-description' });
    divDesc.innerHTML = cst_obj['comment'] ?? "No Comment";
    // divDesc.innerHTML = cst_obj['parameters'].reduce((a, b) => {
    //     return a + b['name'] + ', ';
    // }, "")
    let divAdd = additionalInfoBuilder(cst_obj);
    divCardText.append(divTitle, divDesc);
    divCardInfo.append(divCardText, divAdd);
    divCard.append(divCardInfo);
    return divCard;
}

let disabledConstraintCardBuilder = (cst_obj) => {
    let selected = selected_constraints.has(`${cst_obj.pageid}`) ? "selected" : "unselected";
    let divCard = divBuilder({ 'class': 'constraint-card-disabled transition' });
    divCard.setAttribute('cst-id', cst_obj['pageid']);
    let divCardInfo = divBuilder({ 'class': 'constraint-card-info-disabled transition ' + selected });
    let divCardText = divBuilder({ 'class': 'constraint-card-text ' });
    divCardInfo.addEventListener('click', constraintClicked, false);
    divCardInfo.addEventListener('mouseenter', constraintHovered, false);
    divCardInfo.addEventListener('mouseleave', constraintUnhovered, false);
    let divTitle = divBuilder({ 'class': 'constraint-card-title' });
    divTitle.innerHTML = cst_obj['title'] ?? "No Title";
    let divDesc = divBuilder({ 'class': 'constraint-card-description' });
    divDesc.innerHTML = cst_obj['comment'] ?? "No Comment";
    // divDesc.innerHTML = cst_obj['parameters'].reduce((a, b) => {
    //     return a + b['name'] + ', ';
    // }, "")
    let divAdd = divBuilder({ 'class': 'constraint-card-additional' });
    divCardText.append(divTitle, divDesc);
    let enabled = document.createElement('input');
    enabled.setAttribute('type', 'checkbox');
    enabled.checked = cst_obj.is_active;
    enabled.setAttribute('cst-id', cst_obj.pageid);
    enabled.onchange = activateConstraint;
    divAdd.append(enabled);
    divCardInfo.append(divCardText, divAdd);
    divCard.append(divCardInfo);
    return divCard;
}

let emptyPage = () => {
    let body = constList;
    let bodyDisabled = document.getElementById('constraints-disabled');
    body.innerHTML = "";
    bodyDisabled.innerHTML = "";
}

let renderConstraints = (cst_list = []) => {
    let body = constList;
    let bodyDisabled = document.getElementById('constraints-disabled');
    body.innerHTML = "";
    bodyDisabled.innerHTML = "";
    for(let id of cst_list) {
        if(constraints[id]['is_active']) {
            // body.append(constraintCardBuilder(constraints[id]));
        } else {
            bodyDisabled.append(disabledConstraintCardBuilder(constraints[id]));
        }
    }
    buildSections();
    updateNumberConstraints();
    refreshSelectedFromList(selected_constraints);
}

let sortConstraintsBy = (cst_list, arg) => {
    if(!constraints[cst_list[0]].hasOwnProperty(arg)) {
        return;
    }
    if(typeof constraints[cst_list[0]][arg] == "object") {
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
    renderConstraints();
}

document.getElementById('update-weight-all').onclick = updateWeightAll;

let duplicateSelectedConstraint = (e) => {
    if(!lastSelectedConstraint) {
        return;
    }
    let constr = constraints[`${lastSelectedConstraint}`];
    let newid = changeEvents.duplicateConstraint(constr['pageid']);
    // constraints[copy['pageid']] = copy;
    selected_constraints.clear();
    rearrange();
    clickConstraint(newid);
}

document.getElementById('duplicate-constraint').addEventListener('click', duplicateSelectedConstraint);

let constraint_list = null;
let filtered_constraint_list = null;
let constraint_metadata = null;


fetchers.fetchConstraints(null);
fetchers.fetchDepartments(null);
// fetchers.fetchTrainingPrograms(null);
fetchers.fetchStructuralGroups(null);
fetchers.fetchTutors(null);
fetchers.fetchModules(null);
fetchers.fetchCourseTypes(null);
fetchers.fetchTutorsIDs(null);
// fetchers.fetchCourses(null);
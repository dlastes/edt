let responseToDict = (resp) => {
    let = ret = {};
    resp.forEach(cst => {
        let id = cst['name'] + cst['id'];
        ret[id] = cst;
        ret[id]["pageid"] = id;
    })
    return ret;
}

let toggleDisabledDiv = (e) => {
    document.getElementById('constraints-disabled').classList.toggle('display-none');
}

document.getElementById('show-disabled').addEventListener('click', toggleDisabledDiv);

let copyFromOriginalConstraints = () => {
    let copy = Object.assign({}, originalConstraints);
    return copy;
}

function getRandomInt(max) {
    return Math.floor(Math.random() * max);
}

let clickConstraint = (id) => {
    document.getElementById('constraints-all').querySelector(`.constraint-card[cst-id=${id}]`).children[0].click();
}

let originalConstraints = responseToDict(responseConstraints);
let constraints = copyFromOriginalConstraints();

let outputSlider = (id, val) => {
    val = val == 8 ? 0 : val;
    let ele = document.getElementById(id);
    ele.innerHTML = val;
}

let discardChanges = (e) => {
    constraints = copyFromOriginalConstraints();
    constraint_list = Object.keys(constraints);
    selected_constraints.clear();
    lastSelectedConstraint = null;
    updateBroadcastConstraint(null);
    renderConstraints(constraint_list);
}

document.getElementById('discard-changes').addEventListener('click', discardChanges);

let applyChanges = (e) => {

}

document.getElementById('apply-changes').addEventListener('click', applyChanges);

let URLWeightIcon = document.getElementById('icon-weight').src;
let URLGearsIcon = document.getElementById('icon-gears').src;
let URLCheckIcon = document.getElementById('icon-check').src;
let constraintTitle = document.getElementById('constraint-header-title');
let constraintComment = document.getElementById('constraint-header-comment');
let paramsDiv = document.getElementById('params');
let activatedEle = document.getElementById('id2');
let sliderOne = document.getElementById('slider-one');
let constList = document.getElementById('constraints-list');

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

let buttonWithDropBuilder = (obj) => {
    let butt = elementBuilder("button", { "class": "transition neutral", "style": "width: auto" });
    butt.innerText = obj["name"];
    let dropMenu = divBuilder({});
    butt.addEventListener('click', (e) => {

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

let rerender = () => {
    Array.from(constList.children).forEach(node => {
        let obj = constraints[node.getAttribute('cst-id')];
        node.querySelector('input').checked = obj.is_active;
        node.querySelector('.icon-text.weight').querySelector('strong').innerText = obj.weight;
        node.querySelector('.icon-text.parameters').querySelector('strong').innerText = obj.parameters.length;
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
    let body = constList;
    let bodyDisabled = document.getElementById('constraints-disabled');
    body.innerHTML = "";
    bodyDisabled.innerHTML = "";
    for(let id of constraint_list) {
        if(constraints[id]['is_active']) {
            body.append(constraintCardBuilder(constraints[id]));
        } else {
            bodyDisabled.append(disabledConstraintCardBuilder(constraints[id]));
        }
    }
}

let constraintClicked = (e) => {
    if(e.target.type == "checkbox") {
        return;
    }
    let id = e.currentTarget.parentElement.getAttribute('cst-id')
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
    (Array.from(l.children)).forEach(node => {
        let child = node.children[0];
        if(list.has(node.getAttribute('cst-id'))) {
            child.classList.remove('unselected');
            child.classList.add('selected');
        }
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

let renderConstraints = (cst_list = []) => {
    let body = constList;
    let bodyDisabled = document.getElementById('constraints-disabled');
    body.innerHTML = "";
    bodyDisabled.innerHTML = "";
    for(let id of cst_list) {
        if(constraints[id]['is_active']) {
            body.append(constraintCardBuilder(constraints[id]));
        } else {
            bodyDisabled.append(disabledConstraintCardBuilder(constraints[id]));
        }
    }
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
    rerender();
}

document.getElementById('update-weight-all').onclick = updateWeightAll;

document.getElementById('duplicate-constraint').addEventListener('click', (e) => {
    if(!lastSelectedConstraint) {
        return;
    }
    let constr = constraints[`${lastSelectedConstraint}`];
    let copy = Object.assign({}, constr);
    // copy['id'] = Math.max(...Object.keys(constraints)) + 1;
    copy['pageid'] = copy['name'] + getRandomInt(10000).toString();
    constraints[copy['pageid']] = copy;
    rearrange();
    clickConstraint(copy['pageid']);
});

let constraint_list = Object.keys(constraints);
renderConstraints(constraint_list);

// var abc;

// abc = fetch("http://127.0.0.1:8000/en/api/ttapp/constraint/", {
//     method: 'GET',
//     headers: {
//         'Content-Type': 'application/json',
//         'X-CSRFToken': '5eBpvLT3nsTv6ySJ2J2L3S4lAnhb1E9SnC3rUDc01EahAP75Y3wf3K5nxOTaUQZg',
//     },
// }).then((res) => {
//     return res.json()
// }).then((json) => {
//     ret = {}

//     for(let ele of json) {
//         ret[ele["id"]] = ele
//     }
//     constraints2 = ret;
//     renderConstraints();
//     return json;
// })  return json;
// })
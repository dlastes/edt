// helper function to extract a parameter object from a given constraint
let get_parameter_from_constraint = (cst, name) => {
    let ret = {};
    let l = cst.parameters.filter(obj => obj['name'] === name);
    return l.length === 0 ? ret : l[0];
}

let htmlElements = {
    iconWeight: document.getElementById('icon-weight'),
    iconGears: document.getElementById('icon-gears'),
    iconCheck: document.getElementById('icon-check'),
    newConstraintButton: document.getElementById('nav-new-constraint'),
    constraintsGroupByClass: document.getElementById('constraints-group-by-class'),
    constraintsSelectAll: document.getElementById('constraints-select-all'),
    constraintsInfo: document.getElementById('constraint-info'),
    constraintsInfoBody: document.getElementById('constraint-info-body'),
    constraintHeaderTitle: document.getElementById('constraint-header-title'),
    constraintHeaderComment: document.getElementById('constraint-header-comment'),
    constraintHeaderActivation: document.getElementById('constraint-header-activation'),
    constraintHeaderWeight: document.getElementById('constraint-header-weight'),
    constraintHeaderEditButton: document.getElementById('constraint-header-edit'),
    constraintHeaderDeleteButton: document.getElementById('constraint-header-delete'),
    paramsDiv: document.getElementById('params'),
    constraintsEditPopup: document.getElementById('constraint-edit-popup'),
    constraintEditTitle: document.getElementById('constraint-edit-title'),
    constraintEditComment: document.getElementById('constraint-edit-comment'),
    constraintEditType: document.getElementById('constraint-edit-type'),
    constraintEditParams: document.getElementById('constraint-edit-params'),
    constraintEditWeightSlider: document.getElementById('constraint-edit-weight-slider'),
    constraintEditWeightValue: document.getElementById('constraint-edit-weight-value'),
    constraintEditActivation: document.getElementById('constraint-edit-activation'),
    constraintEditAlert: document.getElementById('constraint-edit-alert-container'),
    enabledConstraintsList: document.getElementById('constraints-enabled'),
    disabledConstraintsList: document.getElementById('constraints-disabled'),
    filtersElement: document.getElementById('filters'),
    numberSelectedConstraints: document.getElementById('num-selected-constraints'),
    commitChangesButton: document.getElementById('apply-changes'),
    fetchConstraintsButton: document.getElementById('fetch-constraints'),
    applyFiltersButton: document.getElementById('clear-filters'),
    cancelEditConstraintButton: document.getElementById('cancel-edit-constraint'),
    confirmEditConstraintButton: document.getElementById('confirm-edit-constraint'),
    selectedConstraintsEditWeightSlider: document.getElementById('selected-constraints-edit-weight-slider'),
    selectedConstraintsEditWeightButton: document.getElementById('selected-constraints-edit-weight'),
    selectedConstraintsDeleteButton: document.getElementById('selected-constraints-delete'),
};

const State = Object.freeze({
    Nothing: Symbol('nothing'),
    CreateNewConstraint: Symbol('create'),
    EditConstraint: Symbol('edit'),
});

let currentState = State.Nothing;

let setState = (newState) => {
    if (!Object.entries(State).find(entry => entry[1] === newState)) {
        return;
    }
    currentState = newState;
};

// object containing functions that involve filtering
let filter_functions = {
    tutor: (str) => {
        str = str.toLowerCase();
        let ret = [];
        let keys = Object.keys(database.tutors).filter((key) => {
            let obj = database.tutors[key];
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
        if (!keys || keys.length === 0) {
            filtered_constraint_list = [];
            refreshConstraints();
            return;
        }
        filtered_constraint_list = filtered_constraint_list.filter(cst_id => {
            let param = get_parameter_from_constraint(constraints[cst_id], 'tutor');
            if (Object.keys(param).length === 0) {
                return true;
            }
            if (param.id_list.length === 0 && !exclusion) {
                return true;
            }
            keys.forEach(k => {
                if (param.id_list.includes(k)) {
                    return true;
                }
            });
            return false;
        });
        refreshConstraints();
    },
    filter_constraints_by_module: (keys, exclusion) => {
        if (!keys || keys.length === 0) {
            filtered_constraint_list = [];
            refreshConstraints();
            return;
        }
        filtered_constraint_list = filtered_constraint_list.filter(cst_id => {
            let param = get_parameter_from_constraint(constraints[cst_id], 'module');
            if (Object.keys(param).length === 0) {
                return true;
            }
            if (param.id_list.length === 0 && !exclusion) {
                return true;
            }
            keys.forEach(k => {
                if (param.id_list.includes(k)) {
                    return true;
                }
            });
            return false;
        });
        refreshConstraints();
    },
}

let visibility = {
    setElementVisible: (htmlElement, isVisible) => {
        htmlElement.hidden = !isVisible;
    },
    showConstraintInfo: _ => {
        visibility.setElementVisible(htmlElements.constraintsInfo, true);
    },
    hideConstraintInfo: _ => {
        visibility.setElementVisible(htmlElements.constraintsInfo, false);
    },
};

// object containing event listeners for constraint management (to prepare for the request)
let changeEvents = {
    addNewConstraint: (constraint) => {
        constraints[constraint.pageid] = constraint;
        actionChanges.add[constraint.pageid] = constraint;
        constraint_list = Object.keys(constraints);
        filter_functions.reset_filtered_constraint_list();
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
    deleteConstraint: (pageid) => {
        let constraint = constraints[pageid];
        if (!constraint) {
            console.log(`Constraint not found for deletion: ${pageid}`);
            return;
        }

        delete constraints[pageid];

        // Check if the constraint is already in the database
        if (!actionChanges.add[pageid]) {
            // Register it for removal
            actionChanges.delete[pageid] = constraint;
        }

        // Remove the constraint from being added or edited
        delete actionChanges.add[pageid];
        delete actionChanges.edit[pageid];

        constraint_list = Object.keys(constraints);
        filter_functions.reset_filtered_constraint_list();
        refreshConstraints();
        updateBroadcastConstraint(null);
    },
    editConstraint: (constraint) => {
        constraints[constraint.pageid] = constraint;

        // Check if the constraint has just been added
        if (actionChanges.add[constraint.pageid]) {
            // Directly edit the constraint in the add list
            actionChanges.add[constraint.pageid] = constraint;
            return;
        }
        // Else add the changes in the edit list (or replace if existing)
        actionChanges.edit[constraint.pageid] = constraint;
    },
    normalizeActionChanges: () => {
        // If the changes are stored as diffs (like a version control system),
        // this function cumulates the diffs before committing.
    },
    commitChanges: () => {
        Object.entries(actionChanges.add).forEach((entry, value) => {
            console.log(entry, value);
        });
    },
}

// object containing functions that fetch data from the database
let fetchers = {
    fetchAcceptableValues: (e) => {
        fetch(build_url(urlAcceptableValues, {"dept": department}))
            .then(resp => resp.json())
            .then(jsonObj => {
                database['acceptable_values'] = {};
                Object.values(jsonObj).forEach(obj => {
                    database['acceptable_values'][obj['name']] = obj;
                });
            })
            .catch(err => {
                console.error("something went wrong while fetching acceptable values");
                console.error(err);
            });
    },
    fetchConstraints: (e) => {
        emptyPage();
        fetchers.fetchAcceptableValues();
        fetch(build_url(urlConstraints, {"dept": department}))
            .then(resp => resp.json())
            .then(jsonObj => {
                originalConstraints = responseToDict(Object.values(jsonObj));
                constraints = copyFromOriginalConstraints();
                Object.values(constraints).forEach((constraint) => {
                    constraint['parameters'].forEach((param) => {
                        if (param.name in database['acceptable_values']) {
                            param['acceptable'] = database['acceptable_values'][param.name]['acceptable'];
                        }
                    });
                });
                actionChanges = emptyChangesDict();
                selected_constraints = [];
                lastSelectedConstraint = null;
                constraint_list = Object.keys(constraints);
                filter_functions.reset_filtered_constraint_list();
                constraint_metadata = buildMetadata();
                refreshConstraints();
            })
            .catch(err => {
                console.error("something went wrong while fetching constraints");
                console.error(err);
            });
    },
    fetchDepartments: (e) => {
        fetch(build_url(urlDepartments))
            .then(resp => resp.json())
            .then(jsonObj => {
                database['departments'] = jsonObj.reduce((obj, next) => {
                    let id = next['id'].toString();
                    let abbrev = next['abbrev'];
                    let ret = obj;
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
        fetch(build_url(urlTrainingPrograms, {"dept": department}))
            .then(resp => resp.json())
            .then(jsonObj => {
                database['train_progs'] = {};
                Object.values(jsonObj).forEach(obj => {
                    database['train_progs'][obj['id']] = obj;
                });
            })
            .catch(err => {
                console.error("something went wrong while fetching training programs");
                console.error(err);
            });
    },
    fetchStructuralGroups: (e) => {
        fetch(build_url(urlGroups, {"dept": department}))
            .then(resp => resp.json())
            .then(jsonObj => {
                database['groups'] = {};
                Object.values(jsonObj).forEach(obj => {
                    database['groups'][obj['id']] = obj;
                });
            })
            .catch(err => {
                console.error("something went wrong while fetching structural groups");
                console.error(err);
            });
    },
    fetchTutors: (e) => {
        fetch(build_url(urlTutors, {"dept": department}))
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
        fetch(build_url(urlModules, {"dept": department}))
            .then(resp => resp.json())
            .then(jsonObj => {
                database['modules'] = {};
                Object.values(jsonObj).forEach(obj => {
                    database['modules'][obj['id']] = obj;
                });
            })
            .catch(err => {
                console.error("something went wrong while fetching modules");
                console.error(err);
            });
    },
    fetchCourseTypes: (e) => {
        fetch(build_url(urlCourseTypes, {"dept": department}))
            .then(resp => resp.json())
            .then(jsonObj => {
                database['course_types'] = {};
                Object.values(jsonObj).forEach(obj => {
                    database['course_types'][obj['id']] = obj['name'];
                });
            })
            .catch(err => {
                console.error("something went wrong while fetching modules");
                console.error(err);
            });
    },
    fetchCourses: (e) => {
        fetch(build_url(urlCourses, {"dept": department}))
            .then(resp => resp.json())
            .then(jsonObj => {
                database['courses'] = {};
                Object.values(jsonObj).forEach(obj => {
                    database['courses'][obj['id']] = obj;
                });
            })
            .catch(err => {
                console.error("something went wrong while fetching courses");
                console.error(err);
            });
    },
    fetchWeeks: (e) => {
        fetch(urlWeeks)
            .then(resp => resp.json())
            .then(jsonObj => {
                database['weeks'] = {};
                Object.values(jsonObj).forEach(obj => {
                    let currentYear = new Date().getFullYear();
                    let year = obj['year'];
                    if (year < currentYear || year > currentYear + 1) {
                        return;
                    }
                    database['weeks'][obj['id']] = obj;
                });
            })
            .catch(err => {
                console.error("something went wrong while fetching weeks");
                console.error(err);
            });
    },
    fetchRooms: (e) => {
        // TODO
    },
    fetchTutorsIDs: (e) => {
        fetch(build_url(urlTutorsID, {"dept": department}))
            .then(resp => resp.json())
            .then(jsonObj => {
                database['tutors_ids'] = {};
                Object.values(jsonObj).forEach(obj => {
                    database['tutors_ids'][obj['id']] = obj;
                });
            })
            .catch(err => {
                console.error("something went wrong while fetching tutors_ids");
                console.error(err);
            });
    },
    fetchConstraintTypes: (e) => {
        fetch(build_url(urlConstraintTypes, {"dept": department}))
            .then(resp => resp.json())
            .then(jsonObj => {
                database.constraint_types = {};
                let constraints = Object.values(jsonObj).sort((a, b) => a.local_name.toString().localeCompare(b.local_name.toString()));

                constraints.forEach(constraint => {
                    database.constraint_types[constraint.name] = constraint;
                    // fill the types in type selection
                    let option = elementBuilder('option', {});
                    option.text = constraint.local_name.toString();
                    htmlElements.constraintEditType.add(option);
                });
            })
            .catch(err => {
                console.error("something went wrong while fetching constraint types");
                console.error(err);
            });
    },
}

// transform DB response to a JSON object
let responseToDict = (resp) => {
    let ret = {};
    resp.forEach(cst => {
        let id = cst['name'] + cst['id'];
        ret[id] = cst;
        ret[id]["pageid"] = id;
    })
    return ret;
}

// a simple way to make a copy of a JSON object
let copyObj = (obj) => {
    return JSON.parse(JSON.stringify(obj));
}

// toggle the tab for disabled constraints
let toggleDisabledDiv = (e) => {
    htmlElements.disabledConstraintsList.classList.toggle('display-none');
}
document.getElementById('show-disabled').addEventListener('click', toggleDisabledDiv);

// returns a copy of the original constraints
let copyFromOriginalConstraints = () => {
    let copy = copyObj(originalConstraints);
    return copy;
}

// helper random integer generator function
let getRandomInt = (max) => {
    return Math.floor(Math.random() * max);
}

// constraint clicked simulator
let clickConstraint = (id) => {
    document.getElementById('constraints-all').querySelector(`.constraint-card[cst-id=${id}]`).children[0].click();
}

// returns an empty JSON object for tracking changes on constraints
let emptyChangesDict = () => {
    return {
        'add': {},
        'delete': {},
        'edit': {},
    };
}

// some variable assignments
let originalConstraints;
let constraints;
let newConstraint;
let editConstraint;
let actionChanges = emptyChangesDict();
let database = {
    'departments': null,
    'train_progs': null,
    'groups': null,
    'tutors': null,
    'tutors_ids': null,
    'modules': null,
    'course_types': null,
    'courses': null,
    'weeks': null,
    'acceptable_values': null,
    'constraint_types': null,
}


let findConstraintClassFromLocalName = (localName) => {
    return Object.values(database.constraint_types).find(obj => {
        return obj.local_name === localName;
    });
};

let findConstraintLocalNameFromClass = (className) => {
    return database.constraint_types[className].local_name;
};


let getNewConstraintID = (className) => {
    let filteredByClassName = Object.values(constraints).filter(constraint => constraint.name === className);
    if (filteredByClassName.length === 0) {
        return 1;
    }

    // Extract each constraint's pageid their number and return the max + 1
    return parseInt(filteredByClassName.reduce((constraint1, constraint2) => {
        let cst1 = constraint1.pageid.match(/\d+/)[0];
        let cst2 = constraint2.pageid.match(/\d+/)[0];
        return (cst1 > cst2 ? constraint1 : constraint2);
    }, filteredByClassName[0]).pageid.match(/\d+/)[0]) + 1;
};

let resetNewConstraint = () => {
    newConstraint = {
        comment: '',
        id: '',
        is_active: false,
        modified_at: '',
        name: '',
        local_name: '',
        pageid: '',
        parameters: {},
        title: '',
        weight: 0,
    };
}

let updateParamsListNewConstraint = () => {
    newConstraint.local_name = htmlElements.constraintEditType.value;
    newConstraint.name = findConstraintClassFromLocalName(newConstraint.local_name).name;
    newConstraint.id = getNewConstraintID(newConstraint.name);
    newConstraint.pageid = newConstraint.name + newConstraint.id;
    newConstraint.parameters = database.constraint_types[newConstraint.name].parameters;
    updateParamsListExistingConstraint(newConstraint);
};

let updateParamsListExistingConstraint = (constraint) => {
    // Clear previous parameters
    let div = htmlElements.constraintEditParams;
    while (div.firstChild) {
        div.removeChild(div.lastChild);
    }

    // Fill parameters
    database.constraint_types[constraint.name].parameters.sort((a, b) => (a.required && !b.required) ? -1 : (!a.required && b.required) ? 1 : 0);
    database.constraint_types[constraint.name].parameters.forEach(param => {
        // Add empty id_list as selected elements (none when constraint has just been created)
        param.id_list = [];

        let button = buttonWithDropBuilder(constraint, param);
        div.append(button);
    })
};

let fillEditConstraintPopup = constraint => {
    let type = htmlElements.constraintEditType;
    let title = htmlElements.constraintEditTitle;
    let comment = htmlElements.constraintEditComment;
    let params = htmlElements.constraintEditParams;
    let activation = htmlElements.constraintEditActivation;
    let weightSlider = htmlElements.constraintEditWeightSlider;
    let weightValue = htmlElements.constraintEditWeightValue;

    if (!constraint) {
        type.selectedIndex = 0;
        type.disabled = false;
        title.value = "";
        comment.value = "";
        activation.checked = false;
        weightSlider.value = 0;
        weightValue.innerText = '0';
        params.innerHTML = '';
    } else {
        let localName = findConstraintLocalNameFromClass(constraint.name);
        Array.from(type.options).some((option, index) => {
            if (option.text === localName) {
                type.selectedIndex = index;
                type.disabled = true;
                return true;
            }
            return false;
        });

        title.value = constraint.title ?? "";
        comment.value = constraint.comment ?? "";
        activation.checked = constraint.is_active;
        weightSlider.value = constraint.weight;
        weightValue.innerText = constraint.weight;
    }
};

let updateEditConstraintPopup = constraint => {
    fillEditConstraintPopup(constraint);
    updateParamsListExistingConstraint(constraint);
};

// Replaces given constraint's values with entered from user
let extractConstraintFromPopup = (constraint) => {
    const alert = (message, type) => {
        const wrapper = document.createElement('div');

        wrapper.innerHTML = [
            `<div class="alert alert-${type} alert-dismissible" role="alert">`,
            `   <div>${message}</div>`,
            '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
            '</div>',
        ].join('');
        htmlElements.constraintEditAlert.append(wrapper);
    }

    if (htmlElements.constraintEditType.selectedIndex === 0) {
        alert('Type is required!', 'danger');
        return;
    }

    constraint.title = htmlElements.constraintEditTitle.value;

    constraint.comment = htmlElements.constraintEditComment.value;
    constraint.is_active = htmlElements.constraintEditActivation.checked;
    constraint.weight = parseInt(htmlElements.constraintEditWeightSlider.value);
    let currentDate = new Date();
    const offset = currentDate.getTimezoneOffset();
    currentDate = new Date(currentDate.getTime() - (offset * 60 * 1000));
    constraint.modified_at = currentDate.toISOString().split('T')[0];

    let isValid = true;

    Object.values(constraint.parameters).forEach(param => {
        // Ignore immutable parameters
        if (param.name === 'department') {
            return;
        }

        // Clear the previously selected values (only keep the latest save)
        param.id_list = [];

        if (param.type.includes('Boolean')) {
            let tag = document.getElementById('param-check-' + param.name);
            param.id_list.push(tag.checked);
        } else {
            // Store the selected values
            let tag = document.getElementById('collapse-parameter-' + param.name);
            tag.querySelectorAll('input').forEach((value, key, parent) => {
                if (value.type === 'text') {
                    param.id_list.push(value.value);
                } else {
                    if (value.checked) {
                        param.id_list.push(value.getAttribute('element-id'));
                    }
                }
            });
        }

        if (param.required && param.id_list.length === 0) {
            isValid = false;
            alert(`Parameter ${param.name} is required!`, 'danger');
        }
    });

    return isValid;
};

let updateEditConstraintWeightDisplay = (labelID, value) => {
    let weightText = "Unwanted";
    if (value <= 8) {
        weightText = value.toString();
    }

    document.getElementById(labelID).innerText = weightText;
}

// event handler that discard constraint changes and restore
// data to the original state
let discardChanges = (e) => {
    constraints = copyFromOriginalConstraints();
    constraint_list = Object.keys(constraints);
    filter_functions.reset_filtered_constraint_list();
    selected_constraints = [];
    lastSelectedConstraint = null;
    updateBroadcastConstraint(null);
    refreshConstraints();
}
document.getElementById('discard-changes').addEventListener('click', discardChanges);

// shortcut function
let applyChanges = (e) => {
    changeEvents.normalizeActionChanges();
    changeEvents.commitChanges();
}

// clear input fields for filters
let clearFilters = (e) => {
    document.getElementById('input-search').value = '';
    document.getElementById('input-tutor').value = '';
    document.getElementById('input-module').value = '';
    document.getElementById('input-date').value = '';
    filtered_constraint_list = [...constraint_list]
    refreshConstraints();
}

let saveConstraintChanges = () => {
    let constraintToSave = null;
    let changeCallback = null;

    // Obtain the contraint and function to call according to current state
    switch (currentState) {
        case State.CreateNewConstraint:
            constraintToSave = newConstraint;
            changeCallback = changeEvents.addNewConstraint;
            break;
        case State.EditConstraint:
            constraintToSave = editConstraint;
            changeCallback = changeEvents.editConstraint;
            break;
        default:
            return;
    }

    // Try to extract the constraint
    let isValid = extractConstraintFromPopup(constraintToSave);

    if (!isValid) {
        console.log("Constraint is not valid, cancelling...");
        return;
    }

    // Apply the change
    changeCallback(constraintToSave);

    // Clear alerts
    htmlElements.constraintEditAlert.innerHTML = '';

    // Hide popup
    const modal = bootstrap.Modal.getInstance(htmlElements.constraintsEditPopup);
    modal.hide();

    // Reset fields
    fillEditConstraintPopup(null);

    // Reset selected constraints
    lastSelectedConstraint = null;
    selected_constraints = [];

    // Reset header
    updateBroadcastConstraint(null);

    // Reset current state
    setState(State.Nothing);

    // Refresh
    refreshConstraints();
};

htmlElements.confirmEditConstraintButton.addEventListener('click', saveConstraintChanges);

let cancelNewConstraint = () => {
    setState(State.Nothing);

    // Hide popup
    const modal = bootstrap.Modal.getInstance(htmlElements.constraintsEditPopup);
    modal.hide();
};
htmlElements.cancelEditConstraintButton.addEventListener('click', cancelNewConstraint);

htmlElements.commitChangesButton.addEventListener('click', applyChanges);
htmlElements.fetchConstraintsButton.addEventListener('click', fetchers.fetchConstraints);
htmlElements.applyFiltersButton.addEventListener('click', clearFilters);

let selected_constraints = [];
let lastSelectedConstraint = null;

// number of constraints selected updater
let updateNumberConstraints = () => {
    htmlElements.numberSelectedConstraints.innerText = selected_constraints.length.toString();
}

let broadcastConstraint = undefined;

// HTML element builder to help with the code
let elementBuilder = (tag, args = {}) => {
    let ele = document.createElement(tag);
    for (const [key, value] of Object.entries(args)) {
        ele.setAttribute(key, value);
    }
    return ele;
}

// returns the corresponding database table based on the parameter given
let getCorrespondantDatabase = (param) => {
    switch (param) {
        case 'group':
        case 'groups':
            return database['groups'];
        case 'module':
        case 'modules':
            return database['modules'];
        case 'course_type':
        case 'course_types':
            return database['course_types'];
        case 'train_prog':
        case 'train_progs':
            return database['train_progs'];
        case 'tutor':
        case 'tutors':
            return database['tutors_ids'];
        case 'weeks':
            return database['weeks'];
        default:
            return database['acceptable_values'][param];
    }
}

// returns the information needed from a parameter and a constraint id given
let getCorrespondantInfo = (id, param, db) => {
    switch (param) {
        case 'group':
        case 'groups':
            return `${db[id]['train_prog']}-${db[id]['name']}`;
        case 'module':
        case 'modules':
        case 'train_prog':
        case 'train_progs':
            return db[id]['abbrev'];
        case 'tutors':
        case 'tutor':
            return db[id]['name'];
        case 'course_type':
        case 'course_types':
            return db[id];
        case 'weeks':
            return `${db[id]['year']}-${db[id]['nb']}`;
        default:
            return id;
    }
}

let isParameterValueSelectedInConstraint = (constraint, parameter, value) => {
    return constraint.parameters.find(param => param.name === parameter).id_list.includes(value);
};

// returns the parameter object from a constraint obejct
let getParamObj = (constraint, param) => {
    for (p of constraint.parameters) {
        if (p.type === param) {
            return p;
        }
    }
}

// event handler that deletes a constraint's parameter
let deleteConstraintParameter = (e) => {
    let div = document.getElementById('parameter-screen');
    let cst_id = div.attributes['data-cst-id'].value;
    let constraint = constraints[cst_id];
    let param = div.attributes['parameter'].value;
    changeEvents.deleteConstraintParameter(
        constraint.name,
        constraint.id,
        param,
        constraint.pageid,
    );
    document.getElementById('parameter-screen').parentElement.remove();
}

// remove the display on constraint parameters
let cancelConstraintParameter = (e) => {
    document.querySelectorAll('#parameter-screen').forEach(node => {
        node.remove();
    });
}

// returns elements that make part of the parameter screen
let createSelectedParameterPopup = (constraint, parameter) => {
    let param_obj = (constraint.parameters.filter(o => o.name === parameter))[0];
    let divs = divBuilder();

    let createCheckboxAndLabel = (ele, inputType) => {
        let temp_id = 'acceptable' + ele.toString();
        let db = getCorrespondantDatabase(parameter);
        let str = getCorrespondantInfo(ele, parameter, db);
        let checked = isParameterValueSelectedInConstraint(constraint, parameter, ele);

        let form = divBuilder({
            'class': 'form-check form-check-inline',
        });

        let input = elementBuilder('input', {
            'class': 'form-check-input me-1',
            'type': inputType,
            'id': temp_id,
            'element-id': ele,
            'name': 'elementsParameter',
        });
        input.checked = checked;
        let label = elementBuilder('label', {
            'class': 'form-check-label ms-1 me-3',
            'for': temp_id,
        });
        label.innerHTML = str;
        form.append(input, label);
        divs.append(form);
    };

    if (param_obj.multiple) {
        let acceptableValues = database.acceptable_values[parameter].acceptable;
        acceptableValues.forEach(ele => {
            createCheckboxAndLabel(ele, 'checkbox');
        });
    } else {
        let temp_id = parameter + '-value';

        let form = divBuilder({
            'class': 'form-floating',
        })

        let input = elementBuilder('input', {
            'class': 'form-control',
            'id': temp_id,
            'element-id': 0,
            'name': 'elementsParameter',
        });

        let label = elementBuilder('label', {
            'for': temp_id,
        });

        label.innerHTML = 'Valeur';

        form.append(input, label);
        divs.append(form);
    }

    let divButtons = divBuilder({
        class: 'buttons-for-parameters',
    });

    let deleteButton = elementBuilder('button', {
        type: 'button',
        class: 'btn btn-danger',
    });
    deleteButton.innerHTML = 'Delete';
    deleteButton.addEventListener('click', deleteConstraintParameter);

    let cancelButton = elementBuilder('button', {
        type: 'button',
        class: 'btn btn-secondary',
    });
    cancelButton.innerHTML = 'Cancel';
    cancelButton.addEventListener('click', cancelConstraintParameter);

    divButtons.append(cancelButton, deleteButton);

    divs.append(divButtons);

    return divs;
}

// builds a button that shows a drop menu after clicking on it
let buttonWithDropBuilder = (constraint, parameter) => {
    let buttonID = 'parameter-' + parameter.name;
    let collapseID = 'collapse-' + buttonID;

    let badge = '';

    if (parameter.required) {
        badge = elementBuilder('span', {
            'class': 'badge text-bg-danger ms-1',
        });
        badge.innerText = "Required";
    }

    let button;

    let buttonHeader = divBuilder({
        'class': 'accordion-header',
        'id': buttonID,
    });

    let collapse = divBuilder({
        'class': 'accordion-collapse collapse',
        'id': collapseID,
        'labelledby': buttonID,
        'data-bs-parent': '#' + htmlElements.constraintEditParams.id,
    });

    // Different display for boolean parameters
    if (parameter.type.includes('Boolean')) {
        button = divBuilder({
            'class': 'form-check form-switch m-3',
        });

        let checkID = `param-check-${parameter.name}`;

        let check = elementBuilder('input', {
            'class': 'form-check-input',
            'type': 'checkbox',
            'role': 'switch',
            'id': checkID,
        });

        let label = elementBuilder('label', {
            'class': 'form-check-label',
            'for': checkID,
        });
        label.innerText = parameter.name;
        button.append(check, label, badge);
    } else {
        button = elementBuilder('button', {
            'class': 'accordion-button collapsed',
            'type': 'button',
            'data-bs-toggle': 'collapse',
            'data-bs-target': '#' + collapseID,
            'aria-expanded': 'false',
            'aria-controls': collapseID,
        });
        button.innerText = parameter.name;
        button.append(badge);

        let elements = createSelectedParameterPopup(constraint, parameter.name);

        let body = divBuilder({
            'class': 'accordion-body',
        });

        body.append(elements);
        collapse.append(body);
    }

    let itemContainer = divBuilder({
        'class': 'accordion-item',
    })

    buttonHeader.append(button);
    itemContainer.append(buttonHeader, collapse);
    return itemContainer;
}

// update the header info by showing the selected constraint's info
let updateBroadcastConstraint = (id) => {
    if (!id) {
        htmlElements.constraintHeaderTitle.value = "";
        htmlElements.constraintHeaderComment.value = "";
        htmlElements.constraintHeaderActivation.innerText = "";
        htmlElements.constraintHeaderWeight.innerText = "";
        htmlElements.paramsDiv.innerHTML = "";
        visibility.hideConstraintInfo();
        return;
    }
    visibility.showConstraintInfo();

    broadcastConstraint = id;
    let obj = constraints[id];

    if (!obj) {
        console.log(`Constraint not found for display: ${id}`);
        return;
    }
    htmlElements.constraintHeaderTitle.value = obj.title || findConstraintLocalNameFromClass(obj.name);
    htmlElements.constraintHeaderComment.value = obj.comment;
    htmlElements.constraintHeaderActivation.innerText = obj.is_active ? "Active" : "Inactive";
    htmlElements.constraintHeaderWeight.innerText = obj.weight;
    htmlElements.paramsDiv.innerHTML = "";
    obj.parameters.forEach(param => {
        // hide the department parameter
        if (param.name === 'department') {
            return;
        }
        let paramDiv = elementBuilder("label", {
            class: "form-label rounded border border-dark p-1",
        });
        paramDiv.innerText = param.name;
        htmlElements.paramsDiv.append(paramDiv);
    });
}

// event handler that fires the update broadcast constraint event handler
let constraintHovered = (e) => {
    updateBroadcastConstraint(e.currentTarget.getAttribute('data-cst-id'));
}

// event handler that resets the update broadcast constraint event handler
let constraintUnhovered = (e) => {
    if (!lastSelectedConstraint) {
        broadcastConstraint = null;
    }
    updateBroadcastConstraint(lastSelectedConstraint);
}

// Unimplemented functionality
let buildMetadata = () => {

}

// rerender the constraints on the page (in case of a modification)
let refreshConstraints = () => {
    htmlElements.enabledConstraintsList.innerHTML = '';
    htmlElements.disabledConstraintsList.innerHTML = '';
    lastSelectedConstraint = null;

    buildConstraintsSections();
    refreshSelectedFromList(selected_constraints);
}

// main section builder
let buildSection = (name, list) => {
    let ret = divBuilder({'class': 'constraints-section-full mb-2'});
    let title = divBuilder({'class': 'constraints-section-title'});
    let cards = divBuilder({'class': 'constraints-section ', 'id': "section-" + name});
    let map = list.map(id => constraintCardBuilder(constraints[id]));
    title.innerText = name;
    cards.append(...map)
    ret.append(title, cards);
    return ret;
}

// helps with the generation of the page's sections
let buildConstraintsSections = () => {
    htmlElements.enabledConstraintsList.innerHTML = "";

    if (filtered_constraint_list == null) {
        filter_functions.reset_filtered_constraint_list();
    }

    let dict = {};

    let group_by_class = htmlElements.constraintsGroupByClass.checked;
    if (group_by_class) {
        Object.values(constraints).forEach(cst => {
            if (filtered_constraint_list.includes(cst.pageid)) {
                if (!dict[cst.name]) {
                    dict[cst.name] = {
                        'active': [],
                        'inactive': [],
                    };
                }
                dict[cst.name][cst.is_active ? 'active' : 'inactive'].push(cst.pageid);
            }
        });
    } else {
        dict['All constraints'] = {
            'active': [],
            'inactive': [],
        };
        Object.values(constraints).forEach(cst => {
            if (filtered_constraint_list.includes(cst.pageid)) {
                dict["All constraints"][cst.is_active ? 'active' : 'inactive'].push(cst.pageid);
            }
        });
    }

    // build active constraints section
    let activeConstraintsElements = {};
    Object.keys(dict).forEach(key => {
        if (dict[key].active.length === 0) {
            return;
        }
        activeConstraintsElements[key] = buildSection(key, dict[key].active);
    });
    htmlElements.enabledConstraintsList.append(...Object.values(activeConstraintsElements));

    // build inactive constraints section
    let inactiveConstraintsElements = {};
    Object.keys(dict).forEach(key => {
        if (dict[key].inactive.length === 0) {
            return;
        }
        inactiveConstraintsElements[key] = buildSection(key, dict[key].inactive);
    });
    htmlElements.disabledConstraintsList.append(...Object.values(inactiveConstraintsElements));
}
htmlElements.constraintsGroupByClass.addEventListener('click', refreshConstraints);

// event handler when clicking on a constraint
let constraintClicked = (e) => {
    if (e.target.type === "checkbox") {
        return;
    }
    let id = e.currentTarget.getAttribute('data-cst-id');
    if (e.currentTarget.classList.contains('selected')) {
        e.currentTarget.classList.remove("selected");
        e.currentTarget.classList.add("unselected");
        let index = selected_constraints.indexOf(id);
        if (index > -1) {
            selected_constraints.splice(index, 1);
        }
        let indexNextConstraint = selected_constraints.length - 1;
        lastSelectedConstraint = (indexNextConstraint > -1) ? selected_constraints[indexNextConstraint] : null;
    } else {
        e.currentTarget.classList.remove("unselected");
        e.currentTarget.classList.add("selected");
        selected_constraints.push(id);

        lastSelectedConstraint = id;
    }
    e.stopPropagation();
    refreshSelectedFromList(selected_constraints);
    updateBroadcastConstraint(id);
}

// color selected constraints
let refreshSelectedFromList = (list) => {
    let cardList = htmlElements.enabledConstraintsList;
    let allSelected = true;

    cardList.querySelectorAll('.constraint-card').forEach(constraintCard => {
        if (list.indexOf(constraintCard.getAttribute('data-cst-id')) < 0) {
            constraintCard.classList.remove('selected');
            constraintCard.classList.add('unselected');
            allSelected = false;
        } else {
            constraintCard.classList.remove('unselected');
            constraintCard.classList.add('selected');
        }
    });

    htmlElements.constraintsSelectAll.checked = allSelected;
    updateNumberConstraints();
}

// select all constraint simulator
let selectAll = (e) => {
    if (selected_constraints.length === Object.keys(constraints).length) {
        selected_constraints = [];
    } else {
        selected_constraints = Object.keys(constraints);
    }
    refreshSelectedFromList(selected_constraints);
}

htmlElements.constraintsSelectAll.checked = false;
htmlElements.constraintsSelectAll.onchange = selectAll;

// builds a div... helps with the code
let divBuilder = (args = {}) => {
    let div = document.createElement('div');
    for (let [key, value] of Object.entries(args)) {
        div.setAttribute(key, value);
    }
    return div;
}

// builds a div that contains an icon and text
let iconTextBuilder = (imgurl, value, attr) => {
    let div = divBuilder({'class': 'icon-text ' + attr});
    let icondiv = divBuilder({'class': 'icon-div'});
    let img = document.createElement('img');
    img.setAttribute('class', 'icon-info');
    img.src = imgurl;
    let strong = document.createElement('strong');
    strong.innerText = value;
    icondiv.append(img);
    div.append(icondiv, strong)

    return div;
}

// event handler that activates a constraint
let toggleConstraint = (e) => {
    // Get constraint's id as in the constraints object
    let pageid = e.getAttribute('data-cst-id');

    // Get its constraint object
    let ele = constraints[pageid];

    // Toggle its activation
    ele.is_active = !ele.is_active;

    console.log(ele);
    refreshConstraints();
}

let openNewConstraintPopup = () => {
    setState(State.CreateNewConstraint);
    const modal = new bootstrap.Modal(htmlElements.constraintsEditPopup, null);

    resetNewConstraint();
    fillEditConstraintPopup(null);

    modal.show();
};
htmlElements.newConstraintButton.addEventListener('click', openNewConstraintPopup);

let editSelectedConstraint = () => {
    if (!lastSelectedConstraint) {
        return;
    }
    setState(State.EditConstraint);

    const modal = new bootstrap.Modal(htmlElements.constraintsEditPopup, null);

    editConstraint = copyObj(constraints[lastSelectedConstraint]);
    updateEditConstraintPopup(editConstraint);

    modal.show();
};

let deleteSelectedConstraint = () => {
    if (!lastSelectedConstraint) {
        return;
    }
    changeEvents.deleteConstraint(lastSelectedConstraint);
};

let deleteSelectedConstraints = () => {
    selected_constraints.forEach(pageid => {
        changeEvents.deleteConstraint(pageid);
    });
};

// builds the card for the constraint
let constraintCardBuilder = (constraint) => {
    const wrapper = divBuilder({
        'class': 'card border border-3 border-primary me-1 mb-1 constraint-card h-25',
        'style': 'width: 18rem;',
        'data-cst-id': constraint.pageid,
        'draggable': true,
    });

    let localName = findConstraintLocalNameFromClass(constraint.name);

    let checkText = constraint.is_active ? 'checked' : "";

    wrapper.innerHTML = [
        `<h6 class="card-header py-1">${constraint.title || localName}</h6>`,
        '<div class="card-body py-0">',
        `    <h7 class="card-subtitle mt-0 mb-1 text-muted">${constraint.comment ?? ''}</h7>`,
        `    <div class="container-fluid">`,
        '        <div class="row">',
        `        <div class="col">${iconTextBuilder(htmlElements.iconGears.src, constraint.parameters.length, 'parameters').outerHTML}</div>`,
        `        <div class="col">${iconTextBuilder(htmlElements.iconWeight.src, constraint.weight, 'weight').outerHTML}</div>`,
        `        <div class="col text-end"><input type="checkbox" data-cst-id="${constraint.pageid}" ${checkText} onchange="toggleConstraint(this)"></div>`,
        '</div>',
    ].join('');

    wrapper.addEventListener('click', constraintClicked, false);
    wrapper.addEventListener('mouseenter', constraintHovered, false);
    wrapper.addEventListener('mouseleave', constraintUnhovered, false);
    wrapper.addEventListener("dragstart", (ev) => {
        // Add the target element's id to the data transfer object
        ev.dataTransfer.setData("text/plain", ev.target.id);
    });

    return wrapper;
}

// empty the page
let emptyPage = () => {
    let body = htmlElements.enabledConstraintsList;
    let bodyDisabled = htmlElements.disabledConstraintsList;
    body.innerHTML = "";
    bodyDisabled.innerHTML = "";
}

// constranit sorting based on argument
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

// updates the weight for all constraints
let editSelectedConstraintsWeight = () => {
    let weight = htmlElements.selectedConstraintsEditWeightSlider.value;
    selected_constraints.forEach(id => {
        constraints[id].weight = weight;
    });
    refreshConstraints();
}

htmlElements.selectedConstraintsEditWeightButton.onclick = editSelectedConstraintsWeight;
htmlElements.selectedConstraintsDeleteButton.onclick = deleteSelectedConstraints;

htmlElements.constraintHeaderDeleteButton.onclick = deleteSelectedConstraint;
htmlElements.constraintHeaderEditButton.onclick = editSelectedConstraint;

// duplicate a constraint
let duplicateSelectedConstraint = (e) => {
    if (!lastSelectedConstraint) {
        return;
    }
    let constr = constraints[`${lastSelectedConstraint}`];
    let newid = changeEvents.duplicateConstraint(constr['pageid']);
    // constraints[copy['pageid']] = copy;
    selected_constraints = [];
    refreshConstraints();
    clickConstraint(newid);
}

let constraint_list = null;
let filtered_constraint_list = null;
let constraint_metadata = null;

// fetch data from database
fetchers.fetchDepartments(null);
fetchers.fetchTrainingPrograms(null);
fetchers.fetchStructuralGroups(null);
fetchers.fetchTutors(null);
fetchers.fetchModules(null);
fetchers.fetchCourseTypes(null);
fetchers.fetchTutorsIDs(null);
//fetchers.fetchCourses(null);
fetchers.fetchWeeks();
fetchers.fetchConstraintTypes();
fetchers.fetchConstraints(null);

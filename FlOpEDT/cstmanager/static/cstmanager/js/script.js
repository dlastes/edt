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

let csts2 = {
    1: {
        "id": 1,
        "name": "MinGroupsHalfDays",
        "weight": 8,
        "is_active": true,
        "comment": null,
        "modified_at": "2021-06-28",
        "weeks": [],
        "parameters": [{
                "name": "department",
                "type": "base.Department",
                "required": true,
                "multiple": false,
                "all_except": false,
                "id_list": [
                    2
                ],
                "acceptable": [
                    2,
                    29,
                    30,
                    31,
                    32
                ]
            },
            {
                "name": "train_progs",
                "type": "base.TrainingProgramme",
                "required": false,
                "multiple": true,
                "all_except": false,
                "id_list": [],
                "acceptable": [
                    3,
                    4,
                    5
                ]
            },
            {
                "name": "groups",
                "type": "base.StructuralGroup",
                "required": false,
                "multiple": true,
                "all_except": false,
                "id_list": [
                    23,
                    24,
                    25,
                    26,
                    27,
                    28,
                    29,
                    30,
                    35,
                    36,
                    37,
                    38,
                    39,
                    40,
                    41
                ],
                "acceptable": [
                    18,
                    19,
                    20,
                    21,
                    22,
                    23,
                    24,
                    25,
                    26,
                    27,
                    28,
                    29,
                    30,
                    31,
                    32,
                    33,
                    34,
                    35,
                    36,
                    37,
                    38,
                    39,
                    40,
                    41,
                    42,
                    43
                ]
            }
        ]
    },
    2: {
        "id": 2,
        "name": "MinNonPreferedTrainProgsSlot",
        "weight": 8,
        "is_active": true,
        "comment": null,
        "modified_at": "2021-06-28",
        "weeks": [],
        "parameters": [{
                "name": "department",
                "type": "base.Department",
                "required": true,
                "multiple": false,
                "all_except": false,
                "id_list": [
                    2
                ],
                "acceptable": [
                    2,
                    29,
                    30,
                    31,
                    32
                ]
            },
            {
                "name": "train_progs",
                "type": "base.TrainingProgramme",
                "required": false,
                "multiple": true,
                "all_except": false,
                "id_list": [],
                "acceptable": [
                    3,
                    4,
                    5
                ]
            }
        ]
    },
    3: {
        "id": 3,
        "name": "MinTutorsHalfDays",
        "weight": 8,
        "is_active": true,
        "comment": null,
        "modified_at": "2021-06-28",
        "weeks": [],
        "parameters": [{
                "name": "department",
                "type": "base.Department",
                "required": true,
                "multiple": false,
                "all_except": false,
                "id_list": [
                    2
                ],
                "acceptable": [
                    2,
                    29,
                    30,
                    31,
                    32
                ]
            },
            {
                "name": "join2courses",
                "type": "BooleanField",
                "required": true,
                "multiple": false,
                "all_except": false,
                "id_list": [],
                "acceptable": []
            },
            {
                "name": "train_progs",
                "type": "base.TrainingProgramme",
                "required": false,
                "multiple": true,
                "all_except": false,
                "id_list": [],
                "acceptable": [
                    3,
                    4,
                    5
                ]
            },
            {
                "name": "tutors",
                "type": "people.Tutor",
                "required": false,
                "multiple": true,
                "all_except": false,
                "id_list": [
                    46,
                    47,
                    55,
                    60,
                    72,
                    73,
                    76,
                    83,
                    89,
                    93,
                    109,
                    111,
                    117,
                    125,
                    138,
                    142,
                    144,
                    145
                ],
                "acceptable": [
                    153,
                    150,
                    46,
                    47,
                    48,
                    49,
                    50,
                    51,
                    52,
                    664,
                    53,
                    189,
                    54,
                    55,
                    660,
                    56,
                    57,
                    58,
                    59,
                    60,
                    61,
                    62,
                    63,
                    64,
                    65,
                    66,
                    225,
                    67,
                    68,
                    69,
                    70,
                    71,
                    72,
                    73,
                    74,
                    152,
                    75,
                    151,
                    196,
                    76,
                    198,
                    77,
                    234,
                    195,
                    236,
                    78,
                    79,
                    80,
                    81,
                    82,
                    83,
                    84,
                    85,
                    86,
                    87,
                    88,
                    89,
                    90,
                    91,
                    92,
                    93,
                    94,
                    95,
                    96,
                    97,
                    98,
                    128,
                    99,
                    100,
                    101,
                    102,
                    194,
                    103,
                    193,
                    104,
                    105,
                    106,
                    237,
                    107,
                    108,
                    190,
                    109,
                    110,
                    33,
                    111,
                    112,
                    113,
                    114,
                    115,
                    116,
                    117,
                    118,
                    119,
                    120,
                    121,
                    122,
                    123,
                    124,
                    125,
                    126,
                    127,
                    129,
                    130,
                    131,
                    132,
                    133,
                    134,
                    135,
                    136,
                    140,
                    137,
                    138,
                    139,
                    192,
                    141,
                    142,
                    197,
                    231,
                    143,
                    144,
                    145,
                    661,
                    154,
                    146,
                    147,
                    148,
                    149
                ]
            }
        ]
    },
    4: {
        "id": 4,
        "name": "MinNonPreferedTutorsSlot",
        "weight": 8,
        "is_active": true,
        "comment": null,
        "modified_at": "2021-06-28",
        "weeks": [],
        "parameters": [{
                "name": "department",
                "type": "base.Department",
                "required": true,
                "multiple": false,
                "all_except": false,
                "id_list": [
                    2
                ],
                "acceptable": [
                    2,
                    29,
                    30,
                    31,
                    32
                ]
            },
            {
                "name": "train_progs",
                "type": "base.TrainingProgramme",
                "required": false,
                "multiple": true,
                "all_except": false,
                "id_list": [],
                "acceptable": [
                    3,
                    4,
                    5
                ]
            },
            {
                "name": "tutors",
                "type": "people.Tutor",
                "required": false,
                "multiple": true,
                "all_except": false,
                "id_list": [],
                "acceptable": [
                    153,
                    150,
                    46,
                    47,
                    48,
                    49,
                    50,
                    51,
                    52,
                    664,
                    53,
                    189,
                    54,
                    55,
                    660,
                    56,
                    57,
                    58,
                    59,
                    60,
                    61,
                    62,
                    63,
                    64,
                    65,
                    66,
                    225,
                    67,
                    68,
                    69,
                    70,
                    71,
                    72,
                    73,
                    74,
                    152,
                    75,
                    151,
                    196,
                    76,
                    198,
                    77,
                    234,
                    195,
                    236,
                    78,
                    79,
                    80,
                    81,
                    82,
                    83,
                    84,
                    85,
                    86,
                    87,
                    88,
                    89,
                    90,
                    91,
                    92,
                    93,
                    94,
                    95,
                    96,
                    97,
                    98,
                    128,
                    99,
                    100,
                    101,
                    102,
                    194,
                    103,
                    193,
                    104,
                    105,
                    106,
                    237,
                    107,
                    108,
                    190,
                    109,
                    110,
                    33,
                    111,
                    112,
                    113,
                    114,
                    115,
                    116,
                    117,
                    118,
                    119,
                    120,
                    121,
                    122,
                    123,
                    124,
                    125,
                    126,
                    127,
                    129,
                    130,
                    131,
                    132,
                    133,
                    134,
                    135,
                    136,
                    140,
                    137,
                    138,
                    139,
                    192,
                    141,
                    142,
                    197,
                    231,
                    143,
                    144,
                    145,
                    661,
                    154,
                    146,
                    147,
                    148,
                    149
                ]
            }
        ]
    },
    5: {
        "id": 5,
        "name": "MinModulesHalfDays",
        "weight": 8,
        "is_active": true,
        "comment": null,
        "modified_at": "2021-06-28",
        "weeks": [],
        "parameters": [{
                "name": "department",
                "type": "base.Department",
                "required": true,
                "multiple": false,
                "all_except": false,
                "id_list": [],
                "acceptable": [
                    2,
                    29,
                    30,
                    31,
                    32
                ]
            },
            {
                "name": "train_progs",
                "type": "base.TrainingProgramme",
                "required": false,
                "multiple": true,
                "all_except": false,
                "id_list": [],
                "acceptable": [
                    3,
                    4,
                    5,
                    59,
                    60,
                    61,
                    62,
                    63,
                    66,
                    67,
                    68
                ]
            },
            {
                "name": "modules",
                "type": "base.Module",
                "required": false,
                "multiple": true,
                "all_except": false,
                "id_list": [
                    127,
                    1677,
                    125,
                    138,
                    126,
                    1661,
                    121,
                    1676,
                    145,
                    144,
                    1679,
                    142,
                    1672,
                    146,
                    129,
                    1678,
                    135,
                    139,
                    1674,
                    147,
                    137,
                    1675,
                    143,
                    140,
                    610,
                    132,
                    120,
                    119,
                    134,
                    130,
                    141,
                    122,
                    609,
                    611,
                    1658,
                    148,
                    149,
                    150,
                    123,
                    136,
                    128,
                    133,
                    1673,
                    131,
                    124
                ],
                "acceptable": [
                    86,
                    105,
                    1603,
                    1581,
                    127,
                    1551,
                    1561,
                    1585,
                    1677,
                    64,
                    78,
                    82,
                    1586,
                    125,
                    1611,
                    1422,
                    1437,
                    1626,
                    1638,
                    1455,
                    1483,
                    1484,
                    1485,
                    1463,
                    1499,
                    1653,
                    1498,
                    138,
                    126,
                    68,
                    1657,
                    70,
                    1661,
                    99,
                    1667,
                    1577,
                    1578,
                    89,
                    1616,
                    121,
                    1676,
                    145,
                    144,
                    102,
                    61,
                    1679,
                    142,
                    1672,
                    146,
                    81,
                    103,
                    608,
                    129,
                    1678,
                    107,
                    135,
                    1610,
                    1625,
                    1637,
                    1652,
                    139,
                    1674,
                    1688,
                    1659,
                    1665,
                    1666,
                    73,
                    94,
                    95,
                    88,
                    1636,
                    147,
                    137,
                    1675,
                    143,
                    1682,
                    1521,
                    1509,
                    1511,
                    1510,
                    1522,
                    1523,
                    1548,
                    1560,
                    1684,
                    1685,
                    1686,
                    1687,
                    1620,
                    1655,
                    1662,
                    140,
                    610,
                    1602,
                    1618,
                    1632,
                    1646,
                    92,
                    132,
                    120,
                    79,
                    114,
                    1423,
                    1438,
                    1488,
                    1456,
                    1486,
                    1487,
                    1500,
                    1501,
                    1464,
                    1619,
                    1633,
                    65,
                    119,
                    607,
                    605,
                    1549,
                    1565,
                    1567,
                    1427,
                    1419,
                    1461,
                    1497,
                    1541,
                    1542,
                    1543,
                    1557,
                    1605,
                    1466,
                    1504,
                    134,
                    1558,
                    1575,
                    1576,
                    1647,
                    67,
                    110,
                    66,
                    112,
                    115,
                    130,
                    1640,
                    1635,
                    77,
                    80,
                    1656,
                    93,
                    1513,
                    1524,
                    1512,
                    1525,
                    1683,
                    1514,
                    1526,
                    111,
                    58,
                    60,
                    113,
                    74,
                    1415,
                    1417,
                    1418,
                    1428,
                    1443,
                    1433,
                    1477,
                    1431,
                    1448,
                    1481,
                    1454,
                    1482,
                    1460,
                    1496,
                    1537,
                    1572,
                    141,
                    1515,
                    1527,
                    1528,
                    1516,
                    1517,
                    1529,
                    57,
                    122,
                    1589,
                    609,
                    1536,
                    1553,
                    1571,
                    1588,
                    1538,
                    1539,
                    1554,
                    1555,
                    1573,
                    1590,
                    63,
                    1544,
                    1559,
                    1579,
                    1583,
                    611,
                    1658,
                    91,
                    148,
                    149,
                    150,
                    1664,
                    1615,
                    96,
                    1612,
                    1628,
                    1639,
                    1425,
                    1429,
                    1426,
                    1440,
                    1444,
                    1441,
                    1458,
                    1493,
                    1492,
                    1507,
                    1468,
                    1508,
                    1550,
                    1568,
                    1569,
                    1593,
                    123,
                    1547,
                    1564,
                    1582,
                    1595,
                    1670,
                    136,
                    75,
                    1442,
                    1617,
                    1631,
                    1645,
                    1634,
                    72,
                    1649,
                    606,
                    1424,
                    1540,
                    1613,
                    69,
                    1556,
                    83,
                    1629,
                    1439,
                    1491,
                    98,
                    1457,
                    1574,
                    1490,
                    1643,
                    1489,
                    1503,
                    1502,
                    1591,
                    1648,
                    1465,
                    1614,
                    1630,
                    1644,
                    1651,
                    1606,
                    100,
                    128,
                    90,
                    84,
                    1623,
                    1607,
                    1621,
                    1654,
                    1421,
                    1436,
                    1453,
                    1462,
                    104,
                    76,
                    62,
                    97,
                    1599,
                    1668,
                    1598,
                    1669,
                    1601,
                    1600,
                    101,
                    87,
                    109,
                    1680,
                    1681,
                    1663,
                    1650,
                    71,
                    1641,
                    106,
                    1413,
                    1416,
                    1430,
                    1432,
                    1470,
                    1471,
                    1445,
                    1469,
                    1446,
                    1472,
                    1473,
                    1474,
                    1449,
                    1478,
                    1452,
                    1467,
                    1505,
                    1506,
                    1604,
                    1609,
                    1624,
                    1597,
                    1596,
                    118,
                    117,
                    1534,
                    1533,
                    133,
                    1673,
                    59,
                    1592,
                    1627,
                    1608,
                    1622,
                    85,
                    116,
                    1671,
                    108,
                    1594,
                    1420,
                    1546,
                    1434,
                    1563,
                    1435,
                    1476,
                    1475,
                    1447,
                    1479,
                    1450,
                    1480,
                    1451,
                    1495,
                    1494,
                    1459,
                    1535,
                    1552,
                    1570,
                    1587,
                    1642,
                    1414,
                    1566,
                    1580,
                    1584,
                    1545,
                    1562,
                    131,
                    124,
                    1518,
                    1530,
                    1519,
                    1531,
                    1520,
                    1532
                ]
            }
        ]
    }
}


constraints = {...constraints, ...csts2 };

let outputSlider = (id, val) => {
    val = val == 8 ? 0 : val;
    let ele = document.getElementById(id);
    ele.innerHTML = val;
}


let URLWeightIcon = document.getElementById('icon-weight').src;
let URLGearsIcon = document.getElementById('icon-gears').src;
let URLCheckIcon = document.getElementById('icon-check').src;
let constraintTitle = document.getElementById('constraint-header-title');
let constraintComment = document.getElementById('constraint-header-comment');
let paramsDiv = document.getElementById('params');
let activatedEle = document.getElementById('id2');
let sliderOne = document.getElementById('slider-one');

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
    let color = obj.length > 0 ? "neutral" : "danger";
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
    constraintTitle.innerText = obj['name'];
    constraintComment.innerText = obj['comment'];
    paramsDiv.innerHTML = "";
    activatedEle.checked = obj['is_active'];
    sliderOne.value = obj['weight'];
    outputSlider('poidsvalue1', obj['weight']);
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
    Array.from(document.getElementById('constraints-list').children).forEach(node => {
        let obj = constraints[node.getAttribute('cst-id')];
        node.querySelector('input').checked = obj.is_active;
        node.querySelector('.icon-text.weight').querySelector('strong').innerText = obj.weight;
        node.querySelector('.icon-text.parameters').querySelector('strong').innerText = obj.parameters.length;
    });
    Array.from(document.getElementById('constraints-disabled').children).forEach(node => {
        let obj = constraints[node.getAttribute('cst-id')];
        node.querySelector('input').checked = obj.is_active;
        node.querySelector('.icon-text.weight').querySelector('strong').innerText = obj.weight;
        node.querySelector('.icon-text.parameters').querySelector('strong').innerText = obj.parameters.length;
    });
}

let rearrange = () => {
    let constraint_list = Object.keys(constraints);
    let body = document.getElementById('constraints-list');
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
    let l = document.getElementById('constraints-list');
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
    let d = document.getElementById('constraints-list').querySelector(str);
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
    enabled.setAttribute('cst-id', cst_obj.id);
    enabled.onchange = activateConstraint;
    let weight = iconTextBuilder(URLWeightIcon, cst_obj.weight, "weight")
    div.append(params, weight, enabled);
    return div;
}

let constraintCardBuilder = (cst_obj) => {
    let selected = selected_constraints.has(`${cst_obj.id}`) ? "selected" : "unselected";
    let divCard = divBuilder({ 'class': 'constraint-card transition' });
    divCard.setAttribute('cst-id', cst_obj['id']);
    let divCardInfo = divBuilder({ 'class': 'constraint-card-info transition ' + selected });
    let divCardText = divBuilder({ 'class': 'constraint-card-text ' });
    divCardInfo.addEventListener('click', constraintClicked, false);
    divCardInfo.addEventListener('mouseenter', constraintHovered, false);
    divCardInfo.addEventListener('mouseleave', constraintUnhovered, false);
    let divTitle = divBuilder({ 'class': 'constraint-card-title' });
    divTitle.innerHTML = cst_obj['name'];
    let divDesc = divBuilder({ 'class': 'constraint-card-description' });
    // divDesc.innerHTML = cst_obj['comment'];
    divDesc.innerHTML = cst_obj['parameters'].reduce((a, b) => {
        return a + b['name'] + ', ';
    }, "")
    let divAdd = additionalInfoBuilder(cst_obj);
    divCardText.append(divTitle, divDesc);
    divCardInfo.append(divCardText, divAdd);
    divCard.append(divCardInfo);
    return divCard;
}

let disabledConstraintCardBuilder = (cst_obj) => {
    let selected = selected_constraints.has(`${cst_obj.id}`) ? "selected" : "unselected";
    let divCard = divBuilder({ 'class': 'constraint-card-disabled transition' });
    divCard.setAttribute('cst-id', cst_obj['id']);
    let divCardInfo = divBuilder({ 'class': 'constraint-card-info-disabled transition ' + selected });
    let divCardText = divBuilder({ 'class': 'constraint-card-text ' });
    divCardInfo.addEventListener('click', constraintClicked, false);
    divCardInfo.addEventListener('mouseenter', constraintHovered, false);
    divCardInfo.addEventListener('mouseleave', constraintUnhovered, false);
    let divTitle = divBuilder({ 'class': 'constraint-card-title' });
    divTitle.innerHTML = cst_obj['name'];
    let divDesc = divBuilder({ 'class': 'constraint-card-description' });
    // divDesc.innerHTML = cst_obj['comment'];
    divDesc.innerHTML = cst_obj['parameters'].reduce((a, b) => {
        return a + b['name'] + ', ';
    }, "")
    let divAdd = divBuilder({ 'class': 'constraint-card-additional' });
    divCardText.append(divTitle, divDesc);
    let enabled = document.createElement('input');
    enabled.setAttribute('type', 'checkbox');
    enabled.checked = cst_obj.is_active;
    enabled.setAttribute('cst-id', cst_obj.id);
    enabled.onchange = activateConstraint;
    divAdd.append(enabled);
    divCardInfo.append(divCardText, divAdd);
    divCard.append(divCardInfo);
    return divCard;
}

let renderConstraints = (cst_list = []) => {
    let body = document.getElementById('constraints-list');
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
    copy['id'] = Math.max(...Object.keys(constraints)) + 1
    constraints[copy['id']] = copy;
    rearrange();
})

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
// })
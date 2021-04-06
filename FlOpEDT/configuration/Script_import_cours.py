# Coucou! Ici on cree un liste de cours à partir d'hyperplanning pour les mettre dans flOp

from hyperplanning import *

def create_course_set_from_hp(username,password,lPrefixeWsdl):
    # Initialisation et connexion
    session = Session()
    session.auth = HTTPBasicAuth(username,password)

    adminService = Client(lPrefixeWsdl + 'IHpSvcWAdmin', transport=Transport(session=session))
    courseService = Client(lPrefixeWsdl + 'IHpSvcWCours',transport=Transport(session=session))
    peopleService = Client(lPrefixeWsdl + 'IHpSvcWEnseignants', transport=Transport(session=session))
    promService = Client(lPrefixeWsdl + 'IHpSvcWPromotions', transport=Transport(session=session))
    tdOptService = Client(lPrefixeWsdl + 'IHpSvcWTDOptions', transport=Transport(session=session))
    moduleService = Client(lPrefixeWsdl + 'IHpSvcWMatieres', transport=Transport(session=session))
    
    # Verification des identifiants
    try:
        print ('Connected to: ' + adminService.service.Version()+"\n")
    except:
        print('Connection failed: either your username/password combination is wrong or your connection is down. Maybe both')
        return None

    validCourseKeys = getValidCourseKeys(courseService,5000)

    coursesList = []

    for i in tqdm(validCourseKeys,"Courses - Extracting : ", bar_format='{l_bar}{bar:15}{r_bar}{bar:-10b}'):
        # type
        courseType =  courseService.service.TypeCours(i)+"_"+str(round(courseService.service.DureeCours(i)*24*60))+"m"

        # room_type
        roomType = 'all'  # Temporaire

        # number
        courseNumber = 0

        # tutor and supp_tutor        
        listOfTutors = courseService.service.EnseignantsDuCours(i)
        courseTutor = None
        courseSuppTutor = set()
        if len(listOfTutors) == 1:
            courseTutor = peopleService.service.IdentifiantCASEnseignant(listOfTutors[0])
        elif len(listOfTutors)>1:
            for j in listOfTutors:
                courseSuppTutor.add(peopleService.service.IdentifiantCASEnseignant(j))
                        
        # groups
        listOfCourseProms = courseService.service.PromotionsDuCours(i)
        listOfCourseTDOpt = courseService.service.TDOptionsDuCours(i)
        courseGroups = set()        
        for j in listOfCourseProms:
            courseGroups.add(promService.service.NomPromotion(j))
        for j in listOfCourseTDOpt:
            courseGroups.add(tdOptService.service.NomTDOption(j))

        # module
        courseModule = moduleService.service.LibelleMatiere(courseService.service.MatiereCours(i))

        # week and year
        courseWeek = None
        hpWeek = courseService.service.DomaineCours(i)
        if len(hpWeek)>0:
            hpWeek = hpWeek[0]
            courseWeek = courseService.service.SemaineEnSemaineCalendaire(hpWeek)
            courseYear = str(courseService.service.SemaineEnDate(hpWeek))[0:4]

        course = {"type" : courseType,
                        "room_type" : roomType,
                        "no" : courseNumber,
                        "tutor" : courseTutor,
                        "supp_tutor" : courseSuppTutor,
                        "groups" : courseGroups,
                        "module" : courseModule,
                        "week" : courseWeek,
                        "year" : courseYear}

        if  courseWeek != None: # Modifier
            coursesList.append(course)
    return coursesList


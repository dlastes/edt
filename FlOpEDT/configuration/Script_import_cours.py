# Coucou! Ici on cree un liste de cours à partir d'hyperplanning pour les mettre dans flOp

from import_hyperplanning import *

def create_course_set_from_hp(username,password,lPrefixeWsdl):
    # Initialisation et connexion
    session = Session()
    session.auth = HTTPBasicAuth(username,password)

    adminService = Client(lPrefixeWsdl + 'IHpSvcWAdmin', transport=Transport(session=session))
    courseService = Client(lPrefixeWsdl + 'IHpSvcWCours',transport=Transport(session=session))
    peopleService = Client(lPrefixeWsdl + 'IHpSvcWEnseignants', transport=Transport(session=session))
    
    # Verification des identifiants
    try:
        print ('Connected to: ' + adminService.service.Version()+"\n")
    except:
        print('Connection failed: either your username/password combination is wrong or your connection is down. Maybe both')
        return None

    validCourseKeys = getValidCourseKeys(courseService,200)

    coursesSet = set()

    for i in tqdm(validCourseKeys,"Courses - Extracting : ", bar_format='{l_bar}{bar:15}{r_bar}{bar:-10b}'):
        typeDeCours =  courseService.service.TypeCours(i)+"_"+str(courseService.service.DureeCours(i))+"m"
        roomType = 'all'
        
        listOfTeachers = courseService.service.EnseignantsDuCours(i)
        if len(listOfTeachers) == 0:
            tutor = None
            supp_tutor = None
        elif len(listOfTeachers) == 1:
            tutor = peopleService.service.IdentifiantCASEnseignant(listOfTeachers[0])
        else:
            tutor = None
            supp_tutor = set()
            for j in listOfTeachers:
                supp_tutor.add(peopleService.service.IdentifiantCASEnseignant(j))
            
        no = 0
            

        listOfCourseProms = courseService.service.PromotionsDuCours(i)
        listOfCourseTDOpt = courseService.service.TDOptionsDuCours(i)
        
        

    
if __name__ == "__main__":
    nomUtilisateur   = "lkosinsk"
    motDePasse        = "KO59lu21&*"
    lien                      = 'https://edt.ens2m.fr/hpsw/2019-2020/wsdl/'
    print(create_course_set_from_hp(nomUtilisateur,motDePasse,lien))

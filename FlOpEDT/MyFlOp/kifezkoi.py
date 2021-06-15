from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport
from tqdm import tqdm


def get_teacher_dictionary(services):
    teacherDictionary = {}
    teacherKeys = services["teacher"].TousLesEnseignants()
    for i in tqdm(teacherKeys,"Loading teachers   ", bar_format='{l_bar}{bar:15}{r_bar}{bar:-10b}'):
        teacherDictionary[i] = services["teacher"].IdentifiantCASEnseignant(i)
    return teacherDictionary
def get_prom_dictionary(services):
    promDictionary = {}
    promKeys = services["prom"].ToutesLesPromotions()
    groupsKeys = services["groups"].TousLesTDOptions()
    for i in tqdm(promKeys,"Loading promotions : ", bar_format='{l_bar}{bar:15}{r_bar}{bar:-10b}'):
        promDictionary[i] = services["prom"].NomPromotion(i)
    for i in tqdm(groupsKeys,"Loading groups     ", bar_format='{l_bar}{bar:15}{r_bar}{bar:-10b}'):
        promDictionary[i] = promDictionary[services["groups"].PromotionTDOption(i)]
    return promDictionary    
def get_module_dictionary(services):
    moduleDictionary = {}
    moduleKeys = services["module"].ToutesLesMatieres()
    for i in tqdm(moduleKeys,"Loading modules    ", bar_format='{l_bar}{bar:15}{r_bar}{bar:-10b}'):
        moduleDictionary[i] = services["module"].LibelleMatiere(i)
    return moduleDictionary
def get_valid_course_keys(services,breakLevel=-1):
    listCoursesKeys = services["courses"].TousLesCours()
    if len(listCoursesKeys)>breakLevel:
        listCoursesKeys = listCoursesKeys[0:breakLevel]
    validCourseKeys = []
    for i in tqdm(listCoursesKeys,"Validating courses ", bar_format='{l_bar}{bar:15}{r_bar}{bar:-10b}'):
        if services["courses"].CoursEstUnCoursFils(i) or services["courses"].CoursEstUnCoursSimple(i):
            if not services["courses"].EstCoursNonPlace(i):
                validCourseKeys.append(i)
    return validCourseKeys

def assign_teachers_to_modules(session,courseKeys,teacherDictionary,promDictionary,moduleDictionary):
    dictionaryOfAssignedTeacher = {}
    for i in tqdm(courseKeys,"Processing         ", bar_format='{l_bar}{bar:15}{r_bar}{bar:-10b}'):
        courseModule = moduleDictionary[services["courses"].MatiereCours(i)]
        courseTeachers = [teacherDictionary[j] for j in services["courses"].EnseignantsDuCours(i)]
        courseProms = [promDictionary[j] for j in services["courses"].PromotionsDuCours(i)]
        courseGroups =[promDictionary[j] for j in services["courses"].TDOptionsDuCours(i)]
        courseProms = courseProms+courseGroups

        if courseModule not in dictionaryOfAssignedTeacher.keys():
            dictionaryOfAssignedTeacher[courseModule] = {}

        for j in courseProms:
            if j not in dictionaryOfAssignedTeacher[courseModule].keys():
                dictionaryOfAssignedTeacher[courseModule][j] = []

            for k in courseTeachers:
                if k not in dictionaryOfAssignedTeacher[courseModule][j]:
                    dictionaryOfAssignedTeacher[courseModule][j].append(k)

    return dictionaryOfAssignedTeacher
        
        
            

    
if __name__ == "__main__":
    session = Session()
    session.auth = HTTPBasicAuth("lkosinsk", input("Mot de passe: "))
    lPrefixeWsdl = 'https://edt.ens2m.fr/hpsw/2020-2021/wsdl/'

    services = {}
    services["admin"] = Client(lPrefixeWsdl + 'IHpSvcWAdmin', transport=Transport(session=session)).service
    services["teacher"] = Client(lPrefixeWsdl + 'IHpSvcWEnseignants', transport=Transport(session=session)).service
    services["courses"] = Client(lPrefixeWsdl + 'IHpSvcWCours', transport=Transport(session=session)).service
    services["module"] = Client(lPrefixeWsdl + 'IHpSvcWMatieres', transport=Transport(session=session)).service
    services["prom"] = Client(lPrefixeWsdl + 'IHpSvcWPromotions', transport=Transport(session=session)).service
    services["groups"] = Client(lPrefixeWsdl + 'IHpSvcWTDOptions', transport=Transport(session=session)).service
    
    try:
        print ('Connecté à ' + services["admin"].Version())
        connecte = True
    except:
        print('Problèmes de connection: identifiants incorrect ou pb de co?')
        connecte = False

    if connecte:
        teacherDictionary = get_teacher_dictionary(services)
        promDictionary = get_prom_dictionary(services)
        moduleDictionary = get_module_dictionary(services)
        validCourseKeys = get_valid_course_keys(services)
        teacherAssignation = assign_teachers_to_modules(session,validCourseKeys,teacherDictionary,promDictionary,moduleDictionary)

        print("\n\n")
        print(teacherAssignation)
        print("\n\n")
        
        for i in teacherAssignation.keys(): #Modules
            print(i)
            for j in teacherAssignation[i].keys(): #Proms
                print("    "+j)
                for k in teacherAssignation[i][j]: #Profs
                    print("        "+k)
                print("")
            print("")

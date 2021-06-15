# Script pour faire des petits test bien sympa

from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport
from tqdm import tqdm
import numpy as np

def getValidCourseKeys(IHpSvcWCours,breakLevel=-1): # Certainement possible d'accelerer tout ça, mais les fonctions de l'API ne fonctionnent pas...
    listCoursesKeys = IHpSvcWCours.service.TousLesCours()#[0:breakLevel]
    if len(listCoursesKeys)>breakLevel:
        listCoursesKeys = listCoursesKeys[0:breakLevel]
    validCourseKeys = []
    for i in tqdm(listCoursesKeys,"Courses - Validating : ", bar_format='{l_bar}{bar:15}{r_bar}{bar:-10b}'):
        if IHpSvcWCours.service.CoursEstUnCoursFils(i) or IHpSvcWCours.service.CoursEstUnCoursSimple(i):
            if not IHpSvcWCours.service.EstCoursNonPlace(i):
                validCourseKeys.append(i)
    return validCourseKeys


session = Session()
mdp = input("mot de passe svp: ")
session.auth = HTTPBasicAuth("lkosinsk", mdp)

lPrefixeWsdl='https://edt.ens2m.fr/hpsw/2020-2021/wsdl/'

# Interfaces utilisées
Matiere = Client(lPrefixeWsdl + 'IHpSvcWMatieres', transport=Transport(session=session))
Admin  = Client(lPrefixeWsdl + 'IHpSvcWAdmin', transport=Transport(session=session))
Salles    = Client(lPrefixeWsdl + 'IHpSvcWSalles', transport=Transport(session=session))
Promo   = Client(lPrefixeWsdl + 'IHpSvcWPromotions', transport=Transport(session=session))
TDOpt   = Client(lPrefixeWsdl + 'IHpSvcWTDOptions', transport=Transport(session=session))
Enseign = Client(lPrefixeWsdl + 'IHpSvcWEnseignants', transport=Transport(session=session))
Cours     = Client(lPrefixeWsdl + 'IHpSvcWCours',transport=Transport(session=session))
Regroupement = Client(lPrefixeWsdl + 'IHpSvcWRegroupements',transport=Transport(session=session))
ModuCurs= Client(lPrefixeWsdl+'IHpSvcWModulesCursus',transport=Transport(session=session))
CoursAnnule = Client(lPrefixeWsdl+'IHpSvcWCoursAnnules',transport=Transport(session=session))

# Affichage de la version

try:
    print ('Connecté à ' + Admin.service.Version())
    connecte = True
        
except:
    print('Problèmes de connection: identifiants incorrect ou pb de co?')
    connecte = False

if connecte:
    listeCours = Cours.service.TousLesCours()
    print(len(listeCours))
    listeCoursPasValide = Cours.service.ClesCoursInvalidesTableauDeCours(ATableau = listeCours)
    print(len(listeCoursPasValide))
    listeCoursValide = Cours.service.ClesCoursValidesTableauDeCours(listeCours)
    print(len(listeCoursValide))
    #listeCoursPere = Cours.service.TousLesCoursFils(ATableau=listeCours)
    #listeCoursFils = Cours.service.TousLesCoursPere(ATableau=listeCours)

    listeCleCours = getValidCourseKeys(Cours,50)
    
    for i in listeCleCours:
        proprio = Matiere.service.ProprietaireMatiere(Cours.service.MatiereCours(i))
        if proprio != None:
            Nom, Prenom = proprio.split(" ")
            print(Prenom)
            print("Len de Prenom: "+str(len(Prenom)))
            print(Nom)
            print("Len de Nom: "+str(len(Nom)))

from cours_ENSMM import cours_ENSMM
from database_ENSMM import database_ENSMM


def clear_terminal():
    print(100*"\n")


def strToIntValid(str):
    try:
        value = int(str)
        return True, value
    except: return False, 0


def create_room_type(listOfRoomTypes, dictOfRoomTypes, roomName):
    newRoomType = input("Quel est le nom du type de salle pour la salle "+roomName+"? : ")
    while newRoomType in listOfRoomTypes:
        print("\nType de salle invalide - Deja définie")
        print("Attribuer le type de salle à la salle "+roomName+"? ")
        addToDict = input("y or n: ")
        while addToDict not in ["y","n"]:
            addToDict = input("y or n: ")
        if addToDict == "y":
            dictOfRoomTypes[newRoomType].add(roomName)
            return None
        if addToDict == "n":
            print("Les types de salle déjà définie sont:")
            for i in listOfRoomTypes:
                print("    "+i+"\n")
            newRoomType = input("Quel est le nom du type de salle pour la salle"+roomName+"? : ")
    dictOfRoomTypes[newRoomType] = set()
    dictOfRoomTypes[newRoomType].add(roomName)
    listOfRoomTypes.append(newRoomType)
    return None

def ask_for_options(listOfRoomTypes, dictOfRoomTypes, roomName):
    print(16*" "+roomName+"\n")
    print("Voici les types disponible pour la salle: ")
    for i in range(len(listOfRoomTypes)):
        print("    "+str(i)+" - "+listOfRoomTypes[i])
    print("\nPour attribuer la salle à un type, tapez le numéro correspondant")
    print("Ecrire 'new' pour créer un nouveau type de salle\n")

    while True:
        choice = input("Votre choix: ")
        if strToIntValid(choice)[0]:
            choice = strToIntValid(choice)[1]+1
            if choice in range(1,len(listOfRoomTypes)+1):
                dictOfRoomTypes[listOfRoomTypes[choice-1]].add(roomName)
                return None
        elif choice == "new":
            print("\n")
            create_room_type(listOfRoomTypes,dictOfRoomTypes,roomName)
            return None
        print("\nErreur - Reessayez\n")


def define_room_types(database_ENSMM):
    dictRoomTypes = {}
    listRoomTypes = ["Amphithéatre","Langue","Informatique","TP","TD","Autres","Ne sais pas"]
    for i in listRoomTypes:
        dictRoomTypes[i]=set()
    
    for i in database_ENSMM["rooms"]:
        clear_terminal()
        if len(listRoomTypes) == 0:
            print("Aucun type de salle défini dans la base")
            create_room_type(listRoomTypes,dictRoomTypes,i)
        else:
            ask_for_options(listRoomTypes,dictRoomTypes,i)
    clear_terminal()
    return dictRoomTypes, listRoomTypes

from enum import Enum, auto

"""
Liste de tous les types de contraintes actuellement identifiees et utilisees
IBS =
IBD =
IBHD =
GBHD =
"""
class ConstraintType(Enum):
    IBS_SUP = "IBS supérieur"
    IBS_INF = "IBS inférieur"
    IBD_INF = "IBD inférieur"
    IBD_EQ = "IBD égal"
    IBHD_INF = "IBHD_inférieur"
    IBHD_EQ = "IBHD_égal"
    IBHD_SUP = "IBHD_supérieur"
    GBHD_INF = "GBHD_inférieur"
    GBHD_SUP = "GBHD_supérieur"
    CONJONCTION = "Conjonction"
    SEUIL = "Seuil"
    SI_A_ALORS_NON_B = "Si a alors non b"
    PAS_PLUS_1_COURS_PAR_CRENEAU = "Pas plus d'un cours par créneau"
    COURS_DOIT_ETRE_PLACE = "Le cours doit êre placé"
    COURS_DOIT_AVOIR_PROFESSEUR = "Le cours doit avoir un professeur"
    PROFESSEUR_NE_PEUT_DONNER_2_COURS_EN_MEME_TEMPS = "Le professeur ne peut pas donner 2 cours en même temps"
    PAS_DE_PROFESSEUR_DISPONIBLE = "Pas de professeur disponible"
    SALLE_NE_PEUT_ACCEPTER_2_COURS_EN_MEME_TEMPS = "Une salle ne peut pas être disponible pour 2 cours à un même moment"
    UN_COURS_POUR_UN_TYPE_DE_SALLE = "Chaque cours doit être assigné à un type de salle"
    DISPO_SALLE = "La salle n'est pas disponible"
    SALLE_DISPO_AU_PLUS_1_FOIS = "Chaque salle ne peut être utilisée qu'une seule fois"
    SALLE_PREFEREE_NON_DISPONIBLE = "La salle préférée n'est pas disponible"
    DEPENDANCE = "Problème de dépendance"
    DEPENDANCE_SALLE = "Problème de dépendance entre les salles"
    DEPARTEMENT_BLOQUE_SLOT = "Les autres départements bloquent le slot"
    PROFESSEUR_A_DEJA_COURS_EN_AUTRE_DEPARTEMENT = "Le professeur a déjà un cours dans un autre département"
    PROFESSEUR_A_DEJA_COURS_EN_AUTRE_DEPARTEMENT_IBD = "Le professeur a déjà un cours dans un autre département IBD"

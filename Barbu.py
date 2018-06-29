##_________Rappels_Ia_Avancee__________##
#
#	Concept :
#			  L'idee est de generer une valeur pour une carte dans une
#			  donnee. Cette valeur est determinee en fonction de deux
#			  facteurs premiers : les points gagnes par les autres joueurs (Pa)
#			  et les points gagnes par le joueur lui meme (Pj) a la fin
#			  du pli dans lequel on a joue cette carte. Ces donnees sont stockees
#			  dans un fichier texte externe et interprete comme un dictionnaire
#			  au lancement du programme.
#  			  	La valeur est calculee comme suit :
#					- Pa/Pj
#
#			  On determine ainsi quelle carte jouer dans une situation.
#
#	Composition d'une clef :
#			  Une clef de situation se definit comme suit :
#					-Le code de la carte qu'on cherche a jouer (voir section Code de carte) -code carte-
#					-Est ce que la carte est jouee en premier (P) ou en suivant (S) -code de position-
#					-Le numero de la manche
#					-Si on veut les points gagnes par les autres (A) ou soi meme (J)
#					-Eventuellement le code de la premiere carte qui a ete jouee  -code premiere carte-
#
#			  Une clef est donc : -code carte- + P/S + manche + A/J (+ -code premiere carte-)
#
#			  Ainsi si on souhaite acceder au nombres de points gagnes par les autres joueurs (A)
#			  pour un As de coeur (id : 154) joue en suivant (S) lorsqu'un 7 de carreau (id : 7)
#			  a ete joue en premier lors de la deuxieme manche on consultera la valeur associee a
#			  la clef : 154S2A7
#
#			  Remarque : On a donc 10240 clefs differentes, reduites a 5659 apres elimination des situations impossibles
#						 (Situations qui apres 10 000 parties enregistrees en ia naive (8*5*10000 = 400 000 plis) n'avaient enregistre aucun point)
#
#	Notion de risque :
#			  Lors de l'instanciation d'un joueur, il lui est attribue un facteur de risque aleatoire [0,10]
#			  base sur ce facteur, le joueur s'il est une Ia avancee ignorera un pourcentage des points gagnes
#			  par les joueurs eux meme dans une situation et donnera donc plus d'importance aux points qu'il
#			  peut faire gagner aux autres. Ce pourcentage de risque (R) est compris entre 0% et 90%.
#
#					Ce qui donne une formule finale :
#
#						###################
#						#  Pa/(Pj*(1-R))  # (le champ risque de l'objet joueur correspond deja a 1-R)
#						###################
#
#	Code de Carte :
#
#		Carreau = 1		id = couleur*numero
#		Coeur = 11
#		Pique = 21
#		Trefle = 31
#
#		Avec ces valeurs les cartes ont un id unique.
#
#		Par exemple : Roi (13) de pique (21) = 13*21 = 273
#
#########################################

##______________Imports________________##
from random import shuffle, \
    randint  # shuffle pour melanger le paquet et randint pour selectionner un entier au (pseudo)hasard dans un intervalle [a,b]
import sys  # sys permet d'interagir avec le systeme, ici pour sys.exit() pour fermer le programme
import tkinter as tk

##_____________________________________##

##_____________Constantes______________##
NB_MANCHES = 5  # Nb de manches a jouer, si > 5 la manche 5 se joue en boucle
NB_JOUEURS = 4  # Pb si > 32
NUM_UTILISATEUR = 0  # Id du joueur humain, correspond au numero-1 /!\, si >= NB_JOUEURS alors partie seulement avec IAs
                     # Devrait pas changer pour le graphique
NB_IA_AVANCEE = 2
if NB_IA_AVANCEE != 0:
    IA_AVANCEE = True
else:
    IA_AVANCEE = False


##_____________________________________##

##_______________Classes_______________##
class Carte:
    """Objet carte a jouer"""

    def __init__(self, numero, couleur):
        """Constructeur de la classe Carte"""
        self.numero = numero  # Numero de la carte [7,14]
        self.couleur = couleur  # Couleur de la carte (Carreau,Coeur...)
        self.origine = None  # Joueur ayant joue la carte, nul par defaut
        self.id = self.generer_id(couleur,
                                  numero)  # Id unique pour chaque carte servant pour l'exploitation des donnees, voir rappels en haut
        self.nom = self.generer_nom(numero)  # Nom plus intelligible (7,8,..,Roi,As)
        self.ref = None
        self.num_slot = None
        self.item_graphique()

    def item_graphique(self):
        """Ajout de l'item correspondant à la carte"""
        if str(self.id) not in dict_items :
            dict_items[str(self.id)] = Item_grapique(card=str(self.id))
        #On passe par un dictionnaire en variable globale pour que le garbage collector ne supprime pas la référence à l'image

    @staticmethod
    def generer_nom(numero):
        """Fonction associant le nom intelligible d'une carte a son numero"""
        if numero <= 10:
            nom = str(numero)
        else:
            if numero == 11:
                nom = "Valet"
            elif numero == 12:
                nom = "Dame"
            elif numero == 13:
                nom = "Roi"
            else:
                nom = "As"
        return nom

    @staticmethod
    def generer_id(couleur, numero):
        """Fonction qui genere l'id d'une carte"""
        if couleur == "Carreau":
            num_couleur = 1
        elif couleur == "Coeur":
            num_couleur = 11
        elif couleur == "Pique":
            num_couleur = 21
        else:
            num_couleur = 31
        return str(numero * num_couleur)

    def __repr__(self):
        return str(self.nom ) + " de " + str(self.couleur)


class Paquet_de_cartes:
    """Objet paquet de 32 cartes a jouer melange"""

    def __init__(self):
        """Constructeur de la classe Paquet_de_carte"""
        self.paquet = []  # Un paquet est une liste de cartes
        self.generer_paquet()  # Que l'on genere

    def generer_paquet(self):
        """Fonction qui remplit le paquet de l'objet"""
        for i in range(7, 15):  # On genere d'abord le paquet bien trie
            self.paquet.append(Carte(i, "Carreau"))
            self.paquet.append(Carte(i, "Coeur"))
            self.paquet.append(Carte(i, "Pique"))
            self.paquet.append(Carte(i, "Trefle"))
        shuffle(self.paquet)  # Puis on le melange avec shuffle (importe du package random)

    def tirer(self):
        """Fonction permettant de tirer une carte se situant en fin de liste ("haut du paquet")"""
        if self.paquet:  # Si il y a des cartes dans le paquet
            return self.paquet.pop()


class Joueur:
    """Objet Joueur de barbu"""

    def __init__(self, id, risque, type):
        """Constructeur de la classe Joueur"""
        self.main = []  # La main du joueur, une liste de cartes
        self.id = id  # L'id du joueur, numero le representant
        self.points = 0  # Les points qu'il a accumule au cours de la partie
        self.risque = self.generer_facteur_risque(risque)  # pourcentage de risque pris si le joueur est une ia avancee
        self.type = type
        self.slot = None if self.type == "humain" else slots_ia[id-1]
        self.label_premier = None
        self.label_points = None

    @staticmethod
    def generer_facteur_risque(risque):
        """Fonction permettant de generer le pourcentage de risque d'une i.a. en fonction du risque renseigne a la creation du joueur"""
        if risque > 10 or risque < 0:  # Le risque devrait etre [0,10]
            risque = 0
        facteur = 1 - 0.09 * risque  # De 0% de risque pour risque=0 a 90% pour risque=10
        return facteur


class Item_grapique :

    def __init__(self, **kwargs):
        self.image = tk.PhotoImage(file="cartes/"+kwargs["card"]+".png")
        self.name = kwargs["card"]

class Slot_carte :

    def __init__(self, x, y, num):
        self.slot = C.create_image(x,y)
        self.x = x
        self.y = y
        self.num = num

    def update_slot(self, image):
        C.itemconfig(self.slot, state=tk.NORMAL)
        C.itemconfig(self.slot, image=image)

    def clear_slot(self):
        C.itemconfig(self.slot, state=tk.HIDDEN)

    def relocate_slot(self, x, y):
        C.coords(self.slot, x, y)

##________________________________________##

##_______________Fonctions________________##
def main():
    """Fonction principale du programme"""
    global Liste_joueurs

    Liste_joueurs = creer_liste_joueurs()  # On cree tous les joueurs sous forme d'une liste

    distribuer_cartes(Liste_joueurs)
    afficher_main_joueur()
    jouer()

def jouer():
    global joueur_courant, carte_choisie, nb_carte_jouee, Pli, premiere_carte

    if not Pli :
        Liste_joueurs[joueur_courant].label_premier.config(state=tk.NORMAL)

    if joueur_courant == NUM_UTILISATEUR:
        carte = carte_choisie
        if carte:
            cartes_jouables = determiner_cartes_jouables(Liste_joueurs[joueur_courant].main, Pli[0].couleur) if Pli else Liste_joueurs[joueur_courant].main
            print(cartes_jouables)
            if carte in cartes_jouables :
                del(Liste_joueurs[joueur_courant].main[Liste_joueurs[joueur_courant].main.index(carte)])
                nb_carte_jouee += 1
                joueur_courant = (joueur_courant+1)%4
            else :
                slot = liste_slot[carte.num_slot]
                slot.relocate_slot(slot.x,slot.y)
                carte = None
                carte_choisie = None
    else :
        carte = jouer_carte_ia(Liste_joueurs[joueur_courant], donnees)
        afficher_carte(carte,Liste_joueurs[joueur_courant].slot,dict_items[str(carte.id)])
        nb_carte_jouee += 1
        joueur_courant = (joueur_courant+1)%4

    if not Pli :
        premiere_carte = carte
    if carte :
        Pli.append(carte)

    if len(Pli) == 4 :
        joueur_courant = determiner_perdant_pli(Pli)
        Label_annonce.config(text='Joueur {x} perd !'.format(x=joueur_courant+1))

        Liste_joueurs[joueur_courant].points += determiner_points_pli()
        for joueur in Liste_joueurs :
            joueur.label_premier.config(state=tk.DISABLED)
            joueur.label_points.config(text='{x} Pts'.format(x=joueur.points))
        print(Pli)
        del Pli
        Pli = []
        premiere_carte = None
        fen.after(1000, fin_de_tour)
        return

    fen.after(100, jouer)

def fin_de_tour():
    global carte_choisie
    slot = liste_slot[carte_choisie.num_slot]
    slot.relocate_slot(slot.x, slot.y)
    carte_choisie = None
    liste_slot[len(Liste_joueurs[NUM_UTILISATEUR].main)].clear_slot()
    for slot in slots_ia:
        slot.clear_slot()
    afficher_main_joueur()
    if nb_carte_jouee%32 == 0:
        fen.after(500,manche_suivante)
    else :
        jouer()

def manche_suivante():
    global manche
    manche += 1

    distribuer_cartes(Liste_joueurs)

    afficher_main_joueur()

    if manche <= NB_MANCHES:
        jouer()
    else :
        fin()


def fin():
    C.delete(tk.ALL)
    tk.Label(fen,text ="Le joueur {x} a perdu !".format(x=determiner_perdant_partie()),font=('Impact',35),bg='#3F6123').place(x=500,y=400,anchor='center')

def ouvrir_fichier_donnees():
    """Fonction permetant d'ouvrir le fichier de donnees, avec gestion des erreurs"""
    try:  # On essaye d'executer ce bloc d'indentation
        with open("Ia_donnees.txt",
                  "r") as fichier:  # Cette syntaxe assure que le fichier est ferme quand on a fini de s'en servir
            donnees = eval(
                fichier.read())  # /!\On utilise eval (pas tres securise ni apprecie, mais plus court) pour interpreter le contenu du fichier
    except:  # Si le bloc de Try n'a pas pu s'executer
        sys.exit("Erreur lors de l'ouverture du fichier")  # On ferme le programme en renvoyant un message d'erreur
    return donnees  # On renvoie les donnees sous forme de dict


def creer_liste_joueurs():
    """Fonction qui cree la liste des joueurs"""
    Liste_joueurs = []
    n = NB_IA_AVANCEE
    for i in range(NB_JOUEURS):
        if i == NUM_UTILISATEUR:
            Liste_joueurs.append(Joueur(i, randint(0, 10), "humain"))
        elif n != 0:
            Liste_joueurs.append(Joueur(i, randint(0, 10), "avancee"))
            n -= 1
        else:
            Liste_joueurs.append(Joueur(i, randint(0, 10),
                                        "naive"))  # On instancie autant de joueurs que necessaire avec un facteur de risque (pseudo)aleatoire
    Liste_joueurs[0].label_premier = tk.Label(fen, text='Premier', bg='#3F6123',font=('Impact', 13), fg='#6D1616',disabledforeground='#3F6123')
    Liste_joueurs[0].label_premier.place(x=498,y=345,anchor='center')

    Liste_joueurs[0].label_points = tk.Label(fen,text='0 pts', bg='#3F6123',font=('Impact',20), fg='#6D1616')
    Liste_joueurs[0].label_points.place(x=498,y=750,anchor='center')

    Liste_joueurs[1].label_premier = tk.Label(fen, text='Premier', bg='#3F6123', font=('Impact', 13), fg='#6D1616',disabledforeground='#3F6123')
    Liste_joueurs[1].label_premier.place(x=260, y=190, anchor='center')

    Liste_joueurs[1].label_points = tk.Label(fen, text='0 pts', bg='#3F6123', font=('Impact', 13))
    Liste_joueurs[1].label_points.place(x=260, y=380, anchor='center')

    Liste_joueurs[2].label_premier = tk.Label(fen, text='Premier', bg='#3F6123', font=('Impact', 13), fg='#6D1616',disabledforeground='#3F6123')
    Liste_joueurs[2].label_premier.place(x=498, y=40, anchor='center')

    Liste_joueurs[2].label_points = tk.Label(fen, text='0 pts', bg='#3F6123', font=('Impact', 13))
    Liste_joueurs[2].label_points.place(x=498, y=230, anchor='center')

    Liste_joueurs[3].label_premier = tk.Label(fen, text='Premier', bg='#3F6123', font=('Impact', 13), fg='#6D1616',disabledforeground='#3F6123')
    Liste_joueurs[3].label_premier.place(x=740, y=190, anchor='center')

    Liste_joueurs[3].label_points = tk.Label(fen, text='0 pts', bg='#3F6123', font=('Impact', 13))
    Liste_joueurs[3].label_points.place(x=740, y=380, anchor='center')

    for joueur in Liste_joueurs :
        joueur.label_premier.config(state=tk.DISABLED)


    return Liste_joueurs


def distribuer_cartes(Liste_joueurs):
    """Fonction qui ajoute iterativement la derniere carte d'un paquet melange"""
    Paquet = Paquet_de_cartes()  # On instancie le paquet
    for i in range(
            32 // NB_JOUEURS):  # On distribue autant de cartes a chaque joueur, et on les distribue toutes (ou presque...)
        for joueur in Liste_joueurs:
            joueur.main.append(Paquet.tirer())
            joueur.main[-1].origine = joueur.id  # On fixe l'origine des cartes quand elles sont attribuees a un joueur
    if NUM_UTILISATEUR < len(Liste_joueurs):  # Si l'utilisateur prend part a la partie
        trier_main(Liste_joueurs[NUM_UTILISATEUR])  # Alors on trie sa main pour faciliter l'utilisation de l'interface


def trier_main(joueur):
    """Fonction qui regroupe les cartes par couleur"""
    indice_carreau = 0  # Adaptation de l'algorithme du drapeau hollandais de Dijkstra
    indice_coeur = 0
    indice_pique = 0
    for i in range(len(joueur.main)):
        if joueur.main[i].couleur == "Carreau":
            joueur.main.insert(indice_carreau, joueur.main.pop(i))  # Permet d'intervertir deux cartes dans la liste
            indice_carreau += 1
            indice_coeur += 1
            indice_pique += 1
        elif joueur.main[i].couleur == "Coeur":
            joueur.main.insert(indice_coeur, joueur.main.pop(i))
            indice_coeur += 1
            indice_pique += 1
        elif joueur.main[i].couleur == "Pique":
            joueur.main.insert(indice_pique, joueur.main.pop(i))
            indice_pique += 1


def jouer_carte_ia(joueur, donnees):  # Les = definissent la valeur par defaut d'un parametre (si il n'est pas passe par l'appelant)
    """Fonction qui renvoie une carte choisie par une IA"""
    if(len(Pli)==0):
        premiere_carte = None
        couleur_imposee = ""
    else :
        premiere_carte = Pli[0]
        couleur_imposee = premiere_carte.couleur
    if joueur.type == "avancee":
        carte_jouee = ia_avancee(joueur, manche, donnees, premiere_carte, couleur_imposee)
    else:
        carte_jouee = ia_naive(joueur, couleur_imposee)

    return carte_jouee


def ia_naive(joueur, couleur_imposee):
    """Fonction qui choisit la premiere carte que le joueur peut jouer"""
    if not couleur_imposee:  # Si il n'y a pas de couleur imposee
        carte_jouee = joueur.main.pop()  # La premiere carte de la main (en la supprimant)
    else:
        a_couleur = joueur_a_couleur(joueur, couleur_imposee)  # On verifie si le joueur a la couleur imposee en main
        if a_couleur:  # Si il l'a
            i = 0
            while joueur.main[
                i].couleur != couleur_imposee:  # On parcourt la main jusqu'a en trouver une de la bonne couleur
                i += 1
            carte_jouee = joueur.main.pop(i)
        else:
            carte_jouee = joueur.main.pop()  # Sinon on joue la premiere venue
    return carte_jouee


def ia_avancee(joueur, manche, donnees, premiere_carte, couleur_imposee):
    """Fonction qui va choisir une carte en fonction du risque du joueur et de donnees recoltees lors de parties precedentes"""
    cartes_jouables = determiner_cartes_jouables(joueur.main,
                                                 couleur_imposee)  # On a d'abord besoin de savoir quelles cartes le joueur peut jouer
    Valeurs_cartes = determiner_valeur_cartes(joueur, cartes_jouables, manche, premiere_carte,
                                              donnees)  # Ensuite on determine la valeur des cartes dans une situation donnee (voir rappels), en prenant en compte le facteur de risque
    index_carte = Valeurs_cartes.index(max(
        Valeurs_cartes))  # On trouve l'index de la meilleure valeur, correspondant a celui de la meilleure carte /!\ dans les cartes jouables /!\
    carte_choisie = cartes_jouables[index_carte]  # On recupere cette carte dans les cartes jouables
    carte_jouee = joueur.main.pop(
        joueur.main.index(carte_choisie))  # Et on trouve sa position dans la main du joueur pour l'en retirer
    return carte_jouee  # Et on renvoie la carte


def determiner_cartes_jouables(main, couleur_imposee):
    """Fonction qui determine la liste des cartes jouables dans une main, fonction d'une couleur imposee"""
    if not couleur_imposee:  # Si il n'y a pas de couleur imposee on peut jouer toute sa main
        return main
    else:  # Si il y a une couleur imposee on cherche toutes les cartes de cette couleur
        cartes_jouables = []
        for carte in main:
            if carte.couleur == couleur_imposee:
                cartes_jouables.append(carte)
    if not cartes_jouables:  # Si on en a trouve aucune c'est qu'on peut jouer n'importe quelle carte
        return main
    return cartes_jouables  # Sinon on renvoie celles qu'on a trouve


def determiner_valeur_cartes(joueur, cartes_jouables, manche, premiere_carte, donnees):  # Voir les rappels /!\
    """Fonction donnant la valeur de cartes en prenant en compte le risque d'un joueur, une situation particuliere et des donnees recoltees"""
    if manche > 5:  # Au cas ou on joue plus de 5 manches
        manche = 5
    valeur_cartes_avec_risque = []  # On cree la liste des valeurs
    code_position = "P" if not premiere_carte else "S"  # On determine le code position /!\ (Var = a if c else b)(Python) <=> (Var = c ? a : b)(C,C#...) /!\
    code_premiere_carte = "" if not premiere_carte else premiere_carte.id  # On determine le code de la premiere carte, pas de code si on joue en premier
    for carte in cartes_jouables:  # Pour toutes les cartes passees a la fonction
        code_joueur = carte.id + code_position + str(
            manche) + "J" + code_premiere_carte  # On genere le code permettant d'acceder aux points gagnes par le joueur de cette carte
        code_autres = carte.id + code_position + str(
            manche) + "A" + code_premiere_carte  # Et celui pour les points gagnes par les autres joueurs
        points_joueur = donnees[
                            code_joueur] * joueur.risque if code_joueur in donnees else 1  # Comme pour la ligne suivante, sauf qu'on ignore une partie de ces points en fonction du pourcentage de risque associe au joueur ([0%..90%])
        points_autres = donnees[
            code_autres] if code_autres in donnees else 1  # On recupere les points (comme on a supprime les valeur nulle pour gagner de la place, on assigne 1 si la situation n'est pas enregistree dans les donnees)
        valeur_cartes_avec_risque.append(
            points_autres / points_joueur)  # Et on determine la valeur d'une carte qu'on ajoute a la liste
    return valeur_cartes_avec_risque  # On revoie la liste


def trouver_carte_reference(liste_cartes,ref):
    """Fonction qui cherche une carte parmi une liste en utilisant sa reference sur le canvas"""
    for carte in liste_cartes :
        if carte.ref == ref:
            return carte
    return None


def jouer_carte_utilisateur():
    """Fonction qui gere l'interraction utilisateur pour jouer une carte"""

    return carte_choisie  # On renvoie la carte finalement selectionnee et conforme aux regles

def joueur_a_couleur(joueur, couleur):
    """Fonction qui permet de determiner la presence d'une couleur dans la main d'un joueur"""
    for carte in joueur.main:
        if carte.couleur == couleur:  # Si on trouve une carte de la bonne couleur on renvoie vrai
            return True
    return False  # Sinon on renvoie faux


def determiner_perdant_pli(Pli):
    """Fonction qui permet de trouver l'id du joueur ayant perdu le pli"""
    carte_perdante = Pli[0]  # On commence par prendre la premiere carte du pli
    for carte in Pli[1:]:  # On parcourt le reste du pli
        if carte.numero > carte_perdante.numero and carte.couleur == carte_perdante.couleur:  # Si le numero de la carte est plus eleve, et de la meme couleur que la carte determine comme perdante avant
            carte_perdante = carte
    return carte_perdante.origine  # Et on se sert de l'origine d'une carte pour retrouver le joueur l'ayant joue


def determiner_points_pli():
    """Fonction qui determine la valeur d'un pli en fonction de la manche"""
    points = 0  # On initialise les points
    if manche == 1:  # En premiere manche, chaque coeur dans le pli vaut 4 points
        for carte in Pli:
            if carte.couleur == "Coeur":
                points += 4
    elif manche == 2:  # En deuxieme manche, chaque pli vaut 4 points
        points = 4
    elif manche == 3:  # En troisieme manche, chaque dame dans le pli vaut 10 points
        for carte in Pli:
            if carte.nom == "Dame":
                points += 10
    elif manche == 4:  # En quatrieme manche, le roi de coeur (le barbu) vaut 40 points
        for carte in Pli:
            if carte.nom == "Roi" and carte.couleur == "Coeur":
                points += 40
    else:  # En cinquieme manche (et toutes les manches suivantes), tous les contrats precedent sont valables
        for carte in Pli:
            if carte.nom == "Roi" and carte.couleur == "Coeur":
                points += 40
            if carte.nom == "Dame":
                points += 10
            if carte.couleur == "Coeur":
                points += 4
        points += 4
    return points


def determiner_perdant_partie():
    """Fonction qui determine le joueur avec le plus de points de la partie"""
    perdant = Liste_joueurs[0]
    for joueur in Liste_joueurs[1:]:  # Meme principe que le perdant d'un pli
        if joueur.points > perdant.points:
            perdant = joueur
    return perdant.id  # On renvoie l'id d'un joueur


##_____________________________________________##

def afficher_carte(carte, slot, item):
    slot.update_slot(item.image)
    carte.ref = slot.slot
    carte.num_slot = slot.num


def afficher_main_joueur():
    if not Liste_joueurs[NUM_UTILISATEUR] :
        print("main inexistante")
        return
    for i in range(len(Liste_joueurs[NUM_UTILISATEUR].main)):
        afficher_carte(Liste_joueurs[NUM_UTILISATEUR].main[i], liste_slot[i], dict_items[str(Liste_joueurs[NUM_UTILISATEUR].main[i].id)])


def selec_carte(evt):
    global carte_selectionnee
    ref = C.find_overlapping(evt.x, evt.y, evt.x, evt.y)
    if ref:
        carte_selectionnee = trouver_carte_reference(Liste_joueurs[NUM_UTILISATEUR].main, ref[0])


def bouger_carte(evt):
    if (carte_selectionnee):
        C.coords(carte_selectionnee.ref, evt.x, evt.y)


def deselec_carte(evt):
    global carte_selectionnee, carte_choisie
    if(carte_selectionnee):
        if (evt.x>460 and evt.x<540) and (evt.y>355 and evt.y<500):
            C.coords(carte_selectionnee.ref, 500, 437)
            carte_choisie = carte_selectionnee
        else:
            C.coords(carte_selectionnee.ref, liste_slot[carte_selectionnee.num_slot].x,liste_slot[carte_selectionnee.num_slot].y)
    carte_selectionnee = None


fen = tk.Tk()
fen.geometry("1000x800")
fen.title("Barbu")
C = tk.Canvas(fen, width=1001, height=801, bg="#3F6123")
C.place(x=-2, y=-2)

Liste_joueurs = []
liste_slot = []
Pli = []
slots_ia = []
dict_items = {}
joueur_courant = randint(0,3)
nb_carte_jouee = 0
manche = 1

if IA_AVANCEE:  # Si on joue contre des ia avancees
    donnees = ouvrir_fichier_donnees()  # On recupere les donnees dans le fichier joint

for i in range(8):
    liste_slot.append(Slot_carte(125 + (108 * i), 605, i))



carte_selectionnee = None
carte_choisie = None
premiere_carte = None

C.create_rectangle(449, 364, 551, 511, outline='#6D1616', width=2)


C.create_rectangle(214, 211, 316, 358, outline='grey', width=2)
tk.Label(fen,text='2',font=('Impact',35),bg='#3F6123').place(x=265,y=284,anchor='center')
slots_ia.append(Slot_carte(265, 284, 8))


C.create_rectangle(449, 64, 551, 211, outline='grey', width=2)
tk.Label(fen,text='3',font=('Impact',35),bg='#3F6123').place(x=500,y=137,anchor='center')
slots_ia.append(Slot_carte(500, 137, 9))


C.create_rectangle(690, 211, 792, 358, outline='grey', width=2)
tk.Label(fen,text='4',font=('Impact',35),bg='#3F6123').place(x=741,y=284,anchor='center')
slots_ia.append(Slot_carte(741, 284, 10))

Label_annonce = tk.Label(fen, text='', bg='#3F6123', font=('Impact',20))
Label_annonce.place(x=500,y=285,anchor='center')

main()


C.bind("<Button-1>", selec_carte)
C.bind("<B1-Motion>", bouger_carte)
C.bind("<ButtonRelease-1>", deselec_carte)

fen.mainloop()

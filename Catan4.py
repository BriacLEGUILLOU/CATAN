#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 18:35:48 2020

@author: leguilloubriac
"""
from math import sqrt, atan
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
import numpy as np

import pandas as pd
import string
from scipy.spatial import distance
from matplotlib import collections  as mc
import random
from random import randint

################################
# Class
################################

class Couleur:
	RED = 'red'
	BLUE = 'blue'
	YELLOW = 'yellow'
	BLACK = 'black'
	PURPLE = 'purple'
	GREEN = 'green'
    

class Player:
    current_player = None
    player_with_most_roads = None
    player_with_most_knights = None
    player_list = []
    id = 0
    colors = {0:'red', 1:'blue', 2:'green', 3:'purple'}
    position_chevalier = 'None'
    def __init__(self):
        self.id = Player.id
        Player.id += 1
        self.color = Player.colors[self.id]
        self.points = 0
        self.wheat = 2
        self.sheep = 2
        self.stone = 0
        self.clay = 4
        self.wood = 4
        self.knights_played = 0
        self.roads = 0
        self.cards = []
        self.can = []
        Player.player_list.append(self)
        # Liste des ports
        self.list_port = []
        self.route_constructible = []

    def check_if_winner(self):
        if self.points >= 10:
            print ('Player', self.id, 'Won')
    

    def get_can(self):
        """ Renvoie la liste des actions possibles par le joueur """
        player_can = []
        if self.clay >= 1 and self.wheat >= 1 and self.sheep >= 1 and self.wood >= 1:
            player_can.append('colonie')
        if self.clay >= 1 and self.wood >= 1:
            player_can.append('route')
        if self.stone >= 3 and self.wheat >= 2:
            player_can.append('ville')
        if self.stone >= 1 and self.wheat >= 1 and self.sheep >= 1:
            player_can.append('achat_carte_développement')
        if self.wood>0 or self.clay>0 or self.sheep>0 or self.wheat>0 or self.stone>0:
            player_can.append('échange_joueur')
        if self.wood>3 or self.clay>3 or self.sheep>3 or self.wheat>3 or self.stone>3:
            player_can.append('échange_banque_4:1')
        if '3:1' in self.list_port:
            if self.wood>2 or self.clay>2 or self.sheep>2 or self.wheat>2 or self.stone>2:
                player_can.append('échange_banque_3:1')
        if len([x for x in self.cards if x != 'vp']) > 0:
            player_can.append('jouer_carte_développement')
        self.can = player_can
    



class Game:
    """ représente les ressources et les cartes en banque """
    
    def __init__(self):
        self.wheat = 20
        self.sheep = 20
        self.stone = 20
        self.clay = 20
        self.wood = 20
        self.knight = 15
        self.dev_build2roads = 2
        self.dev_monopole = 2
        self.dev_2ressource = 2
        self.dev_victory_point = 5


################################
# Fonction
################################


def lancer_des():
    # On lance les dés
    dice =  str(int(randint(1,6) + randint(1,6)))
    print('dice: ', dice)
    # On note les hexagones avec ce numéro
    hexagones = df_hex.loc[df_hex['numéro']==dice,['hex','terrain']]
    
    #Pour chaque terrain, on va identifier les villes
    for index, row in hexagones.iterrows():
        ressource = row['terrain']
        sommets = df_hex.loc[df_hex['hex']==row.hex,['s1','s2','s3','s4','s5','s6']]
        sommets = list(sommets.iloc[0,:])
        # On vient d'identifier les sommets allant gagant gagner la ressource
        
        # On identifie les noeuds ayant une colonie ou une ville
        nodes_constructed = nodes.loc[nodes['construction'] != 'None','sommet']
        # On applique la fonction permettant aux joueurs de gagner cette ressource
        for i in sommets:
            if i in nodes_constructed.values:
                construction = nodes.loc[i, 'construction']
                # On attribue les ressources selon colonie ou ville
                if construction == 'ville':
                    modif_ressource(player_id=Player.current_player, carte=ressource, nombre=2)
                elif construction == 'colonie':
                    modif_ressource(player_id=Player.current_player, carte=ressource, nombre=1)
                else:
                    print('erreur lancé de dés')
    return(int(dice))


def modif_ressource(player_id, carte, nombre):
    """ Cette fonction permet de faire gagner une ressource à un joueur"""
    if nombre != 0:
        Player.player_list[player_id]
        if carte == 'wood':
            Player.player_list[player_id].wood += nombre
        elif carte == 'clay':
            Player.player_list[player_id].clay += nombre
        elif carte == 'wheat':
            Player.player_list[player_id].wheat += nombre
        elif carte == 'sheep':
            Player.player_list[player_id].sheep += nombre
        elif carte == 'stone':
            Player.player_list[player_id].stone += nombre
        elif carte == 'knights':
            Player.player_list[player_id].knights += nombre
        else:
            print('erreur modif_ressource')
        print('modif_ressource joueur{}: {} {}'.format(player_id,nombre,carte))

def get_ressource(player_id):
    """ Cette fonction permet d'afficher les ressources du joueur """
    df = pd.DataFrame(index=['wood','clay','sheep','wheat','stone'],columns=['joueur'+str(player_id)])
    df.loc['wood'] = Player.player_list[player_id].wood
    df.loc['clay'] = Player.player_list[player_id].clay
    df.loc['sheep'] = Player.player_list[player_id].sheep
    df.loc['wheat'] = Player.player_list[player_id].wheat
    df.loc['stone'] = Player.player_list[player_id].stone
    
    return df



def route_constructible(player_id):
    """ renvoie les routes construtibles par le joueur """
    player_color = Player.colors[player_id] #couleur du joueur
    liste_sommet = list(df_route.loc[df_route['couleur']==player_color,'sommet1']) #liste des sommets accessibles par le joueur
    routes_sommets  = df_route[df_route['sommet1'].isin(liste_sommet)] #routes à proximité des sommets
    liste_route_constructible = routes_sommets.loc[routes_sommets['couleur']=='grey',['sommet1','sommet2']]
    
    return liste_route_constructible



def colonie_constructible(player_id):
    """ renvoie les colonies constructibles par le joueur """
    player_color = Player.colors[player_id] #couleur du joueur
    liste_sommet_accessible = list(df_route.loc[df_route['couleur']==player_color,'sommet1']) #liste des sommets accessibles par le joueur
    # Il faut maintenant sélectionner les sommets construtibles
    sommet_constructible = nodes.loc[:,'joueur'] == 'None'  # Sélection des sommets constructibles sur le plateau
    sommet_accessible = nodes.loc[:,'sommet'].isin(liste_sommet_accessible) # Sélection des sommets accessibles par le joueur
    liste_colonie_constructible = list(nodes.loc[(sommet_constructible) & (sommet_accessible),'sommet'])
    
    return liste_colonie_constructible

def ville_constructible(player_id):
    """ renvoie les colonies améliorable en ville """
    ville_constructible = nodes.loc[(nodes['joueur']==player_id) & (nodes['construction']=='colonie'), 'sommet']
    
    return list(ville_constructible)


def construction_route(player_id, sommet1, sommet2):
    player_color = Player.colors[player_id] #couleur du joueur
    df_route.loc[(df_route['sommet1'] == sommet1) & (df_route['sommet2'] == sommet2),['couleur', 'linewidths']] = player_color,4
    df_route.loc[(df_route['sommet2'] == sommet1) & (df_route['sommet1'] == sommet2),['couleur', 'linewidths']] = player_color,4
    # Mise à jour des caractéristiques du joueur
    modif_ressource(player_id, carte='wood', nombre=-1)
    modif_ressource(player_id, carte='clay', nombre=-1)
    print_map()
    print('Création de la route [{},{}] au joueur numéro {}.'.format(sommet1,sommet2,player_id))


def construction_colonie(player_id, sommet):
    """ Construit une colonie au joueur et au sommet sélectionné """
    player_color = Player.colors[player_id] #couleur du joueur
    nodes.loc[sommet,['joueur', 'Couleur', 'construction']] = player_id, player_color, 'colonie'
    # Mise à jour des caractéristiques du joueur
    for carte in ['wood','clay','sheep','wheat']:
        modif_ressource(player_id, carte, nombre=-1)
    Player.player_list[player_id].points +=1
    # Il faut rendre les sommets adjacents impossible à construire
    #sommets adjacents au sommet ou l'on construit la colonie
    sommets_adajacents = nodes.loc[nodes['sommet']==sommet,['lien_s1','lien_s2', 'lien_s3']]
    sommets_adajacents = [x for x in sommets_adajacents.iloc[0] if int(x) >= 0] 
    nodes.loc[nodes.loc[:,'sommet'].isin(sommets_adajacents),'joueur'] = 'impossible'
    # Si le sommet possède un port, alors il faut le renseigner
    if nodes.loc[sommet,'port'] != 'None':
        Player.player_list[player_id].list_port.append(nodes.loc[sommet,'port'])
    print_map()
    print('Création de la colonie {} au joueur numéro {}.'.format(sommet,player_id))
    


def construction_ville(player_id, sommet):
    player_color = Player.colors[player_id] #couleur du joueur
    nodes.loc[sommet,['joueur', 'Couleur', 'construction']] = player_id, player_color, 'ville'
    # Mise à jour des caractéristiques du joueur
    modif_ressource(player_id, carte='wheat', nombre=-2)
    modif_ressource(player_id, carte='stone', nombre=-3)
    Player.player_list[player_id].points +=1
    print_map()
    print('Création de la ville {} au joueur numéro {}.'.format(sommet,player_id))


def dev_chevalier(player_id):
    """ Carte de développement chevalier
    - Déplacement du chevalier sur le terrain, afin de bloquer les ressources
    - Vol de l'un des joueurs adjacents
    - on augmente le nombre de chevalier joué pour le joueur (point)
    """
    roll_seven(player_id)
    Player.player_list[player_id].knights_played += 1


def deplacement_chevalier(player_id):
    """ Déplacement du chevalier en cas en carte développement ou d'un
    lancer de dés égal à 7
    - Déplacement du chevalier sur le terrain, afin de bloquer les ressources
    - Vol de l'un des joueurs adjacents """
    
    # Le chevalier ne peut pas être repositionné sur une position déjà prise
    decision = 'n'
    position_possible = df_hex.loc[df_hex.loc[:,'chevalier']!='chevalier','hex']
    while decision != 'y':
        print_map()
        a = input('Position du chevalier (exemple 21,31)\n Veuillez entrer 2 sommets diamétralement opposés et séparés par une virgule \n sur lhexagon choisit: \n')
        b,c = a.split(',')
        # on cherche l'hexagone avec les 2 sommets
        position_hex = df_hex.loc[df_hex.loc[:,['s1','s2','s3','s4','s5','s6']].isin([b,c]).sum(axis=1) == 2,['hex','numéro','couleur']]
        print('La position retenue a le numéro {} et la couleur {}'.format(position_hex.numéro.values[0],position_hex.couleur.values[0]))
        decision = input('Confirmer ? (y/n)\n')
    # On met à jour df_hex et nodes
    df_hex['chevalier'] = 'None'
    df_hex.loc[position_hex.hex.values[0],['chevalier']] = 'chevalier'
    sommets = df_hex.loc[position_hex.index,['s1','s2','s3','s4','s5','s6']]
    sommets = [int(x) for x in list(sommets.iloc[0,:])]
    nodes['chevalier'] = 'None'
    nodes.loc[sommets,'chevalier']='chevalier'
    # player_id peut voler l'un des joueurs adjacents
    joueur = nodes.loc[sommet,'joueur']
    print('joueur à voler {}'.format(joueur))


def roll_seven(player_id):
    """ En cas de 7 aux dés, tous les joueurs avec 8 cartes ou plus
    doivent se défausser la moitié de leur main.
    Le joueur ayant fait peut déplacer le chevalier """
    # Défausse des cartes
    for player in Player.player_list:
        player_id = player.id
        # on compte le nombre de cartes par joueur
        nombre_carte = player.wood + player.clay + player.sheep + player.wheat + player.stone
        if nombre_carte > 7:
            nombre_carte_à_défausser = nombre_carte//2
            print('Le joueur {} doit se défausser de {} cartes.'.format(player_id,nombre_carte_à_défausser))
            print(get_ressource(player_id).transpose())
            liste_carte_à_défausser = obtention_liste_carte(player_id=player_id,
                                                            texte='Défausse joueur',
                                                            exemple='0,-2,0,-2,0',
                                                            min_=-nombre_carte_à_défausser,
                                                            max_=0,
                                                            sum_=-nombre_carte_à_défausser,
                                                            len_=5)
            # une fois que le joueur a correctement sélectionné les cartes
            # On défausse les cartes du joueurs
            liste_ressource = ['wood','clay','sheep','wheat','stone']
            for i, nombre in enumerate(liste_carte_à_défausser):
                modif_ressource(player_id=player_id, carte=liste_ressource[i], nombre=nombre)
    # Déplacement du chevalier
    deplacement_chevalier(player_id)





def achat_carte_developpement(player_id):
    """ Permet au joueur d'acheter une carte développement """
    
    if len(liste_carte_dev) > 0:
        carte=liste_carte_dev.pop()
        Player.player_list[player_id].cards.append(carte)
        print('Le joueur {} a obtenu la carte {}.'.format(player_id,carte))
        if carte == 'vp':
            Player.player_list[player_id].points += 1



def dev_build2roads(player_id):
    """ Utilise la carte de développement
    construction de 2 routes """
    modif_ressource(player_id=player_id, carte='wood', nombre=2)
    modif_ressource(player_id=player_id, carte='clay', nombre=2)
    print(df_action.loc[df_action.loc[:,'action']=='route',['action','sommet1','sommet2']])




def dev_monopole(player_id):
    """ Utilise la carte monopole, afin de récupérer toutes les ressources 
    des joueurs """
    liste_carte=obtention_liste_carte(player_id=player_id,
                                        texte='Monopole joueur',
                                        exemple='1,0,0,0,0',
                                        min_=0,max_=1,sum_=1,len_=5)
    # le joueur va récupérer toutes les cartes en jeu
    nombre_ressource = 0
    carte=liste_ressource[np.argmax(liste_carte)]
    for player in Player.player_list :
        df_ressource = get_ressource(player.id)
        nombre_ressource += df_ressource.loc[carte,'joueur'+str(player.id)]
        modif_ressource(player_id=player.id, carte=carte, nombre=-df_ressource.loc[carte,'joueur'+str(player.id)])
    modif_ressource(player_id=player_id, carte=carte, nombre=nombre_ressource)



def dev_2ressource(player_id):
    """ le joueur joue la carte développement 2 ressources 
    Il peut piocher 2 ressources dans la banque """
    liste_carte=obtention_liste_carte(player_id=player_id,
                                      texte='Gain de 2 ressources joueur',
                                      exemple='1,1,0,0,0',
                                      min_=0,max_=2,sum_=2,len_=5)
        
    # une fois que le joueur a correctement sélectionné les cartes
    liste_ressource = ['wood','clay','sheep','wheat','stone']
    for i, nombre in enumerate(liste_carte):
        modif_ressource(player_id=player_id, carte=liste_ressource[i], nombre=nombre)



def obtention_liste_carte(player_id,texte,exemple,min_,max_,sum_,len_):
    """ Permet de demander à un joueur une liste de carte à sélectionner """
    decision = 'n' # Permet de corriger les éventuelles erreurs de saisie du joueur
    while decision != 'y':
        liste_carte = input('{} joueur{} (exemple {})\nCondition: min={}, max={}, sum={}, len={}\nVeuillez sélectionner {} ressources:\n'.format(texte, player_id,exemple,min_,max_,sum_,5,sum_))
        if isinstance(liste_carte,str):
            liste_carte = [int(x) for x in liste_carte.split(',')]
        
            # On vérifie que les données rentrées sont bonnes
            if (min(liste_carte) >=min_ and sum(liste_carte)==sum_ and
                len(liste_carte) == len_ and type(liste_carte) == list and
                max(liste_carte) <= max_):
                    # une fois que le joueur a correctement sélectionné les cartes
                    decision ='y'
                    return liste_carte
            else:
                print('Erreur dans la saisie des cartes, veuillez réessayer')


def proposer_echange_joueur(player_id=Player.current_player,liste_carte=[0,0,0,0,0]):
    """ Permet de proposer un échange sous la forme
    ['wood','clay','sheep','wheat','stone']
    Par exemple, si le joueur souhaite donner 1 bois et 
    recevoir 1 argile à un autre joueur : [-1,1,0,0,0]
    """
    
    # échange de carte
    if isinstance(liste_carte,list) and len(liste_carte) == 5:
        input_1 = int(input('player_id pour échange ? \n'))
        for i, carte in enumerate(['wood','clay','sheep','wheat','stone']):
            modif_ressource(player_id, carte, liste_carte[i])
            modif_ressource(int(input_1), carte, -liste_carte[i])
        


liste_carte=[-2,0,0,0,1]
def echange_banque(player_id=Player.current_player,liste_carte=[0,0,0,0,0]):
    """ Permet d'échanger ses cartes avec la banque 
    ['wood','clay','sheep','wheat','stone']
    Par exemple, si le joueur souhaite donner 4 bois et 
    recevoir 1 argile à la banque : [-4,1,0,0,0] """
    # échange de carte
    if (isinstance(liste_carte,list) and len(liste_carte) == 5):
        # échange 4:1
        if (min(liste_carte) == -4 and max(liste_carte) == 1 and sum(liste_carte) == -3):
            for i, carte in enumerate(['wood','clay','sheep','wheat','stone']):
                modif_ressource(player_id, carte, liste_carte[i])

        # échange 2.1 dans le cas d'un port 2:1
        elif len(Player.player_list[player_id].list_port) > 0:
            if '3:1' in Player.player_list[player_id].list_port:
                        # échange 3.1 dans le cas d'un port 3:1
                if (min(liste_carte) == -3 and Player.player_list[player_id].port3_1 and
                    max(liste_carte) == 1 and sum(liste_carte) == -2):
                    for i, carte in enumerate(['wood','clay','sheep','wheat','stone']):
                        modif_ressource(player_id, carte, liste_carte[i])
                        
            # On vérifie que le joueur souhaite utiliser le bon dont il dispose
            elif ['wood','clay','sheep','wheat','stone'][np.argmin(liste_carte)] in Player.player_list[player_id].list_port :
                print('Utilisation du port {}'.format( ['wood','clay','sheep','wheat','stone'][np.argmin(liste_carte)]))
                # On vérifie que liste_carte ne contient que 2 échanges:
                if (max(liste_carte) == 1 and min(liste_carte) == -2 and sum(liste_carte) ==-1):
                    for i, carte in enumerate(['wood','clay','sheep','wheat','stone']):
                        modif_ressource(player_id, carte, liste_carte[i])
            else:
                print('échante incorrect')
        else :
            print('échange incorrect')
        
def get_action(player_id):
    """ Permet d'obtenir la liste des actions possible par un joueur """
    
    Player.player_list[player_id].get_can()
    df_action = pd.DataFrame(columns=['action', 'sommet1', 'sommet2', 'echange', 'exec'])
    df_action.loc[0,['action','exec']] = 'fin du tour','fin du tour'
    df_action.loc[1,['action','exec']] = ['print_ressource','print(get_ressource({}))'.format(player_id)]

    # Construction d'une colonie
    if 'colonie' in Player.player_list[player_id].can:
        debut=len(df_action)
        for j, sommet in enumerate(colonie_constructible(player_id)):
            df_action.loc[debut+j,['action','sommet1','exec']] = 'colonie', sommet, \
            'construction_colonie(player_id={}, sommet={})'.format(player_id,sommet)
    
    # Construction d'une route
    if 'route' in Player.player_list[player_id].can:
        debut=len(df_action)
        for j, sommet in enumerate(route_constructible(player_id)):
            df_action.loc[debut+j,['action','sommet1','sommet2','exec']] = \
            'route', sommet1, sommet2, \
            'construction_route(player_id={}, sommet1={}, sommet2={})'.format(player_id,sommet1,sommet2)
    
    # Construction d'une ville
    if 'ville' in Player.player_list[player_id].can:
        debut=len(df_action)
        for j, sommet in enumerate(ville_constructible(player_id)):
            df_action.loc[debut+j,['action','sommet1','exec']] = \
            'ville', sommet, \
            'construction_ville(player_id={}, sommet={})'.format(player_id,sommet)
    
    # Achat d'une carte de développement
    if 'achat_carte_développement' in Player.player_list[player_id].can:
        # le joueur ne peut jouer qu'une seule carte de développement par tour
        debut=len(df_action)
        df_action.loc[debut,['action','exec']] ='achat_carte_développement', \
        'achat_carte_developpement(player_id={})'.format(player_id)
    
    # On joue une carte développement
    if 'jouer_carte_développement' in Player.player_list[player_id].can:
        if 'knight' in Player.player_list[player_id].cards:
            debut=len(df_action)
            df_action.loc[debut,['action','exec']] = 'knight', \
            'deplacement_chevalier(player_id={})'.format(player_id)
        if 'dev_2ressource' in Player.player_list[player_id].cards:
            debut=len(df_action)
            df_action.loc[debut,['action','exec']] = 'dev_2ressource', \
            'dev_2ressource(player_id={})'.format(player_id)
        if 'dev_monopole' in Player.player_list[player_id].cards:
            debut=len(df_action)
            df_action.loc[debut,['action','exec']] = 'dev_monopole', \
            'dev_monopole(player_id={})'.format(player_id)
        if 'dev_build2roads' in Player.player_list[player_id].cards:
            debut=len(df_action)
            df_action.loc[debut,['action','exec']] = 'dev_build2roads', \
            'dev_build2roads(player_id={})'.format(player_id)
            
    return df_action


liste_ressource = ['wood','clay','sheep','wheat','stone']
##########################################
# Création des hexagones avec df_hex
##########################################
# Coordonées des hexagones
s = 1 # size
w = 1/4 *s # width
h = sqrt(3)/2*s  # height

df_hex = pd.DataFrame()
df_hex['x'] = 3*[-12*w] + 4*[-6*w] + 5*[0] + 4*[6*w] + 3*[12*w]
df_hex['y'] = [2*h,0,-2*h] + [3*h,h,-h,-3*h] + [4*h,2*h,0,-2*h,-4*h] + \
                [3*h,h,-h,-3*h,2*h,0,-2*h]
df_hex['y'] = df_hex['y'].round(2)

# Création des couleurs pour les hexagones
df_hex['hex'] = [elt for elt in string.ascii_uppercase[:len(df_hex)]]
#df_hex['hex'] = ['hex' + str(i) for i in range(len(df_hex))]
# Le terrain est composé de 4 forêts, 4 prés, 4 champs, 3 colline, 3 montage, 1 désert
dict_couleur_terrain ={'wood':'green',
                       'clay':'red',
                       'sheep':'white',
                       'wheat':'yellow',
                       'stone':'blue',
                       'Désert':'grey'}
list_terrain = 4*['wood'] + 4*['wheat'] + 4*['sheep'] + 3*['clay'] + 3*['stone'] + ['Désert']
random.shuffle(list_terrain)
df_hex['terrain']=list_terrain
df_hex['couleur'] = df_hex['terrain'].map(dict_couleur_terrain)

# Ajout des numéros
list_num = [2,12] + 2*[3,4,5,6,8,9,10,11]
random.shuffle(list_num)
df_hex.loc[df_hex['terrain'] !='Désert','numéro'] = list_num
# On vérifie que les 6 et les 8 ne sont pas à côtés
df_hex[df_hex['numéro'].isin([6,8])]
board_correct = True
while board_correct:
    df = df_hex[df_hex['numéro'].isin([6,8])]  # hexagones avec une puissance de 5
    # On enregistre les distances entre les hexagones de puissance 5
    distance_hex=[]
    for row1 in df.itertuples():
        for row2 in df.itertuples():
            if row1.Index != row2.Index:
                distance_hex.append(sqrt(abs(row1.x-row2.x)**2 + abs(row1.y - row2.y)**2))
    if min(distance_hex) < 2:
        """ dans le cas de 2 hexagones de puissance 5 adjacents, il faut refaire la grille """
        random.shuffle(list_num)
        df_hex.loc[df_hex['terrain'] !='Désert','numéro'] = list_num
    else:
        board_correct=False

# On ajoute les puissances des numéros
dict_puissance = {2:1, 3:2,4:3,5:4,6:5,8:5,9:4,10:3,11:2,12:1}  #
df_hex['puissance'] = df_hex['numéro'].map(dict_puissance)
# On converti les float en int puis en str
df_hex.loc[df_hex['terrain'] !='Désert','numéro'] = df_hex.loc[df_hex['terrain'] !='Désert','numéro'].astype(int).astype(str)
df_hex['numéro'].fillna('', inplace=True) # On renseigne le désert
df_hex.fillna(0, inplace=True)
df_hex['puissance'] = df_hex['puissance'].astype(int)




##########################################
# Création des sommets avec nodes
##########################################
# Création de l'abcisse des sommets
x =[-16/4, -14/4, -10/4, -8/4, -2/2, -1/2]
x = [s * i for i in x]
node_x = 3*[x[0]] + 4*[x[1]] + 4*[x[2]] + 5*[x[3]] + 5*[x[4]] + 6*[x[5]]
node_x = node_x + [-i for i in node_x[::-1]]

# Création de l'ordonnée des sommets
node_y = [2*h,0,-2*h] + 2*[3*h,h,-h,-3*h] + 2*[4*h,2*h,0,-2*h,-4*h] + [5*h,3*h,h,-h,-3*h,-5*h]
node_y = node_y + node_y[::-1]


##########################################
#Création des liens sommet-sommet et sommet-hexagone
##########################################
# Distance entre tous les points
nodes = pd.DataFrame()
nodes['sommet'] = range(0,len(node_x))
nodes['x'] = node_x
nodes['y'] = node_y
nodes['y'] = nodes['y'].round(2)
distance_points = distance.cdist(nodes.loc[:,['x','y']], nodes.loc[:,['x','y']], 'euclidean')
distance_points = pd.DataFrame(distance_points, columns=range(len(distance_points)))
couples_points = (distance_points > 0) & (distance_points < 1.5*s)

# distance entre les centres des hexagones et les noeuds
distance_sommets_hex = pd.DataFrame(distance.cdist(nodes.loc[:,['x','y']], df_hex.loc[:,['x','y']], 'euclidean'),
                                    columns=df_hex['hex'],
                                    index=nodes['sommet'])

couples_point_sommet = (distance_sommets_hex > 0) & (distance_sommets_hex < 1.5*s)


nodes['joueur'] = 'None'
nodes['Couleur'] = 'grey'
nodes['construction'] = 'None'
nodes['multiplicateur'] = 1  # est utilisé en cas de ville ou de voleur
nodes['port'] = 'None' #en cas de port 3:1 ou 2:1
player_id, sommet = 0, 2
    



##########################################
#Création des chemins avec df_route
##########################################
segment_route = []
lig = []
for col in couples_points.columns:
    for row in couples_points.index:
        if couples_points.loc[row,col]:
            segment_route.append([list(nodes.loc[row,['x','y']])] + [list(nodes.loc[col,['x','y']])])
            lig.append([row] + list(nodes.loc[row,['x','y']]) + [col] + list(nodes.loc[col,['x','y']]))



# Création d'un dataframe permettant de lier les villes
df_route = pd.DataFrame(lig, columns=['sommet1', 'x1', 'y1', 'sommet2', 'x2', 'y2'])
df_route['couleur'] = 'grey'
df_route['linewidths'] = 2
df_hex['chevalier'] = 'None'
df_hex.loc[df_hex['terrain']=='Désert','chevalier'] = 'chevalier'

lig_hex=[]
for hexa in couples_point_sommet.columns:
    for sommet in couples_point_sommet.index:
        if couples_point_sommet.loc[sommet,hexa]:
           # nodes.loc[sommet,'hex']=hexa
            lig_hex.append([sommet, hexa])
lien_hex_node = pd.DataFrame(lig_hex, columns=['sommet', 'hex'])
lien_hex_node.loc[lien_hex_node['hex']=='A','sommet']
df_hex['s1'], df_hex['s2'], df_hex['s3'] = -1, -1, -1
df_hex['s4'], df_hex['s5'], df_hex['s6'] = -1, -1, -1

for hexa in df_hex['hex']:
    df_hex.loc[df_hex['hex']==hexa,['s1','s2','s3','s4','s5','s6']] = list(lien_hex_node.loc[lien_hex_node['hex']==hexa,'sommet'])




sommet1, sommet2, couleur = 0, 3, 'red'


# On renseigne tous les liens des sommets
def get_link(sommet1):
    """ Renvoie les sommets liés au sommet sélectionné """
    list_link = list(df_route.loc[df_route['sommet1']==sommet1, 'sommet2'])
    if len(list_link) == 2 :
        return list_link + [-1]
    else:
        return list_link

nodes['lien_s1'], nodes['lien_s2'], nodes['lien_s3'] = -1, -1, -1
for sommet in nodes.index:
    nodes.loc[sommet,['lien_s1','lien_s2','lien_s3']] = get_link(sommet)




# On détermine pour chaque sommet la puissance en ressource
nodes['p_wood'], nodes['p_clay'], nodes['p_sheep'], nodes['p_wheat'], nodes['p_stone'] = 0, 0, 0, 0, 0
for sommet in nodes['sommet']:
    # Le DataFrame suivant contient les hexagones adjacents au sommet
    df = df_hex[df_hex[df_hex.loc[:,['s1','s2','s3','s4','s5','s6']]==sommet].max(axis=1)==sommet]
    # On parcourt les ressources adjacentes à la colonie pour obtenir la puissance de cette ressource
    for ressource in ['wood','clay','sheep','wheat','stone']:
        puissance = df.loc[df['terrain']==ressource,'puissance'].sum(axis=0)
        nodes.loc[sommet,'p_'+ressource] = puissance




########################################
# Ajout des ports
########################################
df_port = pd.DataFrame(index=['port' + str(i) for i in range(18)])
df_port['x'] = 4*[-18*w] + 2*[-12*w] + 2*[-6*w] + 2*[0] + 2*[6*w] + 2*[12*w] + 4*[18*w]
df_port['y'] = [3*h,h,-h,-3*h] + [4*h,-4*h] + [5*h,-5*h] + [6*h,-6*h] + \
                [5*h,-5*h] + [4*h,-4*h] + [3*h,h,-h,-3*h]

df_port['y'] = df_port['y'].round(2)


# Obtention de l'angle theta de chaque centre des hexagones ports
def get_coord_polaire_theta(x,y):
     #Obtention de l'angle theta pour un point 
     return(2*atan(y/(x+sqrt(x**2+y**2))))

df_port['theta']= df_port.apply(lambda x: get_coord_polaire_theta(x['x'],x['y']), axis=1)
df_port.sort_values('theta', inplace=True)

liste_port = ['wood','clay','sheep','wheat','stone'] + 4*['3:1']
random.shuffle(liste_port)
for i in range(9):
    liste_port.insert(1+2*i,'')
df_port['port'] = liste_port


sommet_avec_port = [37,42,50,53,52,48,43,27,38,15,10,5,1,0,3,11,16,26]
nodes[nodes['sommet'].isin(sommet_avec_port)]
nodes['port']='None'
nodes['chevalier'] = 'None'

# on associe les ports aux sommets
distance_sommet_port = pd.DataFrame(distance.cdist(
        nodes.loc[nodes['sommet'].isin(sommet_avec_port),['x','y']],
        df_port.loc[df_port['port']!='',['x','y']], 'euclidean'),
    index=nodes.loc[nodes['sommet'].isin(sommet_avec_port),['x','y']].index,
    columns=[m[4:] for m in df_port.loc[df_port['port']!='',['x','y']].index])
# On isole les couples (sommet,port) avec une distance inférieure à 2:
couples_sommet_port = distance_sommet_port < 1.5*s





# On cherche à obtenir les couples sommet-port
segments_port = []
for port in couples_sommet_port.columns:
    for sommet in couples_sommet_port.index:
        if couples_sommet_port.loc[sommet,port]:
            segments_port.append([list(df_port.loc['port'+str(port),['x','y']])] + [list(nodes.loc[sommet,['x','y']])])
            # On renseigne les ports des colonies dans nodes
            nodes.loc[sommet,'port'] = df_port.loc['port'+str(port),'port']

##########################################
# Carte de développement
##########################################
liste_carte_dev = 15*['knight'] + 2*['dev_build2roads'] + 2*['dev_monopole'] \
                    + 2*['dev_2ressource'] + 5*['dev_victory_point']
random.shuffle(liste_carte_dev)



##########################################
# Création du graphique
##########################################
def print_map():
    """ Affiche la carte du jeu """
    fig, ax = plt.subplots(1)  # Create a figure and a set of subplots.
    fig.set_size_inches(18.5, 10.5) #taille de la figure
    ax.set_aspect('equal')   # axes égaux
    
    # Ajout des hexagones de base
    for x, y, c, l, p in zip(df_hex['x'], df_hex['y'], df_hex['couleur'], df_hex['numéro'], df_hex['puissance']):
        color = c[0].lower()  # matplotlib understands lower case words for colours
        hexes = RegularPolygon((x, y), numVertices=6, radius=s, 
                                 orientation=np.radians(30), 
                                 facecolor=color, alpha=0.2)
        ax.add_patch(hexes)
        # Also add a text label
        ax.text(x, y, l, ha='center', va='center', size=16)
        ax.text(x, y-s/3, p*'*', ha='center', va='center', size=10)
        
    # Ajout des segment_route aux hexagones
    # mc = matplotlib.collections
    lc = mc.LineCollection(segment_route, colors=df_route['couleur'], linewidths=df_route['linewidths'])
    ax.add_collection(lc)
    ax.autoscale()
    #ax.margins(0.1)
        
    
    # Ajout des ports
    for x, y, l in zip(df_port['x'], df_port['y'], df_port['port']):
        color = c[0].lower()  # matplotlib understands lower case words for colours
        hexes = RegularPolygon((x, y), numVertices=6, radius=s, 
                                 orientation=np.radians(30), 
                                 facecolor=color, alpha=0.2)
        ax.add_patch(hexes)
        # Also add a text label
        ax.text(x, y, l, ha='center', va='center', size=12)

    # Ajout des segment_route aux hexagones
    # mc = matplotlib.collections
    lc = mc.LineCollection(segments_port)
    ax.add_collection(lc)
    ax.autoscale()


    
    # On trace tous les sommets
    df = nodes[nodes['construction']=='None']
    ax.scatter(df.x, df.y, c=df.Couleur, linewidths=1)  # lieu vide
    # Construction des colonies
    if 'colonie' in list(nodes['construction']):
        df = nodes[nodes['construction']=='colonie']
        ax.scatter(df.x, df.y, c=df.Couleur, linewidths=8, marker='^')  # colonie
    if 'ville' in list(nodes['construction']):
        df = nodes[nodes['construction']=='ville']
        ax.scatter(df.x, df.y, c=df.Couleur, linewidths=17, marker='s')  # colonie
    
    # On affiche le nom des sommets
    for row in nodes.itertuples():
        ax.text(row[2],row[3]+s/8, row[1])
    
    plt.show()

print_map()




##########################################
# Création d'une partie
##########################################
Briac = Player()
Zero = Player()
Briac.wood = 10
Briac.clay = 10
Briac.sheep = 10
Briac.wheat = 10
Briac.stone = 10
#Boss = Player()
Player.current_player=0
get_ressource(player_id=0)
player_id=0

def creation_partie():
    """ Permet aux joueurs de positionner leurs 2 colonies et leurs 2 routes """
    print_map()
    for player in Player.player_list + Player.player_list[::-1]:
        player_id=player.id
        sommets_dispo = list(nodes.loc[nodes['joueur']=='None','sommet'])
        input_1 = int(input('Construction colonie joueur{} \Sommets disponibles : {} \n Veuillez entrer le numéro de la colonie: \n'.format(player_id,sommets_dispo)))
        construction_colonie(player_id=player_id, sommet=int(input_1))
        lien = [x for x in nodes.loc[input_1,['lien_s1','lien_s2', 'lien_s3']].values if x >=0]
        input_2 = int(input('Construction route joueur{} à partir du sommet {} : \n Veuillez entrer lun des numéros suivants {}: '.format(player_id,input_1, lien)))
        construction_route(player_id=player_id, sommet1=input_1, sommet2=input_2)





def partie():
    """ Jouer à Catan"""
    creation_partie()
    for player in Player.player_list:
        action = '' # permet de gérer les événements
        player_id=player.id
        print('######### TOUR JOUEUR ', player_id, '##########')
        Player.current_player=player_id
        # Au début de son tour de jeu, le joueur peut utiliser un voleur
        # Puis il va lancer les dés
        evenement = input('Lancer les dés (y/n)?\n')
        dice = lancer_des()
        if dice == 7:
            get_ressource(player_id)
            roll_seven(player_id)
        # tant que le joueur ne sélectionne pas la fin de tour, il peut jouer
        while action != 'fin de tour':
            df_action = get_action(player_id)
            print_map()
            print(get_ressource(player_id).transpose(),'\n')
            print(df_action.iloc[:,:4])
            evenement = int(input('Numéro action ?\n'))
            if df_action.iloc[evenement,0] != 'fin du tour':
                # Action normal du joueur
                exec(df_action.iloc[evenement,4])
            else:
                # fin de tour du joueur
                action = 'fin de tour'
        
        
        





        




"""
echange_banque(player_id=Player.current_player,liste_carte=[-4,0,1,0,0])
"""









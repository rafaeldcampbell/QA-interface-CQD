#!/usr/bin/env python3
# -*- coding: utf-8 -*-

SUGESTIONS_PER_SEARCH = 5

import pickle
import re
import os



class Entities():
    def __init__(self, path = 'src/data/FB15k-237/'):
        self.ent_id_to_name = dict()
        self.ent_name_to_id = dict()
        self.ent_name_set = set()
        self.initializeDictionaries(path)
        
    def initializeDictionaries(self, path):
        ind2ent_path = path+"ind2ent.pkl"
        entity2text_path = path+"entity2text.txt"
        
        ent_2_ind = {v:k for k,v in pickle.load(open(ind2ent_path, 'rb')).items()} #codEnt -> idEnt
        entity_2_text = [tuple(x.strip('\n').split('\t')) for x in open(entity2text_path)] #(codEnt,textEnt)
        self.ent_id_to_name = {ent_2_ind.get(ent):text for ent,text in entity_2_text} #idEnt -> textEnt
        self.ent_name_to_id = {name.lower()+f' ({id})':id for id,name in self.ent_id_to_name.items()} #textEnt -> idEnt
        self.ent_name_set = set(y+f' ({x})' for x,y in self.ent_id_to_name.items()) # guarda todos os textos
            
    def getNameFromID(self, id):
        return self.ent_id_to_name.get(id, '[missing]')
    
    def getIDFromName(self, name):
        return self.ent_name_to_id.get(name.lower(), -1)
        
    def getAllMatches(self, text_to_search):
        match_pattern = ".*" + ".*".join(text_to_search.split()) + ".*"
        return list(filter(re.compile(match_pattern, re.IGNORECASE).match, self.ent_name_set))
    
    def getBestMatches(self, text_to_search):
        return list(filter(re.compile(text_to_search+'.*', re.IGNORECASE).match, self.ent_name_set))
    
    def __str__(self):
        return "ID->Texto: " + str(self.ent_id_to_name) + "\nTexto->ID: " + str(self.ent_name_to_id) + "\nTextos: " + str(self.ent_name_set)



class Relations():
    def __init__(self,path = 'src/data/FB15k-237/'):
        self.rel_tree = dict()
        self.rel_id_to_name = dict()
        self.rel_name_to_id = dict()
        self.rel_name_set = set()
        self.initializeDictionaries(path)

    def insertRelationInTree(self, node, data):
        if len(data) == 1:
            node[data[0]] = node.get(data[0], dict())
            return node
        else:
            node[data[0]] = node.get(data[0], dict())
            self.insertRelationInTree(node.get(data[0]), data[1:])
        
    def initializeDictionaries(self, path):
        self.rel_id_to_name = pickle.load(open(path+'ind2rel.pkl', 'rb')) # recupera dicionário de ID para Texto
        self.rel_name_to_id = {x:y for y,x in self.rel_id_to_name.items()} # inverte dicionário obtendo Texto para ID
        self.rel_name_set = set(self.rel_name_to_id.keys())
        for rel in self.rel_name_set:
            self.insertRelationInTree(self.rel_tree, rel.split("/")[1:])
            
    def getNameFromID(self, id):
        return self.rel_id_to_name.get(id, '[missing]')
    
    def getIDFromName(self, name):
        return self.rel_name_to_id.get(name.lower(), -1)

    def getRelTree(self):
        return self.rel_tree
    
    def getAllMatches(self, text_to_search):
        match_pattern = ".*"
        for txt in text_to_search.split(): match_pattern = match_pattern + txt + ".*"
        return list(filter(re.compile(match_pattern, re.IGNORECASE).match, self.rel_name_set))
        
    def __str__(self):
        return "ID->Texto: " + str(self.rel_id_to_name) \
             + "\nTexto->ID: " + str(self.rel_name_to_id) \
             + "\nTextos: " + str(self.rel_name_set)
             #+ "\nÁrvore: " + str(self.rel_tree)
        



def getEntity():
    ent = Entities()
    inp = input("-- Buscando entidade --\nBusca: ") # recupera entrada do usuário
    inp_id = ent.getIDFromName(inp) # busca id a partir da entrada do usuário
    
    while inp_id == -1: # enquanto não encontrar
        os.system('cls||clear') # limpa a tela
        matches = ent.getBestMatches(inp) # recupera sugestões
        print("-- Buscando entidade --\nSugestões(%d):" % len(matches)) # imprime header
        for i in range(min(SUGESTIONS_PER_SEARCH, len(matches))): print('\t-', matches[i]) # imprime sugestões
        inp = input("Busca: ") # recupera entrada do usuário
        inp_id = ent.getIDFromName(inp) # busca id a partir da entrada do usuário
        
    os.system('cls||clear') # limpa a tela
    inp_name = ent.getNameFromID(inp_id)
    print("-- Escolhido --\nNome:", inp_name, "\nID:", inp_id)
    return inp_name,inp_id

def getRelation():
    rel = Relations()
    inp = input("-- Buscando relacionamento --\nBusca: ") # recupera entrada do usuário
    inp_id = rel.getIDFromName(inp) # busca id a partir da entrada do usuário
    
    while inp_id == -1: # enquanto não encontrar
        os.system('cls||clear') # limpa a tela
        matches = rel.getAllMatches(inp) # recupera sugestões
        print("-- Buscando relacionamento --\nSugestões(%d):" % len(matches)) # imprime header
        for i in range(min(SUGESTIONS_PER_SEARCH, len(matches))): print('\t-', matches[i]) # imprime sugestões
        inp = input("Busca: ") # recupera entrada do usuário
        inp_id = rel.getIDFromName(inp) # busca id a partir da entrada do usuário
        
    os.system('cls||clear') # limpa a tela
    inp_name = rel.getNameFromID(inp_id)
    print("-- Escolhido --\nNome:", inp_name, "\nID:", inp_id)
    return inp_name,inp_id

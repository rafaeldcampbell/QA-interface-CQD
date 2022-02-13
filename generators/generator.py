import sys
sys.path.insert(1, "/mnt/c/Users/Rafael/Repositórios/cqd/src/")

import pickle
import random
import os

def initialize_dictionaries():
    ind2ent_path = "src/data/FB15k-237/ind2ent.pkl"
    ind2rel_path = "src/data/FB15k-237/ind2rel.pkl"
    entity2text_path = "src/data/FB15k-237/entity2text.txt"
    
    ind_2_relation = pickle.load(open(ind2rel_path, 'rb')) #recupera dicionario idRel -> textRel

    ent_2_ind = {v:k for k,v in pickle.load(open(ind2ent_path, 'rb')).items()} #constroi dicionário codEnt -> idEnt
    entity_2_text = [tuple(x.strip('\n').split('\t')) for x in open(entity2text_path)] #constroi lista (codEnt,textEnt)
    ind_2_entity = {ent_2_ind.get(ent):text for ent,text in entity_2_text} #constroi dicionário idEnt -> textEnt

    test_data =  pickle.load(open("src/data/FB15k-237/test_ans_2c.pkl", 'rb')) #recupera dicionário triple -> answer para queries 1chain2
    test_query_ans = {(k[0][0],k[0][1][0],k[0][1][1]):list(v) for k,v in test_data.items()} #organiza dicionário
    
    return ind_2_relation,ind_2_entity,test_query_ans

def get_random_query(relations, entities, query_tuples):
    queries = list(query_tuples.keys()) #lista as queries
    query = queries[random.randint(0,len(queries))] #seleciona uma query
    query_text = [entities.get(query[0]), relations.get(query[1]), relations.get(query[2])]
    trust_answers = [ entities.get(x) for x in query_tuples.get(query) ]
    return query_text,trust_answers

def get_random_query_with_ids(relations, entities, query_tuples):
    queries = list(query_tuples.keys()) #lista as queries
    query = queries[random.randint(0,len(queries))] #seleciona uma query
    query_text = [entities.get(query[0]), relations.get(query[1]), relations.get(query[2])]
    trust_answers = [ entities.get(x) for x in query_tuples.get(query) ]
    return query,query_text,trust_answers

if __name__ == '__main__':
    relations,entities,query_tuples = initialize_dictionaries()
    while True:
        print("Pressione Enter para gerar uma pergunta")
        inp = input()
        os.system("cls | clear") #limpa o terminal
        if(inp != ""): break
        query_text,trust_answers = get_random_query(relations, entities, query_tuples)
        print("\n-> ".join(query_text), "\n")
        print("Respostas:", ", ".join(trust_answers))
        print("---------------------------------------")


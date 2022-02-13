import sys
sys.path.insert(2, "/mnt/c/Users/Rafael/Repositórios/cqd/")

from generator import *
from qa.QA import QA
import json

COUNT_TEST = 3
CANDIDATES = 2

class Test():
    def __init__(self, triple, query, trusted_answers):
        self.data = {'query IDs': triple,'query': query,'tests' : {},'trusted_answers' : trusted_answers}
    
    def add_test(self, config, results):
        self.data['tests'][config] = results

def get_tests_config():
    pretrained_configs =  [ [str(rank), str(epoch)] for rank in [100,200,500,1000] 
                                                        for epoch in [50, 100] ]
    personal_configs =  [ [model, opt, reg] for model in ['ComplEx', 'DistMult'] 
                                                for opt in ['Adagrad', 'SGD'] 
                                                    for reg in ['N2', 'N3'] ]
    return {0: pretrained_configs, 1: personal_configs}

if __name__ == '__main__':
    relations,entities,query_tuples = initialize_dictionaries()
    test_configs = get_tests_config()
    list_of_tests = {}
    for round in range(COUNT_TEST):
        query,query_text,answers = get_random_query_with_ids(relations,entities,query_tuples)
        query_text_formated = "Query: ?Y:E X.({0}, {1}, X) and (X, {2}, Y)".format(*query_text)
        question_formated = (lambda x:[[x[0], x[1], -1],[-1, x[2], []]])(query)
        test = Test(query,query_text_formated,answers)
        for model_type in [0,1]:
            for configs in test_configs.get(model_type):
                ans,steps = QA.answer(question_formated, CANDIDATES, model_type, configs)
                verified_ans = [(x,y,z,y in answers) for x,y,z in ans]
                test.add_test("-".join(configs), verified_ans)
        list_of_tests["Round " + str(round)] = test.data
        
    with open('tests_data.json', 'w', encoding ='utf8') as json_file:
        json.dump(list_of_tests, json_file, indent="\t")


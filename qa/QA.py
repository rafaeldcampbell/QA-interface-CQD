#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(1, "/mnt/c/Users/Rafael/Repositórios/cqd/src/")
sys.path.insert(2, "/mnt/c/Users/Rafael/Repositórios/cqd/src/models/")
sys.path.insert(3, "/mnt/c/Users/Rafael/Repositórios/cqd/src/data/")

from kbc.utils import QuerDAG,preload_env
from kbc.chain_dataset import Chain,ChaineDataset
from glob import glob
import shutil
from datetime import datetime

QUESTION_DEFAULT = [[1235, 311, -1], [-1, 39, []]]
ANCHOR_DEFAULT = [1235]
CHAIN_TYPE_DEFAULT = '1chain2'

class myChain(Chain): #sobreesrceve o modelo de Chain original para incluir métodos auxiliares
    def setData(self, raw_data, anchors, type):
        self.data['raw_chain'] = raw_data
        self.data['anchors'] = anchors
        self.data['type'] = type
    
    def __str__(self):
        data = ['raw_chain','anchors','optimisable']
        ans = ""
        for d in data:
            ans = ans + d +":\n"
            for i in range(len(self.data[d])):
                if i > 10:
                    ans = ans + "\t...\n"
                    break
                ans = ans + "\t" + str(self.data[d][i]) + "\n"
        ans = ans + "type: " + str(self.data['type']) + "\n"
        return ans

class QA:

    @staticmethod
    def answer(question : list = QUESTION_DEFAULT, candidates : int = 2,
                model_type : int = 0, model_arguments : list = ['100', '50']):
        model_path = QA.getModelPath(model_type, model_arguments)
        QA.ask(question, question[0][0], int(candidates), model_path)
        query,answers,steps = QA.getAnswer()
        try:
            timestamp = str(datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
            shutil.move('explain.log', 'logs/explain_' + timestamp + '.log') #remove o arquivo de log
        except: pass
        return answers,steps


    @staticmethod
    def ask(question : list = QUESTION_DEFAULT, anchor : list = ANCHOR_DEFAULT, 
            candidates : int = 2, model_path = 'FB15k-237-model-rank-100-epoch-50-1602503352.pt'):
        chain = myChain() # constroi uma instância de Chain, que carregará a pergunta
        chain.setData(question, anchor, CHAIN_TYPE_DEFAULT) # adiciona as informações da pergunta à Chain
        dataset = ChaineDataset(None) # construindo um objeto ChaineDataset, que irá carregar a pergunta
        dataset.type1_2chain.append(chain) # adicionando a pergunta ao dataset
        query_type = QuerDAG.TYPE1_2.value
        data_path = 'src/data/FB15k-237'
        preload_env(model_path, dataset, query_type, "hard", data_path, True, True)
        env = preload_env(model_path, dataset, query_type, "complete", data_path, True, False)
        kbc = env.kbc
        score = kbc.model.query_answering_BF(env, candidates, scores_normalize = 0, explain=True)
        return score

    @staticmethod
    def getAnswer():
        answer_file = open('explain.log')
        line = answer_file.readline()
        query = ""
        count = 0
        while line:
            if line[:5] == "Query": query = line[7:]
            if line[:3] == 'Top':
                count = int(line.split()[1])
                line = answer_file.readline() #lê os cabeçalhos
                break
            line = answer_file.readline()
        answers = []
        for i in range(count):
            line = answer_file.readline()
            data = line.split()
            answers.append(tuple([data[1], " ".join(data[2:-1]), data[-1]]))
        answer_file.close()
        steps = QA.getSteps()
        return query,answers,steps

    @staticmethod
    def getSteps():
        with open('explain.log') as answer_file:
            line = answer_file.readline()#ignora separador da primeira linha
            line = answer_file.readline()#ignora linha da pergunta
            line = answer_file.readline()
            steps = ''
            while line:
                if line[:3] != 'Top':
                    steps = steps + line
                    line = answer_file.readline()
                else:
                    break
        return steps


    @staticmethod
    def getModelPath(model_type, model_arguments):
        if(model_type == 0): #pre treinados
            modelPathList = glob(f'src/models/*-Pretrained-*rank-{model_arguments[0]}-*epoch-{model_arguments[1]}-*.pt')
        else:
            modelPathList = glob(f'src/models/*{model_arguments[0]}-{model_arguments[1]}-{model_arguments[2]}*.pt')
        print(modelPathList)
        return modelPathList[0]

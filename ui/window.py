import sys
sys.path.insert(1, "/mnt/c/Users/Rafael/Repositórios/cqd/qa/")
from tkinter import *
from tkinter import ttk
from enum import Enum
from QM import Entities,Relations
from QA import QA

WINDOW_NAME = "Question Answering"
WINDOW_GEOMETRY = "800x500"
ENTITY_NAME_DEFAULT = "<ENTIDADE>"
RELATION_NAME_DEFAULT = "<RELAÇÃO>"
CANDIDATES_OPTIONS = [2,3,4,5]
RANK_OPTIONS = [100,200,500,1000]
EPOCH_OPTIONS = [50,100]
MODEL_OPTIONS = ['ComplEx', 'DistMult']
OPTIMIZER_OPTIONS = ['Adagrad', 'SGD']
REGULARIZER_OPTIONS = ['N2', 'N3']



class Window():
    def __init__(self):
        self.root = Tk()
        self.root.title(WINDOW_NAME)
        self.root.overrideredirect(False)
        self.root.geometry("{0}x{1}+0+0".format(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        #self.root.geometry(WINDOW_GEOMETRY)

        self.main_frame = Frame(self.root)
        self.main_frame.pack(anchor=CENTER)

        self.query_label_text = StringVar()
        self.query_content = [ENTITY_NAME_DEFAULT, RELATION_NAME_DEFAULT, RELATION_NAME_DEFAULT]
        self.updateQuery()
        self.query_label = Label(self.main_frame, textvariable=self.query_label_text, height=3,
                                 pady=20, font=("Courier", 14), wraplength=1000)
        self.query_label.grid(row=0, column=0)

        self.query_frame = Frame(self.main_frame)
        self.query_frame.grid(row=1, column=0)

        self.entity_window = EntityWindow(self.query_frame, self, 0)
        self.entity_frame = self.entity_window.getFrame()
        self.entity_frame.grid(row=0, column=0, pady=5)

        self.relation1_window = RelationWindow(self.query_frame, self, 1)
        self.relation1_frame = self.relation1_window.getFrame()
        self.relation1_frame.grid(row=0, column=1, pady=5, padx=10)

        self.relation2_window = RelationWindow(self.query_frame, self, 2)
        self.relation2_frame = self.relation2_window.getFrame()
        self.relation2_frame.grid(row=0, column=2, pady=5)

        result_frame = ResultWindow(self.main_frame, self)
        self.result_frame = result_frame.getFrame()
        self.result_frame.grid(row=2, column=0)

        self.root.mainloop()
    
    def updateQuery(self):
        self.query_label_text.set("Query: ?Y:∃ X.(" + self.query_content[0] \
                                + ", " + self.query_content[1] + ", X) and (X, " \
                                + self.query_content[2] + ", Y)")
    
    def getQuery(self):
        return [ [self.entity_window.getID(), self.relation1_window.getID(),-1],
                 [-1, self.relation2_window.getID(),[]] ]
        



class EntityWindow():
    def __init__(self, root, parent, query_content_index):
        self.parent = parent
        self.query_content_index = query_content_index
        self.ent_id = -1
        self.Entities = Entities()

        self.frame = Frame(root, width=400, height=250, highlightbackground="black", 
                           highlightthickness=1, padx=10, pady=10) # define o frame principal que engloba todos os elementos da escolha da entidade
        self.frame.pack_propagate(0)

        self.list_frame = Frame(self.frame)
        self.entity_tree = ttk.Treeview(self.list_frame, column=('head'), show='', selectmode="browse")
        self.entity_tree.pack(side=LEFT, expand=1, fill=BOTH)
        self.entity_tree.bind('<<TreeviewSelect>>', self.item_selected)
        self.scrollbar = ttk.Scrollbar(self.list_frame, orient=VERTICAL, command=self.entity_tree.yview)
        self.entity_tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.list_frame.pack(side=TOP, expand=1, fill=BOTH)

        self.input_frame = Frame(self.frame) # define o espaço onde serão alocados o Entry e Button
        self.input_entry_text = StringVar() # define o texto digitado pelo usuário
        self.input_entry = Entry(self.input_frame, textvariable=self.input_entry_text, width=40) # define a entrada do usuário
        self.input_button = Button(self.input_frame, text="Buscar", command=self.updateTree) # define o botão OK
        self.input_entry.grid(row=0, column=0) # posiciona a entrada no grid
        self.input_button.grid(row=0, column=1) # posiciona o botão no grid
        self.input_frame.pack(side=BOTTOM)  # posiciona o frame de entrada no grid

        self.updateTree()
    
    def updateTree(self):
        for item in self.entity_tree.get_children(): # deleta todos os elementos
            self.entity_tree.delete(item)
        sugestions = self.Entities.getAllMatches(self.input_entry_text.get())
        sugestions.sort()
        for sug in sugestions:
            self.entity_tree.insert('', END, values=[sug])
        return 0
    
    def item_selected(self, event):
        name = self.entity_tree.item(self.entity_tree.selection()[0])['values'][0]
        self.ent_id = self.Entities.getIDFromName(name)
        self.frame.config(highlightbackground="green", highlightcolor="green", highlightthickness=2)
        self.parent.query_content[self.query_content_index] = name
        self.parent.updateQuery()

    def getFrame(self): return self.frame
    def getID(self): return self.ent_id




class RelationWindow():
    def __init__(self, root, parent, query_content_index):
        self.parent = parent
        self.query_content_index = query_content_index
        self.rel_id = -1
        self.Relations = Relations()

        self.frame = Frame(root, width=400, height=250, highlightbackground="black", 
                           highlightthickness=1, padx=10, pady=10) # define o frame principal que engloba todos os elementos da escolha da entidade
        self.frame.pack_propagate(0)
        
        self.relation_tree = ttk.Treeview(self.frame, column=('head'), show='tree', selectmode="browse")
        self.relation_tree.column("#0", minwidth=0, width=30)
        self.relation_tree.pack(side=LEFT, expand=1, fill=BOTH)
        self.relation_tree.bind('<<TreeviewSelect>>', self.item_selected)

        self.scrollbar = ttk.Scrollbar(self.frame, orient=VERTICAL, command=self.relation_tree.yview)
        self.relation_tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.populateTreeView('', self.Relations.getRelTree())
    
    def populateTreeView(self, current_id, options : dict):
        opt_list = list(options.keys())
        opt_list.sort()
        for i in opt_list:
            node_id = self.relation_tree.insert(current_id, END, values=i)
            self.populateTreeView(node_id, options.get(i))
        return 0
    
    def item_selected(self, event):
        selected_path = self.getCompletePath(self.relation_tree.selection()[0])
        self.rel_id = self.Relations.getIDFromName(selected_path)
        if self.rel_id != -1:
            self.frame.config(highlightbackground="green", highlightcolor="green", highlightthickness=2)
            self.parent.query_content[self.query_content_index] = self.Relations.getNameFromID(self.rel_id)
            self.parent.updateQuery()
        else:
            self.frame.config(highlightbackground="black", highlightcolor="black", highlightthickness=1)
            self.parent.query_content[self.query_content_index] = RELATION_NAME_DEFAULT
            self.parent.updateQuery()

    def getCompletePath(self, id):
        path = []
        path.append(self.relation_tree.item(id)['values'][0])
        id = self.relation_tree.parent(id)
        while id != "":
            path.append(self.relation_tree.item(id)['values'][0])
            id = self.relation_tree.parent(id)
        path.reverse()
        return "/"+"/".join(path)

    def getFrame(self): return self.frame
    def getID(self): return self.rel_id
        

class ResultWindow():

    __current_config_mode = 0 # 0 - pretrained | 1 - custom

    def __init__(self, root, parent):
        self.parent = parent
        self.frame = Frame(root, width=1240, height=300, padx=10, pady=10) # define o frame principal que engloba todos os elementos da escolha da entidade
        self.frame.pack_propagate(0)

        self.config_and_button_frame = Frame(self.frame, width=400, height=250, highlightbackground="black", 
                           highlightthickness=1, padx=10, pady=5)

        self.set_mode_frame = Frame(self.config_and_button_frame)
        self.set_pretrained_button = Button(self.set_mode_frame, text='Pré-treinados', 
                                            command=self.setPretrainedMode, borderwidth=2)
        self.set_pretrained_button.grid(row=1, column=0, padx=5)
        self.set_custom_button = Button(self.set_mode_frame, text='Personalizados',
                                          command=self.setCustomMode, borderwidth=2)
        self.set_custom_button.grid(row=1, column=1)
        self.set_mode_frame.grid(row=0, column=0, pady=(0,7))

        self.config_frame = Frame(self.config_and_button_frame)
        self.candidate_label = Label(self.config_frame, text="Candidatos", padx=8)
        self.candidate_label.grid(row=0, column=0)
        self.candidate_value = StringVar() #guarda a quantidade de candidatos
        self.candidate_value.set(CANDIDATES_OPTIONS[0]) #define 2 por padrão
        self.candidate_menu = OptionMenu(self.config_frame, self.candidate_value, *CANDIDATES_OPTIONS)
        self.candidate_menu.config(width=7)
        self.candidate_menu.grid(row=0, column=1)
        self.rank_label = Label(self.config_frame, text="Rank", padx=12)
        self.rank_label.grid(row=1, column=0, pady=(7,0))
        self.rank_value = StringVar() #guarda o modelo
        self.rank_value.set(RANK_OPTIONS[0]) #define ComplEx por padrão
        self.rank_menu = OptionMenu(self.config_frame, self.rank_value, *RANK_OPTIONS)
        self.rank_menu.config(width=7)
        self.rank_menu.grid(row=1, column=1, pady=(7,0))
        self.epoch_label = Label(self.config_frame, text="Epoch", padx=12)
        self.epoch_label.grid(row=2, column=0, pady=(0,7))
        self.epoch_value = StringVar() #guarda o otimizador
        self.epoch_value.set(EPOCH_OPTIONS[0]) #define Adagrad por padrão
        self.epoch_menu = OptionMenu(self.config_frame, self.epoch_value, *EPOCH_OPTIONS)
        self.epoch_menu.config(width=7)
        self.epoch_menu.grid(row=2, column=1, pady=(0,7))
        self.model_label = Label(self.config_frame, text="Modelo", padx=5)
        self.model_label.grid(row=3, column=0)
        self.model_value = StringVar() #guarda o modelo
        self.model_value.set(MODEL_OPTIONS[0]) #define ComplEx por padrão
        self.model_menu = OptionMenu(self.config_frame, self.model_value, *MODEL_OPTIONS)
        self.model_menu.config(width=7)
        self.model_menu.grid(row=3, column=1)
        self.optimizer_label = Label(self.config_frame, text="Otimizador", padx=5)
        self.optimizer_label.grid(row=4, column=0)
        self.optimizer_value = StringVar() #guarda o otimizador
        self.optimizer_value.set(OPTIMIZER_OPTIONS[0]) #define Adagrad por padrão
        self.optimizer_menu = OptionMenu(self.config_frame, self.optimizer_value, *OPTIMIZER_OPTIONS)
        self.optimizer_menu.config(width=7)
        self.optimizer_menu.grid(row=4, column=1)
        self.regularizer_label = Label(self.config_frame, text="Regularizador", padx=5)
        self.regularizer_label.grid(row=5, column=0, pady=(0,7))
        self.regularizer_value = StringVar() #guarda o regularizador
        self.regularizer_value.set(REGULARIZER_OPTIONS[1]) #define N3 por padrão
        self.regularizer_menu = OptionMenu(self.config_frame, self.regularizer_value, *REGULARIZER_OPTIONS)
        self.regularizer_menu.config(width=7)
        self.regularizer_menu.grid(row=5, column=1, pady=(0,7))
        self.step_label = Label(self.config_frame, text="Exibir passo-a-passo", padx=5)
        self.step_label.grid(row=6, column=0)
        self.step_checkbox_state = IntVar()
        self.step_checkbox = Checkbutton(self.config_frame, variable=self.step_checkbox_state)
        self.step_checkbox.grid(row=6, column=1)
        self.config_frame.grid(row=1, column=0)

        self.button = Button(self.config_and_button_frame, text="GERAR RESPOSTA", command=self.updateResultGrid)
        self.button.grid(row=2, column=0, pady=7)

        self.config_and_button_frame.pack(side=LEFT, fill=Y)

        self.result_frame = Frame(self.frame)
        self.result_step_frame = Frame(self.result_frame)
        self.result_data_frame = Frame(self.result_frame)
        self.result_data_grid = Frame(self.result_data_frame)

        self.result_step_frame.pack(side=LEFT, padx=(10,0))
        self.result_data_frame.pack(side=RIGHT, expand=1, fill=BOTH)

        self.result_frame.pack(side=RIGHT, expand=1, fill=BOTH, anchor=CENTER)
        self.setPretrainedMode()
        self.result_grid_labels = []



    def updateResultGrid(self):
        #atualiza a query e processa a pergunta
        query = self.parent.getQuery()
        if(query[0][0] == -1 or query[0][1] == -1 or query[1][1] == -1):
            return 0
        self.step_data = ''
        print(query)
        if (self.__current_config_mode == 0): #pretreinado
            self.result_data,self.step_data  = QA.answer(query, self.candidate_value.get(), 0,
                [self.rank_value.get(),self.epoch_value.get()])
        else: #personalizado
            self.result_data,self.step_data  = QA.answer(query, self.candidate_value.get(), 1,
                [self.model_value.get(),self.optimizer_value.get(), self.regularizer_value.get()])

        self.result_step_frame.pack_forget() #apaga da tela
        self.result_step_frame.destroy() #destroi o objeto
        if self.step_checkbox_state.get(): 
            self.updateSteps() #atualiza tela de steps se estiver marcado
        for i in self.result_grid_labels: # apagando cada um dos objetos do grid de resultado
            i.grid_forget()
            i.destroy()
        self.result_grid_labels = []
        self.result_data_grid.pack_forget() #apaga da tela
        self.result_data_grid.destroy() #destroi o objeto
        self.result_data_grid = Frame(self.result_data_frame) #recria o objeto
        header = ["Rank", "Resultado", "Score"] #define o texto dos headers
        for j in range(len(header)): #insere os headers
            label = Label(self.result_data_grid, font=("Courier", 14), text=header[j])
            label.grid(row=0, column=j, padx=5)
            self.result_grid_labels.append(label)
        for i in range(len(self.result_data)): #imprime um resultado por linha
            for j in range(len(self.result_data[i])): #imprime cada uma das colunas do resultado
                label = Label(self.result_data_grid, font=("Courier", 13), text=self.result_data[i][j])
                label.grid(row=i+1, column=j, padx=5)
                self.result_grid_labels.append(label)
        self.result_data_grid.pack(anchor=CENTER)
        self.result_data_frame.update

    def updateSteps(self):        
        self.result_step_frame = Frame(self.result_frame, width=400, height=250, highlightbackground="black", 
                           highlightthickness=1) #recria o objeto
        self.result_step_frame.pack_propagate(0)
        scrollbar = Scrollbar(self.result_step_frame)
        text_frame = Text(self.result_step_frame, yscrollcommand=scrollbar.set)
        text_frame.insert(END, self.step_data)
        text_frame.config(state=DISABLED)
        scrollbar.config(command=text_frame.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        text_frame.pack(side=LEFT, fill=BOTH)
        self.result_step_frame.pack(side=LEFT, padx=(10,0))
        self.result_step_frame.update

    def setPretrainedMode(self):
        self.__current_config_mode = 0
        self.set_pretrained_button.config(relief='sunken')
        self.set_custom_button.config(relief='raised')
        self.rank_menu.config(state=NORMAL)
        self.epoch_menu.config(state=NORMAL)
        self.model_menu.config(state=DISABLED)
        self.optimizer_menu.config(state=DISABLED)
        self.regularizer_menu.config(state=DISABLED)
        return 0

    def setCustomMode(self):
        self.__current_config_mode = 1
        self.set_pretrained_button.config(relief='raised')
        self.set_custom_button.config(relief='sunken')
        self.rank_menu.config(state=DISABLED)
        self.epoch_menu.config(state=DISABLED)
        self.model_menu.config(state=NORMAL)
        self.optimizer_menu.config(state=NORMAL)
        self.regularizer_menu.config(state=NORMAL)
        return 0

    def getFrame(self): return self.frame

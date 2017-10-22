# -*- coding: latin-1 -*-
#Compatível com 3.4 e 2.7
try:
    import requests
    REQUEST = True
except:
    import urllib.request
    REQUEST = False
    
from bs4 import BeautifulSoup as bs
import threading as td
#from BeautifulSoup import BeautifulSoup as bs

try:
    from Tkinter import Tk, Toplevel, Label, LabelFrame, Button, Entry, Frame, StringVar, TOP, LEFT, CENTER, W
except:
    from tkinter import Tk, Toplevel, Label, LabelFrame, Button, Entry, Frame, StringVar, TOP, LEFT, CENTER, W
    
class RastreadorCorreios():
    def __init__(self, codigo):
        self.codigo = codigo
        self.url = "http://websro.correios.com.br/sro_bin/txect01$.QueryList?P_LINGUA=001&P_TIPO=001"
        self.param = {"P_COD_UNI":self.codigo}
    
    def getRespostaRastreio(self):
        if REQUEST: return requests.get(self.url, params=self.param).text
        else:
            url = urllib.request.Request(url=self.url+'&'+urllib.parse.urlencode(self.param))
            return urllib.request.urlopen(url).read()
    
    def criarLinhasTabela(self, resposta):
        bsObj = bs(resposta, "html.parser")
        self._corpo = corpo = bsObj.body
        self._tabela = tabela = corpo.find(name="table")
        try:
            trs = tabela.findAll("td") #Coleta todas as tds com todas as tags
            return [trTag.get_text() for trTag in trs][3:] # Os tipos listas do BeautifulSoup nao tem nenhum metodo fora os normais de lista
        except AttributeError:
            #print "O modulo findall não foi encontrado"
            #print dir(tabela)
            return []
        

    def formatarLinhas(self, linhasTabela):
        linhas_format = []
        data_cte_situacao = [] # Guarda a data, cte e situacao
        linhaUnica = [] # Guarda: ((data, cte, situação, local)

        index_line_data_cte_situacao = 0
        for index, elemento in enumerate(linhasTabela):
            index_line_data_cte_situacao += 1
            #print elemento, index_line_data_cte_situacao
            
            if index_line_data_cte_situacao % 3 == 0 and not index_line_data_cte_situacao == 0:
                if elemento == "Postado" or elemento == "Saiu para entrega ao destinatário":
                    data_cte_situacao.append(elemento)
                    linhas_format.append(data_cte_situacao)
                    data_cte_situacao, linhaUnica = [], []
                    index_line_data_cte_situacao = 0
                else:
                    index_line_data_cte_situacao = -1
                    data_cte_situacao.append(elemento)
                    linhaUnica.append(data_cte_situacao)
                    
            elif index_line_data_cte_situacao == 0:
                linhaUnica.append(elemento)
                linhas_format.append(linhaUnica)
                data_cte_situacao, linhaUnica = [], []
            else:
                data_cte_situacao.append(elemento)

        return linhas_format

class Interface(Frame):
    def __init__(self, master, titulo="App", msg="", *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)
        self.master = master
        #master.resizable(0, 0)
        master.title(titulo)
        self.msg = msg
        try: master.iconbitmap("icones\Site.ico")
        except: master.iconbitmap("Site.ico")
        self.criarInterface()
        
    def criarInterface(self):
        Label(self.master, text=self.msg).pack(side=TOP, pady=10, padx=10)
        botaoEntradaFrame = Frame(self.master)
        botaoEntradaFrame.pack(side=TOP, pady=10)
        
        self.codigoEntrada = StringVar()
        self.codigoEntrada.set("PG148828108BR")
        Entry(botaoEntradaFrame, textvar=self.codigoEntrada, font=("Arial", 11), width=15).pack(side=LEFT, padx=5)
        Button(botaoEntradaFrame, text="Rastrear", width=10, command=self.gerarLabels).pack(side=LEFT, padx=5)
        Button(botaoEntradaFrame, text="Limpar", width=10, command=self.limpar).pack(side=LEFT, padx=5)

        self.msgNaoEncVar = StringVar()
        self.msgNaoEncontrado = Label(self.master, textvar=self.msgNaoEncVar)#, background="#008B8B")
        self.msgNaoEncontrado.pack(side=TOP, padx=30, pady=0, fill="x")

    def exibirMsgNaoEncontrado(self):
        self.msgNaoEncontrado["bg"] = "#008B8B"
        self.msgNaoEncontrado["font"] = ("Arial", 13)
        self.msgNaoEncVar.set("Código não encontrado")
        
    def apagarMsgNaoEncontrado(self):
        self.msgNaoEncontrado["bg"] = "SystemButtonFace"
        self.msgNaoEncontrado["font"] = ("Arial", 2)
        self.msgNaoEncVar.set("")

    def construirLinha(self, frame, track, bg):
        dataCteStateFrame = Frame(master=frame, background=bg)
        dataCteStateFrame.pack(side=TOP, expand=True, fill="x")
        
        Label(dataCteStateFrame, text=track[0], background=bg, justify=CENTER).grid(row=0, column=0, ipadx=5, sticky=W)#Data
        Label(dataCteStateFrame, text=track[1], background=bg, justify=CENTER).grid(row=0, column=1, ipadx=5, sticky=W)#cte ou local
        Label(dataCteStateFrame, text=track[2], background=bg, justify=CENTER).grid(row=0, column=2, ipadx=5, sticky=W)#Situcação
            
    def gerarLabels(self):
        self.apagarMsgNaoEncontrado()
        self.cod = self.codigoEntrada.get()
        #self.limpar()
        self.removerLabels()
        
        self.THREAD = td.Thread(target=self.gerarLabelsProcesso, args=())
        self.THREAD.start()

    def gerarLabelsProcesso(self, entrada=None):
        stop = td.Event()
        self.labelsFrame = labelsFrame = LabelFrame(self.master, text="Rastreio da track", padx=10, pady=10)
        labelsFrame.pack(side=TOP, expand=True, fill="x", padx=30, pady=10)
        self.rc = rc = RastreadorCorreios(codigo=self.cod)
        trackList = rc.formatarLinhas(rc.criarLinhasTabela(rc.getRespostaRastreio()))
        if trackList:
            for index, track in enumerate(trackList):
                #(((data, cte, situacao), local))
                
                if len(track) == 2:#(data, cte, situacao), local)
                    self.construirLinha(frame=labelsFrame, track=track[0], bg="#008B8B")
                    Label(self.labelsFrame, text=track[1]+'\n'.upper(), background="#7FFFD4").pack(side=TOP, fill="x")#local
                else:
                    if track[2] == "Saiu para entrega ao destinatário":
                        self.construirLinha(frame=labelsFrame, track=track, bg="#7FFF00")
                    else:
                        self.construirLinha(frame=labelsFrame, track=track, bg="#008B8B")
        else:
            self.exibirMsgNaoEncontrado()
        stop.set()

    def limpar(self):
        self.codigoEntrada.set("")

    def removerLabels(self):
        try: self.labelsFrame.destroy()
        except: pass#print "Erro ao destruir"
        
        
tk = Tk()
inter = Interface(master=tk, titulo="Rastreio Correios", msg="O horário não indica quando a situação ocorreu, mas sim quando os dados foram recebidos pelo sistema, \nexceto no caso do SEDEX 10 e do SEDEX Hoje, em que ele representa o horário real da entrega.")
inter.mainloop()

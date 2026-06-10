import copy

import networkx as nx
from fastapi._compat import v2

from database.DAO import DAO


class Model:
    def __init__(self):
        self._graph=nx.Graph()
        self._airports=DAO.getAllAirports()
        self._idMapAirports={}
        for a in self._airports:
            self._idMapAirports[a.ID] = a
        self._bestCammino = []
        self._bestScore = 0

    def getCamminoOttimo(self,v0,v1,t):
        self._bestCammino=[]
        self._bestScore=0

        parziale=[v0]

        self._ricorsione(parziale,v1,t)
        return self._bestCammino,self._bestScore

    def _ricorsione(self,parziale,v1,t):
        #verifico se parziale è una soluzione valida, ed in caso salvo
        if parziale[-1]==v1:
            #potenzialmente questa è una sol accettabile
            if self._getScore(parziale)>self._bestScore:
                self._bestCammino=copy.deepcopy(parziale)
                self._bestScore=self._getScore(parziale)

        #verifico se ha senso continuare ad aggiungere lementi in parziale, oppure esco
        if len(parziale)==t+1: #se la condizione è vera, parziale ha già raggiunto il numero massimo di tratte
             return

        #espando parziale e faccio la ricorsione
        for n in self._graph.neighbors(parziale[-1]):
            if n not in parziale:
                parziale.append(n)
                self._ricorsione(parziale,v1,t)
                parziale.pop()

    def _getScore(self,parziale):
        sumPesi=0
        for i in range(0,len(parziale)-1):
            sumPesi+=self._graph[parziale[i]][parziale[i+1]]["weight"]
        return sumPesi

    def buildGraph(self,nMin):
        nodes=DAO.getAllNodes(nMin,self._idMapAirports)
        self._graph.add_nodes_from(nodes)
        print(f"N nodi.{len(self._graph.nodes)},n archi: {len(self._graph.edges)}")
        self.addEdges()
        print(f"N nodi.{len(self._graph.nodes)},n archi: {len(self._graph.edges)}")
        self.addEdgesv2()
        print(f"N nodi.{len(self._graph.nodes)},n archi: {len(self._graph.edges)}")

    def addEdges(self):
        allTratte=DAO.getAllEdgesv1(self._idMapAirports)
        #queste tratte hanno 2 problemi:
        #1- ho archi diretti e inversi, devo fare la somma a mano
        #2- ho archi tra aeroporti che avevo filtrato

        for t in allTratte:
            if t.aeroportoP in self._graph and t.aeroportoA in self._graph:
                if self._graph.has_edge(t.aeroportoP, t.aeroportoA):
                    #se c'era già un arco , mantienilo ma increamenta il peso
                    self._graph[t.aeroportoP][t.aeroportoA]["weight"]+=t.peso
                #allora posso aggiungerlo
                self._graph.add_edge(t.aeroportoP, t.aeroportoA, weight=t.peso)

    def addEdgesv2(self):
        allTratte=DAO.getAllEdgesv2(self._idMapAirports)
        for t in allTratte:
            if t.aeroportoP in self._graph and t.aeroportoA in self._graph:

                # allora posso aggiungerlo
                self._graph.add_edge(t.aeroportoP, t.aeroportoA, weight=t.peso)

    def getViciniOrdinati(self,source):
        #tutti i vicini di source ordinati per peso dell'arco che collega source al vicino
        vicini= self._graph.neighbors(source)
        viciniT=[]
        for v in vicini:
            viciniT.append((v,self._graph[source][v]["weight"]))
        viciniT.sort(key= lambda x:x[1])

        return viciniT
    def hasPath(self,v0,v1):
        #verifico se v1 è presente nella componente connessa di v0
        #nx.connected_components() lista di componenti connesse
        return v1 in nx.node_connected_component(self._graph,v0)

    def getPath(self,v0,v1):
        #v1
        #dictOfPredecessors=dict(nx.bfs_predecessors(self._graph,v0))
        #path=[v1]
        #while path[0]!= v0:
        #    path.insert(0,dictOfPredecessors[path[0]])
        #v2
        #dictOfPredecessors=dict(nx.dfs_predecessors(self._graph,v1))
        #path=[v1]
        #while path[0]!= v0:
        #    path.insert(0,dictOfPredecessors[path[0]])
        #v3
        #path=nx.shortest_path(v0,v1)
        #v4
        path=nx.dijkstra_path(self._graph,v0,v1,weight=None) #non considerare i pesi degli archi
        return path



    def getGraphDetails(self):
        return len(self._graph.nodes),len(self._graph.edges)

    def getAllNodes(self):
        nodes= list(self._graph.nodes)
        nodes.sort(key= lambda x: x.IATA_CODE)
        return nodes

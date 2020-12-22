class MTBrain(object):
    def  __init__(self) -> None:
        self.neurons=dict()
        self.brnin=list()
        self.brnout=list()
        return

    def getNeuron(self,nid):
        return self.neurons[nid]

    def addNeuron(self,neuron,target,weight):
        self.neurons[neuron.nid]=neuron
        if isinstance(target,MTNeuron):
            target.addNeuin(neuron,weight)
            neuron.addNeuout(target)
        # elif target is None:

        return

    def linkNeurons(self,src,tar,weight):
        tar.addNeuin(src,weight)
        src.addNeuout(tar)

        return
    pass

class MTNeuron(object):
    BRAIN=None

    @classmethod
    def setCommon(cls,**argkw):
        if 'BRAIN' in argkw:cls.BRAIN=argkw['BRAIN']
        return

    @staticmethod
    def funcSig(x):
        if x>0:y=1
        elif x<0:y=-1
        else:y=0
        return y

    @staticmethod
    def funcRamp(x):
        if x<=0:y=0
        else:y=x
        return y

    def __init__(self,**argkw) -> None:
        self.nid=argkw.get('nid',0)
        self.dendron=argkw.get('dendron',[0,0,0])
        self.axon=argkw.get('axon',[1,0,0])
        self.neuin=argkw.get('neuin',[])    # List of nid;
        self.neuput=argkw.get('neuout',[])
        self.weight=argkw.get('weight',dict())
        self.func=argkw.get('func',self.funcRamp)
        self._neuin=list()  # Instances;
        # self._neuout=list()
        self.value=0
        self.bias=0
        return

    def actitivate(self):
        if len(self._neuin)!=len(self.neuin):self.bindNeuron()
        self.value=self.bias
        weightsum=0
        for w in self.weight.values():
            weightsum+=w
        for neuron in self._neuin:
            self.value+=self.func(neuron.value)*self.weight[neuron.nid]/weightsum
        return self.value

    def bindNeuron(self):
        self._neuin=list()
        for neuron in self.neuin:
            self._neuin.append(self.BRAIN.getNeuron(neuron.nid))
        return

    def addNeuin(self,neuron,weight=1):
        if neuron.nid not in self.neuin:
            self.neuin.append(neuron.nid)
            self.setWeight(neuron,weight)
        return

    def addNeuout(self,neuron):
        if neuron.nid not in self.neuout:
            self.neuout.append(neuron.nid)
        return

    def setWeight(self,neuron,weight):
        if neuron.nid in self.neuin:
            self.weight[neuron.tid]=weight
        return

    def delNeuin(self,neuron):
        if neuron.nid in self.neuin:
            self.neuin.remove(neuron.nid)
            del self.weight[neuron.nid]
    pass

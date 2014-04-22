class name_dict(dict):
    # def __init__(self,p,arr,repr):
    #     for i,a in enumerate(arr):
    #         self[arr[i]] = p[i+1]
    #     #self = self.append(zip(arr,p))
    #     self["repr"] = repr
    # @staticmethod
    # def create(d,repr):
    def set_repr(self,r):
    	self["repr"] = r
    	return self
       	
    def __getattr__(self,name):
        return self[name] if self[name] is not None else ''
    def __repr__(self):
    	return self["repr"] if not callable(self["repr"]) else self["repr"](self)
    	

        	
       
        	
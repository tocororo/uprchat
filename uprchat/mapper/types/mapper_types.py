class Node:
    def __init__(self, label: str, id: str, properties: dict = {}):
        self.label = label
        self.id = id
        self.properties = {"id": id}
        self.nested_nodes = []


class NestedNode(Node):
    def __init__(self, label, id, belongs_to: str, properties: dict = {}):
        super().__init__(label, id, properties)
        self.belongs_to = belongs_to
        self.relation_label =""
    
    def set_relation_label(self,relation_label:str):
        print("THE RELATION LABEL SET: ", relation_label)
        self.relation_label = relation_label
    
    def get_relation_label(self)->str:
        if self.relation_label:
            print("THE RELATION LABEL returned: ", self.relation_label)
            
            return self.relation_label
        return "HAS"

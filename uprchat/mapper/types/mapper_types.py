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

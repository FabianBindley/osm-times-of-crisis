import osmium

class ElementExtractor(osmium.SimpleHandler):
    def __init__(self, required_nodes):
        super().__init__()
        self.required_nodes = required_nodes


    def node(self, n):
        if n.id in self.required_nodes and n.visible:
            self.required_nodes[n.id] = (n.lon, n.lat)





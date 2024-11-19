import osmium

# Define a handler to process OSM data
class BuildingCounterHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.building_count = 0

    def node(self, n):
        if 'building' in n.tags:
            self.building_count += 1

    def way(self, w):
        if 'building' in w.tags:
            self.building_count += 1

    def relation(self, r):
        if 'building' in r.tags:
            self.building_count += 1

class Edge:
    def __init__(self):
        self.lnode = None
        self.rnode = None
        self.deleted = False # For pointer reasons

    def remove(self):
        self.lnode.edges.remove(self)
        self.rnode.edges.remove(self)
        self.lnode = None
        self.rnode = None

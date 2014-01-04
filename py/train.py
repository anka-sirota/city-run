import helpers
bgl = helpers.bgl
gdict = bgl.globalDict
DELTA = 5.0


def along_path(path):
    for point in path:
        yield point


class Train(object):
    def __init__(self, obj):
        self.navmesh = helpers.get_object(obj['navmesh'])
        self.station_to = helpers.get_object(obj['station_to'])
        self.station_from = helpers.get_object(obj['station_from'])
        self.obj = obj
        self.minipath = []
        self.path = None
        print('Train %s initialized' % self.obj)

    def get_position(self):
        return self.obj.position

    def set_position(self, v):
        self.obj.position = v
    position = property(get_position, set_position)

    def get_vector_to(self, position):
        vector = position - self.position
        delta = vector.length
        return delta, vector

    def move_to(self, point, align=False):
        delta, vector = self.get_vector_to(point)
        self.obj.applyMovement((vector[0], vector[1], 0))
        if align:
            self.obj.alignAxisToVect((vector[0], vector[1], 0), 0, 1)
        return delta

    def move(self):
        if not self.path:
            return
        if not self.minipath:
            try:
                point = next(self.path)
            except StopIteration:
                self.path = None
                return
            delta, vector = self.get_vector_to(point)
            self.minipath = [self.position + i * (vector / delta) for i in reversed(range(1, int(delta + 1)))]
        self.move_to(self.minipath.pop(), True)

    def depart(self):
        #print('Checking departure: %s' % self.obj)
        if self.position == self.station_to.position or not self.path:
            self.position = self.station_from.position
            path = self.navmesh.findPath(self.position, self.station_to.position)
            self.path = along_path(path)
            self.minipath = []
            #print('Train %s departed' % self.obj)


class Railway(object):
    def __init__(self):
        # initialize all trains
        self.obj = bgl.getCurrentController().owner
        self.trains = []
        for obj in self.obj.children:
            self.trains.append(Train(obj))

    def depart(self):
        for train in self.trains:
            train.depart()

    def run(self):
        # move every train there is
        for train in self.trains:
            train.move()

railway = Railway()
run = railway.run
depart = railway.depart

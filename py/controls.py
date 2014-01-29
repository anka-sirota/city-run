from bge import logic as G
from bge import render as R
from bge import events as E
from mathutils import Vector
from helpers import get_object

ACTIVATED = G.KX_INPUT_JUST_ACTIVATED
#RELEASED = G.KX_INPUT_JUST_RELEASED
ACTIVE = G.KX_INPUT_ACTIVE
#INACTIVE = G.KX_INPUT_NONE
scene = G.getCurrentScene()
MAX_FLY_HEIGHT = 30.0

# KEY BINDINGS
kbleft = E.AKEY
kbright = E.DKEY
kbup = E.WKEY
kbdown = E.SKEY
kbascend = E.SPACEKEY


def start_game(walk=False):
    print('Setting up the camera')
    camera.setParent(ply, False)
    scene.active_camera = camera
    movement_controls.init()
    movement_controls.view_toggle(True)


class MovementControl(object):
    def __init__(self):
        print('MovementControl', scene)
        self.init()

    def init(self):
        self.update_screen_size()
        self.sensitivity = 0.0005
        self.smooth = 0.7
        self.obj = ply
        R.setMousePosition(self.w + 2, self.h + 1)
        self.x = self.obj.localOrientation.to_euler().x
        self.y = self.obj.localOrientation.to_euler().y

    def view_toggle(self, to_state=None):
        if to_state is not None:
            self.cabin_view = not to_state
        if self.cabin_view:
            camera.localPosition = (-5, 0, 1)
            self.cabin_view = False
        else:
            camera.localPosition = (0, 0, 0)
            self.cabin_view = True

    def update_screen_size(self):
        self.W = R.getWindowWidth()
        self.H = R.getWindowHeight()
        self.size = Vector((self.W, self.H))
        self.w = self.W // 2
        self.h = self.H // 2
        self.screen_center = (self.w, self.h)

    def apply_cap(self):
        self.cap = 1
        if self.y < - self.cap:
            self.y = - self.cap
        if self.y > self.cap:
            self.y = self.cap

    def update(self):
        scrc = Vector(self.screen_center)
        _pos = Vector(G.mouse.position)
        mpos = Vector((_pos.x * self.size.x, _pos.y * self.size.y))

        self.x += (scrc.x - mpos[0]) * self.sensitivity
        self.y += (scrc.y - mpos[1]) * self.sensitivity
        self.apply_cap()

        # set the values
        ori = self.obj.localOrientation.to_euler()
        ori.y = - self.y
        ori.z = self.x
        self.obj.localOrientation = ori.to_matrix()

        # Center mouse in game window
        R.setMousePosition(*self.screen_center)

        face_vect = self.obj.getAxisVect((1, 0, 0))
        if abs(self.obj.worldPosition.z) > MAX_FLY_HEIGHT:
            self.obj.applyImpulse(self.obj.position, (0, 0, - self.obj.worldPosition.z))
            return

        if G.keyboard.events[kbdown]:
            self.obj.localLinearVelocity *= 0.01
        if G.keyboard.events[kbup]:
            self.obj.applyImpulse(self.obj.position,
                                  (5 * face_vect.x, 5 * face_vect.y, 30 * face_vect.z))


def change_focus(cont):
    mevents = G.mouse.events
    #if mousewheel moves down, bring focus closer
    if mevents[E.WHEELDOWNMOUSE] in (ACTIVE, ACTIVATED):
        camera['focalDepth'] -= 0.005
    #if mousewheel moves up, make focus further
    if mevents[E.WHEELUPMOUSE] in (ACTIVE, ACTIVATED):
        camera['focalDepth'] += 0.005
    camera['focalDepth'] = camera['focalDepth'] < 0.1 and 0.1 or camera['focalDepth']
    camera['focalDepth'] = camera['focalDepth'] > 1.0 and 1.0 or camera['focalDepth']

scene = G.getCurrentScene()
if scene.name == 'City':
    camera = get_object('camera')
    cont = G.getCurrentController()
    ply = cont.owner
    movement_controls = MovementControl()
    G.addScene('HUD', 1)

    def update():
        movement_controls.update()

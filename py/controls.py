from bge import logic as G
from bge import render as R
from bge import events as E
from mathutils import Vector
from helpers import get_object  # , search_object

ACTIVATED = G.KX_INPUT_JUST_ACTIVATED
RELEASED = G.KX_INPUT_JUST_RELEASED
ACTIVE = G.KX_INPUT_ACTIVE
INACTIVE = G.KX_INPUT_NONE
scene = G.getCurrentScene()

# KEY BINDINGS
kbleft = E.AKEY
kbright = E.DKEY
kbup = E.WKEY
kbdown = E.SKEY


def start_game(walk=False):
    print('Setting up the camera')
    yaw.setParent(ply, False)
    camera.setParent(yaw, False)
    camera.position = (0, 0, 0)
    scene.active_camera = camera


class MovementControl(object):
    def __init__(self):
        print('MovementControl', scene)
        #self.speed = 0.08
        self.sensitivity = 0.002
        self.smooth = 0.7
        self.obj = cont.owner
        self.update_screen_size()
        # center mouse on first frame, create temp variables
        R.setMousePosition(self.w + 2, self.h + 1)
        self.old_x = 0.0
        self.old_y = 0.0
        self.moveinit = 1
        self.mx = 0.0
        self.my = 0.0
        self.accel = 2.0
        self.maxspd = 5.0
        self.friction = 0.75
        self.movelocal = 1

    def update_screen_size(self):
        self.W = R.getWindowWidth()
        self.H = R.getWindowHeight()
        self.size = Vector((self.W, self.H))
        self.w = self.W // 2
        self.h = self.H // 2
        self.screen_center = (self.w, self.h)

    def update(self):
        kevents = G.keyboard.events
        scrc = Vector(self.screen_center)
        _pos = Vector(G.mouse.position)
        mpos = Vector((_pos.x * self.size.x, _pos.y * self.size.y))

        x = scrc.x - mpos[0]
        y = scrc.y - mpos[1]

        # Smooth movement
        self.old_x = (self.old_x * self.smooth + x * (1.0 - self.smooth))
        self.old_y = (self.old_y * self.smooth + y * (1.0 - self.smooth))

        x = self.old_x * self.sensitivity
        y = self.old_y * self.sensitivity

        # set the values
        self.obj.applyRotation([0, 0, x], False)
        yaw.applyRotation([0, - y, 0], True)

        # Center mouse in game window
        R.setMousePosition(*self.screen_center)

        if kevents[kbleft]:
            self.mx += self.accel
        elif kevents[kbright]:
            self.mx -= self.accel
        else:
            self.mx *= self.friction

        if kevents[kbup]:
            self.my += self.accel
        elif kevents[kbdown]:
            self.my -= self.accel
        else:
            self.my *= self.friction

        # Clamping
        if self.mx > self.maxspd:
            self.mx = self.maxspd
        elif self.mx < -self.maxspd:
            self.mx = -self.maxspd

        if self.my > self.maxspd:
            self.my = self.maxspd
        elif self.my < -self.maxspd:
            self.my = -self.maxspd

        # Actual movement
        self.obj.setLinearVelocity([self.my, self.mx, self.obj.getLinearVelocity()[2]], self.movelocal)


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
    yaw = get_object('player_yaw')
    ply = cont.owner
    movement_controls = MovementControl()
    G.addScene('HUD', 1)

    def update():
        movement_controls.update()

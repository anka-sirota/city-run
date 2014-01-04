from bge import logic as G
from bge import render as R
from bge import events as E
from mathutils import Vector
from helpers import get_object  # , search_object

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
    yaw.setParent(ply, False)
    camera.setParent(yaw, False)
    camera.position = (0, 0, 0)
    scene.active_camera = camera
    if walk:
        movement_controls.can_fly = False
        movement_controls.maxspd = 5.0
        movement_controls.sensitivity = 0.002


class MovementControl(object):
    def __init__(self):
        print('MovementControl', scene)
        self.update_screen_size()
        #self.speed = 0.08
        self.sensitivity = 0.0005
        self.smooth = 0.7
        self.obj = cont.owner
        # center mouse on first frame, create temp variables
        R.setMousePosition(self.w + 2, self.h + 1)
        self.old_x = 0.0
        self.old_y = 0.0
        self.mx = 0.0
        self.my = 0.0
        self.mz = 0.0
        self.accel = 3.0
        self.initial_v_z = 1.5
        self.accel_z = 1.1
        self.maxspd = 25.0
        self.friction = 0.75
        self.friction_z = 0.85
        self.movelocal = 1
        self.can_fly = True

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

        self.mz = self.obj.localLinearVelocity.z
        if self.can_fly:
            if kevents[kbascend] \
               and abs(self.mz) < self.maxspd \
               and self.obj.worldPosition.z < MAX_FLY_HEIGHT:
                self.mz = max(self.mz, self.initial_v_z)
                print('Ascending', self.obj.position.z, self.obj.worldPosition.z)
                self.mz *= self.accel_z
                self.mz *= self.friction_z

        # Clamping
        if self.mx > self.maxspd:
            self.mx = self.maxspd
        elif self.mx < -self.maxspd:
            self.mx = -self.maxspd

        if self.my > self.maxspd:
            self.my = self.maxspd
        elif self.my < -self.maxspd:
            self.my = -self.maxspd

        if self.mz > self.maxspd:
            self.mz = self.maxspd
        elif self.mz < -self.maxspd:
            self.mz = -self.maxspd

        # Actual movement
        self.obj.setLinearVelocity((self.my, self.mx, self.mz), self.movelocal)


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

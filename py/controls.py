from bge import logic as G
from bge import render as R
from bge import events as E
from mathutils import Vector
from helpers import get_object
import math

ACTIVATED = G.KX_INPUT_JUST_ACTIVATED
#RELEASED = G.KX_INPUT_JUST_RELEASED
ACTIVE = G.KX_INPUT_ACTIVE
#INACTIVE = G.KX_INPUT_NONE
scene = G.getCurrentScene()
MAX_FLY_HEIGHT = 30.0

# KEY BINDINGS
kbup = E.WKEY
kbdown = E.SKEY
kbleft = E.AKEY
kbright = E.DKEY
kb_rleft = E.LEFTARROWKEY
kb_rright = E.RIGHTARROWKEY
kb_pup = E.UPARROWKEY
kb_pdown = E.DOWNARROWKEY


class MovementControl(object):
    def __init__(self):
        print('MovementControl', scene)
        self.init()

    def init(self):
        self.base_torq = 25
        self.minpower = 40.0
        self.power = 0.0
        self.maxpower = 120.0
        self.maxspeed = 15.0
        self.vspeed = 0.0
        self.speed = 0.0
        self.lift = 0.0
        self.maxlift = 100.0
        self.pitch = 0.0
        self.thrust = 0.0
        self.bank = 0.0
        self.thrustpitchfactor = 0.0
        self.status = ''
        self.crashed = False
        self.rollfactor = 0.6
        self.rolltorq = 0
        self.pitchfactor = 16.0
        self.pitchtorq = 0.0
        self.yawfactor = 1.0
        self.yawtorq = 1.0
        self.onground = False

        self.obj = ply
        self.cont = cont
        self.keeper = scene.objects["camerakeeper"]

    def update(self):
        self.keeper.worldPosition = self.obj.worldPosition
        matrix_rotation = self.obj.worldOrientation
        euler_rotation = matrix_rotation.to_euler()
        degrees_rotation = [math.degrees(a) for a in euler_rotation]

        pitch = int(degrees_rotation[0])
        bank = int(degrees_rotation[1])
        #yaw = int(degrees_rotation[2])

        self.pitch = pitch
        self.bank = bank

        pitchcube = scene.objects["pitchcube"]
        thrustpitchfactor = pitchcube.worldPosition[2] - self.obj.worldPosition[2]
        self.thrustpitchfactor = thrustpitchfactor * 10

        localvelocity = self.obj.getLinearVelocity(True)
        worldvelocity = self.obj.getLinearVelocity(False)

        speed = localvelocity[1]
        vspeed = worldvelocity[2]
        self.speed = speed
        self.vspeed = vspeed

        key = G.keyboard.events

        if self.crashed is False:
            lift = localvelocity[1] * 9.7
            self.thrust = self.power
            self.thrust = self.thrust - self.thrustpitchfactor
            if lift < 0:
                lift = 0
            if lift > self.maxlift:
                lift = self.maxlift
            self.lift = lift
            self.obj.applyForce([0, 0, lift], 0)

            if self.power < self.minpower:
                self.power = self.minpower

            if key[kbup] == 2:
                if self.power < self.maxpower:
                    self.power += 1
            if key[kbdown] == 2:
                if self.power > self.minpower:
                    self.power -= 1

            self.obj.applyForce([0, self.thrust, 0], 1)
            self.thrust = self.thrust - self.thrustpitchfactor
            if self.onground is False:
                if self.thrust < 60:
                    self.thrust = 60
            self.rolltorq = self.rollfactor * self.speed
            if self.rolltorq < 4:
                self.rolltorq = 4
            self.pitchtorq = self.pitchfactor - self.speed
            if self.pitchtorq < 4:
                self.pitchtorq = 4

            self.yawtorq = (self.power / 10) - self.yawfactor - self.speed
            if self.onground is True:
                if self.yawtorq < 18:
                    self.yawtorq = 18
            if self.onground is False:
                if self.yawtorq < 9:
                    self.yawtorq = 9
            torq = self.base_torq - self.speed
            if key[kb_rleft] == 2:
                self.obj.applyTorque([0.0, - self.rolltorq * 2, 0.0], 1)
            if key[kb_rright] == 2:
                self.obj.applyTorque([0.0, self.rolltorq * 2, 0.0], 1)
            if key[kb_pup] == 2:
                self.obj.applyTorque([- self.pitchtorq / 1.5, 0.0, 0.0], 1)
            if key[kb_pdown] == 2:
                self.obj.applyTorque([self.pitchtorq / 1.5, 0.0, 0.0], 1)
            if key[kbleft] == 2:
                self.obj.applyTorque([0.0, 0.0, torq], 1)
            if key[kbright] == 2:
                self.obj.applyTorque([0.0, 0.0, - torq], 1)
            if bank < 0 and bank > -180.0001:
                self.obj.applyTorque([0.0, 0.0, - bank / 15], 1)
                self.obj.applyTorque([0.0, -bank / 12, 0.0], 1)
            if bank > 0 and bank < 180.0001:
                self.obj.applyTorque([0.0, 0.0, - bank / 15], 1)
                self.obj.applyTorque([0.0, -bank / 12, 0.0], 1)
            if pitch > 0.001 and pitch < 90:
                self.obj.applyTorque([- pitch / 12, 0.0, 0.0], 1)
            if pitch < 0.001 and pitch > -90:
                self.obj.applyTorque([- pitch / 12, 0.0, 0.0], 1)


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
    camera = get_object('Camera')
    scene.active_camera = camera
    cont = G.getCurrentController()
    ply = cont.owner
    movement_controls = MovementControl()
    G.addScene('HUD', 1)

    def update():
        movement_controls.update()

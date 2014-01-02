from bge import logic as G
from bge import render as R
from bge import events
from mathutils import Vector
ACTIVATED = G.KX_INPUT_JUST_ACTIVATED
RELEASED = G.KX_INPUT_JUST_RELEASED
ACTIVE = G.KX_INPUT_ACTIVE
INACTIVE = G.KX_INPUT_NONE
from helpers import get_object
DEBUG = True
mouse = G.mouse
mouse_events = mouse.events
keyboard = G.keyboard

cont = G.getCurrentController()
camera = get_object("camera")
yaw = get_object("player_yaw")
ply = cont.owner
print("Setting up the camera")
yaw.setParent(ply, False)
camera.setParent(yaw, False)
camera.position = (0, 0, 0)
G.getCurrentScene().active_camera = camera


def mouse_look(cont):
    #Blender Game Engine 2.55 Simple Camera Look
    #Created by Mike Pan: mikepan.com

    # Use mouse to look around
    # W,A,S,D key to walk around
    # E and C key to ascend and decend

    #speed = 0.08				# walk speed
    sensitivity = 0.002		# mouse sensitivity
    smooth = 0.7			# mouse smoothing (0.0 - 0.99)

    owner = cont.owner
    Mouse = cont.sensors["Mouse"]

    w = R.getWindowWidth()//2
    h = R.getWindowHeight()//2
    screen_center = (w, h)

    # center mouse on first frame, create temp variables
    if "oldX" not in owner:
        print("oldX" not in owner)
        R.setMousePosition(w + 1, h + 1)
        owner["oldX"] = 0.0
        owner["oldY"] = 0.0
    else:

        scrc = Vector(screen_center)
        mpos = Vector(Mouse.position)

        x = scrc.x-mpos.x
        y = scrc.y-mpos.y

        # Smooth movement
        owner['oldX'] = (owner['oldX']*smooth + x*(1.0-smooth))
        owner['oldY'] = (owner['oldY']*smooth + y*(1.0-smooth))

        x = owner['oldX'] * sensitivity
        y = owner['oldY'] * sensitivity

        # set the values
        owner.applyRotation([0, 0, x], False)
        yaw.applyRotation([0, -y, 0], True)

        # Center mouse in game window
        R.setMousePosition(*screen_center)

    keyboard = G.keyboard.events

    # KEY BINDINGS

    kbleft = events.AKEY  # Replace these with others, if you wish
    kbright = events.DKEY  # An example would be 'events.WKEY, DKEY, SKEY, and AKEY
    kbup = events.WKEY
    kbdown = events.SKEY

    ##################

    if not 'moveinit' in owner:
        owner['moveinit'] = 1
        owner['mx'] = 0.0
        owner['my'] = 0.0
        owner['accel'] = 2.0      # Acceleration
        owner['maxspd'] = 5.0    # Top speed
        owner['friction'] = 0.75   # Friction percentage; set to 0.0 for immediate stop
        owner['movelocal'] = 1    # Move on local axis?

    if keyboard[kbleft]:
        owner['mx'] += owner['accel']
    elif keyboard[kbright]:
        owner['mx'] -= owner['accel']
    else:
        owner['mx'] *= owner['friction']

    if keyboard[kbup]:
        owner['my'] += owner['accel']
    elif keyboard[kbdown]:
        owner['my'] -= owner['accel']
    else:
        owner['my'] *= owner['friction']

    # Clamping
    if owner['mx'] > owner['maxspd']:
        owner['mx'] = owner['maxspd']
    elif owner['mx'] < -owner['maxspd']:
        owner['mx'] = -owner['maxspd']

    if owner['my'] > owner['maxspd']:
        owner['my'] = owner['maxspd']
    elif owner['my'] < -owner['maxspd']:
        owner['my'] = -owner['maxspd']

    # Actual movement
    owner.setLinearVelocity([owner['my'], owner['mx'], owner.getLinearVelocity()[2]], owner['movelocal'])


def change_focus(cont):
    #if mousewheel moves down, bring focus closer
    if G.mouse.events[events.WHEELDOWNMOUSE] in (ACTIVE, ACTIVATED):
        camera["focalDepth"] -= 0.005
    #if mousewheel moves up, make focus further
    if G.mouse.events[events.WHEELUPMOUSE] in (ACTIVE, ACTIVATED):
        camera["focalDepth"] += 0.005
    camera["focalDepth"] = camera["focalDepth"] < 0.1 and 0.1 or camera["focalDepth"]
    camera["focalDepth"] = camera["focalDepth"] > 1.0 and 1.0 or camera["focalDepth"]

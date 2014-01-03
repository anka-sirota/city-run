from helpers import search_object
import controls
from bge import events as E
from bge import logic as G
from bge import render as R
ACTIVATED = G.KX_INPUT_JUST_ACTIVATED
RELEASED = G.KX_INPUT_JUST_RELEASED
ACTIVE = G.KX_INPUT_ACTIVE
INACTIVE = G.KX_INPUT_NONE

R.setMousePosition(R.getWindowWidth()//2, R.getWindowHeight()//2)
cursor = search_object('cursor')
mouse = cursor.sensors['mouse_over']
menu_highlight = search_object('menu_highlight')
mouse_button = cursor.sensors['mouse_button']


def update():
    cursor.localPosition = mouse.raySource
    obj = mouse.hitObject
    if obj and 'highlight' in obj and obj['highlight']:
        menu_highlight.localPosition = obj.position
        menu_highlight.localPosition.z = obj.position.z - 1.0
        menu_highlight.setVisible(True)
        if mouse.getButtonStatus(E.LEFTMOUSE) == RELEASED \
           and 'start_game' in obj:
            print('mouse button', obj)
            if obj.name == 'choose_walk':
                controls.start_game()
            elif obj.name == 'choose_exit':
                G.endGame()

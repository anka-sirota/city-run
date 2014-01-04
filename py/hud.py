from helpers import search_object, get_object
import controls
from bge import events as E
from bge import logic as G
from bge import render as R
RELEASED = G.KX_INPUT_JUST_RELEASED
R.setMousePosition(R.getWindowWidth()//2, R.getWindowHeight()//2)


class HUD(object):
    def __init__(self):
        self.is_open = False
        # hotkeys
        self.kh_menu = E.QKEY
        self.kh_view_toggle = E.ZKEY
        # 
        self.cursor = search_object('cursor')
        self.mouse = self.cursor.sensors['mouse_over']
        self.menu_highlight = get_object('menu_highlight')
        self.camera = search_object('camera')
        self.scene = G.getCurrentScene()
        self.menu = search_object('hud_menu')
        if not self.menu or not self.menu_highlight:
            raise Exception('Cannot proceed')
        print('HUD', self.scene)
        self.toggle_menu(True)

    def toggle_menu(self, to_state=None):
        if to_state is not None:
            self.is_open = not to_state
        scenes = {_.name: _ for _ in G.getSceneList()}
        if self.is_open:
            #scenes['HUD'].suspend()
            if 'City' in scenes:
                scenes['City'].resume()
            self.menu.setVisible(False, True)
            if self.camera:
                self.camera['focalDepth'] = 1.0
            self.is_open = False
        else:
            if 'City' in scenes:
                scenes['City'].suspend()
            G.addScene('HUD', 1)
            if self.camera:
                self.camera['focalDepth'] = 0.1
            self.menu.setVisible(True, True)
            scenes['HUD'].resume()
            self.is_open = True

    def update(self):
        if not self.is_open:
            # menu's not open, listen to in-game hotkeys
            if G.keyboard.events[self.kh_menu] == RELEASED:
                self.toggle_menu()
            elif G.keyboard.events[self.kh_view_toggle] == RELEASED:
                controls.movement_controls.view_toggle()
            return
        # menu is open
        self.cursor.localPosition = self.mouse.raySource
        obj = self.mouse.hitObject
        if obj and 'highlight' in obj and obj['highlight']:
            self.menu_highlight.localPosition = obj.position
            self.menu_highlight.localPosition.z = obj.position.z - 1.0
            self.menu_highlight.setVisible(True)
            if E.LEFTMOUSE in G.mouse.active_events and 'start_game' in obj:
                print('mouse button', obj)
                if obj.name == 'choose_fly':
                    try:
                        controls.start_game()
                        self.toggle_menu(False)
                    except Exception as e:
                        print(e)
                elif obj.name == 'choose_walk':
                    try:
                        controls.start_game(walk=True)
                        self.toggle_menu(False)
                    except Exception as e:
                        print(e)
                elif obj.name == 'choose_exit':
                    G.endGame()


hud = HUD()


def update():
    hud.update()

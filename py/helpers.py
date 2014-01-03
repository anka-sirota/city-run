import bge
bgl = bge.logic

get_object = lambda name: bgl.getCurrentScene().objects[name]


def search_object(name):
    try:
        return get_object(name)
    except Exception:
        for scene in bgl.getSceneList():
            print(scene, name, scene.objects)
            if name in scene.objects:
                return scene.objects[name]
    return None

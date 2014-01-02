import bge
bgl = bge.logic

get_object = lambda name: bgl.getCurrentScene().objects[name]

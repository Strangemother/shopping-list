from g62 import Connections, Node, Edge, enums, ExitNode

g = Connections()

def mycaller(*a, parent, uuid, direction, **kw):
    print('mycaller', a, kw)
    return 'sausages'

g.connect(*'AP', edge=mycaller)
g.connect(*'ABA')
g.connect(*'TT')


a = g('A')

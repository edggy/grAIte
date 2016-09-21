#!python
import os.path as path
import json
import pickle
import cherrypy
from ws4py.websocket import WebSocket
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from socket import error as socket_error

from PIL import Image, ImageFont, ImageDraw

delimeter = '\t'
worldFile = 'world.pkl'
world = {}
try:
    with open(worldFile, mode='r') as f:
        world = pickle.load(f)
except (pickle.UnpicklingError, EOFError) as e:
    print e

clients = set({})

def saveWorld(fileName = None):
    if fileName == None:
        fileName = worldFile
        
    with open(fileName, mode='w') as f:
        pickle.dump(world, f)

class ServerWebSocket(WebSocket):
    def opened(self):
        clients.add(self)
        
    def closed(self, code, reason=None):
        clients.remove(self)
        
    def received_message(self, message):
        print 'received_message:\t' + str(message)
        try:
            toks = str(message).split(delimeter)
            
            if toks[0] == 'get':
                request = json.loads(toks[1])
                startX = int(request['startX'])
                startY = int(request['startY'])
                endX = int(request['endX'])
                endY = int(request['endY'])
                
                data = {}
                
                for x in range(startX, endX):
                    for y in range(startY, endY):
                        if (x, y) in world:
                            if x not in data:
                                data[x] = {}
                            if 'color' in world[(x, y)] and world[(x, y)]['color'] == '#FFFFFF':
                                continue
                            data[x][y] = world[(x, y)]
                    if x in data and len(data[x]) == 0:
                        del data[x]
                
                
                self.send('set' + delimeter + json.dumps(data))
                #print 'sent:\t' + 'set' + delimeter + json.dumps(data)
            
            elif toks[0] == 'set':
                data = json.loads(toks[1])
                x = int(data['x'])
                y = int(data['y'])
                color = data['color']
                
                
                if (x,y) not in world:
                    world[(x,y)] = {}
                    
                
                world[(x,y)]['color'] = color
                
                if world[(x,y)]['color'] == '' or world[(x,y)]['color'] == '#FFFFFF':
                    world[(x,y)].pop('color', None)
                    if len(world[(x,y)]) == 0:
                        del world[(x,y)]
                else:
                    newData = {}
                    newData[x] = {}
                    newData[x][y] = {}
                    newData[x][y]['color'] = color
                    
                    for client in clients:
                        if client != self:
                            client.send('set' + delimeter + json.dumps(newData))
                            
                    #print 'sent:\t' + 'set'
                saveWorld()
                    
        except (ValueError, TypeError, socket_error) as e:
            print e
        

class Root:
    @cherrypy.expose
    def index(self):
        
        with open('paint.html') as f:
            htmlData = f.read()
        return htmlData
    
    @cherrypy.expose
    def ws(self):
        # you can access the class instance through
        handler = cherrypy.request.ws_handler    
        
    @cherrypy.expose
    def reset(self):
        world.clear()
        saveWorld()
        return self.index()
    
    @cherrypy.expose
    def text(self, **params):
        #print params
        try:
            default = {'data':'', 'x':0, 'y':0, 'size':5, 'color':'#000000', 'font':'arialbd.ttf', 'trans':0}
            
            for k in default:
                if k not in params:
                    params[k] = default[k]
                    
            if '.' not in params['font']:
                params['font'] += '.ttf'
            
            if '#' not in params['color']:
                params['color'] = '#' + params['color']
            
            font = ImageFont.truetype(params['font'], int(params['size'])) #load the font
            size = font.getsize(params['data'])  #calc the size of text in pixels
            size = (size[0], (size[1] + 2) * (params['data'].count('\n') + 1))
            image = Image.new('1', size, 1)  #create a b/w image
            draw = ImageDraw.Draw(image)
            draw.text((0, 0), params['data'], font=font) #render the text to the bitmap
            for rownum in range(size[1]): 
            #scan the bitmap:
            # print ' ' for black pixel and 
            # print '#' for white one
                for colnum in range(size[0]):
                    loc = (colnum + int(params['x']) , rownum + int(params['y']))
                    if loc not in world:
                        world[loc] = {}
                        
                    if image.getpixel((colnum, rownum)): 
                        if int(params['trans']) <= 0:
                            world[loc]['color'] = '#FFFFFF'
                    else: 
                        world[loc]['color'] = params['color']   
        except IOError:
            pass
        
        return self.index()

if __name__ == '__main__':

    current_dir = path.dirname(path.abspath(__file__))
    
    cherrypy.config.update({'server.socket_port': 80})
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()    

    # Set up site-wide config first so we get a log if errors occur.
    cherrypy.config.update({'environment': 'production',
                            'log.error_file': 'site.log',
                            'log.screen': True})

    conf = {'/': {'tools.staticdir.on': True,
                  'tools.staticdir.dir': path.join(current_dir, 'datafiles')},
            '/ws': {'tools.websocket.on': True,
                    'tools.websocket.handler_cls': ServerWebSocket},
            '/paint.js': {'tools.staticfile.on': True,
                          'tools.staticfile.filename': path.join(current_dir, 'paint.js')}}

    cherrypy.quickstart(Root(), '/', config=conf)


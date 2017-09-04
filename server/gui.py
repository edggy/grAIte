import Tkinter as tk
import threading
import time
from PIL import Image, ImageTk
from collections import defaultdict
import math

from world import World
from Vector.vector import Vector
import constants
from actor import PastActor

def toTag(loc, y = None):
    if y is None:
        return '<%s,%s>' % (loc.x, loc.y)
    else:
        x = loc
        return '<%s,%s>' % (x, y)

def fromTag(tag, tick = 0):
    loc = map(int, tag[1:-1].split(',')) + [tick]
    return Vector(*loc)

class Timer(threading.Thread):
    def __init__(self, sleepTime, fun, args = (), kwargs = {}):
        threading.Thread.__init__(self)
        self.time = sleepTime
        self.fun = fun
        self.args = args
        self.kwargs = kwargs
        self.state = 'running'
        self.lastRun = 0
        self.nextRun = 0
        self.pauseTime = 0
        
    def run(self):
        self.nextRun = time.time() + self.time
        while self.state != 'stopped':
            delta = self.nextRun - time.time()
            if delta > 0:
                time.sleep(delta)
            if self.state == 'running' and time.time() >= self.nextRun:
                self.fun(*self.args, **self.kwargs)
                self.lastRun = time.time()
                self.nextRun = self.lastRun + self.time
                
    
    def pause(self, pauseTimer = None):
        if self.state != 'paused':
            self.state = 'paused'
            self.pauseTime = time.time()
            if pauseTimer is not None:
                threading.Timer(pauseTimer, self.unpause).start()
            
    def unpause(self):
        if self.state == 'paused':
            self.state = 'running'
            self.nextRun += time.time() - self.pauseTime
            
    def toggle(self, pauseTimer = None):
        if self.state == 'paused':
            self.unpause()
        else:
            self.pause(pauseTimer)
            
    def stop(self):
        self.state = 'stopped'
        self.join()
        

class GUI(object):
    '''@property
    def _tick(self):
        return self.world._tick + self.timeOffset'''
    
    def __init__(self, world):
        fontName = "Sans Serif"
        largeFontSize = 32
        smallFontSize = 12        
        tickTime = 1.0
        startPaused = True

        self.root = tk.Tk()
        
        self.world = world
        #self.worldLock = threading.RLock()
        #self.gridLock = threading.RLock()
        
        def hello():
            print "hello!"
        
        menubar = tk.Menu(self.root)
        self.root.minsize(800, 600)
        
        self.root.bind("<Key>", self.keypress)
        self.root.protocol("WM_DELETE_WINDOW", self.__del__)
        
        # create a pulldown menu, and add it to the menu bar
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=hello)
        filemenu.add_command(label="Save", command=hello)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.__del__)
        menubar.add_cascade(label="File", menu=filemenu)
        
        # create more pulldown menus
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Cut", command=hello)
        editmenu.add_command(label="Copy", command=hello)
        editmenu.add_command(label="Paste", command=hello)
        menubar.add_cascade(label="Edit", menu=editmenu)
        
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=hello)
        menubar.add_cascade(label="Help", menu=helpmenu)
        
        # display the menu
        self.root.config(menu=menubar)
        
        self.pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, opaqueresize=False)
        self.pane.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        
        self.viewport = tk.Canvas(self.pane, background="white")
        #self.viewport.config(background="white")
        
        #self.viewport.pack(fill=tk.BOTH, expand=tk.YES)
        self.pane.add(self.viewport, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        self.viewport.bind('<Configure>', self.drawGrid)
        self.viewport.bind("<Button-1>", self.clickGrid)
        self.viewport.bind("<<Redraw>>", self.redraw)
        
        self.cellInfo = {}
        self.cellInfo['infoport'] = tk.StringVar()
        self.infoportLabel = tk.Label(self.pane, textvariable=self.cellInfo['infoport'], font=("Sans Serif", 44), background="white")
        
        self.infoport = tk.LabelFrame(self.pane, background="white", font=("Sans Serif", 44), labelanchor='n', labelwidget=self.infoportLabel)
        #self.viewport.config(cnf=None, background="white")
        
        self.pane.add(self.infoport)
        self.root.update_idletasks()
        self.pane.update_idletasks()
        #self.pane.sash_place(0, 800, 600)
        
        labelOrder = ['loc', 'food', 'pheromone', 'actorID', 'energy', 'IP', 'sentence', 'status']

        self.cellInfoView = {}
        
        for label in labelOrder:
            self.cellInfo[label] = tk.StringVar()
            self.cellInfoView[label] = tk.Label(self.infoport, textvariable=self.cellInfo[label], font=(fontName, largeFontSize), background="white")
            self.cellInfoView[label].pack(fill='x')
        
        self.cellInfo['infoport'].set('Tick: %s' % 0)
        self.cellInfo['loc'].set('Cell: None')
        self.cellInfo['food'].set('Food: None')
        self.cellInfoView['sentence'].config(font=(fontName, smallFontSize))
        self.cellInfoView['status'].config(font=(fontName, smallFontSize))
        
        self.antTag = 'Ant'
        self.lineTag = 'Line'
        self.rectTag = 'Rect'
        
        self.lastClick = ''
        self.lastClickBackup = None
        self.undoClick = {}
        self.noRedraw = set()
        
        def autoTick():
            self.tick()
            ahead = self.world._tick - self._tick
            if ahead > 100:
                self.auto.time = tickTime
            else:
                self.auto.time = max(2.0 * self.timeData['sum'] / self.timeData['count'], tickTime)
        
        self.auto = Timer(tickTime, autoTick)
        self.auto.start()
        if startPaused:
            self.auto.pause()
            
        self.autoGen = Timer(1, self.genWorld)
        self.autoGen.start()        
        
        self.images = {}
        self.status = defaultdict(lambda: ['white', None])
        
        self.deltaGridSize = Vector(1,1)
        #self.deltaOffset = Vector(Vector(1,0), Vector(0,1))
        
        self.gridSize = Vector(45, 45)
        self.newGridSize = Vector(self.gridSize)
        self.canvasSize = Vector(0,0)
        self.numCells = Vector(0,0)
        self.offset = Vector(self.gridSize)
        self.cellOffset = Vector(-2,-2)
        
        self._tick = 0
        
        self.delta = {0:0}
        self.timeData = defaultdict(int)
        self.verbose = True
        
    def realLocToCellLoc(self, loc):
        # converts a point on the screen to the cell location
        
        loc = Vector((loc.x - self.offset.x)/self.gridSize.x, ((self.canvasSize.y - loc.y) - self.offset.y)/self.gridSize.y)
        return loc + self.cellOffset
        
    def cellLocToRealLoc(self, loc):
        # converts a cell location to its location on the screen (the upper left most point)
        # self.viewport.canvasy
        
        loc = Vector(loc - self.cellOffset)
        
        return Vector(loc.x*self.gridSize.x + self.offset.x, self.canvasSize.y-((loc.y+1)*self.gridSize.y + self.offset.y))
    
    def cellLocToGridLoc(self, loc):
        return Vector(loc[0], loc[1], self._tick)
        
    def drawCell(self, x, y):
        '''
        x and y are cell indexes
        '''
    
        loc = Vector(x+self.cellOffset.x, y+self.cellOffset.y, self._tick)           
        tag = toTag(loc)
        realLoc = Vector(x*self.gridSize, self.viewport.canvasy(self.canvasSize[1])-(y+1)*self.gridSize)
        bbox = (realLoc.x,realLoc.y,realLoc.x+self.gridSize-1,realLoc.y+self.gridSize-1)
        
        if (bbox[0] <= self.canvasSize[0] or bbox[1] <= self.canvasSize[1] or bbox[2] >= 0 or bbox[3] >= 0) and tag not in self.noRedraw:
            gridCell = self.viewport.find_withtag(tag)
                
            needRedraw = gridCell == () or map(int,self.viewport.coords(gridCell[0])) != map(int,bbox)
            
            #color = 'white'
            image = None
            rotation = None
            #with self.worldLock:
            if loc in self.world.grid:
                cell = self.world.grid[loc]
                actor = cell.actor
                if actor is not None:
                    rotation = constants.DIRECTIONS_VEC_ROT[actor.direction]
                    
                    if actor.direction not in self.images:
                        image = Image.open('ant.png')
                        
                        basewidth = int(self.gridSize*0.9)
                        #wpercent = (basewidth / float(image.size[0]))
                        #hsize = int((float(image.size[1]) * float(wpercent)))
                        image = image.resize((basewidth, basewidth), Image.ANTIALIAS)    
                        image = image.rotate(rotation)
                        image = ImageTk.PhotoImage(image)
                    
                        self.images[actor.direction] = image
                    else:
                        image = self.images[actor.direction]
                        
            needRedraw |= self.status[tag][1] != rotation
                        #color = None   
            needRedraw |= self.status[tag][0] != self.viewport.itemcget(tag, "fill")

            if needRedraw:
                self.viewport.delete(tag)
                for ant in self.viewport.find_withtag(tag+':ant'):
                    self.viewport.delete(ant)
                    
                
                self.viewport.create_rectangle(bbox, tags=(tag), fill=self.status[tag][0], activewidth=4.0, activefill="black")
                #self.status[tag] = color                    
                if image is not None:
                    self.viewport.create_image(tuple(realLoc + Vector(self.gridSize/2, self.gridSize/2)), tags=(tag+':ant'), image=image)
                    self.viewport.tag_raise(tag+':ant')
                    self.status[tag][1] = rotation   
                    
    '''def drawRow(self, y):
        for x in xrange(oldNumCells[0], numCells[0]):
            self.drawCell(x, y)
            
    def drawCol(self, x):
        for y in xrange(oldNumCells[1], numCells[1]):
            self.drawCell(x, y)'''
    
    def getCell(self, loc):
        loc = self.cellLocToGridLoc(loc)
        return self.world.grid[loc]        
    
    def getActor(self, loc):
        cell = self.getCell(loc)
        if cell.actor:
            return PastActor(cell.actor, self._tick)
        else:
            return None
    
    def drawAnt(self, actor):
        loc = actor.here.loc
        
        antTagPost = ':' + self.antTag
        tag = toTag(loc)
        
        realLoc = self.cellLocToRealLoc(loc)
        
        rotation = constants.DIRECTIONS_VEC_ROT[actor.direction]
        
        if actor.direction not in self.images:
            image = Image.open('ant.png')
            
            basewidth = Vector(map(int, self.gridSize*0.9))
            image = image.resize((basewidth.x, basewidth.y), Image.ANTIALIAS)    
            image = image.rotate(rotation)
            image = ImageTk.PhotoImage(image)
        
            self.images[actor.direction] = image
        else:
            image = self.images[actor.direction]          
            
        
        self.viewport.create_image(tuple(realLoc + self.gridSize/2), tags=(tag, self.antTag, tag+antTagPost), image=image)       
            
    def drawAnts(self, rect = None):
        #TODO: Optimize by only editing ants that moved or turned
        
        if rect is None:
            ul = self.cellOffset - Vector(1,1)
            lr = self.numCells - self.cellOffset
        else:
            ul = Vector(rect[:2])
            lr = Vector(rect[2:])
        
        # Delete all ants
        self.viewport.delete(self.antTag) 
        
        for x in xrange(ul.x, lr.x):
            for y in xrange(ul.y, lr.y):
                loc = Vector(x, y) 
                actor = self.getActor(loc)
                if actor is not None:
                    self.drawAnt(actor)
         
        # Bring all ants to the top           
        self.viewport.tag_raise(self.antTag) 
                    
        
    def drawGridlines(self, offset = None, canvasSize = None):
        #self.viewport.create_line()
        
        if offset is None:
            offset = self.offset
        offset = Vector(offset)
        self.canvasSize = canvasSize
        if self.canvasSize is None:
            self.canvasSize = (self.viewport.winfo_width(), self.viewport.winfo_height())
        self.canvasSize = Vector(self.canvasSize)
            
        lineTagPost = ':' + self.lineTag
        
        # Delete all Lines
        self.viewport.delete(self.lineTag)
        
        # Vertical Lines
        for x in xrange(offset.x, self.canvasSize.x, self.gridSize.x):
            tag = toTag(x, 0)
            self.viewport.delete(tag)
            self.viewport.create_line((x,0,x,self.canvasSize.y), tags=(tag, self.lineTag, tag + lineTagPost))
            
        # Horizontal Lines
        for y in xrange(self.canvasSize.y - offset.y, 0, -self.gridSize.y):
            tag = toTag(0, y)
            self.viewport.delete(tag)
            self.viewport.create_line((0,y,self.canvasSize.x,y), tags=(tag, self.lineTag, tag + lineTagPost))
    
    def drawGrid(self, event = None, forceRedraw = False):
        '''
        Draws the entire grid on the canvas with all of the ants in the proper orientation
        
        @param event - The event that triggered the redraw
        @param forceRedraw - Redraw the entire grid without any optimizations
        '''
    
        if self.newGridSize is not None:
            # update self.gridSize and redraw entire grid    
            forceRedraw = True
            self.gridSize = self.newGridSize
            
        if forceRedraw:
            oldSize = (0,0)
            oldNumCells = (0,0)
        else:
            oldSize = self.canvasSize
            oldNumCells = self.numCells
            
        if event is not None:
            self.canvasSize = (event.width, event.height)
        else:
            self.canvasSize = (self.viewport.winfo_width(), self.viewport.winfo_height())
        
        #oldNumCells = map(lambda i: i/self.gridWidth, oldSize)
        self.numCells = Vector(map(lambda i: i[0]/i[1]+1, zip(self.canvasSize, self.gridSize)))
        
        numCellsDelta = map(lambda x: x[0] - x[1], zip(self.numCells,oldNumCells))
        realDelta = map(lambda x: x[0] - x[1], zip(self.canvasSize,oldSize))
        
        self.drawGridlines()
        self.drawAnts()
                
    def clickGrid(self, event = None, location = None):
        #print self.undoClick
        '''for tag, color in self.undoClick.iteritems():
            self.status[tag][0] = color
            self.viewport.itemconfig(tag, fill=color)
            #self.noRedraw.remove(tag)
        self.undoClick.clear()'''
        
        # Delete all rects
        self.viewport.delete(self.rectTag)   
        
        if location is None and event is None:
            location = self.lastClick
        
        try:
            tags = None
            loc = None         
            if location is not None and location != '':
                try:
                    # Assume location is an AgentID
                    try:
                        loc = self.world.actors[int(location)].here.loc
                    except KeyError:
                        loc = self.lastClickBackup
                except ValueError:
                    try:
                        tags = self.viewport.gettags(location)
                    except IndexError as e:
                        if len(location) == 2:
                            loc = Vector(location[0], location[1], self._tick)
                        elif len(location) == 3:
                            loc = Vector(*location)
                        else:
                            raise e
            else:
                tags = self.viewport.gettags('current')
                    
                    
            if loc is None:
                for tag in tags:
                    try:
                        loc = fromTag(tag, self._tick)
                        break
                    except ValueError:
                        try:
                            loc = fromTag(tag.split(':')[0], self._tick)
                            break
                        except ValueError:
                            pass
                        
        except IndexError:
            return False
        
        if loc is None: 
            if not location and event:
                loc = self.realLocToCellLoc(event)
            elif location:
                loc = location
            else:
                return False
            
        try:
            gridLoc = self.cellLocToGridLoc(loc)
        except TypeError:
            return False
                
        food = 0
        pheromone = 0            
        actorID = None
        energy = None    
        actorIP = None
        sentence = None
        status = None            
        #with self.worldLock:
        if gridLoc in self.world.grid:
            cell = self.world.grid[gridLoc]
            actor = cell.actor
            food = cell.food
            pheromone = cell.pheromone
                           
            if actor is not None:
                actor = PastActor(actor, self._tick)
                actorID = actor.actorID
                energy = actor.energy
                actorIP = actor.ip
                sentence = actor.sentence
                status = actor.status
                
                thereTag = toTag(actor.there.loc)
                thereLoc = self.cellLocToRealLoc(actor.there.loc)
                self.viewport.create_rectangle((thereLoc.x, thereLoc.y, thereLoc.x+self.gridSize.x, thereLoc.y+self.gridSize.y), fill='lightblue', tags=(thereTag, self.rectTag, thereTag + ':' + self.rectTag))
                self.viewport.lower(self.rectTag)
                '''self.status[thereTag][0] = 'lightblue'
                oldcolor = self.viewport.itemcget(thereTag, "fill")                          
                if self.status[thereTag][0] != oldcolor:
                    self.undoClick[thereTag] = oldcolor
                    self.viewport.itemconfig(thereTag, fill=self.status[thereTag][0])
                    #self.noRedraw.add(thereTag)'''
                
        #['loc', 'food', 'pheromone', 'actorID', 'energy']
        self.cellInfo['loc'].set('Cell: %s,%s' % (loc.x, loc.y))
        self.cellInfo['food'].set('Food: %s' % food)
        self.cellInfo['pheromone'].set('Pheromone: %s' % pheromone)
        self.cellInfo['actorID'].set('ActorID: %s' % actorID)
        self.cellInfo['energy'].set('Energy: %s' % energy)
        self.cellInfo['IP'].set('IP: %s' % actorIP)
        self.cellInfo['sentence'].set('Next Sentence:\n%s' % sentence)
        self.cellInfo['status'].set('Last Sentence:\n%s' % (status,))
        if actorID is not None:
            self.lastClick = actorID
            self.lastClickBackup = loc
        else:
            self.lastClick = loc
            self.lastClickBackup = None
            
        return True
        
    def keypress(self, event):
        #print event.keysym
        moveMap = {'Left':(1, 0), 'Up':(0,-1), 'Right':(-1, 0), 'Down':(0,1)}
        zoomMap = {'equal':1, 'plus':1, 'minus':-1}
        timeMap = {'less':-1, 'greater':1, 'comma':-1, 'period':1}
        needsRedraw = False
        if event.keysym == 'space':
            self.tick(False)
            needsRedraw = True
        elif event.keysym in ('a', 'A'):
            self.auto.toggle()
            if self.verbose:
                print 'State: %s' % self.auto.state
        elif event.keysym in ('s', 'S'):
            self.autoGen.toggle()     
            if self.verbose:
                print 'AutoGen: %s' % self.autoGen.state            
        elif event.keysym in moveMap:
            # L 37 (1, 0)
            # U 38 (0,-1)
            # R 39 (-1, 0)
            # D 40 (0,1)
            
            self.cellOffset += Vector(*moveMap[event.keysym])
            if self.verbose:
                print 'Move!'
            needsRedraw = True
        elif event.keysym in zoomMap:
            if self.newGridSize is None:
                self.newGridSize = Vector(self.gridSize)
            self.newGridSize = self.newGridSize + zoomMap[event.keysym]*self.deltaGridSize
            self.newGridSize = Vector(map(lambda i: max(i, 20), self.newGridSize))
            if self.newGridSize == self.gridSize:
                self.newGridSize = None
                
            self.images.clear()
            if self.verbose:
                print 'Zoom!'
            needsRedraw = True
        elif event.keysym in timeMap:
            self._tick += timeMap[event.keysym]
            if self._tick < 0: self._tick = 0
            elif self._tick > self.world._tick: self._tick = self.world._tick
            needsRedraw = True
            
            
        if needsRedraw:
            self.viewport.event_generate("<<Redraw>>", when="tail")  
    
    def tick(self, redraw = True):
        if self.verbose:
            print 'Tick!'
            
        self._tick += 1
        
        self.buffer()
        
        if redraw:
            self.viewport.event_generate("<<Redraw>>", when="tail")
            
    def buffer(self):
        while self.world._tick < self._tick:
            self.genWorld()
                
    def genWorld(self):
        start = time.time()
        self.world.tick()
        self.delta[self.world._tick] = time.time() - start
        self.timeData['sum'] += self.delta[self.world._tick]
        self.timeData['count'] += 1
        
        ahead = self.world._tick - self._tick
        
        print 'Ahead by %s' % ahead
        
        if ahead > 1:
            self.autoGen.time = math.sqrt(ahead/100.0)
        else:
            self.autoGen.time = 0
        
        if self.verbose:
            print 'Tick: %s, %dms' % (self.world._tick, self.delta[self.world._tick]*1000)
            print 'Ants: %s' % len(self.world.actors)
            print 'Average time per tick: %s ms' % (1000.0 * self.timeData['sum'] / self.timeData['count'])
            print 'Average time per ant per tick: %s ms' % (1000.0 * self.timeData['sum'] / (len(self.world.actors)*self.timeData['count']))
            #self.cellInfo['infoport'].set('Tick: %s, %dms' % (self._tick, self.delta[self._tick]*1000))
            print 'End Tick!'         
            
    def redraw(self, event = None):
        self.cellInfo['infoport'].set('Tick: %s\n%dms' % (self._tick, self.delta[self._tick]*1000))
        self.drawGrid(forceRedraw=True)
        if not self.clickGrid(location=self.lastClick):
            self.lastClick = ''
        
    def __del__(self):
        self.auto.stop()
        self.autoGen.stop()
        self.root.quit()
        
if __name__ == '__main__':
    from agent import Agent
    
    testScriptA = 'test1'
    testScriptB = 'test2'
    
    agent = Agent(0, testScriptA)
    agent1 = Agent(1, testScriptB)
    
    w = World()
    w.newActor(agent, (0, 0, 0), 'N')
    w.newActor(agent1, (0, 2, 0), 'E')    
    
    mainwindow = GUI(w)
    tk.mainloop()


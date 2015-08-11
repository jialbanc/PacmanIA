
import pygame, sys, os, random
from pygame.locals import *
from random import randint
import os

# WIN???
SCRIPT_PATH=sys.path[0]

TILE_WIDTH=TILE_HEIGHT=24

NO_GIF_TILES=[23]

NO_WX=0 
USER_NAME="User"

HS_FONT_SIZE=14
HS_LINE_HEIGHT=16
HS_WIDTH=408
HS_HEIGHT=120
HS_XOFFSET=48
HS_YOFFSET=384
HS_ALPHA=200

# new constants for the score's position
SCORE_XOFFSET=50 # pixels from left edge
SCORE_YOFFSET=34 # pixels from bottom edge (to top of score)
SCORE_COLWIDTH=13 # width of each character

# Joystick defaults - maybe add a Preferences dialog in the future?
JS_DEVNUM=0 # device 0 (pygame joysticks always start at 0). if JS_DEVNUM is not a valid device, will use 0
JS_XAXIS=0 # axis 0 for left/right (default for most joysticks)
JS_YAXIS=1 # axis 1 for up/down (default for most joysticks)
JS_STARTBUTTON=9 # button number to start the game. this is a matter of personal preference, and will vary from device to device

IMG_EDGE_LIGHT_COLOR = (0xff,0xce,0xff,0xff)
IMG_FILL_COLOR = (0x84,0x00,0x84,0xff)
IMG_EDGE_SHADOW_COLOR = (0xff,0x00,0xff,0xff)
IMG_PELLET_COLOR = (0x80,0x00,0x80,0xff)

pygame.mixer.pre_init(22050,16,2,512)
pygame.mixer.init()


clock = pygame.time.Clock()
pygame.init()

window = pygame.display.set_mode((1, 1))
pygame.display.set_caption("Pacman")

screen = pygame.display.get_surface()

img_Background = pygame.image.load(os.path.join(SCRIPT_PATH,"res","backgrounds","1.gif")).convert()


snd_pellet = {}
snd_pellet[0] = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sounds","pellet1.wav"))
snd_pellet[1] = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sounds","pellet2.wav"))
snd_powerpellet = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sounds","powerpellet.wav"))
snd_eatgh = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sounds","eatgh2.wav"))
snd_eatfruit = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sounds","eatfruit.wav"))
snd_extralife = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sounds","extralife.wav"))
snd_tada = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sounds","tada.wav"))
Font = pygame.font.Font(os.path.join(SCRIPT_PATH,"res","font.ttf"),28)
#      ___________________
# ___/  class definitions  \_______________________________________________

class game ():

        def __init__ (self):
                self.levelNum = 0
                self.lives = 3
                
                # game "mode" variable
                # 1 = normal
                # 2 = hit ghost
                # 3 = game over
                # 4 = wait to start
                # 5 = wait after eating ghost
                # 6 = wait after finishing level
                self.mode = 0
                self.modeTimer = 0
                self.puerta = 0

                self.select = 0
                self.algorithm = 0
                self.numberPellets = 1

                self.ghostTimer = 0
                self.ghostValue = 0
                self.fruitTimer = 0
                self.fruitScoreTimer = 0
                self.fruitScorePos = (0, 0)
                
                self.SetMode( 2 )
                
                # camera variables
                self.screenPixelPos = (0, 0) # absolute x,y position of the screen from the upper-left corner of the level
                self.screenNearestTilePos = (0, 0) # nearest-tile position of the screen from the UL corner
                self.screenPixelOffset = (0, 0) # offset in pixels of the screen from its nearest-tile position
                
                self.screenTileSize = (23, 21)
                self.screenSize = (self.screenTileSize[1] * TILE_WIDTH, self.screenTileSize[0] * TILE_HEIGHT)
                
                # numerical display digits
                self.digit = {}
                for i in range(0, 10, 1):
                        self.digit[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text",str(i) + ".gif")).convert()
                self.imLife = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text","life.gif")).convert()
                self.imGameOver = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text","gameover.gif")).convert()
                self.imReady = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text","ready.gif")).convert()
                self.imLogo = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text","logo.gif")).convert()
                self.imgMenu = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text","menu.gif")).convert()
                self.imgSelect = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text","select.gif")).convert()
                self.imgCheckAlgorithm = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text","check.gif")).convert()

        def StartNewGame (self):
                self.levelNum = 1
                self.score = 0
                self.lives = 3
                
                self.SetMode( 3 )
                thisLevel.LoadLevel( thisGame.GetLevelNum() )
                
        def SmartMoveScreen (self):
                        
                possibleScreenX = player.x - self.screenTileSize[1] / 2 * TILE_WIDTH
                possibleScreenY = player.y - self.screenTileSize[0] / 2 * TILE_HEIGHT
                
                if possibleScreenX < 0:
                        possibleScreenX = 0
                elif possibleScreenX > thisLevel.lvlWidth * TILE_WIDTH - self.screenSize[0]:
                        possibleScreenX = thisLevel.lvlWidth * TILE_HEIGHT - self.screenSize[0]
                        
                if possibleScreenY < 0:
                        possibleScreenY = 0
                elif possibleScreenY > thisLevel.lvlHeight * TILE_WIDTH - self.screenSize[1]:
                        possibleScreenY = thisLevel.lvlHeight * TILE_HEIGHT - self.screenSize[1]
                
                thisGame.MoveScreen( (possibleScreenX, possibleScreenY) )
                
        def MoveScreen (self, (newX, newY) ):
                self.screenPixelPos = (newX, newY)
                self.screenNearestTilePos = (int(newY / TILE_HEIGHT), int(newX / TILE_WIDTH)) # nearest-tile position of the screen from the UL corner
                self.screenPixelOffset = (newX - self.screenNearestTilePos[1]*TILE_WIDTH, newY - self.screenNearestTilePos[0]*TILE_HEIGHT)
                
        def GetScreenPos (self):
                return self.screenPixelPos
                
        def GetLevelNum (self):
                return self.levelNum
        
        def SetNextLevel (self):
                self.levelNum += 1
                
                self.SetMode( 3 )
                thisLevel.LoadLevel( thisGame.GetLevelNum() )
                
                player.velX = 0
                player.velY = 0
                player.anim_pacmanCurrent = player.anim_pacmanS
                
        def SetMode (self, newMode):
                self.mode = newMode
                self.modeTimer = 0
                # print " ***** GAME MODE IS NOW ***** " + str(newMode)
                
class node ():
        
        def __init__ (self):
                self.g = -1 # movement cost to move from previous node to this one (usually +10)
                self.h = -1 # estimated movement cost to move from this node to the ending node (remaining horizontal and vertical steps * 10)
                self.f = -1 # total movement cost of this node (= g + h)
                # parent node - used to trace path back to the starting node at the end
                self.parent = (-1, -1)
                # node type - 0 for empty space, 1 for wall (optionally, 2 for starting node and 3 for end)
                self.type = -1
                
class path_finder ():
        
        def __init__ (self):
                # map is a 1-DIMENSIONAL array.
                # use the Unfold( (row, col) ) function to convert a 2D coordinate pair
                # into a 1D index to use with this array.
                self.map = {}
                self.size = (-1, -1) # rows by columns
                
                self.pathChainRev = ""
                self.pathChain = ""
                                
                # starting and ending nodes
                self.start = (-1, -1)
                self.end = (-1, -1)
                
                # current node (used by algorithm)
                self.current = (-1, -1)
                
                # open and closed lists of nodes to consider (used by algorithm)
                self.openList = []
                self.closedList = []
                
                # used in algorithm (adjacent neighbors path finder is allowed to consider)
                self.neighborSet = [ (0, -1), (0, 1), (-1, 0), (1, 0) ]
                
        def ResizeMap (self, (numRows, numCols)):
                self.map = {}
                self.size = (numRows, numCols)

                # initialize path_finder map to a 2D array of empty nodes
                for row in range(0, self.size[0], 1):
                        for col in range(0, self.size[1], 1):
                                self.Set( (row, col), node() )
                                self.SetType( (row, col), 0 )
                
        def CleanUpTemp (self):
                
                # this resets variables needed for a search (but preserves the same map / maze)
        
                self.pathChainRev = ""
                self.pathChain = ""
                self.current = (-1, -1)
                self.openList = []
                self.closedList = []
                
        def FindPath (self, startPos, endPos ):
                
                self.CleanUpTemp()
                
                # (row, col) tuples
                self.start = startPos
                self.end = endPos
                
                # add start node to open list
                self.AddToOpenList( self.start )
                self.SetG ( self.start, 0 )
                self.SetH ( self.start, 0 )
                self.SetF ( self.start, 0 )
                
                doContinue = True
                
                while (doContinue == True):
                
                        thisLowestFNode = self.GetLowestFNode()

                        if not thisLowestFNode == self.end and not thisLowestFNode == False:
                                self.current = thisLowestFNode
                                self.RemoveFromOpenList( self.current )
                                self.AddToClosedList( self.current )
                                
                                for offset in self.neighborSet:
                                        thisNeighbor = (self.current[0] + offset[0], self.current[1] + offset[1])
                                        
                                        if not thisNeighbor[0] < 0 and not thisNeighbor[1] < 0 and not thisNeighbor[0] > self.size[0] - 1 and not thisNeighbor[1] > self.size[1] - 1 and not self.GetType( thisNeighbor ) == 1:
                                                cost = self.GetG( self.current ) + 10
                                                
                                                if self.IsInOpenList( thisNeighbor ) and cost < self.GetG( thisNeighbor ):
                                                        self.RemoveFromOpenList( thisNeighbor )
                                                        
                                                #if self.IsInClosedList( thisNeighbor ) and cost < self.GetG( thisNeighbor ):
                                                #       self.RemoveFromClosedList( thisNeighbor )
                                                        
                                                if not self.IsInOpenList( thisNeighbor ) and not self.IsInClosedList( thisNeighbor ):
                                                        self.AddToOpenList( thisNeighbor )
                                                        self.SetG( thisNeighbor, cost )
                                                        self.CalcH( thisNeighbor )
                                                        self.CalcF( thisNeighbor )
                                                        self.SetParent( thisNeighbor, self.current )
                        else:
                                doContinue = False
                                                
                if thisLowestFNode == False:
                        return False
                                                
                # reconstruct path
                self.current = self.end
                while not self.current == self.start:
                        # build a string representation of the path using R, L, D, U
                        if self.current[1] > self.GetParent(self.current)[1]:
                                self.pathChainRev += 'R' 
                        elif self.current[1] < self.GetParent(self.current)[1]:
                                self.pathChainRev += 'L'
                        elif self.current[0] > self.GetParent(self.current)[0]:
                                self.pathChainRev += 'D'
                        elif self.current[0] < self.GetParent(self.current)[0]:
                                self.pathChainRev += 'U'
                        self.current = self.GetParent(self.current)
                        self.SetType( self.current, 4)
                        
                # because pathChainRev was constructed in reverse order, it needs to be reversed!
                for i in range(len(self.pathChainRev) - 1, -1, -1):
                        self.pathChain += self.pathChainRev[i]
                
                # set start and ending positions for future reference
                self.SetType( self.start, 2)
                self.SetType( self.end, 3)
                
                return self.pathChain

        def Unfold (self, (row, col)):
                # this function converts a 2D array coordinate pair (row, col)
                # to a 1D-array index, for the object's 1D map array.
                return (row * self.size[1]) + col
        
        def Set (self, (row, col), newNode):
                # sets the value of a particular map cell (usually refers to a node object)
                self.map[ self.Unfold((row, col)) ] = newNode
                
        def GetType (self, (row, col)):
                return self.map[ self.Unfold((row, col)) ].type
                
        def SetType (self, (row, col), newValue):
                self.map[ self.Unfold((row, col)) ].type = newValue

        def GetF (self, (row, col)):
                return self.map[ self.Unfold((row, col)) ].f

        def GetG (self, (row, col)):
                return self.map[ self.Unfold((row, col)) ].g
        
        def GetH (self, (row, col)):
                return self.map[ self.Unfold((row, col)) ].h
                
        def SetG (self, (row, col), newValue ):
                self.map[ self.Unfold((row, col)) ].g = newValue

        def SetH (self, (row, col), newValue ):
                self.map[ self.Unfold((row, col)) ].h = newValue
                
        def SetF (self, (row, col), newValue ):
                self.map[ self.Unfold((row, col)) ].f = newValue
                
        def CalcH (self, (row, col)):
                self.map[ self.Unfold((row, col)) ].h = abs(row - self.end[0]) + abs(col - self.end[0])
                
        def CalcF (self, (row, col)):
                unfoldIndex = self.Unfold((row, col))
                self.map[unfoldIndex].f = self.map[unfoldIndex].g + self.map[unfoldIndex].h
        
        def AddToOpenList (self, (row, col) ):
                self.openList.append( (row, col) )
                
        def RemoveFromOpenList (self, (row, col) ):
                self.openList.remove( (row, col) )
                
        def IsInOpenList (self, (row, col) ):
                if self.openList.count( (row, col) ) > 0:
                        return True
                else:
                        return False
                
        def GetLowestFNode (self):
                lowestValue = 1000 # start arbitrarily high
                lowestPair = (-1, -1)
                
                for iOrderedPair in self.openList:
                        if self.GetF( iOrderedPair ) < lowestValue:
                                lowestValue = self.GetF( iOrderedPair )
                                lowestPair = iOrderedPair
                
                if not lowestPair == (-1, -1):
                        return lowestPair
                else:
                        return False
                
        def AddToClosedList (self, (row, col) ):
                self.closedList.append( (row, col) )
                
        def IsInClosedList (self, (row, col) ):
                if self.closedList.count( (row, col) ) > 0:
                        return True
                else:
                        return False

        def SetParent (self, (row, col), (parentRow, parentCol) ):
                self.map[ self.Unfold((row, col)) ].parent = (parentRow, parentCol)

        def GetParent (self, (row, col) ):
                return self.map[ self.Unfold((row, col)) ].parent
                
        def draw (self):
                for row in range(0, self.size[0], 1):
                        for col in range(0, self.size[1], 1):
                        
                                thisTile = self.GetType((row, col))
                                screen.blit (tileIDImage[ thisTile ], (col * (TILE_WIDTH*2), row * (TILE_WIDTH*2)))
                
class pacman ():
        def __init__ (self):
                self.x = 0
                self.y = 0
                self.velX = 0
                self.velY = 0
                self.speed = 1
                
                self.nearestRow = 0
                self.nearestCol = 0
                
                self.homeX = 0
                self.homeY = 0
                self.currentPath = ""
                
                self.anim_pacmanL = {}
                self.anim_pacmanR = {}
                self.anim_pacmanU = {}
                self.anim_pacmanD = {}
                self.anim_pacmanS = {}
                self.anim_pacmanCurrent = {}
                
                for i in range(1, 9, 1):
                        self.anim_pacmanL[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","sprite","pacman-l " + str(i) + ".gif")).convert()
                        self.anim_pacmanR[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","sprite","pacman-r " + str(i) + ".gif")).convert()
                        self.anim_pacmanU[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","sprite","pacman-u " + str(i) + ".gif")).convert()
                        self.anim_pacmanD[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","sprite","pacman-d " + str(i) + ".gif")).convert()
                        self.anim_pacmanS[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","sprite","pacman.gif")).convert()
                        
                self.animFrame = 1
                self.animDelay = 0

        def Draw (self):
                
                if thisGame.mode == 2:
                        return False
                if self.velX > 0:
                        self.anim_pacmanCurrent = self.anim_pacmanR
                elif self.velX < 0:
                        self.anim_pacmanCurrent = self.anim_pacmanL
                elif self.velY > 0:
                        self.anim_pacmanCurrent = self.anim_pacmanD
                elif self.velY < 0:
                        self.anim_pacmanCurrent = self.anim_pacmanU

                screen.blit (self.anim_pacmanCurrent[ self.animFrame ], (self.x - thisGame.screenPixelPos[0], self.y - thisGame.screenPixelPos[1]))

                if thisGame.mode == 1:
                        if not self.velX == 0 or not self.velY == 0:
                                # only Move mouth when pacman is moving
                                self.animFrame += 1     
                        
                        if self.animFrame == 9:
                                # wrap to beginning
                                self.animFrame = 1
                        
        def Move (self):
                

                self.x += self.velX
                self.y += self.velY
                
                self.nearestRow = int(((self.y + (TILE_HEIGHT/2)) / TILE_HEIGHT))
                self.nearestCol = int(((self.x + (TILE_HEIGHT/2)) / TILE_WIDTH))
                if not thisLevel.CheckIfHitWall((self.x + self.velX, self.y + self.velY), (self.nearestRow, self.nearestCol)):
                        # it's ok to Move
                        self.x += self.velX
                        self.y += self.velY
                        
                        # check for collisions with other tiles (pellets, etc)
                        thisLevel.CheckIfHitSomething((self.x, self.y), (self.nearestRow, self.nearestCol))
                        
                        if (self.x % TILE_WIDTH) == 0 and (self.y % TILE_HEIGHT) == 0:
                                # if the ghost is lined up with the grid again
                                # meaning, it's time to go to the next path item

                                if len(self.currentPath) > 0:
                                        self.currentPath = self.currentPath[1:]
                                        self.FollowNextPathWay()

                                else:
                                        self.x = self.nearestCol * TILE_WIDTH
                                        self.y = self.nearestRow * TILE_HEIGHT
                                        (randRow,randCol) = (0,0)
                                        while not thisLevel.GetMapTile((randRow, randCol)) == tileID[ 'pellet' ] or (randRow, randCol) == (0, 0):
                                                randRow = random.randint(1, thisLevel.lvlHeight - 2)
                                                randCol = random.randint(1, thisLevel.lvlWidth - 2)
                                        self.currentPath = path.FindPath( (self.nearestRow, self.nearestCol), (randRow, randCol) )
                                        self.FollowNextPathWay()

        def FollowNextPathWay (self):
                
                # print "Ghost " + str(self.id) + " rem: " + self.currentPath
                
                # only follow this pathway if there is a possible path found!
                if not self.currentPath == False:
                
                        if len(self.currentPath) > 0:
                                if self.currentPath[0] == "L":
                                        (self.velX, self.velY) = (-self.speed, 0)
                                elif self.currentPath[0] == "R":
                                        (self.velX, self.velY) = (self.speed, 0)
                                elif self.currentPath[0] == "U":
                                        (self.velX, self.velY) = (0, -self.speed)
                                elif self.currentPath[0] == "D":
                                        (self.velX, self.velY) = (0, self.speed)
                                        
                        else:
                            (randRow, randCol) = (0, 0)

                            while not thisLevel.GetMapTile((randRow, randCol)) == tileID[ 'pellet' ] or (randRow, randCol) == (0, 0):
                                    randRow = random.randint(1, thisLevel.lvlHeight - 2)
                                    randCol = random.randint(1, thisLevel.lvlWidth - 2)

                            self.currentPath = path.FindPath( (self.nearestRow, self.nearestCol), (randRow, randCol) )
                            self.FollowNextPathWay()

                        
class level ():
        
        def __init__ (self):
                self.lvlWidth = 0
                self.lvlHeight = 0
                self.edgeLightColor = (255, 255, 0, 255)
                self.edgeShadowColor = (255, 150, 0, 255)
                self.fillColor = (0, 255, 255, 255)
                self.pelletColor = (255, 255, 255, 255)
                self.map = {}
                self.pellets = 0
                self.puertaFijaPos = (3, 0)
                
        def SetMapTile (self, (row, col), newValue):
                self.map[ (row * self.lvlWidth) + col ] = newValue
                
        def GetMapTile (self, (row, col)):
                if row >= 0 and row < self.lvlHeight and col >= 0 and col < self.lvlWidth:
                        return self.map[ (row * self.lvlWidth) + col ]
                else:
                        return 0

        def FarestPointFromPacman(self,(row,col)):
                dp1=(self.lvlHeight-3)
                dp2=(self.lvlWidth-6)
                if self.lvlHeight-row > row:
                        if self.lvlWidth-col > col:
                                h1=(((dp1-row)**2)+((self.lvlWidth-col)**2))**0.5
                                h2=(((dp2-col)**2)+((self.lvlHeight-row)**2))**0.5
                                if h1 > h2:
                                        return dp1, self.lvlWidth-1
                                else:
                                        return self.lvlHeight-1, dp2
                        else:
                                h1=(((dp1-row)**2)+(col**2))**0.5
                                h2=(((col-6)**2)+((self.lvlHeight-row)**2))**0.5
                                if h1 > h2:
                                        return dp1, 0
                                else:
                                        return self.lvlHeight-1, 6
                else:
                        if self.lvlWidth-col > col:
                                h1=(((dp2-col)**2)+(row**2))**0.5
                                h2=(((row-3)**2)+((self.lvlWidth-col)**2))**0.5
                                if h1 > h2:
                                        return 0, dp2
                                else:
                                        return 3, self.lvlWidth-1
                        else:
                                h1=(((col-6)**2)+((self.lvlHeight-row)**2))**0.5
                                h2=(((row-3)**2)+((self.lvlWidth-col)**2))**0.5
                                if h1 > h2:
                                        return 0, 6
                                else:
                                        return 3, 0

        def DrawExitDoor(self, (row,col)):
                if row == 0:
                        self.SetMapTile((row,col-1),113)
                        self.SetMapTile((row,col),21)
                        self.SetMapTile((row,col+1),113)
                        self.SetMapTile((row+1,col-1),106)
                        self.SetMapTile((row+1,col),0)
                        self.SetMapTile((row+1,col+1),105)
                elif col == 0:
                        self.SetMapTile((row-1,col),111)
                        self.SetMapTile((row,col),21)
                        self.SetMapTile((row+1,col),111)
                        if self.GetMapTile((row-1,col+1)) != 101:
                                self.SetMapTile((row-1,col+1),100)
                        else:
                                self.SetMapTile((row-1,col+1),106)
                        self.SetMapTile((row,col+1),0)
                        if self.GetMapTile((row+1,col+1)) != 101:
                                self.SetMapTile((row+1,col+1),100)
                        else:
                                self.SetMapTile((row+1,col+1),108)
                elif row == self.lvlHeight-1:
                        self.SetMapTile((row,col-1),110)
                        self.SetMapTile((row,col),21)
                        self.SetMapTile((row,col+1),110)
                        self.SetMapTile((row-1,col-1),108)
                        self.SetMapTile((row-1,col),0)
                        self.SetMapTile((row-1,col+1),107)
                elif col == self.lvlWidth-1:
                        self.SetMapTile((row-1,col),112)
                        self.SetMapTile((row,col),21)
                        self.SetMapTile((row+1,col),112)
                        if self.GetMapTile((row-1,col-1)) != 101:
                                self.SetMapTile((row-1,col-1),100)
                        else:
                                self.SetMapTile((row-1,col-1),105)
                        self.SetMapTile((row,col-1),0)
                        if self.GetMapTile((row+1,col-1)) != 101:
                                self.SetMapTile((row+1,col-1),100)
                        else:
                                self.SetMapTile((row+1,col-1),107)

        def IsWall (self, (row, col)):
        
                if row > thisLevel.lvlHeight - 1 or row < 0:
                        return True
                
                if col > thisLevel.lvlWidth - 1 or col < 0:
                        return True
        
                # check the offending tile ID
                result = thisLevel.GetMapTile((row, col))

                # if the tile was a wall
                if result >= 100 and result <= 199:
                        return True
                else:
                        return False
        
                                        
        def CheckIfHitWall (self, (possiblePlayerX, possiblePlayerY), (row, col)):
        
                numCollisions = 0
                
                # check each of the 9 surrounding tiles for a collision
                for iRow in range(row - 1, row + 2, 1):
                        for iCol in range(col - 1, col + 2, 1):
                        
                                if  (possiblePlayerX - (iCol * TILE_WIDTH) < TILE_WIDTH) and (possiblePlayerX - (iCol * TILE_WIDTH) > -TILE_WIDTH) and (possiblePlayerY - (iRow * TILE_HEIGHT) < TILE_HEIGHT) and (possiblePlayerY - (iRow * TILE_HEIGHT) > -TILE_HEIGHT):
                                        
                                        if self.IsWall((iRow, iCol)):
                                                numCollisions += 1
                                                
                if numCollisions > 0:
                        return True
                else:
                        return False
                
                
        def CheckIfHit (self, (playerX, playerY), (x, y), cushion):
        
                if (playerX - x < cushion) and (playerX - x > -cushion) and (playerY - y < cushion) and (playerY - y > -cushion):
                        return True
                else:
                        return False


        def CheckIfHitSomething (self, (playerX, playerY), (row, col)):
        
                for iRow in range(row - 1, row + 2, 1):
                        for iCol in range(col - 1, col + 2, 1):
                        
                                if  (playerX - (iCol * TILE_WIDTH) < TILE_WIDTH) and (playerX - (iCol * TILE_WIDTH) > -TILE_WIDTH) and (playerY - (iRow * TILE_HEIGHT) < TILE_HEIGHT) and (playerY - (iRow * TILE_HEIGHT) > -TILE_HEIGHT):
                                        # check the offending tile ID
                                        result = thisLevel.GetMapTile((iRow, iCol))
                
                                        if result == tileID[ 'pellet' ]:
                                                # got a pellet
                                                thisLevel.SetMapTile((iRow, iCol), 0)
                                                snd_pellet[0].play()
                                               
                                                thisLevel.pellets -= 1

                                                if thisLevel.pellets == 0:
                                                        # no more pellets left!
                                                        # WON THE LEVEL
                                                        thisGame.SetMode( 4 )
                                                        #if thisGame.puerta == 1:
                                                        #        self.DrawExitDoor(self.FarestPointFromPacman((iRow,iCol)))
                                                        #if thisGame.puerta == 0:
                                                        #        self.DrawExitDoor(self.puertaFijaPos)
             
                                        elif result == tileID[ 'door-h' ]:
                                                # ran into a horizontal door
                                                for i in range(0, thisLevel.lvlWidth, 1):
                                                        if not i == iCol:
                                                                if thisLevel.GetMapTile((iRow, i)) == tileID[ 'door-h' ]:
                                                                        player.x = i * TILE_WIDTH
                                                                        
                                                                        if player.velX > 0:
                                                                                player.x += TILE_WIDTH
                                                                        else:
                                                                                player.x -= TILE_WIDTH
                                                                                
                                        #elif result == tileID[ 'door-v' ]:
                                                # If he gets to exit door WIN!
                                                #thisGame.SetMode( 4 )

        def GetPathwayPairPos (self):
                
                doorArray = []
                
                for row in range(0, self.lvlHeight, 1):
                        for col in range(0, self.lvlWidth, 1):
                                if self.GetMapTile((row, col)) == tileID[ 'door-h' ]:
                                        # found a horizontal door
                                        doorArray.append( (row, col) )
                                elif self.GetMapTile((row, col)) == tileID[ 'door-v' ]:
                                        # found a vertical door
                                        doorArray.append( (row, col) )
                
                if len(doorArray) == 0:
                        return False
                
                chosenDoor = random.randint(0, len(doorArray) - 1)
                
                if self.GetMapTile( doorArray[chosenDoor] ) == tileID[ 'door-h' ]:
                        # horizontal door was chosen
                        # look for the opposite one
                        for i in range(0, thisLevel.lvlWidth, 1):
                                if not i == doorArray[chosenDoor][1]:
                                        if thisLevel.GetMapTile((doorArray[chosenDoor][0], i)) == tileID[ 'door-h' ]:
                                                return doorArray[chosenDoor], (doorArray[chosenDoor][0], i)
                else:
                        # vertical door was chosen
                        # look for the opposite one
                        for i in range(0, thisLevel.lvlHeight, 1):
                                if not i == doorArray[chosenDoor][0]:
                                        if thisLevel.GetMapTile((i, doorArray[chosenDoor][1])) == tileID[ 'door-v' ]:
                                                return doorArray[chosenDoor], (i, doorArray[chosenDoor][1])
                                        
                return False
                
        def PrintMap (self):
                
                for row in range(0, self.lvlHeight, 1):
                        outputLine = ""
                        for col in range(0, self.lvlWidth, 1):
                        
                                outputLine += str( self.GetMapTile((row, col)) ) + ", "
                                
                        # print outputLine
                        
        def DrawMap (self):


                for row in range(-1, thisGame.screenTileSize[0] +1, 1):
                        outputLine = ""
                        for col in range(-1, thisGame.screenTileSize[1] +1, 1):

                                # row containing tile that actually goes here
                                actualRow = thisGame.screenNearestTilePos[0] + row
                                actualCol = thisGame.screenNearestTilePos[1] + col

                                useTile = self.GetMapTile((actualRow, actualCol))
                                if not useTile == 0 and not useTile == tileID['door-h'] and not useTile == tileID['door-v']:
                                        # if this isn't a blank tile

                                        if useTile == tileID['pellet-power']:
                                                if self.powerPelletBlinkTimer < 30:
                                                        screen.blit (tileIDImage[ useTile ], (col * TILE_WIDTH - thisGame.screenPixelOffset[0], row * TILE_HEIGHT - thisGame.screenPixelOffset[1]) )

                                        elif useTile == tileID['showlogo']:
                                                screen.blit (thisGame.imLogo, (col * TILE_WIDTH - thisGame.screenPixelOffset[0], row * TILE_HEIGHT - thisGame.screenPixelOffset[1]) )
                                                screen.blit (thisGame.imgMenu, ((thisGame.screenSize[0] / 2 - (thisGame.imgMenu.get_width()/2)), thisGame.screenSize[1] / 2 - (thisGame.imgMenu.get_height()/2)) )
                                                if (thisGame.select == 0):
                                                        screen.blit (thisGame.imgSelect, (thisGame.screenSize[0] / 2 - (thisGame.imgSelect.get_width()/2) - 85 , (thisGame.screenSize[1] / 2 - (thisGame.imgSelect.get_height()/2)) - (thisGame.imgMenu.get_height()/2) + 18) )
                                                elif (thisGame.select == 1):
                                                        screen.blit (thisGame.imgSelect, (thisGame.screenSize[0] / 2 - (thisGame.imgSelect.get_width()/2) - 85 , (thisGame.screenSize[1] / 2 - (thisGame.imgSelect.get_height()/2)) + (thisGame.imgMenu.get_height()/2) - 57) )
                                                else:
                                                        screen.blit (thisGame.imgSelect, (thisGame.screenSize[0] / 2 - (thisGame.imgSelect.get_width()/2) - 85 , (thisGame.screenSize[1] / 2 - (thisGame.imgSelect.get_height()/2)) + (thisGame.imgMenu.get_height()/2) - 18) )
                                                if (thisGame.algorithm == 0):
                                                        screen.blit (thisGame.imgCheckAlgorithm, (thisGame.screenSize[0] / 2 - (thisGame.imgCheckAlgorithm.get_width()/2) - 55 , (thisGame.screenSize[1] / 2 - (thisGame.imgCheckAlgorithm.get_height()/2)) + (thisGame.imgMenu.get_height()/2) - 57) )
                                                else:
                                                        screen.blit (thisGame.imgCheckAlgorithm, (thisGame.screenSize[0] / 2 - (thisGame.imgCheckAlgorithm.get_width()/2) - 55 , (thisGame.screenSize[1] / 2 - (thisGame.imgCheckAlgorithm.get_height()/2)) + (thisGame.imgMenu.get_height()/2) - 18) )

                                        elif useTile == tileID['hiscores']:
                                                screen.blit(thisGame.imHiscores,(col*TILE_WIDTH-thisGame.screenPixelOffset[0],row*TILE_HEIGHT-thisGame.screenPixelOffset[1]))

                                        else:
                                                screen.blit (tileIDImage[ useTile ], (col * TILE_WIDTH - thisGame.screenPixelOffset[0], row * TILE_HEIGHT - thisGame.screenPixelOffset[1]) )

        def ChangeLevel(self, levelNum):
                if (levelNum != 0):
                        fin = open(os.path.join(SCRIPT_PATH,"res","levels","Laberinto"+str(levelNum) + ".txt"), 'r')
                        fout = open(os.path.join(SCRIPT_PATH,"res","levels",str(levelNum) + ".txt"), 'w')
                        for line in fin:
                                str_splitBySpace = line.split(' ')
                                for k in range(0, len(str_splitBySpace), 1):
                                        if (str_splitBySpace[k] == "?"):
                                                if (randint(0,8) == 0 and thisGame.numberPellets > 0):
                                                        fout.write("2")
                                                        thisGame.numberPellets = thisGame.numberPellets -1
                                                else:
                                                        fout.write("0")
                                        else:
                                                fout.write(str_splitBySpace[k])
                                        if (k != len(str_splitBySpace) - 1):
                                                fout.write(" ")
                        thisGame.numberPellets = 1

        def LoadLevel (self, levelNum):
                thisLevel.ChangeLevel( levelNum )
                self.map = {}

                self.pellets = 0

                f = open(os.path.join(SCRIPT_PATH,"res","levels",str(levelNum) + ".txt"), 'r')
                lineNum=-1
                rowNum = 0
                useLine = False
                isReadingLevelData = False

                for line in f:

                  lineNum += 1

                        # print " ------- Level Line " + str(lineNum) + " -------- "
                  while len(line)>0 and (line[-1]=="\n" or line[-1]=="\r"): line=line[:-1]
                  while len(line)>0 and (line[0]=="\n" or line[0]=="\r"): line=line[1:]
                  str_splitBySpace = line.split(' ')


                  j = str_splitBySpace[0]

                  if (j == "'" or j == ""):
                                # comment / whitespace line
                                # print " ignoring comment line.. "
                                useLine = False
                  elif j == "#":
                                # special divider / attribute line
                                useLine = False

                                firstWord = str_splitBySpace[1]

                                if firstWord == "lvlwidth":
                                        self.lvlWidth = int( str_splitBySpace[2] )
                                        # print "Width is " + str( self.lvlWidth )

                                elif firstWord == "lvlheight":
                                        self.lvlHeight = int( str_splitBySpace[2] )
                                        # print "Height is " + str( self.lvlHeight )

                                elif firstWord == "edgecolor":
                                        # edge color keyword for backwards compatibility (single edge color) mazes
                                        red = int( str_splitBySpace[2] )
                                        green = int( str_splitBySpace[3] )
                                        blue = int( str_splitBySpace[4] )
                                        self.edgeLightColor = (red, green, blue, 255)
                                        self.edgeShadowColor = (red, green, blue, 255)

                                elif firstWord == "edgelightcolor":
                                        red = int( str_splitBySpace[2] )
                                        green = int( str_splitBySpace[3] )
                                        blue = int( str_splitBySpace[4] )
                                        self.edgeLightColor = (red, green, blue, 255)

                                elif firstWord == "edgeshadowcolor":
                                        red = int( str_splitBySpace[2] )
                                        green = int( str_splitBySpace[3] )
                                        blue = int( str_splitBySpace[4] )
                                        self.edgeShadowColor = (red, green, blue, 255)

                                elif firstWord == "fillcolor":
                                        red = int( str_splitBySpace[2] )
                                        green = int( str_splitBySpace[3] )
                                        blue = int( str_splitBySpace[4] )
                                        self.fillColor = (red, green, blue, 255)

                                elif firstWord == "pelletcolor":
                                        red = int( str_splitBySpace[2] )
                                        green = int( str_splitBySpace[3] )
                                        blue = int( str_splitBySpace[4] )
                                        self.pelletColor = (red, green, blue, 255)


                                elif firstWord == "startleveldata":
                                        isReadingLevelData = True
                                        # print "Level data has begun"
                                        rowNum = 0

                                elif firstWord == "endleveldata":
                                        isReadingLevelData = False
                                        # print "Level data has ended"

                  else:
                                useLine = True


                        # this is a map data line
                  if useLine == True:

                                if isReadingLevelData == True:

                                        # print str( len(str_splitBySpace) ) + " tiles in this column"

                                        for k in range(0, self.lvlWidth, 1):
                                                self.SetMapTile((rowNum, k), int(str_splitBySpace[k]) )

                                                thisID = int(str_splitBySpace[k])
                                                if thisID == 4:
                                                        # starting position for pac-man

                                                        player.homeX = k * TILE_WIDTH
                                                        player.homeY = rowNum * TILE_HEIGHT
                                                        self.SetMapTile((rowNum, k), 0 )

                                                elif thisID == 2:
                                                        # pellet

                                                        self.pellets += 1

                                        rowNum += 1


                # reload all tiles and set appropriate colors
                GetCrossRef()

                # load map into the pathfinder object
                path.ResizeMap( (self.lvlHeight, self.lvlWidth) )

                for row in range(0, path.size[0], 1):
                        for col in range(0, path.size[1], 1):
                                if self.IsWall( (row, col) ):
                                        path.SetType( (row, col), 1 )
                                else:
                                        path.SetType( (row, col), 0 )

                # do all the level-starting stuff
                self.Restart()

        def Restart (self):

                player.x = player.homeX
                player.y = player.homeY
                player.velX = 0
                player.velY = 0
                player.Move()
                player.anim_pacmanCurrent = player.anim_pacmanS
                player.animFrame = 3
                # give each ghost a path to a random spot (containing a pellet)
                (randRow, randCol) = (0, 0)

                while not self.GetMapTile((randRow, randCol)) == tileID[ 'pellet' ] or (randRow, randCol) == (0, 0):
                        randRow = random.randint(1, self.lvlHeight - 2)
                        randCol = random.randint(1, self.lvlWidth - 2)

                # print "Ghost " + str(i) + " headed towards " + str((randRow, randCol))
                player.currentPath = path.FindPath( (player.nearestRow, player.nearestCol), (randRow, randCol) )
                player.FollowNextPathWay()





def CheckIfCloseButton(events):
        for event in events:
                if event.type == QUIT:
                        sys.exit(0)


def CheckInputs():

        if thisGame.mode == 2:
                if pygame.key.get_pressed()[ pygame.K_RETURN ]:
                        if (thisGame.select == 0):
                                thisGame.StartNewGame()
                        elif (thisGame.select == 1):
                                thisGame.algorithm = 0
                        else:
                                thisGame.algorithm = 1
                elif pygame.key.get_pressed()[ pygame.K_UP ]:
                        if (thisGame.select != 0):
                                thisGame.select = thisGame.select - 1
                elif pygame.key.get_pressed()[ pygame.K_DOWN ]:
                        if (thisGame.select != 2):
                                thisGame.select = thisGame.select + 1
                elif pygame.key.get_pressed()[ pygame.K_ESCAPE ]:
                                                pygame.quit()
                                                sys.exit()


#      _____________________________________________
# ___/  function: Get ID-Tilename Cross References  \______________________________________

def GetCrossRef ():

        f = open(os.path.join(SCRIPT_PATH,"res","crossref.txt"), 'r')

        lineNum = 0
        useLine = False

        for i in f.readlines():
                # print " ========= Line " + str(lineNum) + " ============ "
                while len(i)>0 and (i[-1]=='\n' or i[-1]=='\r'): i=i[:-1]
                while len(i)>0 and (i[0]=='\n' or i[0]=='\r'): i=i[1:]
                str_splitBySpace = i.split(' ')

                j = str_splitBySpace[0]

                if (j == "'" or j == "" or j == "#"):
                        # comment / whitespace line
                        # print " ignoring comment line.. "
                        useLine = False
                else:
                        # print str(wordNum) + ". " + j

                        useLine = True

                if useLine == True:
                        tileIDName[ int(str_splitBySpace[0]) ] = str_splitBySpace[1]
                        tileID[ str_splitBySpace[1] ] = int(str_splitBySpace[0])

                        thisID = int(str_splitBySpace[0])
                        if not thisID in NO_GIF_TILES:
                                tileIDImage[ thisID ] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","tiles",str_splitBySpace[1] + ".gif")).convert()
                        else:
                                tileIDImage[ thisID ] = pygame.Surface((TILE_WIDTH,TILE_HEIGHT))

                        # change colors in tileIDImage to match maze colors
                        for y in range(0, TILE_WIDTH, 1):
                                for x in range(0, TILE_HEIGHT, 1):

                                        if tileIDImage[ thisID ].get_at( (x, y) ) == IMG_EDGE_LIGHT_COLOR:
                                                # wall edge
                                                tileIDImage[ thisID ].set_at( (x, y), thisLevel.edgeLightColor )

                                        elif tileIDImage[ thisID ].get_at( (x, y) ) == IMG_FILL_COLOR:
                                                # wall fill
                                                tileIDImage[ thisID ].set_at( (x, y), thisLevel.fillColor )

                                        elif tileIDImage[ thisID ].get_at( (x, y) ) == IMG_EDGE_SHADOW_COLOR:
                                                # pellet color
                                                tileIDImage[ thisID ].set_at( (x, y), thisLevel.edgeShadowColor )

                                        elif tileIDImage[ thisID ].get_at( (x, y) ) == IMG_PELLET_COLOR:
                                                # pellet color
                                                tileIDImage[ thisID ].set_at( (x, y), thisLevel.pelletColor )

                        # print str_splitBySpace[0] + " is married to " + str_splitBySpace[1]
                lineNum += 1


#      __________________
# ___/  main code block  \_____________________________________________________

# create the pacman
player = pacman()

# create a path_finder object
path = path_finder()


tileIDName = {} # gives tile name (when the ID# is known)
tileID = {} # gives tile ID (when the name is known)
tileIDImage = {} # gives tile image (when the ID# is known)

# create game and level objects and load first level
thisGame = game()
thisLevel = level()
thisLevel.LoadLevel( thisGame.GetLevelNum() )

window = pygame.display.set_mode( thisGame.screenSize, pygame.HWSURFACE | pygame.DOUBLEBUF )

while True:

        CheckIfCloseButton( pygame.event.get() )

        if thisGame.mode == 1:

                thisGame.modeTimer += 1
                player.Move()

        elif thisGame.mode == 2:
                CheckInputs()

        elif thisGame.mode == 3:
                # waiting to start
                thisGame.modeTimer += 1

                if thisGame.modeTimer == 90:
                        thisGame.SetMode( 1 )
                        if len(player.currentPath) > 0:
                                if player.currentPath[0] == "L":
                                        (player.velX, player.velY) = (-player.speed, 0)
                                elif player.currentPath[0] == "R":
                                        (player.velX, player.velY) = (player.speed, 0)
                                elif player.currentPath[0] == "U":
                                        (player.velX, player.velY) = (0, -player.speed)
                                elif player.currentPath[0] == "D":
                                        (player.velX, player.velY) = (0, player.speed)

        elif thisGame.mode == 4:
                # pause after eating all the pellets
                thisGame.modeTimer += 1

                if thisGame.modeTimer == 60:
                        thisGame.SetMode( 5 )
                        oldEdgeLightColor = thisLevel.edgeLightColor
                        oldEdgeShadowColor = thisLevel.edgeShadowColor
                        oldFillColor = thisLevel.fillColor

        elif thisGame.mode == 5:
                        # flashing maze after finishing level
                        thisGame.modeTimer += 1
                        if thisGame.modeTimer == 1:
                                pygame.mixer.stop()
                                snd_tada.play()
                        elif thisGame.modeTimer == 60:
                                thisGame.SetMode ( 6 )
        elif thisGame.mode == 6:
                    # blank screen before changing levels
                    thisGame.modeTimer += 1
                    if thisGame.modeTimer == 10:
                            thisGame.SetNextLevel()
        thisGame.SmartMoveScreen()
        screen.blit(img_Background, (0, 0))
        if not thisGame.mode == 6:
                thisLevel.DrawMap()
                player.Draw()
        pygame.display.flip()
        print player.currentPath
        if (thisGame.mode == 2):
                clock.tick (10)
        else:
                clock.tick (60)
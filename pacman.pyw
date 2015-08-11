
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
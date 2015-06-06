import pygame, sys, os, random
from pygame.locals import *

#Ruta de la carpeta donde se encuentra el script.
SCRIPT_PATH=sys.path[0]

#Tamano de cada objeto en la pantalla.
TILE_WIDTH=TILE_HEIGHT=24
NO_GIF_TILES=[23]

# Joystick defaults - maybe add a Preferences dialog in the future?
JS_DEVNUM=0 # device 0 (pygame joysticks always start at 0). if JS_DEVNUM is not a valid device, will use 0
JS_XAXIS=0 # axis 0 for left/right (default for most joysticks)
JS_YAXIS=1 # axis 1 for up/down (default for most joysticks)
JS_STARTBUTTON=9 # button number to start the game. this is a matter of personal preference, and will vary from device to device

IMG_EDGE_LIGHT_COLOR = (0xff,0xce,0xff,0xff)
IMG_FILL_COLOR = (0x84,0x00,0x84,0xff)
IMG_EDGE_SHADOW_COLOR = (0xff,0x00,0xff,0xff)
IMG_PELLET_COLOR = (0x80,0x00,0x80,0xff)

# Must come before pygame.init()
pygame.mixer.pre_init(22050,16,2,512)
pygame.mixer.init()

clock = pygame.time.Clock()
pygame.init()

window = pygame.display.set_mode((1, 1),pygame.FULLSCREEN)
pygame.display.set_caption("Pacman")

screen = pygame.display.get_surface()

img_Background = pygame.image.load(os.path.join(SCRIPT_PATH,"res","backgrounds","1.gif")).convert()

snd_pellet = {}
snd_pellet[0] = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sounds","pellet1.wav"))
snd_pellet[1] = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sounds","pellet2.wav"))
snd_powerpellet = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sounds","powerpellet.wav"))


class game ():
      
        def __init__ (self):
                self.levelNum = 0
                # game "mode" variable
                # 1 = normal
                # 2 = game over
                # 3 = wait to start
                # 4 = wait after finishing level
                self.mode = 0
                self.modeTimer = 0
                #Seteamos game over como primer estado.
                self.SetMode( 2 )
                
                #camera variables
                self.screenPixelPos = (0, 0) # absolute x,y position of the screen from the upper-left corner of the level
                self.screenNearestTilePos = (0, 0) # nearest-tile position of the screen from the UL corner
                self.screenPixelOffset = (0, 0) # offset in pixels of the screen from its nearest-tile position
                
                #Numero de objetos en vertical y horizontal
                self.screenTileSize = (23, 21)
                self.screenSize = (self.screenTileSize[1] * TILE_WIDTH, self.screenTileSize[0] * TILE_HEIGHT)
                
                self.imGameOver = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text","gameover.gif")).convert()
                self.imReady = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text","ready.gif")).convert()
                self.imLogo = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text","logo.gif")).convert()
                
        def StartNewGame (self):
                self.levelNum = 1
                self.SetMode( 4 )
                thisLevel.LoadLevel( thisGame.GetLevelNum() )

                
        def SmartMoveScreen (self):
                        
                possibleScreenX = player.x - self.screenTileSize[1] / 2 * TILE_WIDTH
                possibleScreenY = player.y - self.screenTileSize[0] / 2 * TILE_HEIGHT
                
                #Si esta a la izquierda del centro lo mueve hacia alla.
                if possibleScreenX < 0:
                        possibleScreenX = 0
                #Si esta a la derecha del centro lo mueve hacia alla.
                elif possibleScreenX > thisLevel.lvlWidth * TILE_WIDTH - self.screenSize[0]:
                        possibleScreenX = thisLevel.lvlWidth * TILE_HEIGHT - self.screenSize[0]
                
                #Si esta abajo del centro lo mueve hacia alla.  
                if possibleScreenY < 0:
                        possibleScreenY = 0
                #Si esta arriba del centro lo mueve hacia alla. 
                elif possibleScreenY > thisLevel.lvlHeight * TILE_WIDTH - self.screenSize[1]:
                        possibleScreenY = thisLevel.lvlHeight * TILE_HEIGHT - self.screenSize[1]

                #Mueve la pantalla hacia los nuevos puntos.
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
                
                self.SetMode( 4 )
                thisLevel.LoadLevel( thisGame.GetLevelNum() )
                
                player.velX = 0
                player.velY = 0
                player.anim_pacmanCurrent = player.anim_pacmanS
                
                
        def SetMode (self, newMode):
                self.mode = newMode
                self.modeTimer = 0

class pacman ():
        
        def __init__ (self):
                self.x = 0
                self.y = 0
                self.velX = 0
                self.velY = 0
                self.speed = 3
                
                self.nearestRow = 0
                self.nearestCol = 0
                
                self.homeX = 0
                self.homeY = 0
                
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

                self.pelletSndNum = 0
                
        def Move (self):
                
                self.nearestRow = int(((self.y + (TILE_WIDTH/2)) / TILE_WIDTH))
                self.nearestCol = int(((self.x + (TILE_HEIGHT/2)) / TILE_HEIGHT))

                # make sure the current velocity will not cause a collision before moving
                if not thisLevel.CheckIfHitWall((self.x + self.velX, self.y + self.velY), (self.nearestRow, self.nearestCol)):
                        # it's ok to Move
                        self.x += self.velX
                        self.y += self.velY
                        
                        # check for collisions with other tiles (pellets, etc)
                        thisLevel.CheckIfHitSomething((self.x, self.y), (self.nearestRow, self.nearestCol))
                        
                else:
                        # we're going to hit a wall -- stop moving
                        self.velX = 0
                        self.velY = 0

        def Draw (self):
                
                if thisGame.mode == 2:
                        return False
                
                # set the current frame array to match the direction pacman is facing
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
                self.powerPelletBlinkTimer = 0
                
        def SetMapTile (self, (row, col), newValue):
                self.map[ (row * self.lvlWidth) + col ] = newValue
                
        def GetMapTile (self, (row, col)):
                if row >= 0 and row < self.lvlHeight and col >= 0 and col < self.lvlWidth:
                        return self.map[ (row * self.lvlWidth) + col ]
                else:
                        return 0
        
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
                                                snd_pellet[player.pelletSndNum].play()
                                                player.pelletSndNum = 1 - player.pelletSndNum
                                                
                                                thisLevel.pellets -= 1
                                                                                
                                                if thisLevel.pellets == 0:
                                                        # no more pellets left!
                                                        # WON THE LEVEL
                                                        thisGame.SetMode( 4 )
                                                        
                                                
                                        elif result == tileID[ 'pellet-power' ]:
                                                # got a power pellet
                                                thisLevel.SetMapTile((iRow, iCol), 0)
                                                pygame.mixer.stop()
                                                snd_powerpellet.play()
                                                
                                        
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
                                                                                
                                        elif result == tileID[ 'door-v' ]:
                                                # ran into a vertical door
                                                for i in range(0, thisLevel.lvlHeight, 1):
                                                        if not i == iRow:
                                                                if thisLevel.GetMapTile((i, iCol)) == tileID[ 'door-v' ]:
                                                                        player.y = i * TILE_HEIGHT
                                                                        
                                                                        if player.velY > 0:
                                                                                player.y += TILE_HEIGHT
                                                                        else:
                                                                                player.y -= TILE_HEIGHT
                                                                                

        
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
                
                self.powerPelletBlinkTimer += 1
                if self.powerPelletBlinkTimer == 60:
                        self.powerPelletBlinkTimer = 0
                
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

                                        else:
                                                screen.blit (tileIDImage[ useTile ], (col * TILE_WIDTH - thisGame.screenPixelOffset[0], row * TILE_HEIGHT - thisGame.screenPixelOffset[1]) )
                
        def LoadLevel (self, levelNum):
                
                self.map = {}
                
                self.pellets = 0
                
                f = open(os.path.join(SCRIPT_PATH,"res","levels",str(levelNum) + ".txt"), 'r')
                lineNum=-1
                rowNum = 0
                useLine = False
                isReadingLevelData = False
                  
                for line in f:

                  lineNum += 1
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
                GetCrossRef()                  
                # do all the level-starting stuff
                self.Restart()
                
        def Restart (self):
                
                player.x = player.homeX
                player.y = player.homeY
                player.velX = 0
                player.velY = 0
                
                player.anim_pacmanCurrent = player.anim_pacmanS
                player.animFrame = 3


def CheckIfCloseButton(events):
    for event in events: 
            if event.type == QUIT: 
                    sys.exit(0)


def CheckInputs(): 
        
    if thisGame.mode == 1:
            if pygame.key.get_pressed()[ pygame.K_RIGHT ] or (js!=None and js.get_axis(JS_XAXIS)>0.5):
                    if not (player.velX == player.speed and player.velY == 0) and not thisLevel.CheckIfHitWall((player.x + player.speed, player.y), (player.nearestRow, player.nearestCol)): 
                            player.velX = player.speed
                            player.velY = 0
                            
            elif pygame.key.get_pressed()[ pygame.K_LEFT ] or (js!=None and js.get_axis(JS_XAXIS)<-0.5):
                    if not (player.velX == -player.speed and player.velY == 0) and not thisLevel.CheckIfHitWall((player.x - player.speed, player.y), (player.nearestRow, player.nearestCol)): 
                            player.velX = -player.speed
                            player.velY = 0
                    
            elif pygame.key.get_pressed()[ pygame.K_DOWN ] or (js!=None and js.get_axis(JS_YAXIS)>0.5):
                    if not (player.velX == 0 and player.velY == player.speed) and not thisLevel.CheckIfHitWall((player.x, player.y + player.speed), (player.nearestRow, player.nearestCol)): 
                            player.velX = 0
                            player.velY = player.speed
                    
            elif pygame.key.get_pressed()[ pygame.K_UP ] or (js!=None and js.get_axis(JS_YAXIS)<-0.5):
                    if not (player.velX == 0 and player.velY == -player.speed) and not thisLevel.CheckIfHitWall((player.x, player.y - player.speed), (player.nearestRow, player.nearestCol)):
                            player.velX = 0
                            player.velY = -player.speed
                    
    elif thisGame.mode == 3:
            if pygame.key.get_pressed()[ pygame.K_RETURN ] or (js!=None and js.get_button(JS_STARTBUTTON)):
                    thisGame.StartNewGame()


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

tileIDName = {} # gives tile name (when the ID# is known)
tileID = {} # gives tile ID (when the name is known)
tileIDImage = {} # gives tile image (when the ID# is known)

# create game and level objects and load first level
thisGame = game()
thisLevel = level()
#Podemos setear el nivel que queramos si modificamos este parametro Ej:
#thisLevel.LoadLevel( 1 )
thisLevel.LoadLevel( thisGame.GetLevelNum() )

window = pygame.display.set_mode( thisGame.screenSize, pygame.HWSURFACE | pygame.DOUBLEBUF )

# initialise the joystick
if pygame.joystick.get_count()>0:
  if JS_DEVNUM<pygame.joystick.get_count(): js=pygame.joystick.Joystick(JS_DEVNUM)
  else: js=pygame.joystick.Joystick(0)
  js.init()
else: js=None

while True: 

        CheckIfCloseButton( pygame.event.get() )
        thisGame.mode = 1
        if thisGame.mode == 1:
                # normal gameplay mode
                CheckInputs()
                thisGame.modeTimer += 1
                player.Move()
        
        elif thisGame.mode == 2:
                # game over
                CheckInputs()
                        
        elif thisGame.mode == 3:
                # waiting to start
                thisGame.modeTimer += 1
                
                if thisGame.modeTimer == 90:
                        thisGame.SetMode( 1 )
                        player.velX = player.speed
                        
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
                
                whiteSet = [10, 30, 50, 70]
                normalSet = [20, 40, 60, 80]
                
                if not whiteSet.count(thisGame.modeTimer) == 0:
                        # member of white set
                        thisLevel.edgeLightColor = (255, 255, 254,255)
                        thisLevel.edgeShadowColor = (255, 255, 254,255)
                        thisLevel.fillColor = (0, 0, 0,255)
                        GetCrossRef()
                elif not normalSet.count(thisGame.modeTimer) == 0:
                        # member of normal set
                        thisLevel.edgeLightColor = oldEdgeLightColor
                        thisLevel.edgeShadowColor = oldEdgeShadowColor
                        thisLevel.fillColor = oldFillColor
                        GetCrossRef()
                elif thisGame.modeTimer == 150:
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
        
        clock.tick (60)

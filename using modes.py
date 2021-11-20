from cmu_112_graphics import *
import random
import math
from Enzyme import *
from Mutation import *


##########################################
# Home Screen Mode
##########################################

def homeScreenMode_redrawAll(app, canvas):
    font = 'Sans 26'
    canvas.create_text(app.width/2, 150, text='Play Enzymes vs. Mutations!', font=font)

def homeScreenMode_keyPressed(app, event):
    app.mode = 'gameMode'

##########################################
# Game Mode
##########################################

#GIANT timer fired program...may need to break it up into smaller functions
def gameMode_timerFired(app):
    
    #update current time and time for each enzyme
    #print(app.currentTime)
    app.currentTime += app.timerDelay
    for enzyme in app.boardEnzymes:
        if isinstance(enzyme[0], Enzyme):
            enzyme[0].updateTime()

    #update the sprite image
    app.spriteCounter = (1 + app.spriteCounter) % len(app.sprites)
    
    #update the mutation location after a certain interval
    if app.currentTime % 5000 == 100:
        updateMutationLocation(app, app.currentGreenX, app.currentGreenY + 1)

    #add an atp after a certain interval
    if app.currentTime % 8000 == 200:
        randomx = random.randint(0, app.width)
        randomy = 400
        placeATP(app, randomx, randomy)
    
    #update the atp location after each call to move it
    for atp in app.atp:
        if atp[1] <= app.width:
            atp[1] += 1
    
    #adds the atp shooting locations, if it's off the board, then take it out
    i = 0
    while i < (len(app.caspaseShoot)):
        if app.caspaseShoot[i][0] <= app.width and app.caspaseShoot[i][1] >= 0:
            app.caspaseShoot[i] = (app.caspaseShoot[i][0] + 55/3, app.caspaseShoot[i][1] - 37/3)
            i += 1
        else:
            app.caspaseShoot.pop(i)

    #constantly checks if the enzymes have enough atp and changes availability if not
    for enzyme in app.enzymes:
        if isinstance(enzyme, Enzyme):
            if app.collectedATP >= enzyme.pointValue:
                enzyme.notEnoughATP = False
            else: enzyme.notEnoughATP = True
    
    #basically just does different things at different times for each enzyme group
    #by looping through all the different enzymes on the board
    for enzyme in app.boardEnzymes:
        if isinstance(enzyme[0], Enzyme):
            #if atp synthase, then place atp sporadically
            if enzyme[0].name == "ATP Synthase":
                #print("i'm here!'")
                for time in enzyme[0].times:
                    if time % 10000 == 1000:
                        placeATP(app, enzyme[1], enzyme[2])
            
            #if dna polymerase, then lower duration
            if enzyme[0].name == "DNA Polymerase":
                for i in range(len(enzyme[0].left)):
                    x, y = getCartesianCoordinates(app, enzyme[0].locations[i][0], enzyme[0].locations[i][1])
                    row, col = getRowCol(app, x, y)
                    #print(row, col)
                    if app.colors[row][col - 1] == 1:
                        enzyme[0].left[i] -= 1
                    #print(enzyme[0].left)
                    if enzyme[0].left[i] <= 0:
                        #print("removing enzyme!")
                        removeEnzymeFromBoard(app, enzyme[0], i)
                        app.colors[row][col] = 0
                    elif enzyme[0].left[i] <= 20:
                        enzyme[0].setImage(app, i, 'images/dna polymerase broken.png')
            #if caspase, then shoot a ball after a certain time
            if enzyme[0].name == "Caspase":
                for i in range(len(enzyme[0].times)):
                    time = enzyme[0].times[i]
                    if time % 1500 == 0:
                        app.caspaseShoot.append(enzyme[0].locations[i]) 
                        
#function that takes care of what happens when mouse is pressed
#checks if user is collecting atp or moving a card
def gameMode_mousePressed(app, event):
    index = checkMouseInCard(app, event)
    #print(index, type(app.enzyme))
    
    #this chunk takes care of whether or not an enzyme is being moved right now
    if index != None and (app.enzyme == None or isinstance(app.enzyme, Enzyme) or isinstance(app.enzyme, list)): 
        app.enzyme = app.enzymes[index]
        if (app.enzyme == None or isinstance(app.enzyme, Enzyme)):
            app.enzymeX = app.enzyme.x
            app.enzymeY = app.enzyme.y
        elif app.enzyme == None or not isinstance(app.enzyme, Enzyme):
            app.enzymeX = app.enzyme[1]
            app.enzymeY = app.enzyme[2]
        app.dragCard = True
        #print(app.dragCard)
        
    #this loop checks if the user is collecting atp and removes it from the list of atp locations
    i = 0
    while (i < len(app.atp)):
        atp = app.atp[i]
        halfWidth = app.atpWidth//2
        halfHeight = app.atpHeight//2

        #checking if mouse click is in an atp
        if ((event.x >= atp[0] - halfWidth and event.x <= atp[0] + halfWidth) and 
            (event.y >= atp[1] - halfHeight and event.y <= atp[1] + halfHeight)):
            app.atp.pop(i)
            app.collectedATP += 25
        else:
            i += 1

#function that takes care of what happens when mouse is dragged
def gameMode_mouseDragged(app, event):
    #if it's the shovel, then just draw it
    if (not isinstance(app.enzyme, Enzyme) and app.dragCard and 
        (event.x >= 0 and event.x < app.width) and 
        (event.y >= 0 and event.y < app.height)):
        app.enzymeX, app.enzymeY = event.x - app.cardWidth//2, event.y - app.cardHeight//2

    #if it's an enzyme, make sure you're able to drag it
    elif (app.dragCard and app.enzyme.available and not app.enzyme.notEnoughATP and 
        (event.x >= 0 and event.x < app.width) and 
        (event.y >= 0 and event.y < app.height)):
        app.enzymeX, app.enzymeY = event.x - app.cardWidth//2, event.y - app.cardHeight//2

#function that takes care of what happens when mouse is released
def gameMode_mouseReleased(app, event):
    #doesn't say that the user is dragging the card if mouse is released inside the top bar
    if app.enzymeY < 200:
        app.dragCard = False
        
    #if it's an enzyme, then change dragCard, remove cost from collected atp, 
    #and change the availability of the enzyme group if applicable and update the board
    elif app.dragCard == True and app.enzyme != None and isinstance(app.enzyme, Enzyme) and app.enzymeY > 200:
        app.enzyme.changeAvailability()
        app.dragCard = False
        app.collectedATP -= app.enzyme.pointValue
        updateBoard(app, event)
            
    #if it's the shovel, then only change dragCard and update the board
    elif app.dragCard == True and app.enzyme != None and app.enzyme[0] == "Shovel" and app.enzymeY > 200:
        app.dragCard = False
        updateBoard(app, event)

#different key options for moving the mutation (helping when testing)
def gameMode_keyPressed(app, event):
    if event.key == 'Down':
        if app.currentGreenY < app.cols - 1:
            app.colors[app.currentGreenX][app.currentGreenY] = 0
            app.currentGreenY += 1
            app.colors[app.currentGreenX][app.currentGreenY] = 1

    elif event.key == 'Up':
        if app.currentGreenY > 0:
            app.colors[app.currentGreenX][app.currentGreenY] = 0
            app.currentGreenY -= 1
            app.colors[app.currentGreenX][app.currentGreenY] = 1
        
    elif event.key == 'Right':
        if app.currentGreenX < app.rows - 1:
            app.colors[app.currentGreenX][app.currentGreenY] = 0
            app.currentGreenX += 1
            app.colors[app.currentGreenX][app.currentGreenY] = 1

    elif event.key == 'Left':
        if app.currentGreenX > 0:
            app.colors[app.currentGreenX][app.currentGreenY] = 0
            app.currentGreenX -= 1
            app.colors[app.currentGreenX][app.currentGreenY] = 1

#calls all the drawing helper functions
def gameMode_redrawAll(app, canvas):
    drawBoard(app, canvas)
    drawATP(app, canvas)
    drawTopBar(app, canvas)
    drawMessageBox(app, canvas)
    drawShots(app, canvas)
    #only draws the card on the board if the user is dragging the card
    if app.dragCard:
        drawenzymeCard(app.enzyme, app, canvas, app.enzymeX, app.enzymeY)

##########################################
# Main App
##########################################
class Enzyme(object):
    
    def __init__(self, app, name, pointValue, imgUrl, index, count, scale):
        self.name = name
        self.pointValue = pointValue
        self.imgUrl = imgUrl
        self.image = app.loadImage(imgUrl)
        self.scale = scale
        self.image = app.scaleImage(self.image, scale)
        self.listIndex = index
        self.count = count
        self.times = []
        self.locations = []
        self.images = [self.image]*self.count
        if name == "DNA Polymerase":  
            self.left = []
        
        self.available = self.count > 0
        self.notEnoughATP = True
        self.x = 0
        self.y = 0
        self.time = 0

    #sets the position in the top bar
    def setPosition(self, x, y):
        self.x = x
        self.y = y
    
    #changes the availability of the enzyme group
    def changeAvailability(self):
        self.count -= 1
        self.available = self.count > 0
        
    #updates the time for each enzyme on the board
    def updateTime(self):
        for i in range(len(self.times)):
            self.times[i] += 100
    
    #changes the image for the object if it needs to be changed
    def setImage(self, app, i, imgUrl):
        image = app.loadImage(imgUrl)
        self.images[i] = app.scaleImage(image, self.scale)

class Mutation(object):
    
    def __init__(self, app, name, imgUrl, hits, x, y):
        self.name = name
        self.imgUrl = imgUrl
        self.image = app.loadImage(imgUrl)
        self.image = app.scaleImage(self.image, 1/8)
        self.hits = hits
        self.x = x
        self.y = y
        
    
    # def getHit(self):
    #     change number of hits left
    #     change image if hits is in a certain region
    #     self.hits -= 1
    #     pass

#sets up all the initial helper variables
def appStarted(app):
    app.mode = 'homeScreenMode'
    
    #setting up board configurations
    app.rows = 9
    app.cols = 9
    app.tileWidth = app.width//app.rows
    app.tileHeight = app.height//app.cols

    #setting up model configurations for the board 
    #template board, 
    app.colors = [([0] * app.cols) for row in range(app.rows)]
    app.currentGreenX = random.randint(0, app.cols - 1)
    app.currentGreenY = 0
    #app.colors[app.currentGreenX][app.currentGreenY] = 1
    
    #setting up sprite configurations
    url = 'http://www.cs.cmu.edu/~112/notes/sample-spritestrip.png'
    app.spritestrip = app.loadImage(url)
    app.spritestrip = app.scaleImage(app.spritestrip, 1/4)
    app.spritestrip = app.spritestrip.transpose(Image.FLIP_LEFT_RIGHT)
    app.sprites = getSprites(app, app.spritestrip)    
    app.spriteCounter = 0
    app.currentTime = 0
    
    app.timerDelay = 50

    #setting up atp configurations
    app.atpImage = app.loadImage('images/sun.png')
    app.atpImage = app.scaleImage(app.atpImage, 1/20)
    app.atpWidth, app.atpHeight = app.atpImage.size
    app.atp = []
    app.collectedATP = 100
    
    #setting up enzyme card configurations
    app.cardWidth = 80
    app.cardHeight = 90
    app.cardImgWidth = 15
    app.cardImgHeight = 15
    
    #setting up shovel image configurations
    app.shovelImage = app.loadImage('images/shovel.png')
    app.shovelImage = app.scaleImage(app.shovelImage, 1/30)
    app.shovelImage = app.shovelImage.transpose(Image.FLIP_LEFT_RIGHT)

    app.rotationMatrix = [[math.cos(0), - math.sin(0)],
                          [math.sin(0),   math.cos(0)]]
    
    #setting up starting enzyme configurations
    app.enzymes = []
    app.enzymes.append(Enzyme(app, "ATP Synthase", 25, "images/atp synthase.png", len(app.enzymes), 3, 1/4))
    app.enzymes.append(Enzyme(app, "Caspase", 50, "images/cell.jpeg", len(app.enzymes), 3, 1/10))
    app.enzymes.append(Enzyme(app, "DNA Polymerase", 100, "images/dna polymerase.png", len(app.enzymes), 2, 1/3))
    app.enzymes.append(["Shovel", 0, 0])
    
    #setting the position for each card to go in the top bar when I draw it. 
    for i in range(len(app.enzymes)):
        enzyme = app.enzymes[i]
        if isinstance(enzyme, Enzyme):
            enzyme.setPosition(80 + i*app.cardWidth, 5 + 5)
        else:
            enzyme[1], enzyme[2] = 80 + i*app.cardWidth, 5 + 5
        
    #setting up helper lists
    app.boardEnzymes = []
    app.mutations = []
    app.caspaseShoot = []
    
    #helper variables for dragging
    app.dragCard = False
    app.enzymeX = 0
    app.enzymeY = 0
    app.enzyme = None
    
    #setting up message box configurations
    app.messageBoxWidth = 200
    app.messageBoxHeight = 300
    
#crops the sprite sheet
def getSprites(app, strip):
    sprites = [ ]
    for i in range(6):
        sprite = strip.crop((7.5+65*i, 7.5, 57.5+65*i, 62.5))
        sprites.append(sprite)
    return sprites

#updates the model of the board
def updateBoard(app, event):
    #gets the cartesian coordinates of the event (i dont think this is needed)
    x, y = getCartesianCoordinates(app, event.x, event.y)
    
    #gets the row and column of the location
    row, col = getRowCol(app, x, y)

    #adds a new enzyme to the board since mouse was released
    app.boardEnzymes.append([app.enzyme, event.x, event.y])
    
    #if the enzyme added was caspase, then start shooting
    if isinstance(app.enzyme, Enzyme) and app.enzyme.name == "Caspase":
        app.caspaseShoot.append((event.x, event.y))              

    #if the enzyme was the shovel, then remove whatever enzyme was there by replacing with 0
    if not isinstance(app.enzyme, Enzyme):
        removeEnzymeFromBoard(app, app.colors[row][col], 0)
        app.colors[row][col] = 0
    
    #else, add the enzyme to the board, and update the enzyme group's locations and times
    else:  
        app.colors[row][col] = app.enzyme
        app.enzyme.times.append(0)
        app.enzyme.locations.append((event.x, event.y))
        
        #if the enzyme is dna polymerase, then start its "time left on the board"
        if isinstance(app.enzyme, Enzyme) and app.enzyme.name == "DNA Polymerase":
            app.enzyme.left.append(40)
    #app.dragCard = False

#returns back the index of the card that was clicked in the top bar 
def checkMouseInCard(app, event):
    for enzyme in app.enzymes:
        if isinstance(enzyme, Enzyme):
            if ((event.x >= enzyme.x and event.x <= enzyme.x + app.cardWidth) and
                (event.y >= enzyme.y and event.y <= enzyme.y + app.cardHeight)):
                #print(enzyme.listIndex)
                return enzyme.listIndex
        else:
            if ((event.x >= enzyme[1] and event.x <= enzyme[1] + app.cardWidth) and
                (event.y >= enzyme[2] and event.y <= enzyme[2] + app.cardHeight)):
                return len(app.enzymes) - 1
    return None

#gets the row and column of the mouse location if it's on the board
def getRowCol(app, x, y):
    col = int(y / app.tileHeight)
    row = int(x / app.tileWidth)
    return(row, col)

#places the atp at the location specified by adding it to the atp list 
def placeATP(app, x, y):
    app.atp.append([x, y])

#takes out the enzyme from the board list by checking which location needs to be removed
def removeEnzymeFromBoard(app, enzyme, index):
    i = 0
    if not isinstance(enzyme, int):
        while i < len(app.boardEnzymes):
            boardEnzyme = app.boardEnzymes[i]
            #print((boardEnzyme[1], boardEnzyme[2]), enzyme.locations[index])
            if ((boardEnzyme[1] == enzyme.locations[index][0]) and 
                (boardEnzyme[2] == enzyme.locations[index][1])):
                app.boardEnzymes.pop(i)
            else:
                i += 1

#makes an empty 2dlist
#retrieved from 112 course website
def make2dList(rows, cols):
    return [ ([0] * cols) for row in range(rows) ]

#multiplies matrices
#retrieved from previous 112 homework (my own code that I submitted that week)
def matrixMultiply(m1,m2):
    #get the sizes of both lists
    m1Rows, m1Cols = len(m1), len(m1[0])
    m2Rows, m2Cols = len(m2), len(m2[0])
    #if the dimensions don't match for matrix multiplication, return None
    if m1Cols != m2Rows:
        return None
    #make a new list, loop through the rows of m1 and cols of m2
    newMatrix = make2dList(m1Rows, m2Cols)
    for i in range(m1Rows):
        for j in range(m2Cols):
            dotProduct = 0
            #loop through each index in the row/column and add to dot product
            for k in range(m1Cols):
                dotProduct += m1[i][k] * m2[k][j]
            #add the dotproduct to the ij'th position of the new matrix
            newMatrix[i][j] = dotProduct
    return newMatrix

#changes the location of the mutation object by 
#changing previous location to 0 and next location to 1
#doesn't move if dna polymerase is there
def updateMutationLocation(app, currentX, currentY):
    print("updating!", app.colors)
    if app.currentGreenY < (app.cols - 1):
        # drow, dcol = app.directions[random.randint(0, 3)]
        # if ((app.currentGreenX + dcol >= 0 and app.currentGreenX + dcol <= app.cols) and
        if (isinstance(app.colors[currentX][currentY], Enzyme)):
            if app.colors[currentX][currentY].name == "DNA Polymerase":
                app.colors[app.currentGreenX][app.currentGreenY] = 1
        else:
            app.colors[app.currentGreenX][app.currentGreenY] = 0
            app.colors[currentX][currentY] = 1
            app.currentGreenY += 1 

#big function for drawing the main board
def drawBoard(app, canvas):
    #creates the background oval
    canvas.create_oval(0, app.height/app.cols, app.width, 
                        app.height - 20, 
                        fill = '#9CD3DB', outline = '#a9edff')
    
    #loops through each row and col in the board, 
    # gets x and y coordinates, and gets isometric coordinates from there
    for row in range(app.rows):
        for col in range(app.cols):
            x0 = row*app.tileWidth
            y0 = col*app.tileWidth
            x1 = (row + 1)*app.tileWidth
            y1 = (col + 1)*app.tileHeight
            x, y = getIsoCoordinates(app, (x0+x1)/2, (y0+y1)/2)
        
            #if the enzyme is the shovel, then remove whatever enzyme was there
            if isinstance(app.colors[row][col], list):
                color = '#9CD3DB'
                placeTile(app, x0, y0, x1, y1, canvas, color)
            
            #if the value on the board here is 1, then place the mutation there
            elif app.colors[row][col] == 1:
                placeTile(app, x0, y0, x1, y1, canvas, '#9CD3DB')
                point = [[x], [y]]
                point = matrixMultiply(app.rotationMatrix, point)
                sprite = app.sprites[app.spriteCounter]
                canvas.create_image(point[0][0], point[1][0] - 20, image=ImageTk.PhotoImage(sprite))                
                        
            #if the value on the board here is 0, then place the empty tile there
            elif app.colors[row][col] == 0:
                color = '#9CD3DB'
                placeTile(app, x0, y0, x1, y1, canvas, color)
            
            #for all other enzymes, place the image of the enzyme
            elif isinstance(app.colors[row][col], Enzyme):
                placeTile(app, x0, y0, x1, y1, canvas, color)
                canvas.create_image(x, y - 20, image=ImageTk.PhotoImage(app.colors[row][col].image))                

#draws the atp image for every atp in the list
def drawATP(app, canvas):
    for atp in app.atp:
        canvas.create_image(atp[0], atp[1], image=ImageTk.PhotoImage(app.atpImage))

#draws the atp image and amount in the top bar
def drawCollectedATP(app, canvas):
    canvas.create_image(50, 50, image=ImageTk.PhotoImage(app.atpImage))
    font = 'Sans 18'
    canvas.create_text(45, 50 + 40, text= str(app.collectedATP), 
                       font=font, anchor = 'center')

#draws the ball for caspase's shots
def drawShots(app, canvas):
    for ball in app.caspaseShoot:
        canvas.create_oval(ball[0] - 5, ball[1] - 5, ball[0] + 5, ball[1] + 5, fill = 'green')

#draws the main message box for text input (placeholder for now)
def drawMessageBox(app, canvas):
    x0 = app.width - app.messageBoxWidth - 30
    y0 = 20
    x1 = x0 + app.messageBoxWidth
    y1 = 5 + app.messageBoxHeight
    round_rectangle(canvas, x0, y0, x1, y1, fill = '#BB8D6F')
    canvas.create_rectangle(x0 + 10, y0 + 10, x1 - 10, y1 - 30, fill = '#f7f3f1')
    canvas.create_text(x0 + 10, y1 - 15, text = "MESSAGE BOX", anchor = 'w')

#creates a rectangle with rounded corners
#retrieved from 
#https://stackoverflow.com/questions/44099594/how-to-make-a-tkinter-canvas-rectangle-with-rounded-corners

def round_rectangle(canvas, x1, y1, x2, y2, r=25, **kwargs):    
    points = (x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, 
              x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, 
              x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, 
              x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, 
              x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
    return canvas.create_polygon(points, **kwargs, smooth=True)

#this function draws the entire top bar, calling the smaller functions to help
def drawTopBar(app, canvas):
    startX, startY = 5, 5
    endX, endY = startX + (app.cardWidth + 5)*len(app.enzymes) + 80, 105
    #endX, endY = 500, 105
    height, width = endX - startX, endY - startY
    round_rectangle(canvas, startX, startY, endX, endY, fill = '#BB8D6F')
    drawCollectedATP(app, canvas)
    for i in range(len(app.enzymes)):
        enzyme = app.enzymes[i]
        drawenzymeCard(enzyme, app, canvas, 80 + i*app.cardWidth, startY + 5)
    
#draws the card for the enzyme
def drawenzymeCard(enzyme, app, canvas, x, y):
    
    #if the card is a shovel, then just draw the card where we want
    if not isinstance(enzyme, Enzyme):        
        color = '#f7f3f1'
        round_rectangle(canvas, x + 5, y, x + app.cardWidth, y + app.cardHeight, r = 10, fill = color)
        font = 'Sans 10'
        canvas.create_image(x + app.cardWidth/2, y + app.cardHeight/2 - 10, image=ImageTk.PhotoImage(app.shovelImage))
        canvas.create_text(x + app.cardWidth/2, y + app.cardHeight - 25, text= "shovel", 
                        font=font, anchor = 'center')
    
    #if the card is an actual enzyme, then draw the card where we want
    #color changes based on if all the enzymes in that group are used or if there isn't enough atp to use the card
    else:
        if enzyme.available == False:
            color = '#8C9295'
        elif enzyme.notEnoughATP:
            color = '#D3D3D3'
        else: color = '#f7f3f1'
        round_rectangle(canvas, x + 5, y, x + app.cardWidth, y + app.cardHeight, r = 10, fill = color)
        font = 'Sans 10'
        canvas.create_image(x + app.cardWidth/2, y + app.cardHeight/2 - 10, image=ImageTk.PhotoImage(enzyme.image))
        canvas.create_text(x + app.cardWidth/2, y + app.cardHeight - 25, text= str(enzyme.name), 
                        font=font, anchor = 'center')
        canvas.create_text(x + app.cardWidth/2, y + app.cardHeight - 10, text= str(enzyme.pointValue), 
                        font=font, anchor = 'center')

#gets the coordinates at each corner of the square
#uses isometric function to calculate isometric coordinates
#rotates the tile if needed
#creates a polygon with these 4 points 
def placeTile(app, x0, y0, x1, y1, canvas, color):

    isox0, isoy0 = getIsoCoordinates(app, x0, y0)
    rotation = matrixMultiply(app.rotationMatrix, [[isox0], [isoy0]])
    isox0, isoy0 = rotation[0], rotation[1]
    
    isox1, isoy1 = getIsoCoordinates(app, x1, y0)
    rotation = matrixMultiply(app.rotationMatrix, [[isox1], [isoy1]])
    isox1, isoy1 = rotation[0], rotation[1]
    
    isox2, isoy2 = getIsoCoordinates(app, x1, y1)
    rotation = matrixMultiply(app.rotationMatrix, [[isox2], [isoy2]])
    isox2, isoy2 = rotation[0], rotation[1]
    
    isox3, isoy3 = getIsoCoordinates(app, x0, y1)
    rotation = matrixMultiply(app.rotationMatrix, [[isox3], [isoy3]])
    isox3, isoy3 = rotation[0], rotation[1]

    canvas.create_polygon(isox0, isoy0, isox1, isoy1,
                          isox2, isoy2, isox3, isoy3, 
                          fill = color, outline = '#a9edff')

#gets the isometric coordinates by performing a system of equations
#I actually did not adapt this from anywhere
#I manually drew out a board and came up with my own formula
#I have a page in my notebook where I did this for proof, if needed :)
def getIsoCoordinates(app, x, y):
    x_grid = app.width/2 + 1.25*(x - y)/3
    y_grid = app.height/app.cols + 1.25*(x + y)/(app.cols/2)
    return(x_grid, y_grid)

#does the reverse of getIsoCoordinates
#i solved the system of equations and rewrote the new variable formulas
#but i will change this when I get rotation working
def getCartesianCoordinates(app, x_grid, y_grid):
    x = (6*x_grid + app.cols*y_grid - app.height - 3*app.width)/5
    y = (app.cols*y_grid - 6*x_grid - app.height + 3*app.width)/5
    return(x, y)

runApp(width=1200, height=1200)
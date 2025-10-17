import png
import random


# width and height of the maze
width  = 100
height = 100

# controls the width of the halls
mazeScale = 6
# scales the image so it's a reasonable size
imageScale = 1





class Maze:
	def __init__(self, width, height):
		self.width  = width
		self.height = height
		# the first bit represents being connected to the cell to the right of it
		# the second, the cell above it
		# the third, left, and the fourth, down
		self.cells  = [[0 for x in range(width)] for y in range(height)]
		self.expandables = []

	# prints the pathways to the terminal
	def Print(self):
		for y in range(self.height):
			line = ''
			for x in range(self.width):
				match self.cells[y][x]:
					case 0:
						line+='\u2588'
					case 1:
						line+='\u2576'
					case 2:
						line+='\u2577'
					case 3:
						line+='\u250C'
					case 4:
						line+='\u2574'
					case 5:
						line+='\u2500'
					case 6:
						line+='\u2510'
					case 7:
						line+='\u252C'
					case 8:
						line+='\u2575'
					case 9:
						line+='\u2514'
					case 10:
						line+='\u2502'
					case 11:
						line+='\u251C'
					case 12:
						line+='\u2518'
					case 13:
						line+='\u2534'
					case 14:
						line+='\u2524'
					case 15:
						line+='\u253C'
			print(line)

	# prints the numbers in the array
	def PrintNumbers(self):
		for y in range(self.height):
			print(self.cells[y])

	def AddConnection(self, x, y, direction):
		self.cells[y][x] |= direction
		match direction:
			case 1:
				if x+1!=self.width:
					self.cells[y][x+1] |= 4
			case 2:
				if y+1!=self.height:
					self.cells[y+1][x] |= 8
			case 4:
				if x!=0:
					self.cells[y][x-1] |= 1
			case 8:
				if y!=0:
					self.cells[y-1][x] |= 2
			case _:
				print('unhandled direction')

	def RemoveConnection(self, x, y, direction):
		self.cells[y][x] ^= direction
		match direction:
			case 1:
				if x+1!=self.width:
					self.cells[y][x+1] ^= 4
			case 2:
				if y+1!=self.height:
					self.cells[y+1][x] ^= 8
			case 4:
				if x!=0:
					self.cells[y][x-1] ^= 1
			case 8:
				if y!=0:
					self.cells[y-1][x] ^= 2
			case _:
				print('unhandled direction')

	def GetDirections(self, x, y):
		output = []
		if x+1!=self.width:
			output.append(1)
		if y+1!=self.height:
			output.append(2)
		if y>0:
			output.append(8)
		if x>0:
			output.append(4)
		return output

	def CellInDirection(self, x, y, direction):
		match direction:
			case 1:
				return [x+1, y]
			case 2:
				return [x, y+1]
			case 4:
				return [x-1, y]
			case 8:
				return [x, y-1]
			case _:
				print('unhandled direction')

	def GetAvailableDirections(self, x, y):
		directions = self.GetDirections(x, y)
		output = []
		for direction in directions:
			neighbourX, neighbourY = self.CellInDirection(x, y, direction)
			if self.cells[neighbourY][neighbourX]==0:
				output.append(direction)
		return output

	def GetVisitedCells(self):
		output = []
		for y in range(self.height):
			for x in range(self.width):
				if self.cells[y][x]!=0:
					output.append([x, y])
		return output

	def RandomConnection(self, x, y):
		directions = self.GetAvailableDirections(x, y)
		if len(directions)>=0:
			direction = random.choice(directions)
			self.AddConnection(x, y, direction)



def SaveImage(image, palette, name):
	width    = len(image[0])
	height   = len(image)

	w = png.Writer(size=(width, height), palette=palette, bitdepth=8)
	with open(name+'.png', "wb") as f:
		w.write(f, image)



def CreateGrid(image):
	height = len(image)
	width  = len(image[0])

	for y in range(height):
		for x in range(width):
			if x%mazeScale==0 or y%mazeScale==0:
				image[y][x] = 0



def ScaleImage(image, scale):
	height = len(image)
	width  = len(image[0])

	scaledImage = []
	for y in image:
		scaledRow = []
		for x in y:
			for i in range(scale):
				scaledRow.append(x)
		for i in range(scale):
			scaledImage.append(scaledRow)
	return scaledImage



def MazeToImage(maze):
	image   = [[1 for x in range(mazeScale*width+1)] for y in range(mazeScale*height+1)]
	CreateGrid(image)

	for y in range(height):
		for x in range(width):
			if maze.cells[y][x] & 1  !=  0:
				for i in range(mazeScale-1):
					image[mazeScale*y+1 + i][mazeScale*x+mazeScale] = 1

			if maze.cells[y][x] & 2  !=  0:
				for i in range(mazeScale-1):
					image[mazeScale*y+mazeScale][mazeScale*x+1 + i] = 1

			if maze.cells[y][x] & 4  !=  0:
				for i in range(mazeScale-1):
					image[mazeScale*y+1 + i][mazeScale*x] = 1

			if maze.cells[y][x] & 8  !=  0:
				for i in range(mazeScale-1):
					image[mazeScale*y][mazeScale*x+1 + i] = 1


	for row in image:
		for i in range(2*mazeScale):
			row.append(1)
			row.insert(0, 1)

	margins = []
	for i in range(len(image[0])):
		margins.append(1)
	for i in range(2*mazeScale):
		image.append(margins)
		image.insert(0, margins)
	

	palette = [(0x20,0x20,0x20), (0xFF,0xFF,0xFF)]
	SaveImage(ScaleImage(image, imageScale), palette, 'maze')



def Prim(maze):
	startX = width//2
	startY = height//2
	directions = random.choice(maze.GetAvailableDirections(startX, startY))
	maze.AddConnection(startX, startY, directions)
	edges = maze.GetVisitedCells()

	while len(edges)!=0:
		x, y = random.choice(edges)
		directions = maze.GetAvailableDirections(x, y)
		if len(directions)!=0:
			direction = random.choice(directions)

			if x>y:
				if 2 in directions:
					direction = 2
				elif 1 in directions:
					direction = 1
			else:
				if 1 in directions:
					direction = 1
				elif 2 in directions:
					direction = 2

			maze.AddConnection(x, y, direction)
			edges.append(maze.CellInDirection(x, y, direction))
		else:
			edges.remove([x, y])



def HAK(maze):
	def FindValidStart():
		x, y = random.randrange(width), random.randrange(height)
		while True:
			if maze.cells[y][x]!=0 and len(maze.GetAvailableDirections(x, y))>0:
				return [x, y]
			else:
				x = (x+1)%width
				if x==0:
					y = (y+1)%width

	def Explore(x, y):
		while len(maze.GetAvailableDirections(x, y))!=0:
			directions = maze.GetAvailableDirections(x, y)
			direction  = random.choice(directions)
			maze.AddConnection(x, y, direction)
			x, y = maze.CellInDirection(x, y, direction)

	maze.RandomConnection(width//2, height//2)
	numberOfCellsVisited = len(maze.GetVisitedCells())
	while numberOfCellsVisited < width*height:
		x, y = FindValidStart()
		Explore(x, y)
		numberOfCellsVisited = len(maze.GetVisitedCells())



def LimitedHAK(maze, maxDepth):
	def FindValidStart():
		x, y = random.randrange(width), random.randrange(height)
		while True:
			if maze.cells[y][x]!=0 and len(maze.GetAvailableDirections(x, y))>0:
				return [x, y]
			else:
				x = (x+1)%width
				if x==0:
					y = (y+1)%width

	def Explore(x, y, maxDepth):
		depth = 0
		while len(maze.GetAvailableDirections(x, y))!=0 and depth<maxDepth:
			directions = maze.GetAvailableDirections(x, y)
			direction  = random.choice(directions)
			maze.AddConnection(x, y, direction)
			x, y = maze.CellInDirection(x, y, direction)
			depth+=1

	maze.RandomConnection(width//2, height//2)
	numberOfCellsVisited = len(maze.GetVisitedCells())
	while numberOfCellsVisited < width*height:
		x, y = FindValidStart()
		Explore(x, y, maxDepth)
		numberOfCellsVisited = len(maze.GetVisitedCells())





maze = Maze(width, height)
Prim(maze)
#HAK(maze)
#LimitedHAK(maze, 32)

#maze.Print()
MazeToImage(maze)

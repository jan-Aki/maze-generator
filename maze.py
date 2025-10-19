import numpy as np
import png
import random





class Maze:
	def __init__(self, size):
		self.dimension = len(size)

		self.size = 1
		for length in size:
			self.size*=length

		size.append(self.dimension) # for connections
		self.cells = np.zeros(size, int)

		self.visitedCells = []
		self.origin = tuple([0 for _ in range(self.dimension)])

	def CellInDirection(self, cell, direction):
		# first bit is forwards in that dimension
		# second is backwards in that dimension
		output = []
		for c, d in zip(cell, direction):
			match d:
				case 0:
					output.append(c)
				case 1:
					output.append(c+1)
				case 2:
					output.append(c-1)
				case _:
					print(f"unhandled direction {d}")
		return tuple(output)

	def AddConnection(self, cell, direction):
		def NegateTuple(tup):
			output = []
			for t in tup:
				match t:
					case 0:
						output.append(0)
					case 1:
						output.append(2)
					case 2:
						output.append(1)
					case _:
						print(f"tried to negate {t}")
			return tuple(output)
		
		connectingTo = self.CellInDirection(cell, direction)
		self.cells[cell] |= direction
		self.cells[connectingTo] |= NegateTuple(direction)
		if cell not in self.visitedCells:
			self.visitedCells.append(cell)
		if connectingTo not in self.visitedCells:
			self.visitedCells.append(connectingTo)
	
	def RemoveConnection(self, cell, direction):
		def NegateTuple(tup):
			output = []
			for t in tup:
				match t:
					case 0:
						output.append(0)
					case 1:
						output.append(2)
					case 2:
						output.append(1)
					case _:
						print(f"tried to negate {t}")
			return tuple(output)
		
		connectingTo = self.CellInDirection(cell, direction)
		self.cells[cell] ^= direction
		self.cells[connectingTo] ^= NegateTuple(direction)
		if self.cells[cell]==tuple([0 for _ in range(self.dimension)]):
			self.visitedCells.remove(cell)
		if self.cells[connectingTo]==tuple([0 for _ in range(self.dimension)]):
			self.visitedCells.remove(connectingTo)
		
	def AlreadyVisited(self, cell):
		for direction in self.cells[cell]:
			if direction>0:
				return True
		return False
	
	def GetDirections(self, cell):
		def CellInGrid(cell):
			for i in range(self.dimension):
				if cell[i]<0 or cell[i]>=self.cells.shape[i]:
					return False
			return True

		output = []
		for d in range(self.dimension):
			forwards = tuple([0 for _ in range(d)]) + tuple([1]) + tuple([0 for _ in range(self.dimension-d-1)])
			backwards = tuple([0 for _ in range(d)]) + tuple([2]) + tuple([0 for _ in range(self.dimension-d-1)])
			fwCell = self.CellInDirection(cell, forwards)
			bwCell = self.CellInDirection(cell, backwards)
			if CellInGrid(fwCell):
				output.append(forwards)
			if CellInGrid(bwCell):
				output.append(backwards)
		return output

	def GetAvailableDirections(self, cell):
		directions = self.GetDirections(cell)
		output = []
		for direction in directions:
			neighbour = self.CellInDirection(cell, direction)
			if not self.AlreadyVisited(neighbour):
				output.append(direction)
		return output

	def RandomConnection(self, cell):
		directions = self.GetAvailableDirections(cell)
		if len(directions)>0:
			direction = random.choice(directions)
			self.AddConnection(cell, direction)



def MazeToPNG(maze, mazeScale, imageScale):
	if maze.dimension!=2:
		print('Can only make PNGs of 2d mazes')
		return

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


	width  = len(maze.cells[0])
	height = len(maze.cells)

	image   = [[1 for x in range(mazeScale*width+1)] for y in range(mazeScale*height+1)]
	CreateGrid(image)

	for y in range(height):
		for x in range(width):
			if maze.cells[y][x][1] in [1, 3]:
				for i in range(mazeScale-1):
					image[mazeScale*y+1 + i][mazeScale*x+mazeScale] = 1

			if maze.cells[y][x][0] in [1, 3] :
				for i in range(mazeScale-1):
					image[mazeScale*y+mazeScale][mazeScale*x+1 + i] = 1

			if maze.cells[y][x][1] in [2, 3]:
				for i in range(mazeScale-1):
					image[mazeScale*y+1 + i][mazeScale*x] = 1

			if maze.cells[y][x][0] in [2, 3]:
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



def ChooseBranchDirection(directions):
	return random.choice(directions)



def HAK(maze):
	def FindValidStart(maze, edges):
		originalEdges = edges
		for cell in originalEdges:
			if len(maze.GetAvailableDirections(cell))>0:
				return [cell, edges]
			else:
				edges.remove(cell)
		return [-1, []]

	def Explore(maze, cell, edges):
		directions = maze.GetAvailableDirections(cell)
		while len(directions)>0:
			direction = ChooseBranchDirection(directions)
			maze.AddConnection(cell, direction)
			cell = maze.CellInDirection(cell, direction)
			directions = maze.GetAvailableDirections(cell)
			if (cell not in edges) and (len(directions)>0):
				edges.append(cell)
		return edges

	maze.RandomConnection(maze.origin)
	edges = [maze.origin]
	cell, edges = FindValidStart(maze, edges)
	while len(edges)>0:
		edges = Explore(maze, cell, edges)
		cell, edges = FindValidStart(maze, edges)



sidelength = 3
dimension  = 12

maze = Maze([sidelength for _ in range(dimension)])
HAK(maze)
print(maze.cells)
#MazeToPNG(maze, 6, 2)
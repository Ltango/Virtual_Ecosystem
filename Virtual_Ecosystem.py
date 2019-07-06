#!/usr/bin/python
import numpy as np
import time
import random
import sys





#Fun little simulation game, attempt to create a self sustaining ecosystem by tinkering with the parameters.  Will extend this project to attempt machine
#learning that will find the most effective variables for the longest sustained virtual ecosystem







#number of snakes we start with
numSnakes = 50
#number of rats we start with
numRats = 100
#number of bushes we start with
numBush = 75
#grid X size
xsize = 20
#grid Y size
ysize = 20
#global variable holding the list of all current elements alive
elements = list()
#global variable to keep track of a unique ID for each element (snake/rat/bush) starting at 1
currentID = 1
#maximum age a snake will live to before it has a chance of dying to old age
max_snake_age = 50
#maximum age a rat will live to before it has a chance of dying to old age
max_rat_age = 20
#maximum age a bush will live to before it has a chance of dying to old age
max_bush_age = 100
#how much food value will be added to an element for eating part of a bush and removed that much food attribute from the bush
bush_food_value = 90
#how much food value will be added to an element for eating a rat
rat_food_value = 400
#how much food value a baby snake start with (also takes away that much food value from the parent snake)
baby_snake_starting_food_value = 250
#how much food value a baby rat start with (also takes away that much food value from the parent rat)
baby_rat_starting_food_value = 70
#minimum age a snake will begin to breed
snake_breed_age = 20
#minimum age a rat will begin to breed
rat_breed_age = 3
#A bush will only spread to another random adjacent square once every one of these values
bush_reproduce_years = 10
#A bush will only begin spreading after this amount of turns
bush_mature_age = 2
#How much a new bush's food value will be
bush_starting_food_value = 200
#How much added food value to a bush will be every turn
bush_food_growth_value = 50
#How much food is removed from every animal every turn
food_decay = 5
#The chance a snake would be successful attempting to hunt a rat in a nearby or the same square
snake_kill_chance = 0.04
#Chance a snake will breed with an adjacent snake if all other conditions are met
snake_chance_to_breed = 0.30
#Chance a rat will breed with an adjacent rat if all other conditions are met
rat_chance_to_breed = 0.75
#Chance any living thing will die if their age is over their maximum age
chance_to_die_of_old_age = 0.33
#Bush will not add more food to itself if its food attribute is above this value
bush_full_food_value = 1500
#Snake will not attempt to hunt a rat if its food attribute is above this value
snake_full_food_value = 300
#Rat will not eat from a bush if its food attribute is above this value
rat_full_food_value = 20
#A limiter set on breeding, if [max_units_in_square] elements are already in the square of the animal attempting to breed it will fail
#NOTE: this does not prevent more than 2 elements in a square, only prevents breeding.  This is probably a bad variable name
max_units_in_square = 2


#Animals are based on this class
class Animal:
	def __init__(self, id, name, age, size, fitness, xpos, ypos, food):
		self.name = name
		self.id = id
		self.__age = age
		self.size = size
		self.fitness = fitness
		self.__xpos = xpos
		self.__ypos = ypos
		self.__food = food

	def get_xpos(self):
		return self.__xpos

	def get_ypos(self):
		return self.__ypos

	def set_xpos(self, xposition):
		self.__xpos = xposition

	def set_ypos(self, yposition):
		self.__ypos = yposition

	def get_age(self):
		return self.__age

	def set_age(self, age):
		self.__age = age

	def get_food(self):
		return self.__food

	def set_food(self, food):
		self.__food = food

#Plants are based on this class
class Plant:
	def __init__(self, id, name, age, size, xpos, ypos, food):
		self.name = name
		self.id = id
		self.__age = age
		self.size = size
		self.__xpos = xpos
		self.__ypos = ypos
		self.__food = food

	def get_xpos(self):
		return self.__xpos

	def get_ypos(self):
		return self.__ypos

	def set_xpos(self, xposition):
		self.__xpos = xposition

	def set_ypos(self, yposition):
		self.__ypos = yposition

	def get_age(self):
		return self.__age

	def set_age(self, age):
		self.__age = age

	def get_food(self):
		return self.__food

	def set_food(self, food):
		self.__food = food


#Deletes element from the grid based on ID
def deleteElementFromGrid(element):
	global grid
	for x in range(len(grid)):
		for y in range(len(grid[0])):
			for entry in grid[x][y]:
				if(entry.id == element.id):
					grid[x][y].remove(entry)
					return

#Deletes elements from the master list based on ID
def deleteElementFromElementList(element):
	global elements
	for item in elements:
		if(item.id == element.id):
			elements.remove(item)
			return


#Returns all neighbor coordinates that exist on the board.  Does not return the spot the element begins on.
def ValidGridSpots(x, y):
	global grid
	spots = list()
	if(x - 1 >= 0):
		spots.append([x - 1, y])
		if(y - 1 >= 0):
			spots.append([x - 1, y - 1])
		if(y + 1 < len(grid[0])):
			spots.append([x - 1, y + 1])
	if(x + 1 < len(grid)):
		spots.append([x + 1, y])
		if(y - 1 >= 0):
			spots.append([x + 1, y - 1])
		if(y + 1 < len(grid[0])):
			spots.append([x + 1, y + 1])
	if(y + 1 < len(grid[0])):
		spots.append([x, y + 1])
	if(y - 1 >= 0):
		spots.append([x, y - 1])
	#print(spots)
	return(spots)


#Uses ValidGridSpots() on the passed element and creates a list of all elements next to the element and the elements sharing the square
def findLocales(element):
	global grid
	x = element.get_xpos()
	y = element.get_ypos()
	validspots = ValidGridSpots(x,y)
	validspots.append([x,y])
	nearby = list()
	for spot in validspots:
		if(grid[spot[0]][spot[1]]):
			for item in grid[spot[0]][spot[1]]:
				nearby.append(item)
	return(nearby)


#Extends from Animal
#First checks to see if there are any rats neighboring the snake
#If there is it will attempt [snake_kill_chance] to eat the rat IF its self.food < snake_full_food_value
#If this fails it will check for Snakes to breed with
#Will create a new baby Snake if the conditions are met
#	1. The selected nearby snake is at least the minimum breeding age for snakes
#	2. This Snake is at least the minimum breeding age for snakes
#	3. This Snake has enough food to subtract [baby_snake_starting_food_value] from itself
#	4. There is not more than [max_units_in_square] in the current square
#	5. Additionally there is only a [snake_chance_to_breed] chance the snake will still breed
#If the Snake has not eaten after attempting to it will move to a random eligible neighbor spot
class Snake(Animal):
	def __init__(self, id, name, age, size, fitness, xpos, ypos, food, deathAge = max_snake_age):
		Animal.__init__(self, id, name, age, size, fitness, xpos, ypos, food)
		self.name = name
		self.id = id
		self.size = size
		self.fitness = fitness
		self.speed = fitness/size
		self.deathAge = deathAge

	def behavior(self):
		global grid
		global elements
		eaten = False
		#print(findLocales(self))
		for option in findLocales(self):
			if(isinstance(option, Rat) and self.get_food() < snake_full_food_value):
				if(random.randint(1,100) > snake_kill_chance * 100):
					break
				self.set_xpos(option.get_xpos())
				self.set_ypos(option.get_ypos())
				deleteElementFromGrid(self)
				grid[option.get_xpos()][option.get_ypos()].append(self)
				deleteElementFromElementList(option)
				deleteElementFromGrid(option)
				self.set_food(self.get_food() + rat_food_value)
				break
			if(isinstance(option, Snake)):
				if(option.get_age() >= snake_breed_age and self.get_age() >= snake_breed_age and self.get_food() > baby_snake_starting_food_value and random.randint(1,100) <= snake_chance_to_breed * 100 and len(grid[self.get_xpos()][self.get_ypos()]) <= max_units_in_square):
					global currentID
					self.set_food(self.get_food() - baby_snake_starting_food_value)
					babySnake = Snake(currentID, "S",0,1,10,self.get_xpos(),self.get_ypos(), baby_snake_starting_food_value)
					grid[self.get_xpos()][self.get_ypos()].append(babySnake)
					elements.append(babySnake)
					currentID = currentID + 1
					break
		if(not eaten):
			spots = ValidGridSpots(self.get_xpos(), self.get_ypos())
			chosen_spot = spots[random.randint(0,len(spots) - 1)]
			self.set_xpos(chosen_spot[0])
			self.set_ypos(chosen_spot[1])
			deleteElementFromGrid(self)
			grid[chosen_spot[0]][chosen_spot[1]].append(self)


#Extends from Animal
#First checks to see if there are any bushes neighboring the rat
#If there is it will remove [bush_food_value] from the bush and add it to itself IF self.food < rat_full_food_value
#If this fails it will check for Rats to breed with
#Will create a new baby Rat if the conditions are met
#	1. The selected nearby rat is at least the minimum breeding age for rats
#	2. This rat is at least the minimum breeding age for rats
#	3. This rat has enough food to subtract [baby_rat_starting_food_value] from itself
#	4. There is not more than [max_units_in_square] in the current square
#	5. Additionally there is only a [rat_chance_to_breed] chance the rat will still breed
#The Rat will then move to a random eligible neighbor spot
class Rat(Animal):
	def __init__(self, id, name, age, size, fitness, xpos, ypos, food, deathAge = max_rat_age):
		Animal.__init__(self, id, name, age, size, fitness, xpos, ypos, food)
		self.name = name
		self.id = id
		self.size = size
		self.fitness = fitness
		self.speed = fitness/size
		self.deathAge = deathAge

	def behavior(self):
		global grid
		global elements
		spots = ValidGridSpots(self.get_xpos(), self.get_ypos())
		chosen_spot = spots[random.randint(0,len(spots) - 1)]
		self.set_xpos(chosen_spot[0])
		self.set_ypos(chosen_spot[1])
		deleteElementFromGrid(self)
		grid[chosen_spot[0]][chosen_spot[1]].append(self)
		for option in findLocales(self):
			if(isinstance(option, Bush) and self.get_food() < rat_full_food_value):
				self.set_food(self.get_food() + bush_food_value)
				option.set_food(option.get_food() - bush_food_value)
				if(option.get_food() <= 0):
					deleteElementFromElementList(option)
					deleteElementFromGrid(option)
					
				break
		for option in findLocales(self):
			if(isinstance(option, Rat)):
				if(option.get_age() >= rat_breed_age and self.get_age() >= rat_breed_age and self.get_food() > baby_rat_starting_food_value and random.randint(1,100) <= rat_chance_to_breed * 100 and len(grid[self.get_xpos()][self.get_ypos()]) <= max_units_in_square):
					global currentID
					self.set_food(self.get_food() - baby_rat_starting_food_value)
					babyRat = Rat(currentID, "R",0,1,10,self.get_xpos(),self.get_ypos(), baby_rat_starting_food_value)
					grid[self.get_xpos()][self.get_ypos()].append(babyRat)
					elements.append(babyRat)
					currentID = currentID + 1
					break

#Extends from Plant
#First feeds itself from the void if self.food < bush_full_food_value
#Then will create a new bush every [bush_reproduce_years] and its age is at least the mature age for bushes
#This bush location is determined at random from eligible neighbor squares that do not already have a bush
class Bush(Plant):
	def __init__(self, id, name, age, size, xpos, ypos, food, deathAge = max_bush_age):
		Plant.__init__(self, id, name, age, size, xpos, ypos, food)
		self.name = name
		self.id = id
		self.size = size
		self.deathAge = deathAge

	def behavior(self):
		global currentID
		global grid
		potential_spots = list()
		plantFound = False
		if(self.get_food() < bush_full_food_value):
			self.set_food(self.get_food() + bush_food_growth_value)
		if(self.get_age() % bush_reproduce_years == 0 and self.get_age() >= bush_mature_age):
			spots = ValidGridSpots(self.get_xpos(), self.get_ypos())
			for spot in spots:
				plantFound = False
				for item in grid[spot[0]][spot[1]]:
					if(isinstance(item, Plant)):
						plantFound = True
				if(not plantFound):
					potential_spots.append(spot)
			if(len(potential_spots) == 0):
				return
			random_chosen_spot = potential_spots[random.randint(0, len(potential_spots) - 1)]
			self.set_food(self.get_food() - bush_starting_food_value)
			babyBush = Bush(currentID, "B",0,1,10,random_chosen_spot[0],random_chosen_spot[1], bush_starting_food_value)
			grid[random_chosen_spot[0]][random_chosen_spot[1]].append(babyBush)
			elements.append(babyBush)
			currentID = currentID + 1


#Prints information of the current simulation status and exits the program if if any of the 3 elements hit 0
def printstatus():
	global elements
	current_bushes = 0
	current_rats = 0
	current_snakes = 0
	c_bush_age = 0
	c_bush_food = 0
	c_rat_age = 0
	c_rat_food = 0
	c_snake_age = 0
	c_snake_food = 0	
	for element in elements:
		if(isinstance(element, Bush)):
			current_bushes = current_bushes + 1
			c_bush_age = c_bush_age + element.get_age()
			c_bush_food = c_bush_food + element.get_food()
		if(isinstance(element, Rat)):
			current_rats = current_rats + 1
			c_rat_age = c_rat_age + element.get_age()
			c_rat_food = c_rat_food + element.get_food()			
		if(isinstance(element, Snake)):
			current_snakes = current_snakes + 1
			c_snake_age = c_snake_age + element.get_age()
			c_snake_food = c_snake_food + element.get_food()
	if(current_bushes == 0 or current_rats == 0 or current_snakes == 0):
		sys.exit()
	print("Snakes: " + str(current_snakes) + " Avg Age: " + str(c_snake_age/current_snakes) + " Avg Food: " + str(c_snake_food/current_snakes))
	print("Rats: " + str(current_rats) + " Avg Age: " + str(c_rat_age/current_rats) + " Avg Food: " + str(c_rat_food/current_rats))
	print("Bushes: " + str(current_bushes) + " Avg Age: " + str(c_bush_age/current_bushes) + " Avg Food: " + str(c_bush_food/current_bushes))


#Print the 2D array of elements for a visual aid.  Not perfect when the critters breed out of control.
def printGrid():
	global grid
	sb = "=======" * len(grid) + "\n"
	for x in range(len(grid)):
		for y in range(len(grid[0])):
			if(not grid[x][y]):
				sb += ". . ."
			else:
				for item in grid[x][y]:
					sb += item.name
			sb += "\t"
		sb += "\n\n"
	sb += "=======" * len(grid)
	print(sb)

#Not used
def updateGrid(element):
	global grid
	grid[element.get_xpos()][element.get_ypos()] = element


#Updates the global variable list of the specified element so that its x,y coordinates match its position in the grid
def updateElementFromGrid(gridx, gridy, currentSquare):
	for element in currentSquare:
		element.set_xpos(gridx)
		element.set_ypos(gridy)


#Is called every turn
#Checks to see if elements are passed their maximum age and attempts to kill them if they are
#If the elements has <= 0 food then it dies
#incriment the age of every element
#Decay the food from every animal (should probably change this to emulate behavior better and only decay food if the animal moves...  hmmm or both maybe
def updater():
	global elements
	for element in elements:
		if(element.get_age() > element.deathAge and random.randint(1,100) <= chance_to_die_of_old_age * 100):
			deleteElementFromGrid(element)
			deleteElementFromElementList(element)
			continue
		if(isinstance(element, Animal) or isinstance(element, Plant)):
			if(element.get_food() <= 0):
				deleteElementFromGrid(element)
				deleteElementFromElementList(element)
				continue
			
	for element in elements:		
		element.set_age(element.get_age() + 1)
		if(isinstance(element, Animal)):
			element.set_food(element.get_food() - food_decay)
		element.behavior()


#Create random elements for the master list based on the variables and append them to the master list
#id, name, age, size, fitness, xpos, ypos, food
for x in range(numSnakes):
	elements.append(Snake(currentID,"S",random.randint(0,max_snake_age),1,10,0,0, random.randint(1,100)))
	currentID = currentID + 1
for x in range(numRats):
	elements.append(Rat(currentID, "R",random.randint(0,max_rat_age),1,10,0,0, random.randint(1,100)))
	currentID = currentID + 1
for x in range(numBush):
	elements.append(Bush(currentID, "B",random.randint(0,max_bush_age),1,0,0, random.randint(1,100)))
	currentID = currentID + 1
#Create the empty grid
grid = [[list() for i in range(xsize)] for j in range(ysize)]


#Main logic
def main():
	global currentID
	global grid
	global elements
	i = 0
	j = 0
	#put the elements from the master element list into the grid
	for element in elements:
		grid[i][j].append(element)
		if(i>=xsize-1):
			i=-1
			j=j+1
		i=i+1
	#forceSnake = Snake(currentID, "fS",0,1,10,0,0, random.randint(1,100))
	#grid[0][0].append(forceSnake)
	#elements.append(forceSnake)
	#currentID = currentID + 1
	
	#shuffle the grid on both x and y axis
	np.random.shuffle(grid)
	for ii, sublist in enumerate(grid): 
		np.random.shuffle(grid[ii])

	#update every element's xpos,ypos values according to their new grid values
	for x in range(len(grid)):
		for y in range(len(grid[0])):
			if(grid[x][y]):
				updateElementFromGrid(x,y,grid[x][y])


	#Main logic loop

	#printGrid()
	turn = 1
	time.sleep(0.1)
	while True:
		for x in range(len(grid)):
			for y in range(len(grid[0])):
				if(grid[x][y] is not None):
					updateElementFromGrid(x,y,grid[x][y])
		updater()
		printGrid()
		print("Turn: " + str(turn))
		turn = turn + 1
		printstatus()
		time.sleep(0.1)

main()





















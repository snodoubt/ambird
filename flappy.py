import pygame
import time
import os
import random
import neat
pygame.font.init()

#define screen as a constant for testing.  
# change later
WIN_WIDTH = 500
WIN_WEIGHT = 800

##what needs to be objects and what doesn't

##bring in images and assign (the bird, the background, the pipes, the base)
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

#create a class for bird and define attributes so it can animate
class Bird:
	IMGS = BIRD_IMGS
	MAX_ROTATION =25
	ROT_VEL = 20
	ANIMATION_TIME = 5 #how long show each bird animation (how fast it flaps its wings)

#starting postition of bird
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.tilt = 0 #(bird looking flat ahead)
		self.tick_count = 0
		self.vel = 0
		self.height = self.y
		self.img_count = 0 #(shows which image we are displaying as part of animation)
		self.img = self.IMGS[0]


  #when jump reset tick count to 0
	def jump(self):
		self.vel = -10.5 #give negative so it goes against  "gravity"  down is postiive vel
		self.tick_count = 0 #to know when we last jumped / change velocity
		self.height = self.y #where we jumped from

	def move(self): #what we call each time to move our bird A tick happend and a frame went by
		self.tick_count += 1

		#displacement aka how far we moved
		d = self.vel*self.tick_count + 1.5*self.tick_count**2
		#-10.5 + the 1.5 times 1 raised to the 2nd power

		if d >= 16:
			#d = d/abs(d) * 16
			d = 16

		if d< 0:
			d -= 2

		self.y = self.y + d

#make it fall but only after it has passed the height before changing animation
		if d < 0 or self.y < self.height + 50:
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION
		else:
			if self.tilt > -90: #when we fall we want to to point down
				self.tilt -= self.ROT_VEL



	def draw(self, win):  #we need to keep track of how many ticks we ahve shown the current image for
		self.img_count += 1

	#what image do we show based on the current image count. make wings move up and down
		if self.img_count < self.ANIMATION_TIME: #if less than 5 show this
			self.img = self.IMGS[0]
		elif self.img_count < self.ANIMATION_TIME*2: #if less that 10 (5 * 2) show second img
			self.img = self.IMGS[1]
		elif self.img_count < self.ANIMATION_TIME*3:
			self.img = self.IMGS[2]
		elif self.img_count < self.ANIMATION_TIME*4: # reverse order back down to first image
			self.img = self.IMGS[1]
		elif self.img_count < self.ANIMATION_TIME*4 + 1:
			self.img = self.IMGS[0]
			self.img_count = 0 

	# if image is down facing don't flap
		if self.tilt <= -80:
			self.img = self.IMGS[1]
			self.img_count = self.ANIMATION_TIME*2

		#roate an image around its center in pygame
		rotated_image = pygame.transform.rotate(self.img, self.tilt)
		new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
		win.blit(rotated_image, new_rect.topleft)

	def get_mask(self):
		return pygame.mask.from_surface(self.img)

class Pipe:
	GAP = 200 #space between pipe
	VEL = 5 #need to move pipes toward bird

	def __init__(self, x):
		self.x = x #give random height
		self.height = 0

#create variables to track where the boundary of the pipe will be drawn
#flip the pipe to make a top and bottom
		self.top = 0
		self.bottom = 0
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) #get image for pipe and flip it since it needs to come from the top
		self.PIPE_BOTTOM = PIPE_IMG

		self.passed = False
		self.set_height() #define where the top and bottom is and how tall each are

	def set_height(self):
		self.height = random.randrange(50, 450)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.GAP

	def move(self): #move pipe to the left a little based on the velocity
		self.x -= self.VEL

	def draw(self, win):
		win.blit(self.PIPE_TOP, (self.x, self.top))
		win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

#collision pygame functions mask collisions 2d list to compare
	def collide(self, bird, win):
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

		top_offset = (self.x - bird.x, self.top - round(bird.y)) #round so no negative
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

		b_point = bird_mask.overlap(bottom_mask, bottom_offset)
		t_point = bird_mask.overlap(top_mask, top_offset)

		#check if they exist not none, if so they are colliding.  evertime we move check for
		#collision 
		if t_point or b_point:
			return True

		return False

#we need a class because this needs to move / animate.  tom and jerry style
#we speed same as pipe vel
#need the first image to be follwed the second image and they chase each other

class Base:
	VEL = 5
	WIDTH = BASE_IMG.get_width()
	IMG = BASE_IMG

	def __init__(self, y):
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH

	def move(self,):
		self.x1 -= self.VEL
		self.x2 -= self.VEL

#once image gets off the screen moves to the second image space
		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH

		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self, win):
		win.blit(self.IMG, (self.x1, self.y))
		win.blit(self.IMG, (self.x2, self.y))

#draw the everything in the window
def draw_window(win, bird, pipes, base, score):
	win.blit(BG_IMG, (0,0))  #top left location of where to draw
	
	for pipe in pipes:
		pipe.draw(win)


	text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
	win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10)) #ensure score is always on screen


	base.draw(win)

	bird.draw(win)
	pygame.display.update()


#run the main game loop
def main(): 
	bird = Bird(230,350)
	base = Base(730)
	pipes = [Pipe(700)]
	win = pygame.display.set_mode((WIN_WIDTH, WIN_WEIGHT))
	clock = pygame.time.Clock()
	score = 0


	run = True
	while run:
		clock.tick(30)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
		
		#bird.move()
		add_pipe =False
		rem = []
		for pipe in pipes:   #pipe move
			if pipe.collide(bird, win):  #collision check
				pass #ignore for now  but should end game

			if pipe.x + pipe.PIPE_TOP.get_width() < 0: #check if pipe is off the screen
				rem.append(pipe)
#how do we know if we passed a pipe?
#check if bird is passed the pipe so we can generate more pipes MORE PIPES(power)!!!
			if not pipe.passed and pipe.x < bird.x:
				pipe.passed = True
				add_pipe = True


			pipe.move()
#we should give credit for the pipe being passed, so if we add then we increment
		if add_pipe:
			score += 1
			pipes.append(Pipe(700))

		# remove pipes from the array
		for r in rem:
			pipes.remove(r)

		if bird.y + bird.img.get_height() >= 730: #see if the birdies hit the floor
			pass	
	
		base.move()
		draw_window(win, bird, pipes, base, score)		

	pygame.quit()
	quit()


main()

	def run(config_path)






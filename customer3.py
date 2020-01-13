import random
import numpy as np


class Customer():
    def __init__(self, transition_matrix,states):
        """
        Initialize the Customer instance
        Parameters:
        - transition_matrix: 2-D array representing the probabilities of change of state
        - states: 1-D array representing the states of the Customer. It needs to be in the same order as transition_matrix.
        """
        self.transition_matrix = np.atleast_2d(transition_matrix)
        self.states = states
        #Every state is assigned an index
        self.index_dict = {self.states[index]: index for index in range(len(self.states))}
        #Every index is assigned a state
        self.state_dict = {index: self.states[index] for index in range(len(self.states))}
        self.state = "entrance"
        self.current_state = "entrance"
        self.history = []
        self.gen = self.markov()
        self.x = 800
        self.y = 600
        self.new_x = 0
        self.new_y = 0
        self.path_x = []
        self.path_y = []
        self.time_shift = random.randint(0,1000)
        self.x_move = np.zeros(1)
        self.y_move = np.zeros(1)

    def get_next_state(self):
        #self.history.append(self.state)
        if self.current_state == "checkout":
            return
        else:
            return next(self.gen)

    def markov(self):
        """
        Generate the random states
        """
        while True:
            self.history.append(self.state)
            yield self.state
            self.state = np.random.choice(self.states,p=self.transition_matrix[self.index_dict[self.state], :])

    def generate_super_path(self):
        while self.state != "checkout":
            self.get_next_state()

    def move_x_axis(self):
        steps_x = abs(self.x-self.new_x)
        if self.x >= self.new_x:
            for i in range(steps_x):
                self.x_move=np.append(self.x_move,self.x-i)
                self.y_move=np.append(self.y_move,self.y)
        else:
            for i in range(steps_x):
                self.x_move=np.append(self.x_move,self.x+i)
                self.y_move=np.append(self.y_move,self.y)
        self.x = self.new_x

    def move_x_left(self):
        steps_x = abs(self.x-self.new_x)
        print(f'nr_steps: {steps_x}')
        print(f'x: {self.x}')
        print(f'new x: {self.new_x}')
        for i in range(steps_x):
            self.x_move=np.append(self.x_move,self.x-i)
            self.y_move=np.append(self.y_move,self.y)
        self.x = self.new_x


    def move_x_right(self):
        steps_x = abs(self.x-self.new_x)
        for i in range(steps_x):
            self.x_move=np.append(self.x_move,self.x+i)
            self.y_move=np.append(self.y_move,self.y)
        #self.x = self.new_x
        self.x = self.x + steps_x


    def move_y_axis(self):
        steps_y = abs(self.y-self.new_y)
        if self.y >= self.new_y:
            for i in range(steps_y):
                self.x_move=np.append(self.x_move,self.x)
                self.y_move=np.append(self.y_move,self.y-i)
        else:
            for i in range(steps_y):
                self.x_move=np.append(self.x_move,self.x)
                self.y_move=np.append(self.y_move,self.y+i)
        self.y = self.new_y

    def move_y_up(self,nsteps):
        for i in range(nsteps):
            self.x_move=np.append(self.x_move,self.x)
            self.y_move=np.append(self.y_move,self.y-i)
        self.y = self.y-nsteps

    def move_y_down(self):
        steps_y = abs(self.y-self.new_y)
        for i in range(steps_y):
            self.x_move=np.append(self.x_move,self.x)
            self.y_move=np.append(self.y_move,self.y+i)
        self.y = self.new_y


    def stay(self,nsteps):
        for i in range(nsteps):
            self.x_move=np.append(self.x_move,self.x)
            self.y_move=np.append(self.y_move,self.y)


    def move(self):
        # Generate path for x and y
        # Create path in the supermarket
        self.generate_super_path()

        li = self.history
        #li = ['entrance','fruits','checkout']
        #print(li)
        for s in li[1:-1]:
            self.coord_next_section(s)
            #move from previous to new
            if self.current_state == s: #next state is the same
                self.stay(200)
            else:
                # add transition if not starting at entrance
                if self.current_state != "entrance":
                    q = self.y - 60
                    #self.move_y_up(300)
                    self.move_y_up(q)
                    self.move_x_axis()
                    self.move_y_axis()
                    self.current_state = s
                    self.stay(200)
                else: #at the entrance
                    if s != 'fruits':
                        # add small move forward
                        self.move_y_up(150)
                        self.move_x_axis()
                        self.move_y_axis()
                        self.current_state = s
                        #Add time at the section
                        self.stay(200)
                    else: #going to fruit from entrance
                        self.move_y_axis()
                        self.x = self.new_x
                        self.current_state = s
                        self.stay(200)

        # must be outside the for loop of supermarket path
        # Go to checkout
        # Go randomly to one of the checkouts (checkout_x is the x coord)
        checkout_x = [80,210,350,490]
        self.new_x = random.choice(checkout_x)
        self.new_y = 450
        # From section to checkout y axis
        self.move_y_down()
        #print({self.new_x})
        #self.move_x_left()
        self.move_x_axis()
        # at checkout
        self.new_y = 500
        self.move_y_down()
        #Add time at the section
        self.stay(200)
        # Go out
        self.new_x = 800
        self.new_y = 625
        self.move_y_down()
        self.move_x_right()
        self.move_y_down()
        # Final path
        self.path_x = self.x_move[self.x_move!=0]
        self.path_y = self.y_move[self.y_move!=0]



    def coord_next_section(self,section):
        if section == "fruits" :
            self.new_x = 800
            self.new_y = 360 - random.randint(0,200)
        elif section == "spices":
            self.new_x = 550
            self.new_y = 360 - random.randint(0,200)
        elif section == "dairy":
            self.new_x = 300
            self.new_y = 360 - random.randint(0,200)
        elif section == "drinks":
            self.new_x = 80
            self.new_y = 360 - random.randint(0,200)
        else:
            self.new_x = 80
            self.new_y = 660

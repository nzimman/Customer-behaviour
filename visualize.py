import numpy as np
import cv2
from customer3 import Customer
import pandas as pd
import time

img = cv2.imread('market.png')
cust1 = cv2.imread('c1.png')
cust2 = cv2.imread('c2.png')
cust3 = cv2.imread('c3.png')
cust4 = cv2.imread('c4.png')
cust5 = cv2.imread('c5.png')

# Rad transition probabilites in csv file
df = pd.read_csv('prob.csv',sep=',',index_col='From/To')
tmat = df.values.tolist()

# Same order as in transition matrix
sections = ['checkout','dairy','drinks','entrance','fruits','spices']

c1 = Customer(transition_matrix=tmat,states=sections)
c2 = Customer(transition_matrix=tmat,states=sections)
c3 = Customer(transition_matrix=tmat,states=sections)
c4 = Customer(transition_matrix=tmat,states=sections)
c5 = Customer(transition_matrix=tmat,states=sections)

i = 0
c1.move()
c2.move()
c3.move()
c4.move()
c5.move()

while True:
    frame = img.copy()

    if (len(c1.path_y)>i):
        frame[int(c1.path_y[i]):int(c1.path_y[i])+50,int(c1.path_x[i]):int(c1.path_x[i])+50] = cust1

    if (len(c2.path_y)>i+c2.time_shift):
       frame[int(c2.path_y[i+c2.time_shift]):int(c2.path_y[i+c2.time_shift])+50,int(c2.path_x[i+c2.time_shift]):int(c2.path_x[i+c2.time_shift])+50] = cust2

    if (len(c3.path_y)>i+c3.time_shift):
        frame[int(c3.path_y[i+c3.time_shift]):int(c3.path_y[i+c3.time_shift])+50,int(c3.path_x[i+c3.time_shift]):int(c3.path_x[i+c3.time_shift])+50] = cust3

    if (len(c4.path_y)>i+c4.time_shift):
        frame[int(c4.path_y[i+c4.time_shift]):int(c4.path_y[i+c4.time_shift])+50,int(c4.path_x[i+c4.time_shift]):int(c4.path_x[i+c4.time_shift])+50] = cust4

    if (len(c5.path_y)>i+c5.time_shift):
        frame[int(c5.path_y[i+c5.time_shift]):int(c5.path_y[i+c5.time_shift])+50,int(c5.path_x[i+c5.time_shift]):int(c5.path_x[i+c5.time_shift])+50] = cust5

    i +=1

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

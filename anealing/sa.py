import random
import math
import logging
import os
from urllib import urlretrieve

def P(prev_score,next_score,temperature):
    if next_score > prev_score:
        return 1.0
    else:
        return math.exp( -abs(next_score-prev_score)/temperature )

class ObjectiveFunction:
    '''class to wrap an objective function and 
    keep track of the best solution evaluated'''
    def __init__(self,objective_function,coords):
        self.objective_function=objective_function
        self.best=None
        self.best_score=None
        self.coords = coords
    
    def __call__(self,solution):
        score=self.objective_function(solution)
        if self.best is None or score > self.best_score:
            self.best_score=score
            self.best=solution
            logging.info('new best score: %f',self.best_score)
            if score > (-341):
              getimg(self.coords,self.best)
              os.popen("open path.png")

        return score

def kirkpatrick_cooling(start_temp,alpha):
    T=start_temp
    while True:
        yield T
        T=alpha*T

def anneal(init_function,move_operator,objective_function,max_evaluations,start_temp,alpha,coords):
    
    # wrap the objective function (so we record the best)
    objective_function=ObjectiveFunction(objective_function,coords)
    
    current=init_function()
    current_score=objective_function(current)
    num_evaluations=1

    last_evals=2
    
    cooling_schedule=kirkpatrick_cooling(start_temp,alpha)
    
    logging.info('anneal started: score=%f',current_score)
    
    for temperature in cooling_schedule:
        done = False
        # examine moves around our current position
        for next in move_operator(current):
            if num_evaluations >= max_evaluations:
                done=True
                break
            elif num_evaluations >= last_evals:
              logging.info('current run at %s runs', num_evaluations )
              last_evals = last_evals *2
            
            next_score=objective_function(next)
            num_evaluations+=1
            
            # probablistically accept this solution
            # always accepting better solutions
            p=P(current_score,next_score,temperature)
            if random.random() < p:
                current=next
                current_score=next_score
                break
        # see if completely finished
        if done: break
    
    best_score=objective_function.best_score
    best=objective_function.best
    logging.info('final temperature: %f',temperature)
    logging.info('anneal finished: num_evaluations=%d, best_score=%f',num_evaluations,best_score)
    return (num_evaluations,best_score,best)

def getimg(coords, best):
    url = "http://maps.google.com/maps/api/staticmap?path=color:0x000000ff|weight:4"

    for i in best:
        url = url + "|" + str(coords[i][0]) + "," + str(coords[i][1])

    url = url + "&size=1024x1024&sensor=false&key=ABQIAAAAzr2EBOXUKnm_jVnk0OJI7xSsTL4WIgxhMZ0ZK_kHjwHeQuOD4xQJpBVbSrqNn69S6DOTv203MQ5ufA"
    urlretrieve(url,"path.png")

    url = "http://maps.google.com/maps/api/staticmap?markers=color:blue|"
    for i in best:
            url = url + "|" + str(coords[i][0]) + "," + str(coords[i][1])

    url = url + "&size=1024x1024&sensor=false&key=ABQIAAAAzr2EBOXUKnm_jVnk0OJI7xSsTL4WIgxhMZ0ZK_kHjwHeQuOD4xQJpBVbSrqNn69S6DOTv203MQ5ufA"
    #urlretrieve(url,"points.png")



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Dec 12 00:50:04 2017

@author: jonatanpinol
"""

# recommender library : 

import pandas as pd
import numpy as np

def userSim(u1,u2,a):
    #a = a.drop_duplicates()
    s1 = a.T[u1]
    s2 = a.T[u2]
    dif = 0
    cont = 0
    for i in s1.index:
        if s1[i] != 0.0 and s2[i] != 0.0:
            cont += 1
            dif += 4 - np.abs(s1[i] - s2[i])
    return dif/cont/2 - 1


def predUsrRec(u,r,a): 
    #print("------------------------------------------")
    #print("Current recipe rate :",a.loc[u,r]," user :",u,"recipe :",r)
    #print("------------------------------------------")
    if (a.loc[u,r] != 0.0):
        return a.loc[u,r]
    else:
        tot = 0
        simCoef = 0
        sr = a[r]
        for i in sr.index:
            if sr[i] != 0.0:
                c = userSim(u,i,a)
                tot += (sr[i]-3) * c
                simCoef += c
        if simCoef > 0.0:
            return tot/simCoef + 3
        return 3
    
def distance_recipes(recipe1,recipe2,db_recipes_ingredients):
    return (np.dot(db_recipes_ingredients.loc[recipe1].values\
                ,db_recipes_ingredients.loc[recipe2].values)/np.sum(db_recipes_ingredients.loc[recipe1].values))
    
    
def predusrecalter2(u,r,a,db_recipes_ingredients,mode=0):
    if(mode==0):
        if a[r][u]!= 0.0: #recepta r, user u
            return a[r][u]
        else:    
            nota=0
            compt=0
            for j in a.columns:
                if a.loc[u,j]!=0.0 and (j in db_recipes_ingredients.index):
                    nota+=a.loc[u,j]*distance_recipes(j,r,db_recipes_ingredients)
                    compt+=1
            nota=((nota/compt)*4 + predUsrRec(u,r,a))/2
    elif(mode==1):
            if a[r][u]!= 0.0: #recepta r, user u
                return a[r][u]
            else:    
                nota=0
                compt=0
                for j in a.columns:
                    if a.loc[u,j]!=0.0 and (j in db_recipes_ingredients.index):
                        nota+=a.loc[u,j]*distance_recipes(j,r,db_recipes_ingredients)
                        compt+=1
                nota=(nota/compt)*4 
    else:
        nota = predUsrRec(u,r,a)
    return nota

def getRecipesRecommender(filtered_recipes,current_user,a,db_recipes_ingredients,mode=0):
    #start = timeit.default_timer()
    #i = 0
    aux_recipes = pd.DataFrame(index = filtered_recipes.index)
    aux_recipes["rating"] = np.zeros(filtered_recipes.shape[0])
    for recip in filtered_recipes.index:
        if(recip in a.columns):
            #print("Hi!")
            rate = predusrecalter2(current_user, recip, a, db_recipes_ingredients,mode)
            aux_recipes.loc[recip,"rating"] = rate 
    aux_recipes = aux_recipes.sort_values("rating",ascending = False )
    stop = timeit.default_timer()    
    timevect=stop-start
    #print(timevect)
    return(aux_recipes)



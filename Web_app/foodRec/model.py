import pymongo
import pandas as pd
import requests
from bs4 import BeautifulSoup

class User():

    def __init__(self, username):
        self.username = username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    @staticmethod
    def validate_login(password_form, password):
        return password_form == password

class Users(object):
    def __init__(self, filename=None):
        try:
            conn=pymongo.MongoClient("mongodb://god:god@ds113938.mlab.com:13938/app")
            print ("Connected successfully!!!")
        except pymongo.errors.ConnectionFailure:
            print ("Could not connect to MongoDB: %s" % e )
        db = conn['app']
        self.collection = db.users
        if filename==None:
            self.users = pd.DataFrame(columns=['username','password','name','image','allergies'])
            for d in self.collection.find():
                self.users = self.users.append(pd.DataFrame.from_dict(d, orient='index').T,ignore_index=True)
        else:
            self.users = pd.read_json(filename).transpose()
            self.users = self.users.reset_index()
            print(self.users)
            self.users.columns = ['username','allergies','image','name','password']
            self.collection.insert_many(pd.DataFrame.to_dict(self.users,orient='records'))
        #self.users = self.users.set_index('username')
    
    def getUsers(self):
        return self.users
    
    def getUser(self, username):
        try:
            conn=pymongo.MongoClient("mongodb://god:god@ds113938.mlab.com:13938/app")
            print ("Connected successfully!!!")
        except pymongo.errors.ConnectionFailure:
            print ("Could not connect to MongoDB: %s" % e )
        db = conn['app']
        return db.users.find_one({'username':username})

    def setUser(self, username, name, allergies, image):
        try:
            conn=pymongo.MongoClient("mongodb://god:god@ds113938.mlab.com:13938/app")
            print ("Connected successfully!!!")
        except pymongo.errors.ConnectionFailure:
            print ("Could not connect to MongoDB: %s" % e )
        db = conn['app']
        print(allergies)
        db.users.update_one({'username':username},{'$set':{'allergies': allergies, 'image': image, 'name': name, 'username':username}})
        obj = db.users.find_one({'username':username})
        print(obj)
        return True
    
    def addUser(self, username, password, name = '', image = '', allergies = ''):
        if(username in self.users.username.unique()): return False
        aux = {'allergies': allergies, 'image': image, 'name': name, 'password': password, 'username':username}
        self.collection.insert_one(aux)
        self.users = self.users.append(pd.DataFrame.from_dict(aux, orient='index').T,ignore_index=True)
        return True
    
    def deleteUser(self, username):
        if(username not in self.users.username.unique()): return False
        self.collection.delete_one({"username":username})
        self.users = self.users[self.users['username'] != username]
        return True

    def addRating(self, username, recipe, rating):
        if(self.getUser(username) == ""): 
            return False
        self.collection.update_one({'username':username},{"$set":{recipe:rating}})
        if not self.users.empty:
            self.users[username,recipe]=rating
        print('Rating added')
        return True


class Recipes(object):
    def __init__(self, filename=None):
        try:
            conn=pymongo.MongoClient("mongodb://god:god@ds113938.mlab.com:13938/app")
            print ("Connected successfully!!!")
        except pymongo.errors.ConnectionFailure:
            print ("Could not connect to MongoDB: %s" % e )
        db = conn['app']
        self.collection = db.recipes2
        if filename==None:
            self.recipes = pd.DataFrame(columns=['name','c','i','l','p','s','url','v'])
        else:
            self.recipes = pd.read_json(path_or_buf=filename).T
            self.recipes = self.recipes.reset_index()
            self.recipes.columns = ['name','c','i','l','p','s','url','v']
            self.recipes['name'] = self.recipes['name'].str.replace('.','')
            self.collection.insert_many(pd.DataFrame.to_dict(self.recipes,orient='records'))
            self.recipe = self.recipe.set_index('name')

    def getRecipes(self):
        if not self.recipes.empty:
            return self.recipes
        for d in self.collection.find():
            self.recipes = self.recipes.append(pd.DataFrame.from_dict(d, orient='index').T,ignore_index=True)
        self.recipes = self.recipes.set_index('name')
        return self.recipes
    
    def getRecipe(self, name):
        self.recipe = pd.DataFrame(columns=['name','c','i','l','p','s','url','v'])
        for d in self.collection.find({"name":name}):
            self.recipe = self.recipe.append(pd.DataFrame.from_dict(d, orient='index').T,ignore_index=True)
        self.recipe = self.recipe.set_index('name')
        return self.recipe
    
    def getFilteredRecipes(self, name=None, maxtime=1e6, maxing=1e6,avgpoints=0):
        self.filtered = pd.DataFrame(columns=['name','c','i','l','p','s','url','v'])
        for d in self.collection.find({"name":{"$regex" : name},"$where": '(this.c + this.p) <='+str(maxtime),"$where":'this.l.length<='+str(maxing)}):
            self.filtered = self.filtered.append(pd.DataFrame.from_dict(d, orient='index').T,ignore_index=True)
        self.filtered = self.filtered.set_index('name')
        return self.filtered

    def BBCurl(self, url):
        base = "https://www.bbc.co.uk/food/recipes/"
        url = url.split("recipes_")[1]
        url = url.split(".")[0]
        return base+url

    def readSourceBBC(self, url, im = False, method = False):
        r = requests.get(self.BBCurl(url))
        soup = BeautifulSoup(r.content, "lxml")
        if (im):
            img = soup.find('img', itemprop='image')
            img = img.attrs['src']
        else:
            img = None

        try:
            description = soup.find('p', {"class" : "recipe-description__text"}).text
        except:
            description = ""

        if(method):
            methodAux = soup.find_all('p', {"class" : "recipe-method__list-item-text"})
            method = []
            for m in methodAux:
                method.append(m.text)
            return img, method, description
         
        return img, description

    def getFullRecipe(self,name):
        recipe = self.getRecipe(name)
        #link = recipe['link']
        #im = False
        #if recipe['i'] == 1:
        #    im = True
        im = recipe.i.values[0]
        link = recipe.url.values[0]
        img, method, description = self.readSourceBBC(link, im, True)
        return img, method, description

    def getRecipesRecommender(recipes_filter,current_user):

        self.recommend #aquí va la funció del recommender

        return self.recommend


class Ratings(object):
    def __init__(self, filename=None):
        try:
            conn=pymongo.MongoClient("mongodb://god:god@ds113938.mlab.com:13938/app")
            print ("Connected successfully!!!")
        except pymongo.errors.ConnectionFailure:
            print ("Could not connect to MongoDB: %s" % e )
        db = conn['app']
        self.collection = db.ratings
        if filename!=None:
            r = pd.read_csv(filename,index_col = 0)
            r = pd.DataFrame.to_dict(r.T)
            for k, v in list(r.items()):
                for k2, v2 in list(v.items()):
                    if v2 == 0: del v[k2]
            for k, v in list(r.items()):
                v['username'] = k
                self.collection.insert_one(v)
        self.ratings = pd.DataFrame()
        for d in self.collection.find():
            u = d['username']
            del d['username']
            del d['_id']
            self.ratings = self.ratings.append(pd.DataFrame.from_dict(dict([(u,d)])).T)
            self.ratings = self.ratings.fillna(0)
    def getRatings(self):
        return self.ratings
    
    def addRating(self, username, recipe, rating):
        self.collection.update_one({'username':username},{"$set":{recipe:rating}})
        self.ratings.at[username,recipe] = rating
        return True



    
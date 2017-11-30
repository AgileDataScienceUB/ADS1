import pymongo
import pandas as pd

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

class Recipes(object):
    def __init__(self, filename=None):
        try:
            conn=pymongo.MongoClient("mongodb://god:god@ds113938.mlab.com:13938/app")
            print ("Connected successfully!!!")
        except pymongo.errors.ConnectionFailure:
            print ("Could not connect to MongoDB: %s" % e )
        db = conn['app']
        self.collection = db.recipes
        if filename==None:
            self.recipes = pd.DataFrame(columns=['name','c','i','l','p','s','v'])
        else:
            self.recipes = pd.read_json(path_or_buf=filename).T
            self.recipes = self.recipes.reset_index()
            self.recipes.columns = ['name','c','i','l','p','s','v']
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
        if self.recipes.empty:
            self.recipe = pd.DataFrame(columns=['name','c','i','l','p','s','v'])
            for d in self.collection.find({"name":name}):
                self.recipe = self.recipe.append(pd.DataFrame.from_dict(d, orient='index').T,ignore_index=True)
            self.recipe = self.recipe.set_index('name')
            if self.recipe.empty: print('Recipe not found')
            return self.recipe
        if not self.recipes.index.str.contains(name).any(): 
            print('Recipe not found')
            return False
        return self.recipes.loc[name]
    
    # TODO: Filter by excluded ingredients
    # TODO: Filter by average rating
    def getFilteredRecipes(self, name=None, maxtime=1e6, maxing=1e6, avgpoints=0):
        # I don't know how to pandas
        '''
        if not self.recipes.empty:
            self.aux = self.recipes
            self.aux['recipename'] = self.aux.index
            self.aux = self.aux[[i<=maxing for i in [len(self.aux['l'][i]) for i in range(len(self.aux['l']))]]][self.aux['recipename'].str.contains(name)][self.aux['c']+self.aux['p']<=maxtime]
            del self.aux['recipename']
            return self.aux
        '''
        self.filtered = pd.DataFrame(columns=['name','c','i','l','p','s','v'])
        for d in self.collection.find({"name":{"$regex" : name},"$where": '(this.c + this.p) <='+str(maxtime),"$where":'this.l.length<='+str(maxing)}):
            self.filtered = self.filtered.append(pd.DataFrame.from_dict(d, orient='index').T,ignore_index=True)
        self.filtered = self.filtered.set_index('name')
        return self.filtered


class Users(object):
    def __init__(self, filename=None):
        try:
            conn=pymongo.MongoClient("mongodb://god:god@ds113938.mlab.com:13938/app")
            print ("Connected successfully!!!")
        except pymongo.errors.ConnectionFailure:
            print ("Could not connect to MongoDB: %s" % e )
        db = conn['app']
        self.collection = db.users2
        self.users = pd.DataFrame(columns=['username','password','name','image','allergies'])
        if filename!=None:
            self.users = pd.read_json(filename).transpose()
            self.users = self.users.reset_index()
            self.users.columns = ['username','allergies','image','name','password']
            self.collection.insert_many(pd.DataFrame.to_dict(self.users,orient='records'))
            self.users = self.users.set_index('username')
            
            # Version with users + ratings
            # Probably doesn't work right now
            ''' 
            r = pd.read_csv('ratingsFull.csv',index_col = 0, encoding="ISO-8859-1")
            r = pd.DataFrame.to_dict(r.T)
            users = Users().getUsers()
            users = users.iloc[:,-5:]
            users = pd.DataFrame.to_dict(users.T)

            for k, v in list(r.items()):
                for k2, v2 in list(v.items()):
                    if v2 == 0: del v[k2]
            for k, v in list(r.items()):
                v['username'] = k
                v['name'] = users[k]['name']
                v['password'] = users[k]['password']
                v['image'] = users[k]['image']
                v['allergies'] = users[k]['allergies']
                for k2, v2 in list(v.items()):
                    if('.' in k2):
                        v[k2.replace('.','')] = v.pop(k2)
                collection.insert_one(v)
            '''
    
    def getUsers(self):
        if not self.users.empty: return self.users
        else:
            for d in self.collection.find():
                self.users = self.users.append(pd.DataFrame.from_dict(d, orient='index').T,ignore_index=True)
                self.users = self.users.set_index('username')
        return self.users
    
    def getUser(self, username):
        if not self.users.empty: return self.users[self.users['username']==username]
        else:
            self.user = pd.DataFrame(columns=['username','allergies','image','name','password'])
            for d in self.collection.find({"username":username}):
                self.user = self.user.append(pd.DataFrame.from_dict(d, orient='index').T,ignore_index=True)
            self.user = self.user.set_index('username')
        if self.user.empty: 
            print('User not found')
            return self.user
        return self.user
    
    def addUser(self, username, password, name = '', image = '', allergies = ''):
        if(not self.getUser(username).empty): 
            print('Username taken')
            return False
        aux = {'allergies': allergies, 'image': image, 'name': name, 'password': password, 'username':username}
        self.collection.insert_one(aux)
        if not self.users.empty:
            self.users = self.users.append(pd.DataFrame.from_dict(aux, orient='index').T,ignore_index=True)
        print('User added')
        return True
    
    def deleteUser(self, username):
        if self.getUser(username).empty: 
            return False
        self.collection.delete_one({"username":username})
        if not self.users.empty:
            self.users = self.users[self.users['username'] != username]
        print('User deleted')
        return True
    
    def addRating(self, username, recipe, rating):
        if(self.getUser(username).empty): 
            return False
        self.collection.update_one({'username':username},{"$set":{recipe:rating}})
        if not self.users.empty:
            self.users[username,recipe]=rating
        print('Rating added')
        return True


    
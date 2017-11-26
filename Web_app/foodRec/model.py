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
        self.users = self.users.set_index('username')
    
    def getUsers(self):
        return self.users
    
    def getUser(self, username):
        return self.users[self.users['username']==username]
    
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
            for d in self.collection.find():
                self.recipes = self.recipes.append(pd.DataFrame.from_dict(d, orient='index').T,ignore_index=True)
        else:
            self.recipes = pd.read_json(path_or_buf=filename).T
            self.recipes = self.recipes.reset_index()
            self.recipes.columns = ['name','c','i','l','p','s','v']
            self.recipes['name'] = self.recipes['name'].str.replace('.','')
            self.collection.insert_many(pd.DataFrame.to_dict(self.recipes,orient='records'))
        self.recipes = self.recipes.set_index('name')

    def getRecipes(self):
        return self.recipes
    
    def getRecipe(self, name):
        return self.recipes[self.recipes['name']==name]

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


    
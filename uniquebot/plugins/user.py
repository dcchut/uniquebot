from uniquebot.core.plugin import CorePlugin
from uniquebot.core.user import User

class Plugin(CorePlugin):
	register_methods = ['getUser', 'getUserPoints', 'getAllUsers', 'createUser', 'updateUser']
	
	def getUser(self, user):
		self.factory.c.execute("SELECT h, p, u FROM points WHERE h = ?", (user,))
		row = self.factory.c.fetchone()
		
		if row != None:
			return User(row[0], row[1], row[2])
		else:
			return None
			
	def getAllUsers(self):
		self.factory.c.execute("SELECT h, p, u FROM points ORDER BY p DESC")
		r = []
		
		for row in self.factory.c:
			r.append(User(row[0], row[1], row[2]))
		
		return r
		
	def getUserPoints(self, user):
		u = self.getUser(user)
		
		if u != None:
			return u.points
		else:
			return None
		
	def createUser(self, user, current_time):
		self.factory.c.execute("INSERT INTO POINTS (h,p,u) VALUES (?,?,?)", (user, 0, current_time))
		self.factory.db.commit()
		
		return self.getUser(user)
		
	def updateUser(self, user, points, time):
		self.factory.c.execute("UPDATE points SET p = ?, u = ? WHERE h = ?", (points, time, user.user))
		self.factory.db.commit()
		
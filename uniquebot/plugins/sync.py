from uniquebot.core.plugin import CorePlugin

class Plugin(CorePlugin):
	register_methods = ['syncAllUsers', 'syncUser']
	rate = 15
	
	# sync all user
	def syncAllUsers(self, current_time):
		users = self.bot.getAllUsers()
		
		for user in users:
			self.syncUser(user, 0, current_time)
		
	# sync a user
	def syncUser(self, user, point_delta, current_time):
		if isinstance(user, str):
			# is this person already a user?
			u = self.bot.getUser(user)
			
			# if not, create a user record for them
			if u == None:
				u = self.bot.createUser(user, current_time)
			
			user = u
		
		# sync them
		points = user.points + point_delta
		time_delta = current_time - user.time
		
		# have we gotten any points since the last update?
		time_points_delta = time_delta / self.rate
		
		if time_points_delta > 0:
			new_points = max(min(points + time_points_delta, 0), points)
			
			if new_points == 0:
				update_time = current_time
			else:
				update_time = user.time + self.rate * time_points_delta
			
			points = new_points
		else:
			update_time = user.time
			
		self.bot.updateUser(user, points, update_time)
		
		return points
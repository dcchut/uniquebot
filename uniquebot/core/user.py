class User(object):
	def __init__(self, user, points, time):
		# i hate encoding
		self.user = str(user).encode('ascii', 'ignore')
		self.points = points
		self.time = time
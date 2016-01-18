import requests
import unittest


class TestServerFunctionality(unittest.TestCase):

	def setUp(self):  #setUp function is called before each test, a built-in method of unittest
		self.url= 'http://ec2-52-11-248-121.us-west-2.compute.amazonaws.com/api/v1'
		self.loginval= {"login":"test", "password":"test"}

	def test_1_login(self):
		requestLogin = requests.post(self.url+'/login', json = self.loginval)
		token = (requestLogin.json().get('data')).get('tokenKey')
		self.assertEqual(requestLogin.json().get('status'), 1)
		emailVerif = (requestLogin.json().get('data')).get('emailVerified')
		self.assertEqual(emailVerif,1)
		userid = (requestLogin.json().get('data')).get('user_id')
		self.assertEqual(userid,1)

	def test_2_get_items(self):
		requestLogin = requests.post(self.url+'/login', json = self.loginval)
		token = (requestLogin.json().get('data')).get('tokenKey')
		headers = {'Token-Key':'%s'%token }
		requestItems = requests.get(self.url+'/items', headers = headers)
		self.assertEqual(requestItems.json().get('status'), 1)
		todoData = (requestItems.json().get('data')).get('todoData')
		for x in range(0,len(todoData)):
			self.assertEqual(todoData[x].get('description'),'test%s'%(x+1))
			self.assertEqual(todoData[x].get('title'),'test%s'%(x+1))
			self.assertEqual(todoData[x].get('id'),(x+1))

	def test_3_add_item(self):
		requestLogin = requests.post(self.url+'/login', json = self.loginval)
		token = (requestLogin.json().get('data')).get('tokenKey')
		headers = {'Token-Key':'%s'%token }
		requestItem = requests.post(self.url+'/item', json = {"title":"test4", "description":"test4"}, headers = headers)
		self.assertEqual(requestItem.json().get('status'), 1)

	def test_4_edit_item(self):
		requestLogin = requests.post(self.url+'/login', json = self.loginval)
		token = (requestLogin.json().get('data')).get('tokenKey')
		headers = {'Token-Key':'%s'%token }
		requestItemEdit = requests.put(self.url+'/item/4', json = {"title":"test4", "description":"test4"}, headers = headers)
		self.assertEqual(requestItemEdit.json().get('status'), 1)

	def test_5_delete_item(self):
		requestLogin = requests.post(self.url+'/login', json = self.loginval)
		token = (requestLogin.json().get('data')).get('tokenKey')
		headers = {'Token-Key':'%s'%token }
		requestItemDelete = requests.delete(self.url+'/item/4', headers = headers)
		self.assertEqual(requestItemDelete.json().get('status'), 1)

	def test_6_logout(self):
		requestLogin = requests.post(self.url+'/login', json = self.loginval)
		token = (requestLogin.json().get('data')).get('tokenKey')
		headers = {'Token-Key':'%s'%token }
		requestLogout = requests.post(self.url+'/logout', headers = headers)
		self.assertEqual(requestLogout.json().get('status'), 1)

if __name__ == '__main__':
	unittest.main(verbosity=2)
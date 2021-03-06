import time
from socket import *
import threading
from queue import Queue
import messageProcessing
import msgCrypto
from Crypto.PublicKey import RSA

class messaging:
	def __init__(self):
		self.broadcastQ = Queue()
		self.messageQ = Queue()
		self.lock = threading.Lock()
		self.table = {}
<<<<<<< HEAD

		# generate Public and Private Key pair
		msgCrypto.generateKeys()
		self.strPubKey, self.PrivKey = msgCrypto.readKeys()
		self.PubKey = RSA.importKey(self.strPubKey.encode())

		self.broadCastingPort = 62112
		self.ipReceivingPort = 62111
		self.messageReceivingPort = 62110
=======
		self.myPubKey = myPubKey
		self.broadCastingPort = 62542
		self.ipReceivingPort = 62541
		self.messageReceivingPort = 62540
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> parent of ae3c471... Fixed lost prefix in msg-content
=======
>>>>>>> parent of ae3c471... Fixed lost prefix in msg-content
=======
>>>>>>> parent of ae3c471... Fixed lost prefix in msg-content
		self.myIP = self.getMyIP()
		self.broadCasting = socket(AF_INET, SOCK_DGRAM)
		self.broacastReceivingSocket = socket(AF_INET,SOCK_DGRAM)
		self.broacastReceivingSocket.bind(('',self.broadCastingPort))
		self.ipSendingSocket = socket(AF_INET,SOCK_DGRAM)
		self.ipReceivingSocket = socket(AF_INET,SOCK_DGRAM)
		self.ipReceivingSocket.bind(('',self.ipReceivingPort))
		self.messageSendingSocket = socket(AF_INET, SOCK_STREAM)
		self.messageReceivingSocket = socket(AF_INET, SOCK_STREAM)
		self.messageReceivingSocket.bind(("",self.messageReceivingPort))
		self.messageReceivingSocket.listen(1)


		answerThread = threading.Thread(target=self.Answer)
		answerThread.start()
		broadcasterThread = threading.Thread(target=self.broadcaster)
		broadcasterThread.start()
		messageReceiverThread = threading.Thread(target=self.messageReceiver)
		messageReceiverThread.start()

		self.table[self.strPubKey] = (self.myIP, float('Inf'))

	def iplookups(self, targetPubKey):
		for x in range(3):
			ip = self.iplookup(targetPubKey)
			if ip:
				return ip
			time.sleep(6)
			
	def iplookup(self, targetPubKey):
		try:
			targetTuple = self.table[targetPubKey]
			if time.time() - targetTuple[1] < 600:
				return targetTuple[0]
			else:
				del(self.table[targetPubKey])
				return self.iplookup(targetPubKey)

		except KeyError:
			self.ask(targetPubKey)

	def broadcaster(self):
		while True:
			task = self.broadcastQ.get()
			self.broadcast(task)
			self.broadcastQ.task_done()

	def broadcast(self, targetPubKey):
		for x in range(255):
			for y in range(255):
				try:
					self.broadCasting.sendto(targetPubKey.encode(),('10.27.'+str(x)+'.'+str(y), self.broadCastingPort))
					time.sleep(0.00005)
				except:
					time.sleep(0.0001)


	def recvAnswer(self, targetPubKey):  # received other's reply(IP addr) to my broadcasting
		while True:
			try:
				self.ipReceivingSocket.settimeout(None)
				message, Address = self.ipReceivingSocket.recvfrom(2048)
				decodedMessage = message.decode()
				if decodedMessage == targetPubKey:
					self.ipReceivingSocket.settimeout(None)
					self.table[targetPubKey] = (Address[0],time.time())
					break
			except socket.timeout:
				break

	def ask(self, targetPubKey):
		self.broadcastQ.put(targetPubKey)
		t = threading.Thread(target=self.recvAnswer,args = (targetPubKey,))
		t.start()

	def Answer(self):
		while True:
			message, Address = self.broacastReceivingSocket.recvfrom(2048)
			decodedMessage = message.decode()
			if decodedMessage != self.strPubKey:
				continue
			self.ipSendingSocket.sendto(self.strPubKey.encode(),(Address[0], self.ipReceivingPort))

	def sendMessage(self,recipientPubKey,message):
		print("Finding IP of " + recipientPubKey)
		ip = self.iplookups(recipientPubKey)
		if ip:
			print("IP found!")
			packedMsg = messageProcessing.messagePacking(# self.strPubKey,
															recipientPubKey,
															message)
			try:
				print("Sending Message!")
				self.messageSendingSocket = socket(AF_INET, SOCK_STREAM)
				self.messageSendingSocket.connect((ip, self.messageReceivingPort))
				self.messageSendingSocket.send(packedMsg)
				#this one need to add to encrypt later
				self.messageSendingSocket.close()
				self.updateTTL(recipientPubKey)
				print("Message Sent!")
				return True
			except:
				print("Sending Failed!")
				return False
		else:
			print("IP not found!")
			return False

	def messageReceiver(self):
		while True:
			connectionSocket,Address = self.messageReceivingSocket.accept()
			print(Address)
			rawMsg = connectionSocket.recv(1024)
			connectionSocket.close()
			#this one need to add to encrypt later
			self.messageQ.put(rawMsg)

	def getMsgFromQ(self):
		if not self.messageQ.empty():
			msg = self.messageQ.get()
			self.messageQ.task_done()
			return msg

	def updateTTL(self,strPubKey):
		prevRec = self.table[strPubKey]
		newRec = (prevRec[0],time.time())
		self.table[strPubKey] = newRec

	def getMyIP(self):
		s = socket(AF_INET, SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		return s.getsockname()[0]
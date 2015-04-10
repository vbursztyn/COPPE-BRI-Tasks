import math


class Evaluator():


	resultsFile = ""
	expectedFile = ""
	resultsData = dict()
	expectedData = dict()

	precision = dict()
	recall = dict()
	F1 = dict()
	precisionAt10 = 0
	MAP = 0
	meanDCG = 0

	DEBUG_MODE = False


	def __init__(self, DEBUG_MODE=False, resultsFile="default_results_output.csv", expectedFile="default_PC_output_2.csv"):
		self.DEBUG_MODE = DEBUG_MODE
		self.resultsFile = resultsFile
		self.expectedFile = expectedFile
		self.setup()


	def setup(self, querySeparator="; ", resultSeparator="), (", innerSeparator=", "):
		with open(self.resultsFile, "r") as fResults:
			for line in fResults:
				tokens = line.split(querySeparator)
				if len(tokens) != 2:
					print "WARNING: malformed line, skipping... Line: " + str(tokens)
					continue

				queryId = tokens[0]
				queryResults = tokens[1].replace("[", "").replace("]", "").split(resultSeparator)
				if not len(queryResults):
					print "WARNING: malformed line, skipping... Line: " + str(tokens)
					continue

				self.resultsData[queryId] = list()
				for resultStr in queryResults:
					innerTokens = resultStr.replace("(", "").replace(")", "").split(innerSeparator)
					queryResult = dict()
					queryResult["id"] = int(innerTokens[1])
					queryResult["score"] = float(innerTokens[2])
					self.resultsData[queryId].append( queryResult )

		with open(self.expectedFile, "r") as fExpected:
			for line in fExpected:
				tokens = line.split(querySeparator)
				if len(tokens) != 2:
					print "WARNING: malformed line, skipping... Line: " + str(tokens)
					continue

				queryId = tokens[0]
				queryResults = tokens[1].replace("[", "").replace("]", "").split(resultSeparator)
				if not len(queryResults):
					print "WARNING: malformed line, skipping... Line: " + str(tokens)
					continue

				self.expectedData[queryId] = list()
				for resultStr in queryResults:
					innerTokens = resultStr.replace("(", "").replace(")", "").split(innerSeparator)
					queryResult = dict()
					queryResult["id"] = int(innerTokens[0])
					queryResult["score"] = float(innerTokens[1])
					self.expectedData[queryId].append( queryResult )

		# if self.DEBUG_MODE:
		# 	print self.resultsData
		# 	print self.expectedData


	def evaluate(self):
		self.processPrecision()
		self.processRecall()
		self.calculateF1()
		self.calculatePrecisionAt10()
		self.calculateMAP()
		self.calculateDCG()
		self.calculateNDCG()
	

	def processPrecision(self):
		for size in range(1,12):
			self.precision[size] = dict()
			for queryId in self.resultsData:
				
				expectedIds = list()
				for expectedResult in self.expectedData[queryId][:size]:
					expectedIds.append(expectedResult["id"])

				topN = self.resultsData[queryId][:size]
				matches = 0
				for queryResult in topN:
					if queryResult["id"] in expectedIds:
						matches = matches + 1
				self.precision[size][queryId] = matches / float(size)

			self.precision[size]["average"] = 0
			for queryId in self.precision[size]:
				self.precision[size]["average"] = self.precision[size]["average"] + self.precision[size][queryId]
			self.precision[size]["average"] = self.precision[size]["average"] / len(self.precision[size])
		
		if self.DEBUG_MODE:
			for size in self.precision:
				print "Precision for size = " + str(size) + " is: " + str(self.precision[size]["average"])


	def processRecall(self):
		for size in range(1,12):
			self.recall[size] = dict()
			for queryId in self.resultsData:
				
				expectedIds = list()
				for expectedResult in self.expectedData[queryId]:
					expectedIds.append(expectedResult["id"])

				topN = self.resultsData[queryId][:size]
				matches = 0
				for queryResult in topN:
					if queryResult["id"] in expectedIds:
						matches = matches + 1
				self.recall[size][queryId] = matches / float(len(expectedIds))

			self.recall[size]["average"] = 0
			for queryId in self.recall[size]:
				self.recall[size]["average"] = self.recall[size]["average"] + self.recall[size][queryId]
			self.recall[size]["average"] = self.recall[size]["average"] / len(self.recall[size])
		
		if self.DEBUG_MODE:
			for size in self.recall:
				print "Recall for size = " + str(size) + " is: " + str(self.recall[size]["average"])


	def calculateF1(self):
		for size in range(1,12):
			P = self.precision[size]["average"]
			R = self.recall[size]["average"]
			self.F1[size] = 2 * P * R / float( P + R )

		if self.DEBUG_MODE:
			for size in self.F1:
				print "F1 for size = " + str(size) + " is: " + str(self.F1[size])


	def calculatePrecisionAt10(self):
		self.precisionAt10 = self.precision[10]["average"]

		if self.DEBUG_MODE:
			print "Precision@10 is: " + str(self.precisionAt10)


	def calculateMAP(self):
		for size in range(1,12):
			self.MAP = self.MAP + self.precision[size]["average"]
		self.MAP = self.MAP / 11.0

		if self.DEBUG_MODE:
			print "MAP is: " + str(self.MAP)


	def calculateDCG(self):
		for queryId in self.resultsData:
			DCG = 0
			for queryResult in self.resultsData[queryId]:
				recordId = queryResult["id"]
				score = queryResult["score"]
				expectedPosition = None
				for i, expectedResult in enumerate(self.expectedData[queryId]):
					if expectedResult["id"] == recordId:
						expectedPosition = i
						break
				if not expectedPosition:
					continue
				discount = math.log(expectedPosition, 2)
				if not discount:
					continue
				DCG = DCG + ( score / discount )
			self.meanDCG = self.meanDCG + ( DCG / float(len(self.resultsData[queryId])) )
		self.meanDCG = self.meanDCG / float(len(self.resultsData))


		if self.DEBUG_MODE:
			print "Mean DCG is: " + str(self.meanDCG)


	def calculateNDCG(self):
		return


	def saveOutput(self):
		return


print "Starting: <Evaluator>"
EV = Evaluator(DEBUG_MODE=True, resultsFile="results_output.csv", expectedFile="PC_results_output.csv")
EV.evaluate()
EV.saveOutput()
print "...Finished! </Evaluator>"
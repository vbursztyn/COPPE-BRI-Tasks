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
	DCG = dict()
	NDCG = dict()

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


	def normalizeScore(self, score):
		topScore = 9
		minScore = 1
		nTopScore = 1.0
		nMinScore = 0.0
		ratio = (score - minScore) / (topScore - minScore)
		return ratio * (nTopScore - nMinScore) + nMinScore


	def findRelevancyScore(self, recordId, queryId):
		for expectedResult in self.expectedData[queryId]:
			if recordId == expectedResult["id"]:
				relevancyScore = self.normalizeScore(expectedResult["score"])
				return relevancyScore
		return 0.0


	def calculateDCG(self):
		MAX_P = 11
		for queryId in self.resultsData: # Do the sum of DCG(i) among all available queries:
			for i, queryResult in enumerate(self.resultsData[queryId]):
				i = i + 1
				if i > MAX_P:
					break
				if i not in self.DCG:
					self.DCG[i] = 0

				score = self.findRelevancyScore(queryResult["id"], queryId) # Find actual relevance (and normalize it).
				
				if i == 1:
					self.DCG[i] = self.DCG[i] + score
					continue
				
				discount = math.log(i, 2)
				if discount:
					self.DCG[i] = self.DCG[i] + score / discount
				
		
		queriesUsed = len(self.resultsData) # Average DCG(i), obtained by dividing the sum of all queries tested:
		for i in self.DCG:
			self.DCG[i] = self.DCG[i] / queriesUsed # So far, we have the "Discounted" and "Gain" aspects.

		for i in self.DCG: # On top of all averages, apply the "Cumulative" aspect of DCG:
			if i == 1:
				continue
			for j in self.DCG:
				if j == i:
					break
				self.DCG[i] = self.DCG[i] + self.DCG[j]		

		if self.DEBUG_MODE:
			for i in self.DCG:
				print "DCG for p = " + str(i) + " is: " + str(self.DCG[i])


	def calculateNDCG(self):
		# Now, the challenge is to normalize our DCGs with the DCGs of ideal orderings we could have achieved (IDCGs).
		MAX_P = 11
		idealOrdering = dict()
		IDCG = dict()
		for queryId in self.resultsData: # So, first, lets find all ideal orderings:
			idealOrdering[queryId] = list()
			for i, queryResult in enumerate(self.resultsData[queryId]):
				i = i + 1
				if i > MAX_P:
					break	
				score = self.findRelevancyScore(queryResult["id"], queryId)
				queryResult["score"] = score
				idealOrdering[queryId].append(queryResult)
			
			idealOrdering[queryId] = sorted(idealOrdering[queryId], key=lambda k: k["score"], reverse=True)

			for i, idealResult in enumerate(idealOrdering[queryId]): # Then respectives IDCGs:
				i = i + 1
				if i not in IDCG:
					IDCG[i] = 0

				score = self.findRelevancyScore(idealResult["id"], queryId)

				if i == 1:
					IDCG[i] = IDCG[i] + score
					continue
				
				discount = math.log(i, 2)
				if discount:
					IDCG[i] = IDCG[i] + score / discount


		queriesUsed = len(self.resultsData) # Same process as in for DCGs:
		for i in IDCG:
			IDCG[i] = IDCG[i] / queriesUsed # So far, we have the "Discounted" and "Gain" aspects.

		for i in IDCG: # Now the "Cumulative" aspect:
			if i == 1:
				continue
			for j in IDCG:
				if j == i:
					break
				IDCG[i] = IDCG[i] + IDCG[j]

		for i in self.DCG: # Finally, we create the normalized NDCG(i)
						   # with the ratio between actual results and the ideal ones.
			self.NDCG[i] = self.DCG[i] / IDCG[i]		

		if self.DEBUG_MODE:
			for i in self.NDCG:
				print "NDCG for p = " + str(i) + " is: " + str(self.NDCG[i])
				

	def saveOutput(self):
		return


print "Starting: <Evaluator>"
EV = Evaluator(DEBUG_MODE=True, resultsFile="SR_results_output.csv", expectedFile="PC_results_output.csv")
EV.evaluate()
print "...Finished! </Evaluator>"
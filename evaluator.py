

class Evaluator():


	resultsFile = ""
	expectedFile = ""
	resultsData = dict()
	expectedData = dict()

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
				continue # Similarly to above, parse stuff

		if self.DEBUG_MODE:
			print self.resultsData


	def evaluate(self):
		self.processPrecision()
		self.processRecall()
		self.calculateElevenPointsPrecisionRecall()
		self.calculateF1()
		self.calculateMAP()
		self.calculateDCG()
		self.calculateNDCG()
	

	def processPrecision(self):
		return


	def processRecall(self):
		return


	def calculateElevenPointsPrecisionRecall(self):
		return


	def calculateF1(self):
		return


	def calculatePrecisionAtTen(self):
		return


	def calculateMAP(self):
		return


	def calculateDCG(self):
		return


	def calculateNDCG(self):
		return


	def saveOutput(self):
		return


print "Starting: <Evaluator>"
EV = Evaluator(DEBUG_MODE=True, resultsFile="results_output.csv", expectedFile="PC_queries_output.csv")
EV.evaluate()
EV.saveOutput()
print "...Finished! </Evaluator>"
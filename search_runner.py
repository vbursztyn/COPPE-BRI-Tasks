

class SearchRunner():


    modelFile = ""
    queriesFile = ""
    queries = dict()
    BoW = dict()
    results = dict()
    resultsFile = ""

    DEBUG_MODE = False


    def __init__(self, DEBUG_MODE=False):
        self.DEBUG_MODE = DEBUG_MODE
        self.modelFile = "default_INDEX_output.csv"
        self.queriesFile = "default_PC_output_1.csv"
        self.resultsFile = "default_results_output.csv"
        self.setup()


    def setup(self, configFile="BUSCA.CFG"):
	    with open(configFile, "r") as fConfig:
	        for line in fConfig:
	            tokens = line.split("=")
	            if len(tokens) != 2:
	                print "WARNING: malformed line, skipping... Line: " + str(tokens)
	                continue

	            command = tokens[0]
	            argument = tokens[1].replace("\n", "")
	            if command == "MODELO":
	                self.modelFile = argument
	            elif command == "CONSULTAS":
	                self.queriesFile = argument
	            elif command == "RESULTADOS":
	                self.resultsFile = argument
	            else:
	                print "WARNING: malformed line, skipping... Line: " + str(tokens)
	                continue


    def openBoW(self, BoWSeparator=", "):
        with open(self.modelFile, "r") as fModel:
            for line in fModel:
                tokens = line.split(BoWSeparator)
                term = tokens[0]
                record = tokens[1]
                value = tokens[2].replace("\n", "")
                if term not in self.BoW:
                    self.BoW[term] = list()
                recordAndValue = dict()
                recordAndValue[record] = float(value)
                self.BoW[term].append(recordAndValue)
        if self.DEBUG_MODE:
            print self.BoW


    def validateTerms(self, queryStr):
    	terms = list()
    	termCandidates = queryStr.split(" ")
    	for candidate in termCandidates:
    		if len(candidate) <= 2:
    			continue
    		terms.append(candidate)
    	return terms


    def openQueries(self, querySeparator="; "):
    	with open(self.queriesFile, "r") as fQueries:
    		for line in fQueries:
    			tokens = line.split(querySeparator)
    			queryId = tokens[0]
    			queryText = tokens[1]
    			self.queries[queryId] = self.validateTerms(queryText)
    	if self.DEBUG_MODE:
    		print self.queries


    def runSingleTermSearch(self, term):
    	if term in self.BoW:
    		return self.BoW[term]
    	return None


    def mergeResults(self, destination, source):
    	for recordAndValue in source:
    		record = recordAndValue.keys()[0]
    		value = recordAndValue[record]
    		if record not in destination:
    			destination[record] = value
    		else:
    			destination[record] = destination[record] + value
    	return destination


    def run(self):
    	for query in self.queries:
    		queryResults = dict()
    		
    		for term in self.queries[query]:
    			termResults = self.runSingleTermSearch(term)
    			if not termResults:
    				continue
    			queryResults = self.mergeResults(queryResults, termResults)

    		self.results[query] = sorted(queryResults.items(), key=lambda k: k[1], reverse=True)
    	
    	if self.DEBUG_MODE:
    		print self.results


    def saveOutput(self, querySeparator="; ", resultSeparator=", "):
        print "Saving to: " + self.resultsFile
        with open(self.resultsFile, "w") as fOut:
            for query in self.queries:
                line = query + querySeparator + "[ "
                for i, result in enumerate(self.results[query]):
					line = line + "( " + str(i + 1) + ", " + result[0] + ", " + str(result[1]) + " )" + resultSeparator    
                cut = (len(resultSeparator)) * (-1)
                line = line[:cut] + " ]"
                fOut.write(line + "\n")


print "Starting: <SearchRunner>"
SR = SearchRunner()
SR.openBoW()
SR.openQueries()
SR.run()
SR.saveOutput()
print "...Finished! </SearchRunner>"
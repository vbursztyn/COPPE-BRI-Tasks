import untangle # XML handling
import regex # as in <<'re' boosted for unicode>>
import nltk # stemming


class ListGenerator():


    inputFiles = list()
    textExcerpts = dict()
    invertedIndex = dict()
    outputFile = ""

    USE_STEMMER = False

    DEBUG_MODE = False

    
    def __init__(self, DEBUG_MODE=False):
        self.DEBUG_MODE = DEBUG_MODE
        self.outputFile = "default_GLI_output.csv"
        self.setup()


    def setup(self, configFile="GLI.CFG"):
        with open(configFile, "r") as fConfig:
            for line in fConfig:
                tokens = line.split("=")

                if len(tokens) == 1:
                    singleToken = tokens[0].replace("\n", "")
                    if singleToken == "STEMMER":
                        self.USE_STEMMER = True
                        continue
                    elif singleToken == "NOSTEMMER":
                        continue # Default value already set to False, continue without warning

                if len(tokens) != 2:
                    print "WARNING: malformed line, skipping... Line: " + str(tokens)
                    continue

                command = tokens[0]
                argument = tokens[1].replace("\n", "")
                if command == "LEIA":
                    self.inputFiles.append(argument)
                elif command == "ESCREVA":
                    self.outputFile = argument
                else:
                    print "WARNING: malformed line, skipping... Line: " + str(tokens)
                    continue


    def formatText(self, text):
        formatted = text.replace("\n", " ")
        formatted = regex.sub(ur"[\p{P}+]", "", formatted)
        if self.USE_STEMMER:
            porter = nltk.stem.PorterStemmer()
            formatted = " ".join([ porter.stem(term) for term in formatted.split(" ") ])
        return formatted.upper()
    

    def batchOpen(self): # TO-DO: catch FileNotFound exception
        print "Reading from input files: " + str(self.inputFiles)
        for xmlFile in self.inputFiles:
            fileObj = untangle.parse(xmlFile)
            records = fileObj.FILE.RECORD
            for record in records:
                recordId = record.RECORDNUM.cdata
                if hasattr(record, "ABSTRACT"):
                    if hasattr(record.ABSTRACT, "cdata"):
                        recordText = record.ABSTRACT.cdata
                        self.textExcerpts[recordId] = self.formatText(recordText)
                    continue
                if hasattr(record, "EXTRACT"):
                    for extract in record.EXTRACT:
                        recordText = recordText + " " + extract.cdata
                    self.textExcerpts[recordId] = self.formatText(recordText)
        if self.DEBUG_MODE:
            print self.textExcerpts


    def batchProcessLists(self):
    	for recordId, text in self.textExcerpts.iteritems():
    		terms = text.split(" ")
    		for term in terms:
    			if term == "":
    				continue
    			if term not in self.invertedIndex:
    				self.invertedIndex[term] = list()
    			self.invertedIndex[term].append(recordId)
        if self.DEBUG_MODE:
            print self.invertedIndex				


    def saveOutput(self, termSeparator="; ", recordSeparator=", "):
    	print "Saving to: " + self.outputFile
    	with open(self.outputFile, "w") as fOut:
    		for term, records in self.invertedIndex.iteritems():
    			line = term + termSeparator + "[ "
    			for record in records:
    				line = line + record.strip() + recordSeparator
    			cut = (len(recordSeparator))*(-1)
    			line = line[:cut]
    			fOut.write(line + " ]\n")


print "Starting: <ListGenerator>"
LG = ListGenerator()
LG.batchOpen()
LG.batchProcessLists()
LG.saveOutput(termSeparator="; ", recordSeparator=", ")
print "...Finished! </ListGenerator>"
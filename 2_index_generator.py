

class Indexer():


    inputFile = ""
    inputTermSeparator = ""
    inputRecordSeparator = ""
    BoW = dict()
    # We do not need text lengths for regular tf-idf. However, based on class notes,
    # we shall be prepared to put this parameter in good use in a near future.
    recordsLengths = dict()
    outputFile = ""

    DEBUG_MODE = False


    def __init__(self, DEBUG_MODE=False):
        self.DEBUG_MODE = DEBUG_MODE
        self.inputTermSeparator = "; "
        self.inputRecordSeparator = ", "
        self.outputFile = "default_INDEX_output.csv"
        self.setup()


    def setup(self, configFile="INDEX.CFG"):
        with open(configFile, "r") as fConfig:
            for line in fConfig:
                tokens = line.split("=")
                if len(tokens) != 2:
                    print "WARNING: malformed line, skipping... Line: " + str(tokens)
                    continue

                command = tokens[0]
                argument = tokens[1].replace("\n", "")
                if command == "LEIA":
                    self.inputFile = argument
                elif command == "ESCREVA":
                    self.outputFile = argument
                else:
                    print "WARNING: malformed line, skipping... Line: " + str(tokens)
                    continue


    def validateTerm(self, term):
        term = term.strip()
        if len(term) <= 2:
            return ""
        if any(char.isdigit() for char in term):
            return ""
        return term


    def openInvertedIndex(self):
        # print "Reading from input file: " + self.inputFile
        with open(self.inputFile, "r") as fIn:
            for line in fIn:
                tokens1 = line.split(self.inputTermSeparator)
                if len(tokens1) != 2:
                    print "WARNING: malformed line, skipping... Line: " + str(tokens1)
                    continue

                # impose some validation rules for keeping terms
                term = self.validateTerm(tokens1[0])
                if term == "":
                    continue

                recordStr = tokens1[1]
                recordStr = recordStr.replace("[", "").replace("]", "").replace("\n", "")
                tokens2 = recordStr.split(self.inputRecordSeparator)
                if not len(tokens2):
                    print "WARNING: malformed line, skipping... Line: " + str(tokens1)
                    continue

                self.BoW[term] = dict()
                for record in tokens2:
                    record = record.strip()
                    if record == "":
                        continue
                    if record not in self.BoW[term]:
                        self.BoW[term][record] = 1
                    else:
                        self.BoW[term][record] = self.BoW[term][record] + 1

                    # In both cases, we just found a valid term-record pair.
                    # This way, we can also increment record's length:
                    if record not in self.recordsLengths:
                        self.recordsLengths[record] = 1
                    else:
                        self.recordsLengths[record] = self.recordsLengths[record] + 1
        if self.DEBUG_MODE:
            print self.BoW
            print self.recordsLengths


    def processBoW(self):
        for term in self.BoW:
            occurencesInAllDocuments = 0
            for record in self.BoW[term]:
                occurencesInAllDocuments = occurencesInAllDocuments + self.BoW[term][record]
            for record in self.BoW[term]:
                self.BoW[term][record] = self.calculateTfIdf(self.BoW[term][record], occurencesInAllDocuments)
        if self.DEBUG_MODE:
            print self.BoW


    def calculateTfIdf(self, occurencesInRecord, occurencesInAllDocuments):
		return occurencesInRecord / float(occurencesInAllDocuments)


    def saveOutput(self):
        print "Saving to: " + self.outputFile
        with open(self.outputFile, "w") as fOut:
            for term, records in self.BoW.iteritems():
                for recordId, tfIdf in records.iteritems():
                    fOut.write(term + ", " + recordId + ", " + "{0:.4f}".format(tfIdf) + "\n")


print "Starting: <IndexGenerator>"
IDX = Indexer()
IDX.openInvertedIndex()
IDX.processBoW()
IDX.saveOutput()
print "...Finished! </IndexGenerator>"

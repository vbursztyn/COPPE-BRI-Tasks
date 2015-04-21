import untangle # XML handling
import regex # as in <<'re' boosted for unicode>>
import nltk # stemming


class QueriesProcessor():


    inputFiles = list()
    queriesAndResults = dict()
    outputQueries = ""
    outputResults = ""

    USE_STEMMER = False

    DEBUG_MODE = False


    def __init__(self, DEBUG_MODE=False):
        self.DEBUG_MODE = DEBUG_MODE
        self.outputQueries = "default_PC_output_1.csv"
        self.outputResults = "default_PC_output_2.csv"
        self.setup()


    def setup(self, configFile="PC.CFG"):
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
                elif command == "CONSULTAS":
                    self.outputQueries = argument
                elif command == "ESPERADOS" or command == "RESULTADOS":
                    self.outputResults = argument
                else:
                    print "WARNING: malformed line, skipping... Line: " + str(tokens)
                    continue


    def countVotes(self, votesStr):
        votes = 0
        for char in votesStr:
            if char.isdigit():
                votes = votes + int(char)
        return str(votes)


    def formatText(self, text):
        formatted = text.replace("\n", " ")
        formatted = regex.sub(ur"[\p{P}+]", "", formatted)
        if self.USE_STEMMER:
            porter = nltk.stem.PorterStemmer()
            formatted = " ".join([ porter.stem(term) for term in formatted.split(" ") ])
        return formatted.upper()


    def batchOpen(self):  # TO-DO: catch FileNotFound exception
        print "Reading from input files: " + str(self.inputFiles)
        for xmlFile in self.inputFiles:
            fileObj = untangle.parse(xmlFile)
            queries = fileObj.FILEQUERY.QUERY
            for query in queries:
                queryId = query.QueryNumber.cdata
                queryText = query.QueryText.cdata
                queryResults = list()
                results = query.Records

                for item in results.Item:
                    resultItem = dict()
                    resultItem["id"] = item.cdata
                    resultItem["votes"] = self.countVotes(item["score"])
                    queryResults.append(resultItem)

                queryResults = sorted(queryResults, key=lambda k: k["votes"], reverse=True)

                self.queriesAndResults[queryId] = dict()
                self.queriesAndResults[queryId]["text"] = self.formatText(queryText)
                self.queriesAndResults[queryId]["results"] = queryResults
        if self.DEBUG_MODE:
            print self.queriesAndResults


    def saveOutput(self, querySeparator="; ", resultSeparator=", "):
        print "Saving to: " + self.outputQueries
        with open(self.outputQueries, "w") as fQueries:
            for queryId in self.queriesAndResults:
                line = queryId + querySeparator + self.queriesAndResults[queryId]["text"]
                fQueries.write(line + "\n")

        print "Saving to: " + self.outputResults
        with open(self.outputResults, "w") as fResults:
            for queryId in self.queriesAndResults:
                line = queryId + querySeparator + "[ "
                for result in self.queriesAndResults[queryId]["results"]:
                    line = line + "( " + result["id"] + ", " + result["votes"] + " )" + resultSeparator
                cut = (len(resultSeparator))*(-1)
                line = line[:cut] + " ]"
                fResults.write(line + "\n")


print "Starting: <QueriesProcessor>"
QP = QueriesProcessor()
QP.batchOpen()
QP.saveOutput(querySeparator="; ", resultSeparator=", ")
print "...Finished! </QueriesProcessor>"
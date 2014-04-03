#!/usr/bin/python

# Stemplex class definition
# 2014-04-03
# Jackson Lee

import math
import itertools
import time
import random
import numpy
import codecs
import re

#####################################################

# Cost parameters

#STEM_USED = 1
#STEM_NOT_USED = 20
#AFFIX_USED = 5
#AFFIX_NOT_USED = 10
#EXTRA = 30

#STEM_USED = 3
#STEM_NOT_USED = 4
#AFFIX_USED = 1
#AFFIX_NOT_USED = 2
#EXTRA = 10

STEM_USED = 4
STEM_NOT_USED = 3
AFFIX_USED = 1
AFFIX_NOT_USED = 2
EXTRA = 10

#STEM_USED = 4
#STEM_NOT_USED = 3
#AFFIX_USED = 2
#AFFIX_NOT_USED = 1
#EXTRA = 1

AFFIX_DIFF = 5

LAMBDA_BITS = 5 # lambda

#####################################################

###############
## Functions ##
###############

#----------------------------------------------------------------#

# highest common factor (HCF) and least common multiple (LCM)
# source: http://stackoverflow.com/questions/147515/least-common-multiple-for-3-or-more-numbers
# date of access: 2014-02-07

def gcd(a, b):
    """Return greatest common divisor using Euclid's Algorithm."""
    while b:      
        a, b = b, a % b
    return a

def lcm(a, b):
    """Return lowest common multiple."""
    return a * b // gcd(a, b)

def lcmm(args):
    """Return lcm of args."""   
    return reduce(lcm, args)

#----------------------------------------------------------------#

def choose(n,k):
    'n choose k'
    import math
    return math.factorial(n)/(math.factorial(k)*math.factorial(n-k))

#----------------------------------------------------------------#

def null(s):
    if s:
        return s
    else:
        return '\\O'

#----------------------------------------------------------------#

def unorder(s):
    'takes a string and returns its alphabetized version'
    return ''.join(sorted(list(iter(s))))

#----------------------------------------------------------------#

def reorder(s, sample):
    'takes a string s and re-orders its characters according to "sample"'
    result = ''
    for character in sample:
        if character in s:
            result += character
            s = s.replace(character,'',1)
    if result:
        return result
    else:
        return '{\\O}'

#----------------------------------------------------------------#

def union(s):
    'takes a list of strings and returns its union'
    temp = unorder(''.join(s))
    letters = list(set(sorted([x for x in temp])))
    result = ''
    for l in letters:
        c = 0
        for word in s:
            if word.count(l) > c:
                c = word.count(l)
        result += l*c
    return result

#----------------------------------------------------------------#

def cost(stem,affix,target):
    '''calculates the cost of a (stem, affix, target) trio
    and returns the 5-dimensional cost vector'''

    stemUsed = 0 # count of stem letters used
    stemNotUsed = 0  # count of stem letters not used
    affixUsed = 0  # count of affix letters used
    affixNotUsed = 0  # count of affix letters not used
    extra = 0  # count of extra letters needed
    tempStem = str(stem)
    tempAffix = str(affix)

    for l in target:
        if l in tempStem:
            stemUsed += 1
            tempStem = tempStem.replace(l,'',1)
        elif l in tempAffix:
            affixUsed += 1
            tempAffix = tempAffix.replace(l,'',1)
        else:
            extra += 1
    stemNotUsed = len(stem) - stemUsed
    affixNotUsed = len(affix) - affixUsed

    return numpy.array([STEM_USED*stemUsed, STEM_NOT_USED*stemNotUsed,
             AFFIX_USED*affixUsed, AFFIX_NOT_USED*affixNotUsed, EXTRA*extra])

#----------------------------------------------------------------#

def shortest(L):
    'finds the shortest string(s) in a list'
    c = min([len(w) for w in L]) # shortest length in L
    return [x for x in L if len(x) == c]


#----------------------------------------------------------------#


def createUnionAffixes(affixLists):
    'takes a list of lists of affixes, and returns the list of union affixes'
    return [unorder(union(x)) for x in zip(*affixLists)]
#    return map(lambda x,y: unorder(union([x,y])), group1, group2)


#----------------------------------------------------------------#

def sublist(L, indices):
    'takes list L and outputs a sublist from L whose indices in L are specified'
    tempList = list()
    for i in indices:
        tempList.append(L[i])
    return tempList


def locateByIndex(string, substring):
    '''locate substring in string by indices of string'''
    resultIndexList = list()
    i = 0
    while i < len(string):
        try:
            startIndex = string[i:].index(substring)
        except ValueError:
            break
        resultIndexList.append(startIndex + i)
        i = startIndex + i + 1
    return list(resultIndexList)

#----------------------------------------------------------------#

#####################################################

####################
## Class Stemplex ##
####################

class Stemplex:
    def __init__(self, L, rowNumber, nColumns):
        self.MyDirtyFlag = False

        self.MySourceRowList = [L[1:]]
        self.MyRowNumberList = [rowNumber]
        self.numColumns = nColumns

        # alphabetize all source words in the paradigm
        unorderL = [unorder(x) for x in L[1:]]

        # find the stem
        self.shortWord = shortest(L[1:])[0] # need shortWord for function "reorder"
        shortWordUnorder = unorder(self.shortWord)
        stem = ''
        for l in shortWordUnorder:
            AllExist = True # whether l exists in each of the words in unorderL
            for w in unorderL:
                if l not in w:
                    AllExist = False
                    break
            if AllExist:
                stem += l
                unorderL = [w.replace(l,'',1) for w in unorderL]

        self.MyStemList = [stem]
        self.MyTargetsList = [[unorder(x) for x in L[1:]]]
        self.MyOriginalAffixesList = [unorderL]
        self.MyAffixes = unorderL

        self.MyGrammarCost = 0
        self.MyCostMatrixList = []
        self.MyDataCost = 0
        self.MyTotalCost = 0
        self.updateEverything()

        # use the first word form in the data (usually the infinitive) as the paradigm's leaf
        self.MyTree = L[0]
        self.MyBareTree = L[0]
        self.MyCollapsedBareTree = L[0]
        self.MyLeaveList = [L[0]]
        self.MyCollapsedTree = ''

        # encode this stemplex as a node in a tree
        self.MyNodeIndex = 0

    #class Stemplex------------------------------------------------------------#

    def updateEverything(self):
        self.computeGrammarCost()
        self.computeCostMatrixList()
        self.computeDataCost()
        self.computeTotalCost()
        self.MyDirtyFlag = False

    def leaves(self):
        return self.MyLeaveList

#    def nodeIndex(self):
#        return self.MyNodeIndex

#    def nodeDaughters(self):
#        return self.MyNodeDaughters

#    def nodeMother(self):
#        return self.MyNodeMother

    def rowNums(self):
        return self.MyRowNumberList

    def sourceRows(self):
        return self.MySourceRowList

#    def improvedSourceRows(self):
#        return self.MyImprovedSourceRowList

#    def improvedSourcedRowDictList(self):
#        return self.MyImprovedSourceRowDictList

#    def improvedSourceRowBagOfSymbolsList(self):
#        return self.MyImprovedSourceRowBagOfSymbolsList

    def improvedSourcedRowSubstringDictList(self):
        return self.MyImprovedSourceRowSubstringDictList

    def stems(self):
        return self.MyStemList

    def targets(self):
        return self.MyTargetsList

    def originalAffixes(self):
        return self.MyOriginalAffixesList

    def affixes(self):
        return self.MyAffixes

    def tree(self):
        return self.MyTree

    def bareTree(self):
        return self.MyBareTree

    def collapsedBareTree(self):
        return self.MyCollapsedBareTree

    def collapsedTree(self):
        return self.MyCollapsedTree

    #class Stemplex------------------------------------------------------------#

    def affixMatrix(self):
        return numpy.array(self.affixes())

    #class Stemplex------------------------------------------------------------#

    def grammarCost(self):
        if self.MyDirtyFlag:
            self.updateEverything()
        return self.MyGrammarCost

    def computeGrammarCost(self):
#        self.MyGrammarCost = LAMBDA_BITS * (len(''.join(self.MyStemList)) + self.MyStemList.count('') + len(''.join(self.MyAffixes)) + self.MyAffixes.count('') + self.numColumns)
        self.MyGrammarCost = LAMBDA_BITS * (len(''.join(self.MyStemList)) + len(''.join(self.MyAffixes)) + self.numColumns)

    #class Stemplex------------------------------------------------------------#

    def costMatrixList(self):
        if self.MyDirtyFlag:
            self.updateEverything()
        return self.MyCostMatrixList

    def computeCostMatrixList(self):
        matrixList = list()
        for (e, stem) in enumerate(self.MyStemList):
            matrixForEachStem = numpy.zeros((self.numColumns,5), dtype=int)
            try:
                for k in range(self.numColumns):
                    matrixForEachStem[k] = cost(stem, self.MyAffixes[k], self.MyTargetsList[e][k])
            except:
                print 'self.MySourceRowList', self.MySourceRowList
                print 'matrixForEachStem', matrixForEachStem
                print 'e', e
                print 'k', k
                print 'self.numColumns', self.numColumns
                print 'self.MyAffixes', self.MyAffixes
                print 'self.MyTargetsList', self.MyTargetsList
                print 'self.MyAffixes[k]', self.MyAffixes[k]
                print 'matrixForEachStem[k]', matrixForEachStem[k]
                print 'self.MyTargetsList[e][k]', self.MyTargetsList[e][k]
                raw_input()
            matrixList.append(matrixForEachStem.T)
        self.MyCostMatrixList =  matrixList

    #class Stemplex------------------------------------------------------------#

    def dataCost(self):
        if self.MyDirtyFlag:
            self.updateEverything()
        return self.MyDataCost

    def computeDataCost(self):
        self.MyDataCost = sum([matrixForEachStem.sum() for matrixForEachStem in self.costMatrixList()])

    #class Stemplex------------------------------------------------------------#

    def totalCost(self):
        if self.MyDirtyFlag:
            self.updateEverything()
        return self.MyTotalCost

    def computeTotalCost(self):
        self.MyTotalCost = self.grammarCost() + self.dataCost()

    #class Stemplex------------------------------------------------------------#


    def merge(self, stmplx, newAlignment, mergeCount=None, costSaved=None, nodeDict=None, leftLeaves=None, rightLeaves=None):
        # When mergeCount==None, this merge() function is only *pretending* to merge two stemplexes,
        # because in this case the focus is the total cost (if merged), not really doing the merge.

        self.MyLeaveList += stmplx.leaves()
        self.MyStemList += stmplx.stems()
        self.MyRowNumberList += stmplx.rowNums()

        self.MySourceRowList += [[s[i] for i in newAlignment] for s in stmplx.sourceRows()]
        self.MyImprovedSourceRowList += [[s[i] for i in newAlignment] for s in stmplx.improvedSourceRows()]
        self.MyTargetsList += [[s[i] for i in newAlignment] for s in stmplx.targets()]
        self.MyOriginalAffixesList += [[s[i] for i in newAlignment] for s in stmplx.originalAffixes()]

        # createUnionAffixes() takes a list of two lists.
        # The second affix list is in its new alignment.
        self.MyAffixes = createUnionAffixes([self.affixes(), [stmplx.affixes()[i] for i in newAlignment]])

        self.updateEverything()

        if costSaved < 0:
            costSavedStr = '{\\color{red}' + str(costSaved) + '}'
        else:
            costSavedStr = str(costSaved)

        self.MyTree = '[.{' + str(mergeCount) + '$_{' + costSavedStr + '}$} ' + self.MyTree + ' ' + stmplx.tree() + ' ]'
        self.MyBareTree = '[ ' + self.MyBareTree + ' ' + stmplx.bareTree() + ' ]'

        # updating tree node information
#        self.MyNodeDaughters = (self.MyNodeIndex, stmplx.MyNodeIndex)
        self.MyNodeIndex = mergeCount


        if nodeDict:

            self.MyCollapsedTree = self.MyTree

            ###################################################################
            # create a collapsed tree, where paradigms that are morphologically
            # identical collapse if the following two conditions are met:
            #   1. they all are in the same subtree in self.MyTree
            #   2. their saved costs at each mother node inside are the same
            ###################################################################

            # locate nodes which:
            #  1. have only one leaf as left daughter and only one leaf as right daughter
            #  2. are the *right* daughter of another node
            #  3. have a sister node that consists only of one single leaf
            #
            #        mother
            #         /  \
            #      leaf  *SELF* <== locate
            #             /  \
            #           leaf  leaf

            candidateNodeList = list()

            for k in filter(lambda x: x < ROWS, nodeDict.keys()):
                print 'k', k
                print 'nodeDict[k].MyLeftDaughterLeaves', nodeDict[k].MyLeftDaughterLeaves
                print 'nodeDict[k].MyRightDaughterLeaves', nodeDict[k].MyRightDaughterLeaves
                print 'nodeDict[k].MyMother', nodeDict[k].MyMother
                if (nodeDict[k].MyLeftDaughterLeaves and nodeDict[k].MyRightDaughterLeaves and nodeDict[k].MyMother) and \
                   (len(nodeDict[k].MyLeftDaughterLeaves) == len(nodeDict[k].MyRightDaughterLeaves) == 1) and \
                   (nodeDict[nodeDict[k].MyMother].MyRightDaughter == k) and \
                   (len(nodeDict[nodeDict[k].MyMother].MyLeftDaughterLeaves) == 1):
                    candidateNodeList.append(k)

            print '\ncandidateNodeList', candidateNodeList

            collapseNodeList = [0] * len(candidateNodeList)
            # ^-- will contain the node indices for nodes to collapse, after the following for-loop

            for (e,k) in enumerate(candidateNodeList):
                currentNodeIndex = k
                currentNodeCostSaved = nodeDict[k].MyCostSaved

                while True and nodeDict[currentNodeIndex].MyMother:
                    motherNodeIndex = nodeDict[currentNodeIndex].MyMother
                    motherNodeCostSaved = nodeDict[nodeDict[currentNodeIndex].MyMother].MyCostSaved

                    # if...
                    #    1. my own cost saved == my mum's cost saved
                    #    2. my sister consists only of a single leaf
                    # then:
                    #    signal the merging of my mum and myself
                    # else:
                    #    leave this while loop

                    if (currentNodeCostSaved == motherNodeCostSaved) and \
                       (len(nodeDict[motherNodeIndex].MyLeftDaughterLeaves) ==  1):
                        collapseNodeList[e] = motherNodeIndex
                    else:
                        break

                    currentNodeIndex = motherNodeIndex
                    currentNodeCostSaved = motherNodeCostSaved

            print '\ncollapseNodeList:'
            print collapseNodeList#; raw_input()

            # collapseNodeList contains node indices for nodes to collapse
            # if node index == 0 in collapseNodeList, ignore it. (No node index can be 0.)

            # for each node to collapse
            #     find the corresponding subtree '[ ... ]' in self.MyTree (use technique of matching parentheses)

            for nodeIndex in filter(lambda x: x, collapseNodeList):
                search_str = '[.{' + str(nodeIndex) + '$'
                try:
                    subtree = self.MyTree[self.MyTree.index(search_str):]
                except ValueError: # when this nodeIndex is not relevant to the current merge
                    continue

                paren_count = 0
                for (e,char) in enumerate(subtree):
                    if char == '[':
                        paren_count += 1
                    elif char == ']':
                        paren_count -= 1
                    if paren_count == 0:
                        matchParenIndex = e
                        break

                replacee = subtree[:matchParenIndex+1]

#                print '\nreplacee', replacee; raw_input()

                replacer = '{\\begin{tabular}{|ll|} \\hline ' + \
                            ''.join([x+' \\\ ' if e % 2 else x+' & ' for (e,x) in enumerate(nodeDict[nodeIndex].MyDaughterLeaves)]) + \
                            '#\\hline \\end{tabular}} '
                if len(nodeDict[nodeIndex].MyDaughterLeaves) % 2:
                    replacer = replacer.replace('#','\\\ ')
                else:
                    replacer = replacer.replace('#',' ')

                self.MyCollapsedTree = self.MyCollapsedTree.replace(replacee, replacer)
                if '[' not in self.MyCollapsedTree:
                    self.MyCollapsedTree = '[ ' + self.MyCollapsedTree + ' ]'

        self.MyCollapsedBareTree = ' '.join([x if x[0] != '[' else '[' for x in self.MyCollapsedTree.split()])

    #class Stemplex------------------------------------------------------------#

    def printTerminal(self):
        print 'Row numbers:', self.rowNums()
        print 'Source rows:', self.sourceRows()
        print 'Number of rows:', len(self.rowNums())
        print 'Stems:', self.stems()
        print 'Targets:', self.targets()
        print 'Original affixes:', self.originalAffixes()
        print 'Affixes:', self.affixes()
        print 'grammar cost:', self.grammarCost()
        print 'data cost:', self.dataCost()
        print 'total cost:', self.totalCost()
        print 'tree:', self.tree()
        print 'cost matrix:', self.costMatrixList()
        print


    #class Stemplex------------------------------------------------------------#


    def printlatex(self, latexfile):

        # -----------------------------------
        #  print the tree
        # -----------------------------------
        #latexfile.write('\\begin{landscape}\n')
        latexfile.write('%s\n\n' % (latexfile.name))
        latexfile.write('\\normalsize{\n\n')
        latexfile.write('\\Tree ')
        latexfile.write(self.tree())
        latexfile.write('\\\ \n\n')
        latexfile.write('\\Tree ')
        latexfile.write(self.collapsedTree())
        latexfile.write('\\\ \n\n')
        latexfile.write('\\Tree ')
        latexfile.write(self.bareTree())
        latexfile.write('\\\ \n\n')
        latexfile.write('\\Tree ')
        latexfile.write(self.collapsedBareTree())
        latexfile.write('\\\ \n')
        latexfile.write('} % end of non-normal font size\n')
        latexfile.write('\\end{landscape}\n')
#        latexfile.write('\\newpage\n')

        latexfile.write('\\begin{longtable}[l]{%s}\n\\toprule\n' % ('l'+'l'*(self.numColumns*2)))

        # -----------------------------------
        #  print alignment results in words
        # -----------------------------------
        for (stem, rowSourceWords) in zip(self.stems(), self.improvedSourceRows()):
            latexfile.write('{\\color{red} %s} & ' % (null(stem)))
            latexfile.write('%s \\\ \n' %
               (' & '.join(['\\multicolumn{2}{r}{'+x+'}' for x in rowSourceWords])))
        latexfile.write('\\toprule\n')

        # ---------------------
        #  print union affixes
        # ---------------------
        for unionAffix in self.affixes():
            latexfile.write('& \\multicolumn{2}{r}{\\color{red}-%s-} ' % (null(unionAffix)))
        latexfile.write('\\\ \n\\toprule\n')

        # ---------------------------------------------------------------------
        #  for each paradigm, print:
        #
        #  STEM     (AFFIX,TARGET)  (AFFIX,TARGET)  (AFFIX,TARGET)...
        #            __________________________________________________
        #           |            5xk cost matrix here                  |
        #           |__________________________________________________|
        # ---------------------------------------------------------------------
        for (e, stem) in enumerate(self.stems()):
            if e:
                latexfile.write('\\toprule\n')

            # print Stem 
            latexfile.write('{\\color{red} %s} ' % (null(stem)))

            # print { (Affix,Target), (Affix,Target), ...}
            for k in range(self.numColumns):
                latexfile.write('& (%s, & %s) ' % (null(self.originalAffixes()[e][k]),
                                                   self.targets()[e][k]))
            latexfile.write('\\\ \n')

            # print costMatrix
            costMatrix = self.costMatrixList()[e]
            wordDataCostVector = costMatrix.sum(axis=0) # axis=0 to get vertical sums
            for line in costMatrix: # there are 5 lines in self.costMatrixList()[e]
                for pointCost in line: # pointCost = cell cost in costMatrix
                    latexfile.write('& & %d ' % (pointCost))
                latexfile.write('\\\ \n')
            latexfile.write('\\midrule\n')
            latexfile.write('{\\color{blue} %d} ' % (self.costMatrixList()[e].sum()))
            for wordDataCost in wordDataCostVector:
                latexfile.write('& & %d ' % (wordDataCost))
            latexfile.write('\\\ \n')

        latexfile.write('\\bottomrule\n\\end{longtable}\n\n')

        # ----------------------
        # -- print cost summary
        # ----------------------

#        latexfile.write('Data cost = %d ({\\color{blue}%d}+{\\color{blue}%d}+{\\color{blue}%d})\\\ '
#                % (sum(dataCost), dataCost[0], dataCost[1], dataCost[2]))
        latexfile.write('Total cost = %d\n\n' % (self.totalCost()))
        latexfile.write('Grammar cost = %d\n\n' % (self.grammarCost()))
        latexfile.write('Data cost = %d\n\n' % (self.dataCost()))


        # latexfile.write('\\end{landscape}\n')
        latexfile.write('\\break\n\n')

    ################################################################################
    # compute the 'improved' sourcerow and latex-color the word forms
    # for stem, prefix, infix, suffix
    #
    # data structure of self.extractStemX (X = {Substring, Multiset, Subsequence}):
    #     { possibleStem1 :
    #            [ [(indexTuple1), ...], [(indexTuple1), ...], ... ]
    #       possibleStem2 : 
    #            [ [(indexTuple1), ...], [(indexTuple1), ...], ... ] }
    #
    # ALGORITHM 1:
    # among all words in a paradigm, find the longest common substring(s)
    #
    # ALGORITHM 2:
    # use bags of letters (multisets) from stem, find their best match in each word form
    #
    ################################################################################

    def extractStemSubstring(self):
        resultDict = dict()
        sourceRow = self.MySourceRowList[0]

        # if the shortest multiset stem is a null string, then the paradigm is completely suppletive
        if self.MyStemList[0] == '':
            sourceWordsIndexList = map(lambda x: [tuple(range(len(x)))], sourceRow)
            resultWordMasterList = list()
            for i in range(len(sourceRow)):
                resultWordMasterList.append(sourceWordsIndexList[i])
            resultDict[''] = resultWordMasterList
            return resultDict

        longestLength = 0

        for k in range(len(self.shortWord), -1, -1): # k = length of stem
            if k <= longestLength:
                break

            numOfPossibleStems = len(self.shortWord) - k + 1
            # if len(shortWord) == 5 and k == 5, there's 1 possible stem
            # if len(shortWord) == 5 and k == 4, there are 2 possible stems

            possibleStemList = [self.shortWord[i: i+k]
                                for i in range(numOfPossibleStems)]

            for possibleStem in possibleStemList:
                goodStem = True # whether a possible stem is a substring common
                                # to ALL words in a paradigm
                for sourceWord in sourceRow:
                    if possibleStem not in sourceWord:
                        goodStem = False
                        break

                if goodStem:
                    resultList = list()
                    if not longestLength:
                        longestLength = len(possibleStem)

                    # get indices in source words
                    for sourceWord in sourceRow:
                        indexTuplesList = [tuple(range(x,x+len(possibleStem)))
                                           for x in locateByIndex(sourceWord, possibleStem)]
                        resultList.append(indexTuplesList)

                    resultDict[possibleStem] = resultList
        return resultDict


    #class Stemplex------------------------------------------------------------#


    def extractStemMultiset(self):
        resultDict = dict()
        sourceRow = self.MySourceRowList[0]
        multisetStem = self.MyStemList[0]
        multisetStemSet = list(set(multisetStem))

        # if the shortest multiset stem is a null string, then the paradigm is completely suppletive
        if self.MyStemList[0] == '':
            sourceWordsIndexList = map(lambda x: [tuple(range(len(x)))], sourceRow)
            resultWordMasterList = list()
            for i in range(len(sourceRow)):
                resultWordMasterList.append(sourceWordsIndexList[i])
            resultDict[''] = resultWordMasterList
            return resultDict

        # stemIndicesMasterList =
        # [
        #     [ <= indexList, for a source word
        #         [ (indices), (indices) ], <= list(NChooseKCombos), for a particular stem character
        #         [ (indices) ] ...
        #     ]
        # ]
        stemIndicesMasterList = list()
        for sourceWord in sourceRow:
            indexList = list()

            for stemChar in multisetStemSet:
                numOfStemCharInStem = multisetStem.count(stemChar)
                stemCharIndexList = locateByIndex(sourceWord, stemChar)

                NChooseKCombos = itertools.combinations(stemCharIndexList, numOfStemCharInStem)
                indexList.append(list(NChooseKCombos))

            stemIndicesMasterList.append(indexList)

        resultList = list()
        for (sourceWord, stemIndicesList) in zip(sourceRow, stemIndicesMasterList):
            LCM = lcmm(map(len, stemIndicesList)) # least common multiple among lengths
                                                  # = number of source word patterns

            indexMatrix = list()
            for stemIndices in stemIndicesList:
                factor = LCM / len(stemIndices)
                indexMatrix.append( stemIndices * factor )

            indexTuplesList = list()
            for i in range(LCM):
                indexTuple = tuple()
                for stemCharIndices in indexMatrix:
                    indexTuple = indexTuple + stemCharIndices[i]
                indexTuplesList.append(tuple(sorted(indexTuple)))

            resultList.append(indexTuplesList)

        resultDict[multisetStem] = resultList

        return resultDict


    #class Stemplex------------------------------------------------------------#


    def extractStemSubsequence(self):
        resultDict = dict()
        sourceRow = self.MySourceRowList[0]
        goodStemList = list()
        longestLength = 0

        # if the shortest multiset stem is a null string, then the paradigm is completely suppletive
        if self.MyStemList[0] == '':
            sourceWordsIndexList = map(lambda x: [tuple(range(len(x)))], sourceRow)
            resultWordMasterList = list()
            for i in range(len(sourceRow)):
                resultWordMasterList.append(sourceWordsIndexList[i])
            resultDict[''] = resultWordMasterList
            return resultDict

        # find all good stem subsequences => goodStemList
        for k in range(len(self.shortWord), -1, -1): # k = length of stem
            if k <= longestLength:
                break

            possibleStemList = list(itertools.combinations(self.shortWord, k))

            for possibleStem in possibleStemList: # type(possibleStem) = tuple
                for sourceWord in sourceRow:
                    NChooseKCombos = list(itertools.combinations(sourceWord, k))
                    if possibleStem not in NChooseKCombos:
                        break
                else:
                    goodStemList.append(''.join(possibleStem))
                    if not longestLength:
                        longestLength = len(possibleStem)

        #### work from here ####
        #### at this indentation level ###

        for stemSubsequence in goodStemList: # type(stemSubsequence) = tuple
            resultList = list()

            for sourceWord in sourceRow:
                wordResultList = list()
                stemCharIndexInWordList = list()

                for stemChar in stemSubsequence:
                    stemCharIndexInWordList.append(locateByIndex(sourceWord, stemChar))

                stemIndicesInWordList = list(itertools.product(*stemCharIndexInWordList))

                for stemIndicesInWord in stemIndicesInWordList:

                    for i in range(len(stemIndicesInWord)-1):
                        if not (stemIndicesInWord[i] < stemIndicesInWord[i+1]):
                            break
                    else:
                        wordResultList.append(stemIndicesInWord)

                resultList.append(wordResultList)

            stemStr = ''.join(stemSubsequence)
            resultDict[stemStr] = resultList

        return resultDict

    # END of class Stemplex----------------------------------------------------#



#!/usr/bin/python

# algorithmic approaches to identifying stems
# 2014-04-03
# Jackson Lee

import sys
import subprocess
import os
import time
from stemplex import *



###############
## Functions ##
###############


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

def sublist(L, indices):
    'takes a list L and outputs a sublist from L whose indices in L are specified'
    tempList = list()
    for i in indices:
        tempList.append(L[i])
    return tempList


#----------------------------------------------------------------#

def improvedSourceWord(sourceWord, bestIndexList):
    # to color-code the stem, prefix, infix, and suffix in the "improvedSourceWord"
    # in the surface word, the best stem characters are in black
    s = ''
    for (k,c) in enumerate(sourceWord):
        if k not in bestIndexList:
            # if c is an affix letter

            # check where c is
            # (on all stem letters' left-hand side? on the right? or sandwiched in-between?)
            stemLetterPreceding = False
            stemLetterFollowing = False
            for j in bestIndexList:
                if j < k:
                    stemLetterPreceding = True
                    break
            for j in bestIndexList:
                if j > k:
                    stemLetterFollowing = True
                    break

            if stemLetterPreceding and stemLetterFollowing:
                s += '{\\bf \\color{OliveGreen}' + c + '}'
            elif stemLetterPreceding:
                s += '{\\bf \\color{Blue}' + c + '}'
            elif stemLetterFollowing:
                s += '{\\bf \\color{Red}' + c + '}'
            else:
                s += '{\\bf \\color{RedOrange}' + c + '}'
        else:
            # if c is a stem letter
            s += '{\\bf\\underline{' + c + '}}'
    return s


#----------------------------------------------------------------#

def printLatexImprovedSourceWords(latexfile, sourceRow, improvedDictItems, stemType):
    for (k, (stem, indexTuplesMasterList)) in enumerate(improvedDictItems):

        # print 'substring' (or not)
        if k == 0:
            latexfile.write('%s & \n' % (stemType))
        else:
            latexfile.write(' & \n')

        # print stem
        latexfile.write('%s & \n' % (stem))

        # print improved word form
        for (e, indexTuplesList) in enumerate(indexTuplesMasterList):
            dboxbrString = ' \\\\ '.join([improvedSourceWord(sourceRow[e],indexTuple)
                                          for indexTuple in indexTuplesList])
            latexfile.write('\\dboxbr{' + dboxbrString + '}')
            if e == (len(indexTuplesMasterList)-1):
                latexfile.write(' \\\\ \n')
            else:
                latexfile.write(' & \n')
        latexfile.write('\\midrule \n')

#----------------------------------------------------------------#

######################
#### Main Program ####
######################

def main(inputfile=None, latexfilename=None, width='8.5', height='11'):

    logfilename = 'log-%s.txt' % (time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
    sys.stdout = open(logfilename, 'w')

    print '\nStemExtract\nBy Jackson Lee and John Goldsmith\n'
    print '\nCurrent local time: %s' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    # Data source

    if inputfile:
        fname = inputfile.name
    else:
        return

    fname_bare = fname.split('/')[-1] # fname without the full path info

    print '\nData file: %s' % (fname_bare)
    print 'Reading data file...'

    delimiter = ','
    source = [x.replace('\n','').replace('\r','').split(delimiter) for x in open(fname)]

    if not latexfilename:
        latexfilename = fname_bare[:-4] + '.tex'
    else:
        latexfilename = latexfilename + '.tex'

    ROWS = len(source)
    COLUMNS = len(source[0])-1

    print '\nData loaded'

    print '\nROWS:', ROWS
    print 'COLUMNS:', COLUMNS

    ################################################################################################

    # initialize all stemplexes

    print '\nInitializing stemplexes...'

    stemplexList = []

    for i in range(ROWS):
        StcxComplex = Stemplex(source[i], i, COLUMNS)
        StcxComplex.MyNodeIndex = i+ROWS
        stemplexList.append(StcxComplex)

    print 'All stemplexes initialized'

    ################################################################################################

    # write the latex preamble in "latexfile"

    print '\nInitializing LaTeX output file...'

    latexfile = open(latexfilename, 'w')

    latexfile.write('\\documentclass{article}\n')
    latexfile.write('\\usepackage{longtable}\n')
    latexfile.write('\\usepackage[letterpaper, margin=.3in, '
                    'paperwidth=%sin, paperheight=%sin]{geometry}\n' %
                    (width, height))
    latexfile.write('\\usepackage[usenames,dvipsnames]{color}\n')
    latexfile.write('\\usepackage{booktabs}\n\n')
    latexfile.write('\\usepackage{dashbox}\n\n')
    latexfile.write('\\usepackage{minibox}\n\n')
    latexfile.write('\\newcommand{\\dboxbr}[1]{\\framebox{\\minibox{#1}}}\n')
    latexfile.write('\\setlength{\\parindent}{0pt}\n\n')

    latexfile.write('\\begin{document}\n\n')
    latexfile.write('\\footnotesize\n\n')

    print 'LaTeX output file initialized'

    ################################################################################################

    # output stems and improved affixes, based on longest common subsequences

    print '\nPrinting stem identification results to LaTeX output file...'

    #latexfile.write('\\newpage\n\n')
    latexfile.write('results from StemExtract\n\n')
    latexfile.write('program created by Jackson Lee and John Goldsmith\\\\ \n\n')
    latexfile.write('Data file: %s\n\n' % fname_bare)
    latexfile.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n\n')


    for stmplx in stemplexList:

        # print paradigm's "leaf" in latex
        latexfile.write('\\bf{' + stmplx.MyLeaveList[0] + '}\n\n')

        latexfile.write('\\begin{longtable}[l]{l|c|%s}\n' % (' p{8em} ' * (COLUMNS)))

        latexfile.write('\\toprule [3pt]\n')
        stem = stmplx.stems()[0]
        sourceRow = stmplx.sourceRows()[0]

        improvedStemIndicesSubstring = stmplx.extractStemSubstring().items()
        improvedStemIndicesMultiset = stmplx.extractStemMultiset().items()
        improvedStemIndicesSubsequence = stmplx.extractStemSubsequence().items()

        # based on longest common substrings
        printLatexImprovedSourceWords(latexfile, sourceRow,
                                      improvedStemIndicesSubstring, 'substring')

        # based on largest common multisets
        printLatexImprovedSourceWords(latexfile, sourceRow,
                                      improvedStemIndicesMultiset, 'multiset')

        # based on longest common subsequences
        printLatexImprovedSourceWords(latexfile, sourceRow,
                                      improvedStemIndicesSubsequence, 'subsequence')

        latexfile.write('\\bottomrule  [3pt] \\\\ [10pt] \n')

        latexfile.write('\\end{longtable}\n\n')

    latexfile.write('\\end{document}\n')
    latexfile.close()

    print 'All done for printing stem identification results to LaTeX output file'

    ################################################################################################

    # produce .tex and .pdf

    print '\nCompiling output .pdf from .tex file\n'

    commands = ['latex','latex','dvipdf']

    sys.stdout.close()
    for command in commands:
        subprocess.call((command, latexfilename[:-4]), stdout=open(logfilename, 'a'))
    subprocess.call(('evince', latexfilename[:-4]+'.pdf'), stdout=open(logfilename, 'a'))
    sys.stdout = open(logfilename, 'a')

    print '\nOutput .pdf file produced!'

    print
    sys.stdout.close()

if __name__ == '__main__':
    main()


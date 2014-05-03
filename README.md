stem-extract
============

# What is this?

This is a Python program which takes morphological paradigms (from a .csv file) and identifies the stem for each paradigm based on three strategies: substrings, multisets, and subsequences. Paradigms are considered one at a time. A graphical user interface is provided.

There are three essential files of the program: stemGUI.pyw, stemExtract.py, and stemplex.py; these three files must be in the same directory. To run the program, execute stemGUI.pyw and the GUI will pop up. The program takes as the input a suitably prepared .csv file with morphological paradigms; see the sample .csv files on this GitHub repository.

# System requirements

## Python

Specifically, the program is written under Python 2.7.

## PyQt4

PyQt4 is needed to run the GUI. If you have not had PyQt4, be sure to get Python 2.7 first. To install PyQt4: http://www.riverbankcomputing.com/software/pyqt/download

If you are on Linux like Ubuntu, the easiest way to get PyQt4 on your machine is run the following (or whatever fits your Linux distribution) from the terminal:

    sudo apt-get install python-sip python-qt4

If you are on Windows, use a Windows `.exe` installer suitable for your operating system which is provided by the website just mentioned above.

# Input and output files

The input file is a tabulated form of morphological paradigms as a .csv file whose delimiter is the comma. There must be no quotes for any fields. The first column of the .csv is *not* treated as part of the paradigms; it is used as the identifier of the individuals (it can be the infinitival forms and/or the English translation, for instance). Sample .csv data files are provided in this repository.

The program outputs the results of stem extraction as a LaTeX .tex file and compiles it to generate a .pdf file. For this to work as described here, the assumption is that the commands "latex" (which takes a `.tex` file and generates the `.dvi`) and "dvipdf" (which converts `.dvi` into `.pdf`) are available and in the path. Otherwise, the program at least generates the `.tex` file, and you can convert the `.tex` into `.pdf` by other means.

# Conference presentations

- Lee, Jackson L. and John Goldsmith. 2014. “Complexity across morphological paradigms: A minimum description length approach to identifying inﬂectional stems”. MorphologyFest: Symposium on Morphological Complexity, Indiana University,
Bloomington. June 16-20, 2014.

- Lee, Jackson L. and John Goldsmith. 2014. “Algorithmic approaches to identifying inﬂectional stems: implications from Spanish”. Linguistic Symposium on Romance Languages, Western University, London, Ontario. May 2-4, 2014.

- Lee, Jackson L. and John Goldsmith. 2014. “Algorithmic approaches to identifying inﬂectional stems”. The 6th annual Illinois Language and Linguistics Society conference, University of Illinois at Urbana-Champaign. April 4-6, 2014.



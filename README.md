stem-extract
============

## What is this

This is a Python program which takes morphological paradigms (from a .csv file) and identifies the stem for each paradigm based on three strategies: substrings, multisets, and subsequences. Paradigms are considered one at a time. A graphical user interface is provided.

There are three essential files of the program: stemGUI.pyw, stemExtract.py, and stemplex.py; these three files must be in the same directory. To run the program, execute stemGUI.pyw and the GUI will pop up. The program takes as the input a suitably prepared .csv file with morphological paradigms; see the sample .csv files on this GitHub repository.

## System requirements

The program is written in Python 2.7 on Ubuntu 12.10, and the GUI is written in PyQt4. The Qt4 application development framework and the SIP bindings tool are therefore required.

## Input and output files

The input file is a tabulated form of morphological paradigms as a .csv file whose delimiter is the comma. There must be no quotes for any fields. The first column of the .csv is *not* treated as part of the paradigms; it is used as the identifier of the individuals (it can be the infinitival forms and/or the English translation, for instance). Sample .csv data files are provided in this repository.

The program outputs the results of stem extraction as a LaTeX .tex file and compiles it to generate a .pdf file.

## Conference presentations

- Lee, Jackson L. and John Goldsmith. 2014. “Complexity across morphological paradigms: A minimum description length approach to identifying inﬂectional stems”. MorphologyFest: Symposium on Morphological Complexity, Indiana University,
Bloomington. June 16-20, 2014.

- Lee, Jackson L. and John Goldsmith. 2014. “Algorithmic approaches to identifying inﬂectional stems: implications from Spanish”. Linguistic Symposium on Romance Languages, Western University, London, Ontario. May 2-4, 2014.

- Lee, Jackson L. and John Goldsmith. 2014. “Algorithmic approaches to identifying inﬂectional stems”. The 6th annual Illinois Language and Linguistics Society conference, University of Illinois at Urbana-Champaign. April 4-6, 2014.



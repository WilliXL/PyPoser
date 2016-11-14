import numpy as np
import pysynth as ps
import random

# high level algorithm knowledge and probabilities were taken from research from
# a Cornell research paper. I didn't use the code they had in their Github repo,
# mainly because they used multiple files, I wasn't sure how that works. I just
# used their high level logic and probability to implement my own code.

# Computoser - rule-based, probability-driven algorithmic music composition

def generateMusic(length,key,genre):
    probabilityType = [["unison",25],
                       ["octave",2],
                       ["step",48],
                       ["skip",25]]
                   
    probabilityInterval = [["perf5",25],
                           ["perf4",2],
                           ["third",48],
                           ["sixth",25]]
                       
    probabilityLength = [["sixteenth",10],
                         ["eighth",31],
                         ["quarter",40],
                         ["dottedQuarter",7],
                         ["half",9],
                         ["whole",3]]
                     
    meters = ["3/4","4/4","5/4","6/8"] # list of choosable meters
    meter = random.choice(meters) # selects a random meter to compose upon
    moods = ["major","minor"]
    mood = random.choice(moods)

    keyList = ["C","G","D","A","E","B","F#","C#","F","Bb","Eb","Ab","Db","Gb",
               "Cb"] # list of all of the keys

    def titleCreator(mood,key):
        happyNouns = ["Love","Yesterday","Piano","Heaven","Babe","Freedom",
            "Home","Weekend","Wonder","Night","Message","Heart,","Gold","Grace"]
        happyVerbs = ["Out","Imagine","Rising","Need","Love","Look","Falling",
            "Knocking","Bound","Take"]
        happyAdjectives = ["Happy","Lovely","Amazing"]
        title = ""
        # if (mood == "major"):
        #TBA

    def mainPartGenerator(mood,key,tempo,measures):
        pass

import numpy as np
import pysynth as ps
import random
import pyaudio
import wave
from pydub import AudioSegment
from tkinter import *
import copy

# high level algorithm knowledge and probabilities were taken from research from
# a Cornell research paper. I didn't use the code they had in their Github repo,
# mainly because they used multiple files, I wasn't sure how that works. I just
# used their high level logic and probability to implement my own code.

# Computoser - rule-based, probability-driven algorithmic music composition
# Link: https://www.academia.edu/9696759/Computoser_-_rule-based_probability-driven_algorithmic_music_composition

#Global Constants:
MinsPerSec = 1/60
Width = 1000
Height = 1000
totalLength = 20
# Musical Constants:
step = 1
Tonic = 0
SubTonic = -1
STDDominant = 4
JazzDominant = 5
ClassicalDominant = 4
Subdominant = 3
MelodyStartOctave = 4
MSO = MelodyStartOctave
HarmonyStartOctave = 3
HSO = HarmonyStartOctave
tempo = 100


# the two individual music lines that are separately generated and merged later
finalPieceMelody = []
finalPieceHarmony = []

keyList = ["C","G","D","A","E","B","F#","C#","F","Bb","Eb","Ab","Db","Gb","Cb"] 
# list of all of the keys
noteList = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"] # starts on "C"
#            0   1    2   3    4   5   6    7   8    9   10   11
# to be transformed later to match key
# list of all of the notes


def generateMusic(key,genre,mood): # totalLength: 15-30
    global finalPieceMelody
    global finalPieceHarmony
    global noteList
    finalPieceMelody = []
    finalPieceHarmony = []
    unisonLocations = []
    
    def expandProbability(probabilityTable):
        result = []
        for list in probabilityTable:
            result += ["%s" %(list[0])]*list[1]
        return result
        
        
    ##################################
    # Standard Pop Song Probabilities
    ##################################
    
    # data taken directly from the journal
    
    probabilityTypeSTD = [["unison",25], # playing an octave at the same time
                                         # coordinated with harmony
                          ["octave",2],  # stepping eight notes at once
                          ["step",48],   # stepping whole step
                          ["skip",25]]   # skip refers to an interval
                   
    probabilityIntervalSTD = [[4,25], # perfect fifth
                              [3,2],  # perfect fourth
                              [2,48], # third
                              [5,25]] # sixth
                       
    probabilityLengthSTD = [[16,10], 
                            [8,31],       
                            [4,40],      
                            [3,7], 
                            [2,9],        
                            [1,3]]       
                            
    
    #####################################
    # Jazz Song Probabilities
    #####################################
    
    # self-derived data based on my experiences with improv jazz/blues
    
    probabilityTypeJazz = [["unison",20],
                           ["octave",2],
                           ["step",60],
                           ["skip",18]]
    
    probabilityIntervalJazz = [[5,5],  # perfect fifth
                               [4,5],  # perfect fourth
                               [3,65], # third
                               [7,25]] # minor 7th
                               
    probabilityLengthJazz = [[12,40],
                             [6,40],
                             [8,15],
                             [4,5]]
                             
    
    ################################
    # Classical Song Probabilities
    ################################
    
    # self-derived data based on my experiences with classical music
    
    probabilityTypeClassical = [["unison",30],
                                ["octave",5],
                                ["step",45],
                                ["skip",20]]
    
    probabilityIntervalClassical = [[4,33],  # perfect fifth
                                    [3,12],  # perfect fourth
                                    [2,50],  # third
                                    [5,5]]   # sixth
                               
    probabilityLengthClassical = [[16,30], 
                                  [8,50],       
                                  [4,7],      
                                  [3,3], 
                                  [2,7],        
                                  [1,3]]  
    
    
    ################################
    # Replacement Probabilities
    ################################
    
    restProbability = [[1,5], # True
                       [0,95]] # False
    
    harmonyProbability = [[1,35], # True
                          [0,65]] # False
    
    
    ##############################
    # Randomly Assigned Variables
    ##############################
                     
    meters = ["2/4","3/4","4/4","5/4"] # list of choosable meters
    meter = random.choice(meters) # selects a random meter to compose upon
    
    
    #####################
    # Scale Creators
    #####################

    def makeJazzScale(noteList): # create jazz scale based on random
        list = [0,2,3,4,5,7,9,10,11]
        newList = []
        for note in list:
            newList.append(noteList[note])
        return newList
    
    def makeMajMinScale(noteList,mood): # takes current noteList and only leave
                                         # in necessary notes
        majorList = [0,2,4,5,7,9,11]
        minorList = [0,2,3,5,7,8,11]
        newList = []
        if (mood == "Major"):
            for note in majorList:
                newList.append(noteList[note])
        if (mood == "Minor"):
            for note in minorList:
                newList.append(noteList[note])
        return newList
    
    def scaleTransformer(noteList,key): # takes current noteList and starts it
                                        # from the given key's tonic note
        simplifiedList = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
        newList = noteList
        if (not key in simplifiedList):
            if (key == "Db"):
                key = "C"
            if (key == "Eb"):
                key = "D#"
            if (key == "Gb"):
                key = "F#"
            if (key == "Ab"):
                key = "G#"
            if (key == "Bb"):
                key = "A#"
        while (newList[0] != key):
            newList.append(newList.pop(0))
        return newList
        
    
    ###################
    # Genre Dispatcher
    ###################
    
    if (genre == "Standard"):
        probabilityType = probabilityTypeSTD
        probabilityInterval = probabilityIntervalSTD
        probabilityLength = probabilityLengthSTD
        noteList = scaleTransformer(noteList,key)
        scale = makeMajMinScale(noteList,mood)
        Dominant = STDDominant
    if (genre == "Jazz"):
        probabilityType = probabilityTypeJazz
        probabilityInterval = probabilityIntervalJazz
        probabilityLength = probabilityLengthJazz
        noteList = scaleTransformer(noteList,key)
        scale = makeJazzScale(noteList)
        Dominant = JazzDominant
    if (genre == "Classical"):
        probabilityType = probabilityTypeClassical
        probabilityInterval = probabilityIntervalClassical
        probabilityLength = probabilityLengthClassical
        noteList = scaleTransformer(noteList,key)
        scale = makeMajMinScale(noteList,mood)
        Dominant = ClassicalDominant
    
    #######################
    # Calculated Variables
    #######################

    def titleCreator(mood,key): # TBA
        happyNouns = ["Love","Yesterday","Piano","Heaven","Babe","Freedom",
            "Home","Weekend","Wonder","Night","Message","Heart,","Gold","Grace"]
        happyVerbs = ["Out","Imagine","Rising","Need","Love","Look","Falling",
            "Knocking","Bound","Take"]
        happyAdjectives = ["Happy","Lovely","Amazing"]
        title = ""
        # if (mood == "major"):
        #TBA
        
    def getMainMeasures(totalLength,tempo,meter):
        return int((tempo*MinsPerSec*totalLength/int(meter[0])))
        
    def getEndingMeasures(totalLength):
        return totalLength//8
    
    def getProbability(probabilityTable):
        probabilities = expandProbability(probabilityTable)
        return random.choice(probabilities)
    
    mainLength = getMainMeasures(totalLength,tempo,meter)
    endLength = getEndingMeasures(mainLength)
    mainLength = mainLength - endLength
    
    def melodyMainGenerator(mainLength):
        global finalPieceMelody
        skipOctave = False # checks if an octave is ever done
        octaveDirection = None # checks which direction it went in
        startingNotes = [noteList[0],noteList[Dominant]]
        # piece can either start on tonic or dominant
        startingNote = random.choice(startingNotes)
        startingLength = getProbability(probabilityLength)
        startingNote = ("%s%i" %(startingNote.lower(),MSO),int(startingLength))
        finalPieceMelody.append(startingNote)
        currNote = startingNote
        totalMeasures = 1/int(startingLength)
        
        ##### appendNotes #####
        def appendOctave(length):
            nonlocal skipOctave
            nonlocal octaveDirection
            nonlocal currNote
            nonlocal totalMeasures
            nonlocal mainLength
            if (skipOctave == False):
                directions = ["down","up"]
                direction = random.choice(directions)
                if (direction == "up"):
                    newNote = ("%s%i" %(currNote[0][:-1],
                        int(currNote[0][-1:])+1),length)
                    finalPieceMelody.append(newNote)
                    octaveDirection = "up"
                    currNote = newNote
                    totalMeasures += (1/length)
                elif (direction == "down"):
                    newNote = ("%s%i" %(currNote[0][:-1],
                        int(currNote[0][-1:])-1),length)
                    finalPieceMelody.append(newNote)
                    octaveDirection = "down"
                    currNote = newNote
                    totalMeasures += (1/length)
                skipOctave = True
            if (skipOctave == True):
                if (octaveDirection == "up"):
                    newNote = ("%s%i" %(currNote[0][:-1],
                            int(currNote[0][-1:])-1),length)
                    finalPieceMelody.append(newNote)
                    octaveDirection = None
                    currNote = newNote
                    totalMeasures += (1/length)
                if (octaveDirection == "down"):
                    newNote = ("%s%i" %(currNote[0][:-1],
                            int(currNote[0][-1:])+1),length)
                    finalPieceMelody.append(newNote)
                    octaveDirection = None
                    currNote = newNote
                    totalMeasures += (1/length)
                skipOctave = False
        
        def appendSkip(length):
            nonlocal skipOctave
            nonlocal octaveDirection
            nonlocal currNote
            nonlocal totalMeasures
            nonlocal mainLength
            if (skipOctave == False):
                directions = ["down","up"]
                direction = random.choice(directions)
                stepSize = int(getProbability(probabilityInterval))
                if (direction == "up"):
                    newNote = (("%s%i" %((noteList[(noteList.index(
                        currNote[0][0].upper()) + stepSize) %
                        len(noteList)]).lower(),MSO),length))
                    if (newNote[0][:-1].upper() in scale):
                        finalPieceMelody.append(newNote)
                        currNote = newNote
                        totalMeasures += (1/length)
                    else:
                        return False
                elif (direction == "down"):
                    newNote = (("%s%i" %((noteList[(noteList.index(
                        currNote[0][0].upper()) - stepSize) %
                        len(noteList)]).lower(),MSO),length))
                    if (newNote[0][:-1].upper() in scale):
                        finalPieceMelody.append(newNote)
                        currNote = newNote
                        totalMeasures += (1/length)
                    else:
                        return False
            if (skipOctave == True):
                if (octaveDirection == "up"):
                    stepSize = int(getProbability(probabilityInterval))
                    newNote = (("%s%i" %((noteList[(noteList.index(
                        currNote[0][0].upper()) - stepSize) %
                        len(noteList)]).lower(),MSO),length))
                    if (newNote[0][:-1].upper() in scale):
                        finalPieceMelody.append(newNote)
                        currNote = newNote
                        skipOctave = False
                        totalMeasures += (1/length)
                    else:
                        return False
                if (octaveDirection == "down"):
                    stepSize = int(getProbability(probabilityInterval))
                    newNote = (("%s%i" %((noteList[(noteList.index(
                        currNote[0][0].upper()) + stepSize) %
                        len(noteList)]).lower(),MSO),length))
                    if (newNote[0][:-1].upper() in scale):
                        finalPieceMelody.append(newNote)
                        currNote = newNote
                        skipOctave = False
                        totalMeasures += (1/length)
                    else:
                        return False
                        
        def appendStep(length):
            nonlocal skipOctave
            nonlocal octaveDirection
            nonlocal currNote
            nonlocal totalMeasures
            nonlocal mainLength
            if (skipOctave == False):
                directions = ["down","up"]
                direction = random.choice(directions)
                if (direction == "up"):
                    newNote = (("%s%i" %((noteList[(noteList.index(
                        currNote[0][0].upper()) + step) %
                        len(noteList)]).lower(),MSO),length))
                    if (newNote[0][:-1].upper() in scale):
                        finalPieceMelody.append(newNote)
                        currNote = newNote
                        totalMeasures += (1/length)
                    else:
                        return False
                elif (direction == "down"):
                    newNote = (("%s%i" %((noteList[(noteList.index(
                        currNote[0][0].upper()) - step) %
                        len(noteList)]).lower(),MSO),length))
                    if (newNote[0][:-1].upper() in scale):
                        finalPieceMelody.append(newNote)
                        currNote = newNote
                        totalMeasures += (1/length)
                    else:
                        return False
            if (skipOctave == True):
                if (octaveDirection == "up"):
                    newNote = (("%s%i" %((noteList[(noteList.index(
                        currNote[0][0].upper()) - step) %
                        len(noteList)]).lower(),MSO),length))
                    if (newNote[0][:-1].upper() in scale):
                        finalPieceMelody.append(newNote)
                        currNote = newNote
                        skipOctave = False
                        totalMeasures += (1/length)
                    else:
                        return False
                if (octaveDirection == "down"):
                    newNote = (("%s%i" %((noteList[(noteList.index(
                        currNote[0][0].upper()) + step) %
                        len(noteList)]).lower(),MSO),length))
                    if (newNote[0][:-1].upper() in scale):
                        finalPieceMelody.append(newNote)
                        currNote = newNote
                        skipOctave = False
                        totalMeasures += (1/length)
                    else:
                        return False
                        
        def appendUnison(length,noteType):
            nonlocal skipOctave
            nonlocal octaveDirection
            nonlocal currNote
            nonlocal totalMeasures
            nonlocal mainLength
            if (noteType == "skip"):
                returnValue = appendSkip(length)
                if (returnValue != False):
                    unisonLocations.append(len(finalPieceMelody))
                    appendSkip(length)
                    totalMeasures += (1/length)
                else:
                    return False
            if (noteType == "step"):
                returnValue = appendSkip(length)
                if (returnValue != False):
                    unisonLocations.append(len(finalPieceMelody))
                    appendStep(length)
                    totalMeasures += (1/length)
                else:
                    return False
                    
    
        while (totalMeasures < mainLength):
            if ((mainLength - totalMeasures) < 1):
                length = 1/(mainLength - totalMeasures)
            else:
                length = int(getProbability(probabilityLength))
            type = getProbability(probabilityType)
            if (type == "octave"):
                appendOctave(length)
            if (type == "skip"):
                returnValue = appendSkip(length)
                if (returnValue != False):
                    appendSkip(length)
            if (type == "step"):
                returnValue = appendStep(length)
                if (returnValue != False):
                    appendStep(length)
            if (type == "unison"):
                noteTypes = ["step","step","skip"]
                noteType = random.choice(noteTypes)
                returnValue = appendUnison(length,noteType)
                if (returnValue != False):
                    appendUnison(length,noteType)
    
    def melodyEndGenerator():
        global finalPieceMelody
        skipOctave = False # checks if an octave is ever done
        octaveDirection = None # checks which direction it went in
        endingNotes = ["%s%d" %(noteList[-1].lower(),3),
            "%s%d" %(noteList[0].lower(),4)] # subtonic, tonic
        finalPieceMelody[-2] = (endingNotes[0],finalPieceMelody[-2][1])
        finalPieceMelody[-1] = (endingNotes[-1],finalPieceMelody[-1][1])
        
        
    def harmonyMainGenerator(mainLength):
        global finalPieceHarmony
        removeLocations = []
        auxList = []
        
        def appendHarmony(note,length):
            interval = getProbability(probabilityInterval)
            newNote = (("%s%i" %((noteList[(noteList.index(
                        note.upper()) - int(interval)) %
                        len(noteList)]).lower(),HSO),length))
            finalPieceHarmony.append(newNote)
        
        def appendHarmonyUnison(location,noteRef,lengthRef):
            unison = ("%s%i" %(noteRef,HSO),lengthRef)
            finalPieceHarmony[location] = unison
                
        for note in range(len(finalPieceMelody)):
            noteReference = finalPieceMelody[note][0][:-1]
            lengthReference = finalPieceMelody[note][1]
            appendHarmony(noteReference,lengthReference)
        
        for note in unisonLocations:
            noteReference = finalPieceMelody[note][0][:-1]
            lengthReference = finalPieceMelody[note][1]
            appendHarmonyUnison(note,noteReference,lengthReference)
        
        for note in range(len(finalPieceHarmony)):
            if (not note in unisonLocations and note != 0):
                remove = getProbability(harmonyProbability)
                if (int(remove) == 1):
                    newLength = 1/(1/finalPieceHarmony[note-1][1] + 
                        1/finalPieceHarmony[note][1])
                    removeLocations.append(note)
                    finalPieceHarmony[note-1] = (finalPieceHarmony[note-1][0],
                        newLength)
        for note in range(len(finalPieceHarmony)):
            if (not note in removeLocations):
                auxList.append(finalPieceHarmony[note])
        finalPieceHarmony = auxList
        
           
    def melodyModifications(totalLength):
        for note in range(len(finalPieceMelody)):
            restProb = getProbability(restProbability)
            if (int(restProb) == 1):
                rest = ("r",finalPieceMelody[note][1])
                finalPieceMelody[note] = rest
        
        
    melodyMainGenerator(totalLength)
    harmonyMainGenerator(totalLength)
    melodyModifications(totalLength)
    melodyEndGenerator()
    
    
    

def playMusic(fileName): # plays wav file at specified location.
                         # code adapted from online forum
# Link: http://stackoverflow.com/questions/17657103/how-to-play-wav-file-in-python
# Yes, yes it's StackOverflow but it's just a simple, self-contained function
    chunk = 1024
    wf = wave.open('%s' %fileName, 'rb')
    p = pyaudio.PyAudio()
    
    stream = p.open(
        format = p.get_format_from_width(wf.getsampwidth()),
        channels = wf.getnchannels(),
        rate = wf.getframerate(),
        output = True)
    data = wf.readframes(chunk)

    while data != '':
        stream.write(data)
        data = wf.readframes(chunk)

    stream.close()
    p.terminate()
    wf.close()


# entire GUI was built with reference to this documentation:
# https://docs.python.org/3/library/tk.html

################################################################################

class PyPoserGUI:
    def __init__(self, parent):
        
        self.parent = parent
        parent.title("PyPoser!")
        
        self.mainFrame = Frame(root)
        self.leftFrame = Frame(self.mainFrame)
        self.middleFrame = Frame(self.mainFrame)
        self.rightFrame = Frame(self.mainFrame)
        
        self.space = Label(parent, text=" ")
        self.space.pack()
        
        self.desc = Label(parent, 
            text="A Probability-Driven Music Composer Written in Python")
        self.desc.pack(padx=20)
        
        self.space1 = Label(parent, text=" ")
        self.space1.pack()
        
        self.instr = Label(parent, text="Customize Parameters     OR     Enter a Title")
        self.instr.pack()
        
        self.pad = Label(parent, text=" ")
        self.pad.pack()
        self.pad2 = Label(parent, text=" ")
        self.pad2.pack()

        self.keys = StringVar(self.leftFrame)
        self.keys.set("C") # default key
        self.keyLabel = Label(self.leftFrame, text="Key")
        self.keyLabel.pack()
        self.key_button = OptionMenu(self.leftFrame, self.keys,"C","G","D","A","E",
            "B","F#","C#","F","Bb","Eb","Ab","Db","Gb","Cb")
        self.key_button.pack()
        
        self.genreLabel = Label(self.middleFrame, text="Genre")
        self.genreLabel.pack()
        self.genres = StringVar(self.middleFrame)
        self.genres.set("Jazz") # default genre
        self.genre_button = OptionMenu(self.middleFrame, self.genres, "Jazz",
            "Standard", "Classical")
        self.genre_button.pack()
        
        self.moodLabel = Label(self.rightFrame, text="Mood")
        self.moodLabel.pack()
        self.moods = StringVar(self.rightFrame)
        self.moods.set("Major") # default mood
        self.mood_button = OptionMenu(self.rightFrame, self.moods, "Major", "Minor")
        self.mood_button.pack()

        self.leftFrame.pack(side=LEFT)
        self.middleFrame.pack(side=LEFT)
        self.rightFrame.pack(side=LEFT)
        self.mainFrame.pack()
        
        self.space2 = Label(parent, text=" ")
        self.space2.pack()
        
        self.titleLabel = Label(parent, text="Enter Title[WIP]")
        self.titleLabel.pack()
        self.title = StringVar(parent)
        self.titleEntry = Entry(root, textvariable=self.title)
        self.titleEntry.pack()
        
        self.error = Label(parent, text="")
        self.error.pack()
        
        self.space3 = Label(parent, text=" ")
        self.space3.pack()
        self.space4 = Label(parent, text=" ")
        self.space4.pack()
        
        self.generate_button = Button(parent, text="Generate!", command=self.generateDispatcher)
        self.generate_button.pack()

        self.close_button = Button(parent, text="Quit", command=root.destroy)
        self.close_button.pack(side=RIGHT,padx=20,pady=20)
        
################################################################################
    
    def generateDispatcher(self):
        if (self.title.get().isalpha()):
            self.error.configure(text="")
            self.generateWithTitle()
        elif (self.title.get().isdigit()):
            self.error.configure(text="Enter Proper Word Ples",color="red")
        else:
            self.error.configure(text="")
            self.generateWithVariables()

    def generateWithVariables(self):
        generateMusic(self.keys.get(),self.genres.get(),self.moods.get())
        ps.make_wav(finalPieceMelody, fn="melody.wav")
        ps.make_wav(finalPieceHarmony, fn="harmony.wav")
        # combine melody and harmony together to make the final piece
        #################################################################
        ##### Borrowed from: http://stackoverflow.com/questions/4039158/mixing-two-audio-files-together-with-python #####
        sound1 = AudioSegment.from_file("melody.wav")
        sound2 = AudioSegment.from_file("harmony.wav")
        
        combined = sound1.overlay(sound2)
        
        combined.export("final.wav", format='wav')
        #################################################################
        playMusic("final.wav")

    def generateWithTitle(self):
        pass

root = Tk()
my_gui = PyPoserGUI(root)
root.mainloop()






















        

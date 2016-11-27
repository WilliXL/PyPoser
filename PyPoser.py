import numpy as np
import pysynth as ps
import random
import pyaudio
import wave
from pydub import AudioSegment

# high level algorithm knowledge and probabilities were taken from research from
# a Cornell research paper. I didn't use the code they had in their Github repo,
# mainly because they used multiple files, I wasn't sure how that works. I just
# used their high level logic and probability to implement my own code.

# Computoser - rule-based, probability-driven algorithmic music composition
# Link: https://www.academia.edu/9696759/Computoser_-_rule-based_probability-driven_algorithmic_music_composition


#Global Constants:
MinsPerSec = 1/60
# Musical Constants:
WholeStep = 2
Tonic = 0
SubTonic = -1
Dominant = 7
Subdominant = 5
MelodyStartOctave = 4
MSO = MelodyStartOctave
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


def generateMusic(totalLength,key,genre): # totalLength: 15-30
    global finalPieceMelody
    global noteList
    
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
                   
    probabilityIntervalSTD = [[7,25], # perfect fifth
                              [5,2],  # perfect fourth
                              [4,48], # third
                              [9,25]] # sixth
                       
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
    
    probabilityIntervalJazz = [[7,5],
                               [5,5],
                               [4,65],
                               [10,25]] # minor 7th
                               
    probabilityLengthJazz = [[12,40],
                             [6,40],
                             [8,15],
                             [4,5]]
    
    
    ##############################
    # Randomly Assigned Variables
    ##############################
                     
    meters = ["2/4","3/4","4/4","5/4"] # list of choosable meters
    meter = random.choice(meters) # selects a random meter to compose upon
    moods = ["major","minor"]
    mood = random.choice(moods) # either major or minor
    
    
    #####################
    # Scale Creators
    #####################

    def makeJazzScale(noteList): # create jazz scale based on random
        list = [0,2,3,4,5,7,9,10,11]
        newList = []
        for note in list:
            newList.append(noteList[note])
        return newList
    
    def makeMajMinScale(noteList,style): # takes current noteList and only leave
                                         # in necessary notes
        majorList = [0,2,4,5,7,9,11]
        minorList = [0,2,3,5,7,8,11]
        newList = []
        if (style == "major"):
            for note in majorList:
                newList.append(noteList[note])
        if (style == "minor"):
            for note in minorList:
                newList.append(noteList[note])
        return newList
    
    def scaleTransformer(noteList,key): # takes current noteList and starts it
                                        # from the given key's tonic note
        return noteList # TBA
    
    ###################
    # Genre Dispatcher TBA
    ###################
    if (genre == "Standard Pop"):
        probabilityType = probabilityTypeSTD
        probabilityInterval = probabilityIntervalSTD
        probabilityLength = probabilityLengthSTD
        noteList = scaleTransformer(noteList,key)
        scale = makeMajMinScale(noteList,mood)
    elif (genre == "Jazz"):
        probabilityType = probabilityTypeJazz
        probabilityInterval = probabilityIntervalJazz
        probabilityLength = probabilityLengthJazz
        noteList = scaleTransformer(noteList,key)
        scale = makeJazzScale(noteList)
        
    
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
    
    def melodyMainGenerator(mainLength,key,tempo,genre):
        global finalPieceMelody
        skipOctave = False # checks if an octave is ever done
        octaveDirection = None # checks which direction it went in
        # so the next note will go in the opposite direction to compensate
        startingNotes = [key,noteList[(noteList.index(key) + Dominant) % 
            len(noteList)]]
        # piece can either start on tonic or dominant
        startingNote = random.choice(startingNotes)
        startingLength = getProbability(probabilityLength)
        startingNote = ("%s%i" %(startingNote.lower(),MSO),int(startingLength))
        finalPieceMelody.append(startingNote)
        currNote = startingNote
        totalMeasures = 1/int(startingLength)
        
        ##### appendNoteMelody #####
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
                        currNote[0][0].upper()) + WholeStep) %
                        len(noteList)]).lower(),MSO),length))
                    if (newNote[0][:-1].upper() in scale):
                        finalPieceMelody.append(newNote)
                        currNote = newNote
                        totalMeasures += (1/length)
                    else:
                        return False
                elif (direction == "down"):
                    newNote = (("%s%i" %((noteList[(noteList.index(
                        currNote[0][0].upper()) - WholeStep) %
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
                        currNote[0][0].upper()) - WholeStep) %
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
                        currNote[0][0].upper()) + WholeStep) %
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
                    appendSkip(length)
                    #finalPieceMelody.append("u")
                    totalMeasures += (1/length)
                else:
                    return False
            if (noteType == "step"):
                returnValue = appendSkip(length)
                if (returnValue != False):
                    appendStep(length)
                    #finalPieceMelody.append("u")
                    totalMeasures += (1/length)
                else:
                    return False
                    
    
        while (totalMeasures < mainLength):
            type = getProbability(probabilityType)
            if ((mainLength - totalMeasures) < 1):
                length = int(1/(mainLength - totalMeasures))
                break
            else:
                length = int(getProbability(probabilityLength))
            if (type == "octave"):
                appendOctave(length)
            elif (type == "skip"):
                returnValue = appendSkip(length)
                if (returnValue != False):
                    appendSkip(length)
            elif (type == "step"):
                returnValue = appendStep(length)
                if (returnValue != False):
                    appendStep(length)
            elif (type == "unison"):
                noteTypes = ["step","step","skip"]
                noteType = random.choice(noteTypes)
                returnValue = appendUnison(length,noteType)
                if (returnValue != False):
                    appendUnison(length,noteType)
        

    def harmonyMainGenerator(mainLength,key,tempo,genre):
        pass
        
    return melodyMainGenerator(totalLength,key,tempo,genre)
    return harmonyMainGenerator(totalLength,key,tempo,genre)

generateMusic(20,"C","Jazz")

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
    

print (finalPieceMelody)

finalPieceHarmony = [('a#3',64),('a3',8),('g3',4)]

#print (finalPieceHarmony)

ps.make_wav(finalPieceMelody, fn="melody.wav")
#ps.make_wav(finalPieceHarmony, fn="harmony.wav")

# combine melody and harmony together to make the final piece
#################################################################
##### Borrowed from: http://stackoverflow.com/questions/4039158/mixing-two-audio-files-together-with-python #####
#sound1 = AudioSegment.from_file("melody.wav")
#sound2 = AudioSegment.from_file("harmony.wav")

#combined = sound1.overlay(sound2)

#combined.export("final.wav", format='wav')
#################################################################



playMusic("melody.wav")

import numpy as np
import pysynth as ps
import random
import pyaudio
import wave

# high level algorithm knowledge and probabilities were taken from research from
# a Cornell research paper. I didn't use the code they had in their Github repo,
# mainly because they used multiple files, I wasn't sure how that works. I just
# used their high level logic and probability to implement my own code.

# Computoser - rule-based, probability-driven algorithmic music composition


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


keyList = ["C","G","D","A","E","B","F#","C#","F","Bb","Eb","Ab","Db","Gb","Cb"] 
# list of all of the keys
noteList = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
# list of all of the notes

def generateMusic(length,key,tempo,genre): # length: 15-30, tempo: 70-140
    finalPieceMelody = []
    # data taken directly from the journal
    probabilityType = [["unison",25], # playing an octave at the same time
                                      # coordinated with harmony
                       ["octave",2],  # stepping eight notes at once
                       ["step",48],   # stepping whole step in either direction
                       ["skip",25]]   # skip refers to an interval
                   
    probabilityInterval = [[7,25], # perfect fifth
                           [5,2],  # perfect fourth
                           [4,48], # third
                           [9,25]] # sixth
                       
    probabilityLength = [[16,10], 
                         [8,31],       
                         [4,40],      
                         [3,7], 
                         [2,9],        
                         [1,3]]       
                         
    probabilityKey = [["G",73],
                      ["F",73],
                      ["C",68],
                      ["Am",56],
                      ["Dm",26],
                      ["Em",17],
                      ["E",10],
                      ["D",6],
                      ["Bb",2],
                      ["A",2]]
    
    def expandProbability(probabilityTable):
        result = []
        for list in probabilityTable:
            result += ["%s" %(list[0])]*list[1]
        return result
                     
    meters = ["2/4","3/4","4/4","5/4"] # list of choosable meters
    meter = random.choice(meters) # selects a random meter to compose upon
    moods = ["major","minor"]
    mood = random.choice(moods)

    def titleCreator(mood,key):
        happyNouns = ["Love","Yesterday","Piano","Heaven","Babe","Freedom",
            "Home","Weekend","Wonder","Night","Message","Heart,","Gold","Grace"]
        happyVerbs = ["Out","Imagine","Rising","Need","Love","Look","Falling",
            "Knocking","Bound","Take"]
        happyAdjectives = ["Happy","Lovely","Amazing"]
        title = ""
        # if (mood == "major"):
        #TBA
    def getMainMeasures(length,tempo,meter):
        return int((tempo*MinsPerSec*length/int(meter[0])))
    def getEndingMeasures(mainLength):
        return mainLength//8
    
    mainLength = getMainMeasures(length,tempo,meter)
    
    def getProbability(probabilityTable):
        probabilities = expandProbability(probabilityTable)
        return random.choice(probabilities)
    
    def mainPartGenerator(mainLength,key,tempo,genre):
        nonlocal finalPieceMelody
        skipOctave = False # checks if an octave is ever done
        octaveDirection = None # checks which direction it went in
        # so the next note will go in the opposite direction to compensate
        startingNotes = [key,noteList[(noteList.index(key) + Dominant) % 
            len(noteList)]]
        # piece can either start on tonic or dominant
        startingNote = random.choice(startingNotes)
        startingLength = getProbability(probabilityLength)
        finalPieceMelody.append(("%s%i" %(startingNote.lower(),MSO),
            int(startingLength)))
        currNote = ("%s%i" %(startingNote.lower(),MSO), int(startingLength))
        
        
        ###################
        # just for testing
        ###################
        iterations = 0
        def appendNote():
            nonlocal skipOctave
            nonlocal octaveDirection
            nonlocal currNote
            type = getProbability(probabilityType)
            length = int(getProbability(probabilityLength))
            if (skipOctave == False):
                if (type == "unison"):
                    print ('hi')
                if (type == "octave"):
                    directions = ["down","up"]
                    direction = random.choice(directions)
                    if (direction == "up"):
                        newNote = ("%s%i" %(currNote[0][:-1],
                            int(currNote[0][-1:])+1),length)
                        finalPieceMelody.append(newNote)
                        octaveDirection = "up"
                        currNote = newNote
                    elif (direction == "down"):
                        newNote = ("%s%i" %(currNote[0][:-1],
                            int(currNote[0][-1:])-1),length)
                        finalPieceMelody.append(newNote)
                        octaveDirection = "down"
                        currNote = newNote
                    skipOctave = True
                if (type == "skip"):
                    directions = ["down","up"]
                    direction = random.choice(directions)
                    stepSize = int(getProbability(probabilityInterval))
                    if (direction == "up"):
                        newNote = (("%s%i" %((noteList[(noteList.index(
                            currNote[0][0].upper()) + stepSize) %
                            len(noteList)]).lower(),MSO),length))
                        finalPieceMelody.append(newNote)
                        currNote = newNote
                    elif (direction == "down"):
                        newNote = (("%s%i" %((noteList[(noteList.index(
                            currNote[0][0].upper()) - stepSize) %
                            len(noteList)]).lower(),MSO),length))
                        finalPieceMelody.append(newNote)
                        currNote = newNote
                if (type == "step"):
                    directions = ["down","up"]
                    direction = random.choice(directions)
                    if (direction == "up"):
                        newNote = (("%s%i" %((noteList[(noteList.index(
                            currNote[0][0].upper()) + WholeStep) %
                            len(noteList)]).lower(),MSO),length))
                        finalPieceMelody.append(newNote)
                        currNote = newNote
                    elif (direction == "down"):
                        newNote = (("%s%i" %((noteList[(noteList.index(
                            currNote[0][0].upper()) - WholeStep) %
                            len(noteList)]).lower(),MSO),length))
                        finalPieceMelody.append(newNote)
                        currNote = newNote
            else:
                pass
            
        for iterations in range(50):
            appendNote()
            iterations += 1
            print (iterations)
        
        ps.make_wav(finalPieceMelody,fn="output.wav")
    return mainPartGenerator(20,key,100,"Lel")


def playMusic(fileName):
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
    
generateMusic(20,"F",100,"Lel")
playMusic("output.wav")
generateMusic(20,"F",100,"Lel")
























        

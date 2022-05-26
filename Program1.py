import sys
import re
import json

#Define "state"
class State:
    def __init__(self, name) -> None:
        self.name=name

#TODO: Read in cmd arguments
helpMode=False
verbose=False
definitions=""
fileCaptureMode=False
nondeterministic=False

for x in sys.argv:
    regexMatch=re.search("^(-h|--help)$",x)
    if(regexMatch):
        helpMode=True
    regexMatch=re.search("^(-v|--verbose)$",x)
    if(regexMatch):
        verbose=True
    regexMatch=re.search("^(-d=|--definitions=)(.*)$",x)
    if(regexMatch):
        definitions=regexMatch.group(2)
    regexMatch=re.search("^(-n|--nondeterministic)$",x)
    if(regexMatch):
        nondeterministic=True
    regexMatch=re.search("^(-d|--definitions)$",x)
    if(regexMatch):
        fileCaptureMode=True
    else:
        fileCaptureMode=False
    


#If running in help mode, print help instructions and quit.
if(helpMode):
    print('Deterministic Finite Automaton')
    print('Author: James Yakura')
    print('Usage: dfa *flags*')
    print('Executes a finite automaton on a string entered by the user. ')
    print('Flags:')
    print('-h --help \t\t\t Display usage hints.')
    print('-d=(file) --definitions=(file) \t\t\t Definitions file for the automaton.')
    print('-v --verbose \t\t\t Verbose mode; display internal program logic.')
    print('-n --nondeterministic \t\t\t Nondeterministic mode')
    #print('-p --pushdown \t\t\t Pushdown mode') #Not implemented yet!

else:
    states={}              #Dictionary <string, state>
    alphabet={}             #Dictionary <char, void>
    transition={}          #Dictionary <state, Dictionary <char, Array<state>>> (nondeterministic) or Dictionary<state, Dictionary <letter, state>> (deterministic)
    epsilonTransitions={}   #Dictionary <state, Array<state>> or Dictionary <state, state>
    startState=State('dummy')          #State
    acceptStates={}        #Dictionary <state, void>
    #Read in state machine
    if(verbose):
        print('Read file: '+definitions)    
    #Read in JSON file, using string placeholders for transitions
    defFile=open(definitions, "rt").read()
    defJson=json.loads(defFile)
    for x in defJson["alphabet"]:
        alphabet[x]=0
    for x in defJson["states"]:
        name=x["name"]
        state=State(name)
        states[name]=state
        if("transitions" in x):
            transition[state]=x["transitions"]
        if("epsilon" in x):
            epsilonTransitions[state]=x["epsilon"]
        if(x["start"]):
            startState=state
        if(x["accept"]):
            acceptStates[state]=0
    #Replace placeholder strings with states
    for x in transition:
        for y in transition[x]:
            if(nondeterministic):
                outputs=[]
                for z in transition[x][y]:
                    outputs.append(states[z])
                transition[x][y]=outputs
            else:
                transition[x][y]=states[transition[x][y]]
    for x in epsilonTransitions:
        if(nondeterministic):
            outputs=[]
            for y in epsilonTransitions[x]:
                outputs.append(states[y])
            epsilonTransitions[x]=outputs
        else:
            epsilonTransitions[x]=states[epsilonTransitions[x]]
    #Print definition if verbose.
    if(verbose):
        stateString="States:"
        for x in states:
            stateString+=" "+states[x].name
        alphabetString="Alphabet:"
        for x in alphabet:
            alphabetString+=" "+x
        acceptString="Final states:"
        for x in acceptStates:
            acceptString+=" "+x.name
        print(stateString)
        print(alphabetString)
        print("Start state: "+startState.name)
        print(acceptString)
        for x in transition:
            for y in transition[x]:
                if(nondeterministic):
                    for z in transition[x][y]:
                        print("Transition: "+x.name+" "+y+" "+z.name)
                else:
                    print("Transition: "+x.name+" "+y+" "+transition[x][y].name)
        for x in epsilonTransitions:
            if(nondeterministic):
                for y in epsilonTransitions[x]:
                    print("Transition: "+x.name+" epsilon "+y.name)
            else:
                print("Transition: "+x.name+" epsilon "+epsilonTransitions[x].name)
    #Main program loop
    while(True):
        inputString=input()
        #read in input string
        currentState=[]
        if(nondeterministic):
            currentState={startState: 0}
        else:
            currentState=startState
        if(verbose):
            print('Start state: ' + startState.name)
        for x in inputString:
            #Advance through input string. Update state machine.
            if(not x in alphabet):
                print('Invalid character: ' + x + '. Reject.')
                if(nondeterministic):
                    currentState={}
                else:
                    currentState=State("INVALID")
                break
            if(verbose):
                print('')
                print('Processing: '+x)
            if(nondeterministic):
                nextStates={}
                for y in currentState:
                    for z in transition[y][x]:
                        nextStates[z]=0
                        if(verbose):
                            print('Transition from '+ y.name + ' to ' +z.name)
                currentState=nextStates
                epsilonTransitioning=True
                while(epsilonTransitioning):
                    epsilonTransitioning=False
                    nextStates={}
                    for y in currentState:
                        if(y in epsilonTransitions):
                            for z in epsilonTransitions[y]:
                                if(not z in nextStates and not z in currentState):
                                    epsilonTransitioning=True
                                nextStates[z]=0
                                print('Epsilon transition from '+y.name+' to '+z.name)
                        else:
                            nextStates.append(y)
                    currentState=nextStates
            else:
                currentState=transition[currentState][x]
                if(verbose):
                    print('Next state: '+currentState.name)
                epsilonTransitioning=True
                while(epsilonTransitioning):
                    epsilonTransitioning=False
                    if(y in epsilonTransitions):
                        nextState=epsilonTransitions[y]
                        if(not nextState==currentState):
                            epsilonTransitions=True
                            currentState=nextState
                        print('Epsilon: next state:' + currentState.name)
        #Check for accept or reject.
        accept=False
        if(nondeterministic):
            for x in currentState:
                if(x in acceptStates):
                    accept=True
                    if(verbose):
                        print('Accept state: '+x.name)
        else:
            accept=(currentState in acceptStates)
            if(verbose and accept):
                print('Accept state: '+currentState.name)
        if(accept):
            print('ACCEPT')
        else:
            print('NOT ACCEPT')

from flask import Flask, jsonify, request, render_template, make_response
# from playsound import playsound
import winsound
import json, chess, chess.engine, os, random
import numpy as np
from chess.engine import Cp, Mate, MateGiven
app = Flask(__name__)



#load moves from file if necessary
with open("./moves.json") as f:
    moves = json.load(f)

GUARANTEED_MATE = 100000
HIGH_SCORE_THRESHOLD = 100
LOW_SCORE_THRESHOLD = 20

DEBUG = False
previousScore = 0
whiteBlunderCounter = 0
blackBlunderCounter = 0
captureCounter = 0
totalTime = 0


#controls go here
@app.route('/')
def index():
    return render_template('index.html')

#post requests get routed through the api
@app.route('/api', methods=['GET', 'POST', 'OPTIONS'])
def api_create_order():
    global moves, board, engine, previousScore
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
        
    #POST request
    elif request.method == 'POST':
        print('Incoming..')
        
        temp = []
        newMoves = []

        # if we have no moves on the board yet
        if(not moves):
            newMoves = request.get_json()
        else:
            # clear the board if our new data doesn't match our old data
            if(len(moves) <= len(request.get_json())):
                temp = request.get_json()[:len(moves)]
                newMoves = request.get_json()[len(moves):]

                #compare our new data with existing board state
                if(not np.array_equal(moves, temp)):
                    board.reset()
                    newMoves = request.get_json()
            else:
                board.reset()
                newMoves = request.get_json()

        moves = request.get_json()   

        print(newMoves)

        for move in newMoves:
            board.push_san(move)
           
        evaluatePosition()
        
        
        return _corsify_actual_response(jsonify(moves))

    else:
        return jsonify(moves)

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

def playRandomSound(folderName):
    winsound.PlaySound(fileFromDirectory("./sounds/" + folderName), winsound.SND_FILENAME)

def fileFromDirectory(folderPath):
    filePath = folderPath + '/' + random.choice(os.listdir(folderPath))
    print(filePath)
    return filePath

def chanceOfTrue(percent):
    num = random.randrange(100)
    if(num < percent):
        print(str(percent) + '% chance succeeded')
        return True
    print(str(percent) + '% chance failed')
    return False

def playSoundEffect(difference, relativeScore, previousScore, currentScore, isCheckmate, isStalemate, isEndByRepition, promotion, enPassant, castling, turnCounter, playerTurn, totalTime, blackTimeRemaining, whiteTimeRemaining, blackBlunderCounter, whiteBlunderCounter, checkCreated, pinCreated, forkCreated, captureCounter, whitePiecesRemaining, blackPiecesRemaining, isPieceRetreating, isCapture, pieceCaptured):
    

    isWinning = False
    if((currentScore > 0 and playerTurn) or (currentScore <= 0 and not playerTurn)):
        isWinning = True
    goodMove = relativeScore > 0 or (isWinning and currentScore > HIGH_SCORE_THRESHOLD and difference < HIGH_SCORE_THRESHOLD)

    if(DEBUG):
        print("good move: " + str(goodMove))
        print("is winning: " + str(isWinning))
        print("turn counter: " + str(turnCounter) + " | score difference: " + str(difference) + " | previous score: " + str(previousScore) + " | current score: " + str(currentScore) + " | relative score: " + str(relativeScore))
        print("stalemate: " + str(isStalemate) + " | checkmate: " + str(isCheckmate) + " | draw: " + str(isEndByRepition) + " | promotion: " + str(promotion) + " | is capture: " + str(isCapture) + " | en passant: " + str(enPassant) + " | is castling: " + str(castling))
        # print("elo difference: " + str(eloDifference))
        print("white's move: " + str(playerTurn) + " | white pieces remaining: " + str(whitePiecesRemaining) + " | black pieces remaining: " + str(blackPiecesRemaining) + " | black blunder counter: " + str(blackBlunderCounter) + " | white blunder counter: " + str(whiteBlunderCounter))
        print("total time: " + str(totalTime) + " | black time remaining: " + str(blackTimeRemaining) + " | white time remaining: " + str(whiteTimeRemaining))
        print("check created: " + str(checkCreated) + " | pin created: " + str(pinCreated) + " | fork created: " + str(forkCreated) + " | capture counter: " + str(captureCounter) + " | piece retreating?: " + str(isPieceRetreating))

    # Game ends
    if(isStalemate):
        print("draw: stalemate")
        playRandomSound("stalemate")
        return

    if(isEndByRepition):
        print("draw: repitition")
        playRandomSound("stalemate")
        return

    if(isCheckmate):
        print("checkmate")
        playRandomSound("checkmate")
        return

    # Unique moves (castling | en-passant | promote)
    if(castling):
        print("castling")
        playRandomSound("castling")
        return

    if(enPassant):
        print("en passant")
        playRandomSound("en-passant")
        return

    if(promotion):
        print("promotion")
        playRandomSound("promoted")
        return

    if(currentScore == GUARANTEED_MATE and previousScore != GUARANTEED_MATE):
        print("mate-in")
        playRandomSound("mate-in")
        return 

    # Check
    if(checkCreated):
        print("checked")
        playRandomSound("checked")
        return

    # Very early minor piece capture
    if(turnCounter < 4 and isCapture and pieceCaptured != chess.PAWN):
        print(pieceCaptured)
        print("very early capture")
        playRandomSound("very-early-capture")
        return

    # Early minor piece capture
    if(turnCounter < 20 and chanceOfTrue(30) and isCapture and pieceCaptured != chess.PAWN):
        print("early capture")
        playRandomSound("early-capture")
        return

    # No early captures
    if(turnCounter == 20 and whitePiecesRemaining+blackPiecesRemaining == 14):
        print("no early captures")
        playRandomSound("no-early-captures")
        return

    # Pins and Forks
    if(pinCreated):
        print("pin created")
        playRandomSound("pinned")
        return

    # Capture chain
    if(isCapture and captureCounter > 1 and chanceOfTrue(30)):
        playRandomSound("recapture")
        return

    # Attack start
    if(difference > HIGH_SCORE_THRESHOLD):
        
        if(isCapture):
            if(blackPiecesRemaining <= 3 and whitePiecesRemaining <= 3 and chanceOfTrue(15)):
                print(whitePiecesRemaining + " vs " + blackPiecesRemaining)
                playXvsYSound(whitePiecesRemaining, blackPiecesRemaining)
                return

            if(goodMove):
                print("great capture")
                playRandomSound("strong-capture")
                return
            else:
                if(chanceOfTrue(50)):
                    print("bad capture")
                    playRandomSound("blunder")
                    return
                else:
                    print("bad capture")
                    playRandomSound("not-very-effective")
                    return
        else:
            if(goodMove):
                print("great move")
                playRandomSound("super-effective")
                return
            else:
                print("bad move")
                playRandomSound("blunder")
                return
    
    if(difference < LOW_SCORE_THRESHOLD and isCapture and chanceOfTrue(30)):
        print("weak capture")
        playRandomSound("not-very-effective")
        return

    # Uninteresting turns go down here
    if(turnCounter < 20 and chanceOfTrue(10)):
        print("early move")
        playRandomSound("early-move")
        return

    # Position upgraded
    if(relativeScore > LOW_SCORE_THRESHOLD and chanceOfTrue(10)):
        print("improving position")
        playRandomSound("stats-up")
        return
    elif(chanceOfTrue(10)):
        print("neutral move")
        playRandomSound("neutral-position")
        return

def playXvsYSound(x, y):
    if((x == 1 and y == 0) or (x == 0 and y == 1)):
        playRandomSound("pieces-remaining/1vs0")
        return
    if(x == 1 and y == 1):
        playRandomSound("pieces-remaining/1vs1")
        return
    if((x == 1 and y == 2) or (x == 2 and y == 1)):
        playRandomSound("pieces-remaining/1vs2")
        return
    if((x == 1 and y == 3) or (x == 3 and y == 1)):
        playRandomSound("pieces-remaining/1vs3")
        return
    if(x == 2 and y == 2):
        playRandomSound("pieces-remaining/2vs2")
        return
    if((x == 2 and y == 3) or (x == 3 and y == 2)):
        playRandomSound("pieces-remaining/2vs3")
        return

def evaluatePosition():
    global moves, board, engine, previousScore, blackBlunderCounter, whiteBlunderCounter, totalTime, captureCounter

    info = engine.analyse(board, chess.engine.Limit(depth=20))

    whitePiecesRemaining = 0
    blackPiecesRemaining = 0

    for square in board.piece_map():
        piece = board.piece_at(square)
        if(piece.piece_type != chess.PAWN and piece.piece_type != chess.KING):
            if(board.piece_at(square).color == chess.WHITE):
                whitePiecesRemaining += 1
            else:
                blackPiecesRemaining += 1

    checkCreated = board.is_check()
    lastMove = board.pop()

    score = 0
    # set variables here
    try:
        score = int(info["score"].pov(chess.WHITE).__str__())
    except:
        #TODO: figure out what to do with mate
        score = GUARANTEED_MATE
    
    isCheckmate = board.is_checkmate()
    isStalemate = board.is_stalemate()
    isEndByRepitition = board.is_fivefold_repetition()
    promotion = False
    if(lastMove.promotion != None):
        promotion = True
    enPassant = board.is_en_passant(lastMove)
    castling = board.is_castling(lastMove)
    turnCounter = len(board.move_stack)
    playerTurn = board.color_at(lastMove.from_square)
    blackTimeRemaining = 1000
    whiteTimeRemaining = 800
    
    #TODO: set these
    pinCreated = False
    forkCreated = False
    # if():
    #     forkCreated = True

    isCapture = False
    if(board.is_capture(lastMove)):
        isCapture = True
        captureCounter += 1
    else:
        captureCounter = 0

    # get the piece formerly at the new location for our piece | should return none if it's not a capture

    pieceCaptured = board.piece_at(lastMove.to_square)

    if(pieceCaptured):
        pieceCaptured = pieceCaptured.piece_type
    
    isPieceRetreating = False
    # if():
    #     isPieceRetreating = True


    # get the change in score relative to the current player
    relativeScore = score-previousScore
    if(not playerTurn):
        relativeScore *= -1
    difference = abs(relativeScore)

    # if it's a blunder
    if(relativeScore < (-1 * HIGH_SCORE_THRESHOLD)):
        if(playerTurn):
            whiteBlunderCounter += 1
        else:
            blackBlunderCounter += 1

    playSoundEffect(difference, relativeScore, previousScore, score, isCheckmate, isStalemate, isEndByRepitition, promotion, enPassant, castling, turnCounter, playerTurn, totalTime, blackTimeRemaining, whiteTimeRemaining, blackBlunderCounter, whiteBlunderCounter, checkCreated, pinCreated, forkCreated, captureCounter, whitePiecesRemaining, blackPiecesRemaining, isPieceRetreating, isCapture, pieceCaptured)
    previousScore = score
    board.push(lastMove)
    return score

if __name__ == "__main__":
    board = chess.Board()
    engine = chess.engine.SimpleEngine.popen_uci("D:/Projects/Chess Stadium/usr/bin/stockfish_20090216_x64_modern")
    app.run(debug=True)
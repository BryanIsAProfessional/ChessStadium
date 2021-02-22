//import init from './initialize';
const NOT_FOUND = Number.MAX_SAFE_INTEGER;
const POINT_FLUCTUATION_THRESHOLD = .01;
const POLL_RATE_MILLIS = 200;
const POLL_RATE_MILLIS_LONG = 3000;

async function startJQuery(){
    var script = document.createElement('script');
    script.src = "https://ajax.googleapis.com/ajax/libs/jquery/1.6.3/jquery.min.js";
    document.getElementsByTagName('head')[0].appendChild(script);
    return;
}

// function setMoveContainer(){
//     ret = $($($('#analysis-vml-scroll-container').context.querySelector(".move-list-component").firstChild)[0])
//     return ret
// }

function setMoveContainer(){
    ret = $(".game-controls-wrapper")
    console.log(ret)
    return ret
}

function setListener(){
    return $('#analysis-vml-scroll-container');
}

// set an observer to listen for changes
function startObserver(){
    //var node = document.querySelectorAll('.move-list-component')[0];
    var node = document.querySelectorAll('.game-controls-wrapper')[0];
    
    if(!node) {
        //The node we need does not exist yet.
        //Wait 500ms and try again
        window.setTimeout(startObserver,POLL_RATE_MILLIS);
        return;
    }

    var observer = new MutationObserver(callback);

    var config = {
        attributes: true,
        childList: true,
        characterData: true,
        subtree: true
    };

    console.log("Starting observer");
    observer.observe(node, config);
}

// read all moves
function getAllMoves(){
    let ret = [];

    try{
        moveContainer = setMoveContainer();
        if(!moveContainer){
            window.setTimeout(getAllMoves(),500);
            return ret;
        }else{
            try{
                holder = moveContainer[0].querySelectorAll(".vertical-move-list-column")
                $(holder).each(function() {
    
                    if(this.className !== "variation main"){
                        }
                        move = $( this.lastElementChild ).text().trim()
                        if(!move.includes('.') && !(move === "")){
                            ret.push(move);
                        }
                        
                    }
                );
            }catch(e){
                console.log(e);
            }
        }
    }catch(e){
        console.log(e)
    }
    return ret;
}

// read most recent move
function getLastMove(){
    moveContainer = setMoveContainer();
    if(!moveContainer){
        window.setTimeout(getLastMove,POLL_RATE_MILLIS);
        return "";
    }else{
        pieceType = $(moveContainer[0].lastElementChild.lastElementChild.lastElementChild.lastElementChild).attr("data-figurine");
        if(pieceType === undefined){
            pieceType = "";
        }
        move = moveContainer[0].lastElementChild.lastElementChild.lastChild.textContent;
        console.log("Piece type: " + pieceType + ", Move: " + move)
        return pieceType + move;
    }
}

function sendData(data){
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://127.0.0.1:5000/api", true);
    xhr.setRequestHeader('Content-type', 'application/json');
    console.log("sending data: " + JSON.stringify(data))
    xhr.send(JSON.stringify(data));
}

function arraysEqual(lhs, rhs){
    if(lhs === rhs){
        return true;
    }
    if(lhs == null || rhs == null){return false;}
    if(lhs.length != rhs.length){return false;}

    for(var i = 0; i < lhs.length; i++){
        if(lhs[i] != rhs[i]){
            return false;
        }
    }
    return true;
}

const callback = function(){
    currentMoves = getAllMoves()

    if(!arraysEqual(moves, currentMoves)){
        sendData(getAllMoves());
        moves = currentMoves;
    }
}

// initialize and start listening/updating
let listenerContainer = null;
let moveContainer = null;
let moves = [];

// await startJQuery()
//     .then(startObserver(callback))

startObserver(callback)
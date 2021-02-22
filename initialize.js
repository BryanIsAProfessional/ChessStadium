async function startJQuery(){
    var script = document.createElement('script');
    script.src = "https://ajax.googleapis.com/ajax/libs/jquery/1.6.3/jquery.min.js";
    document.getElementsByTagName('head')[0].appendChild(script);
}

function setMoveContainer(){
    return $($($('#analysis-vml-scroll-container').context.querySelector(".move-list-component").firstChild)[0]);
}

function setListener(){
    return $('#analysis-vml-scroll-container');
}

// read all moves
function getAllMoves(){
    let ret = [];
    if(moveContainer != null){
        try{
            $(moveContainer[0].children).each(function() {
                if(this.className !== "variation main"){
                    ret.push($( this.lastChild ).text());
                }
            });
        }catch(e){
            console.log(e);
        }
    }    
    return ret;
}

// read most recent move
function getLastMove(){
    if(moveContainer != null){
        return moveContainer[0].lastElementChild.lastChild.textContent;
    }
    return "";
}
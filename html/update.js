var websocket = new WebSocket('ws://'+window.location.hostname+':9999');

const forward = document.getElementById("forward")
const reverse = document.getElementById("reverse")
const left = document.getElementById("left")
const right = document.getElementById("right")
const rleft = document.getElementById("rleft")
const rright = document.getElementById("rright")
let timer;

forward.onpointerdown = function(){
    timer = setInterval(function(){websocket.send("forward")}, 100);
}

forward.onpointerup = function(){
    clearInterval(timer)
}

reverse.onpointerdown = function(){
    timer = setInterval(function(){websocket.send("reverse")}, 100);
}

reverse.onpointerup = function(){
    clearInterval(timer)
}

left.onpointerdown = function(){
    timer = setInterval(function(){websocket.send("left")}, 100);
}

left.onpointerup = function(){
    clearInterval(timer)
}

right.onpointerdown = function(){
    timer = setInterval(function(){websocket.send("right")}, 100);
}

right.onpointerup = function(){
    clearInterval(timer)
}

rleft.onpointerdown = function(){
    timer = setInterval(function(){websocket.send("rleft")}, 100);
}

rleft.onpointerup = function(){
    clearInterval(timer)
}

rright.onpointerdown = function(){
    timer = setInterval(function(){websocket.send("rright")}, 100);
}

rright.onpointerup = function(){
    clearInterval(timer)
}

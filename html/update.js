var websocket = new WebSocket('ws://'+window.location.hostname+':9999');

websocket.onmessage = function(message){
    console.log(message);
    const data = JSON.parse(message.data)
    for (let key in data){
        try{
            if (key == "image"){
                document.getElementById("view").src = "images/" + data[key] + ".jpg?" + Date.now();
            } else {
                document.getElementById(key).innerHTML = key+" "+data[key];
            }
        }
        catch (TypeError) {}
    }
};

const forward = document.getElementById("forward")
const reverse = document.getElementById("reverse")
const left = document.getElementById("left")
const right = document.getElementById("right")
const rleft = document.getElementById("rleft")
const rright = document.getElementById("rright")
const camera = document.getElementById("camera")
let timer;

function sendpos(event){
    img = document.getElementById("view");
    let x = event.offsetX/img.clientWidth;
    let y = event.offsetY/img.clientHeight;
    websocket.send(JSON.stringify([x,1-y]))
}

camera.onclick = function(){
    websocket.send("pitch "+document.getElementById("pitch").value)
    websocket.send("yaw "+document.getElementById("yaw").value)
}

forward.onpointerdown = function(){
    clearInterval(timer)
    timer = setInterval(function(){websocket.send("forward")}, 100);
}

forward.onpointerup = function(){
    clearInterval(timer)
}

reverse.onpointerdown = function(){
    clearInterval(timer)
    timer = setInterval(function(){websocket.send("reverse")}, 100);
}

reverse.onpointerup = function(){
    clearInterval(timer)
}

left.onpointerdown = function(){
    clearInterval(timer)
    timer = setInterval(function(){websocket.send("left")}, 100);
}

left.onpointerup = function(){
    clearInterval(timer)
}

right.onpointerdown = function(){
    clearInterval(timer)
    timer = setInterval(function(){websocket.send("right")}, 100);
}

right.onpointerup = function(){
    clearInterval(timer)
}

rleft.onpointerdown = function(){
    clearInterval(timer)
    timer = setInterval(function(){websocket.send("rleft")}, 100);
}

rleft.onpointerup = function(){
    clearInterval(timer)
}

rright.onpointerdown = function(){
    clearInterval(timer)
    timer = setInterval(function(){websocket.send("rright")}, 100);
}

rright.onpointerup = function(){
    clearInterval(timer)
}

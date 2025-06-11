const server_url = window.location.href

var host_url = new URL(server_url)
host_url = host_url.hostname

var username = ""

var times = 1

const websocket_url = "ws://" + host_url +":8001"
console.log(websocket_url)

const socket = new WebSocket(websocket_url);

socket.addEventListener('open', function (data) {
    console.log("Websocket connection open")
});

socket.addEventListener("message", function (data) {                        // listen for messages

    var packet_json = JSON.parse(data["data"])
    
    
    if (packet_json["type"] == "msg_update") {
        
        console.log(packet_json)


            var username = packet_json["username"]
            
            document.getElementById("messages").textContent += username + ": " + packet_json["msg"] + "\n"
    }
    if (packet_json["type"] == "msg_send") {
        
        document.getElementById("messages").textContent = ""
        var messages = packet_json["msg"]

        for (let i in packet_json["msg"]) {

            var current_message = messages[i]
            var username = current_message["username"]
            

            document.getElementById("messages").textContent += username + ": " + current_message["msg"] + "\n"
        } 
    }
    
})

function send() {                                                      //send
    
    if (username == "" || username == null) {
        username = prompt("Enter your username:")
        if (username == "" || username == null){
            document.getElementById("messages").innerHTML += "<b>Please select a username</b><br>"
            return 0
        }
        send()
    }

    if (document.getElementById('input-field').value == "") {
        return 0
    }

    var packet = {
        "type"    : "msg_send",
        "msg"     : document.getElementById('input-field').value,
        "username": username
    }

    socket.send(JSON.stringify(packet))
    document.getElementById("input-field").value = ""

}
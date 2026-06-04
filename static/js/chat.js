const socket = io();

const room_id = document.getElementById('room_id').getAttribute('room_id');

socket.emit('join', {
    'room_id': room_id
})

document.getElementById('send-message').addEventListener('click', function(){
    console.log('are you actually being clicked??')
    const input_element = document.getElementById('message_input') 
    const message_content = input_element.value;
    socket.emit('send_message', {
        'room_id': room_id,
        'message': message_content
    });
    input_element.value = '';
});

socket.on('receive_message', function(data){
    const chatWindow = document.getElementById('chat-window')
    newMessageElement = document.createElement('p')
    newMessageElement.innerHTML = `<strong>${data.username}:</strong> ${data.message}`;
    chatWindow.appendChild(newMessageElement);

    chatWindow.scrollTop = chatWindow.scrollHeight;
});
const socket = io();
let typingTimer;
let isTyping = false;
const my_userid = document.getElementById('current-userid').getAttribute('current_userid')

const room_id = document.getElementById('room_id').getAttribute('room_id');

socket.emit('join', {
    'room_id': room_id
})

document.getElementById('send-message').addEventListener('click', function(){
    console.log('are you actually being clicked??')
    const input_element = document.getElementById('message-input') 
    const message_content = input_element.value;
    socket.emit('send_message', {
        'room_id': room_id,
        'message': message_content,
    });
    input_element.value = '';
});

document.getElementById('message-input').addEventListener('input', function(){
    const room_name = document.getElementById('room-name').getAttribute('room_name')
    const room_id = document.getElementById('room-id').getAttribute('room_id')

    if (!isTyping){
        isTyping = true;
        socket.emit('typing_started', {
            'room_name': room_name,
            'room_id': room_id,
        })
    }
    clearTimeout(typingTimer)

    typingTimer = setTimeout(function(){
        socket.emit('typing_ended', {
            'room_name': room_name,
            'room_id': room_id
        })
        isTyping = false;
    }, 2200)
    
})

document.getElementById('invite-user-submitbutton').addEventListener('click', function(e){
    e.preventDefault();
    const room_name = document.getElementById('room-name').getAttribute('room_name')
    const invited_username = document.getElementById('invited-username').value;
    const room_id = document.getElementById('room-id').getAttribute('room_id')
    console.log(room_name, invited_username, room_id)
    socket.emit('send_invite', {
        'room_name': room_name,
        'room_id': room_id,
        'invited_username': invited_username
    })
    const modal = e.target.closest('dialog')
    if (modal){
        modal.close()
    }
})

socket.on('receive_message', function(data){
    const chatWindow = document.getElementById('chat-window')
    newMessageElement = document.createElement('p')
    newMessageElement.innerHTML = `<strong>${data.username}:</strong> ${data.message}`;
    chatWindow.appendChild(newMessageElement);

    chatWindow.scrollTop = chatWindow.scrollHeight;
});

socket.on('update_typing_indicator', function(data){
    const typing_indicator = document.getElementById('typing-indicator')
    if (data['status'] == 'started' && data['user_id'] != my_userid){
        typing_indicator.innerHTML = `${data['username']} is typing...`
    }
    else if (data['status'] == 'ended'){
        typing_indicator.innerHTML = ''
    }
    
})
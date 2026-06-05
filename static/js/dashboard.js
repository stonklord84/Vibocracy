const socket = io();

const username = document.getElementById('current_username').getAttribute('username')

socket.emit('join_dashboard', {
    'username': username
})

socket.on('receive_invite', (data)=>{
    const room_list = document.getElementById('room-list')
    new_pending_invite = document.createElement('li')
    new_pending_invite.classList.add('grid-item') 
    room_list.appendChild(new_pending_invite)
})
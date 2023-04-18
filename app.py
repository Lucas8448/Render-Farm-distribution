import docker
from flask import *
from flask_socketio import SocketIO, emit

# Create a docker client
client = docker.from_env()

# Create a Flask client
app = Flask(__name__)
socketio = SocketIO(app)

# Store mapping between WebSocket session IDs and Docker containers
containers = {}


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def ws_connect():
    print('WebSocket connected')
    container = client.containers.run(
        "ubuntu", detach=True, command="tail -f /dev/null")
    session_id = request.sid
    containers[session_id] = container
    print(f'Started container: {container.id} for session: {session_id}')


@socketio.on('disconnect')
def ws_disconnect():
    print('WebSocket disconnected')
    session_id = request.sid
    if session_id in containers:
        container = containers[session_id]
        container.stop()
        container.remove()
        del containers[session_id]
        print(
            f'Stopped and removed container: {container.id} for session: {session_id}')
    else:
        print(f'No container found for session: {session_id}')


if __name__ == '__main__':
    socketio.run(app)

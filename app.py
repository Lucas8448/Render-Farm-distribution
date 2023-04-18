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


@socketio.on('start_container')
def start_container(data):
    image = data['image']
    print(f'Request to start {image} container')
    if image not in ['debian', 'bash', 'ubuntu']:
        print(f'Invalid container image: {image}')
        return

    session_id = request.sid
    if session_id in containers:
        print(f'Container already running for session: {session_id}')
        return

    container = client.containers.run(
        image, detach=True, command="tail -f /dev/null")
    containers[session_id] = container
    print(
        f'Started {image} container: {container.id} for session: {session_id}')


@socketio.on('stop_container')
def stop_container():
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

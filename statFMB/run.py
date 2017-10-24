from statFMB.views import app, socketio

#NOTE: change the comments in order change hosts
def main():
    socketio.run(app)
    #socketio.run(app, host='0.0.0.0', port='80')

if __name__ == "__main__":
    socketio.run(app)
    #socketio.run(app, host='0.0.0.0', port='80')

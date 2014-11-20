import chatbot

if __name__ == '__main__':
    try:
        ws = chatbot.Chatbot('ws://sim.smogon.com:8000/showdown/websocket',
                             protocols=['http-only', 'chat'])
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()

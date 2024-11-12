'''
Bronnen:
https://flask.palletsprojects.com/en/stable/
Microsoft Copilot. (2024, November 11)

'''
from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

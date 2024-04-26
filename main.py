from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
import requests
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
isAuthorized = False

connection = sqlite3.connect('userData.db', check_same_thread=False)
cursor = connection.cursor()


@app.route('/', methods=['POST', 'GET'])
def index():
    global isAuthorized
    print(request.range)
    if request.method == 'POST':
        if list(request.form)[0] == 'LoginButton':
            return redirect(
                'https://discord.com/oauth2/authorize?client_id=779423124873019392&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A8080&scope=identify+guilds')
        if list(request.form)[0] == 'addToServer':
            return redirect('https://discord.com/oauth2/authorize?client_id=779423124873019392')
    if 'code' in request.args and not isAuthorized:
        code = request.args['code']
        userData = get_access_token(code)
        avatar_url = f'https://cdn.discordapp.com/avatars/{userData['user']['id']}/{userData['user']['avatar']}.png?size=300'
        userName = userData['user']['username']
        cursor.execute(f'INSERT INTO userData VALUES("{userName}","{avatar_url}")')
        connection.commit()
        isAuthorized = True
    if isAuthorized:
        avatar_url = cursor.execute('SELECT avatar_url FROM userData').fetchone()[0]
        userName = cursor.execute('SELECT userName FROM userData').fetchone()[0]
        return render_template('LoginnedPage.html', avatar_url=avatar_url, userName=userName)
    return render_template('index.html')


def get_access_token(code):
    API_ENDPOINT = 'https://discord.com/api/oauth2/token'
    CLIENT_ID = '779423124873019392'
    CLIENT_SECRET = 'NAaGGRI0uqrnJz84Yk7GeZOESDoj2wsQ'
    REDIRECT_URI = 'http://localhost:8080'
    code = code
    data = {
        'grant_type': 'authorization_code',
        "code": code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.post('https://discord.com/api/oauth2/token', headers=headers, data=data,
                      auth=(CLIENT_ID, CLIENT_SECRET))
    return get_user_data(r.json())


def get_user_data(data):
    CLIENT_ID = '779423124873019392'
    CLIENT_SECRET = 'NAaGGRI0uqrnJz84Yk7GeZOESDoj2wsQ'
    REDIRECT_URI = 'http://localhost:8080'
    data = data
    headers = {'Authorization': f'Bearer {data["access_token"]}'}

    r = requests.get('https://discord.com/api/v10/oauth2/@me', headers=headers)

    return r.json()


if __name__ == '__main__':
    app.run(port=8080, host='localhost')
    cursor.execute("DELETE FROM userData")
    connection.commit()

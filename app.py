from flask import Flask, redirect, render_template, request
import mysql.connector
import configparser
import uuid
import re

def isValidURL(str):
    
    regex = ("((http|https)://)(www.)?" +
             "[a-zA-Z0-9@:%._\\+~#?&//=]" +
             "{2,256}\\.[a-z]" +
             "{2,6}\\b([-a-zA-Z0-9@:%" +
             "._\\+~#?&//=]*)")

    p = re.compile(regex)
 
    if (str == None):
        return False
    
    if(re.search(p, str)):
        return True
    else:
        return False
    
config = configparser.ConfigParser()

config.read('config.secret')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', url=config['MISC']['URL'], title=config['MISC']['TITLE']), 200

@app.route('/<string>')
def route(string: str):

    cnx = mysql.connector.connect(
    user=config['MYSQL']['USERNAME'], 
    password=config['MYSQL']['PASSWORD'],
    host=config['MYSQL']['HOST'],
    database=config['MYSQL']['DATABASE']
    )

    uid = string

    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            
            query = ("SELECT long_url FROM `pairs` " f"WHERE short_url = \"{uid}\"")
            
            cursor.execute(query)

            result = cursor.fetchall()

            cursor.close()
            cnx.close()

            if result == None:
                return redirect(config['MISC']['URL'])
            else:
                return redirect(result[0][0])

    return redirect(config['MISC']['URL'])

@app.route('/api/generate', methods=['POST'])
def api_generate():

    cnx = mysql.connector.connect(
    user=config['MYSQL']['USERNAME'], 
    password=config['MYSQL']['PASSWORD'],
    host=config['MYSQL']['HOST'],
    database=config['MYSQL']['DATABASE']
    )

    url = request.json['url']

    if isValidURL(url) == False:
        return 'invalid url', 403
    
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:

            uid = str(uuid.uuid4())[:5]

            query = ("SELECT * from `pairs` ")

            cursor.execute(query)

            results = cursor.fetchall()

            for result in results:
                if result[0] == url:
                    return f'{config['MISC']['URL']}/{result[1]}', 200
                if result[1] == uid:
                    uid = str(uuid.uuid4())[:5]

            add_pair = ("INSERT INTO pairs " "(long_url, short_url) " "VALUES (%s, %s)")
            data_pair = (url, uid)

            cursor.execute(add_pair, data_pair)

            cnx.commit()
            
            cursor.close()
            cnx.close()
    else:
        return 'db error', 500
    
    return f'{config['MISC']['URL']}/{uid}', 200

if __name__ == '__main__':
    app.run("127.0.0.1", 80, True)
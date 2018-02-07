from sanic import Sanic
from sanic.response import json
from sanic.exceptions import NotFound
from sanic import response

import requests

app = Sanic("Congregate")
app.static('/', './www')

with open('./www/404.html', 'r') as fh:
    notfound = fh.read()

# main page
@app.route("/")
async def index(request):
    return json({"hello": "world"})


### Congregate Access ###

@app.route('/get/<key>', methods=['GET'])
async def get():
    pass

@app.route('/put/<key>', methods=['POST'])
async def put():
    pass


### APP ### 

@app.route("/query_string")
def query_string(request):
    return json(request.json)
    #return json({ "parsed": True, "args": request.args, "url": request.url, "query_string": request.query_string })


async def get_page(url, headers):
    print("fetching url: ", url)
    print("headers: ", headers)
    r = requests.get(url, headers=headers)
    return r


@app.route('/proxy', methods=['GET', 'POST'])
async def proxy(request):
    #s = requests.Session()

    print("IP: ", request.ip)
    print("args: ", request.args)
    print("path: ", request.path)

    # collect page

    headers = request.headers
    url = request.args['clientURL'][0].strip()

    # TODO sanity check url
    
    # remove referer and host from headers
    #headers['host'] = url
    headers['referer'] = "www.google.com" # TODO set to own domain for ads?

    """
    prefixes = ["http://", "https://"]
    for prefix in prefixes:
        if url.startswith(prefix):
            url = url[len(prefix):]
    """

    try:
        r = await get_page(url, headers) #requests.get(url, headers=headers)
    except Exception as e:
        with open("www/404.html") as fh:
            return response.html(fh.read())

    

    # log page
    print(r.text)
    
    # replace urls

    #regex

    

    # return page

    return response.text(r.text)


@app.route('/login', methods=['GET', 'POST'])
def login(request):
    if request.method == 'POST':
        username = request.form['username']
        print("{} logged in".format(username))
        return response.redirect('/')
    return response.html('<form method="post"><p><input type=text name=username><p><input type=submit value=Login></form>')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return response.redirect('/')



@app.exception(NotFound)
def not_found(request, exception):
    return response.html(notfound, status=404)


### App Config ###

# set the secret key
import os
app.secret_key = os.urandom(24)

# create ssl context
import ssl
context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain('creds/server.crt', keyfile='creds/server.key')


if __name__ == "__main__":
    #app.run(host="0.0.0.0", port=8000)
    app.run(port=8000, debug=True, ssl=context)

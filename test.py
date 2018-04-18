from sanic import Sanic
from sanic.response import json
from sanic.exceptions import NotFound
from sanic import response

import requests
import re

app = Sanic("Proxy")
app.static('/', './www')
proxy_prefix = "https://localhost:8000/proxy?clientURL="

with open('./www/404.html', 'r') as fh:
    notfound = fh.read()

### APP ### 

async def get_page(url, headers):
    print("fetching url: ", url)
    print("headers: ", headers)
    r = requests.get(url, verify=False)#, headers=headers) # TODO transfer screen size etc.
    return r

async def post_page(url, headers, data):
    r = requests.post(url, data=data, verify=False)
    return r

@app.route('/proxy', methods=['GET', 'POST'])
async def proxy(request):

    print("IP: ", request.ip)
    print("args: ", request.args)
    print("path: ", request.path)
    print("query_string: ", request.query_string)

    # collect page

    headers = request.headers
    url = request.args['clientURL'][0].strip()
    # TODO sanity check url

    # remove referer and host from headers
    #headers['host'] = url
    headers['referer'] = "www.google.com" # TODO set to own domain for ads?

    
    if request.method == "POST":
        try:
            payload = request.body
            r = await post_page(url, headers, data=payload)
        
        except Exception as e:
            print("malformed url")


    elif request.method == "GET":
        try:
            r = await get_page(url, headers) #requests.get(url, headers=headers)
        except Exception as e:
            print("request failed: ", e)
            with open("www/404.html") as fh:
                return response.html(fh.read())



    # log page
    #print(r.text)
    

    filetype = "html"
    # determine filetype

    ### IMAGES ###
    image_suffixes = [".png", ".svg", ".jpg", ".jpeg"]
    for suf in image_suffixes:
        if suf in url:
            filetype = "image"

    if filetype == "image":
        return response.raw(r.content)


    ### HTML ###

    # replace urls for html

    #regex
    text = re.sub(r'"((http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*))"', r'"https://localhost:8000/proxy?clientURL=\1"', r.text, flags=re.IGNORECASE)

    stub = r'="https://localhost:8000/proxy?clientURL={}/'.format(url)
    text = re.sub(r'="/', stub, text)


    # return page
    #if text[0
    return response.html(text)


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

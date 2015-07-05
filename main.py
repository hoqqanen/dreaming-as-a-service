from flask import Flask, g, request

from dream import *

app = Flask(__name__)

@app.before_first_request
def load_model():
    g.net = dream.create_classifier('../caffe/models/bvlc_googlenet/')

@app.route('/', methods=['GET', 'POST'])
def make_dream():
    if request.method == 'POST' and len(request.files.keys()) > 0:
        key = request.files.keys()[0]
        filename = 'tmp/%s' % key
        with open(filename, 'wb') as file:
            file.write(request.files[key].read())
        return dream.deepdream(g.net, filename)
    #else if request.method == 'GET' and request.params['image_url']:
        # TODO: add the ability to dreamify a url image
    return 'No image found.'

if __name__ == '__main__':
    app.run()

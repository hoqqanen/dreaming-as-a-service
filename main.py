from flask import Flask, g, request

import deepdream_test

app = Flask(__name__)

#@app.before_first_request
#def load_model():
#    g.net = deepdream_test.make_net('../caffe/models/bvlc_googlenet/')

@app.route('/', methods=['GET', 'POST'])
def make_dream():
    net = deepdream_test.make_net('../caffe/models/bvlc_googlenet/')
    if request.method == 'POST' and len(request.files.keys()) > 0:
        key = request.files.keys()[0]
        filename = 'tmp/%s' % key
        with open(filename, 'wb') as file:
            file.write(request.files[key].read())
        return deepdream_test.one_iter_deep(net, filename)
    #else if request.method == 'GET' and request.params['image_url']:
        # TODO: add the ability to dreamify a url image
    return 'No image found.'

@app.route('/hello')
def say_hello():
    print "HELLO WORLD"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

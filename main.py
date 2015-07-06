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
	num_iterations = request.args.get('iters', 1)
   	inverse_gradient = request.args.get('inverse_gradient', 0)
	if int(inverse_gradient):
	    inverse_gradient = True
	else: 
	    inverse_gradient = False
        return deepdream_test.layerDream(net, filename, num_iterations, inverse_gradient)
    #else if request.method == 'GET' and request.params['image_url']:
        # TODO: add the ability to dreamify a url image
    return 'No image found.'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

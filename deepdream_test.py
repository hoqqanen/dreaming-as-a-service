# imports and basic notebook setup
from cStringIO import StringIO
import numpy as np
import scipy.ndimage as nd
import PIL.Image
from IPython.display import clear_output, Image, display
from google.protobuf import text_format
import re
import caffe

def showarray(a, fmt='jpeg'):
    a = np.uint8(np.clip(a, 0, 255))
    f = StringIO()
    PIL.Image.fromarray(a).save(f, fmt)
    display(Image(data=f.getvalue()))

def saveImage(a, octave, i, file_root="test_2", fmt='jpeg'):
    a = np.uint8(np.clip(a, 0, 255))
    f = StringIO()
    img = PIL.Image.fromarray(a)
    filename = file_root + str(octave) + "_" + str(i) + ".jpg"
    img.save(filename)

#model_path = '../caffe/models/bvlc_googlenet/' # substitute your path here
# Patching model to be able to compute gradients.
# Note that you can also manually add "force_backward: true" line to "deploy.prototxt".
def make_net(model_path):
    net_fn   = model_path + 'deploy.prototxt'
    param_fn = model_path + 'bvlc_googlenet.caffemodel'
    model = caffe.io.caffe_pb2.NetParameter()
    text_format.Merge(open(net_fn).read(), model)
    model.force_backward = True
    open('tmp.prototxt', 'w').write(str(model))

    #net = caffe.Classifier('tmp.prototxt', param_fn,
     #                  mean = np.float32([104.0, 116.0, 122.0]), # ImageNet mean, training set dependent
                       #channel_swap = (2,1,0)) # the reference model has channels in BGR order instead of RGB

    net = caffe.Classifier('tmp.prototxt', param_fn)
    net.set_channel_swap('data', (2, 1, 0))
    mean = np.float32([104.0, 116.0, 122.0]).reshape((3,1,1))
    net.set_mean('data', mean)
    return net

# a couple of utility functions for converting to and from Caffe's input image layout
def preprocess(net, img):
    return np.float32(np.rollaxis(img, 2)[::-1]) - net.mean['data']
def deprocess(net, img):
    return np.dstack((img + net.mean['data'])[::-1])

def make_step(net, step_size=1.5, end='inception_4c/output', jitter=32, clip=True, inverse_gradient=False):
    '''Basic gradient ascent step.'''

    src = net.blobs['data'] # input image is stored in Net's 'data' blob
    dst = net.blobs[end]

    ox, oy = np.random.randint(-jitter, jitter+1, 2)
    src.data[0] = np.roll(np.roll(src.data[0], ox, -1), oy, -2) # apply jitter shift

    net.forward(end=end)
    dst.diff[:] = dst.data  # specify the optimization objective
    net.backward(start=end)
    g = src.diff[0]
    # apply normalized ascent step to the input image
    if inverse_gradient:
        src.data[:] -= step_size/np.abs(g).mean() * g
    else:
        src.data[:] += step_size/np.abs(g).mean() * g

    src.data[0] = np.roll(np.roll(src.data[0], -ox, -1), -oy, -2) # unshift image

    if clip:
        bias = net.mean['data']
        src.data[:] = np.clip(src.data, -bias, 255-bias)

def deepdream(net, base_img, iter_n=10, octave_n=4, octave_scale=1.4, end='inception_4c/output', clip=True, inverse_gradient=False, **step_params):
    # prepare base images for all octaves
    octaves = [preprocess(net, base_img)]
    for i in xrange(octave_n-1):
        octaves.append(nd.zoom(octaves[-1], (1, 1.0/octave_scale,1.0/octave_scale), order=1))

    src = net.blobs['data']
    detail = np.zeros_like(octaves[-1]) # allocate image for network-produced details
    for octave, octave_base in enumerate(octaves[::-1]):
        h, w = octave_base.shape[-2:]
        if octave > 0:
            # upscale details from the previous octave
            h1, w1 = detail.shape[-2:]
            detail = nd.zoom(detail, (1, 1.0*h/h1,1.0*w/w1), order=1)

        src.reshape(1,3,h,w) # resize the network's input image size
        src.data[0] = octave_base+detail
        for i in xrange(iter_n):
            make_step(net, end=end, clip=clip, inverse_gradient=inverse_gradient, **step_params)

            # visualization
            vis = deprocess(net, src.data[0])
            if not clip: # adjust image contrast if clipping is disabled
                vis = vis*(255.0/np.percentile(vis, 99.98))
            #showarray(vis)
	    #saveImage(vis, octave, i)
            print octave, i, end, vis.shape
            clear_output(wait=True)

        # extract details produced on the current octave
        detail = src.data[0]-octave_base
    # returning the resulting image
    return deprocess(net, src.data[0])

def recursive_dream(net, file_path):
    frame = np.float32(PIL.Image.open(file_path))
    h, w = frame.shape[:2]
    s = 0.05 # scale coefficient
    frame_i = 0
    for i in xrange(100):
        frame = deepdream(net, frame)
        PIL.Image.fromarray(np.uint8(frame)).save("frames/%04d.jpg"%frame_i)
        frame = nd.affine_transform(frame, [1-s,1-s,1], [h*s/2,w*s/2,0], order=1)
        frame_i += 1

    

FILE_EXTENSIONS = {
    "jpg" : "jpeg",
    "jpeg" : "jpeg",
    "JPG" : "jpeg",
    "png" : "png",
    "PNG" : "png"
}

def infer_file_type(file_path):
    try:
        file_end = file_path.split(".")[1]
	file_ext = FILE_EXTENSIONS[file_end]
    except:
	print "unrecognized file type"
	return
    return file_ext

def numpyImageToStr(img, file_type):
    pil_image = PIL.Image.fromarray(np.uint8(img))
    output = StringIO()
    pil_image.save(output, file_type)
    contents = output.getvalue()
    output.close()
    return contents

def one_iter_deep(net, file_path):
    try:
        file_end = file_path.split(".")[1]
	file_ext = FILE_EXTENSIONS[file_end]
    except:
	print "unrecognized file type"
	return

    img = np.float32(PIL.Image.open(file_path))
    img_out = deepdream(net, img)
    return numpyImageToStr(img_out, file_ext)	

def layerDream(net, file_path, iters=1, inverse_gradient=False):
    file_ext = infer_file_type(file_path)
    frame = np.float32(PIL.Image.open(file_path))
    h, w = img.shape[:2]
    s = 0.05 # scale coefficient
    frame_i = 0
    iters = int(iters)
    for i in xrange(iters):
        frame = deepdream(net, frame, inverse_gradient)
        #PIL.Image.fromarray(np.uint8(frame)).save("frames/%04d.jpg"%frame_i)
        frame = nd.affine_transform(frame, [1-s,1-s,1], [h*s/2,w*s/2,0], order=1)
        frame_i += 1

    return numpyImageToStr(frame, file_ext)  

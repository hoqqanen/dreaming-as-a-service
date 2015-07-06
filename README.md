# Setup
We used an [Amazon EC2 AMI] provided by [Tito Costa] which already has Caffe. We largely use existing functionality provided in the [Google Deep Dream] repository and wrap an endpoint around it. Future work may include extending the endpoint to select between different models and layers (including target labels a la [twitch 317070]).

# How you can run this on EC2
- Boot up an AMI with Caffe (e.g. the one above)
- Grab the models you wish (e.g. `curl http://dl.caffe.berkeleyvision.org/bvlc_googlenet.caffemodel` from within caffe/models/bvlc_googlenet)
- Apply the Fixes mentioned below
- Clone this repo into home, `pip install -r requirements.txt`
- Add a custom tcp rule to the security groups in AWS and set the port to 5000, this allows incoming connections.

## Fixes
- `_Net_set_mean` in caffe needs to take `channel` rather than `elementwise` mode. We hacked this by simply changing the default parameter to be `channel`.
- We're not sure if this environment actually makes use of the gpu, but there's a patch that we've found which is not applied to the AMI ([available here][1]). In the future we may want to build Caffe ourselves with the patch applied. If this bullet is still here, you may expect the server to be slow. Using gunicorn to launch the app (eg `gunicorn -w 8 -t 360 main:app -b 0.0.0.0:5000` on an 8 core g2.2xlarge instance) can make use of multicore machines.

## Modifications of deepdream
- We specified the shape of the mean in the deepdream demo from `np.float32([104.0, 116.0, 122.0])` to `np.float32([104.0, 116.0, 122.0]).reshape((3,1,1))`
- Changed every instance of `net.transformer.mean` -> `net.mean`

[amazon ec2 ami]: https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#LaunchInstanceWizard:ami=ami-ffba7b94
[tito costa]:  http://blog.titocosta.com/post/110345699197/public-ec2-ami-with-torch-and-caffe-deep-learning
[1]: http://vision.princeton.edu/pvt/GoogLeNet/code/caffe-change-for-googlenet.patch
[Google Deep Dream]: https://github.com/google/deepdream
[twitch 317070]: http://www.twitch.tv/317070

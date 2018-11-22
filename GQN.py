import tensorflow as tf
from data_reader import DataReader
import matplotlib.pyplot as plt


def conv_block(prev, size, k: tuple, s: tuple):
    size_policy = 'same' if s == (1, 1) else 'valid'
    after_conv = tf.layers.conv2d(prev, size, k, s, size_policy)
    return tf.nn.relu(after_conv)


def representation_pipeline_tower(x, v):
    input_img = x
    input_v = tf.broadcast_to(v, (1, 16, 16, 7))

    test = conv_block(input_img, 256, (2, 2), (2, 2))

    # first residual
    test2 = conv_block(test, 128, (3, 3), (1, 1))
    test3 = tf.concat([test, test2], 3)
    test4 = conv_block(test3, 256, (2, 2), (2, 2))

    # add v
    test5 = tf.concat([test4, input_v], 3)

    # second residual
    test6 = conv_block(test5, 128, (3, 3), (1, 1))
    test7 = tf.concat([test6, test5], 3)
    test8 = conv_block(test7, 256, (3, 3), (1, 1))

    # last conv
    return conv_block(test8, 256, (1, 1), (1, 1))


def add_to_r(r, new_part):
    return tf.math.add(r, new_part)

def sample_gaussian(mu, sigma=1.):
    sampled = tf.random_normal((), mean=0., stddev=1.)
    return tf.multiply(tf.math.add(mu, sampled), sigma)

def prior_posterior(h_i, n_features):
    gaussianStats = conv_block(h_i, 2*n_features, (5, 5), (1, 1))
    means = gaussianStats[:, :, :, 0:n_features]
    stds = gaussianStats[:, :, :, n_features:]
    stds = tf.nn.softmax(stds)
    gaussianStats = (means, stds)
    latent = tf.map_fn(lambda stats : sample_gaussian(stats[0], stats[1]), gaussianStats, dtype=tf.float32)
    return latent

def recon_loss(x_true, x_pred):
    tf.sigmoid_cross_entropy_with_logits(labels=x_true, logits=x_pred)

def regularization_loss(prior, posterior):
    pass

def loss():
    return recon_loss + regularization_loss

def observation_sample(u_L):
    means = conv_block(u_L, 3, (1, 1), (1, 1))
    x = tf.map_fn(lambda mean : sample_gaussian(mean), means, dtype=tf.float32)
    return x

def image_reconstruction(sampled):
    pass
    #dunno how to to that
    #x = tf.layers.conv2d_transpose(sampled, 128, 3, 16, 'SAME')


root_path = 'data'
data_reader = DataReader(dataset='rooms_ring_camera', context_size=5, root=root_path)
data = data_reader.read(batch_size=1)
print(data[1])

#xd = representation_pipeline_tower(data[1], data[0][1])
#someTensor = tf.random_normal([1, 16, 16, 256], 0, 1)
#test = prior_posterior(someTensor, someTensor.shape[-1])
u_L = tf.random_normal([1, 64, 64, 256], 0, 1)
output_images = observation_sample(u_L)
output_images = tf.clip_by_value(output_images, 0, 1)

with tf.train.SingularMonitoredSession() as sess:
    d = sess.run(output_images)
    plt.imshow(d[0, :, :, :])
    plt.show()

a = 1

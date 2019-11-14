'''Xception V1 model for Keras.
On ImageNet, this model gets to a top-1 validation accuracy of 0.790.
and a top-5 validation accuracy of 0.945.
Do note that the input image format for this model is different than for
the VGG16 and ResNet models (299x299 instead of 224x224),
and that the input preprocessing function
is also different (same as Inception V3).
Also do note that this model is only available for the TensorFlow backend,
due to its reliance on `SeparableConvolution` layers.
# Reference:
- [Xception: Deep Learning with Depthwise Separable Convolutions](https://arxiv.org/abs/1610.02357)
'''

import warnings
import numpy as np
import h5py
from preprocessing import load_batches
from keras.models import Model
from keras import layers
from keras.layers import Dense
from keras.layers import Input
from keras.layers import BatchNormalization
from keras.layers import Activation
from keras.layers import Conv2D
from keras.layers import SeparableConv2D
from keras.layers import MaxPooling2D
from keras.layers import GlobalAveragePooling2D
from keras.layers import GlobalMaxPooling2D
from keras.layers import Lambda
from keras.models import Sequential
from keras import backend as K
from keras.engine.topology import get_source_inputs
from keras.utils.data_utils import get_file
from keras.utils import np_utils 
from keras.applications.imagenet_utils import decode_predictions
from keras.preprocessing import image

def model1():
    img_input = Input(shape=(80,320,3))
    #print("model1 img_input.shape",img_input.shape)
    x = Conv2D(32, (3, 3), strides=(2, 2), use_bias=False, name='block1_conv1')(img_input)
    x = BatchNormalization(name='block1_conv1_bn')(x)
    
    x = Activation('relu', name='block1_conv1_act')(x)
    x = Conv2D(32, (3, 3), use_bias=False, name='block1_conv2')(x)
    x = BatchNormalization(name='block1_conv2_bn')(x)
    print("modex.shape 0",x.shape)

    x = Activation('relu', name='block2_sepconv2_act1')(x)
    x = SeparableConv2D(32, (3, 3), padding='same', use_bias=False, name='block2_sepconv21')(x)
    x = BatchNormalization(name='block2_sepconv2_bn1')(x)
    print("modex.shape 1",x.shape)

    x = Activation('relu', name='block2_sepconv2_act2')(x)
    x = SeparableConv2D(64, (3, 3), padding='same', use_bias=False, name='block2_sepconv22')(x)
    x = BatchNormalization(name='block2_sepconv2_bn2')(x)
    print("modex.shape 2",x.shape)

    x = Activation('relu', name='block2_sepconv2_act3')(x)
    x = SeparableConv2D(64, (3, 3), padding='same', use_bias=False, name='block2_sepconv23')(x)
    x = BatchNormalization(name='block2_sepconv2_bn3')(x)
    print("modex.shape 3",x.shape)


    '''
    x = Activation('relu', name='block1_conv2_act')(x)
    residual = Conv2D(128, (1, 1), strides=(2, 2),
                      padding='same', use_bias=False)(x)
    residual = BatchNormalization()(residual)
    
    x = SeparableConv2D(128, (3, 3), padding='same', use_bias=False, name='block2_sepconv1')(x)
    x = BatchNormalization(name='block2_sepconv1_bn')(x)
    
    x = Activation('relu', name='block2_sepconv2_act')(x)
    x = SeparableConv2D(128, (3, 3), padding='same', use_bias=False, name='block2_sepconv2')(x)
    x = BatchNormalization(name='block2_sepconv2_bn')(x)

    x = MaxPooling2D((3, 3), strides=(2, 2), padding='same', name='block2_pool')(x)
    x = layers.add([x, residual])
 
    residual = Conv2D(256, (1, 1), strides=(2, 2),
                      padding='same', use_bias=False)(x)
    residual = BatchNormalization()(residual)
    
    x = Activation('relu', name='block3_sepconv1_act')(x)
    x = SeparableConv2D(256, (3, 3), padding='same', use_bias=False, name='block3_sepconv1')(x)
    x = BatchNormalization(name='block3_sepconv1_bn')(x)

    x = Activation('relu', name='block3_sepconv2_act')(x)
    x = SeparableConv2D(256, (3, 3), padding='same', use_bias=False, name='block3_sepconv2')(x)
    x = BatchNormalization(name='block3_sepconv2_bn')(x)

    x = MaxPooling2D((3, 3), strides=(2, 2), padding='same', name='block3_pool')(x)
    x = layers.add([x, residual])

    residual = Conv2D(728, (1, 1), strides=(2, 2),
                      padding='same', use_bias=False)(x)
    residual = BatchNormalization()(residual)

    x = Activation('relu', name='block4_sepconv1_act')(x)
    x = SeparableConv2D(728, (3, 3), padding='same', use_bias=False, name='block4_sepconv1')(x)
    x = BatchNormalization(name='block4_sepconv1_bn')(x)

    x = Activation('relu', name='block4_sepconv2_act')(x)
    x = SeparableConv2D(728, (3, 3), padding='same', use_bias=False, name='block4_sepconv2')(x)
    x = BatchNormalization(name='block4_sepconv2_bn')(x)
 
    x = MaxPooling2D((3, 3), strides=(2, 2), padding='same', name='block4_pool')(x)
    x = layers.add([x, residual])

    
    for i in range(1):
        residual = x
        prefix = 'block' + str(i + 5)

        x = Activation('relu', name=prefix + '_sepconv1_act')(x)
        x = SeparableConv2D(728, (3, 3), padding='same', use_bias=False, name=prefix + '_sepconv1')(x)
        x = BatchNormalization(name=prefix + '_sepconv1_bn')(x)
        x = Activation('relu', name=prefix + '_sepconv2_act')(x)
        x = SeparableConv2D(728, (3, 3), padding='same', use_bias=False, name=prefix + '_sepconv2')(x)
        x = BatchNormalization(name=prefix + '_sepconv2_bn')(x)
        x = Activation('relu', name=prefix + '_sepconv3_act')(x)
        x = SeparableConv2D(728, (3, 3), padding='same', use_bias=False, name=prefix + '_sepconv3')(x)
        x = BatchNormalization(name=prefix + '_sepconv3_bn')(x)

        x = layers.add([x, residual])
    

    residual = Conv2D(1024, (1, 1), strides=(2, 2),
                      padding='same', use_bias=False)(x)
    residual = BatchNormalization()(residual)

    x = Activation('relu', name='block13_sepconv1_act')(x)
    x = SeparableConv2D(728, (3, 3), padding='same', use_bias=False, name='block13_sepconv1')(x)
    x = BatchNormalization(name='block13_sepconv1_bn')(x)

    
    x = Activation('relu', name='block13_sepconv2_act')(x)
    x = SeparableConv2D(1024, (3, 3), padding='same', use_bias=False, name='block13_sepconv2')(x)
    x = BatchNormalization(name='block13_sepconv2_bn')(x)

    x = MaxPooling2D((3, 3), strides=(2, 2), padding='same', name='block13_pool')(x)
    x = layers.add([x, residual])

    x = SeparableConv2D(1536, (3, 3), padding='same', use_bias=False, name='block14_sepconv1')(x)
    x = BatchNormalization(name='block14_sepconv1_bn')(x)
    x = Activation('relu', name='block14_sepconv1_act')(x)
 
    x = SeparableConv2D(2048, (3, 3), padding='same', use_bias=False, name='block14_sepconv2')(x)
    x = BatchNormalization(name='block14_sepconv2_bn')(x)
    x = Activation('relu', name='block14_sepconv2_act')(x)
    '''
    
    x = GlobalAveragePooling2D(name='avg_pool_')(x)
    x = Dense(200, activation='softmax', name='predictions_')(x)
    '''
    
    if include_top:
        x = GlobalAveragePooling2D(name='avg_pool')(x)
        x = Dense(40, activation='softmax', name='predictions')(x)
    else:
        if pooling == 'avg':
            x = GlobalAveragePooling2D()(x)
        elif pooling == 'max':
            x = GlobalMaxPooling2D()(x)
    '''
    print("modex.shape",x.shape)

    return  Model(img_input, x, name='model_c')

def Xception(include_top=True, weights='imagenet',
             input_tensor=None, input_shape=None,
             pooling=None):
    """Instantiates the Xception architecture.
    Optionally loads weights pre-trained
    on ImageNet. This model is available for TensorFlow only,
    and can only be used with inputs following the TensorFlow
    data format `(width, height, channels)`.
    You should set `image_data_format="channels_last"` in your Keras config
    located at ~/.keras/keras.json.
    Note that the default input image size for this model is 299x299.
    # Arguments
        include_top: whether to include the fully-connected
            layer at the top of the network.
        weights: one of `None` (random initialization)
            or "imagenet" (pre-training on ImageNet).
        input_tensor: optional Keras tensor (i.e. output of `layers.Input()`)
            to use as image input for the model.
        input_shape: optional shape tuple, only to be specified
            if `include_top` is False (otherwise the input shape
            has to be `(299, 299, 3)`.
            It should have exactly 3 inputs channels,
            and width and height should be no smaller than 71.
            E.g. `(150, 150, 3)` would be one valid value.
        pooling: Optional pooling mode for feature extraction
            when `include_top` is `False`.
            - `None` means that the output of the model will be
                the 4D tensor output of the
                last convolutional layer.
            - `avg` means that global average pooling
                will be applied to the output of the
                last convolutional layer, and thus
                the output of the model will be a 2D tensor.
            - `max` means that global max pooling will
                be applied.
        classes: optional number of classes to classify images
            into, only to be specified if `include_top` is True, and
            if no `weights` argument is specified.
    # Returns
        A Keras model instance.
    # Raises
        ValueError: in case of invalid argument for `weights`,
            or invalid input shape.
        RuntimeError: If attempting to run this model with a
            backend that does not support separable convolutions.
    """
    if K.backend() != 'tensorflow':
        raise RuntimeError('The Xception model is only available with '
                           'the TensorFlow backend.')
    if K.image_data_format() != 'channels_last':
        warnings.warn('The Xception model is only available for the '
                      'input data format "channels_last" '
                      '(width, height, channels). '
                      'However your settings specify the default '
                      'data format "channels_first" (channels, width, height). '
                      'You should set `image_data_format="channels_last"` in your Keras '
                      'config located at ~/.keras/keras.json. '
                      'The model being returned right now will expect inputs '
                      'to follow the "channels_last" data format.')
        K.set_image_data_format('channels_last')
        old_data_format = 'channels_first'
    else:
        old_data_format = None

    input_shape = (3,80,320,3)

    if input_tensor is None:
        img_input = Input(shape=input_shape)
    else:
        if not K.is_keras_tensor(input_tensor):
            img_input = Input(tensor=input_tensor, shape=input_shape)
        else:
            img_input = input_tensor

    print("img_input.shape",img_input.shape)
 
    model_c = model1()

    def slice(x,idx):
        return x[:,idx]

    img_input0 =Lambda(slice,arguments={'idx': 0})(img_input)

    x0=model_c(img_input0)
    x0 = Dense(40, activation='softmax', name='predictions0')(x0)

    img_input1 =Lambda(slice,arguments={'idx': 1})(img_input)
    x1=model_c(img_input1)
    x1 = Dense(40, activation='softmax', name='predictions1')(x1)

    img_input2 =Lambda(slice,arguments={'idx': 2})(img_input)
    x2=model_c(img_input2)
    x2 = Dense(40, activation='softmax', name='predictions2')(x2)

    #img_input3 =Lambda(slice,arguments={'idx': 3})(img_input)
    #x3 = model_c(img_input3)
    #x3 = Dense(40, activation='softmax', name='predictions3')(x3)

    print("x0.shape",x0.shape)
    #x = np.add(x0,x1)
    #x = np.add(x,x2)
    #x = np.add(x,x3)

    added = layers.add([x0, x1])
    x = layers.add([added, x2])
    #x = layers.add([x, x3])

    '''
    
    img_input0 = Sequential([
    Lambda(lambda img_input: img_input[:,0], input_shape=[img_input.shape[0],4,160,320,3])  # 第二维截前 2 个
])
    '''
    
    #x=model1(img_input0,include_top)

    print("x.shape",x.shape)
     #K.concatenate([x0,x1,x2,x3] , axis=-1)


    # Ensure that the model takes into account
    # any potential predecessors of `input_tensor`.
    if input_tensor is not None:
        inputs = get_source_inputs(input_tensor)
    else:
        inputs = img_input
    # Create model.
    model = Model(inputs, x, name='xception')

    if old_data_format:
        K.set_image_data_format(old_data_format)
    return model

def append_data(data1,data2):
    return np.append(data1,[data2],0)

if __name__ == '__main__':
    # Load and compile model
    model = Xception(include_top=True,weights=None)
    model.compile(optimizer='Adadelta',
          loss='categorical_crossentropy',
          metrics=['accuracy'])
    batch_count = 0
    try:
        for i in range(0,5):
            print('----------- On Epoch: ' + str(i) + ' ----------')
            for x_train, y_train, x_test, y_test in load_batches():   
                # Model input requires numpy array

                x_train = np.array(x_train)
                '''
                x_train1 = np.array([x_train])
                x_train_0_5S = np.array(x_train_0_5S)
                x_train1 = append_data(x_train1,x_train_0_5S)
                x_train_2S = np.array(x_train_2S)
                x_train1 = append_data(x_train1,x_train_2S)
                x_train_5S = np.array(x_train_5S)
                x_train1 = append_data(x_train1,x_train_5S)
                '''

               
                x_test = np.array(x_test)
                '''
                x_test1 = np.array([x_test])
                x_test_0_5S = np.array(x_test_0_5S)
                x_test1 = append_data(x_test1,x_test_0_5S)
                x_test_2S = np.array(x_test_2S)
                x_test1 = append_data(x_test1,x_test_2S)
                x_test_5S = np.array(x_test_5S)
                x_test1 = append_data(x_test1,x_test_5S)
                '''

                # Classification to one-hot vector
                y_train = np_utils.to_categorical(y_train, num_classes=40)
                y_test = np_utils.to_categorical(y_test, num_classes=40)

                print("x_train.shape",x_train.shape)
                print("y_train.shape",y_train.shape)
                # Fit model to batch
                model.fit(x_train, y_train, verbose=1,epochs=1, 
                    validation_data=(x_test, y_test))
                
                batch_count += 1
                # Save a checkpoint
                if (batch_count % 20) == 0:
                    print('Saving checkpoint ' + str(batch_count))
                    model.save('model_checkpoint' + batch_count + '.h5')
                    print('Checkpoint saved. Continuing...')
    except Exception as e:
        print('Excepted with ' + str(e))
        print('Saving model...')
        model.save('model_trained_categorical.h5')
        print('Model saved.')
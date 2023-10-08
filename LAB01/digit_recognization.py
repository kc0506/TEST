# Standard scientific Python imports
import matplotlib.pyplot as plt

# Import datasets, classifiers and performance metrics
from sklearn import datasets, metrics, svm
from sklearn.model_selection import train_test_split

import cv2

def train_model():
    ###############################################################################
    # Digits dataset
    # --------------
    #
    # The digits dataset consists of 8x8
    # pixel images of digits. The ``images`` attribute of the dataset stores
    # 8x8 arrays of grayscale values for each image. We will use these arrays to
    # visualize the first 4 images. The ``target`` attribute of the dataset stores
    # the digit each image represents and this is included in the title of the 4
    # plots below.
    #
    # Note: if we were working from image files (e.g., 'png' files), we would load
    # them using :func:`matplotlib.pyplot.imread`.

    digits = datasets.load_digits()

    # _, axes = plt.subplots(nrows=1, ncols=4, figsize=(10, 3))
    # for ax, image, label in zip(axes, digits.images, digits.target):
    #     ax.set_axis_off()
    #     ax.imshow(image, cmap=plt.cm.gray_r, interpolation="nearest")
    #     ax.set_title("Training: %i" % label)

    ###############################################################################
    # Classification
    # --------------
    #
    # To apply a classifier on this data, we need to flatten the images, turning
    # each 2-D array of grayscale values from shape ``(8, 8)`` into shape
    # ``(64,)``. Subsequently, the entire dataset will be of shape
    # ``(n_samples, n_features)``, where ``n_samples`` is the number of images and
    # ``n_features`` is the total number of pixels in each image.
    #
    # We can then split the data into train and test subsets and fit a support
    # vector classifier on the train samples. The fitted classifier can
    # subsequently be used to predict the value of the digit for the samples
    # in the test subset.

    # flatten the images
    n_samples = len(digits.images)
    data = digits.images.reshape((n_samples, -1))

    # Create a classifier: a support vector classifier
    clf = svm.SVC(gamma=0.001)

    # Split data into 50% train and 50% test subsets
    X_train, X_test, y_train, y_test = train_test_split(
        data, digits.target, test_size=0.5, shuffle=False
    )

    # Learn the digits on the train subset
    clf.fit(X_train, y_train)

    # Predict the value of the digit on the test subset
    # predicted = clf.predict(X_test)
    return clf


def recognize_img_to_digit(path:str, clf:svm.SVC, logging=True):
    # Load an image
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    resized_img = 255-cv2.resize(img, (8, 8), interpolation=cv2.INTER_AREA)
    for i in range(8):
        for j in range(8):
            resized_img[i][j] =  int(resized_img[i][j]/16)
            if resized_img[i][j] <= 3:
                resized_img[i][j] = 0
    # print(resized_img)
    cv2.imwrite('./img/resized_img.png', resized_img)
    data = resized_img.reshape((1, -1))
    if logging:
        print("START RECOGNIZING...")
    digit = clf.predict(data)
    if logging:
        print(f"Result: {digit[0]}")
        print("FINISH RECOGNIZING...")
    return digit[0]
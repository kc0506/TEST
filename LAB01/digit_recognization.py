# Standard scientific Python imports
import matplotlib.pyplot as plt

# Import datasets, classifiers and performance metrics
from sklearn import datasets, metrics, svm
from sklearn.model_selection import train_test_split
import pytesseract
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

    _, axes = plt.subplots(nrows=1, ncols=4, figsize=(10, 3))
    for ax, image, label in zip(axes, digits.images, digits.target):
        ax.set_axis_off()
        ax.imshow(image, cmap=plt.cm.gray_r, interpolation="nearest")
        ax.set_title("Training: %i" % label)

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


def recognize_img_to_digit(path:str):
    # Load an image
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    #img = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV)[1]
    # Threshold the grayscale image to create a binary mask where the white line is detected
    ret, thresh = cv2.threshold(img, 1, 255, cv2.THRESH_BINARY)

    # Find contours in the binary mask
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Iterate through the contours and find the largest one (assuming the white line is the largest contour)
    largest_contour = max(contours, key=cv2.contourArea)

    # Get the bounding box of the largest contour
    x, y, w, h = cv2.boundingRect(largest_contour)
    center_x = (x + x + w) / 2
    center_y = (y + y + h) / 2
    r = max(w/2, h/2) + 30
    s_x = int(max(0, center_x - r))
    e_x = int(min(480, center_x + r))
    s_y = int(max(50, center_y - r))
    e_y = int(min(640, center_y + r))
    # Crop the image to fit the size of the white line
    cropped_image = img[s_y:e_y, s_x:e_x]
    
    cv2.imwrite('./img/cropped_image.jpg', cropped_image)

    print("START RECOGNIZING...")
    digit = pytesseract.image_to_string(img, config='--oem 3 --psm 6')
    digit = digit.replace('\n', '').replace('\f', '')
    print(digit)
    print("FINISH RECOGNIZING...")
    return digit
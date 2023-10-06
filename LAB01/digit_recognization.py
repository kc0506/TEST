import pytesseract
from PIL import Image


def recognize_img_to_digit(path:str):
    # Load an image
    image = Image.open(path)

    # Perform OCR on the image to recognize digits
    digits = pytesseract.image_to_string(image, config="--psm 6")

    print(digits)
                path_cropped = screenshot(display, DIGIT_IMG, 1)  # Screenshot
                digit = recognize_img_to_digit(path_cropped, CLF_MODEL)  # Get Result
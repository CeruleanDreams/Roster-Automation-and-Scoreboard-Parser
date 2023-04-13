from PIL import Image, ImageEnhance, ImageFilter
import cv2
import pytesseract
import numpy
import math
import glob
import os.path
import configparser


#Creating the object of configparser
config_data = configparser.ConfigParser()


#Reading data
config_data.read("config.ini")

#Getting Image Data
folder_path = './Pictures'


def stack_effects_and_combine(image, colour_1_bounds, colour_2_bounds, blur):
    part_colour_1 = mask_produce(image, colour_1_bounds, False, 0)

    part_colour_2 = mask_produce(image, colour_2_bounds, False, blur)

    #part_colour_2.show()

    combined_part = Image.blend(part_colour_1, part_colour_2, 0.4)
    enhancer = ImageEnhance.Contrast(combined_part)
    final_output = enhancer.enhance(3)
    return final_output

def mask_produce(image, colour_bounds, sharpen, blur):

    #Turning into a numpy array and removing the alpha channel
    image_data = numpy.asarray(image)
    image_data = image_data[:, :, :3]

    #Creating colour mask and blurring
    mask = cv2.inRange(image_data, colour_bounds[0], colour_bounds[1])  # modify your thresholds
    inv_mask = cv2.bitwise_not(mask)
    inv_mask = cv2.GaussianBlur(inv_mask, (5, 5), 1)

    if blur:
        inv_mask = cv2.blur(inv_mask, (5,5), blur)

    if sharpen == True:
        # Create the sharpening kernel
        kernel = numpy.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        # Apply the sharpening kernel to the image using filter2D
        inv_mask = cv2.filter2D(inv_mask, -1, kernel)

    transf_img = Image.fromarray(numpy.uint8(inv_mask)).convert('RGB')

    return transf_img


def parse_scoreboard(image_name):

    if image_name == "": #Grabs the most recent file inside the folder ./Pictures of the specified image type
        file_type = r'*.' + config_data["IMAGE"]["ImageType"]
        files = glob.glob(os.path.join(folder_path, file_type))
        most_recent_pic = max(files, key=os.path.getctime)
        raw_image = Image.open(most_recent_pic)

    else:
        raw_image = Image.open(folder_path + "/" + image_name)

    #Creating separate configurations for detecting the numbers and names
    #name_config_1 = r'--dpi 500 --oem 0 --psm 6 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890_. "'
    #name_config_2 = r'--dpi 500 --oem 1 --psm 6 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890_. "'
    #name_config_3 = r'--dpi 500 --oem 2 --psm 6 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890_. "'
    name_config_4 = r'--dpi 500 --oem 3 --psm 6 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890_. "'

    #num_config_1 = r'--dpi 500 --oem 0 --psm 6 -c tessedit_char_whitelist="1234567890 "'
    #num_config_2 = r'--dpi 500 --oem 1 --psm 6 -c tessedit_char_whitelist="1234567890 "'
    #num_config_3 = r'--dpi 500 --oem 2 --psm 6 -c tessedit_char_whitelist="1234567890 "'
    num_config_4 = r'--dpi 500 --oem 3 --psm 6 -c tessedit_char_whitelist="1234567890 "'

    #Determining the bounds of the colourscape
    white_bounds = [numpy.array([200, 200, 200]), numpy.array([256, 256, 256])]
    red_bounds = [numpy.array([60, 0, 60]), numpy.array([256, 85, 180])]


    #Create a contrast enhancer
    enhancer = ImageEnhance.Contrast(raw_image)

    # Increase the contrast
    enhanced_img = enhancer.enhance(3)

    # Increase the size of the image for better recognition
    width, height = enhanced_img.size
    new_width = math.floor(2 * width)
    new_height = math.floor(2 * height)
    scaled_enhanced_img = enhanced_img.resize((new_width, new_height))

    #scaled_enhanced_img.show()


    #Cropping out the right side of the image
    left_part = scaled_enhanced_img.crop((0, 0, new_width * 0.6, new_height))
    left_part_white = mask_produce(left_part, white_bounds, False, 0.9)
    #left_part_white.show()

    #Mergine the red and white masked versions of the left side
    left_part = stack_effects_and_combine(left_part, white_bounds, red_bounds, 0)
    left_part.show()

    #Extracting the string of names
    names = pytesseract.image_to_string(left_part, lang='eng', config=name_config_4)


    #Cropping out the left side of the image and rescaling for better detection
    right_part = scaled_enhanced_img.crop((0.67 * new_width, 0, new_width, new_height))
    right_extended_width = math.floor(1.6 * right_part.width)
    right_extended_height = math.floor(1.15 * right_part.height)


    right_part = right_part.resize((right_extended_width, right_extended_height))
    right_part = stack_effects_and_combine(right_part, white_bounds, red_bounds, 0.1)
    right_part.show()

    #Extracting the stats
    #stats_alt = pytesseract.image_to_string(right_part, lang='eng', config=num_config_1)
    stats = pytesseract.image_to_string(right_part, lang='eng', config=num_config_4)

    return[names, stats]


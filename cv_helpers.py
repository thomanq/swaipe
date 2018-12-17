
import os

import cv2
import numpy as np
from PIL import ImageGrab

from helpers import Region

OPENCV_DATA_PATH = os.path.join(os.path.dirname(cv2.__file__), "data")

def cv2_detect_main_pic():
    image = np.asarray(ImageGrab.grab()).copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    WHITE_BGR = [255,255,255]
    TINDER_BACKGROUND_BGR_LIGHT = [250,247,245]
    TINDER_BACKGROUND_BGR_DARK = [230,230,230]
    BADOO_BACKGROUND_BGR = [248,248,248]

    for bg_color in [BADOO_BACKGROUND_BGR, WHITE_BGR]:
        image[np.where((image == bg_color).all(axis = 2))] = [0,0,0]
    
    image[np.where((image > TINDER_BACKGROUND_BGR_DARK ).all(axis = 2))] = [0,0,0]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    edged = cv2.Canny(gray, 10, 250)
    dilate = cv2.dilate(edged,None)
    erode = cv2.erode(dilate,None)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    closed = cv2.morphologyEx(erode, cv2.MORPH_CLOSE, kernel)
    _, cnts, _ = cv2.findContours(closed.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
 

    for c in cnts:
        epsilon = 0.1 * cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, epsilon, True)
        if len(approx) == 4 and 500_000 > cv2.contourArea(c) > 100_000:
            cv2.drawContours(image, [approx], -1, (0, 255, 0), 4)

            # cv2.imshow("Output", image)
            # cv2.waitKey(0)
            
            left = approx[0][0][0]
            top = approx[0][0][1]
            width = approx[2][0][0] - left
            height = approx[2][0][1] - top

            return Region(left, top, width, height)
    
    return None

def locate_image(needleImage, haystackImage, method=cv2.TM_CCOEFF_NORMED, threshold = 0.5):
    ''' OpenCV matchTemplate method wrapper
        Available methods:
            cv2.TM_CCOEFF, cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR, cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED
    '''
    
    res = cv2.matchTemplate(haystackImage,needleImage, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    _, width, height = needleImage.shape[::-1]

    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left_x = min_loc[0]
        top_left_y = min_loc[1]
    else:
        top_left_x = max_loc[0]
        top_left_y = max_loc[1]
    
    if max_val > threshold: 
        return (top_left_x, top_left_y, width, height)
    else: 
        return None

def detect_face(img_path):

    frontalface_alt_xml_path  = os.path.join(OPENCV_DATA_PATH, "haarcascade_frontalface_alt.xml")
    haarcascade_eye  = os.path.join(OPENCV_DATA_PATH, "haarcascade_eye.xml")
    haarcascade_fullbody  = os.path.join(OPENCV_DATA_PATH, "haarcascade_lowerbody.xml")

    face_cascade = cv2.CascadeClassifier(frontalface_alt_xml_path)
    eye_cascade = cv2.CascadeClassifier(haarcascade_eye)
    fullbody_cascade = cv2.CascadeClassifier(haarcascade_fullbody)

    img = cv2.imread(img_path)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray_img)
    eyes = eye_cascade.detectMultiScale(gray_img)
    fullbody = fullbody_cascade.detectMultiScale(gray_img)

    # for (x,y,w,h) in faces:
    #     img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)

    # cv2.imshow('img',img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # print(faces)
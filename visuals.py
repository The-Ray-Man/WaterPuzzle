import cv2
import pyautogui
import numpy as np
from collections import defaultdict

def not_there():
    return None

def find_glasses(im,thresh):
    contours,hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    found_positions = []
    average_height = 0
    i = 0
    for cnt in contours:
        if cv2.contourArea(cnt)>500 and cv2.contourArea(cnt)<100000:
            i += 1
            [x,y,w,h] = cv2.boundingRect(cnt)
            if h > average_height*1.1/i or h < average_height*0.9/i and average_height != 0:
                continue
            average_height += h
            if w/h < 0.3:
                if all(do_collide([x,y,w,h],s) == False for s in found_positions):
                    found_positions.append([x,y,w,h])
                    cv2.rectangle(im,(x,y),(x+w,y+h),(0,0,255),2)
                    cv2.imshow("glasses",im)
                    cv2.waitKey(0)
                    # roi = im[y:y+h,x:x+w]
                    # yield(roi)
                    yield [x,y,w,h]

def thresh_im(im):
    gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),0)
    thresh = cv2.adaptiveThreshold(blur,255,1,1,11,2)
    return thresh


def get_glasses(image,x_handy,y_handy):
    im = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    thresh = thresh_im(im)
    blur = cv2.blur(image,(10,10))


    glasses = []
    glasses_pos = []
    color_dic = defaultdict(not_there)
    color_id = 0

    for x,y,w,h in list(find_glasses(im,thresh)):
        h_ = h//6*5 // 4
        liquids = []
        for i in range(4):
            pos = (x+w//2, y+i*h_+h_//2+h//6)
            color = blur[pos[1],pos[0]]
            print(color)
            color_combined = color[2]*256**2 + color[1]*256 + color[0]
            # cv2.circle(image, pos, 10, (255,0,0), 10)
            # cv2.imshow("title",image)
            # key = cv2.waitKey(0)
            g = get_gray_value(color)
            # print(g)
            if g > 55 and g < 375: 
                if color_dic[color_combined] == None:
                    color_id += 1
                    color_dic[color_combined] = color_id
                liquids.insert(0,color_dic[color_combined])
            else:
                liquids.insert(0,0)

        glasses.append(liquids)
        glasses_pos.append((x+w//2 + x_handy,y+h//2 + y_handy))
    return glasses, glasses_pos


def findHandy(image,thresh):
    contours,hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    sorted_contours = sorted(contours, key = lambda cnt: cv2.contourArea(cnt), reverse=True)
    # print(sorted_contours)
    for cnt in sorted_contours:
        if cv2.contourArea(cnt) > 100000:
            [x,y,w,h] = cv2.boundingRect(cnt)
            # if  h/w<0.8 and h/w > 0.3:
            if w/h>0.3:
                cv2.rectangle(image,(x,y),(x+w,y+h),(0,0,255),2)
                roi = thresh[y:y+h,x:x+w]
                im = image[y:y+h,x:x+w]
                # cv2.imwrite("./screen.jpg",im)
                cv2.imshow('norm',image)
                key = cv2.waitKey(0)
                if key == 13:
                    cv2.destroyAllWindows()
                    return [x,y,w,h]
    cv2.destroyAllWindows()



def do_collide(s1,s2):
    x,y,w,h = s1
    middle_pos = (x+w//2, y+h//2)
    x,y,w,h = s2
    return middle_pos[0]<x+w and middle_pos[0]>x and middle_pos[1]<y+h and middle_pos[1] >  y

def get_gray_value(color_code):
    x,y,z = color_code
    x = (int(x)+int(x))/2
    y = (int(y)+int(y))/2
    z = (int(z)+int(z))/2
    return int((x*x+y*y+z*z)**0.5)

pos_handy = None

def read_display():
    global pos_handy
    image = pyautogui.screenshot()
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    thresh = thresh_im(image)
    if pos_handy == None:
        x,y,w,h = findHandy(image,thresh)
        pos_handy = [x,y,w,h]
    x,y,w,h = pos_handy
    image = image[y:y+h,x:x+w]
    # cv2.imshow('norm',image)
    # key = cv2.waitKey(0)
    # glasses,glasses_pos = get_glasses(cv2.imread("./WaterPuzzle/screen.jpg"))
    glasses,glasses_pos = get_glasses(image,x,y)
    return glasses, glasses_pos


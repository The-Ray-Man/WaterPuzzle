import cv2
import pyautogui
import numpy as np

def analize_sudoku():
    image = pyautogui.screenshot()
    im = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    out = np.zeros(im.shape,np.uint8)
    gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),0)
    thresh = cv2.adaptiveThreshold(blur,255,1,1,11,2)
    cv2.imshow('norm',thresh)
    (x,y,w,h) = findHandy(im,thresh)
    thresh = thresh[y:y+h,x:x+w]
    im = im[y:y+h,x:x+w]
    im = highlit_glass(im)
    contours,hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    found_positions = []

    for cnt in contours:
        if cv2.contourArea(cnt)>500 and cv2.contourArea(cnt)<100000:
            [x,y,w,h] = cv2.boundingRect(cnt)
            if w/h < 0.3:
                if all(do_colide([x,y,w,h],s) == False for s in found_positions):
                    found_positions.append([x,y,w,h])
                    cv2.rectangle(im,(x,y),(x+w,y+h),(0,0,255),2)
                    roi = thresh[y:y+h,x:x+w]
                    cv2.imshow('norm',im)
                    key = cv2.waitKey(0)

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
                cv2.imshow('norm',image,)
                key = cv2.waitKey(0)
                im = image[y:y+h,x:x+w]
                cv2.imwrite("./screen.jpg",im)
                if key == 13:
                    print("found sudoku")
                    cv2.destroyAllWindows()
                    return [x,y,w,h]
    cv2.destroyAllWindows()


def highlit_glass(im):
    height, width, channels = im.shape
    for y in range(0,height):
        for x in range(0,width):
            if all(c  < 200 and c>170 for c in im[y,x]):
                im[y,x] = [255,0,0]
            else:
                im[y,x] = [0,0,0]
    return im

def do_colide(s1,s2):
    x,y,w,h = s1
    middle_pos = (x+w//2, y+h//2)
    x,y,w,h = s2
    return middle_pos[0]<x+w and middle_pos[0]>x and middle_pos[1]<y+h and middle_pos[1] >  y


analize_sudoku()


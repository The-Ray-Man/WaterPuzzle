import cv2
import numpy as np
from collections import defaultdict

import subprocess
import os
import sys


def not_there():
    return None


def find_glasses(im, thresh):
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    found_positions = []
    average_height = 0
    i = 0
    for cnt in contours:
        if 10000 < cv2.contourArea(cnt) < 100000:
            [x, y, w, h] = cv2.boundingRect(cnt)
            # if not i == 0:
            #     if (h > average_height*1.1/i or h < average_height*0.9/i) or average_height != 0:
            #         continue
            # i += 1
            # average_height += h
            if w / h < 0.3:
                if all(do_collide([x, y, w, h], s) is False for s in found_positions):
                    found_positions.append([x, y, w, h])
                    cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    # cv2.imshow("glasses",im)
                    # cv2.waitKey(0)
                    # roi = im[y:y+h,x:x+w]
                    # yield(roi)
                    yield [x, y, w, h]


def thresh_im(im):
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)
    return thresh


def get_glasses(image, x_handy, y_handy):
    im = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    thresh = thresh_im(im)
    blur = cv2.blur(image, (6, 6))

    glasses = []
    glasses_pos = []
    color_dic = defaultdict(not_there)
    color_id = 1

    for x, y, w, h in list(find_glasses(im, thresh)):
        h_ = h // 10 * 9 // 4
        liquids = []
        for i in range(4):
            pos = ((x + w // 2), (y + i * h_ + h_ // 2 + h // 9))
            print(pos)
            color = im[pos[1], pos[0]]
            print(color)
            color_combined = color[2] * 256 ** 2 + color[1] * 256 + color[0]
            cv2.circle(image, pos, 10, (255, 0, 0), 10)
            # cv2.imshow("title",image)
            # key = cv2.waitKey(0)
            g = get_gray_value(color)

            # if color_id == 1:
            #     color_dic[color_combined] = 1
            #     color_id = 2

            if color_combined in color_dic.keys():
                liquids.insert(0, color_dic[color_combined])

            else:
                for color_code, id_ in color_dic.items():
                    c_x, c_y, c_z = reverse_colorcode(color_code)
                    d = calculate_distance(color, (c_x, c_y, c_z))
                    print("d: ", d)
                    if d < 20:
                        liquids.insert(0, color_dic[color_code])
                        break
                else:
                    color_dic[color_combined] = color_id
                    liquids.insert(0, color_id)

                    color_id += 1
        glasses.append(liquids)
        glasses_pos.append((x + w // 2 + x_handy, y + h // 2 + y_handy))
    print(glasses)
    max_value = 0
    max_index = 0
    for i in range(1, len(glasses)):
        if sum(x.count(i) for x in glasses) > max_value:
            max_value = sum(x.count(i) for x in glasses)
            max_index = i
    for b in range(len(glasses)):
        for l in range(len(glasses[b])):
            if glasses[b][l] == max_index:
                glasses[b][l] = 0

    return glasses, glasses_pos


def findHandy(image, thresh):
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    sorted_contours = sorted(contours, key=lambda cnt: cv2.contourArea(cnt), reverse=True)
    # print(sorted_contours)
    for cnt in sorted_contours:
        if cv2.contourArea(cnt) > 100000:
            [x, y, w, h] = cv2.boundingRect(cnt)
            # if  h/w<0.8 and h/w > 0.3:
            if w / h > 0.3:
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                roi = thresh[y:y + h, x:x + w]
                im = image[y:y + h, x:x + w]
                # cv2.imwrite("./screen.jpg",im)
                cv2.imshow('norm', image)
                key = cv2.waitKey(0)
                if key == 13:
                    cv2.destroyAllWindows()
                    return [x, y, w, h]
    cv2.destroyAllWindows()


def do_collide(s1, s2):
    x, y, w, h = s1
    middle_pos = (x + w // 2, y + h // 2)
    x, y, w, h = s2
    return x + w > middle_pos[0] > x and y + h > middle_pos[1] > y


def get_gray_value(color_code):
    x, y, z = color_code
    x = (int(x) + int(x)) / 2
    y = (int(y) + int(y)) / 2
    z = (int(z) + int(z)) / 2
    return int((x * x + y * y + z * z) ** 0.5)


pos_handy = None


def get_screen():
    os.system("adb shell screencap -p > screen.png")
    # cmd = "adb  shell screencap -p"
    # process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    # binary_screenshot = process.stdout.read()
    #
    # binary_screenshot = binary_screenshot.replace(b'\r\r\n', b'\n')
    # with open(filename, 'wb') as f:
    #     f.write(binary_screenshot)


def read_display():
    global pos_handy
    get_screen()
    image = cv2.imread("screen.png", cv2.COLOR_RGB2BGR)
    thresh = thresh_im(image)
    if pos_handy is None:
        x, y, w, h = findHandy(image, thresh)
        pos_handy = [x, y, w, h]
    x, y, w, h = pos_handy
    image = image[y:y + h, x:x + w]
    # cv2.imshow('norm',image)
    # key = cv2.waitKey(0)
    # glasses,glasses_pos = get_glasses(cv2.imread("./WaterPuzzle/screen.jpg"))
    glasses, glasses_pos = get_glasses(image, x, y)
    return glasses, glasses_pos


def calculate_distance(v1, v2):
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2) ** 0.5


def reverse_colorcode(color_code):
    x_color = color_code >> 16
    y_color = (color_code >> 8) & 0b11111111
    z_color = color_code & 0b11111111
    print("reversed colors:", z_color, y_color, x_color)
    return z_color, y_color, x_color

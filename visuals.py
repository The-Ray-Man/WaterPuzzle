import cv2
import numpy as np
from collections import defaultdict
import os
import platform
from ppadb.client import Client as AdbClient

if platform.system() == "Windows":
    os.environ['PATH'] = 'C:/Program Files/platform-tools/'


def not_there():
    return None



def find_glasses(glass_hi, im, debug=False):

    glass_hi = cv2.cvtColor(glass_hi, cv2.COLOR_HSV2BGR)
    glass_hi = cv2.cvtColor(glass_hi, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("glass_hi",glass_hi)
    # cv2.waitKey(0)
    contours, hierarchy = cv2.findContours(glass_hi, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    found_positions = []
    average_height = 0
    i = 0
    for cnt in contours:
        if 10000 < cv2.contourArea(cnt) < 100000:
            [x, y, w, h] = cv2.boundingRect(cnt)
            if w / h < 0.3:
                if all(do_collide([x, y, w, h], s) is False for s in found_positions):
                    found_positions.append([x, y, w, h])
                    cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    if debug:
                        cv2.imshow("glasses", im)

                        cv2.waitKey(0)
                    yield [x, y, w, h]


def thresh_im(im):
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)
    return thresh


def highlit_glasses(im):
    hsv_img = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

    hsv_color1 = np.array([0, 0, 185])
    hsv_color2 = np.array([0, 0, 188])

    # Define threshold color range to filter
    mask = cv2.inRange(hsv_img, hsv_color1, hsv_color2)

    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(hsv_img, hsv_img, mask=mask)
    return res


def get_glasses(image, glass_hi, debug=False):
    im = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    thresh = thresh_im(im)
    blur = cv2.blur(image, (6, 6))

    glasses = []
    glasses_pos = []
    color_dic = defaultdict(not_there)
    color_id = 1

    for x, y, w, h in list(find_glasses(glass_hi, im)):
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

        h_ = h // 10 * 9 // 4
        liquids = []
        for i in range(4):
            pos = ((x + w // 2), (y + i * h_ + h_ // 2 + h // 9))
            # print(pos)
            color = im[pos[1], pos[0]]
            # print(color)
            color_combined = color[2] * 256 ** 2 + color[1] * 256 + color[0]
            cv2.circle(image, pos, 10, (255, 0, 0), 10)

            if debug:
                cv2.imshow("found glasses",im)
                key = cv2.waitKey(0)

            if color_combined in color_dic.keys():
                liquids.insert(0, color_dic[color_combined])

            else:
                for color_code, id_ in color_dic.items():
                    c_x, c_y, c_z = reverse_colorcode(color_code)
                    d = calculate_distance(color, (c_x, c_y, c_z))
                    if d < 30:
                        liquids.insert(0, color_dic[color_code])
                        break
                else:
                    color_dic[color_combined] = color_id
                    liquids.insert(0, color_id)

                    color_id += 1
        glasses.append(liquids)
        glasses_pos.append((x + w // 2, y + h // 2))

    glasses = findEmptyGlasses(glasses)
    cv2.imwrite("data.png",image)

    return glasses, glasses_pos


def findEmptyGlasses(glasses):
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
    return glasses


def do_collide(s1, s2):
    x, y, w, h = s1
    middle_pos = (x + w // 2, y + h // 2)
    x, y, w, h = s2
    return x + w > middle_pos[0] > x and y + h > middle_pos[1] > y


def read_display(device):
    global pos_handy

    result = device.screencap()
    with open("pic.png", "wb") as fp:
        fp.write(result)

    image = cv2.imread("pic.png", cv2.COLOR_RGB2BGR)

    thresh = thresh_im(image)
    glass_highlit = highlit_glasses(image)

    glasses, glasses_pos = get_glasses(image, glass_highlit)
    if len(glasses) == 0:
        return [], []
    print(glasses_pos)
    glasses_pos = put_glasses_down(device,glasses_pos)
    print(glasses_pos)
    return glasses, glasses_pos


def calculate_distance(v1, v2):
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2) ** 0.5


def reverse_colorcode(color_code):
    x_color = color_code >> 16
    y_color = (color_code >> 8) & 0b11111111
    z_color = color_code & 0b11111111
    return z_color, y_color, x_color


def put_glasses_down(device,glass_pos):
    y_pos = [(i,y) for i,(x,y) in enumerate(glass_pos)]

    first_glass = y_pos[0]
    glass_rows = [y_pos[0]]

    for i,y in y_pos[1:]:
        if y < first_glass[1] + 110 and y > first_glass[1] - 110:
            glass_rows.append((i,y))
    remaining_glasse = [g for g in y_pos if g not in glass_rows]

    rows = [glass_rows, remaining_glasse]
    glasses_up = []
    for row in rows:
        average = sum([y for (i,y) in row]) / len(row)
        for i,y in row:
            if y < average:
                glasses_up.append(i)
                X, Y = glass_pos[i]
                cmd = f"input tap {X} {Y}"
                device.shell(cmd)
        for i in glasses_up:
            glass_pos[i] = (glass_pos[i][0],glass_pos[(i+1)%len(row)][1])

    return glass_pos

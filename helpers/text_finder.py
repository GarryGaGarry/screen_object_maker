from imutils.object_detection import non_max_suppression
import numpy as np
import pytesseract
from itertools import groupby
import argparse
import time
from operator import itemgetter
import cv2


def hsv_filter(_image, h_min=(0, 0, 149), h_max=(0, 0, 255)):
    _image = cv2.cvtColor(_image, cv2.COLOR_BGR2HSV)
    h_min = np.array(h_min, np.uint8)
    h_max = np.array(h_max, np.uint8)

    # накладываем фильтр на кадр в модели HSV
    _image = cv2.inRange(_image, h_min, h_max)
    _image = cv2.cvtColor(_image, cv2.COLOR_GRAY2BGR)
    return _image


def _calculate_new_image_size(old_w, old_h, speed=2):
    ratio = round(old_h / old_w, 1)
    # высота и ширина картинки должны быть кратны 32
    CONSTANT = 32
    new_h = round(CONSTANT * speed * ratio * 10)
    new_w = round(CONSTANT * speed * 10)
    ratio_w = old_w / float(new_w)
    ratio_h = old_h / float(new_h)
    return new_w, new_h, ratio_w, ratio_h


def _find_words(_image, w, h, _args):
    layer_names = [
        "feature_fusion/Conv_7/Sigmoid",
        "feature_fusion/concat_3"]
    print("[INFO] loading EAST text detector...")
    net = cv2.dnn.readNet(_args["east"])
    blob = cv2.dnn.blobFromImage(_image, 1.0, (w, h),
                                 (123.68, 116.78, 103.94), swapRB=True, crop=False)
    start = time.time()
    net.setInput(blob)
    (scores, geometry) = net.forward(layer_names)
    end = time.time()
    print("[INFO] text detection took {:.6f} seconds".format(end - start))
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []
    for y in range(0, numRows):
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        for x in range(0, numCols):
            if scoresData[x] < _args["min_confidence"]:
                continue

            (offsetX, offsetY) = (x * 4.0, y * 4.0)

            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)

            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            bot_x = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            bot_y = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            top_x = int(bot_x - w)
            top_y = int(bot_y - h)

            rects.append((top_x, top_y, bot_x, bot_y))
            confidences.append(scoresData[x])
    result = non_max_suppression(np.array(rects), probs=confidences)
    return result


def _scale_coordinates(boxes, ratio_w, ratio_h):
    new_boxes = []
    for (top_x, top_y, bot_x, bot_y) in boxes:
        top_x = int(top_x * ratio_w)
        top_y = int(top_y * ratio_h)
        bot_x = int(bot_x * ratio_w)
        bot_y = int(bot_y * ratio_h)
        new_boxes.append([top_x, top_y, bot_x, bot_y])
    return new_boxes


# Сортируем координаты по горизонтальным группам с шагом line_size,
# номер группы приписываем к координатам пятым параметром
def _group_boxes_by_horizontal_lines(boxes, line_size=10):
    y_start_group = boxes[0][1]
    group_count = 0
    for index, (top_x, top_y, bot_x, bot_y) in enumerate(boxes):
        # Если в ближайшие group_pixel_size нет бокса с координатами
        # создаем новую группу
        if (top_y - y_start_group) < line_size:
            boxes[index].append(group_count)
        else:
            # Переходим на следующую группу и обновляем начало группы(y_start_group)
            group_count = group_count + 1
            boxes[index].append(group_count)
            y_start_group = top_y
    return groupby(boxes, itemgetter(4))


def _group_boxes_for_merging(boxes_group, distance=80):
    groups_of_boxes_for_merge = []
    for group_name, boxes in boxes_group:
        boxes_list = list(boxes)

        # Сортируем по top x
        boxes_list.sort(key=itemgetter(0))
        boxes_for_merge = [boxes_list[0]]
        for previous_index, box in enumerate(boxes_list[1:]):
            previous_box = boxes_list[previous_index]
            finish_x_previous_box = previous_box[2]     # bot x
            start_x_box = box[0]    # top x

            if (finish_x_previous_box >= start_x_box) or ((start_x_box - finish_x_previous_box) <= distance):
                # Если координаты накладываются на предыдущими координатами или находятся не далеко от них
                # то добавляем координаты в группу для слияния
                boxes_for_merge.append(box)
            else:
                # Иначе создаем новую группу для слияния
                groups_of_boxes_for_merge.append(boxes_for_merge)
                boxes_for_merge = [box]
        groups_of_boxes_for_merge.append(boxes_for_merge)
    return groups_of_boxes_for_merge


def _merge_groups(groups_of_boxes_for_merge):
    _result_boxes = []
    for group_for_merge in groups_of_boxes_for_merge:
        group_for_merge.sort(key=itemgetter(0))
        top_x = group_for_merge[0][0]
        group_for_merge.sort(key=itemgetter(1))
        top_y = group_for_merge[0][1]
        group_for_merge.sort(key=itemgetter(2))
        bot_x = group_for_merge[-1][2]
        group_for_merge.sort(key=itemgetter(3))
        bot_y = group_for_merge[-1][3]
        _result_boxes.append([top_x, top_y, bot_x, bot_y])
    return _result_boxes


def image_to_text(image_with_text):
    pytesseract.pytesseract.tesseract_cmd = r'C:\tools\tesseract\tesseract.exe'
    text = pytesseract.image_to_string(image_with_text)  # чтоб искать русский текст добавь lang='rus'
    return text


def show_image_with_found_text(boxes, original_image):
    i = 1
    for (top_x, top_y, bot_x, bot_y) in boxes:
        image_with_text = original_image[top_y:bot_y + 10, top_x:bot_x + 10]
        # image_with_text = image_with_text.quantize(2, 0)

        image_with_text = np.asarray(image_with_text)
        text = image_to_text(image_with_text)
        print('%d Text: %s [%d, %d, %d, %d]' % (i, text, top_x, top_y, bot_x, bot_y))

        # cv2.imshow('%d' % i, image_with_text)   # выводим каждый найденный текст

        cv2.rectangle(original_image, (top_x - 1, top_y), (bot_x, bot_y + 2), 100, 2)   # Обводим найденный текст

        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (top_x, top_y)
        fontScale = 1
        fontColor = (0, 0, 255)
        lineType = 2

        cv2.putText(original_image, '%d' % i,   # нумеруем текст
                    bottomLeftCornerOfText,
                    font,
                    fontScale,
                    fontColor,
                    lineType)
        i = i + 1

    # выводим результат
    cv2.imshow("Origin", original_image)
    cv2.waitKey(0)


def find_text(_image, _args):
    # размеры картинки должны быть кратны 32, поэтому высчитываем новый размер картинки
    # speed - это множетель для размеров, чем он меньше, тем меньше картинка и быстрее поиск, но результат хуже
    (h, w) = _image.shape[:2]
    (w, h, ratio_w, ratio_h) = _calculate_new_image_size(w, h, _args["speed"])
    _image = cv2.resize(_image, (w, h))

    boxes = _find_words(_image, w, h, _args)   # находим координаты слов на картинке
    # переводим координаты, чтоб они соответствовали оригинальной картинке
    boxes = _scale_coordinates(boxes.tolist(), ratio_w, ratio_h)
    boxes.sort(key=itemgetter(1))   # Сортируем координаты по top_Y

    # чтоб на выходе иметь координаты строк с текстом, а не отдельных слов, группируем координаты близкие по оси Y
    boxes_group = _group_boxes_by_horizontal_lines(boxes, 20)

    # теперь группируем ближайшие друг к другу координаты по оси X
    groups_of_boxes_for_merge = _group_boxes_for_merging(boxes_group, 100)

    # сойденяем группы координат которые мы нашли ранее
    result = _merge_groups(groups_of_boxes_for_merge)
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", type=str,
                    help="path to input image")
    ap.add_argument("-east", "--east", type=str, default='frozen_east_text_detection.pb',
                    help="path to input EAST text detector")
    ap.add_argument("-c", "--min-confidence", type=float, default=0.5,
                    help="minimum probability required to inspect a region")
    ap.add_argument("-s", "--speed", type=int, default=2,
                    help="The lower parameter, faster text search will complete,\
                     but probability of success is lower.\
                     It is not recommended to set more than 3")
    ap.add_argument("-t", "--path-to-tesseract", type=str, default=r'C:\tools\tesseract\tesseract.exe',
                    help="path to tesseract.exe")
    args = vars(ap.parse_args())

    # для дебага
    # args["image"] = "text.png"

    if args["image"] is None:
        raise ValueError("Please set path to image from which you want to get text")

    image = cv2.imread(args["image"])
    orig = image.copy()
    image = hsv_filter(image)

    result_boxes = find_text(image, args)
    show_image_with_found_text(result_boxes, orig)

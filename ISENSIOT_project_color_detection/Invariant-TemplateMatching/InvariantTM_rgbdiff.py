import cv2
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.patches as patches
import matplotlib as mpl
import math

box_points = []
button_down = False


def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, -angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR,borderValue=255)
    return result


def scale_image(image, percent, maxwh):
    max_width = maxwh[1]
    max_height = maxwh[0]
    max_percent_width = max_width / image.shape[1] * 100
    max_percent_height = max_height / image.shape[0] * 100
    if max_percent_width < max_percent_height:
        max_percent = max_percent_width
    else:
        max_percent = max_percent_height
    if percent > max_percent:
        percent = max_percent
    width = int(image.shape[1] * percent / 100)
    height = int(image.shape[0] * percent / 100)
    result = cv2.resize(image, (width, height), interpolation = cv2.INTER_AREA)
    return result, percent


def invariantMatchTemplate(rgbimage, rgbtemplate, method, matched_thresh, rgbdiff_thresh, rot_range, rot_interval, scale_range, scale_interval, rm_redundant):
    """
    rgbimage: RGB image where the search is running.
    rgbtemplate: RGB searched template. It must be not greater than the source image and have the same data type.
    method: [String] Parameter specifying the comparison method
    matched_thresh: [Float] Setting threshold of matched results(0~1).
    rgbdiff_thresh: [Float] Setting threshold of average RGB difference between template and source image.
    rot_range: [Integer] Array of range of rotation angle in degrees. Example: [0,360]
    rot_interval: [Integer] Interval of traversing the range of rotation angle in degrees.
    scale_range: [Integer] Array of range of scaling in percentage. Example: [50,200]
    scale_interval: [Integer] Interval of traversing the range of scaling in percentage.
    rm_redundant: [Boolean] Option for removing redundant matched results based on the width and height of the template.
    minmax:[Boolean] Option for finding points with minimum/maximum value.

    Returns: List of satisfied matched points in format [[point.x, point.y], angle, scale].
    """
    img_gray = cv2.cvtColor(rgbimage, cv2.COLOR_RGB2GRAY)
    template_gray = cv2.cvtColor(rgbtemplate, cv2.COLOR_RGB2GRAY)
    image_maxwh = img_gray.shape
    height, width = template_gray.shape
    all_points = []

    for next_angle in range(rot_range[0], rot_range[1], rot_interval):
        for next_scale in range(scale_range[0], scale_range[1], scale_interval):
            scaled_template_gray, actual_scale = scale_image(template_gray, next_scale, image_maxwh)
            if next_angle == 0:
                rotated_template = scaled_template_gray
            else:
                rotated_template = rotate_image(scaled_template_gray, next_angle)
                if next_scale == 100 and next_angle == 15:
                    plt.imshow(rotated_template)
                    plt.show()
            if method == "TM_CCOEFF":
                matched_points = cv2.matchTemplate(img_gray, rotated_template, cv2.TM_CCOEFF)
                satisfied_points = np.where(matched_points >= matched_thresh)
            elif method == "TM_CCOEFF_NORMED":
                matched_points = cv2.matchTemplate(img_gray, rotated_template, cv2.TM_CCOEFF_NORMED)
                satisfied_points = np.where(matched_points >= matched_thresh)
            elif method == "TM_CCORR":
                matched_points = cv2.matchTemplate(img_gray, rotated_template, cv2.TM_CCORR)
                satisfied_points = np.where(matched_points >= matched_thresh)
            elif method == "TM_CCORR_NORMED":
                matched_points = cv2.matchTemplate(img_gray, rotated_template, cv2.TM_CCORR_NORMED)
                satisfied_points = np.where(matched_points >= matched_thresh)
            elif method == "TM_SQDIFF":
                matched_points = cv2.matchTemplate(img_gray, rotated_template, cv2.TM_SQDIFF)
                satisfied_points = np.where(matched_points <= matched_thresh)
            elif method == "TM_SQDIFF_NORMED":
                matched_points = cv2.matchTemplate(img_gray, rotated_template, cv2.TM_SQDIFF_NORMED)
                satisfied_points = np.where(matched_points <= matched_thresh)
            else:
                raise Exception("There's no such comparison method for template matching.")
            for pt in zip(*satisfied_points[::-1]):
                all_points.append([pt, next_angle, actual_scale])
    if rm_redundant:
        lone_points_list = []
        visited_points_list = []
        for point_info in all_points:
            point = point_info[0]
            scale = point_info[2]
            all_visited_points_not_close = True
            if len(visited_points_list) != 0:
                for visited_point in visited_points_list:
                    if ((abs(visited_point[0] - point[0]) < (width * scale / 100)) and (abs(visited_point[1] - point[1]) < (height * scale / 100))):
                        all_visited_points_not_close = False
                if all_visited_points_not_close == True:
                    lone_points_list.append(point_info)
                    visited_points_list.append(point)
            else:
                lone_points_list.append(point_info)
                visited_points_list.append(point)
        points_list = lone_points_list
    else:
        points_list = all_points
    color_filtered_list = []
    template_channels = cv2.mean(rgbtemplate)
    template_channels = np.array([template_channels[0], template_channels[1], template_channels[2]])
    for point_info in points_list:
        point = point_info[0]
        cropped_img = rgbimage[point[1]:point[1]+height, point[0]:point[0]+width]
        cropped_channels = cv2.mean(cropped_img)
        cropped_channels = np.array([cropped_channels[0], cropped_channels[1], cropped_channels[2]])
        diff_observation = cropped_channels - template_channels
        total_diff = np.sum(np.absolute(diff_observation))
        print(total_diff)
        if total_diff < rgbdiff_thresh:
            color_filtered_list.append([point_info[0],point_info[1],point_info[2]])
    return color_filtered_list

def calculateDistance(point1, point2):
    return math.sqrt(
        (point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2
    )


def main():
    img_bgr = cv2.imread('images/image_4a.jpg')
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    template_bgr = plt.imread('images/template_3a.jpg')
    template_rgb = cv2.cvtColor(template_bgr, cv2.COLOR_BGR2RGB)

    cropped_template_rgb = np.array(template_rgb)
    cropped_template_gray = cv2.cvtColor(cropped_template_rgb, cv2.COLOR_RGB2GRAY)
    height, width = cropped_template_gray.shape
    plt.imshow(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY))
    plt.show()
    plt.imshow(cropped_template_gray)
    plt.show()
    cv2.matchTemplate(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY), cropped_template_gray, cv2.TM_CCOEFF)

    points_list = invariantMatchTemplate(img_rgb, cropped_template_rgb, "TM_CCOEFF_NORMED", 0.8, 500, [0, 90], 10, [50, 150], 10, True)
    fig, ax = plt.subplots(1)
    ax.imshow(img_rgb)
    centers_list = []


    if len(points_list) == 3:
        # 3 punten we meten de afstand tussen elk van deze punten
        point1 = points_list[0][0]
        point2 = points_list[1][0]
        point3 = points_list[2][0]

        distance1 = calculateDistance(point1, point2)  #point 1 and 2
        distance2 = calculateDistance(point2, point3)  #point 2 and 3
        distance3 = calculateDistance(point3, point1)  #point 3 and 1

        maxDistance = max(distance1, distance2, distance3)

        if maxDistance == distance2:
            temp_point = point3
            point3 = point1
            point1 = temp_point
        if maxDistance == distance3:
            temp_point = point3
            point3 = point2
            point2 = temp_point

        difference1 = (point1[0] - point3[0], point1[1] - point3[1])
        difference2 = (point2[0] - point3[0], point2[1] - point3[1])

        point4 = (point3[0] + difference1[0] + difference2[0], point3[1] + difference1[1] + difference2[1])
        plt.scatter(point4[0] + width / 2, point4[1] + height / 2, s=20, color="red")


    for point_info in points_list:
        point = point_info[0]
        angle = point_info[1]
        scale = point_info[2]
        centers_list.append([point, scale])
        plt.scatter(point[0] + (width/2)*scale/100, point[1] + (height/2)*scale/100, s=20, color="red")
        plt.scatter(point[0], point[1], s=20, color="green")
        rectangle = patches.Rectangle((point[0], point[1]), width*scale/100, height*scale/100, color="red", alpha=0.50, label='Matched box')
        box = patches.Rectangle((point[0], point[1]), width*scale/100, height*scale/100, color="green", alpha=0.50, label='Bounding box')
        transform = mpl.transforms.Affine2D().rotate_deg_around(point[0] + width/2*scale/100, point[1] + height/2*scale/100, angle) + ax.transData
        rectangle.set_transform(transform)
        ax.add_patch(rectangle)
        ax.add_patch(box)
        plt.legend(handles=[rectangle, box])
    plt.show()
    fig2, ax2 = plt.subplots(1)
    ax2.imshow(img_rgb)
    for point_info in centers_list:
        point = point_info[0]
        scale = point_info[1]
        plt.scatter(point[0]+width/2*scale/100, point[1]+height/2*scale/100, s=20, color="red")
    plt.show()


if __name__ == "__main__":
    main()


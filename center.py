import cv2
import numpy as np
import math
from enum import Enum

class CenterPipeline:
    """
    An OpenCV pipeline generated by GRIP.
    """

    def __init__(self):
        """initializes all values to presets or None if need to be set
        """

        self.hsv_threshold_hue = [0.0, 255.0]
        self.hsv_threshold_saturation = [95.0, 255.0]
        self.hsv_threshold_value = [130.0, 255.0]
        self.hsv_threshold_output = None

        self.mask_mask = self.hsv_threshold_output
        self.mask_output = None

        self.find_contours_input = self.hsv_threshold_output
        self.find_contours_external_only = False
        self.find_contours_output = None

        self.filter_contours_contours = self.find_contours_output
        self.filter_contours_min_area = 100.0
        self.filter_contours_min_perimeter = 100.0
        self.filter_contours_min_width = 0
        self.filter_contours_max_width = 1000
        self.filter_contours_min_height = 0
        self.filter_contours_max_height = 1000
        self.filter_contours_solidity = [0, 100]
        self.filter_contours_max_vertices = 1000000
        self.filter_contours_min_vertices = 0
        self.filter_contours_min_ratio = 0
        self.filter_contours_max_ratio = 1000
        self.filter_contours_output = None

    def process(self, source0):
        """
        Runs the pipeline and sets all outputs to new values.
        """
        # Step HSV_Threshold0:
        self.hsv_threshold_input = source0
        self.hsv_threshold_output = self.hsv_threshold(self.hsv_threshold_input, self.hsv_threshold_hue, self.hsv_threshold_saturation, self.hsv_threshold_value)

        # Step Mask0:
        self.mask_input = source0
        self.mask_mask = self.hsv_threshold_output
        (self.mask_output) = self.mask(self.mask_input, self.mask_mask)

        # Step Find_Contours0:
        self.find_contours_input = self.hsv_threshold_output
        self.find_contours_output = self.find_contours(self.find_contours_input, self.find_contours_external_only)

        # Step Filter_Contours0:
        self.filter_contours_contours = self.find_contours_output
        (self.filter_contours_output) = self.filter_contours(self.filter_contours_contours, self.filter_contours_min_area, self.filter_contours_min_perimeter, self.filter_contours_min_width, self.filter_contours_max_width, self.filter_contours_min_height, self.filter_contours_max_height, self.filter_contours_solidity, self.filter_contours_max_vertices, self.filter_contours_min_vertices, self.filter_contours_min_ratio, self.filter_contours_max_ratio)


    @staticmethod
    def hsv_threshold(input, hue, sat, val):
        """Segment an image based on hue, saturation, and value ranges.
        Args:
            input: A BGR numpy.ndarray.
            hue: A list of two numbers the are the min and max hue.
            sat: A list of two numbers the are the min and max saturation.
            lum: A list of two numbers the are the min and max value.
        Returns:
            A black and white numpy.ndarray.
        """
        out = cv2.cvtColor(input, cv2.COLOR_BGR2HSV)
        return cv2.inRange(out, (hue[0], sat[0], val[0]),  (hue[1], sat[1], val[1]))

    @staticmethod
    def mask(input, mask):
        """Filter out an area of an image using a binary mask.
        Args:
            input: A three channel numpy.ndarray.
            mask: A black and white numpy.ndarray.
        Returns:
            A three channel numpy.ndarray.
        """
        return cv2.bitwise_and(input, input, mask=mask)

    @staticmethod
    def find_contours(input, external_only):
        """Sets the values of pixels in a binary image to their distance to the nearest black pixel.
        Args:
            input: A numpy.ndarray.
            external_only: A boolean. If true only external contours are found.
        Return:
            A list of numpy.ndarray where each one represents a contour.
        """
        if(external_only):
            mode = cv2.RETR_EXTERNAL
        else:
            mode = cv2.RETR_LIST
        method = cv2.CHAIN_APPROX_SIMPLE
        contours, heirarchy =cv2.findContours(input, mode=mode, method=method)
        return contours

    @staticmethod
    def filter_contours(input_contours, min_area, min_perimeter, min_width, max_width,
                        min_height, max_height, solidity, max_vertex_count, min_vertex_count,
                        min_ratio, max_ratio):
        """Filters out contours that do not meet certain criteria.
        Args:
            input_contours: Contours as a list of numpy.ndarray.
            min_area: The minimum area of a contour that will be kept.
            min_perimeter: The minimum perimeter of a contour that will be kept.
            min_width: Minimum width of a contour.
            max_width: MaxWidth maximum width.
            min_height: Minimum height.
            max_height: Maximimum height.
            solidity: The minimum and maximum solidity of a contour.
            min_vertex_count: Minimum vertex Count of the contours.
            max_vertex_count: Maximum vertex Count.
            min_ratio: Minimum ratio of width to height.
            max_ratio: Maximum ratio of width to height.
        Returns:
            Contours as a list of numpy.ndarray.
        """
        output = []
        for contour in input_contours:
            x,y,w,h = cv2.boundingRect(contour)
            if (w < min_width or w > max_width):
                continue
            if (h < min_height or h > max_height):
                continue
            area = cv2.contourArea(contour)
            if (area < min_area):
                continue
            if (cv2.arcLength(contour, True) < min_perimeter):
                continue
            hull = cv2.convexHull(contour)
            solid = 100 * area / cv2.contourArea(hull)
            if (solid < solidity[0] or solid > solidity[1]):
                continue
            if (len(contour) < min_vertex_count or len(contour) > max_vertex_count):
                continue
            ratio = (float)(w) / h
            if (ratio < min_ratio or ratio > max_ratio):
                continue
            output.append(contour)
        return output

def get_center_color(source):
    # run pipeline to detect center where test result is shown
    img = source.copy()
    p = CenterPipeline()
    p.process(img)

    # get the average bgr for the center
    float_bgr = list(cv2.mean(p.mask_output[:,:,:], p.mask_mask)[0:3])
    bgr_center = [round(x) for x in float_bgr]

    # get the average hsv for the center as well
    hsv_mat = cv2.cvtColor(np.uint8([[bgr_center]]), cv2.COLOR_BGR2HSV)
    hsv_center = hsv_mat[0][0]

    return p, np.array(bgr_center).astype(int), np.array(hsv_center).astype(int)


# # Ellipse fit -- no longer using
# ellipse = cv2.fitEllipse(p.filter_contours_output[0]) #print(ellipse)
# show_ellipse = img.copy()
# cv2.ellipse(show_ellipse,ellipse,(0,0,255),15)
# cv2.namedWindow('ellipse_fit', cv2.WINDOW_NORMAL)
# cv2.imshow('ellipse_fit',show_ellipse)

# # Normalize - no longer using, remap does a better job
# norm_bgr = cv2.normalize(input, None, 255, 0, cv2.NORM_MINMAX)
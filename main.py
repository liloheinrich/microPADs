import cv2
import numpy as np
import math
from enum import Enum
import os.path
import sys
from background import get_background_color
from center import get_center_color

def get_filename():
    if len(sys.argv) != 2:
        print("wrong amount of arguments. specify one image filename")
        exit()

    filename = sys.argv[1]
    lf = len(filename)
    if (not os.path.isfile(filename)) or (filename[lf-4:lf] != ".jpg"):
        print("filename invalid")
        exit()

    return filename

def remap(img, white, black):
    """ Remaps the pixel colors by assigning pixels lighter than "white" 
    to white, as dark as "black" to black, and everything inbetween on a 
    linear transformation. This can be used to clean up the image to 
    account for lighting, both exposure and tint/warmth. 

    For white, input the average paper background color. For black, input
    the darkest pixel found, either the minimum by channel or overall.
    """

    # splits image into channels, does linear transform, merges them back together
    im = img.copy()

    b = cv2.extractChannel(im, 0)
    b = cv2.multiply((b-black[0]), 255.0 / (white[0]-black[0]))
    b = cv2.min(b, 255)

    g = cv2.extractChannel(im, 1)
    g = cv2.multiply((g-black[1]), 255.0 / (white[1]-black[1]))
    g = cv2.min(g, 255)

    r = cv2.extractChannel(im, 2)
    r = cv2.multiply((r-black[2]), 255.0 / (white[2]-black[2]))
    r = cv2.min(r, 255)

    im = cv2.merge([b, g, r])
    return im

def level(img, bgr_background):
    """ 
    """

    # splits image into channels, does linear transform, merges them back together
    im = img.copy()
    max_bgr_background = max(bgr_background)

    b = cv2.extractChannel(im, 0)
    db = (max_bgr_background-bgr_background[0])
    b = b+db
    b = cv2.max(b, 0)

    g = cv2.extractChannel(im, 1)
    dg = (max_bgr_background-bgr_background[1])
    g = g+dg
    g = cv2.max(g, 0)

    r = cv2.extractChannel(im, 2)
    dr = (max_bgr_background-bgr_background[2])
    r = r+dr
    r = cv2.max(r, 0)

    im = cv2.merge([b, g, r])
    return im

def show_images(img, levelled, remapped, background_pipeline, center_pipeline):
    # original image
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.imshow('image',img)

    # should show less tinted looking, it is color-levelled
    cv2.namedWindow('levelled', cv2.WINDOW_NORMAL)
    cv2.imshow('levelled',levelled)

    # should show everything except background as masked
    cv2.namedWindow('background', cv2.WINDOW_NORMAL)
    cv2.imshow('background',background_pipeline.mask_output)

    # should show remapped image, cleaned up with actually white background
    cv2.namedWindow('remapped', cv2.WINDOW_NORMAL)
    cv2.imshow('remapped',remapped)

    # should show center in white, rest black
    cv2.namedWindow('hsv_threshold_output', cv2.WINDOW_NORMAL)
    cv2.imshow('hsv_threshold_output',center_pipeline.hsv_threshold_output)

    # should show only one contour around the center where the result is
    filter_contours = remapped.copy()
    cv2.drawContours(filter_contours, center_pipeline.filter_contours_output, -1, (0, 255, 0), 15)
    cv2.namedWindow('filter_contours', cv2.WINDOW_NORMAL)
    cv2.imshow('filter_contours',filter_contours)

    # should show image with mask over everything but the ph test
    cv2.namedWindow('mask_output', cv2.WINDOW_NORMAL)
    cv2.imshow('mask_output',center_pipeline.mask_output)

def get_ph(hue):
    # linear fit using slope of ph=7 / hue=22.5ish
    # slope = 7.0/22.5
    # ph = hue*slope

    # used desmos to very roughly estimate color->ph curve
    a = 1.55
    ph = math.log(hue)/math.log(a)
    return ph

def main():
    filename = get_filename()
    img = cv2.imread(filename)

    # run pipeline to pick out background color
    background_pipeline, bgr_background, hsv_background = get_background_color(img)
    print("bgr_background", bgr_background)
    print("hsv_background", hsv_background)

    # params to remap to. takes averge background color as white and darkest color as black
    # black = [img[:,:,0].min(), img[:,:,1].min(), img[:,:,2].min()]
    black = [0,0,0] # black, the dark color limit, doesn't matter so much
    white = bgr_background
    print("white", white)
    print("black", black)

    # cleans up image, accounts for lighting
    # remapped = remap(img, white, black)
    levelled = level(img, bgr_background)
    background_pipeline, bgr_background, hsv_background = get_background_color(levelled)
    print("bgr_background", bgr_background)
    print("hsv_background", hsv_background)
    remapped = remap(levelled, white, black)

    # finally calculates the result
    center_pipeline, bgr_center, hsv_center = get_center_color(remapped)
    print("bgr_center", bgr_center)
    print("hsv_center", hsv_center)

    # optionally show annotated images. helps for debugging
    show_images(img, levelled, remapped, background_pipeline, center_pipeline)

    ph = get_ph(hsv_center[0])
    print("\nEstimated pH value:", round(ph,1), "\n")

    cv2.waitKey(0)
    cv2.destroyAllWindows()

main()
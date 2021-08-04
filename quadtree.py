#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg
import numpy as np
import cv2
#import os

from operator import add
from functools import reduce

#quadtree ode ripped from https://medium.com/analytics-vidhya/transform-an-image-into-a-quadtree-39b3aa6e019a for the most part
#FUNCTIONS
def split4(image):
    """split image into 4 smaller ones, returns array of 2D subarrays"""
    #produces array of 2, split along one axis
    half_split = np.array_split(image, 2)
    
    #split into 2 along other axis for already split arrays
    res = map(lambda x: np.array_split(x, 2, axis=1), half_split)
    
    #reduces repeatedly applies the add function to the map, which just
    #puts the 4 subimages all into another array to return
    return reduce(add, res)

def concatenate4(nw, ne, sw, se):
    """puts 4 subimages together into whole image, returns single 2D list"""
    #concatenate just merges the arrays, we just do it on the two dimensions
    top = np.concatenate((nw, ne), axis=1)
    bottom = np.concatenate((sw, se), axis=1)
    return np.concatenate((top, bottom), axis=0)

def calculate_mean(img):
    """calculates the mean color of an image, returns np list"""
    #the image array has 2 dimensions and 2-4 channels for the color
    #we take the mean across the dimension axes 0 and 1 to get our color channel
    pixel = np.mean(img, axis=(0, 1)).astype(np.uint8)
    
    if(pixel.shape[0] == 3):
        #add transparency channel
        return np.append(pixel, 255)
    elif(pixel.shape[0] == 4):
        return pixel
    else:
        raise AttributeError("calculate_mean method requires RGB or RGBA images")

def checkEqual(myList):
    """checking if all the colors in an np array are equal, returns bool"""
    first=myList[0]
    #myList is 2D, so (x==first) returns a list of booleans
    #we check that all those booleans are satisfied
    #the outer all makes sure the alls all hold through the other dimension
    return all((x==first).all() for x in myList)


def outline(image):
    """turns border pixels to red if imag is at least 3x3"""
    red_bgr_trans = (255 * np.array([0.14117648, 0.10980392, 0.92941177, 1.0])).astype(np.uint8)
    red_bgr = (255 * np.array([0.14117648, 0.10980392, 0.92941177])).astype(np.uint8)

    white_bgr_trans = np.array([255,255,255,255]).astype(np.uint8)
    white_bgr = np.array([255,255,255]).astype(np.uint8)


    rows, cols = image.shape[0], image.shape[1]

    #do nothing if not at least 3x3
    if image.shape[0] < 3 or image.shape[1] < 3:
        return image

    #3 channel vs 4 channel
    if(image.shape[2] == 4):
        var = white_bgr_trans
    else:
        var = white_bgr
        
    image[0,:] = var
    image[rows-1,:] = var
    #technically doubles on the corners, but more readable
    image[:, 0] = var
    image[:,cols-1] = var

    return image

def isWhite(pixel):
    """tests if all channels in given pixel is 255, aka white"""
    return all(x == 255 for x in pixel[0:-2])

def isWhiteish(pixel):
    """tests if all channels in given pixel is greater than 128, aka whiteish"""
    #the last value in the array is transparency, we ignore it
    #print(pixel[:-1].shape)
    return np.all(pixel[:-1] >= 100)

    

#CLASS
class QuadTree:
    black_bgrt = (255 * np.array([0,0,0,1])).astype(np.uint8)
    white_bgrt = np.array([255,255,255,255]).astype(np.uint8)
    
    """implementation of quadtree in python using above methods"""
    def insert(self, img, limit, level = 0):
        """lets us insert into the quadtree, called recursively"""
        #level tells us how far into the tree we are
        self.level = level
        #self.mean = calculate_mean(img).astype(np.float64)
        #shape is a tuple, we call the first 2 entries to get the dimensions
        self.resolution = (img.shape[0], img.shape[1])
        self.isLeaf = True
        self.allSame = checkEqual(img)
        #if the image is not purely one color, we call for 4 subimages
        if not self.allSame and level < limit:
            split_img = split4(img)

            #no longer leaf cuz we got subimages
            self.isLeaf = False
            #btw, these vars arent out of scope, python is cool
            self.nw = QuadTree().insert(split_img[0], limit, level + 1)
            self.ne = QuadTree().insert(split_img[1], limit, level + 1)
            self.sw = QuadTree().insert(split_img[2], limit, level + 1)
            self.se = QuadTree().insert(split_img[3], limit, level + 1)
        else:
            self.img = img

        return self
    
    def get_image(self, level, img = None):
        """gives us the image from the quadtree"""
        if(self.isLeaf or self.level == level):
            if isWhiteish(calculate_mean(self.img)):
                if img is None: #if no insert image is provided, also holy fuck "is" works but "==" doesnt
                    return np.tile(QuadTree.white_bgrt, (self.resolution[0], self.resolution[1], 1))
                else:
                    #log new values into dict, else just pull from dict to save time
                    key = (hash(img.tobytes()),) + self.resolution
                    #print(key)
                    if key in GIF_dict:
                        return GIF_dict[key]
                    else:
                        #resize takes the dimensions in reverse, kinda annoying
                        resized_Gimage = cv2.resize(img, self.resolution[::-1], interpolation = cv2.INTER_AREA)
                        GIF_dict[key] = resized_Gimage
                        print("Logged with key: " + str(key))
                        return resized_Gimage
            else:
                #tile gives us a same dimension image with mean color
                #return np.tile(calculate_mean(self.img), (self.resolution[0], self.resolution[1], 1))
                return outline(np.tile(calculate_mean(self.img), (self.resolution[0], self.resolution[1], 1)))

        else:
            return concatenate4(
                self.nw.get_image(level, img), 
                self.ne.get_image(level, img),
                self.sw.get_image(level, img),
                self.se.get_image(level, img))



GIF_dict = {}

##    base = cv2.imread("badapple.png", cv2.IMREAD_UNCHANGED)
##    quadtree = QuadTree().insert(base,3)
##    #insert = cv2.imread("amogus.png", cv2.IMREAD_UNCHANGED)
##
##    print("START")
##    for i in GIF_array:
##        print(id(i))
##        
##    #cv2.imshow("test", quadtree.get_image(6))
##    quadtree.get_image(3, GIF_array[0])
##    print("[0] id is {}".format(id(GIF_array[0])))
##    quadtree.get_image(3, GIF_array[1])
##    print("[1] id is {}".format(id(GIF_array[1])))
##    quadtree.get_image(3, GIF_array[0])
##    print("[0] id is {}".format(id(GIF_array[0])))
##
##    print("END")
##    for i in GIF_array:
##        print(id(i))
##
##    print(len(GIF_dict))
##    print(GIF_dict.keys())


##    #reordered array tries to match top of animation to start of beat
##    GIF_array = folder_import("C:\\Users\\Gexin\\Desktop\\quadtree\\GIFFrames reordered")
##
##    GIF_dict = {}
##    #print(len(GIF_dict))
##    #print(GIF_dict.keys())
##
##    #frames per second when converting the frames to mp4
##    FPS = 30
##
##    #beats per second of song, synchronize GIF cycle to it
##    BPS = 138/60
##
##    #seconds per frame
##    SPF = 1/FPS
##
##    #seconds for each GIF image
##    seconds_per_gimage = 1/(BPS * GIF_array.shape[0])
##
##    #number of frames that fit into a single GIF image
##    spacing = seconds_per_gimage/SPF
##
##
##    
##    vidcap = cv2.VideoCapture("BadApple.mp4")
##
##    try:
##        #creating a folder named data
##        if not os.path.exists('Frames'):
##            os.makedirs('Frames')
##            
##    #if not created then raise error
##    except OSError:
##        print ('Error: Creating directory of Frames')
##
##    currentFrame = 0
##        
##    while(currentFrame < 200):
##        #read returns 2, ret is success bool and frame is numpy array
##        ret, frame = vidcap.read()
##
##        if ret:
##            #print(frame.dtype)
##            
##            quadtree = QuadTree().insert(frame,6)
##            fr = quadtree.get_image(6)
##            #:0>4 makes it so it pads 0s at the front to get a length of 4
##            name = "C:\\Users\\Gexin\\Desktop\\quadtree\\Frames\\frame{:0>4}.png".format(currentFrame)
##            print("Printing {}".format(currentFrame))
##
##            cv2.imwrite(name, fr)
##            
##            currentFrame += 1
##        else:
##            break
##    print(len(GIF_dict))
##    print(list(GIF_dict.keys()))
##
##    vidcap.release()
##    cv2.destroyAllWindows()
    
    



#ffmpeg command, NO CLUE how this works
#ffmpeg -framerate 30 -i frame%04d.png -c:v libx264 -pix_fmt yuv420p output.mp4

#merge audio and frames in mp4
#ffmpeg -i "output.mp4" -i "badapple.mp3" -shortest done.mp4
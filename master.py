import cProfile
import numpy as np
import cv2
import os
from quadtree import QuadTree


def folder_import(folder_path):
    """get images from folder into np array, returns 4 channels"""
    images = []

    for file in os.listdir(folder_path):
        image = cv2.imread(os.path.join(folder_path, file), cv2.IMREAD_UNCHANGED)

        # if no alpha channel in image, add one
        if image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image = np.concatenate([image[..., np.newaxis]]*3, axis=2)

        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
            image = np.concatenate([image[..., np.newaxis]]*3, axis=2)

        trans_layer = np.tile(255, (image.shape[0], image.shape[1], 1)).astype(np.uint8)

        image = np.concatenate((image, trans_layer), axis=2)

        # print(image.shape)
        # print(image)
        # cv2.imshow("shit", image)
        images.append(image)

    return np.asarray(images)


def BPM_matching_index(fr, space):
    """gets index of image that would fit in defined BPM"""
    """uses the current frame, the number of frames for a GIF image, and length of tuple"""
    return int((fr//space) % len(GIF_array))


def main():
    cur_frame = 0

    while cur_frame < 100:
        ret, frame = vidcap.read()

        if ret:
            quad = QuadTree(frame, 6)
            fr = quad.get_image(6, GIF_array[BPM_matching_index(cur_frame, spacing)])
            # :0>4 makes it so it pads 0s at the front to get a length of 4
            name = os.path.join(dirname, "Frames", "frame{:0>4}.png".format(cur_frame))
            print("Printing {}".format(cur_frame))

            cv2.imwrite(name, fr)

            cur_frame += 1
        else:
            break

    print("Done!")
    vidcap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    dirname = os.path.dirname(__file__)

    GIF_array = folder_import(os.path.join(dirname, 'GIFFrames'))

    # shitty hack, but for some reason array items' ids are really weird?
    GIF_array = tuple(GIF_array)

    # frames per second when converting the frames to mp4
    FPS = 30

    # beats per second of song, synchronize GIF cycle to it
    BPS = 138/60

    # seconds per frame
    SPF = 1/FPS

    # seconds for each GIF image
    seconds_per_gimage = 1/(BPS * len(GIF_array))

    # number of frames that fit into a single GIF image
    spacing = seconds_per_gimage/SPF

    vidcap = cv2.VideoCapture("BadApple.mp4")

    try:
        # creating a folder named data
        if not os.path.exists('Frames'):
            os.makedirs('Frames')

    # if not created then raise error
    except OSError:
        print('Error: Creating directory of Frames')

    cProfile.run('main()')

# ffmpeg command, NO CLUE how this works
# ffmpeg -framerate 30 -i frame%04d.png -c:v libx264 -pix_fmt yuv420p output.mp4

# merge audio and frames in mp4
# ffmpeg -i "output.mp4" -i "badapple.mp3" -shortest done.mp4

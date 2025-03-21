import argparse
import os
import shutil
import pygame
import alive_progress
import subprocess
import math
import random

FRAME_W = 1080 * 2
FRAME_H = 1920 * 2

ANGLE_MAX = 12
X_OFFSET_MAX = 0.075
Y_OFFSET_MAX = 0.1

IMG_OUTLAP = -0.075
IMG_W = math.cos(math.radians(ANGLE_MAX)) * FRAME_W * (1 + IMG_OUTLAP)
IMG_RATIO = 1.57
IMG_H = IMG_W * IMG_RATIO

SIDE_MIN_PADDING = 0.07
TOP_MIN_PADDING = 0.10
BOT_MIN_PADDING = TOP_MIN_PADDING * 2.0

MAX_W = IMG_W * (1 - 2 * SIDE_MIN_PADDING)
MAX_H = IMG_H * (1 - TOP_MIN_PADDING - BOT_MIN_PADDING)

RATIO = MAX_W / MAX_H


def blitRotate(surf, image, pos, originPos, angle):
    image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
    rotated_image = pygame.transform.rotozoom(image, angle, 1)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)
    surf.blit(rotated_image, rotated_image_rect)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input",  help="input folder",         required=True)
    parser.add_argument("-o", "--output", help="output folder",        required=True)
    parser.add_argument("-v", "--video",  help="save output as video", required=False, action="store_true")
    parser.add_argument("-f", "--fps",    help="video fps",            required=False, default=8, type=float)
    parser.add_argument("-n", "--name",   help="video filename",       required=False, default="output.mp4")
    parser.add_argument("-y", "--yes",    help="overwrite output",     required=False, action="store_true")
    
    args = parser.parse_args()
    # ------------------------------------------------------------------------ #

    try:
        shutil.rmtree(args.output)
    except FileNotFoundError:
        pass
    
    os.makedirs(args.output)

    # ------------------------------------------------------------------------ #
    ld = list(os.listdir(args.input))
    ld.sort()
    l = len(ld)

    wood = pygame.image.load("wood.png")
    wood = pygame.transform.smoothscale(wood, (FRAME_W, FRAME_H))

    def make_bg():
        running_frame = pygame.surface.Surface((FRAME_W, FRAME_H), pygame.SRCALPHA)
        running_frame.fill((0, 0, 0, 0))
        running_frame.blit(wood, (0, 0))
        return running_frame


    last_five = []

    with alive_progress.alive_bar(l) as bar:
        for filename in ld:
            img = pygame.image.load(os.path.join(args.input, filename))

            i = int(os.path.basename(filename).split(".")[0])

            out = pygame.surface.Surface((IMG_W, IMG_H), pygame.SRCALPHA)
            out.fill((0, 0, 0, 0))
            pygame.draw.rect(out, (255, 255, 255, 255), (0, 0, IMG_W, IMG_H), 0)

            img_ratio = img.get_width() / img.get_height()

            if img_ratio > RATIO:
                # wider ratio than target, background width = image width
                background_width = img.get_width()
                background_height = background_width / RATIO
            else:
                # taller ratio than target, background height = image height
                background_height = img.get_height()
                background_width = background_height * RATIO

            img_output = pygame.surface.Surface((background_width, background_height))
            img_output.fill((255, 255, 255))

            # center the image horizontally, top spacing 1/2 of bot (1/3 overall) 
            x_offset = (background_width - img.get_width()) / 2
            y_offset = (background_height - img.get_height()) / 3

            img_output.blit(img, (x_offset, y_offset))

            img_output = pygame.transform.smoothscale(img_output, (MAX_W, MAX_H))

            x_offset = IMG_W * SIDE_MIN_PADDING
            y_offset = IMG_H * TOP_MIN_PADDING

            out.blit(img_output, (x_offset, y_offset))

            angle = random.uniform(-ANGLE_MAX, ANGLE_MAX)
            x_offset = random.uniform(-X_OFFSET_MAX, X_OFFSET_MAX) * FRAME_W
            y_offset = random.uniform(-Y_OFFSET_MAX, Y_OFFSET_MAX) * FRAME_H
            x_pos = FRAME_W / 2 + x_offset
            y_pos = FRAME_H / 2 + y_offset

            bg = make_bg()

            last_five.append(bg)
            for i in range(len(last_five)):
                blitRotate(last_five[i], out, (x_pos, y_pos), (IMG_W / 2, IMG_H / 2), angle)

            last_five = last_five[-5:]

            output_filename = filename.split(".")[0] + ".png"
            pygame.image.save(last_five[0], os.path.join(args.output, output_filename))

            i += 1
            bar()
    # ------------------------------------------------------------------------ #

    # ------------------------------------------------------------------------ #
    if args.video:
        if args.output.endswith("/"): args.output = args.output[:-1]
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "error",
            "-framerate", str(args.fps),
            "-i", f"{args.output}/%03d.png",
            "-vf", "scale=iw:ih",
            "-c:v", "mjpeg",
            "-q:v", "0",
            "-y" if args.yes else "",
            args.name
        ]
        print(f"Running command: {' '.join(cmd)}")
        subprocess.run(cmd)
    # ------------------------------------------------------------------------ #




if __name__ == "__main__":
    main()

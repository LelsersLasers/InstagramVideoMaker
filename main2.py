import argparse
import os
import shutil
# import cv2
# import numpy as np
import pygame
# import json
import alive_progress
import subprocess
import math
import random

FRAME_W = 1080
FRAME_H = 1920

ANGLE_MAX = 12
X_OFFSET_MAX = 0.1
Y_OFFSET_MAX = 0.1

IMG_OUTLAP = 0.2
IMG_W = math.cos(math.radians(ANGLE_MAX)) * FRAME_W * (1 + IMG_OUTLAP)
IMG_RATIO = 1.57
IMG_H = IMG_W * IMG_RATIO

# SIDE_MIN_PADDING = 0.09
# TOP_MIN_PADDING = 0.12
# BOT_MIN_PADDING = TOP_MIN_PADDING * 2.0

SIDE_MIN_PADDING = 0.07
TOP_MIN_PADDING = 0.10
BOT_MIN_PADDING = TOP_MIN_PADDING * 2.0

MAX_W = IMG_W * (1 - 2 * SIDE_MIN_PADDING)
MAX_H = IMG_H * (1 - TOP_MIN_PADDING - BOT_MIN_PADDING)

RATIO = MAX_W / MAX_H

IMG_W = int(IMG_W)
IMG_H = int(IMG_H)

MAX_W = int(MAX_W)
MAX_H = int(MAX_H)

# pygame.init()
# window = pygame.display.set_mode((FRAME_W, FRAME_H))
# clock = pygame.time.Clock()

# def blitRotateCenter(surf, image, topleft, angle):

#     rotated_image = pygame.transform.rotate(image, angle)
#     new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

#     surf.blit(rotated_image, new_rect)

def blitRotate(surf, image, pos, originPos, angle):
    # img_a = image.convert_alpha()
    # img_a = pygame.surface.Surface(image.get_size(), pygame.SRCALPHA)
    # img_a.fill((0, 0, 0, 0))
    # img_a.blit(image, (0, 0))
    # img_a.set_at((0, 0), (0, 0, 0, 0))
    # img_a.set_colorkey((0, 0, 0))

    # Offset from pivot to center
    image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    
    # Rotated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # Rotated image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # Get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

    # rotate and blit the image
    surf.blit(rotated_image, rotated_image_rect)

# def blitRotate(surf, image, pos, originPos, angle):
#     # Create a surface with an alpha channel for the rotated image
#     # Calculate the new size of the rotated image to avoid clipping
#     w, h = image.get_size()
#     # The diagonal length is the maximum possible size after rotation
#     max_size = int((w**2 + h**2)**0.5)
#     rotated_surface = pygame.Surface((max_size, max_size), pygame.SRCALPHA)
#     rotated_surface.fill((0, 0, 0, 0))  # Fill with transparent color

#     # Blit the original image onto the center of the rotated surface
#     rotated_surface.blit(image, (max_size // 2 - w // 2, max_size // 2 - h // 2))

#     # Rotate the surface
#     rotated_image = pygame.transform.rotate(rotated_surface, angle)

#     # Calculate the new rect for the rotated image
#     rotated_rect = rotated_image.get_rect(center=pos)

#     # Blit the rotated image onto the target surface
#     surf.blit(rotated_image, rotated_rect.topleft)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input",  help="input folder",         required=True)
    parser.add_argument("-o", "--output", help="output folder",        required=True)
    # parser.add_argument("-t", "--text",   help="overlay text json",    required=True)
    parser.add_argument("-v", "--video",  help="save output as video", required=False, action="store_true")
    parser.add_argument("-f", "--fps",    help="video fps",            required=False, default=8, type=float)
    parser.add_argument("-n", "--name",   help="video filename",       required=False, default="output.mp4")
    # parser.add_argument("-r", "--ratio",  help="aspect ratio w:h",     required=False, default="9:16")
    
    args = parser.parse_args()
    # ------------------------------------------------------------------------ #

    try:
        shutil.rmtree(args.output)
    except FileNotFoundError:
        pass
    
    os.makedirs(args.output)

    # ratio_parts = args.ratio.split(":")
    # target_ratio = float(ratio_parts[0]) / float(ratio_parts[1])

    # ------------------------------------------------------------------------ #
    ld = list(os.listdir(args.input))
    ld.sort()
    l = len(ld)
    # target_index = int(0.75 * l)

    # all_widths = {}

    # with alive_progress.alive_bar(l) as bar:
    # 	for filename in ld:
    # 		img = cv2.imread(os.path.join(args.input, filename))
    # 		width = img.shape[1]
    # 		try:
    # 			all_widths[width] += 1
    # 		except KeyError:
    # 			all_widths[width] = 1
            
    # 		bar()
    # ------------------------------------------------------------------------ #

    # ------------------------------------------------------------------------ #
    # target_width = 0
    # running_count = 0
    # keys = sorted(list(all_widths.keys()))
    # for width in keys:
    # 	count = all_widths[width]
    # 	next_count = running_count + count
    # 	if running_count < target_index <= next_count:
    # 		target_width = width
    # 	running_count = next_count
    
    # print(f"Target width: {target_width}")
    # ------------------------------------------------------------------------ #

    # ------------------------------------------------------------------------ #
    # font = cv2.FONT_HERSHEY_SIMPLEX
    # font_size = int(0.00125 * target_width)
    # font_thickness = int(0.003 * target_width)
    # line_type = cv2.LINE_AA
    # font_color = (255, 255, 255)

    # x = int(0.05 * target_width)
    # y = lambda i: int(0.08 * target_width + (i + 0.4) * font_size * 30)

    # all_text = json.load(open(args.text))
    # current_text = {
    # 	"date": "",
    # 	"location": "",
    # 	"area": "",
    # 	"comment": ""
    # }

    # i = 0
    # random.shuffle(ld)

    wood = pygame.image.load("wood.png")
    wood = pygame.transform.scale(wood, (FRAME_W, FRAME_H))

    running_frame = pygame.surface.Surface((FRAME_W, FRAME_H), pygame.SRCALPHA)
    running_frame.fill((0, 0, 0, 0))
    running_frame.blit(wood, (0, 0))

     

    with alive_progress.alive_bar(l) as bar:
        for filename in ld:
            img = pygame.image.load(os.path.join(args.input, filename))

            i = int(os.path.basename(filename).split(".")[0])

            out = pygame.surface.Surface((IMG_W, IMG_H), pygame.SRCALPHA)
            # out.fill((0, random.randint(100, 255), random.randint(100, 255)))
            out.fill((0, 0, 0, 0))
            pygame.draw.rect(out, (255, 255, 255, 255), (0, 0, IMG_W, IMG_H), 0)

            img_ratio = img.get_width() / img.get_height()

            if img_ratio > RATIO:
                # wider ratio than target, background width = image width
                background_width = img.get_width()
                background_height = int(background_width / RATIO)
            else:
                # taller ratio than target, background height = image height
                background_height = img.get_height()
                background_width = int(background_height * RATIO)

            img_output = pygame.surface.Surface((background_width, background_height))
            img_output.fill((255, 255, 255))

            # center the image horizontally, top spacing 1/2 of bot (1/3 overall) 
            x_offset = (background_width - img.get_width()) // 2
            y_offset = (background_height - img.get_height()) // 3

            img_output.blit(img, (x_offset, y_offset))

            img_output = pygame.transform.scale(img_output, (MAX_W, MAX_H))

            x_offset = int(IMG_W * SIDE_MIN_PADDING)
            y_offset = int(IMG_H * TOP_MIN_PADDING)

            out.blit(img_output, (x_offset, y_offset))

            angle = random.uniform(-ANGLE_MAX, ANGLE_MAX)
            x_offset = random.uniform(-X_OFFSET_MAX, X_OFFSET_MAX) * FRAME_W
            y_offset = random.uniform(-Y_OFFSET_MAX, Y_OFFSET_MAX) * FRAME_H
            x_pos = FRAME_W // 2 + x_offset
            y_pos = FRAME_H // 2 + y_offset

            # t = pygame.surface.Surface((MAX_W, MAX_H))
            # t.blit(out, (0, 0))

            # blitRotate(running_frame, out, (x_pos, y_pos), (IMG_W // 2, IMG_H // 2), angle)
            # blitRotateAroundPoint(running_frame, out, (x_pos - IMG_W // 2, y_pos - IMG_H // 2), (IMG_W // 2, IMG_H // 2), angle)
            blitRotate(running_frame, out, (x_pos, y_pos), (IMG_W // 2, IMG_H // 2), angle)


            rot = pygame.transform.rotate(out, angle)
            rot_rect = rot.get_rect(center = (x_pos, y_pos))

            running_frame.blit(rot, rot_rect)


            output_filename = filename.split(".")[0] + ".jpg"
            pygame.image.save(running_frame, os.path.join(args.output, output_filename))

            # output_filename = f"{i:03}.jpg"
            # cv2.imwrite(os.path.join(args.output, output_filename), running_frame)

            i += 1
            bar()
    # ------------------------------------------------------------------------ #

    # ------------------------------------------------------------------------ #
    if args.video:
        if args.output.endswith("/"): args.output = args.output[:-1]
        # cmd_str = f"ffmpeg -framerate {args.fps} -i {args.output}/%03d.jpg {args.name}"
        # cmd_lst = cmd_str.split(" ")
        # subprocess.run(cmd_lst)
        cmd = [
            "ffmpeg",
            "-framerate", str(args.fps),
            "-i", f"{args.output}/%03d.jpg",
            "-vf", "scale=iw:ih",
            args.name
        ]
        subprocess.run(cmd)
    # ------------------------------------------------------------------------ #




if __name__ == "__main__":
    main()

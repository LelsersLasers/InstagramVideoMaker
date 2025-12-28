import argparse
import os
import shutil
import cv2
import numpy as np
# import json
import alive_progress
import subprocess
import random

OUTPUT_RATIO = 5 / 4 # height / width
OUTPUT_W = 1320
OUTPUT_H = int(OUTPUT_W * OUTPUT_RATIO)

IMG_MAX_W = OUTPUT_W * 0.35
IMG_MAX_H = IMG_MAX_W * 16/10

PADDING_PX = 20
# EXTRA_OVERLAP_PX = 16


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input",  help="input folder",         required=True)
    parser.add_argument("-o", "--output", help="output folder",        required=True)
    # parser.add_argument("-t", "--text",   help="overlay text json",    required=True)
    parser.add_argument("-v", "--video",  help="save output as video", required=False, action="store_true")
    parser.add_argument("-f", "--fps",    help="video fps",            required=False, default=8, type=float)
    parser.add_argument("-n", "--name",   help="video filename",       required=False, default="output.mp4")
    # parser.add_argument("-r", "--ratio",  help="aspect ratio w:h",     required=False, default="9:16")
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
    # 			all_widths[width] = 1
            
    # 		bar()
    # ------------------------------------------------------------------------ #

    
    # ------------------------------------------------------------------------ #
    output_img = np.zeros((OUTPUT_H, OUTPUT_W, 3), np.uint8)
    output_depth = np.zeros((OUTPUT_H, OUTPUT_W), np.float32)

    def scale_img(img):
        # Make the image fit within IMG_MAX_W and IMG_MAX_H while maintaining aspect ratio
        h, w = img.shape[:2]
        scale_w = IMG_MAX_W / w
        scale_h = IMG_MAX_H / h
        scale = min(scale_w, scale_h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        if scale < 1.0:
            interpolate_method = cv2.INTER_AREA
        else:
            interpolate_method = cv2.INTER_CUBIC
        resized_img = cv2.resize(img, (new_w, new_h), interpolation=interpolate_method)
        padded_img = np.zeros((new_h + 2 * PADDING_PX, new_w + 2 * PADDING_PX, 3), np.uint8)
        padded_img += 255  # white padding
        padded_img[PADDING_PX:PADDING_PX+new_h, PADDING_PX:PADDING_PX+new_w] = resized_img
        return padded_img
    
    def place_img(resized_img, position, output_img, output_depth):
        # Place the resized image onto the output image at the specified position
        # Increase the depth of the area where the image is placed by 1
        # Modify output_img and output_depth in place
        h, w = resized_img.shape[:2]
        x, y = position
        output_img[y:y+h, x:x+w] = resized_img
        # y_start = y + EXTRA_OVERLAP_PX + PADDING_PX
        # y_end = y + h - EXTRA_OVERLAP_PX - PADDING_PX
        # x_start = x + EXTRA_OVERLAP_PX + PADDING_PX
        # x_end = x + w - EXTRA_OVERLAP_PX - PADDING_PX
        # output_depth[y_start:y_end, x_start:x_end] += 1.0
        output_depth[y:y+h, x:x+w] += 1.0

    # def place_img(resized_img, position, output_img, output_depth):
    #     h, w = resized_img.shape[:2]
    #     x, y = position
    #     output_img[y:y+h, x:x+w] = resized_img

    #     cy = y + h // 2
    #     cx = x + w // 2
    #     radius = min(h, w) // 2 - (PADDING_PX)
    #     yy, xx = np.ogrid[:output_depth.shape[0], :output_depth.shape[1]]
    #     mask = (yy - cy) ** 2 + (xx - cx) ** 2 <= radius ** 2
    #     output_depth[mask] += 1
        
    #     # y_start = y + EXTRA_OVERLAP_PX + PADDING_PX
    #     # y_end = y + h - EXTRA_OVERLAP_PX - PADDING_PX
    #     # x_start = x + EXTRA_OVERLAP_PX + PADDING_PX
    #     # x_end = x + w - EXTRA_OVERLAP_PX - PADDING_PX
    #     # output_depth[y_start:y_end, x_start:x_end] += 1
    #     output_depth[y:y+h, x:x+w] += 1

    # def get_position(resized_img, output_depth):
    #     # Find a position to place the resized image where the depth is minimal
    #     # Image should fit entirely within output dimensions
    #     # Returns all the (top-left) positions that yield the minimal depth
    #     h, w = resized_img.shape[:2]
    #     min_depth = None
    #     best_positions = []
    #     for y in range(0, OUTPUT_H - h + 1):
    #         for x in range(0, OUTPUT_W - w + 1):
    #             region = output_depth[y:y+h, x:x+w]
    #             sum_region_depth = np.sum(region)
    #             if (min_depth is None) or (sum_region_depth < min_depth):
    #                 min_depth = sum_region_depth
    #                 best_positions = [(x, y)]
    #             elif sum_region_depth == min_depth:
    #                 best_positions.append((x, y))
    #     return best_positions

    def get_position(resized_img, output_depth):
        h, w = resized_img.shape[:2]

        # Bias towards center as a circular area
        center_y = OUTPUT_H // 2
        center_x = OUTPUT_W // 2
        Y, X = np.ogrid[:OUTPUT_H, :OUTPUT_W]
        distance_from_center = np.sqrt((Y - center_y) ** 2 + (X - center_x) ** 2)
        max_distance = np.sqrt((center_y) ** 2 + (center_x) ** 2)
        bias_c = (1 - (distance_from_center / max_distance)) * 0.5

        output_depth_wb = output_depth.copy()

        if np.min(output_depth) != 0.0:
            # print(".", end="", flush=True)
            print(f"Min: {np.min(output_depth):.4f}, Max: {np.max(output_depth):.4f}")
            output_depth_wb -= bias_c * np.max(output_depth)

        # Bias towards center as a rectangular area
        r_start_x = int(OUTPUT_W * 0.45)
        r_end_x   = int(OUTPUT_W * 0.55)
        r_start_y = int(OUTPUT_H * 0.35)
        r_end_y   = int(OUTPUT_H * 0.65)
        bias_r = np.zeros((OUTPUT_H, OUTPUT_W), np.float32)
        bias_r[r_start_y:r_end_y, r_start_x:r_end_x] = 0.9
        output_depth_wb -= bias_r

        print(f"After bias Min: {np.min(output_depth_wb):.4f}, Max: {np.max(output_depth_wb):.4f}")

        # output_depth_wb[output_depth_wb < 0] = 0.0

        show_max = np.max(output_depth_wb)
        if show_max <= 0:
            show_max = 1.0
        show_scaled = (output_depth_wb / show_max * 255).astype(np.uint8)
        show_scaled = cv2.resize(show_scaled, (OUTPUT_W // 2, OUTPUT_H // 2))
        cv2.imshow("depth", show_scaled)

        # Integral image (pad to simplify indexing)
        integral = np.pad(output_depth_wb, ((1, 0), (1, 0)), mode="constant")
        integral = integral.cumsum(axis=0).cumsum(axis=1)

        # Compute all window sums at once
        sums = (
            integral[h:, w:]
            - integral[:-h, w:]
            - integral[h:, :-w]
            + integral[:-h, :-w]
        )

        min_depth = np.min(sums)
        ys, xs = np.where(sums == min_depth)

        return list(zip(xs.tolist(), ys.tolist()))
    
    with alive_progress.alive_bar(l) as bar:
        for filename in ld:
            img = cv2.imread(os.path.join(args.input, filename))

            resized_img = scale_img(img)
            best_positions = get_position(resized_img, output_depth)
            chosen_position = random.choice(best_positions)
            place_img(resized_img, chosen_position, output_img, output_depth)

            output_filename = filename.split(".")[0] + ".png"
            cv2.imwrite(os.path.join(args.output, output_filename), output_img)

            # ---------------------------------------------------------------- #
            scaled_down_output = cv2.resize(output_img, (OUTPUT_W // 2, OUTPUT_H // 2))
            cv2.imshow("output", scaled_down_output)
            cv2.waitKey(1)
            # ---------------------------------------------------------------- #

            bar()
    # ------------------------------------------------------------------------ #

    # ------------------------------------------------------------------------ #
    if args.video:
        if args.output.endswith("/"): args.output = args.output[:-1]
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-framerate", str(args.fps),
            "-i", f"{args.output}/%03d.png",
            "-vf", "scale=iw:ih",
            # "-c:v", "libx264",
            # "-crf", "0",
            # "-preset", "veryslow",
            "-y" if args.yes else "",
            args.name
        ]
        print("Running command:", " ".join(cmd))
        subprocess.run(cmd)
    # ------------------------------------------------------------------------ #




if __name__ == "__main__":
    main()

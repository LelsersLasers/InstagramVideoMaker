import argparse
import os
import shutil
import cv2
import numpy as np
# import json
import alive_progress
import subprocess
import random


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

	with alive_progress.alive_bar(l) as bar:
		for filename in ld:
			# i = filename.split(".")[0]
			# try:
			# 	current_text.update(all_text[i])
			# except KeyError:
			# 	pass


			img = cv2.imread(os.path.join(args.input, filename))


			# i = int(os.path.basename(filename).split(".")[0])

			# skip the top 84, bottom 84, left 2, and right 1 pixels
			img_output = img[84:-84, 2:-1, :]


			# img_ratio = img.shape[1] / img.shape[0] # width / height


			# if img_ratio > target_ratio:
			# 	# wider ratio than target, background width = image width
			# 	background_width = img.shape[1]
			# 	background_height = int(background_width / target_ratio)
			# else:
			# 	# taller ratio than target, background height = image height
			# 	background_height = img.shape[0]
			# 	background_width = int(background_height * target_ratio)

			# img_output = np.zeros((background_height, background_width, 3), np.float32)
			# img_output += 255 # white background

			# # center the image
			# x_offset = (background_width - img.shape[1]) // 2
			# y_offset = (background_height - img.shape[0]) // 2

			# img_output[y_offset:y_offset + img.shape[0], x_offset:x_offset + img.shape[1]] = img


			# resize_ratio = target_width / background_width
			# img_output = cv2.resize(img_output, (target_width, int(background_height * resize_ratio)))


			# cv2.putText(img_output, current_text["date"],     (x, y(0)), font, font_size, font_color, font_thickness, line_type)
			# cv2.putText(img_output, current_text["location"], (x, y(1)), font, font_size, font_color, font_thickness, line_type)
			# cv2.putText(img_output, current_text["area"],     (x, y(2)), font, font_size, font_color, font_thickness, line_type)
			# cv2.putText(img_output, current_text["comment"],  (x, y(3)), font, font_size, font_color, font_thickness, line_type)


			# img_output = img

			output_filename = filename.split(".")[0] + ".png"
			# output_filename = f"{i:03}.jpg"
			cv2.imwrite(os.path.join(args.output, output_filename), img_output)

			# i += 1
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
		subprocess.run(cmd)
	# ------------------------------------------------------------------------ #




if __name__ == "__main__":
	main()

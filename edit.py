import argparse
import os
import cv2
import numpy as np
import json
import alive_progress


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--folder", help="input folder", required=True)
	parser.add_argument("-o", "--output", help="output folder", required=True)
	parser.add_argument("-t", "--text", help="overlay text json", required=True)
	args = parser.parse_args()


	target_ratio = 9 / 19.5 # width / height

	try:
		os.makedirs(args.output)
	except FileExistsError:
		pass

	all_text = json.load(open(args.text))
	current_text = {
		"date": "",
		"country": "",
		"city": "",
		"area": ""
	}

	ld = list(os.listdir(args.folder))
	ld.sort()
	l = len(ld)
	target_index = int(0.75 * l)

	all_widths = {}

	with alive_progress.alive_bar(l) as bar:
		for filename in ld:
			img = cv2.imread(os.path.join(args.folder, filename))
			width = img.shape[1]
			try:
				all_widths[width] += 1
			except KeyError:
				all_widths[width] = 1
			
			bar()

	target_width = 0
	running_count = 0
	keys = sorted(list(all_widths.keys()))
	with alive_progress.alive_bar(len(all_widths)) as bar:
		for width in keys:
			count = all_widths[width]
			next_count = running_count + count
			if running_count < target_index <= next_count:
				target_width = width
			running_count = next_count

			bar()

	font = cv2.FONT_HERSHEY_SIMPLEX
	font_size = int(0.00125 * target_width)
	font_thickness = int(0.003 * target_width)
	line_type = cv2.LINE_AA
	font_color = (255, 255, 255)

	x = int(0.015 * target_width)
	y = lambda i: int(0.025 * target_width + (i + 0.4) * font_size * 30)

	with alive_progress.alive_bar(l) as bar:
		for filename in ld:
			i = filename.split(".")[0]
			try:
				current_text.update(all_text[i])
			except KeyError:
				pass

			img = cv2.imread(os.path.join(args.folder, filename))

			img_ratio = img.shape[1] / img.shape[0] # width / height

			if img_ratio > target_ratio:
				# wider ratio than target, background width = image width
				background_width = img.shape[1]
				background_height = int(background_width / target_ratio)
			else:
				# taller ratio than target, background height = image height
				background_height = img.shape[0]
				background_width = int(background_height * target_ratio)

			img_output = np.zeros((background_height, background_width, 3), np.float32)

			# center the image
			x_offset = (background_width - img.shape[1]) // 2
			y_offset = (background_height - img.shape[0]) // 2

			img_output[y_offset:y_offset + img.shape[0], x_offset:x_offset + img.shape[1]] = img

			resize_ratio = target_width / background_width
			img_output = cv2.resize(img_output, (target_width, int(background_height * resize_ratio)))

			cv2.putText(img_output, current_text["date"],    (x, y(0)), font, font_size, font_color, font_thickness, line_type)
			cv2.putText(img_output, current_text["country"], (x, y(1)), font, font_size, font_color, font_thickness, line_type)
			cv2.putText(img_output, current_text["city"],    (x, y(2)), font, font_size, font_color, font_thickness, line_type)
			cv2.putText(img_output, current_text["area"],    (x, y(3)), font, font_size, font_color, font_thickness, line_type)

			output_filename = filename.split(".")[0] + ".jpg"
			cv2.imwrite(os.path.join(args.output, output_filename), img_output)

			bar()




if __name__ == "__main__":
	main()
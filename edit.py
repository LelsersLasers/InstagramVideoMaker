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


			font = cv2.FONT_HERSHEY_SIMPLEX
			font_size = int(0.0005 * background_height)
			line_type = cv2.LINE_AA

			x = int(0.01 * background_width)
			y = lambda i: int(0.02 * background_width + (i + 0.4) * font_size * 30)

			print(font_size, x, y(0))

			cv2.putText(img_output, current_text["date"],    (x, y(0)), font, font_size, (255, 255, 255), 2, line_type)
			cv2.putText(img_output, current_text["country"], (x, y(1)), font, font_size, (255, 255, 255), 2, line_type)
			cv2.putText(img_output, current_text["city"],    (x, y(2)), font, font_size, (255, 255, 255), 2, line_type)
			cv2.putText(img_output, current_text["area"],    (x, y(3)), font, font_size, (255, 255, 255), 2, line_type)

			cv2.imwrite(os.path.join(args.output, filename), img_output)

			bar()




if __name__ == "__main__":
	main()
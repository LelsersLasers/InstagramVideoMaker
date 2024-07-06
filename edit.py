import argparse
import os
import cv2
import json
import alive_progress


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--folder", help="input folder", required=True)
	parser.add_argument("-o", "--output", help="output folder", required=True)
	parser.add_argument("-t", "--text", help="overlay text json", required=True)
	args = parser.parse_args()

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
			font = cv2.FONT_HERSHEY_SIMPLEX

			# cv2.putText(img, current_text["date"], (x, y(0)), font, font_size, (255, 255, 255), 2, line_type)
			# cv2.putText(img, current_text["country"], (x, y(1)), font, font_size, (255, 255, 255), 2, line_type)
			# cv2.putText(img, current_text["city"], (x, y(2)), font, font_size, (255, 255, 255), 2, line_type)
			# cv2.putText(img, current_text["area"], (x, y(3)), font, font_size, (255, 255, 255), 2, line_type)

			cv2.putText(img, current_text["date"], (15, 40), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
			cv2.putText(img, current_text["country"], (15, 70), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
			cv2.putText(img, current_text["city"], (15, 100), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
			cv2.putText(img, current_text["area"], (15, 130), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

			cv2.imwrite(os.path.join(args.output, filename), img)

			bar()




if __name__ == "__main__":
	main()
import os
import argparse
import alive_progress


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input",     help="input folder",            required=True)
    parser.add_argument("-e", "--extension", help="extension to convert to", required=False, default="jpeg")
    
    args = parser.parse_args()

    ld = list(os.listdir(args.input))
    l = len(ld)

    with alive_progress.alive_bar(l) as bar:
        for filename in ld:
            base_name, ext = os.path.splitext(filename)
            if ext != f".{args.extension}":
                os.rename(os.path.join(args.input, filename), os.path.join(args.input, f"{base_name}.{args.extension}"))
            bar()
    
    print("Done")


if __name__ == "__main__":
    main()
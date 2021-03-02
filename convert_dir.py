import os
import argparse
from shutil import rmtree, move
import converter
from tqdm import tqdm
from converter.util import find


# moves all .m4a files to Automatically Add to Music Folder
# input: str path to find .m4a files in
# output: None
def move_to_auto(search_path, auto_path):
    pathlist = find("m4a", dir=search_path)
    for path in tqdm(pathlist, unit="files"):
        filename = path.split("/")[-1]
        move(path, f"{auto_path}/{filename}")


def convert_all(dir, auto_folder, skip_conv=False):
    if skip_conv:
        print("skipping conversion for existing files")
    cues = converter.get_cues(dir)
    if len(cues) > 0:
        converter.split_cues(cues, remove_flac=True)

    print("\nConverting files to ALAC...\n")
    converter.convert_dir(dir, threads=8, skip_conv=skip_conv)
    print("\nValidating metadata...\n")
    converter.validate_dir(dir)
    print(f"\nMoving files to {auto_folder}...\n")
    move_to_auto(dir, auto_folder)

    # deletes the flac files
    remaining_dirs = os.listdir(dir)
    remaining_dirs.remove(".DS_Store")
    if remaining_dirs:
        for file in remaining_dirs:
            if os.path.isdir(dir + "/" + file):
                rmtree(dir + "/" + file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert all files to alac and move to folder"
    )
    parser.add_argument(
        "-nd",
        "--no-delete",
        help="Do not delete the files after conversion",
        action="store_true",
    )
    parser.add_argument(
        "-nm",
        "--no-move",
        help="Do not move the files after conversion",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--skip-converted",
        help="Don't overwrite files, skip if they exist.",
        action="store_true",
    )

    parser.add_argument("dir", help="The directory to convert.")
    parser.add_argument(
        "auto_folder",
        help="The Automatically Add to Music folder in the "
        + "macOS music library. The files will be moved here "
        + "after conversion.",
    )
    args = parser.parse_args()

    convert_all(args.dir, args.auto_folder, skip_conv=args.skip_converted)

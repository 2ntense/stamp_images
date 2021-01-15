import os
import shutil
import subprocess
from datetime import datetime
from dataclasses import dataclass
from PIL import Image, ImageFont, ImageDraw

root_dir = r"C:\Users\stefa\Desktop\mush\pics"


@dataclass
class Camera:
    name: str
    res: tuple

    def dir(self):
        return os.path.join(root_dir, self.name)

    def stamped_dir(self):
        return os.path.join(self.dir(), "stamped")


def add_time(path, dt: datetime, index):
    output_dir = os.path.join(os.path.dirname(path), "stamped")
    os.makedirs(output_dir, exist_ok=True)
    with open(path, "rb") as f:
        im = Image.open(f)
        w, h = im.size
        font = ImageFont.truetype("./FiraCode-Regular.ttf", size=200)
        text = dt.strftime("%H:%M\n%Y-%m-%d")
        dr = ImageDraw.Draw(im)
        dr.multiline_text(xy=(w * 0.025, h - h * 0.025), text=text, anchor="ld", font=font, fill="black", spacing=50)
        dr.text(xy=(w - w * 0.025, h - h * 0.025), text=str(index), anchor="rd", font=font, fill="black")
        output_file = os.path.join(output_dir, f"{index}.jpg")
        im.save(output_file)


def get_all_jpg_in_dir(path):
    out = (x for x in os.scandir(path) if x.is_file and x.name.endswith(".jpg"))
    return out


def sort_images_by_cam(path: str, cam: Camera):
    os.makedirs(cam.dir(), exist_ok=True)
    for jpg in get_all_jpg_in_dir(path):
        with open(jpg.path, "rb") as f:
            im = Image.open(f)
            res = im.size
        if res == cam.res:
            shutil.move(jpg.path, cam.dir())


def hourly_list(path):
    image_list = list()
    for e in get_all_jpg_in_dir(path):
        with open(e.path, "rb") as f:
            im = Image.open(f)
            try:
                exif_dt = im.getexif()[36867]
            except KeyError:
                continue
        dt_fmt = "%Y:%m:%d %H:%M:%S"
        dt = datetime.strptime(exif_dt, dt_fmt)
        if dt.minute == 0:
            image_list.append((e.path, dt))
    image_list.sort(key=lambda x: x[1])
    return image_list


def check_hourly_list(image_list):
    h = image_list[0][1].hour
    for e in image_list[1:]:
        if h == 23:
            h = 0
        else:
            h += 1
        if e[1].hour != h:
            print(f"Error hour {h} missing!")
            return False
    return True


def create_vid(path):
    input_images = os.path.join(path, "%d.jpg")
    output_file = os.path.join(path, "out.mp4")
    ffmpeg_bin = r"C:\Users\stefa\Documents\Apps\ffmpeg-4.3.1-2021-01-01-full_build\bin\ffmpeg.exe"
    subprocess.run(
        f"{ffmpeg_bin} -y -f image2 -framerate 1 -i {input_images} -r 30 -s 3840x2160 -pix_fmt yuv420p -c:v hevc {output_file}")


def stamp_images(path):
    img_list = hourly_list(path)
    if not check_hourly_list(img_list):
        exit(0)
    for i, e in enumerate(img_list, 1):
        add_time(e[0], e[1], i)


def main():
    main_cam = Camera("main", (4656, 3492))
    wide_cam = Camera("wide", (4160, 3120))

    sort_images_by_cam(root_dir, main_cam)
    sort_images_by_cam(root_dir, wide_cam)

    stamp_images(main_cam.dir())
    stamp_images(wide_cam.dir())

    create_vid(main_cam.stamped_dir())
    create_vid(wide_cam.stamped_dir())


if __name__ == "__main__":
    main()

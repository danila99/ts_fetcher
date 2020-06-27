import argparse
import concurrent.futures
import os
import re
import shutil
import urllib.request

MAX_FORESEEABLE_INDEX = 10000
MAX_WORKERS = 32


class VideoChunk(object):
    def __init__(self, base_url, postfix_url, pad):
        self.base = base_url
        self.postfix = postfix_url
        self.pad = pad

    def url(self, i):
        return f"{self.base}{str(i).zfill(self.pad)}.ts{self.postfix}"

    def exists(self, i):
        url = self.url(i)
        req = urllib.request.Request(url, method="HEAD")
        print(f"looking for: {url}...", end=" ")
        try:
            with urllib.request.urlopen(req) as response:
                print("found")
                return response.getcode() == 200
        except Exception as ex:
            print(f"not found: {ex}")
            return False

    def get_max_index(self, left, right):
        while left + 1 < right:
            index = left + (right - left) // 2
            if self.exists(index):
                left = index
            else:
                right = index

        if self.exists(left + 1):
            return left + 1
        else:
            return left

    def save_locally(self, base_folder, i):
        file_name = os.path.join(base_folder, f"{i}.ts")
        url = self.url(i)
        # TODO: treat unexpected HTTP exceptions here
        with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
            # print(f"writing to: {file_name}...")
            shutil.copyfileobj(response, out_file)
            return f"done: {file_name}"


def analyze_url(full_url):
    if "{i.ts}" in full_url:
        base, *postfix = url.split("{i.ts}")
        return base, postfix[0] if postfix else ""
    else:
        regex = r"(?P<url>.+?)\d+\.ts(?P<url_postfix>.*)"
        matches = re.search(regex, full_url)
        return matches.group("url"), matches.group("url_postfix")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download all *.ts files for remote video resource")
    parser.add_argument("folder", help="destination folder", default=".", type=str)
    parser.add_argument("url", help="URL pattern for video chunks, example: http://any.com/any/any0.ts?any. " \
                                    "'0.ts' should be present, or replace it with '{i.ts}' stub where '{index}.ts' " \
                                    "part of the url is", type=str)
    parser.add_argument("-p", "--pad",
                        help="pad index with zeros, i.e. use -p 5 to generate 00001.ts in a video chunk url",
                        type=int,
                        default=0)
    args = parser.parse_args()

    if not os.path.exists(args.folder):
        os.makedirs(args.folder)

    base_folder = args.folder
    base_url, url_postfix = analyze_url(args.url)
    video_chunk = VideoChunk(base_url, url_postfix, args.pad)

    print(f"will download from: {video_chunk.url(1)}")
    print(f"will write to: {base_folder}")

    if not video_chunk.exists(1):
        raise Exception(f"no resource at {video_chunk.url(1)}")

    max_index = video_chunk.get_max_index(1, MAX_FORESEEABLE_INDEX)
    all_indices = list(range(1, max_index + 1))
    print(f"max index found: {max_index}")

    # fetching files from the website
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {executor.submit(video_chunk.save_locally, base_folder, i): i for i in all_indices}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                status = future.result()
                print(status)
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))

    # saving the result file list txt
    file_list_name = os.path.join(base_folder, "_filelist.txt")
    print(f"creating {file_list_name}...")
    with open(file_list_name, "w") as text_file:
        for index in all_indices:
            print(f"file '{os.path.join(base_folder, str(index))}.ts'", file=text_file)

    print("done. Now proceed with the following shell command:")
    print(f"> ffmpeg -safe 0 -f concat -i {os.path.join(base_folder, '_filelist.txt')}"
          f" -c copy {os.path.join(base_folder, 'output.mp4')}")

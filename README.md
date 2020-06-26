# Ts_fetcher
Typically, hosted videos are spilt into *.ts video chunks and are served
to a browser in a rapid succession one after another. This makes it
somewhat harder to download all of them manually.

Ts_fetcher is a Python based script to download all *.ts chunks
in the provided URL and save them as files to the local drive.

Saved video files could be easily assembled back into a full video with the
free [ffmpeg](https://ffmpeg.org/) tool. Ts_fetcher will helpfully
prompt the needed ffmpeg command, but make sure you've
[installed it](https://ffmpeg.org/download.html) first.

Start using with:

`$ python ts_fetcher.py --help`
# Ts_fetcher
Typically, hosted videos are spilt into *.ts video chunks and are served
to a browser in a rapid succession one after another. This makes it
somewhat harder to download all of them manually.

Ts_fetcher is a Python based script, that will search for all *.ts files
in the provided URL and save found files to the local drive.

Saved video chunks could be easily assembled back into full video with a
free [ffmpeg](https://ffmpeg.org/) tool. Ts_fetcher will helpfully
prompt the needed ffmpeg command, but make sure you've
[installed it](https://ffmpeg.org/download.html) first.

Start using with:

`$ python ts_fetcher.py --help`
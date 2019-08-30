# -*- coding: utf-8 -*-

"""Request continuous waveform data from NIED F-net.
"""

import io
import os
import re
import sys
import requests
import datetime


class Client():
    """Client for F-net server."""
    FNET = "http://www.fnet.bosai.go.jp/auth/dataget/"
    DATAGET = FNET + "cgi-bin/dataget.cgi"
    DATADOWN = FNET + "dlDialogue.php"

    def __init__(self, user, password, timeout=120):
        self.session = requests.Session()
        self.session.auth = (user, password)
        self.timeout = timeout

    def get_waveform(
            self,
            starttime,
            end='time', # or duration
            endtime=datetime.date.today(), # daufult endtime, just to initialize endtime
            duration_in_seconds=0,  # daufult duration_in_seconds, just to initialize duration_in_seconds
            format = "SAC",#"SEED",
            station = "ALL",
            component = "LH?",
            time="UT",
            path_save='./',  # where the download zipfile will be saved
            # you can use the proxy running on local PC, e.g {'http': 'http://127.0.0.1:1080','https':'https://127.0.0.1:1080'}
            proxies = {},
            filename=None,
    ):
        """Get waveform data from NIED F-net."""

        if starttime.year < 1995:
            raise ValueError("No data avaiable before year 1995.")

        # BH? => BHX
        component = component.replace("?", "X")

        if end == 'time':
            data0 = {
                "end": "time",
                "e_year": endtime.strftime("%Y"),
                "e_month": endtime.strftime("%m"),
                "e_day": endtime.strftime("%d"),
                "e_hour": endtime.strftime("%H"),
                "e_min": endtime.strftime("%M"),
                "e_sec": endtime.strftime("%S"),
            }
        elif end == 'duration':
            data0 = {
                "end": "duration",
                "sec": duration_in_seconds,
            }

        data1 = {
            "s_year": starttime.strftime("%Y"),
            "s_month": starttime.strftime("%m"),
            "s_day": starttime.strftime("%d"),
            "s_hour": starttime.strftime("%H"),
            "s_min": starttime.strftime("%M"),
            "s_sec": starttime.strftime("%S"),
            "format": format,
            "archive": "zip",  # alawys use ZIP format
            "station": station,
            "component": component,
            "time": time,
        }

        data = data0.copy()
        data.update(data1)
        # print(data)
        r = self.session.post(self.DATAGET, auth=self.session.auth, data=data, proxies=proxies)
        if r.status_code == 401:  # username is right, password is wrong
            sys.exit("Unauthorized! Please check your username and password!")
        elif r.status_code == 500:  # internal server error, or username is wrong
            sys.exit("Internal server error! Or you're using the wrong username!")
        elif r.status_code != 200:
            sys.exit("Something wrong happened! Status code = %d" % (r.status_code))
        print(r)

        # extract data id
        m = re.search(r"dataget\.cgi\?data=(NIED_\d+\.zip)&", r.text)

        if m:
            data_id = m.group(1)
        else:
            sys.stderr.write(r.text)
            sys.exit("Error in parsing HTML!")

        # check if data preparation is done
        r = self.session.get(self.DATAGET + "?data=" + data_id,
                             auth=self.session.auth, proxies=proxies)
        if "Our data server is very busy now." in r.text:
            sys.stderr.write("Something wrong with the F-net server.\n")
            return None
        if "Your request has been rejected because the total file size exceeds 50 MB." in r.text:
            sys.stderr.write("Your request has been rejected because the total file size exceeds 50 MB.")
            return None


        # download waveform data (.zip)
        url_down = self.DATADOWN + "?_f=" + data_id
        path = path_save + data_id
        print('Download URL: ',url_down, '\nFile PATH: ', path )
        print("Data is downloading...")
        r = self.session.get(url_down, auth=self.session.auth, stream=True, proxies=proxies)
        if "Could not open your requested file" in r.text:
            sys.stderr.write(r.text + "\n")
            sys.stderr.write(
                "Possible reasons:\n"
                "1. Something wrong happened to the Fnet server.\n"
                "2. No data avaiable in your requested time range.\n"
                "3. Multiple requests at the same time.\n"
            )
            return None

        with open(path, 'wb') as f:
            f.write(r.content)
        print('File has been saved to ', path)
        # if not filename:
        #     filename = starttime.strftime("%Y%m%d%H%M%S") + ".SAC"#".SEED"
        # dirname = os.path.dirname(filename)
        #
        # z = zipfile.ZipFile(io.BytesIO(r.content))
        # for f in z.filelist:
        #     ext = os.path.splitext(f.filename)[1]
        #     if ext.lower() == '.sac' and f.file_size != 0:
        #         if not os.path.exists(dirname):
        #             os.makedirs(dirname, exist_ok=True)
        #         f.filename = filename
        #         z.extract(f)
        #         return f.filename
        #     else:
        #         return None

FnetPy is a Python package to request seismic waveform data from `NIED F-net <http://www.fnet.bosai.go.jp>`_.

Install
=======

::

    pip install https://github.com/seisman/FnetPy/archive/master.zip

Usage
=====
   Download waveform data by start time and duration :
.. code-block::

   from FnetPy import Client
   from datetime import datetime

   starttime = datetime(2011, 1, 2, 5, 10)
   duration_time = 300
   client = Client(username, password)
   client.get_waveform(starttime=starttime, end="duration", duration_in_seconds=duration_time)
====
   Download waveform data by start time and duration :
.. code-block::

   from FnetPy import Client
   from datetime import datetime

   starttime = datetime(2011, 1, 2, 5, 10, 0)
   endtime = datetime(2011, 1, 15, 0, 0, 0)
   client = Client(username, password)
   client.get_waveform(starttime=starttime, end="time", endtime=endtime)

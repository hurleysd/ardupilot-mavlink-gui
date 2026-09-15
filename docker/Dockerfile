FROM python:3.12-slim-bookworm

RUN apt-get update \
   && apt-get install -y \
      python3-tk \
   && rm -rf /var/lib/apt/lists/*

WORKDIR /ardupilot-mavlink-gui

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

#############################################################################
# Sean Hurley (seandhurley@live.com)                                        #
# September 15, 2026                                                        #
#############################################################################
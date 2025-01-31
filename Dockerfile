FROM alt:p10
RUN apt-get update && apt-get install -y python3 --fix-missing
RUN apt-get install -y python3-module-pip python3-modules-sqlite3
WORKDIR /ScheduleNNTCBot
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
CMD ["/usr/bin/python3", "main.py"]

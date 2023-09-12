FROM apache/airflow:2.7.0
COPY . .
COPY requirement.txt /
RUN pip install --no-cache-dir  -r /requirement.txt
USER root
RUN sudo apt-get update
RUN sudo apt-get install wget
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add - 
RUN sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN sudo apt-get update
RUN sudo apt-get install google-chrome-stable -y
RUN apt-get update
RUN sudo apt-get install vim -y
USER airflow
RUN echo "alias ll='ls --color=auto -alF'" >> ~/.bashrc
RUN source ~/.bashrc
VOLUME /home/ubuntu/airflow

FROM ubuntu:20.04

# Install dependencies
RUN apt update
RUN apt install python3-pip net-tools wget mrtparse vim nano -y && \
    rm -rf /var/lib/apt/lists/* && apt clean
RUN pip install exabgp==4.2.25

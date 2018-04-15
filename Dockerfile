FROM python:3

RUN set -ex \
    && mkdir /usr/local/src/twitter_logger

COPY \
      MANIFEST.in \
      requirements.txt \
      setup.cfg \
      setup.py \
    /usr/local/src/twitter_logger/

COPY twitter_logger /usr/local/src/twitter_logger/twitter_logger

RUN set -ex \
    && cd /usr/local/src/twitter_logger \
    && pip install -e .

ENTRYPOINT ["twitter_logger"]

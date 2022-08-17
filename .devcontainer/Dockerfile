FROM python:3.10.4-slim-buster
ENV PYTHONPATH=.

RUN apt update && apt install gcc icu-devtools curl zsh git socat -y

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
RUN sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

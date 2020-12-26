FROM python:3.8

RUN mkdir /app
WORKDIR /app

COPY mycollect mycollect 
COPY Pipfile* ./

RUN pip install pip --upgrade
RUN pip install pipenv
RUN pipenv install --deploy --system

CMD ["python", "-m", "mycollect.starter"]
FROM python:3.11.5-bullseye

WORKDIR /usr/app

# Install python requirements

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
ENV PYTHONPATH=/usr/app
# Copy rest of the project

COPY . ./

# Run
CMD ["python", "main.py"]



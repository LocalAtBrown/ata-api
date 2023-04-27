FROM public.ecr.aws/docker/library/python:3.9.15-slim as req
COPY pyproject.toml .
COPY poetry.lock .
RUN pip install poetry && poetry export -o requirements.txt

FROM public.ecr.aws/lambda/python:3.9 as runner
COPY --from=req requirements.txt .
RUN yum update -y && yum install amazon-linux-extras postgresql-devel gcc -y
RUN PYTHON=python2 amazon-linux-extras install postgresql11
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
COPY /ata_api/ ${LAMBDA_TASK_ROOT}/ata_api
# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "ata_api/main.handler" ]

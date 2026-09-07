FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY src/pivot_lambda ${LAMBDA_TASK_ROOT}/pivot_lambda

CMD ["pivot_lambda.handler.lambda_handler"]

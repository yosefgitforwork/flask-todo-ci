FROM python
WORKDIR /tests
COPY testserver .
CMD ["python", "testserver.py"]
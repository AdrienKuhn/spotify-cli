FROM python:3.13.0rc1-slim AS compile-image
WORKDIR /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends git
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"
RUN python -m venv /opt/venv
COPY setup.py ./
COPY spotify/ spotify/
RUN pip install .

FROM python:3.13.0rc1-slim AS runtime-image
COPY --from=compile-image /opt/venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH
RUN useradd -ms /bin/sh -u 1000 spotify
USER 1000
CMD spotify-cli

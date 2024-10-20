FROM python:3.9-bullseye as build
ARG appName
RUN python3.9 -m venv /opt/engati/${appName}/venv
ENV PATH="/opt/engati/${appName}/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.9-slim-bullseye
ARG appName
RUN useradd --create-home appuser
RUN mkdir -p /var/log/engati/${appName}
RUN chown -R appuser: /var/log/engati/${appName}
USER appuser
WORKDIR /opt/engati/${appName}
COPY --from=build --chown=appuser /opt/engati/${appName}/venv venv/
COPY --chown=appuser duckdbengine duckdbengine/
ENV PATH=/opt/engati/${appName}/venv/bin:$PATH
CMD ["gunicorn", "-c", "metahackathonfinance/default_gunicorn.py", "metahackathonfinance:app"]

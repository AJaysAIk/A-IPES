# CPU analysis/static-check environment. MLX inference requires Apple Silicon.
# Version-tagged base, not digest-locked. Docker build not validated on author host.
FROM python:3.11.15-slim
WORKDIR /app
ENV MPLCONFIGDIR=/tmp/matplotlib PYTHONDONTWRITEBYTECODE=1 SEMGREP_SEND_METRICS=off
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir '.[dev,codeguard]' semgrep==1.178.0
COPY tests ./tests
COPY samples ./samples
COPY rules ./rules
COPY codeguard/corpus ./codeguard/corpus
COPY codeguard/configs ./codeguard/configs
COPY codeguard/docs ./codeguard/docs
COPY codeguard/results ./codeguard/results
RUN mkdir -p codeguard/figures && chmod -R a+rwX /app/codeguard
USER 65534:65534
ENTRYPOINT ["python", "-m", "codeguard"]
CMD ["analyse"]

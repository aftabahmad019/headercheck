# headercheck

![Tests](https://github.com/aftabahmad019/headercheck/actions/workflows/tests.yml/badge.svg)

A small Python command-line tool that checks a website for missing HTTP security headers. It is built to run locally, in Docker, or as a step in a CI pipeline.

## What it checks

| Header | Protects against |
|---|---|
| Strict-Transport-Security | Downgrade to unencrypted HTTP |
| Content-Security-Policy | Cross-site scripting (XSS) and content injection |
| X-Frame-Options | Clickjacking |
| X-Content-Type-Options | MIME-type sniffing |
| Referrer-Policy | Leaking URLs to other sites |

## Usage

### Locally

```
pip install -r requirements.txt
python headercheck.py https://example.com
```

### With Docker

```
docker build -t headercheck .
docker run --rm headercheck https://example.com
```

Example output:

```
[OK     ] Strict-Transport-Security
[OK     ] Content-Security-Policy
[OK     ] X-Frame-Options
[MISSING] X-Content-Type-Options
[MISSING] Referrer-Policy

2 of 5 security headers missing.
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | All security headers present |
| 1 | One or more headers missing |
| 2 | Usage error (no URL given) |
| 3 | Site could not be reached |

This makes the tool usable as a quality gate in CI: a non-zero exit code fails the pipeline.

## Testing

```
pytest -v
```

The test suite mocks all network calls, so it runs fast and never depends on a live website. It covers present and missing headers, case-insensitive header names, all exit codes, and unreachable sites.

Coverage is measured with `pytest-cov` (currently 97%), and CI fails if it drops below 90%. The HTML coverage report is uploaded as a build artifact on every run.

## Design notes

- **Mocked tests:** HTTP responses are faked with `unittest.mock`, keeping tests fast, deterministic and offline.
- **Clean failure handling:** network errors produce a clear message and exit code 3 instead of a stack trace.
- **Non-root container:** the Docker image runs as an unprivileged user (`appuser`), following the principle of least privilege. CI verifies this on every push.
- **CI pipeline:** GitHub Actions runs the tests, then builds the Docker image and smoke-tests it.

## Roadmap

- Run as a scheduled Kubernetes CronJob
- JSON output for integration with other tools
- Checking header values, not just presence

## Responsible use

Only scan websites you own or are permitted to test. The tool sends a single standard GET request.
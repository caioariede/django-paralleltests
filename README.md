**This project is under heavy development**

# django-paralleltests
A Test Runner for Django that runs tests in parallel.

The `--parallel` option for running tests was added in Django 1.9, described as follows:

> Each process gets its own database. You must ensure that different test cases don’t access the same resources. For instance, test cases that touch the filesystem should create a temporary directory for their own use.

It's such a fantastic feature and well done, but what if you have a code base prior to Django 1.9?

## Backporting the `--parallel` option

It's not as easy because it doesn't depend only on building a new test runner or backporting some existing work.

Tests needs to be written knowing they are running in parallel and [they may collide with other tests](https://github.com/aaugustin/django/commit/bf2c969eb7d941812993d69bcf7c8ac35bdb7726).

To prevent this, we need isolation. Docker.

## Idea

Develop a test runner that will run tests in parallel inside an isolated environment (Docker), to avoid collisions.

## Installation

    pip install https://github.com/caioariede/django-paralleltests/archive/master.zip

## Configuration

You must have a `Dockerfile` in place to generate the image to be used.

A Dockerfile example:

    FROM python:2.7
    ENV PYTHONUNBUFFERED 1
    ENV PYTHONPATH .:$PYTHONPATH
    RUN mkdir /code
    WORKDIR /code
    ADD . /code/
    RUN pip install -r requirements.txt

With this, you can generate a image with the following command:

    docker build -t paralleltest .

Right now, the image name is hardcoded to `paralleltest:latest`.

## Usage

Set `TEST_RUNNER` to `paralleltests.runner.parallel.ParallelRunner` in your `settings.py`.

Then run your tests as usual.

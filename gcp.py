#!/usr/bin/python3

import json
import os
import subprocess
import sys

import click
from google.cloud import storage


@click.group()
def cli():
    pass


@cli.command()
@click.argument("conf", default="SPECIAL_NONE_PROVIDED")
def context(conf):
    """gcloud context switcher"""
    cmd = "gcloud"
    if conf == "SPECIAL_NONE_PROVIDED":
        call = subprocess.run(
            [cmd, "config", "configurations", "list"], capture_output=True
        )
    else:
        call = subprocess.run(
            [cmd, "config", "configurations", "activate", conf], capture_output=True
        )
    print(call.stdout.decode())
    print(call.stderr.decode())


@cli.command()
def buckets():
    client = storage.Client()
    for bucket in client.list_buckets():
        print(bucket.name)


def get_current_project():
    call = subprocess.run(
        ["gcloud", "config", "get", "project", "--format='json'"], capture_output=True
    )
    return json.loads(call.stdout.decode())


if __name__ == "__main__":
    argv0 = os.path.basename(sys.argv[0])
    if argv0 == "gcp":
        cli()
    if argv0 == "gcs":
        buckets()
    else:
        sys.exit(f"{sys.argv[0]} is not a recognized command.")


# vim: syntax=python

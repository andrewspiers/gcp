#!/usr/bin/env python3

import json
import os
import subprocess
import sys

import click
from click import echo
from google.api_core import client_options
from google.cloud import storage
from google.cloud.devtools import cloudbuild_v1


@click.group()
def cli():
    pass


@cli.command()
@click.argument("conf", default="SPECIAL_NONE_PROVIDED")
def context(conf):
    """gcloud context switcher"""
    if conf == "SPECIAL_NONE_PROVIDED":
        call = gcloud_process(("config", "configurations", "list"))
    else:
        call = gcloud_process(("config", "configurations", "activate", conf))
    print(call.stdout.decode())
    print(call.stderr.decode())


@cli.command()
def buckets():
    client = storage.Client()
    for bucket in client.list_buckets():
        echo(bucket.name)


@cli.command()
@click.option("--region", default=None)
def triggers(region):
    project = get_current_project()
    if region is None:
        region = get_build_region()
        suffix = " from gcloud config."
    else:
        suffix = ""
    echo("using region: " + click.style(f"{region}", italic=True) + suffix)
    options = client_options.ClientOptions(
        api_endpoint=f"{region}-cloudbuild.googleapis.com"
    )
    client = cloudbuild_v1.CloudBuildClient(client_options=options)
    request = cloudbuild_v1.ListBuildTriggersRequest(project_id=project)
    page_result = client.list_build_triggers(request=request)
    responses = [r for r in page_result]
    for r in responses:
        print(r.name)
    echo("\nFor build details use the command:")
    echo(click.style("gcloud builds triggers describe <trigger>", italic=True))


def get_build_region():
    call = gcloud_process(("config", "get", "builds/region", "--format='json'"))
    val = call.stdout.decode()
    first_line = val.split()[0]
    stripped_val = first_line.strip('"')
    return stripped_val


def print_character_codes(input_string):
    """Only used for debugging."""
    for char in input_string:
        print(f"Character: {char}, Code: {ord(char)}")


def get_current_project():
    call = gcloud_process(("config", "get", "project", "--format='json'"))
    return json.loads(call.stdout.decode())


def gcloud_process(arg_list=[], capture_output=True):
    cmd = ["gcloud"]
    cmd.extend(arg_list)
    return subprocess.run(cmd, capture_output=capture_output)


if __name__ == "__main__":
    argv0 = os.path.basename(sys.argv[0])
    if argv0 == "gcp":
        cli()
    if argv0 == "gcs":
        buckets()
    else:
        sys.exit(f"{sys.argv[0]} is not a recognized command.")


# vim: syntax=python

#!/usr/bin/env python3

from glob import glob
from os.path import basename, isfile

import click
from CloudFlare import CloudFlare

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


@click.command()
@click.option(
    "--cloudflare-token",
    "token",
    required=True,
    envvar="CLOUDFLARE_TOKEN",
    show_envvar=True,
)
@click.option(
    "--cloudflare-zone-id",
    "zone_id",
    required=True,
    envvar="CLOUDFLARE_ZONE_ID",
    show_envvar=True,
)
@click.argument("files", required=True, nargs=-1)
def main(token, zone_id, files):
    with CloudFlare(token=token) as cloudflare:
        dns_records = cloudflare.zones.dns_records.get(zone_id)
        cname_records = {
            dns_record["name"]: dns_record
            for dns_record in dns_records
            if dns_record["type"] == "CNAME"
        }
    click.echo(f"{len(cname_records)} CNAME in Cloudflare")

    cname_files = {}
    for pathname in files:
        for filename in glob(pathname):
            if isfile(filename):
                cname_files[basename(filename)] = filename
    click.echo(f"{len(cname_records)} CNAME in File System")

    for name in cname_files.keys() - cname_records.keys():
        with open(cname_files[name]) as file:
            content = file.read().strip()
        data = {"type": "CNAME", "name": name, "content": content, "ttl": 1}
        cloudflare.zones.dns_records.post(zone_id, data=data)
        click.echo(f"+ {name}")

    for name in cname_records.keys() - cname_files.keys():
        dns_record_id = cname_records[name]["id"]
        cloudflare.zones.dns_records.delete(zone_id, dns_record_id)
        click.echo(f"- {name}")

    for name in cname_records.keys() & cname_files.keys():
        with open(cname_files[name]) as file:
            cname_file_content = file.read().strip()
        dns_record_content = cname_records[name]["content"]
        if cname_file_content == dns_record_content:
            click.echo(f"S {name}")
            continue

        dns_record_id = cname_records[name]["id"]
        data = {"content": cname_file_content}
        cloudflare.zones.dns_records.patch(zone_id, dns_record_id, data=data)
        click.echo(f"U {name}")


if __name__ == "__main__":
    main()

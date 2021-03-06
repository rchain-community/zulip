import argparse
import os
import tempfile
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser

from zerver.data_import.slack import do_convert_data


class Command(BaseCommand):
    help = """Convert the Slack data into Zulip data format."""

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('slack_data_zip', nargs='+',
                            metavar='<slack data zip>',
                            help="Zipped slack data")

        parser.add_argument('--token', metavar='<slack_token>',
                            type=str, help='Slack legacy token of the organsation')

        parser.add_argument('--output', dest='output_dir',
                            action="store", default=None,
                            help='Directory to write exported data to.')

        parser.add_argument('--threads',
                            action="store",
                            default=settings.DEFAULT_DATA_EXPORT_IMPORT_PARALLELISM,
                            help='Threads to use in exporting UserMessage objects in parallel')

        parser.formatter_class = argparse.RawTextHelpFormatter

    def handle(self, *args: Any, **options: Any) -> None:
        output_dir = options["output_dir"]
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="converted-slack-data-")
        else:
            output_dir = os.path.realpath(output_dir)

        token = options['token']
        if token is None:
            raise CommandError("Enter slack legacy token!")

        num_threads = int(options['threads'])
        if num_threads < 1:
            raise CommandError('You must have at least one thread.')

        for path in options['slack_data_zip']:
            if not os.path.exists(path):
                raise CommandError(f"Slack data directory not found: '{path}'")

            print("Converting Data ...")
            do_convert_data(path, output_dir, token, threads=num_threads)

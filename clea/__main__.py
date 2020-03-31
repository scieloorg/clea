import click
import ujson

from clea import Article, clean_empty


def xml2dict(xml_file):
    art = Article(xml_file, raise_on_invalid=False)
    return clean_empty({**art.data_full,
        "filename": xml_file.name,
        "aff_contrib_pairs": art.aff_contrib_full_indices,
    })


@click.command()
@click.option("jsonl_output", "-o", "--output",
              type=click.File("w"), default="-",
              help="JSONL output file, "
                   "defaults to the standard output stream.")
@click.argument("xml_files", type=click.File("r"), nargs=-1, required=True)
def main(xml_files, jsonl_output):
    for xml_file in xml_files:
        ujson.dump(
            xml2dict(xml_file), jsonl_output,
            ensure_ascii=False,
            escape_forward_slashes=False,
        )
        jsonl_output.write("\n")


if __name__ == "__main__":  # Not a "from clea import __main__"
    from signal import signal, SIGPIPE, SIG_IGN
    signal(SIGPIPE, SIG_IGN)  # Ignore broken pipe
    main()

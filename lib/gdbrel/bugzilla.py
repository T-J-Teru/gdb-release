import requests


class DumpFormat(object):
    """The various ways to format the information about a bug.

    There are two types of placeholders in those strings:
        - Those enclosed between curly brackets (eg: '{xxx}')
          refer to general configuration elements, and get
          substituted once. This information is usually replaced
          with information extracted from the config.yaml file.
        - Those enclosed inside '%(' and ')s' (eg: %(xxx)s').
          Those refer to elements of each bug returned by
          bugzilla's REST interface.
    """

    TEXT = " * PR %(component)s/%(id)s (%(summary)s)"
    HTML = (
        '<li> <a href="{bugzilla_url}/{show_bug}?id=%(id)s">'
        "PR %(component)s/%(id)s</a> (%(summary)s)"
    )


def get_fixed_bugs(config, version):
    """Return the list of fixed bugs for the given version.

    PARAMETERS
        config: a gdbrel.config.Config object.
        version: The GDB version (a string).
    """
    request_info = (
        "product=gdb",
        "resolution=FIXED",
        "target_milestone=%s" % version,
        "include_fields=%s" % ",".join(("id", "component", "summary")),
    )
    request_url = "%s/%s/bug?%s" % (
        config["bugzilla.url"],
        config["bugzilla.rest_suburl"],
        "&".join(request_info),
    )

    r = requests.get(request_url)
    return r.json()


def dump_fixed_bugs(config, version, fmt):
    """Dump the list of fixed bugs for the given version.

    PARAMETERS
        config: a gdbrel.config.Config object.
        version: The GDB version (a string).
        fmt: The format to use when printing the description of each bug.
            Use any of the formats provided by the DumpFormat class above.
    """
    data = get_fixed_bugs(config, version)
    fmt = fmt.format(
        bugzilla_url=config["bugzilla.url"], show_bug=config["bugzilla.show_bug_suburl"]
    )

    for bug in data["bugs"]:
        # Remove trailing periods (it looks better).
        bug["summary"] = bug["summary"].rstrip(".")
        print(fmt % bug)

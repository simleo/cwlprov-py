#!/usr/bin/env python

## © 2018 Software Freedom Conservancy (SFC)
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

import sys
import argparse

from cwlprov.ro import ResearchObject

# TODO: Move any use these to cwlprov.*
import arcp
import bagit

from enum import IntEnum

BAGIT_RO_PROFILE = "https://w3id.org/ro/bagit/profile"
CWLPROV_SUPPORTED = set((
    # Decreasing order as first item is output as example
    "https://w3id.org/cwl/prov/0.4.0",
    "https://w3id.org/cwl/prov/0.3.0",
))

class Status(IntEnum):
    """Exit codes from main()"""
    OK = 0
    INVALID_BAG = 1
    MISSING_PROFILE = 2
    UNSUPPORTED_CWLPROV_VERSION = 3

def parse_args(args):
    parser = argparse.ArgumentParser(description='cwlprov')

    parser.add_argument("ro",
        help="Path to CWLProv Research Object folder")
    parser.add_argument("--validate",
        help="Validate CWLProv RO and return", action="store_true")

    return parser.parse_args(args)

def main(*args):
    # type: (...) -> None
    """cwlprov command line tool"""
    args = parse_args(args)

    bag = bagit.Bag(args.ro)

    ## BagIt check
    # Always do a minimal validation, but
    # will also test checksum on --validate
    valid_bag = bag.validate(fast=args.validate)

    ## RO check
    profiles = bag.info.get("BagIt-Profile-Identifier", ())
    is_ro = BAGIT_RO_PROFILE in profiles
    cwlprov = set()
    for p in profiles:
        if "https://w3id.org/cwl/prov/" in p:
            cwlprov.add(p)
    supported_cwlprov = CWLPROV_SUPPORTED.intersection(cwlprov)
    if cwlprov and not supported_cwlprov:
        print("Unsupported CWLProv version: %s" % cwlprov, file=sys.stderr)

    # TODO: Find the master run


    ##PROV check
    # TODO: Prov check

    if args.validate:
        # TODO: More checks, e.g. every PROV file valid?
        if not valid_bag:
            print("Invalid BagIt folder: %s" % args.ro,
                file=sys.stderr)
            return Status.INVALID_BAG
        if not is_ro:
            print("Missing BdBag profile (%s): %s" %
                (BAGIT_RO_PROFILE, args.ro),
                file=sys.stderr)
            return Status.MISSING_PROFILE
        if not cwlprov:
            print("Missing CWLProv profile (e.g. %s): %s" %
                (next(iter(CWLPROV_SUPPORTED)), args.ro),
                file=sys.stderr)
            return Status.MISSING_PROFILE
        if not supported_cwlprov:
            # Warning already printed above
            print("Supported CWLProv profiles: %s" %
                " ".join(CWLPROV_SUPPORTED),
                file=sys.stderr)
            return Status.MISSING_PROFILE

            return Status.UNSUPPORTED_CWLPROV_VERSION

    # Probably went fine if we made it to here
    return Status.OK

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))


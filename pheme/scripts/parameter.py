#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pheme/scripts/parameter-json-from-dir.py
# Copyright (C) 2020 Greenbone Networks GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Usage: pheme-parameter-json-from-dir $path > parameter.json

import json
import mimetypes
import sys
from pathlib import Path
from typing import Dict

from pheme.datalink import as_datalink


def load_data(parent: Path) -> Dict:
    data = {}
    for i in parent.glob("*"):
        file_type, _ = mimetypes.guess_type(i.name)
        key = (
            i.name[: -len(i.suffix)]
            if not 'css' in i.suffix
            else "{}_css".format(i.name[: -len(i.suffix)])
        )
        if i.is_dir():
            data = {**data, **load_data(i)}
        elif file_type and file_type.startswith('image'):
            data[key] = as_datalink(i.read_bytes(), file_type)
        elif file_type and file_type.startswith('text'):
            data[key] = i.read_text()
        elif file_type and file_type == 'application/json':
            data = {**data, **json.loads(i.read_text())}
        else:
            sys.stderr.write("skipping {} -> {}".format(i, file_type))
    return data


def main():
    if len(sys.argv) != 2:
        sys.stderr.write("need exactly one one path parameter. Aborting.")
        sys.exit(1)
    mimetypes.add_type('text/scss', '.scss')
    data = {}
    paths = sys.argv[1:]
    for i in paths:
        parent = Path(i)
        data = {**data, **load_data(parent)}
    print(json.dumps(data))


if __name__ == "__main__":
    main()

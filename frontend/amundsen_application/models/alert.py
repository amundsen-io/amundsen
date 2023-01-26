# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import attr

# TODO seems attr.attrs() is the preferred alias for attr.s()? Modern way might be one of the other methods entirely. https://www.attrs.org/en/stable/names.html
@attr.attrs(auto_attribs=True, kw_only=True)
class TableAlertsSummary:
    severity: int = attr.attrib()  # TODO enum
    details: dict = attr.attrib()
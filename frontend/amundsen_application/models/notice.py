# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import attr


@attr.attrs(auto_attribs=True, kw_only=True)
class TableNotice:
    message: str = attr.attrib()  # TODO make this HTML
    severity: int = attr.attrib()
    link: str = attr.attrib()
    details: dict = attr.attrib()  # TODO make them optional

# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import attr


@attr.attrs(auto_attribs=True, kw_only=True)
class TableNotice:
    severity: int = attr.attrib()
    message: str = attr.attrib()  # TODO make this HTML
    link: str = attr.attrib()  # TODO it's an Amundsen link?
    details: dict = attr.attrib()  # TODO make them optional

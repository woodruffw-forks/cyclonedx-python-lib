# encoding: utf-8

# This file is part of CycloneDX Python Lib
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) OWASP Foundation. All Rights Reserved.

import datetime
import sys
from typing import List, Union
from uuid import uuid4

from . import HashType
from .component import Component
from ..parser import BaseParser


class Tool:
    """
    This is out internal representation of the toolType complex type within the CycloneDX standard.

    Tool(s) are the things used in the creation of the BOM.

    .. note::
        See the CycloneDX Schema for toolType: https://cyclonedx.org/docs/1.3/#type_toolType
    """

    _vendor: str = None
    _name: str = None
    _version: str = None
    _hashes: List[HashType] = []

    def __init__(self, vendor: str, name: str, version: str, hashes: List[HashType] = []):
        self._vendor = vendor
        self._name = name
        self._version = version
        self._hashes = hashes

    def get_hashes(self) -> List[HashType]:
        """
        List of cryptographic hashes that identify this version of this Tool.

        Returns:
            `List` of `HashType` objects where there are any hashes, else an empty `List`.
        """
        return self._hashes

    def get_name(self) -> str:
        """
        The name of this Tool.

        Returns:
            `str` representing the name of the Tool
        """
        return self._name

    def get_vendor(self) -> str:
        """
        The vendor of this Tool.

        Returns:
            `str` representing the vendor of the Tool
        """
        return self._vendor

    def get_version(self) -> str:
        """
        The version of this Tool.

        Returns:
            `str` representing the version of the Tool
        """
        return self._version

    def __repr__(self):
        return '<Tool {}:{}:{}>'.format(self._vendor, self._name, self._version)


if sys.version_info >= (3, 8, 0):
    from importlib.metadata import version as meta_version
else:
    from importlib_metadata import version as meta_version

try:
    ThisTool = Tool(vendor='CycloneDX', name='cyclonedx-python-lib', version=meta_version('cyclonedx-python-lib'))
except Exception:
    ThisTool = Tool(vendor='CycloneDX', name='cyclonedx-python-lib', version='UNKNOWN')


class BomMetaData:
    """
    This is our internal representation of the metadata complex type within the CycloneDX standard.

    .. note::
        See the CycloneDX Schema for Bom metadata: https://cyclonedx.org/docs/1.3/#type_metadata
    """

    _timestamp: datetime.datetime
    _tools: List[Tool] = []

    def __init__(self, tools: List[Tool] = []):
        self._timestamp = datetime.datetime.now(tz=datetime.timezone.utc)
        self._tools.clear()
        if len(tools) == 0:
            tools.append(ThisTool)
        self._tools = tools

    def add_tool(self, tool: Tool):
        """
        Add a Tool definition to this Bom Metadata. The `cyclonedx-python-lib` is automatically added - you do not need
        to add this yourself.

        Args:
            tool:
                Instance of `Tool` that represents the tool you are using.
        """
        self._tools.append(tool)

    def get_timestamp(self) -> datetime.datetime:
        """
        The date and time (in UTC) when this BomMetaData was created.

        Returns:
            `datetime.datetime` instance in UTC timezone
        """
        return self._timestamp

    def get_tools(self) -> List[Tool]:
        """
        Tools used to create this BOM.

        Returns:
            `List` of `Tool` objects where there are any, else an empty `List`.
        """
        return self._tools


class Bom:
    """
    This is our internal representation of a bill-of-materials (BOM).

    You can either create a `cyclonedx.model.bom.Bom` yourself programmatically, or generate a `cyclonedx.model.bom.Bom`
    from a `cyclonedx.parser.BaseParser` implementation.

    Once you have an instance of `cyclonedx.model.bom.Bom`, you can pass this to an instance of
    `cyclonedx.output.BaseOutput` to produce a CycloneDX document according to a specific schema version and format.
    """

    _uuid: str
    _metadata: BomMetaData = None
    _components: List[Component] = []

    @staticmethod
    def from_parser(parser: BaseParser):
        """
        Create a Bom instance from a Parser object.

        Args:
            parser (`cyclonedx.parser.BaseParser`): A valid parser instance.

        Returns:
            `cyclonedx.model.bom.Bom`: A Bom instance that represents the valid data held in the supplied parser.
        """
        bom = Bom()
        bom.add_components(parser.get_components())
        return bom

    def __init__(self):
        """
        Create a new Bom that you can manually/programmatically add data to later.

        Returns:
            New, empty `cyclonedx.model.bom.Bom` instance.
        """
        self._uuid = uuid4()
        self._metadata = BomMetaData(tools=[])
        self._components.clear()

    def add_component(self, component: Component):
        """
        Add a Component to this Bom instance.

        Args:
            component:
                `cyclonedx.model.component.Component` instance to add to this Bom.

        Returns:
            None
        """
        if not self.has_component(component=component):
            self._components.append(component)

    def add_components(self, components: List[Component]):
        """
        Add multiple Components at once to this Bom instance.

        Args:
            components:
                List of `cyclonedx.model.component.Component` instances to add to this Bom.

        Returns:
            None
        """
        self._components = self._components + components

    def component_count(self) -> int:
        """
        Returns the current count of Components within this Bom.

        Returns:
             The number of Components in this Bom as `int`.
        """
        return len(self._components)

    def get_component_by_purl(self, purl: str) -> Union[Component, None]:
        """
        Get a Component already in the Bom by it's PURL

        Args:
             purl:
                Package URL as a `str` to look and find `Component`

        Returns:
            `Component` or `None`
        """
        found = list(filter(lambda x: x.get_purl() == purl, self._components))
        if len(found) == 1:
            return found[0]

        return None

    def get_components(self) -> List[Component]:
        """
        Get all the Components currently in this Bom.

        Returns:
             List of all Components in this Bom.
        """
        return self._components

    def get_metadata(self) -> BomMetaData:
        """
        Get our internal metadata object for this Bom.

        Returns:
            Metadata object instance for this Bom.

        .. note::
            See the CycloneDX Schema for Bom metadata: https://cyclonedx.org/docs/1.3/#type_metadata
        """
        return self._metadata

    def get_urn_uuid(self) -> str:
        """
        Get the unique reference for this Bom.

        Returns:
            URN formatted UUID that uniquely identified this Bom instance.
        """
        return 'urn:uuid:{}'.format(self._uuid)

    def has_component(self, component: Component) -> bool:
        """
        Check whether this Bom contains the provided Component.

        Args:
            component:
                The instance of `cyclonedx.model.component.Component` to check if this Bom contains.

        Returns:
            `bool` - `True` if the supplied Component is part of this Bom, `False` otherwise.
        """
        return component in self._components

    def has_vulnerabilities(self) -> bool:
        """
        Check whether this Bom has any declared vulnerabilities.

        Returns:
            `bool` - `True` if at least one `cyclonedx.model.component.Component` has at least one Vulnerability,
                `False` otherwise.
        """
        for c in self.get_components():
            if c.has_vulnerabilities():
                return True

        return False
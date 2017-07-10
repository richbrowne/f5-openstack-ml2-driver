"""Setup install script for F5 Networks ML2 plugin driver."""
# Copyright 2017 F5 Networks Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import setuptools

setuptools.setup(
    version="0.1.0",
    name="f5-openstack-ml2-driver",
    description="F5 Networks OpenStack Neutron ML2 plugin driver",
    license='Apache License, Version 2.0',
    author="F5 Networks"
)

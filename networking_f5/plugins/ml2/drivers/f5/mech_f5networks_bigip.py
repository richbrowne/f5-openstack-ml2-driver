u"""This module provides a ML2 driver for BIG-IP."""
# coding=utf-8
#
# Copyright 2017 F5 Networks Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from oslo_log import log

from neutron.extensions import portbindings
from neutron.plugins.ml2 import driver_api as api


LOG = log.getLogger(__name__)


class F5NetworksMechanismDriver(api.MechanismDriver):
    """F5NetworksMechanismDriver implementation.

    Provides BIG-IP with Neutron Port Binding capability.
    """

    def __init__(self):
        """Create F5NetworksMechanismDriver."""
        super(F5NetworksMechanismDriver, self).__init__()

    def initialize(self):
        """Initialize the F5Networks mechanism driver."""
        LOG.debug("F5Networks Mechanism Driver Initialize")

    def bind_port(self, context):
        """Bind the port for a BIG-IP device.

        :param context: PortContext instaces describing the port

        We need to bind the port for the BIG-IP agent.  This is not
        connected to any other network.

        """
        LOG.debug(
            "Attempting to bind port %(port)s on "
            "network %(network)s",
            {'port': context.current['id'],
             'network': context.network.current['id']})

        for segment in context.segments_to_bind:
            if self._is_f5lbaas_port(context.current):
                context.set_binding(
                    segment['id'],
                    portbindings.VIF_TYPE_OTHER,
                    {})
            else:
                LOG.debug("F5Networks Mechanism Driver not binding port")

    def _is_f5lbaas_port(self, port):
        return port['device_owner'] == 'network:f5lbaasv2'

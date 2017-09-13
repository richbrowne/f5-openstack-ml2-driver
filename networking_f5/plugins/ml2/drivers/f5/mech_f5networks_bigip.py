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
from neutron.plugins.common import constants as p_constants
from neutron.plugins.ml2 import driver_api as api
from neutron.plugins.ml2.drivers import mech_agent

LOG = log.getLogger(__name__)

VNIC_F5_APPLIANCE = 'f5appliance'
AGENT_TYPE_LOADBALANCERV2 = 'Loadbalancerv2 agent'


class F5NetworksMechanismDriver(mech_agent.AgentMechanismDriverBase):
    """F5NetworksMechanismDriver implementation.

    Provides BIG-IP with Neutron Port Binding capability.
    """

    def __init__(self):
        """Create F5NetworksMechanismDriver."""
        super(F5NetworksMechanismDriver, self).__init__(
            AGENT_TYPE_LOADBALANCERV2,
            [VNIC_F5_APPLIANCE])

    def initialize(self):
        """Initialize the F5Networks mechanism driver."""
        LOG.debug("F5Networks Mechanism Driver Initialize")

    def try_to_bind_segment_for_agent(self, context, segment, agent):
        """Try to bind with segment for agent.

        :param context: PortContext instance describing the port
        :param segment: segment dictionary describing segment to bind
        :param agent: agents_db entry describing agent to bind
        :returns: True iff segment has been bound for agent

        Called outside any transaction during bind_port() so that
        derived MechanismDrivers can use agent_db data along with
        built-in knowledge of the corresponding agent's capabilities
        to attempt to bind to the specified network segment for the
        agent.
        """
        agent_config = agent.get('configurations', {})

        # Get the supporting tunnel types (e.g. vxlan, gre)
        tunnel_types = agent_config.get("tunnel_types", [])

        # Get the BigIP interface to physicaL_network mappings to
        # determine what networks the BigIP is connected to.
        bridge_mappings = agent_config.get('bridge_mappings', {})

        # Get the physical network of the Hierachical Port Binding
        # network segment.
        hpb_physical_network_segment = agent_config.get(
            'network_segment_physical_network', None)

        network_type = segment.get('network_type', "")

        bind_segment = False
        # For now, the only criteria for binding is if the network
        # type is supported.  We can modify this for physical network
        # types, if the agent can report the physical_network for each
        # of the agent bridge_mappings.
        if network_type in tunnel_types:
            bind_segment = True
        elif network_type in [p_constants.TYPE_FLAT, p_constants.TYPE_VLAN]:
            physnet = segment[api.PHYSICAL_NETWORK]
            if physnet in bridge_mappings:
                bind_segment = True
            elif physnet == hpb_physical_network_segment:
                bind_segment = False

        # Can we bind the port to this segment?
        if bind_segment:
            # Yes, set the binding.
            context.set_binding(
                segment['id'],
                portbindings.VIF_TYPE_OTHER,
                {})

        return bind_segment

    def _is_f5lbaasv2_device_owner(self, port):
        return port['device_owner'] == 'network:f5lbaasv2'

    def _is_f5appliance_vnic(self, vnic_type):
        return vnic_type == VNIC_F5_APPLIANCE

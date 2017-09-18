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

from neutron.plugins.common import constants as p_constants
from neutron.plugins.ml2 import driver_api as api
from neutron.plugins.ml2.drivers import mech_agent
from neutron_lib.api.definitions import portbindings

from networking_f5.plugins.ml2.drivers.f5 import constants

LOG = log.getLogger(__name__)


class F5NetworksMechanismDriver(mech_agent.AgentMechanismDriverBase):
    """F5NetworksMechanismDriver implementation.

    Provides BIG-IP with Neutron Port Binding capability.
    """

    def __init__(self):
        """Create F5NetworksMechanismDriver."""
        super(F5NetworksMechanismDriver, self).__init__(
            constants.AGENT_TYPE_LOADBALANCERV2,
            [constants.VNIC_F5_APPLIANCE])

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
        if not agent:
            LOG.warn("No agent passed in to binding call.")
            return False

        agent_config = agent.get('configurations', {})

        # Get the supporting tunnel types (e.g. vxlan, gre)
        tunnel_types = agent_config.get(constants.AGENT_TUNNEL_TYPES, [])

        # Get the BigIP interface to physicaL_network mappings to
        # determine what vlan/flat networks the BigIP is connected to.
        bridge_mappings = agent_config.get(constants.AGENT_BRIDGE_MAPPINGS, {})

        # Get the physical network of the Hierachical Port Binding
        # network segment.
        hpb_physical_network_segment = agent_config.get(
            constants.AGENT_HPB_PHYSICAL_NETWORK, None)

        network_type = segment.get(api.NETWORK_TYPE, "")

        # The criteria for port binding is if the segment network type is:
        # 1. If the segment network type is the same as one of the
        #    advertised tunnel types, the port can be bound.
        # 2. If the segment network type is 'flat' or 'vlan' and the
        #    agent advertises a bridge mapping between the physical_network
        #    of the segment and an interface on the BIG-IP, the port can
        #    be bound.
        # 3. IF the agent is advertising the physical network name of
        #    a segment in a hierarchical network, the port can be bound
        #    if the segement physical_network matches that of the agent's
        bind_segment = False
        if network_type in tunnel_types:
            LOG.debug("binding segment with tunnel type: %s" % network_type)
            bind_segment = True
        elif network_type in [p_constants.TYPE_FLAT, p_constants.TYPE_VLAN]:
            physnet = segment[api.PHYSICAL_NETWORK]
            if physnet in bridge_mappings:
                LOG.debug("binding segment with network type: %(network_type) "
                          "on physical network %(physical_network)",
                          {'network_type': network_type,
                           'physical_network': physnet})
                bind_segment = True
            elif physnet == hpb_physical_network_segment:
                LOG.debug("binding segment with network type: %(network_type) "
                          "on hierarchical network, physical network "
                          "%(physical_network)",
                          {'network_type': network_type,
                           'physical_network': physnet})
                bind_segment = True

        # Can we bind the port to this segment?
        if bind_segment:
            # Yes, set the binding for now the vif details are
            # empty.
            vif_details = dict()
            context.set_binding(
                segment[api.ID],
                portbindings.VIF_TYPE_OTHER,
                vif_details)

        return bind_segment

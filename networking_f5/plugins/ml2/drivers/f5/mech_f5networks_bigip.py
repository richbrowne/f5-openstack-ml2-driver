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

from neutron._i18n import _LW
from neutron.extensions import portbindings
from neutron.plugins.ml2 import driver_api as api
from neutron.plugins.ml2.drivers import mech_agent
from neutron_lib import constants as q_const

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

        agent_config = agent.get('configurations', {})
        tunnel_types = agent_config.get("tunnel_types", [])
        tunnel_types.append('vlan')

        network_type = segment.get('network_type', "")

        bind_segment = False
        if network_type in tunnel_types:
            bind_segment = True

        if bind_segment:
            context.set_binding(
                segment['id'],
                portbindings.VIF_TYPE_OTHER,
                {})

        return bind_segment
        
    def _is_f5lbaasv2_device_owner(self, port):
        return port['device_owner'] == 'network:f5lbaasv2'

    def _is_f5appliance_vnic(self, vnic_type):
        return vnic_type == VNIC_F5_APPLIANCE

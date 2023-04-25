# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
#            Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Spectrum Virtualize Ansible module: ibm_svc_info """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.spectrum_virtualize.plugins.modules.ibm_svc_info import IBMSVCGatherInfo


def set_module_args(args):
    """prepare arguments so that they will be picked up during module
    creation """
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)  # pylint: disable=protected-access


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the
    test case """
    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the
    test case """
    pass


def exit_json(*args, **kwargs):  # pylint: disable=unused-argument
    """function to patch over exit_json; package return data into an
    exception """
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):  # pylint: disable=unused-argument
    """function to patch over fail_json; package return data into an
    exception """
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


class TestIBMSVCGatherInfo(unittest.TestCase):
    """ a group of related Unit Tests"""

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def setUp(self, connect):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)
        self.restapi = IBMSVCRestApi(self.mock_module_helper, '1.2.3.4',
                                     'domain.ibm.com', 'username', 'password',
                                     False, 'test.log', '')

    def set_default_args(self):
        return dict({
            'name': 'test',
            'state': 'present'
        })

    def test_module_fail_when_required_args_missing(self):
        """ required arguments are reported as errors """
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args({})
            IBMSVCGatherInfo()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_info.IBMSVCGatherInfo.get_hosts_list')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_info.IBMSVCGatherInfo.is_code_level_supported')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_host_list_called(self, mock_svc_authorize,
                                  mock_is_code_level_supported,
                                  get_hosts_list_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'host',
        })
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_hosts_list_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_info.IBMSVCGatherInfo.get_pools_list')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_info.IBMSVCGatherInfo.get_volumes_list')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_info.IBMSVCGatherInfo.get_hosts_list')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_info.IBMSVCGatherInfo.is_code_level_supported')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_pool_vol_host_list_called(self, mock_svc_authorize,
                                           mock_is_code_level_supported,
                                           get_hosts_list_mock,
                                           get_volumes_list_mock,
                                           get_pools_list_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'pool,host,vol',
        })
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
            get_hosts_list_mock.assert_called_with()
            get_pools_list_mock.assert_called_with()
            get_volumes_list_mock.assert_called_with()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_info.IBMSVCGatherInfo.is_code_level_supported')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_the_host_result_by_gather_info(self, svc_authorize_mock,
                                            mock_is_code_level_supported,
                                            svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'host',
        })
        host_ret = [{"id": "1", "name": "ansible_host", "port_count": "1",
                     "iogrp_count": "4", "status": "offline",
                     "site_id": "", "site_name": "",
                     "host_cluster_id": "", "host_cluster_name": "",
                     "protocol": "nvme", "owner_id": "",
                     "owner_name": ""}]
        svc_obj_info_mock.return_value = host_ret
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertFalse(exc.value.args[0]['changed'])
        self.assertDictEqual(exc.value.args[0]['Host'][0], host_ret[0])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_info.IBMSVCGatherInfo.is_code_level_supported')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_the_host_and_vol_result_by_gather_info(self, svc_authorize_mock,
                                                    mock_is_code_level_supported,
                                                    svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'host,vol',
        })
        host_ret = [{"id": "1", "name": "ansible_host", "port_count": "1",
                     "iogrp_count": "4", "status": "offline",
                     "site_id": "", "site_name": "",
                     "host_cluster_id": "", "host_cluster_name": "",
                     "protocol": "nvme", "owner_id": "",
                     "owner_name": ""}]
        vol_ret = [{"id": "0", "name": "volume_Ansible_collections",
                    "IO_group_id": "0", "IO_group_name": "io_grp0",
                    "status": "online", "mdisk_grp_id": "0",
                    "mdisk_grp_name": "Pool_Ansible_collections",
                    "capacity": "4.00GB", "type": "striped", "FC_id": "",
                    "FC_name": "", "RC_id": "", "RC_name": "",
                    "vdisk_UID": "6005076810CA0166C00000000000019F",
                    "fc_map_count": "0", "copy_count": "1",
                    "fast_write_state": "empty", "se_copy_count": "0",
                    "RC_change": "no", "compressed_copy_count": "0",
                    "parent_mdisk_grp_id": "0",
                    "parent_mdisk_grp_name": "Pool_Ansible_collections",
                    "owner_id": "", "owner_name": "", "formatting": "no",
                    "encrypt": "no", "volume_id": "0",
                    "volume_name": "volume_Ansible_collections",
                    "function": "", "protocol": "scsi"}]
        svc_obj_info_mock.side_effect = [vol_ret, host_ret]
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertFalse(exc.value.args[0]['changed'])
        self.assertDictEqual(exc.value.args[0]['Host'][0], host_ret[0])
        self.assertDictEqual(exc.value.args[0]['Volume'][0], vol_ret[0])

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_info.IBMSVCGatherInfo.get_volumegroup_list')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_volumegroup_unsupported_called(self, svc_authorize_mock, svc_obj_info_mock,
                                                get_volumegroup_list_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'volumegroup',
        })
        svc_obj_info_mock.return_value = {
            "id": "0000010023806192",
            "name": "Cluster_9.71.42.198",
            "location": "local",
            "partnership": "",
            "total_mdisk_capacity": "3.6TB",
            "space_in_mdisk_grps": "3.6TB",
            "space_allocated_to_vdisks": "449.70GB",
            "total_free_space": "3.2TB",
            "total_vdiskcopy_capacity": "993.00GB",
            "total_used_capacity": "435.67GB",
            "total_overallocation": "26",
            "total_vdisk_capacity": "993.00GB",
            "total_allocated_extent_capacity": "455.00GB",
            "statistics_status": "on",
            "statistics_frequency": "15",
            "cluster_locale": "en_US",
            "time_zone": "503 SystemV/PST8",
            "code_level": "8.4.2.0 (build 154.20.2109031944000)",
            "console_IP": "9.71.42.198:443",
            "id_alias": "0000010023806192",
            "gm_link_tolerance": "300",
            "gm_inter_cluster_delay_simulation": "0",
            "gm_intra_cluster_delay_simulation": "0",
            "gm_max_host_delay": "5",
            "email_reply": "sreshtant.bohidar@ibm.com",
            "email_contact": "Sreshtant Bohidar",
            "email_contact_primary": "9439394132",
            "email_contact_alternate": "9439394132",
            "email_contact_location": "floor 2",
            "email_contact2": "",
            "email_contact2_primary": "",
            "email_contact2_alternate": "",
            "email_state": "stopped",
            "inventory_mail_interval": "1",
            "cluster_ntp_IP_address": "2.2.2.2",
            "cluster_isns_IP_address": "",
            "iscsi_auth_method": "none",
            "iscsi_chap_secret": "",
            "auth_service_configured": "no",
            "auth_service_enabled": "no",
            "auth_service_url": "",
            "auth_service_user_name": "",
            "auth_service_pwd_set": "no",
            "auth_service_cert_set": "no",
            "auth_service_type": "ldap",
            "relationship_bandwidth_limit": "25",
            "tiers": [
                {
                    "tier": "tier_scm",
                    "tier_capacity": "0.00MB",
                    "tier_free_capacity": "0.00MB"
                },
                {
                    "tier": "tier0_flash",
                    "tier_capacity": "1.78TB",
                    "tier_free_capacity": "1.47TB"
                },
                {
                    "tier": "tier1_flash",
                    "tier_capacity": "0.00MB",
                    "tier_free_capacity": "0.00MB"
                },
                {
                    "tier": "tier_enterprise",
                    "tier_capacity": "0.00MB",
                    "tier_free_capacity": "0.00MB"
                },
                {
                    "tier": "tier_nearline",
                    "tier_capacity": "1.82TB",
                    "tier_free_capacity": "1.68TB"
                }
            ],
            "easy_tier_acceleration": "off",
            "has_nas_key": "no",
            "layer": "storage",
            "rc_buffer_size": "256",
            "compression_active": "no",
            "compression_virtual_capacity": "0.00MB",
            "compression_compressed_capacity": "0.00MB",
            "compression_uncompressed_capacity": "0.00MB",
            "cache_prefetch": "on",
            "email_organization": "IBM",
            "email_machine_address": "Street 39",
            "email_machine_city": "New York",
            "email_machine_state": "CAN",
            "email_machine_zip": "123456",
            "email_machine_country": "US",
            "total_drive_raw_capacity": "10.10TB",
            "compression_destage_mode": "off",
            "local_fc_port_mask": "1111111111111111111111111111111111111111111111111111111111111111",
            "partner_fc_port_mask": "1111111111111111111111111111111111111111111111111111111111111111",
            "high_temp_mode": "off",
            "topology": "hyperswap",
            "topology_status": "dual_site",
            "rc_auth_method": "none",
            "vdisk_protection_time": "15",
            "vdisk_protection_enabled": "no",
            "product_name": "IBM Storwize V7000",
            "odx": "off",
            "max_replication_delay": "0",
            "partnership_exclusion_threshold": "315",
            "gen1_compatibility_mode_enabled": "no",
            "ibm_customer": "262727272",
            "ibm_component": "",
            "ibm_country": "383",
            "tier_scm_compressed_data_used": "0.00MB",
            "tier0_flash_compressed_data_used": "0.00MB",
            "tier1_flash_compressed_data_used": "0.00MB",
            "tier_enterprise_compressed_data_used": "0.00MB",
            "tier_nearline_compressed_data_used": "0.00MB",
            "total_reclaimable_capacity": "380.13MB",
            "physical_capacity": "3.60TB",
            "physical_free_capacity": "3.15TB",
            "used_capacity_before_reduction": "361.81MB",
            "used_capacity_after_reduction": "14.27GB",
            "overhead_capacity": "34.00GB",
            "deduplication_capacity_saving": "0.00MB",
            "enhanced_callhome": "on",
            "censor_callhome": "on",
            "host_unmap": "off",
            "backend_unmap": "on",
            "quorum_mode": "standard",
            "quorum_site_id": "",
            "quorum_site_name": "",
            "quorum_lease": "short",
            "automatic_vdisk_analysis_enabled": "on",
            "callhome_accepted_usage": "no",
            "safeguarded_copy_suspended": "no",
            'serverIP': '9.20.118.16',
            'serverPort': 25
        }
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_volumegroup_list_mock.assert_not_called()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_info.IBMSVCGatherInfo.get_snapshot_list')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_snapshot_unsupported_called(self, svc_authorize_mock, svc_obj_info_mock,
                                             get_snapshot_list_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'system,snapshot',
        })
        svc_obj_info_mock.return_value = [{
            "id": "0000010023806192",
            "name": "Cluster_9.71.42.198",
            "location": "local",
            "partnership": "",
            "total_mdisk_capacity": "3.6TB",
            "space_in_mdisk_grps": "3.6TB",
            "space_allocated_to_vdisks": "449.70GB",
            "total_free_space": "3.2TB",
            "total_vdiskcopy_capacity": "993.00GB",
            "total_used_capacity": "435.67GB",
            "total_overallocation": "26",
            "total_vdisk_capacity": "993.00GB",
            "total_allocated_extent_capacity": "455.00GB",
            "statistics_status": "on",
            "statistics_frequency": "15",
            "cluster_locale": "en_US",
            "time_zone": "503 SystemV/PST8",
            "code_level": "8.5.1.0 (mocked)",
            "console_IP": "9.71.42.198:443",
            "id_alias": "0000010023806192",
            "gm_link_tolerance": "300",
            "gm_inter_cluster_delay_simulation": "0",
            "gm_intra_cluster_delay_simulation": "0",
            "gm_max_host_delay": "5",
            "email_reply": "sreshtant.bohidar@ibm.com",
            "email_contact": "Sreshtant Bohidar",
            "email_contact_primary": "9439394132",
            "email_contact_alternate": "9439394132",
            "email_contact_location": "floor 2",
            "email_contact2": "",
            "email_contact2_primary": "",
            "email_contact2_alternate": "",
            "email_state": "stopped",
            "inventory_mail_interval": "1",
            "cluster_ntp_IP_address": "2.2.2.2",
            "cluster_isns_IP_address": "",
            "iscsi_auth_method": "none",
            "iscsi_chap_secret": "",
            "auth_service_configured": "no",
            "auth_service_enabled": "no",
            "auth_service_url": "",
            "auth_service_user_name": "",
            "auth_service_pwd_set": "no",
            "auth_service_cert_set": "no",
            "auth_service_type": "ldap",
            "relationship_bandwidth_limit": "25",
            "tiers": [
                {
                    "tier": "tier_scm",
                    "tier_capacity": "0.00MB",
                    "tier_free_capacity": "0.00MB"
                },
                {
                    "tier": "tier0_flash",
                    "tier_capacity": "1.78TB",
                    "tier_free_capacity": "1.47TB"
                },
                {
                    "tier": "tier1_flash",
                    "tier_capacity": "0.00MB",
                    "tier_free_capacity": "0.00MB"
                },
                {
                    "tier": "tier_enterprise",
                    "tier_capacity": "0.00MB",
                    "tier_free_capacity": "0.00MB"
                },
                {
                    "tier": "tier_nearline",
                    "tier_capacity": "1.82TB",
                    "tier_free_capacity": "1.68TB"
                }
            ],
            "easy_tier_acceleration": "off",
            "has_nas_key": "no",
            "layer": "storage",
            "rc_buffer_size": "256",
            "compression_active": "no",
            "compression_virtual_capacity": "0.00MB",
            "compression_compressed_capacity": "0.00MB",
            "compression_uncompressed_capacity": "0.00MB",
            "cache_prefetch": "on",
            "email_organization": "IBM",
            "email_machine_address": "Street 39",
            "email_machine_city": "New York",
            "email_machine_state": "CAN",
            "email_machine_zip": "123456",
            "email_machine_country": "US",
            "total_drive_raw_capacity": "10.10TB",
            "compression_destage_mode": "off",
            "local_fc_port_mask": "1111111111111111111111111111111111111111111111111111111111111111",
            "partner_fc_port_mask": "1111111111111111111111111111111111111111111111111111111111111111",
            "high_temp_mode": "off",
            "topology": "hyperswap",
            "topology_status": "dual_site",
            "rc_auth_method": "none",
            "vdisk_protection_time": "15",
            "vdisk_protection_enabled": "no",
            "product_name": "IBM Storwize V7000",
            "odx": "off",
            "max_replication_delay": "0",
            "partnership_exclusion_threshold": "315",
            "gen1_compatibility_mode_enabled": "no",
            "ibm_customer": "262727272",
            "ibm_component": "",
            "ibm_country": "383",
            "tier_scm_compressed_data_used": "0.00MB",
            "tier0_flash_compressed_data_used": "0.00MB",
            "tier1_flash_compressed_data_used": "0.00MB",
            "tier_enterprise_compressed_data_used": "0.00MB",
            "tier_nearline_compressed_data_used": "0.00MB",
            "total_reclaimable_capacity": "380.13MB",
            "physical_capacity": "3.60TB",
            "physical_free_capacity": "3.15TB",
            "used_capacity_before_reduction": "361.81MB",
            "used_capacity_after_reduction": "14.27GB",
            "overhead_capacity": "34.00GB",
            "deduplication_capacity_saving": "0.00MB",
            "enhanced_callhome": "on",
            "censor_callhome": "on",
            "host_unmap": "off",
            "backend_unmap": "on",
            "quorum_mode": "standard",
            "quorum_site_id": "",
            "quorum_site_name": "",
            "quorum_lease": "short",
            "automatic_vdisk_analysis_enabled": "on",
            "callhome_accepted_usage": "no",
            "safeguarded_copy_suspended": "no",
            'serverIP': '9.20.118.16',
            'serverPort': 25
        }]
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_snapshot_list_mock.assert_not_called()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_info.IBMSVCGatherInfo.get_snapshot_list')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_snapshot_volumegroup_unsupported_called(self, svc_authorize_mock,
                                                         svc_obj_info_mock,
                                                         get_snapshot_list_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'snapshot,volumegroup',
        })
        svc_obj_info_mock.return_value = [{
            "id": "0000010023806192",
            "name": "Cluster_9.71.42.198",
            "location": "local",
            "partnership": "",
            "total_mdisk_capacity": "3.6TB",
            "space_in_mdisk_grps": "3.6TB",
            "space_allocated_to_vdisks": "449.70GB",
            "total_free_space": "3.2TB",
            "total_vdiskcopy_capacity": "993.00GB",
            "total_used_capacity": "435.67GB",
            "total_overallocation": "26",
            "total_vdisk_capacity": "993.00GB",
            "total_allocated_extent_capacity": "455.00GB",
            "statistics_status": "on",
            "statistics_frequency": "15",
            "cluster_locale": "en_US",
            "time_zone": "503 SystemV/PST8",
            "code_level": "7.8.0.0 (mocked)",
            "console_IP": "9.71.42.198:443",
            "id_alias": "0000010023806192",
            "gm_link_tolerance": "300",
            "gm_inter_cluster_delay_simulation": "0",
            "gm_intra_cluster_delay_simulation": "0",
            "gm_max_host_delay": "5",
            "email_reply": "sreshtant.bohidar@ibm.com",
            "email_contact": "Sreshtant Bohidar",
            "email_contact_primary": "9439394132",
            "email_contact_alternate": "9439394132",
            "email_contact_location": "floor 2",
            "email_contact2": "",
            "email_contact2_primary": "",
            "email_contact2_alternate": "",
            "email_state": "stopped",
            "inventory_mail_interval": "1",
            "cluster_ntp_IP_address": "2.2.2.2",
            "cluster_isns_IP_address": "",
            "iscsi_auth_method": "none",
            "iscsi_chap_secret": "",
            "auth_service_configured": "no",
            "auth_service_enabled": "no",
            "auth_service_url": "",
            "auth_service_user_name": "",
            "auth_service_pwd_set": "no",
            "auth_service_cert_set": "no",
            "auth_service_type": "ldap",
            "relationship_bandwidth_limit": "25",
            "tiers": [
                {
                    "tier": "tier_scm",
                    "tier_capacity": "0.00MB",
                    "tier_free_capacity": "0.00MB"
                },
                {
                    "tier": "tier0_flash",
                    "tier_capacity": "1.78TB",
                    "tier_free_capacity": "1.47TB"
                },
                {
                    "tier": "tier1_flash",
                    "tier_capacity": "0.00MB",
                    "tier_free_capacity": "0.00MB"
                },
                {
                    "tier": "tier_enterprise",
                    "tier_capacity": "0.00MB",
                    "tier_free_capacity": "0.00MB"
                },
                {
                    "tier": "tier_nearline",
                    "tier_capacity": "1.82TB",
                    "tier_free_capacity": "1.68TB"
                }
            ],
            "easy_tier_acceleration": "off",
            "has_nas_key": "no",
            "layer": "storage",
            "rc_buffer_size": "256",
            "compression_active": "no",
            "compression_virtual_capacity": "0.00MB",
            "compression_compressed_capacity": "0.00MB",
            "compression_uncompressed_capacity": "0.00MB",
            "cache_prefetch": "on",
            "email_organization": "IBM",
            "email_machine_address": "Street 39",
            "email_machine_city": "New York",
            "email_machine_state": "CAN",
            "email_machine_zip": "123456",
            "email_machine_country": "US",
            "total_drive_raw_capacity": "10.10TB",
            "compression_destage_mode": "off",
            "local_fc_port_mask": "1111111111111111111111111111111111111111111111111111111111111111",
            "partner_fc_port_mask": "1111111111111111111111111111111111111111111111111111111111111111",
            "high_temp_mode": "off",
            "topology": "hyperswap",
            "topology_status": "dual_site",
            "rc_auth_method": "none",
            "vdisk_protection_time": "15",
            "vdisk_protection_enabled": "no",
            "product_name": "IBM Storwize V7000",
            "odx": "off",
            "max_replication_delay": "0",
            "partnership_exclusion_threshold": "315",
            "gen1_compatibility_mode_enabled": "no",
            "ibm_customer": "262727272",
            "ibm_component": "",
            "ibm_country": "383",
            "tier_scm_compressed_data_used": "0.00MB",
            "tier0_flash_compressed_data_used": "0.00MB",
            "tier1_flash_compressed_data_used": "0.00MB",
            "tier_enterprise_compressed_data_used": "0.00MB",
            "tier_nearline_compressed_data_used": "0.00MB",
            "total_reclaimable_capacity": "380.13MB",
            "physical_capacity": "3.60TB",
            "physical_free_capacity": "3.15TB",
            "used_capacity_before_reduction": "361.81MB",
            "used_capacity_after_reduction": "14.27GB",
            "overhead_capacity": "34.00GB",
            "deduplication_capacity_saving": "0.00MB",
            "enhanced_callhome": "on",
            "censor_callhome": "on",
            "host_unmap": "off",
            "backend_unmap": "on",
            "quorum_mode": "standard",
            "quorum_site_id": "",
            "quorum_site_name": "",
            "quorum_lease": "short",
            "automatic_vdisk_analysis_enabled": "on",
            "callhome_accepted_usage": "no",
            "safeguarded_copy_suspended": "no",
            'serverIP': '9.20.118.16',
            'serverPort': 25
        }]
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_snapshot_list_mock.assert_not_called()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_info.IBMSVCGatherInfo.get_volumegroup_list')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_volumegroup_list_called(self, svc_authorize_mock, svc_obj_info_mock,
                                         get_volumegroup_list_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'volumegroup',
        })
        svc_obj_info_mock.return_value = {
            "id": "0000010023806192",
            "name": "Cluster_9.71.42.198",
            "location": "local",
            "partnership": "",
            "total_mdisk_capacity": "3.6TB",
            "space_in_mdisk_grps": "3.6TB",
            "space_allocated_to_vdisks": "449.70GB",
            "total_free_space": "3.2TB",
            "total_vdiskcopy_capacity": "993.00GB",
            "total_used_capacity": "435.67GB",
            "total_overallocation": "26",
            "total_vdisk_capacity": "993.00GB",
            "total_allocated_extent_capacity": "455.00GB",
            "statistics_status": "on",
            "statistics_frequency": "15",
            "cluster_locale": "en_US",
            "time_zone": "503 SystemV/PST8",
            "code_level": "8.5.2.0 (mocked)",
            "console_IP": "9.71.42.198:443",
            "id_alias": "0000010023806192",
            "gm_link_tolerance": "300",
            "gm_inter_cluster_delay_simulation": "0",
            "gm_intra_cluster_delay_simulation": "0",
            "gm_max_host_delay": "5",
            "email_reply": "sreshtant.bohidar@ibm.com",
            "email_contact": "Sreshtant Bohidar",
            "email_contact_primary": "9439394132",
            "email_contact_alternate": "9439394132",
            "email_contact_location": "floor 2",
            "email_contact2": "",
            "email_contact2_primary": "",
            "email_contact2_alternate": "",
            "email_state": "stopped",
            "inventory_mail_interval": "1",
            "cluster_ntp_IP_address": "2.2.2.2",
            "cluster_isns_IP_address": "",
            "iscsi_auth_method": "none",
            "iscsi_chap_secret": "",
            "auth_service_configured": "no",
            "auth_service_enabled": "no",
            "auth_service_url": "",
            "auth_service_user_name": "",
            "auth_service_pwd_set": "no",
            "auth_service_cert_set": "no",
            "auth_service_type": "ldap",
            "relationship_bandwidth_limit": "25",
            "tiers": [
                {
                    "tier": "tier_scm",
                    "tier_capacity": "0.00MB",
                    "tier_free_capacity": "0.00MB"
                },
                {
                    "tier": "tier0_flash",
                    "tier_capacity": "1.78TB",
                    "tier_free_capacity": "1.47TB"
                },
                {
                    "tier": "tier1_flash",
                    "tier_capacity": "0.00MB",
                    "tier_free_capacity": "0.00MB"
                },
                {
                    "tier": "tier_enterprise",
                    "tier_capacity": "0.00MB",
                    "tier_free_capacity": "0.00MB"
                },
                {
                    "tier": "tier_nearline",
                    "tier_capacity": "1.82TB",
                    "tier_free_capacity": "1.68TB"
                }
            ],
            "easy_tier_acceleration": "off",
            "has_nas_key": "no",
            "layer": "storage",
            "rc_buffer_size": "256",
            "compression_active": "no",
            "compression_virtual_capacity": "0.00MB",
            "compression_compressed_capacity": "0.00MB",
            "compression_uncompressed_capacity": "0.00MB",
            "cache_prefetch": "on",
            "email_organization": "IBM",
            "email_machine_address": "Street 39",
            "email_machine_city": "New York",
            "email_machine_state": "CAN",
            "email_machine_zip": "123456",
            "email_machine_country": "US",
            "total_drive_raw_capacity": "10.10TB",
            "compression_destage_mode": "off",
            "local_fc_port_mask": "1111111111111111111111111111111111111111111111111111111111111111",
            "partner_fc_port_mask": "1111111111111111111111111111111111111111111111111111111111111111",
            "high_temp_mode": "off",
            "topology": "hyperswap",
            "topology_status": "dual_site",
            "rc_auth_method": "none",
            "vdisk_protection_time": "15",
            "vdisk_protection_enabled": "no",
            "product_name": "IBM Storwize V7000",
            "odx": "off",
            "max_replication_delay": "0",
            "partnership_exclusion_threshold": "315",
            "gen1_compatibility_mode_enabled": "no",
            "ibm_customer": "262727272",
            "ibm_component": "",
            "ibm_country": "383",
            "tier_scm_compressed_data_used": "0.00MB",
            "tier0_flash_compressed_data_used": "0.00MB",
            "tier1_flash_compressed_data_used": "0.00MB",
            "tier_enterprise_compressed_data_used": "0.00MB",
            "tier_nearline_compressed_data_used": "0.00MB",
            "total_reclaimable_capacity": "380.13MB",
            "physical_capacity": "3.60TB",
            "physical_free_capacity": "3.15TB",
            "used_capacity_before_reduction": "361.81MB",
            "used_capacity_after_reduction": "14.27GB",
            "overhead_capacity": "34.00GB",
            "deduplication_capacity_saving": "0.00MB",
            "enhanced_callhome": "on",
            "censor_callhome": "on",
            "host_unmap": "off",
            "backend_unmap": "on",
            "quorum_mode": "standard",
            "quorum_site_id": "",
            "quorum_site_name": "",
            "quorum_lease": "short",
            "automatic_vdisk_analysis_enabled": "on",
            "callhome_accepted_usage": "no",
            "safeguarded_copy_suspended": "no",
            'serverIP': '9.20.118.16',
            'serverPort': 25
        }
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_volumegroup_list_mock.assert_called_with()

    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.modules.'
           'ibm_svc_info.IBMSVCGatherInfo.get_snapshot_list')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_snapshot_list_called(self, svc_authorize_mock, svc_obj_info_mock,
                                      get_snapshot_list_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'snapshot',
        })
        svc_obj_info_mock.return_value = {
            "id": "0000010023806192",
            "name": "Cluster_9.71.42.198",
            "location": "local",
            "partnership": "",
            "total_mdisk_capacity": "3.6TB",
            "space_in_mdisk_grps": "3.6TB",
            "space_allocated_to_vdisks": "449.70GB",
            "total_free_space": "3.2TB",
            "total_vdiskcopy_capacity": "993.00GB",
            "total_used_capacity": "435.67GB",
            "total_overallocation": "26",
            "total_vdisk_capacity": "993.00GB",
            "total_allocated_extent_capacity": "455.00GB",
            "statistics_status": "on",
            "statistics_frequency": "15",
            "cluster_locale": "en_US",
            "time_zone": "503 SystemV/PST8",
            "code_level": "8.5.3.1 (build 163.7.2212281621000)",
            "console_IP": "9.71.42.198:443",
            "id_alias": "0000010023806192",
            "gm_link_tolerance": "300",
            "gm_inter_cluster_delay_simulation": "0",
            "gm_intra_cluster_delay_simulation": "0",
            "gm_max_host_delay": "5",
            "email_reply": "sreshtant.bohidar@ibm.com",
            "email_contact": "Sreshtant Bohidar",
            "email_contact_primary": "9439394132",
            "email_contact_alternate": "9439394132",
            "email_contact_location": "floor 2",
            "email_contact2": "",
            "email_contact2_primary": "",
            "email_contact2_alternate": "",
            "email_state": "stopped",
            "inventory_mail_interval": "1",
            "cluster_ntp_IP_address": "2.2.2.2",
            "cluster_isns_IP_address": "",
            "iscsi_auth_method": "none",
            "iscsi_chap_secret": "",
            "auth_service_configured": "no",
            "auth_service_enabled": "no",
            "auth_service_url": "",
            "auth_service_user_name": "",
            "auth_service_pwd_set": "no",
            "auth_service_cert_set": "no",
            "auth_service_type": "ldap",
            "relationship_bandwidth_limit": "25",
            "tiers": [
                {
                    "tier": "tier_scm",
                    "tier_capacity": "0.00MB",
                    "tier_free_capacity": "0.00MB"
                },
                {
                    "tier": "tier0_flash",
                    "tier_capacity": "1.78TB",
                    "tier_free_capacity": "1.47TB"
                },
                {
                    "tier": "tier1_flash",
                    "tier_capacity": "0.00MB",
                    "tier_free_capacity": "0.00MB"
                },
                {
                    "tier": "tier_enterprise",
                    "tier_capacity": "0.00MB",
                    "tier_free_capacity": "0.00MB"
                },
                {
                    "tier": "tier_nearline",
                    "tier_capacity": "1.82TB",
                    "tier_free_capacity": "1.68TB"
                }
            ],
            "easy_tier_acceleration": "off",
            "has_nas_key": "no",
            "layer": "storage",
            "rc_buffer_size": "256",
            "compression_active": "no",
            "compression_virtual_capacity": "0.00MB",
            "compression_compressed_capacity": "0.00MB",
            "compression_uncompressed_capacity": "0.00MB",
            "cache_prefetch": "on",
            "email_organization": "IBM",
            "email_machine_address": "Street 39",
            "email_machine_city": "New York",
            "email_machine_state": "CAN",
            "email_machine_zip": "123456",
            "email_machine_country": "US",
            "total_drive_raw_capacity": "10.10TB",
            "compression_destage_mode": "off",
            "local_fc_port_mask": "1111111111111111111111111111111111111111111111111111111111111111",
            "partner_fc_port_mask": "1111111111111111111111111111111111111111111111111111111111111111",
            "high_temp_mode": "off",
            "topology": "hyperswap",
            "topology_status": "dual_site",
            "rc_auth_method": "none",
            "vdisk_protection_time": "15",
            "vdisk_protection_enabled": "no",
            "product_name": "IBM Storwize V7000",
            "odx": "off",
            "max_replication_delay": "0",
            "partnership_exclusion_threshold": "315",
            "gen1_compatibility_mode_enabled": "no",
            "ibm_customer": "262727272",
            "ibm_component": "",
            "ibm_country": "383",
            "tier_scm_compressed_data_used": "0.00MB",
            "tier0_flash_compressed_data_used": "0.00MB",
            "tier1_flash_compressed_data_used": "0.00MB",
            "tier_enterprise_compressed_data_used": "0.00MB",
            "tier_nearline_compressed_data_used": "0.00MB",
            "total_reclaimable_capacity": "380.13MB",
            "physical_capacity": "3.60TB",
            "physical_free_capacity": "3.15TB",
            "used_capacity_before_reduction": "361.81MB",
            "used_capacity_after_reduction": "14.27GB",
            "overhead_capacity": "34.00GB",
            "deduplication_capacity_saving": "0.00MB",
            "enhanced_callhome": "on",
            "censor_callhome": "on",
            "host_unmap": "off",
            "backend_unmap": "on",
            "quorum_mode": "standard",
            "quorum_site_id": "",
            "quorum_site_name": "",
            "quorum_lease": "short",
            "automatic_vdisk_analysis_enabled": "on",
            "callhome_accepted_usage": "no",
            "safeguarded_copy_suspended": "no",
            'serverIP': '9.20.118.16',
            'serverPort': 25
        }
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_snapshot_list_mock.assert_called_with()


if __name__ == '__main__':
    unittest.main()

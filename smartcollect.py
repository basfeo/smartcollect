#!/usr/bin/env python3

import datetime
import sys
import subprocess
import json
from typing import Dict, Any
import os


def pretty_print_json(obj):
    """
    This func output data in json format
    :param obj: json data
    :return: output json format pretty print
    """
    json_formatted_str = json.dumps(obj, sort_key=True, indent=2)
    print(json_formatted_str)


def device_scan_scsi(device_path=""):
    """
    This func is scanning scsi devices
    :param device_path: ''
    :return: dict
    """
    try:
        proc = subprocess.Popen(f"smartctl --scan-open {device_path} -d scsi --json", shell=True, stdout=subprocess.PIPE,
                                encoding='utf-8')
        stdout, stderr = proc.communicate()
        json_data = json.loads(stdout)

        return json_data
    except Exception:
        return {}


def device_scan_sat(device_path=""):
    """
    This func is scanning scsi devices
    :param device_path: ''
    :return: dict
    """
    try:
        proc = subprocess.Popen(f"smartctl --scan-open {device_path} -d sat --json", shell=True, stdout=subprocess.PIPE,
                                encoding='utf-8')
        stdout, stderr = proc.communicate()
        json_data = json.loads(stdout)

        return json_data
    except Exception:
        return {}



def device_scan(device_path="", id_dev='-d auto'):
    """
    This func is scanning all devices
    :param device_path: ''
    :return: dict
    """
    try:
        proc = subprocess.Popen(f"smartctl --scan-open {id_dev} --json", shell=True, stdout=subprocess.PIPE,
                                encoding='utf-8')
        stdout, stderr = proc.communicate()
        json_data = json.loads(stdout)

        return json_data
    except Exception:
        return {}


def get_device(data):
    """
    This func parse dict from device_scan() or device_scan_scsi
    :return: list
    """
    devices = []
    if isinstance(data, dict):
        for device in data.get('devices', []):
            if not device['name'].startswith('/dev/bus/'):
                devices.append(device['name'])
    return devices


def device_info(device_path, id_dev='-d auto'):
    """

    :param device_path: dev; id_dev: param for smartcl
    :return: dict
    """
    exit_status = 0
    try:
        proc = subprocess.Popen(f"smartctl {id_dev} --info {device_path} --json", shell=True, stdout=subprocess.PIPE,
                                encoding='utf-8')
        stdout, stderr = proc.communicate()
        json_data = json.loads(stdout)

        return json_data
    except Exception:
        return {}


def get_info(data):
    """
    this fun pars date from func device_info()
    :param json_data:
    :return: dict
    """
    if isinstance(data, dict):
        return data
    return {}


def collect_error_count(device_path, id_dev='-d auto'):
    """
    This func add info about dev errors
    :param device_path: dev_path; id_dev: param for scan
    :return: dict
    """
    try:
        proc = subprocess.Popen(f"smartctl {id_dev} --all {device_path} --json=svc", shell=True, stdout=subprocess.PIPE, encoding='utf-8')
        stdout, stderr = proc.communicate()
        json_data = json.loads(stdout)

        return json_data
    except Exception:
        return {}


def get_device_type(data, device_type='nvme'):
    """
    This func parse data from func collect_error_count. NVME type disk
     :param json_data:
     :return: dict
     """
    if isinstance(data, dict):
        return data.get('device', {}).get('type')
    return ''


def ata_device_statistics_pages(data):
    """
    This func parse data from func collect_error_count. NVME type disk
    :param json_data:
    :return: dict
    : ata_device_statistics_pages
    """
    ata_device = {}
    if data.get('device', {}).get('type', {}) == 'sat':
        ata_device['device'] = data.get('device')
    if data.get('ata_smart_attributes', {}).get('table'):
        if data.get('ata_smart_attributes', {}).get('table'):
            for item in data.get('ata_smart_attributes', {}).get('table'):
                if item.get('name', {}) != 'Unknown_Attribute':
                    ata_device[item.get('name', {})] = {
                        'raw': item.get('value')
                    }
    if data.get('ata_device_statistics', {}).get('pages',{}):
        for items in data.get('ata_device_statistics', {}).get('pages',{}):
            if items.get('name'):
                for item in items.get('table'):
                    ata_device[item.get('name', {})] = {
                        'offset': item.get('offset', {}),
                        'size': item.get('size', {}),
                        'value': item.get('value', {}),
                    }
    return ata_device


def scsi_device_statistics_pages(data):
    """
    This func parse data from func collect_error_count. NVME type disk
    :param json_data:
    :return: dict
    """
    data_return = {}
    if isinstance(data, dict) and data.get('device', {}).get('type') == 'scsi':
        for key, item in data.items():
            data_return[key] = item

    return data_return


def nvme_device_statistics_pages(data):
    """
    This func parse data from func collect_erro r_count. NVME type disk
     :param json_data:
     :return: dict
     """
    data_return = {}
    if isinstance(data, dict) and data.get('device', {}).get('type') == 'nvme':
        for key, item in data.items():
            data_return[key] = item

    return data_return


def sat_device_statistics_pages(data):
    """
    This func parse data from func collect_error_count. NVME type disk
    :param json_data:
    :return: dict
    : ata_device_statistics_pages
    """
    sat_device = {}
    if data.get('smart_status'):
        sat_device['smart_status'] = {
            'passed': data.get('smart_status', {}).get('passed')
        }
    if data.get('model_name') and data.get('serial_number'):
        sat_device['info'] = {
            'model_name': data.get('model_name'),
            'serial_number': data.get('serial_number')
        }
    if data.get('device', {}).get('type', {}) == 'sat':
        sat_device['device'] = data.get('device')
    if data.get('ata_smart_attributes', {}).get('table'):
        if data.get('ata_smart_attributes', {}).get('table'):
            for item in data.get('ata_smart_attributes', {}).get('table'):
                if item.get('name', {}) != 'Unknown_Attribute':
                    sat_device[item.get('name', {})] = {
                        'value': item.get('value'),
                        'raw': item.get('raw').get('string')
                    }
    if data.get('ata_device_statistics', {}).get('pages',{}):
        for items in data.get('ata_device_statistics', {}).get('pages',{}):
            if items.get('name'):
                for item in items.get('table'):
                    sat_device[item.get('name', {})] = {
                        'offset': item.get('offset', {}),
                        'size': item.get('size', {}),
                        'value': item.get('value', {}),
                    }
    return sat_device


def print_for_exporter_format_nvme(data):
    """
    Output print_for_exporter_format_nvme fot node_exporter nvme type disks
    :param data: data
    :return: string
    """
    smart_status = 'smart_status' #data.get('passed', {}')
    device_nvme = data.get('device', {})
    device_path_nvme = device_nvme.get('name')
    capacity = ''
    size = ''
    utilization = ''
    sub_id = 'subsystem_id'
    avail_sp = 'available_spare'
    avail_sp_tr = 'available_spare_threshold'
    cr_war = 'critical_warning'
    date_u_r = 'data_units_read'
    data_u_wr = 'data_units_written'
    host_reads = 'host_reads'
    host_writes = 'host_writes'
    med_errs = 'media_errors'
    num_err_log = 'num_err_log_entries'
    perc_used = 'percentage_used'
    pow_cycl = 'power_cycles'
    pow_hs = 'power_on_hours'
    temp = 'temperature'
    unsafe_shut = 'unsafe_shutdowns'
    sm_dev_cp = 'smartmon_device_smart_capacity'
    sm_dev_sz = 'smartmon_device_smart_size'
    sm_dev_ut = 'smartmon_device_smart_utilization'
    device_serial = data.get('serial_number')
    device_model = data.get('model_name')
    out = []
    for key, items in data.items():
        if not isinstance(items, dict):
            continue
        device_key = f"smartmon_device_smart"
        if key == smart_status:
            out.append(f"{device_key}{{name=\"{smart_status.lower()}\", device=\"{device_path_nvme}\", serial_number=\"{device_serial}\", device_model=\"{device_model}\"}} {int(items.get('passed', {}))}")
        if items.get(sub_id):
            out.append(f"{device_key}{{name=\"{sub_id.lower()}\", device=\"{device_path_nvme}\", serial_number=\"{device_serial}\", device_model=\"{device_model}\"}} {items.get(sub_id, {})}")
        if items.get(avail_sp):
            out.append(f"{device_key}{{name=\"{avail_sp.lower()}\", device=\"{device_path_nvme}\", serial_number=\"{device_serial}\", device_model=\"{device_model}\"}} {items.get(avail_sp, {})}")
        if items.get(avail_sp_tr):
            out.append(f"{device_key}{{name=\"{avail_sp_tr.lower()}\", device=\"{device_path_nvme}\", serial_number=\"{device_serial}\", device_model=\"{device_model}\"}} {items.get(avail_sp_tr, {})}")
        if items.get(cr_war):
            out.append(f"{device_key}{{name=\"{cr_war.lower()}\", device=\"{device_path_nvme}\", serial_number=\"{device_serial}\", device_model=\"{device_model}\"}} {items.get(cr_war, {})}")
        if items.get(date_u_r):
            out.append(f"{device_key}{{name=\"{date_u_r.lower()}\", device=\"{device_path_nvme}\", serial_number=\"{device_serial}\", device_model=\"{device_model}\"}} {items.get(date_u_r, {})}")
        if items.get(data_u_wr):
            out.append(f"{device_key}{{name=\"{data_u_wr.lower()}\", device=\"{device_path_nvme}\", serial_number=\"{device_serial}\", device_model=\"{device_model}\"}} {items.get(data_u_wr, {})}")
        if items.get(host_reads):
            out.append(f"{device_key}{{name=\"{host_reads.lower()}\", device=\"{device_path_nvme}\", serial_number=\"{device_serial}\", device_model=\"{device_model}\"}} {items.get(host_reads, {})}")
        if items.get(host_writes):
            out.append(f"{device_key}{{name=\"{host_writes.lower()}\", device=\"{device_path_nvme}\", serial_number=\"{device_serial}\", device_model=\"{device_model}\"}} {items.get(host_writes, {})}")
        if items.get(med_errs):
            out.append(f"{device_key}{{name=\"{med_errs.lower()}\", device=\"{device_path_nvme}\", serial_number=\"{device_serial}\", device_model=\"{device_model}\"}} {items.get(med_errs, {})}")
        if items.get(num_err_log):
            out.append(f"{device_key}{{name=\"{num_err_log.lower()}\", device=\"{device_path_nvme}\", serial_number=\"{device_serial}\", device_model=\"{device_model}\"}} {items.get(num_err_log, {})}")
        if items.get(perc_used):
            out.append(f"{device_key}{{name=\"{perc_used.lower()}\", device=\"{device_path_nvme}\", serial_number=\"{device_serial}\", device_model=\"{device_model}\"}} {items.get(perc_used, {})}")
        if items.get(pow_cycl):
            out.append(f"{device_key}{{name=\"{pow_cycl.lower()}\", device=\"{device_path_nvme}\", serial_number=\"{device_serial}\", device_model=\"{device_model}\"}} {items.get(pow_cycl, {})}")
        if items.get(pow_hs):
            out.append(f"{device_key}{{name=\"{pow_hs.lower()}\", device=\"{device_path_nvme}\", serial_number=\"{device_serial}\", device_model=\"{device_serial}\"}} {items.get(pow_hs, {})}")
        if items.get(temp):
            out.append(f"{device_key}{{name=\"{temp.lower()}\", device=\"{device_path_nvme}\", serial_number=\"{device_serial}\", device_model=\"{device_serial}\"}} {items.get(temp, {})}")
        if items.get(unsafe_shut):
            out.append(f"{device_key}{{name=\"{unsafe_shut.lower()}\", device=\"{device_path_nvme}\", serial_number=\"{device_serial}\", device_model=\"{device_serial}\"}} {items.get(unsafe_shut, {})}")

    for item in data.get('nvme_namespaces', {}):
        if item.get('capacity', {}).get('bytes'):
            capacity = item.get('capacity', {}).get('bytes')
        if item.get('size', {}).get('bytes'):
            size = item.get('size', {}).get('bytes')
        if item.get('utilization', {}).get('bytes'):
            utilization = item.get('utilization', {}).get('bytes')

    out.append(f"{sm_dev_cp}{{name=\"capacity\", device=\"{device_path_nvme}\"}} {capacity}")
    out.append(f"{sm_dev_sz}{{name=\"size\", device=\"{device_path_nvme}\"}} {size}")
    out.append(f"{sm_dev_ut}{{name=\"utilization\", device=\"{device_path_nvme}\"}} {utilization}")
    return out


def print_for_exporter_format_ata(data):
    """
    Output print_for_exporter_format_ata fot node_exporter ata type disks
    :param data: data
    :return: string
    """

    out = []
    for key, data_value in data.items():
        if not isinstance(data_value, dict):
            continue
        device_key = f"smartmon_device_smart_{key}"
        raw_value = data_value.get("raw", {})
        value = data_value.get("value", {})
        device_path = data.get('device', {}).get('name')
        unusedRsvd = 'Unused_Rsvd_Blk_Cnt_Tot'
        lifePowerOn = 'Lifetime-Power-On-Resets'
        powerHours = 'Power-on-Hours'
        logicSecWr = 'Logical-Sectors-Written'
        numOfWr = 'Number-of-Write-Commands'
        logicSecRe = 'Logical-Sectors-Read'
        numOfRe = 'Number-of-Read-Commands'
        numOfRepUncrErr = 'Number-of-Reported-Uncorrectable-Errors'
        acceptComplt = 'Resets-Between-Cmd-Acceptance-and-Completion'
        tempVal = 'Current-Temperature'
        crcErrors = 'Number-of-Interface-CRC-Errors'
        endIndic = 'Percentage-Used-Endurance-Indicator'
        if key == unusedRsvd:
            out.append(f"{device_key}{{name=\"{unusedRsvd}-row\" device=\"{device_path}\"}} {raw_value}")
        if key == lifePowerOn:
            out.append(f"{device_key}{{name=\"{lifePowerOn}-value\" device=\"{device_path}\"}} {value}")
        if key == powerHours:
            out.append(f"{device_key}{{name=\"{powerHours}-value\" device={device_path}}} {value}")
        if key == logicSecWr:
            out.append(f"{device_key}{{name=\"{logicSecWr}-value\" device=\"{device_path}\"}} {value}")
        if key == numOfWr:
            out.append(f"{device_key}{{name=\"{numOfWr}-value\" device=\"{device_path}\"}} {value}")
        if key == logicSecRe:
            out.append(f"{device_key}{{name=\"{logicSecRe}-value\" device=\"{device_path}\"}} {value}")
        if key == numOfRe:
            out.append(f"{device_key}{{name=\"{numOfRe}-value\" device=\"{device_path}\"}} {value}")
        if key == numOfRepUncrErr:
            out.append(f"{device_key}{{name=\"{numOfRepUncrErr}-value\" device=\"{device_path}\"}} {value}")
        if key == acceptComplt:
            out.append(f"{device_key}{{name=\"{acceptComplt}-value\" device=\"{device_path}\"}} {value}")
        if key == tempVal:
            out.append(f"{device_key}{{name=\"{tempVal}-value\" device=\"{device_path}\"}} {value}")
        if key == crcErrors:
            out.append(f"{device_key}{{name=\"{crcErrors}-value\" device=\"{device_path}\"}} {value}")
        if key == endIndic:
            out.append(f"{device_key}{{name=\"{endIndic}-value\" device=\"{device_path}\"}} {value}")

    return out


def print_for_exporter_format_sat(data):
    """
    Output print_for_exporter_format_ata fot node_exporter ata type disks
    :param data: data
    :return: string
    """
    smart_status = 'smart_status'
    model_name = data.get('info', {}).get('model_name')
    serial_number = data.get('info', {}).get('serial_number')
    Reserved_Block_Pct = 'Reserved_Block_Pct'
    Raw_Read = 'Raw_Read_Error_Rate'
    Avg_BlockErase_Count = 'Avg_Block-Erase_Count'
    Temperature_Celsius = 'Temperature_Celsius'
    Reallocated = 'Reallocated_Sector_Ct'
    Current_Pending_Sector = 'Current_Pending_Sector'
    Hours = 'Power_On_Hours'
    Power_Cycle = 'Power_Cycle_Count'
    Avail_Space = 'Available_Reservd_Space'
    Prog_Fail = 'Program_Fail_Count'
    Erase_Fail = 'Erase_Fail_Count'
    Unsafe_Shut = 'Unsafe_Shutdown_Count'
    Power_Loss = 'Power_Loss_Cap_Test'
    SATA_Downshift = 'SATA_Downshift_Count'
    E_t_E_Error = 'End-to-End_Error_Count'
    Uncorrected_Err = 'Uncorrectable_Error_Cnt'
    Temp_Case = 'Temperature_Case'
    Pend_Sec = 'Pending_Sector_Count'
    CRC_Error = 'CRC_Error_Count'
    Media_Wearout = 'Media_Wearout_Indicator'
    Throughput_Performance = 'Throughput_Performance'
    Start_Stop_Count = 'Start_Stop_Count'
    Seek_Error_Rate = 'Seek_Error_Rate'
    Seek_Time_Performance = 'Seek_Time_Performance'
    Spin_Retry_Count = 'Spin_Retry_Count'


    out = []
    for key, data_value in data.items():
        if not isinstance(data_value, dict):
            continue
        metrics_key = f"smartmon_device_smart"
        device_key = metrics_key.lower()

        value = data_value.get("value", {})
        rawVal = data_value.get("raw", {})
        devPath = data.get('device', {}).get('name')
        if key == smart_status:
            out.append(f"{device_key}{{name=\"smart_status\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(data_value.get('passed',{}))}")
        if key == Spin_Retry_Count:
            out.append(f"{device_key}{{name=\"spin_retry_count\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == Seek_Time_Performance:
            out.append(f"{device_key}{{name=\"seek_time_performance\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == Seek_Error_Rate:
            out.append(f"{device_key}{{name=\"seek_error_rate\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == Start_Stop_Count:
            out.append(f"{device_key}{{name=\"start_stop_count\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == Throughput_Performance:
            out.append(f"{device_key}{{name=\"throughput_performance\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == E_t_E_Error:
            out.append(f"{device_key}{{name=\"end-to-end_error\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == Temperature_Celsius:
            out.append(f"{device_key}{{name=\"temperature\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(rawVal.split(' ')[0])}")
        if key == Avg_BlockErase_Count:
            out.append(f"{device_key}{{name=\"{Avg_BlockErase_Count.lower()}\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == Raw_Read:
            out.append(f"{device_key}{{name=\"{Raw_Read.lower()}\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == Reserved_Block_Pct:
            out.append(f"{device_key}{{name=\"{Reserved_Block_Pct.lower()}\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == Hours:
            out.append(f"{device_key}{{name=\"{Hours.lower()}\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(rawVal)}")
        if key == Power_Cycle:
            out.append(f"{device_key}{{name=\"{Power_Cycle.lower()}\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == Avail_Space:
            out.append(f"{device_key}{{name=\"{Avail_Space.lower()}\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == Prog_Fail:
            out.append(f"{device_key}{{name=\"{Prog_Fail.lower()}\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == Erase_Fail:
            out.append(f"{device_key}{{name=\"{Erase_Fail.lower()}\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == Unsafe_Shut:
            out.append(f"{device_key}{{name=\"{Unsafe_Shut.lower()}\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == Power_Loss:
            out.append(f"{device_key}{{name=\"{Power_Loss.lower()}\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == SATA_Downshift:
            out.append(f"{device_key}{{name=\"{SATA_Downshift.lower()}\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == E_t_E_Error:
            out.append(f"{device_key}{{name=\"{E_t_E_Error.lower()}\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == Uncorrected_Err:
            out.append(f"{device_key}{{name=\"{Uncorrected_Err.lower()}\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == Pend_Sec:
            out.append(f"{device_key}{{name=\"{Pend_Sec.lower()}\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == CRC_Error:
            out.append(f"{device_key}{{name=\"{CRC_Error.lower()}\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == Media_Wearout:
            out.append(f"{device_key}{{name=\"{Media_Wearout.lower()}\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == Reallocated:
            out.append(f"{device_key}{{name=\"{Reallocated.lower()}\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")
        if key == Temp_Case:
            out.append(f"{device_key}{{name=\"temperature\", device=\"{devPath}\", device_model=\"{model_name}\", serial_number=\"{serial_number}\"}} {int(value)}")

    return out


def print_for_exporter_format_scsi(data):
    """
    Output print_for_exporter_format_scsi fot node_exporter scsi type disks
    :param data: data
    :return: string
    """
    mdlName = data.get('model_name')
    serNum = data.get('serial_number', {})
    out = []
    devPathScsi = data.get('device', {}).get('name')
    for key, value in data.items():
        if not isinstance(value, dict):
            continue
        devKey = "smartmon_device_smart"
        smartSt = 'smart_status'
        powTime = 'power_on_time'
        temp = 'temperature'
        userCap = 'user_capacity'
        scsi_error_counter_log = 'scsi_error_counter_log'
        re = data.get('scsi_error_counter_log', {}).get('read', {})
        ver = data.get('scsi_error_counter_log', {}).get('verify', {})
        wr = data.get('scsi_error_counter_log', {}).get('write', {})
        corrAlgInv = 'correction_algorithm_invocations'
        errCorrEccDl = 'errors_corrected_by_eccdelayed'
        errCorrEccFst = 'errors_corrected_by_eccfast'
        errCorrReWr = 'errors_corrected_by_rereads_rewrites'
        totalErrCorrd = 'total_errors_corrected'
        totalUncurErr = 'total_uncorrected_errors'
        if key == smartSt:
            out.append(f"{devKey}{{name=\"{smartSt.lower()}\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {int(value.get('passed'))}")
        if key == powTime:
            out.append(f"{devKey}{{name=\"{powTime.lower()}\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {value.get('hours')}")
        if key == temp:
            out.append(f"{devKey}{{name=\"{temp.lower()}\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {value.get('current')}")
        if key == userCap:
            out.append(f"{devKey}{{name=\"{userCap.lower()}\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {value.get('bytes')}")
        if key == scsi_error_counter_log:
            # read
            out.append(f"{devKey}{{name=\"{corrAlgInv.lower()}-read\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {re.get(corrAlgInv)}")
            out.append(f"{devKey}{{name=\"{errCorrEccDl.lower()}-read\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {re.get(errCorrEccDl)}")
            out.append(f"{devKey}{{name=\"{errCorrEccFst.lower()}-read\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {re.get(errCorrEccFst)}")
            out.append(f"{devKey}{{name=\"{errCorrReWr.lower()}-read\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {re.get(errCorrReWr)}")
            out.append(f"{devKey}{{name=\"{totalErrCorrd.lower()}-read\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {re.get(totalErrCorrd)}")
            out.append(f"{devKey}{{name=\"{totalUncurErr.lower()}-read\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {re.get(totalUncurErr)}")
            # verify
            out.append(f"{devKey}{{name=\"{corrAlgInv.lower()}-verify\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {ver.get(corrAlgInv)}")
            out.append(f"{devKey}{{name=\"{errCorrEccDl.lower()}-verify\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {ver.get(errCorrEccDl)}")
            out.append(f"{devKey}{{name=\"{errCorrEccFst.lower()}-verify\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {ver.get(errCorrEccFst)}")
            out.append(f"{devKey}{{name=\"{errCorrReWr.lower()}-verify\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {ver.get(errCorrReWr)}")
            out.append(f"{devKey}{{name=\"{totalErrCorrd.lower()}-verify\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {ver.get(totalErrCorrd)}")
            out.append(f"{devKey}{{name=\"{totalUncurErr.lower()}-verify\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {ver.get(totalUncurErr)}")
            # write
            out.append(f"{devKey}{{name=\"{corrAlgInv.lower()}-write\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {wr.get(corrAlgInv)}")
            out.append(f"{devKey}{{name=\"{errCorrEccDl.lower()}-write\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {wr.get(errCorrEccDl)}")
            out.append(f"{devKey}{{name=\"{errCorrEccFst.lower()}-write\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {wr.get(errCorrEccFst)}")
            out.append(f"{devKey}{{name=\"{errCorrReWr.lower()}-write\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {wr.get(errCorrReWr)}")
            out.append(f"{devKey}{{name=\"{totalErrCorrd.lower()}-write\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {wr.get(totalErrCorrd)}")
            out.append(f"{devKey}{{name=\"{totalUncurErr.lower()}-write\", device=\"{devPathScsi}\", device_model=\"{mdlName}\", serial_number=\"{serNum}\"}} {wr.get(totalUncurErr)}")


    return out


def print_device_data(data):
    """
    Output for node_exporter info device
    :param data:
    :return: string
    """
    out = []
    device_path = data.get('device', {}).get('name')

    for key, value in data.items():
        device_key = f"smartmon_device_smart_{key}"
        if isinstance(value, dict):
            if key == 'wwn':
                out.append(
                    f"{device_key}{{name=\"wwn_id\", device=\"{device_path}\"}} {value.get('id',{})}")
            if key == 'sata_version':
                out.append(
                    f"{device_key}{key}{{name=\"sata_version\", device=\"{device_path}\"}} {value.get('string',{})}")
        else:
            if key == 'model_name':
                out.append(
                    f"{device_key}{{name=\"model_name\", device=\"{device_path}\"}} {value}")
            if key == 'serial_number':
                out.append(
                    f"{device_key}{key}{{name=\"serial_number\", device=\"{device_path}\"}} {value}")
            if key == 'firmware_version':
                out.append(
                    f"{device_key}{{name=\"firmware_version\", device=\"{device_path}\"}} {value}")

    return out


if __name__ == '__main__':
    device_scsi = get_device(device_scan_scsi())
    device_sat = get_device(device_scan_sat())
    device_nvme = get_device(device_scan(id_dev='-d nvme'))
    output = []
    for dev in device_sat:
        output.append(print_for_exporter_format_sat(sat_device_statistics_pages(collect_error_count(dev, id_dev='-d sat'))))
    for dev in device_scsi:
        output.append(print_for_exporter_format_scsi(scsi_device_statistics_pages(collect_error_count(dev, id_dev='-d auto'))))
    for dev in device_nvme:
        output.append(print_for_exporter_format_nvme(nvme_device_statistics_pages(collect_error_count(dev, id_dev='-d nvme'))))

    out = '\n'.join(item
        for items in output
        for item in items)
    print(out)

"""
        Copies files and gathers output from a DUT or DUTs to aid in testing

USAGE: 
      basic_output_gather.py test_id when (-d FQDN / IP | -f file_of_IPs) [-z] 

      Either specify a device IP / hostname or a file containing a list of IPs / hostnames
      'when': i.e. whether the output is gathered: before, during or after a test is executed. 

OUTPUT COMMANDS:
      Place text files in 'output_commands' directory containing CLI commands.
      These commands will all be executed on the DUT(s) to gather 
      the output to support your testing.
      Use different files in this directory to structure the output.  e.g.
      place all BGP commands in a 'bgp.txt' file.  When output is gathered
      all output per DUT will then be stored in a 'bgp.txt' out file.

"""

import sys
import lxml.etree
import os 
import argparse
import tarfile
import shutil

from getpass import getpass
from jnpr.junos import Device
from jnpr.junos.utils.scp import SCP

# Gather CLI arguments

parser = argparse.ArgumentParser(description="Gather router CLI output and scp files from a router."
                                             "Use to document testing")
parser.add_argument('-d', '--device', help="Single IP of: router, switch, firewall etc that is being tested")
parser.add_argument('-f', '--device_file', help="File with list of IPs of devices to test.  Mutually exclusive with -d")
parser.add_argument('test_id', help="Name of test being executed e.g '1.1.1-Blah'")
parser.add_argument('output_time', help="When output is being gathered e.g. 'pre', 'during' or 'post' test execution")
parser.add_argument('-z', action='store_true', help="Archive results into a zipped tarball")
args = parser.parse_args()
test_id = args.test_id
output_time = args.output_time
dut = args.device
dut_files = args.device_file
tozip = args.z

# Functions


def read_file(filename):
    """Read files and return a list with each line as an item.
    Ignore hashed out (i.e. #) lines"""
    file_lines = []
    with open(filename) as file_raw:
        for line in file_raw.readlines():
            if not line.startswith('#'):
                line = line.rstrip()
                file_lines.append(line)
    return file_lines


def write_file(dev, filename, cmd_list, directory):
    """Execute commands on the router and write command output to a file separated with a line of '=' """
    print "=" * 100
    print "Executing commands listed in file: %s on %s" % (filename, dut)
    with open(directory + filename, "w") as a_file:
        for cmd in cmd_list:
            a_file.write("=" * 100 + "\n")
            a_file.write(cmd + "\n")
            a_file.write(dev.cli(cmd, warning=False))
    print "%s commands written to %s%s" % (filename, directory, filename)


def router_connect(dut):
    if not os.path.exists(DIRECTORY + dut):
        os.makedirs(DIRECTORY + dut)
    directory = DIRECTORY + dut + "/"
    # connect to device
    dev = Device(dut, user='danny')
    dev.open()
    print "=" * 100
    print "Device  hostname is '%s'\n\nSoftware version is '%s'\n" % (dev.facts['hostname'], dev.facts['version'])
    # Output some basic info about the DUT to stdout 
    alarms = dev.rpc.get_alarm_information()
    alarm_desc = alarms.findall('.//alarm-description')
    if alarm_desc:
        print "=" * 100
        print "There are chassis alarms:"
        for alarm in alarm_desc:
            print alarm.text
        print "=" * 100 
    re_info = dev.rpc.get_route_engine_information()
    one_min = re_info.find('.//load-average-one').text
    five_min = re_info.find('.//load-average-five').text
    fifteen_min = re_info.find('.//load-average-fifteen').text
    print "=" * 100
    print "Load Averages:    %s    %s    %s" % (one_min, five_min, fifteen_min)
    print "=" * 100
    # SCP log files off the router
    scp_list = read_file('scp.txt')
    with SCP(dev, progress=True) as scp:
        print "scp-ing log files off %s  ...\n" % dut
        for scp_file in scp_list:
            scp.get('/var/log/' + scp_file, directory + scp_file)
    # Get commands to run from text files and output to specified directory
    for file_name in os.listdir('./output_commands'):
        cmd_list = read_file('./output_commands' + '/' + file_name)
        write_file(dev, file_name, cmd_list, directory)
    dev.close()

# Main body

# Create output directories
if not os.path.exists(test_id):
    os.makedirs(test_id)
    if not os.path.exists(test_id + '/' + output_time):
        os.makedirs(test_id + '/' + output_time)
DIRECTORY = test_id + '/' + output_time + '/'

print '#' * 100
print "Script will write output to %s" % DIRECTORY

# Run the main output gathering function
if dut:
    router_connect(dut)
elif dut_files:
    with open(dut_files) as fh:
        duts = fh.read().splitlines()
    for dut in duts:
        router_connect(dut)
else:
    print "No DUT specified existing..."
    sys.exit()

if tozip:
    print '=' * 100 + '\n' + "zipping test results"
    with tarfile.open(test_id + '.tgz', 'w:gz') as tar:
        tar.add(DIRECTORY, arcname=os.path.basename(DIRECTORY))
    shutil.rmtree(test_id, ignore_errors=False, onerror=None)

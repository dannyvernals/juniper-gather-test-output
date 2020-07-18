# Juniper Gather Output

This (very hacky) python 2.7 script uses the PyEZ library to run arbitrary CLI commands
on a router or routers.  It's a quick and dirty way to automate some of your output
gathering when executing repeated tests.

## Help
Output Commands:

        Place text files in 'output_commands' directory containing CLI commands.
        These commands will all be executed on the DUT(s) to gather 
        the output to support your testing.
        Use different files in this directory to structure the output.  e.g.
        place all BGP commands in a 'bgp.txt' file.  When output is gathered
        all output per DUT will then be stored in a 'bgp.txt' out file.

Usage:

        basic_output_gather.py test_id output_time (-d FQDN / IP | -f file_of_IPs) [-z]
        Either specify a device IP / hostname or a file containing a list of IPs / hostnames
        'when': i.e. whether the output is gathered: before, during or after a test is executed.


Positional arguments:

    test_id               Name of test being executed e.g '1.1.1-Blah'
    output_time           When output is being gathered e.g. 'pre', 'during' or
                          'post' test execution

Optional arguments:

    -h, --help          show this help message and exit
    -d DEVICE, --device DEVICE
                        Single IP of: router, switch, firewall etc that is
                        being tested
    -f DEVICE_FILE, --device_file DEVICE_FILE
                        File with list of IPs of devices to test. Mutually
                        exclusive with -d
    -z                  Archive results into a zipped tarball


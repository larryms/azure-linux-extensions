import os
import os.path
import re
import rstr
import sys
import xeger

from omsData import *
from verify_e2e import check_e2e

operation = None

def main():
    # Determine the operation being executed
    global operation
    try:
        option = sys.argv[1]
        if re.match('^([-/]*)(createvm)', option):
            operation = 'Create VM'
        elif re.match('^([-/]*)(addext)', option):
            operation = 'Add Extension'
        elif re.match('^([-/]*)(vmandext)', option):
            operation = 'Create VM and Add Extension'
        elif re.match('^([-/]*)(verifydata)', option):
            operation = 'Verify Data'
        elif re.match('^([-/]*)(removeext)', option):
            operation = 'Remove Extension'
        elif re.match('^([-/]*)(deletevm)', option):
            operation = 'Delete VM'
    except:
        if operation is None:
            print "No operation specified. run with 'preinstall' or 'postinstall'"

    run_operation()


def copy_to_vm(dnsname, username, password, location):
    os.system("pscp -pw {} -r omsStatusCheck.py {}@{}.{}.cloudapp.azure.com:/tmp/".format(password, username, dnsname.lower(), location))
    #os.system("pscp -pw {} -r oms*.conf {}@{}.{}.cloudapp.azure.com:/tmp/".format(password, username, dnsname.lower(), location))

def copy_from_vm(dnsname, username, password, location):
    os.system("pscp -pw {} -r {}@{}.{}.cloudapp.azure.com:/tmp/omsresults.* .".format(password, username, dnsname.lower(), location))

def run_command(resourcegroup, vmname, commandid, script):
    os.system('az vm run-command invoke -g {} -n {} --command-id {} --scripts "{}" --debug'.format(resourcegroup, vmname, commandid, script))

def create_vm(resourcegroup, vmname, image, username, password, location, dnsname, vmsize, networksecuritygroup):
    os.system('az vm create -g {} -n {} --image {} --admin-username {} --admin-password {} --location {} --public-ip-address-dns-name {} --size {} --nsg {} --debug'.format(resourcegroup, vmname, image, username, password, location, dnsname, vmsize, networksecuritygroup))

def add_extension(extension, publisher, vmname, resourcegroup, private_settings, public_settings):
    os.system('az vm extension set -n {} --publisher {} --vm-name {} --resource-group {} --protected-settings "{}" --settings "{}" --debug'.format(extension, publisher, vmname, resourcegroup, private_settings, public_settings))

def remove_extension(extension, vmname, resourcegroup):
    os.system('az vm extension delete -n {} --vm-name {} --resource-group {} --debug'.format(extension, vmname, resourcegroup))

def delete_vm(resourcegroup, vmname):
    os.system('az vm delete -g {} -n {} --yes --debug'.format(resourcegroup, vmname))

def run_operation():
    for vmname, image in images.iteritems():
        print "\n{} - {}: {} \n".format(operation, vmname, image)
        uid = rstr.xeger(r'[0-9a-fA-F]{8}')
        vmname = vmname.lower() + '-' + uid
        dnsname = vmname
        if operation == 'Create VM and Add Extension':
            create_vm(rGroup, vmname, image, username, password, location, dnsname, size, nsg)
            remove_extension(extension, vmname, rGroup)
            copy_to_vm(dnsname, username, password, location)
            run_command(rGroup, vmname, 'RunShellScript', 'python /tmp/omsStatusCheck.py -preinstall')
            add_extension(extension, publisher, vmname, rGroup, private_settings, public_settings)
            run_command(rGroup, vmname, 'RunShellScript', 'python /tmp/omsStatusCheck.py -postinstall')
            copy_from_vm(dnsname, username, password, location)
        elif operation == 'Create VM':
            create_vm(rGroup, vmname, image, username, password, location, dnsname, size, nsg)
        elif operation == 'Add Extension':
            add_extension(extension, publisher, vmname, rGroup, private_settings, public_settings)
            run_command(rGroup, vmname, 'RunShellScript', 'python /tmp/omsStatusCheck.py -status')
            copy_from_vm(dnsname, username, password, location)
        elif operation == 'Verify Data':
            check_e2e(vmname)
        elif operation == 'Remove Extension':
            remove_extension(extension, vmname, rGroup)
            run_command(rGroup, vmname, 'RunShellScript', 'python /tmp/omsStatusCheck.py -status')
            copy_from_vm(dnsname, username, password, location)
        elif operation == 'Delete VM':
            delete_vm(rGroup, vmname)


if __name__ == '__main__' :
    main()

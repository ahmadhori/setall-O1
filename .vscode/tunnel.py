from subprocess import Popen
import boto3
import os
import argparse


def get_bastion_public_dns(env):
    dns = None
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_instances()
    for reservation in response["Reservations"]:
        if dns is not None:
            break
        for instance in reservation["Instances"]:
            try:
                instance['Tags']
            except:
                continue
            for tag in instance['Tags']:
                if tag['Key'] == 'Name' and 'bastion' in tag['Value'] and env in tag['Value']:
                    dns = instance['PublicDnsName']
                    return dns


def get_ec2_instance(filter_list=[]):
    dns = None
    response = ec2_client.describe_instances()
    for reservation in response["Reservations"]:
        if dns is not None:
            break
        for instance in reservation["Instances"]:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name' and all(f in tag['Value'].split('-') for f in filter_list):
                    print('Find instance ' + tag['Value'])
                    return instance['PrivateDnsName']


def create_pem_file(data_dir='', environment=''):
    key = ''
    key = get_key_ssm()
    if key:
        print('Found inception key!')
        print(key)
    else:
        print('SSH Key not found')

    try:
        os.remove(os.path.join(data_dir, environment + '.pem'))
    except OSError:
        pass
    with open(os.path.join(data_dir, environment+'.pem'), 'w+') as file:
        file.write(key)
    os.chmod(os.path.join(data_dir, environment + '.pem'), 0o400)


def get_rds_instance(filter_list=[]):
    db_client = boto3.client('rds')
    response = db_client.describe_db_instances()
    for instance in response['DBInstances']:
        if all(f in instance['DBInstanceIdentifier'].split('-') for f in filter_list):
            return instance['Endpoint']['Address']


def get_key_ssm():
    ssm_client = boto3.client('ssm')
    key = ssm_client.get_parameter(Name='/BASTION/KEY', WithDecryption=True)
    return key['Parameter']['Value']


def build_tunnel_command(resource, local_port, data_dir='', filter_list=[], environment='', target_port=None):
    create_pem_file(data_dir=data_dir, environment=environment)
    command = 'ssh -o StrictHostKeyChecking=no -i {}.pem -N -L {}:{}:{} ubuntu@{}'

    if resource == 'ec2':
        port = '3389'
        if target_port:
            port = str(target_port)
        print('Resouce EC2')
        command = command.format(os.path.join(data_dir, environment), local_port, get_ec2_instance(filter_list=filter_list), port, get_bastion_public_dns())
        print(command)
    else:
        port = '5432'
        if target_port:
            port = str(target_port)
        print('Resouce RDS')
        command = command.format(os.path.join(data_dir, environment), local_port, get_rds_instance(filter_list=filter_list), port, get_bastion_public_dns(environment))
        print(command)
    return command


if __name__ == '__main__':
    command = build_tunnel_command(data_dir=os.path.expanduser('~') + '/.ssh', resource='rds', local_port='54329', filter_list=['recommend'], target_port=None, environment='prd')
    p = Popen(command.split())  # something long running

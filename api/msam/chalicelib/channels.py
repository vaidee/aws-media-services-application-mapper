# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
This file contains helper functions related to channels.
"""

import os
from urllib.parse import unquote

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

import chalicelib.settings as msam_settings

# table names generated by CloudFormation
CHANNELS_TABLE_NAME = os.environ["CHANNELS_TABLE_NAME"]

# DynamoDB
DYNAMO_RESOURCE = boto3.resource("dynamodb")


def delete_channel_nodes(request, name):
    """
    API entry point to delete a channel.
    """
    try:
        name = unquote(name)
        table_name = CHANNELS_TABLE_NAME
        table = DYNAMO_RESOURCE.Table(table_name)
        print(request.method)
        try:
            # get the settings object
            response = table.query(KeyConditionExpression=Key('channel').eq(name))
            print(response)
            # return the response or an empty object
            if "Items" in response:
                for item in response["Items"]:
                    table.delete_item(Key={"channel": item["channel"], "id": item["id"]})
            name_list = msam_settings.get_setting("channels")
            if not name_list:
                name_list = []
            if name in name_list:
                name_list.remove(name)
                msam_settings.put_setting("channels", name_list)
            print("channel items deleted, channel list updated")
        except ClientError:
            print("not found")
        response = {"message": "done"}
    except ClientError as outer_error:
        # send the exception back in the object
        print(outer_error)
        response = {"exception": str(outer_error)}
    return response


def get_channel_list():
    """
    Return all the current channel names.
    """
    channels = msam_settings.get_setting("channels")
    if not channels:
        channels = []
    return channels


def set_channel_nodes(request, name):
    """
     API entry point to set the nodes for a given channel name.
    """
    try:
        name = unquote(name)
        table = DYNAMO_RESOURCE.Table(CHANNELS_TABLE_NAME)
        print(request.json_body)
        node_ids = request.json_body
        # write the channel nodes to the database
        for node_id in node_ids:
            item = {"channel": name, "id": node_id}
            table.put_item(Item=item)
        # update the list of channels in settings
        name_list = msam_settings.get_setting("channels")
        if not name_list:
            name_list = []
        if name not in name_list:
            name_list.append(name)
            msam_settings.put_setting("channels", name_list)
        result = {"message": "saved"}
        print(result)
    except ClientError as error:
        # send the exception back in the object
        print(error)
        result = {"exception": str(error)}
    return result


def get_channel_nodes(request, name):
    """
    API entry point to get the nodes for a given channel name.
    """
    try:
        name = unquote(name)
        table_name = CHANNELS_TABLE_NAME
        table = DYNAMO_RESOURCE.Table(table_name)
        print(request.method)
        try:
            # get the settings object
            response = table.query(KeyConditionExpression=Key('channel').eq(name))
            print(response)
            # return the response or an empty object
            if "Items" in response:
                settings = response["Items"]
            else:
                settings = []
            print("retrieved")
        except ClientError:
            print("not found")
            settings = []
    except ClientError as outer_error:
        # send the exception back in the object
        print(outer_error)
        settings = {"exception": str(outer_error)}
    return settings

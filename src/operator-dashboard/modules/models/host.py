
# Copyright IBM Corp, All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
import logging
from enum import Enum

from marshmallow import Schema, fields
from parse_client.datatypes import Object
import time

logger = logging.getLogger(__name__)

LOG_LEVEL = Enum("LOG_LEVEL", ("INFO", "DEBUG", "NOTICE",
                               "WARNING", "ERROR", "CRITICAL"))

CLUSTER_STATE = Enum("CLUSTER_STATE", ("active", "released"))
CLUSTER_STATUS = Enum("CLUSTER_STATUS", ("running", "stopped"))


class Host(Object):
    # id = StringField(default="", primary_key=True)
    # name = StringField(default="")
    # worker_api = StringField(default="")
    # create_ts = DateTimeField(default=datetime.datetime.now)
    # status = StringField(default="active")
    # type = StringField(default="")
    # log_level = StringField(default=LOG_LEVEL.INFO.name)
    # log_type = StringField(default="")
    # log_server = StringField(default="")
    # autofill = BooleanField(default=False)
    # schedulable = BooleanField(default=False)
    # capacity = IntField(default=0)
    # clusters = ListField(default=[])
    # vcparam = DictField(default={})
    # k8s_param = DictField(default={})
    pass


class Cluster(Object):
    # id = StringField(default="", primary_key=True)
    # name = StringField(default="")
    # duration = IntField(default=0)
    # network_type = StringField(default="")
    # mapped_ports = DictField(default={})
    # service_url = DictField(default={})
    # containers = DictField(default={})
    # size = IntField(default=0)
    # release_ts = DateTimeField()
    # health = StringField(default="")
    # create_ts = DateTimeField(default=datetime.datetime.now)
    # apply_ts = DateTimeField()
    # worker_api = StringField(default="")
    # status = StringField(default=CLUSTER_STATUS.running.name)
    # state = StringField(default=CLUSTER_STATE.active.name)
    # # host = ReferenceField(Host, default=None)
    # user_id = StringField(default="")
    # api_url = StringField(default="")
    # env = DictField(default={})
    # consensus_plugin = StringField(default="")
    pass


class Container(Object):
    # id = StringField(default="", primary_key=True)
    # name = StringField(default="")
    # cluster = ReferenceField(Cluster, reverse_delete_rule=CASCADE)
    pass


class ServicePort(Object):
    # port = IntField(default=0)
    # ip = StringField(default="")
    # name = StringField(default="")
    # cluster = ReferenceField(Cluster, reverse_delete_rule=CASCADE)
    pass


class ClusterSchema(Schema):
    id = fields.String()
    name = fields.String()
    duration = fields.Number()
    network_type = fields.String()
    mapped_ports = fields.Dict()
    service_url = fields.Dict()
    containers = fields.Dict()
    size = fields.Integer()
    release_ts = fields.DateTime()
    health = fields.String()
    create_ts = fields.Method("format_create_ts")
    apply_ts = fields.DateTime()
    worker_api = fields.String()
    status = fields.String()
    host = fields.Method("get_host_name")
    host_id = fields.Method("get_host_id")
    user_id = fields.String()
    api_url = fields.String()
    consensus_plugin = fields.String()
    containers = fields.Method("get_containers")
    service_ports = fields.Method("get_service_ports")

    def get_host_name(self, cluster):
        return cluster.host.name if cluster.host else ""

    def get_host_id(self, cluster):
        return str(cluster.host.id) if cluster.host else ""

    def format_create_ts(self, cluster):
        return time.mktime(cluster.createdAt.timetuple())

    def format_apply_ts(self, cluster):
        return cluster.apply_ts.strftime("%a, %d %b %Y %H:%M:%S")

    def get_containers(self, cluster):
        return [container.name for container in
                Container.Query.filter(cluster=cluster.as_pointer)]

    def get_service_ports(self, cluster):
        return [
            service_port.port for service_port in
            ServicePort.Query.filter(
                cluster=cluster.as_pointer).order_by('port')]


class HostSchema(Schema):
    objectId = fields.String()
    id = fields.String()
    name = fields.String()
    worker_api = fields.String()
    create_ts = fields.Method("format_create_ts", dump_only=True)
    status = fields.String()
    type = fields.String()
    log_level = fields.String()
    log_type = fields.String()
    log_server = fields.String()
    autofill = fields.Method("format_autofill", dump_only=True)
    schedulable = fields.Method("format_schedulable", dump_only=True)
    clusters = fields.Method("get_clusters", dump_only=True)
    capacity = fields.Integer()

    def format_autofill(self, host):
        return "true" if host.autofill else "false"

    def format_create_ts(self, host):
        return time.mktime(host.createdAt.timetuple())

    def format_schedulable(self, host):
        return "true" if host.schedulable else "false"

    def get_clusters(self, host):
        clusters = Cluster.Query.filter(host=host.as_pointer)

        return [str(cluster.id) for cluster in clusters]

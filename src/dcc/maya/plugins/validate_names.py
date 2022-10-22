import re

import pyblish.api

from dcc.maya.api.cmds import Maya

from maya import cmds


class SelectInvalidNameNodes(pyblish.api.Action):
    label = "Select node"
    on = "failed"
    icon = "hand-o-up"

    def process(self, context, plugin):

        for result in context.data["results"]:
            if result["error"]:
                instance = result['instance']
                shape_node = instance.data.get("output", {}).get('node')
                cmds.select(shape_node)


class ValidateNamespaces(pyblish.api.InstancePlugin):
    """
    To validate and removing all namespaces in current file
    """

    order = pyblish.api.ValidatorOrder + 0.10

    optional = True
    label = "remove namespaces"
    hosts = ["maya"]
    families = ["model"]
    active = True

    def process(self, instance):
        self.log.info("Initialize validation of namespaces")
        ma = Maya()
        ma.remove_all_namespaces()


class ValidateNaming(pyblish.api.InstancePlugin):
    """
    To validate the naming conventional of nodes
    """

    order = pyblish.api.ValidatorOrder + 0.11

    optional = True
    label = "check naming conventional"
    hosts = ["maya"]
    families = ["model"]
    active = True
    actions = [SelectInvalidNameNodes]

    def process(self, instance):
        self.log.info("Initialize naming conventional")

        invalid_names = ["polySurface", "StandardSurface"]

        ma = Maya()
        for shape_node in instance:
            shape_name = shape_node.rsplit('|', 1)[-1]

            for name in invalid_names:
                if re.findall(r"(?i)" + name, shape_name):
                    instance.set_data("output", {'node': shape_node})
                    msg = f"'{shape_name}' name is not allowed!"
                    self.log.error(msg)
                    raise pyblish.api.ValidationError(msg)

            sgs = ma.list_all_DG_nodes(shape_node)
            for sg_node in sgs:
                # add suffix SG
                if sg_node == 'initialShadingGroup':
                    continue
                sg_name = re.findall(r'(?i)sg', sg_node)
                if not sg_name:
                    new_name = sg_node + "SG"

                else:
                    new_name = re.sub(r'(?i)sg', sg_name[0].upper(), sg_node)

                # remove underscore
                new_name = "".join([x.capitalize() for x in new_name.split("_")])

                cmds.rename(sg_node, new_name)

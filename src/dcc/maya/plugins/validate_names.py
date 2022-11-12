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
                invalid_nodes = instance.data.get("output", {}).get('invalid_nodes', [])
                cmds.select([x.get('node') for x in invalid_nodes if x])


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

        # Not allowed names
        invalid_names = ["polySurface", "StandardSurface"]
        invalid_nodes_names = []
        ma = Maya()
        for shape_node in instance:
            shape_name = shape_node.rsplit('|', 1)[-1]

            for name in invalid_names:
                if re.findall(r"(?i)" + name, shape_name):
                    invalid_nodes = {'node': shape_node}
                    invalid_nodes_names.append(invalid_nodes)

            # rename all shadings groups
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

        if invalid_nodes_names:
            instance.set_data("output", invalid_nodes_names)
            msg = f"'Some nodes names is not allowed! '{invalid_nodes_names}'"
            self.log.error(msg)
            raise pyblish.api.ValidationError(msg)
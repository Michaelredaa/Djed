import pyblish.api

from dcc.maya.api.cmds import Maya

from maya import cmds


class SelectInvalidMTLNodes(pyblish.api.Action):
    label = "Select node"
    on = "failed"
    icon = "hand-o-up"

    def process(self, context, plugin):

        for result in context.data["results"]:
            if result["error"]:
                instance = result['instance']
                shape_node = instance.data.get("output", {}).get('node')
                cmds.select(shape_node)


class SplitPerMaterials(pyblish.api.Action):
    label = "Split object by materials"
    on = "failed"
    icon = "hand-o-up"

    def process(self, context, plugin):

        ma = Maya()
        for result in context.data["results"]:
            for record in result["records"]:
                print(record.levelno)
            if result["error"]:
                self.log.info("Split object by materials")

                instance = result['instance']
                shape_node = instance.data.get("output", {}).get('node')
                ma.split_by_material(shape_node, keep_original=1)


class ValidateShadingGroups(pyblish.api.InstancePlugin):
    """
    To validate the binding shading groups on geometry
    """

    order = pyblish.api.ValidatorOrder + 0.20

    optional = True
    label = "Validate shading groups"
    hosts = ["maya"]
    families = ["model"]
    active = True
    actions = [SelectInvalidMTLNodes, SplitPerMaterials]

    def process(self, instance):
        self.log.info("Initialize validation binding materials")

        ma = Maya()
        for shape_node in instance:
            shape_name = shape_node.rsplit('|', 1)[-1]

            sgs = ma.list_all_DG_nodes(shape_node)

            msg = ''
            if len(sgs) == 0:
                instance.set_data("output", {'node': shape_node, 'sgs': sgs})
                msg = f"'{shape_name}' have no shading group."

            elif len(sgs) != 1:
                instance.set_data("output", {'node': shape_node, 'sgs': sgs})
                msg = f"'{shape_name}' have multiple material assign on one object. sgs: {sgs}"

            elif sgs[0] == "initialShadingGroup":
                instance.set_data("output", {'node': shape_node, 'sgs': sgs})
                msg = f"'{shape_name}' have 'lambert1' material assign. ('lambert1' not allowed)"

            if msg:
                self.log.error(msg)
                raise pyblish.api.ValidationError(msg)

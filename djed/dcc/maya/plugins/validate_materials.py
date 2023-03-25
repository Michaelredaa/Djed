import pyblish.api

from dcc.maya.api.cmds import Maya

from maya import cmds


class SelectInvalidMTLNodes(pyblish.api.Action):
    label = "Select nodes"
    on = "failed"
    icon = "hand-o-up"

    def process(self, context, plugin):

        for result in context.data["results"]:
            if result["error"] and plugin == result['plugin']:
                instance = result['instance']
                invalid_nodes = instance.data.get("djed_errors", {}).get('invalid_sg_nodes', [])
                cmds.select([x.get('node') for x in invalid_nodes if x])


class SelectInvalidMultiMTLNodes(pyblish.api.Action):
    label = "Select nodes"
    on = "failed"
    icon = "hand-o-up"

    def process(self, context, plugin):

        for result in context.data["results"]:
            if result["error"] and plugin == result['plugin']:
                instance = result['instance']
                invalid_nodes = instance.data.get("djed_errors", {}).get('invalid_mtl_nodes', [])
                cmds.select([x.get('node') for x in invalid_nodes if x])


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
                invalid_nodes = instance.data.get("djed_errors", {}).get('invalid_mtl_nodes', [])
                for item in invalid_nodes:
                    ma.split_by_material(item.get('node'), keep_original=1)


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
    actions = [SelectInvalidMTLNodes]

    def process(self, instance):
        self.log.info("Initialize validation binding materials")

        ma = Maya()
        no_shading_grps = []
        lambert_shading_grps = []

        for shape_node in instance:
            sgs = ma.list_all_DG_nodes(shape_node)

            if len(sgs) == 0:
                invalid_nodes = {'node': shape_node, 'sgs': sgs}
                no_shading_grps.append(invalid_nodes)

            elif sgs[0] == "initialShadingGroup":
                invalid_nodes = {'node': shape_node, 'sgs': sgs}
                lambert_shading_grps.append(invalid_nodes)

        if 'output' not in instance:
            instance.set_data("output", {})

        if no_shading_grps:
            instance.data['djed_errors']['invalid_sg_nodes'] = no_shading_grps
            msg = f"Some nodes have no shading group '{no_shading_grps}'"
            self.log.error(msg)
            raise pyblish.api.ValidationError(msg)

        if lambert_shading_grps:
            instance.data['djed_errors']['invalid_sg_nodes'] = lambert_shading_grps
            msg = f"Some nodes have 'lambert1' material assign. ('lambert1' not allowed)'{lambert_shading_grps}'"
            self.log.error(msg)
            raise pyblish.api.ValidationError(msg)


class ValidateMultipleMaterialAssign(pyblish.api.InstancePlugin):
    """
    To validate that one object assigned on one geometry
    """

    order = pyblish.api.ValidatorOrder + 0.21

    optional = True
    label = "Validate multi material assign"
    hosts = ["maya"]
    families = ["model"]
    active = True
    actions = [SelectInvalidMultiMTLNodes, SplitPerMaterials]

    def process(self, instance):
        self.log.info("Initialize validation binding materials")

        ma = Maya()
        faces_shading_grps = []

        for shape_node in instance:
            sgs = ma.list_all_DG_nodes(shape_node)

            if len(sgs) != 1:
                invalid_nodes = {'node': shape_node, 'sgs': sgs}
                faces_shading_grps.append(invalid_nodes)

        if faces_shading_grps:
            instance.data['djed_errors']['invalid_mtl_nodes'] = faces_shading_grps
            msg = f"Some nodes have multiple material assign on one object.'{faces_shading_grps}'"
            self.log.error(msg)
            raise pyblish.api.ValidationError(msg)

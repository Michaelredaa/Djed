import pyblish.api

from dcc.maya.api.cmds import Maya
from maya import cmds


class SelectInvalidUVSetsNodes(pyblish.api.Action):
    label = "Select nodes"
    on = "failed"
    icon = "hand-o-up"

    def process(self, context, plugin):

        for result in context.data["results"]:

            if result["error"] and plugin == result['plugin']:
                instance = result['instance']
                invalid_nodes = instance.data.get("djed_errors", {}).get('invalid_uvsets_nodes', [])
                cmds.select([x.get('node') for x in invalid_nodes if x], r=1)


class SelectInvalidUVNodes(pyblish.api.Action):
    label = "Select UVs"
    on = "failed"
    icon = "hand-o-up"

    def process(self, context, plugin):

        for result in context.data["results"]:
            if result["error"] and plugin == result['plugin']:
                instance = result['instance']
                print(instance.data)
                invalid_nodes = instance.data.get("djed_errors", {}).get('invalid_uv_nodes', [])
                invalid_uvs = []
                for uvs in invalid_nodes:
                    for uv in uvs.get('uvs_on_boarders', []):
                        invalid_uvs.append(uv)

                cmds.select(invalid_uvs, r=1)


class FixUVSets(pyblish.api.Action):
    label = "Fix UV sets"
    on = "failed"
    icon = "wrench"

    def process(self, context, plugin):

        ma = Maya()

        for result in context.data["results"]:
            if result["error"] and plugin == result['plugin']:
                instance = result['instance']

                invalid_nodes = instance.data.get("djed_errors", {}).get('invalid_uvsets_nodes', [])

                for node_dict in invalid_nodes:
                    shape_node = node_dict.get('node')
                    uv_sets = node_dict.get('uv_sets')
                    if not uv_sets:
                        return

                    for uv_set in uv_sets[1:]:
                        ma.delete_uv_set(shape_node, uv_set)
                    uv_name = uv_sets[0]

                    if uv_name != "map1":
                        ma.rename_uv_set(shape_node, "map1")


class ValidateUVSets(pyblish.api.InstancePlugin):
    """
    To validate the uv sets of mesh
    """

    order = pyblish.api.ValidatorOrder + 0.01
    optional = True

    label = "Validate uv sets"
    hosts = ["maya"]
    families = ["model"]
    active = True
    actions = [SelectInvalidUVSetsNodes, FixUVSets]

    def process(self, instance):

        self.log.info("Initialize validation of uv sets")

        ma = Maya()

        no_uv_sets = []
        more_uv_sets = []
        invalid_uv_set_names = []
        for shape_node in instance:
            # check uv_sets
            uv_sets = ma.uv_sets(shape_node)

            if len(uv_sets) == 0:
                invalid_nodes = {'node': shape_node, 'uv_sets': uv_sets}
                no_uv_sets.append(invalid_nodes)

            elif len(uv_sets) != 1:
                invalid_nodes = {'node': shape_node, 'uv_sets': uv_sets}
                more_uv_sets.append(invalid_nodes)


            elif uv_sets[0] != "map1":
                invalid_nodes = {'node': shape_node, 'uv_sets': uv_sets}
                invalid_uv_set_names.append(invalid_nodes)

        if 'output' not in instance:
            instance.set_data("output", {})

        if no_uv_sets:
            instance.data['djed_errors']['invalid_uvsets_nodes'] = no_uv_sets
            msg = f"Some nodes have no uvSets'{no_uv_sets}'"
            self.log.error(msg)
            raise pyblish.api.ValidationError(msg)

        if more_uv_sets:
            instance.data['djed_errors']['invalid_uvsets_nodes'] = more_uv_sets
            msg = f"Some nodes have more than uvSets'{more_uv_sets}'"
            self.log.error(msg)
            raise pyblish.api.ValidationError(msg)

        if invalid_uv_set_names:
            instance.data['djed_errors']['invalid_uvsets_nodes'] = invalid_uv_set_names
            msg = f"uv set name must have the uv set name 'map1' '{invalid_uv_set_names}'"
            self.log.error(msg)
            raise pyblish.api.ValidationError(msg)


class ValidateUVBoarders(pyblish.api.InstancePlugin):
    """
    To validate the intersection of uv shells with boarders
    """

    order = pyblish.api.ValidatorOrder + 0.00
    optional = False
    label = "Validate uv shells on boarders"
    hosts = ["maya"]
    families = ["model"]
    active = True
    actions = [SelectInvalidUVNodes]

    def process(self, instance):

        self.log.info("Initialize validation of uv shells on boarders")

        overlapped = []

        ma = Maya()
        for shape_node in instance:
            # check uv shells
            validate_result = ma.validate_uv_shells(shape_node)

            if validate_result is not True:
                invalid_nodes = {'node': shape_node, 'uvs_on_boarders': validate_result[1]}
                overlapped.append(invalid_nodes)

        if 'output' not in instance:
            instance.set_data("output", {})

        if overlapped:
            msg = f"Some uv shells has intersection with border '{overlapped}'"
            instance.data['djed_errors']['invalid_uv_nodes'] = overlapped
            self.log.error(msg)
            raise pyblish.api.ValidationError(msg)

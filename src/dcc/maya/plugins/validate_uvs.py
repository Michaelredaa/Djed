import pyblish.api

from dcc.maya.api.cmds import Maya
from maya import cmds


class SelectInvalidNodes(pyblish.api.Action):
    label = "Select node"
    on = "failed"
    icon = "hand-o-up"

    def process(self, context, plugin):

        for result in context.data["results"]:
            if result["error"]:
                instance = result['instance']
                shape_node = instance.data.get("output", {}).get('node')
                cmds.select(shape_node)

                uvs_on_boarders = instance.data.get("output", {}).get('uvs_on_boarders')
                if uvs_on_boarders:
                    cmds.select(uvs_on_boarders)


class FixInvalidNodes(pyblish.api.Action):
    label = "Fix invalid node"
    on = "failed"
    icon = "wrench"


    def process(self, context, plugin):

        ma = Maya()

        for result in context.data["results"]:
            if result["error"]:
                instance = result['instance']
                shape_node = instance.data.get("output", {}).get('node')
                uv_sets = instance.data.get("output", {}).get('uv_sets')

                if not uv_sets:
                    return

                for uv_set in uv_sets[1:]:
                    ma.delete_uv_set(shape_node, uv_set)
                uv_name = uv_sets[0]

                if uv_name != "map1":
                    ma.rename_uv_set(shape_node, "map1")



class ValidateUVSets(pyblish.api.InstancePlugin):
    """
    To validate the uv of mesh
    """

    order = pyblish.api.ValidatorOrder + 1.01
    optional = True

    label = "Validate uv sets"
    hosts = ["maya"]
    families = ["model"]
    active = True
    actions = [SelectInvalidNodes, FixInvalidNodes]

    def process(self, instance):

        self.log.info("Initialize validation of uv sets")

        ma = Maya()
        for shape_node in instance:
            shape_name = shape_node.rsplit('|', 1)[-1]

            # check uv_sets
            uv_sets = ma.uv_sets(shape_node)
            if len(uv_sets) == 0:
                instance.set_data("output", {'node': shape_node, 'uv_sets': uv_sets})
                raise pyblish.api.ValidationError(f"'{shape_name}' have no uvSets.")

            elif len(uv_sets) != 1:
                instance.set_data("output", {'node': shape_node, 'uv_sets': uv_sets})
                raise pyblish.api.ValidationError(f"'{shape_name}' have more than uvSets.")

            elif uv_sets[0] != "map1":
                instance.set_data("output", {'node': shape_node, 'uv_sets': uv_sets})
                raise pyblish.api.ValidationError(f"'{shape_name}' uv set name must have the uv set name 'map1'.")


class ValidateUVBoarders(pyblish.api.InstancePlugin):
    """
    To validate the intersection of uv shells with boarders
    """

    order = pyblish.api.ValidatorOrder + 1.00
    optional = False
    label = "Validate uv shells on boarders"
    hosts = ["maya"]
    families = ["model"]
    active = True
    actions = [SelectInvalidNodes]

    def process(self, instance):

        self.log.info("Initialize validation of uv shells on boarders")

        ma = Maya()
        for shape_node in instance:
            # check uv shells
            validate_result = ma.validate_uv_shells(shape_node)
            print(validate_result)
            if validate_result is not True:
                instance.set_data("output", {'node': shape_node, 'uvs_on_boarders': validate_result[1]})
                raise pyblish.api.ValidationError(validate_result[0])

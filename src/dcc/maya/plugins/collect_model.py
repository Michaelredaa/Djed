import pyblish.api

from dcc.maya.api.cmds import Maya


class CollectMesh(pyblish.api.ContextPlugin):
    """
    Get the current selection
    """

    label = "Get current selection"
    order = pyblish.api.CollectorOrder + 0.00
    hosts = ["maya"]
    families = ["model"]
    external_data = {}


    def process(self, context):
        ma = Maya()
        selection = ma.selection()

        assert len(selection) == 1, "You should select the asset main group only."
        assert '.' not in selection[0], "You should select the asset main group only."

        shapes = ma.list_all_dag_meshes(node=selection[0], shape=True, hidden=False)

        name = selection[0]
        if '|' in selection[0]:
            name = selection[0].split('|')[1]

        instance = context.create_instance(name, family="model", **self.external_data)

        instance.extend(shapes)

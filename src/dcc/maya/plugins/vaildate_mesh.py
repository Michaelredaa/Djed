import pyblish.api

from dcc.maya.api.cmds import Maya


class ValidateNormals(pyblish.api.InstancePlugin):
    """
    To validate and recalculate the mesh normals
    """

    order = pyblish.api.ValidatorOrder + 0.30

    optional = True
    label = "Recalculate normals"
    hosts = ["maya"]
    families = ["model"]
    active = True

    def process(self, instance):
        self.log.info("Initialize recalculating of mesh normals")
        ma = Maya()
        for shape_node in instance:
            ma.recalculate_normals(shape_node)


class ValidateTopology(pyblish.api.InstancePlugin):
    """
    To validate and fix topology like ngons, floating points, unused points, zero length edges, and delete history
    """

    order = pyblish.api.ValidatorOrder + 0.31

    optional = True
    label = "Cleanup mesh"
    hosts = ["maya"]
    families = ["model"]
    active = True

    def process(self, instance):
        self.log.info("Initialize recalculating of mesh normals")
        ma = Maya()
        for shape_node in instance:
            ma.claenup_mesh(shape_node)

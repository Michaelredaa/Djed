from pyblish.api import Action



class SelectInvalidNodes(Action):

    label = "Select node"
    on = "failed"
    icon = "hand-o-up"


    def process(self, context, plugin):

        for result in context.data["results"]:
            if result["error"]:
                instance = result['instance']

class FixInvalidNodes(Action):

    label = "Fix invalid node"
    on = "failed"
    icon = "wrench"


    def process(self, context, plugin):

        for result in context.data["results"]:
            if result["error"]:
                instance = result['instance']
                print(instance.data)
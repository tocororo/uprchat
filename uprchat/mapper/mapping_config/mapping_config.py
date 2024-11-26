import json


class EntityMapping:
    def __init__(self, config: dict):
        # print("_____config entity mapping creation_______")
        # print(config)
        # print(config.get("required"))
        self.config = config
        # self.pid = self.config["pid"]
        self.name = self.config.get("name")
        # # self.description = self.config["description"]
        # self.destination_class = self.config["_class"]
        self.required = self.config.get("mapping").get("required")
        self.properties = self.config.get("mapping").get("properties")
        # self.valuesof = self.config["valuesOf"]

    def validate_required(self, instance):

        """Validates that all required attributes are present in the instance

            Args:
                required_attributes (list): A list of attribute names that are required.
                instance (dict): A dictionary representing the instance to validate.

        Returns:
            bool: True if all required attributes are present, False otherwise.

        """
        # Iterate over the list of required attributes
        for required_attribute in self.required:
            # If any required attribute is missing from the instance JSON, return False
            if required_attribute not in instance:
                return False
        # All required attributes are present in the instance JSON, so return True
        return True


class MappingConfig:

    def __init__(self, config: dict):
        self.config = config
        self.name = self.config.get("name")
        # self.description = self.config["description"]
        # self.created = self.config["created"]
        # self.last_updated = self.config["last_updated"]
        # self._order = self.config["_order"]
        # self.namespaces = self.config["namespaces"]
        # self.default_namespace = self.config["default_namespace"]

        # Possible values n-ary, direct, reification
        self.relation_strategy = (
            self.config["relation_strategy"]
            if ("relation_strategy" in self.config)
            else "n-ary"
        )

        # Possible values Bag, Seq, Alt, List
        self.list_strategy = (
            self.config["list_strategy"] if ("list_strategy" in self.config) else "Bag"
        )

        entities = [EntityMapping(entity) for entity in self.config.get("entities")]
        # entities_map = {entity.pid: entity for entity in entities}
        # ordered_entities = [
        #     entities_map[pid] for pid in self._order if pid in entities_map
        # ]
        self.entities = entities

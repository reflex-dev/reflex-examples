from pydantic import (
    BaseModel as BaseModelPydantic,
    ConfigDict,
)


class BaseModel(BaseModelPydantic):
    """A base model for all models in the application.
    We validate whenever a value is assigned to an attribute.
    We also allow populating attributes by their name/alias.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        populate_by_name=True,
    )

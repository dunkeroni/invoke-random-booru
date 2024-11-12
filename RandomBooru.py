from PIL import ImageDraw, ImageFont

from invokeai.invocation_api import (
    ImageField,
    ImageOutput,
    ColorField,
    BaseInvocation,
    InputField,
    InvocationContext,
    invocation,
    StringOutput,
)

import pyyaml



@invocation("random-booru",
            title="Random Booru Tags",
            tags=["image", "caption"],
            category="image",
            version="2.0.0",
        )
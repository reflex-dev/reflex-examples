"""Tensorflow Hub Object Detection

https://www.tensorflow.org/hub/tutorials/object_detection
"""
import asyncio
import concurrent.futures
import time
from typing import Sequence
from io import BytesIO

import numpy as np
from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFont

import tensorflow as tf
import tensorflow_hub as hub

# Print Tensorflow version
print(tf.__version__)

# Check available GPU devices.
print("The following GPU devices are available: %s" % tf.test.gpu_device_name())


FONT = "Arial.ttf"

MODEL_SLOW = "https://tfhub.dev/google/faster_rcnn/openimages_v4/inception_resnet_v2/1"
MODEL_FAST = "https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1"
DETECTOR = hub.load(MODEL_FAST).signatures["default"]  # type: ignore


def draw_bounding_box_on_image(
    image: Image.Image,
    ymin: int,
    xmin: int,
    ymax: int,
    xmax: int,
    color: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    thickness: int = 4,
    display_str_list: Sequence[str] = (),
):
    """Adds a bounding box to an image."""
    draw = ImageDraw.Draw(image)
    im_width, im_height = image.size
    (left, right, top, bottom) = (
        xmin * im_width,
        xmax * im_width,
        ymin * im_height,
        ymax * im_height,
    )
    draw.line(
        [(left, top), (left, bottom), (right, bottom), (right, top), (left, top)],
        width=thickness,
        fill=color,
    )

    # If the total height of the display strings added to the top of the bounding
    # box exceeds the top of the image, stack the strings below the bounding box
    # instead of above.
    display_str_heights = [font.getbbox(ds)[3] for ds in display_str_list]
    # Each display_str has a top and bottom margin of 0.05x.
    total_display_str_height = (1 + 2 * 0.05) * sum(display_str_heights)

    if top > total_display_str_height:
        text_bottom = top
    else:
        text_bottom = top + total_display_str_height
    # Reverse list and print from bottom to top.
    for display_str in display_str_list[::-1]:
        bbox = font.getbbox(display_str)
        text_width, text_height = bbox[2], bbox[3]
        margin = np.ceil(0.05 * text_height)
        draw.rectangle(
            (
                (left, text_bottom - text_height - 2 * margin),
                (left + text_width, text_bottom),
            ),
            fill=color,
        )
        draw.text(
            (left + margin, text_bottom - text_height - margin),
            display_str,
            fill="black",
            font=font,
        )
        text_bottom -= text_height - 2 * margin


def draw_boxes(
    image: Image.Image,
    boxes: np.ndarray,
    class_names: list[bytes],
    scores: list[float],
    max_boxes: int = 10,
    min_score: float = 0.1,
):
    """Overlay labeled boxes on an image with formatted scores and label names."""
    colors = list(ImageColor.colormap.values())

    try:
        font = ImageFont.truetype(FONT, 10)
    except IOError:
        print("Font not found, using default font.")
        font = ImageFont.load_default()

    for i in range(min(boxes.shape[0], max_boxes)):
        if scores[i] >= min_score:
            ymin, xmin, ymax, xmax = tuple(boxes[i])
            display_str = "{}: {}%".format(
                class_names[i].decode("ascii"), int(100 * scores[i])
            )
            color = colors[hash(class_names[i]) % len(colors)]
            draw_bounding_box_on_image(
                image,
                ymin,
                xmin,
                ymax,
                xmax,
                color,
                font,
                display_str_list=[display_str],
            )
    return image


def load_image(img: Image.Image) -> tf.Tensor:
    """Load a PIL image as a Tensorflow Tensor."""
    buff = BytesIO()
    img.save(buff, format="JPEG")
    return tf.image.decode_jpeg(buff.getvalue(), channels=3)  # type: ignore


def run_detector(img: Image.Image) -> Image.Image:
    """Run object detection on an image.

    Args:
        img: The image to detect objects in.

    Returns:
        The image with bounding boxes drawn around detected objects.
    """
    tf_img = load_image(img)
    converted_img = tf.image.convert_image_dtype(tf_img, tf.float32)[tf.newaxis, ...]  # type: ignore
    print("Starting detection")
    start_time = time.time()
    result = DETECTOR(converted_img)
    end_time = time.time()

    result = {key: value.numpy() for key, value in result.items()}

    print("Found %d objects." % len(result["detection_scores"]))
    print("Inference time: ", end_time - start_time)

    return draw_boxes(
        Image.fromarray(tf_img.numpy()),  # type: ignore
        result["detection_boxes"],
        result["detection_class_entities"],
        result["detection_scores"],
        max_boxes=5,
    )


THREAD_POOL = None


async def run_detector_async(img: Image.Image) -> Image.Image:
    """Run object detection on an image asynchronously.

    Run the model in a thread pool to avoid blocking the event loop. Allow
    multiple clients to process images concurrently up to pool limit.

    Args:
        img: The image to detect objects in.

    Returns:
        The image with bounding boxes drawn around detected objects.
    """
    global THREAD_POOL
    if THREAD_POOL is None:
        THREAD_POOL = concurrent.futures.ThreadPoolExecutor()
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(THREAD_POOL, run_detector, img)

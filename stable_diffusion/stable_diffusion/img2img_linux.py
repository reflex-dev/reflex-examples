from typing import Optional

import torch
from diffusers import EulerDiscreteScheduler, StableDiffusionImg2ImgPipeline
from PIL import Image


def img2img_pipe() -> StableDiffusionImg2ImgPipeline:
    model_id = "stabilityai/stable-diffusion-2-1"
    scheduler = EulerDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")
    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
        model_id, scheduler=scheduler, torch_dtype=torch.float16
    )
    pipe = pipe.to("cuda")
    pipe.enable_xformers_memory_efficient_attention()
    pipe.enable_model_cpu_offload()
    return pipe


def img2img(
    img: Image,
    strength: float = 0.6,
    pipe: Optional[StableDiffusionImg2ImgPipeline] = None,
    guidance_scale=8.5,
    num_inference_steps=150,
    prompt: str = "",
    negative_prompt: str = "",
    seed: Optional[int] = None,
) -> Image:
    """Generate an image conditioned on a source image.

    Args:
        img: an image to use for conditioning
        pipe: a diffusion pipeline to use for anonymisation; Must match the mode. if None,
            a new pipeline will be created.
        strength: the strength of the diffusion used if mode is 'img2img'
        guidance_scale: the guidance scale used for classifier free guidance
        num_inference_steps:  the number of inference steps to use (for img2img the actual
            number of steps ran per image will be num_inference_steps * strength)
        prompt: the prompt to use; this will be prepended to the base prompt
        negative_prompt: the negative prompt to use; this will be prepended to the base prompt_neg
        seed: the seed to use for the random number generator, if None no seed will be set

    Returns:
        new image of dimension (width, height)
    """
    assert num_inference_steps >= 2, "num_inference_steps must be >= 2"

    if pipe is None:
        pipe = img2img_pipe()

    if not isinstance(pipe, StableDiffusionImg2ImgPipeline):
        raise ValueError("pipe must be a StableDiffusionImg2ImgPipeline")

    gen = torch.Generator(device="cuda").manual_seed(seed) if seed is not None else None

    return pipe(
        prompt=prompt,
        image=img,
        strength=strength,
        negative_prompt=negative_prompt,
        guidance_scale=guidance_scale,
        num_inference_steps=num_inference_steps,
        generator=gen,
        num_images_per_prompt=1,
    ).images[0]
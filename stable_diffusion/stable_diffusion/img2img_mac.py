from typing import Optional
from diffusers import DiffusionPipeline, StableDiffusionImg2ImgPipeline

import torch
from PIL import Image



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

    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
        "stabilityai/stable-diffusion-2-1"
    )
    pipe = pipe.to("mps")

    gen = torch.Generator(device="mps").manual_seed(seed) if seed is not None else None

    # Recommended if your computer has < 64 GB of RAM
    pipe.enable_attention_slicing()

    # First-time "warmup" pass if PyTorch version is 1.13 (see explanation above)
    _ = pipe(prompt, image=img, num_inference_steps=1, generator=gen)

    return pipe(
        prompt=prompt,
        image=img,
        strength=strength,
        negative_prompt=negative_prompt,
        guidance_scale=guidance_scale,
        num_inference_steps=num_inference_steps,
        generator=gen,
        num_images_per_prompt=1
    ).images[0]





# def txt2img():
#     pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-2-1")
#     pipe = pipe.to("mps")

#     # Recommended if your computer has < 64 GB of RAM
#     pipe.enable_attention_slicing()

#     prompt = "a photo of an astronaut riding a horse on mars"

#     # First-time "warmup" pass if PyTorch version is 1.13 (see explanation above)
#     _ = pipe(prompt, num_inference_steps=1)

#     # Results match those from the CPU device after the warmup pass.
#     image = pipe(prompt).images[0]
#     print(image)
#     image.show()

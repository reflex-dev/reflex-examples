from typing import Optional
from diffusers import StableDiffusionImg2ImgPipeline
from PIL import Image


def img2img(
    img: Image,
    strength: float = 0.6,
    pipe: Optional[StableDiffusionImg2ImgPipeline] = None,
    guidance_scale=8.5,
    num_inference_steps=50,
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

    model_id = "runwayml/stable-diffusion-v1-5"
    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_id)
    pipe.safety_checker = None
    pipe.requires_safety_checker = False
    # Recommended if your computer has < 64 GB of RAM
    pipe.enable_attention_slicing()

    # First-time "warmup" pass if PyTorch version is 1.13 (see explanation above)
    _ = pipe(prompt, image=img, num_inference_steps=2, num_images_per_prompt=1)

    return pipe(
        prompt=prompt,
        image=img,
        strength=strength,
        negative_prompt=negative_prompt,
        guidance_scale=guidance_scale,
        num_inference_steps=num_inference_steps,
        num_images_per_prompt=1,
    ).images[0]

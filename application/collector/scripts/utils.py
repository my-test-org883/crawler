import subprocess


def image_digest(image):
    """Given an image returns its digest in the form @sha256:..."""
    return subprocess.check_output(["docker", "build", image]).decode()

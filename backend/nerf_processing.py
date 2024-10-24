import subprocess
import os


def process_3d_model(input_path):
    """
    Calls NeRF Studio's demo script to process input video/photo
    and generate a 3D model.
    """
    output_dir = "output/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Assuming the NeRFStudio command (or script) processes input to create a model.
    subprocess.run(
        ["python", "demo.ipynb", input_path, output_dir], check=True
    )

    # For now, return the path of the generated 3D model
    return os.path.join(output_dir, "model.obj")

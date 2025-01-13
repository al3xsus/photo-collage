from random import shuffle

from PIL import Image, ImageDraw, ImageOps
import os
import math
import random
from itertools import cycle

GOLDEN_RATIO = (1 + math.sqrt(5)) / 2  # Define the golden ratio

def golden_ratio_collage(canvas_size, padding, output_path, images, randomization=True, bg_color=None, bg_image=None):

    """
    Create a golden ratio-based collage from the provided images.

    Parameters:
        canvas_size (tuple): Dimensions of the canvas (width, height).
        padding (int): Space between images and canvas edges.
        output_path (str): File path to save the resulting collage.
        images (list): List of image file paths to include in the collage.
        randomization (bool): Randomize image placement and order (default: True).
        bg_color (tuple): Background color of the canvas (e.g., (255, 255, 255) for white).
        bg_image (str): File path to an image to use as the background (overrides `bg_color`).

    Notes:
        - Images are dynamically resized based on the golden ratio and remaining working area.
        - Either `bg_color` or `bg_image` must be provided. If both are given, `bg_image` takes precedence.
    """
    canvas_width, canvas_height = canvas_size
    # Initialize the working area for placing images
    working_area = {
        "x": 0,
        "y": 0,
        "width": canvas_width,
        "height": canvas_height
    }

    # Initialize the canvas (background image or color)
    collage = None
    if bg_image:
        collage = Image.open(bg_image)
    if bg_color:
        collage = Image.new("RGB", canvas_size, bg_color)

    # Determine the initial layout orders
    horizontal_order = "right-to-left"
    vertical_order = "bottom-to-top"

    # Determine the initial layout orders
    if randomization:
        horizontal_order = random.choice(["right-to-left", "left-to-right"])
        vertical_order = random.choice(["bottom-to-top", "top-to-bottom"])
        random.shuffle(images)

    x, y = 0, 0  # Starting position
    for idx, img_path in enumerate(images):
        img = Image.open(img_path)
        # Decide whether to split horizontally or vertically based on working area dimensions
        if working_area["width"] > working_area["height"]:  # Horizontal split
            img = ImageOps.fit(img, (int(working_area["width"] / GOLDEN_RATIO), working_area["height"]), method=Image.Resampling.LANCZOS)
            # Adjust position and update working area
            if horizontal_order == "right-to-left":
                horizontal_order = "left-to-right"
                working_area["x"] += img.width + padding
            else:
                x = x + working_area["width"] - img.width
                horizontal_order = "right-to-left"
            working_area["width"] -= img.width + padding
        else:  # Vertical split
            img = ImageOps.fit(img, (working_area["width"], int(working_area["height"] / GOLDEN_RATIO)), method=Image.Resampling.LANCZOS)
            # Adjust position and update working area
            if vertical_order == "bottom-to-top":
                working_area["y"] += img.height + padding
                vertical_order = "top-to-bottom"
            else:
                y = y + working_area["height"] - img.height
                vertical_order = "bottom-to-top"
            working_area["height"] -= img.height + padding

        # Paste the image onto the canvas
        collage.paste(img, (x, y))
        x, y = working_area["x"], working_area["y"]  # Update position for the next image

        # Stop if the working area becomes too small
        if working_area["width"] <= 0 or working_area["height"] <= 0:
            print("Working area exhausted. Stopping collage creation.")
            break

    # Save the resulting collage
    collage.save(output_path)
    print(f"Golden ratio collage saved at {output_path}")

def keep_aspect_grid_collage(canvas_size, padding, output_path, images, bg_color="white", scaling_factor=1.0):
    """
    Create a grid-based collage where images are resized to keep their original aspect ratio.
    :param canvas_size:
    :param padding:
    :param output_path:
    :param images:
    :param bg_color:
    :param scaling_factor:
    :return:
    """
    canvas_width, canvas_height = canvas_size

    # Create the canvas
    collage = Image.new("RGB", canvas_size, bg_color)
    x = y = working_row = working_column = 0
    order = None
    working_row_height = working_column_width = 0

    aspect_mismatch_skipped = 0

    images_to_skip = set()
    image_iterator = cycle(images)

    shuffle(images)

    TOLERANCE = 50   # Tolerance for aspect ratio comparison

    while len(images_to_skip) < len(images):
        img_path = next(image_iterator)
        if img_path in images_to_skip:
            continue
        img = Image.open(img_path)
        scaled_width = int(img.width * scaling_factor)
        scaled_height = int(img.height * scaling_factor)
        '''
        if it is first element, place'em in the 0.0 position
        its width and height gonna be example for possible column/row layout
        '''
        if x == y == 0:
            img = ImageOps.fit(img, (scaled_width, scaled_height), method=Image.Resampling.LANCZOS)
            working_column_width = img.width
            working_row_height = img.height
            order = "column" if working_column_width < working_row_height else "row"
        if order == "row":
            if scaled_width + padding + x > canvas_width:
                if abs(working_row_height - scaled_height) > TOLERANCE:
                    aspect_mismatch_skipped += 1
                    print(f"Aspect ratio mismatch for {img_path}. Skipping.")
                    continue
                img = ImageOps.fit(img, (working_column_width, scaled_height), method=Image.Resampling.LANCZOS)
        else:
            img = ImageOps.fit(img, (scaled_width, working_row_height), method=Image.Resampling.LANCZOS)
        print(f"Processing {img_path}")
        images_to_skip.add(img_path)
        collage.paste(img, (x, y))

    # Save the resulting collage
    collage.save(output_path)
    print(f"Grid aspect collage [keep aspect ratio] saved at {output_path}")

def all_squares(canvas_size, bg_color, padding, output_path, images, centered=False):
    """
    Create a grid-based collage where all images are resized to fit into square cells.

    Parameters:
        canvas_size (tuple): Dimensions of the canvas (width, height).
        bg_color (tuple): Background color of the canvas (e.g., (255, 255, 255) for white).
        padding (int): Space between images and edges of the canvas.
        output_path (str): File path to save the resulting collage.
        images (list): List of file paths to the images.
        centered (bool): Whether to center the grid if the canvas is not square (default: False).
    """
    canvas_width, canvas_height = canvas_size

    images_num = len(images)

    # Create the canvas
    collage = Image.new("RGB", canvas_size, bg_color)

    if canvas_width == canvas_height:
        # Square canvas: Determine grid dimensions for a square layout
        grid_size = math.ceil(math.sqrt(images_num))
        cell_size = (canvas_width - (grid_size + 1) * padding) // grid_size

        for idx, img_path in enumerate(images):
            img = Image.open(img_path)
            img = ImageOps.fit(img, (cell_size, cell_size), method=Image.Resampling.LANCZOS)

            # Calculate position in the grid
            x = (idx % grid_size) * (cell_size + padding) + padding
            y = (idx // grid_size) * (cell_size + padding) + padding

            collage.paste(img, (x, y))

    else:
        # Non-square canvas: Determine grid dimensions for the closest layout
        cols = math.ceil(math.sqrt(images_num))
        rows = math.ceil(images_num / cols)
        offset_x, offset_y = 0, 0

        # Adjust grid dimensions and offsets based on canvas proportions
        if canvas_width > canvas_height:
            if cols < rows:
                cols, rows = rows, cols
            if centered:
                offset_x = (canvas_width - (rows * (canvas_height // rows))) // 2
        elif canvas_width < canvas_height:
            if cols > rows:
                cols, rows = rows, cols
            if centered:
                offset_y = (canvas_height - (cols * (canvas_width // cols))) // 2

        # Calculate cell dimensions
        cell_width = (canvas_width - (cols + 1) * padding) // cols
        cell_height = (canvas_height - (rows + 1) * padding) // rows

        # Use the smaller dimension if centering is enabled
        if centered:
            cell_width = cell_height = min(cell_width, cell_height)

        for idx, img_path in enumerate(images):
            img = Image.open(img_path)
            img = ImageOps.fit(img, (cell_width, cell_height), method=Image.Resampling.LANCZOS)

            # Calculate position in the grid
            x = (idx % cols) * (cell_width + padding) + padding + offset_x
            y = (idx // cols) * (cell_height + padding) + padding + offset_y

            collage.paste(img, (x, y))

    # Save the resulting collage
    collage.save(output_path)
    print(f"Grid packing collage [square images] saved at {output_path}")

def all_rectangles(canvas_size, bg_color, padding, output_path, images, centered=False, orientation="horizontal"):
    """
    Create a grid-based collage where all images are resized to fit rectangular blocks, arranged
    either horizontally or vertically.

    Parameters:
        canvas_size (tuple): Dimensions of the canvas (width, height).
        bg_color (tuple): Background color of the canvas (e.g., (255, 255, 255) for white).
        padding (int): Space between images and edges of the canvas.
        output_path (str): File path to save the resulting collage.
        images (list): List of file paths to the images.
        centered (bool): Whether to center the grid if the blocks don't fill the canvas (default: False).
        orientation (str): Orientation of the grid: "horizontal" or "vertical" (default: "horizontal").
    """
    canvas_width, canvas_height = canvas_size

    images_num = len(images)

    # Create the canvas
    collage = Image.new("RGB", canvas_size, bg_color)

    # Determine block size based on orientation
    if orientation == "horizontal":
        block_height = (canvas_height - (images_num + 1) * padding) // images_num
        block_width = canvas_width
    elif orientation == "vertical":
        block_width = (canvas_width - (images_num + 1) * padding) // images_num
        block_height = canvas_height
    else:
        raise ValueError("Orientation must be 'horizontal' or 'vertical'.")

    # Centering offsets
    offset_x, offset_y = 0, 0
    if centered:
        if orientation == "horizontal" and images_num * (block_height + padding) < canvas_height:
            offset_y = (canvas_height - (images_num * (block_height + padding))) // 2
        if orientation == "vertical" and images_num * (block_width + padding) < canvas_width:
            offset_x = (canvas_width - (images_num * (block_width + padding))) // 2

    # Resize and paste images
    for idx, img_path in enumerate(images):
        img = Image.open(img_path)
        img = ImageOps.fit(img, (block_width, block_height), method=Image.Resampling.LANCZOS)

        # Calculate position
        x, y = 0, 0
        if orientation == "horizontal":
            y = idx * (block_height + padding) + padding + offset_y
        elif orientation == "vertical":
            x = idx * (block_width + padding) + padding + offset_x

        collage.paste(img, (x, y))

    # Save the collage
    collage.save(output_path)
    print(f"Grid packing collage [all_rectangles] saved at {output_path}")

def auto_layout(images, output_path, canvas_size=(800, 800), padding=10, bg_color="white"):
    """
    Create a grid layout.

    Args:
        images (list): List of image file paths.
        output_path (str): Path to save the output collage.
        canvas_size (tuple): Size of the canvas (width, height).
        padding (int): Padding between images in pixels.
        bg_color (str): Background color.
    """
    canvas_width, canvas_height = canvas_size
    images_num = len(images)
    image_objects_list = []
    squares = 0
    horizontal_rectangles = 0
    vertical_rectangles = 0
    total_area = 0
    aspect_ratio_sum_width = aspect_ratio_sum_height = 0
    for idx, img_path in enumerate(images):
        img = Image.open(img_path)
        image_objects_list.append({
            "image": img
        })
        total_area += img.width * img.height
        if img.height == img.width:
            squares += 1
            aspect_ratio_sum_width += 1
            aspect_ratio_sum_height += 1

        elif img.height > img.width:
            vertical_rectangles += 1
            aspect_ratio_sum_height += img.height / img.width
            aspect_ratio_sum_width += 1

        else:
            horizontal_rectangles += 1
            aspect_ratio_sum_width += img.width / img.height
            aspect_ratio_sum_height += 1

    if squares == images_num:
        all_squares(canvas_size, bg_color, padding, output_path, images, centered=True)

    elif horizontal_rectangles == images_num:
        all_rectangles(canvas_size, bg_color, padding, output_path, images, centered=True, orientation="horizontal")

    elif vertical_rectangles == images_num:
        all_rectangles(canvas_size, bg_color, padding, output_path, images, centered=True, orientation="vertical")
    else:
        canvas_area = canvas_width * canvas_height
        scaling_factor = math.sqrt(canvas_area / total_area)
        rows = 0
        cols = 0
        aspect_sum_diff = abs(aspect_ratio_sum_width - aspect_ratio_sum_height)
        # golden_ratio_collage(canvas_size=canvas_size, bg_color=bg_color, padding=padding, output_path=output_path, images=images)
        keep_aspect_grid_collage(canvas_size=canvas_size, bg_color=bg_color, padding=padding, output_path=output_path, images=images, scaling_factor=scaling_factor)

if __name__ == "__main__":
    images = []
    square_image_paths = ["./images/square-1.jpg", "./images/square-2.jpg", "./images/square-3.jpg", "./images/square-4.jpg", "./images/square-5.jpg"]
    horizontal_image_paths = ["./images/horizontal-rectangle-1.jpg", "./images/horizontal-rectangle-2.png", "./images/horizontal-rectangle-3.png", "./images/horizontal-rectangle-4.jpg", "./images/horizontal-rectangle-5.jpg"]
    vertical_image_paths = ["./images/vertical-rectangle-1.jpg", "./images/vertical-rectangle-2.jpg", "./images/vertical-rectangle-3.jpg", "./images/vertical-rectangle-4.jpg", "./images/vertical-rectangle-5.jpg"]
    for img_path in square_image_paths + horizontal_image_paths + vertical_image_paths:
        img = Image.open(img_path)
        print(f"Image: {img_path} - Size: {img.size}")

    golden_ratio_collage(canvas_size=(800, 800), padding=10, output_path="golden_ratio_collage.jpg", images=square_image_paths + horizontal_image_paths + vertical_image_paths, randomization=True, bg_color=(255, 255, 255))

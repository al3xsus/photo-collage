import io
import math
import random
import uuid

import numpy as np
import streamlit as st
from PIL import Image, ImageOps

GOLDEN_RATIO = (1 + math.sqrt(5)) / 2  # Define the golden ratio

MIN_IMAGES = 4
MAX_IMAGES = 20

MIN_PADDING = 0
MAX_PADDING = 50

# Provided data for social media sizes
SOCIAL_MEDIA_IMAGE_SIZES = {
    "Instagram Feed Square": (1080, 1080),
    "Instagram Feed Portrait": (1080, 1350),
    "Instagram Feed Landscape": (1080, 608),
    "Instagram Stories/Reels": (1080, 1920),
    "Facebook Feed Post": (1200, 630),
    "Facebook Stories": (1080, 1920),
    "Facebook Event Cover": (1920, 1005),
    "YouTube Thumbnail": (1280, 720),
    "YouTube Channel Art": (2560, 1440),
    "X Single Image": (1200, 675),
    "X Multi-Image": (1200, 600),
    "LinkedIn Feed Post": (1200, 627),
    "LinkedIn Company Cover": (1128, 191),
}

# Icons for each platform
SOCIAL_MEDIA_ICONS = {
    "Instagram": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Instagram_icon.png/240px-Instagram_icon.png",
    "Facebook": "https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg",
    "YouTube": "https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg",
    "X": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/X_icon_black.svg/240px-X_icon_black.svg.png",
    "LinkedIn": "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png",
}


def golden_ratio_collage(images, collage, padding, randomization):
    """
    Create a golden ratio-based collage from the provided images.

    Parameters:
        images (list): List of image file paths to include in the collage.
        collage (PIL.Image): Blank canvas to place the images.
        padding (int): Space between images and canvas edges.
        randomization (bool): Randomize image placement and order.

    Notes:
        - Images are dynamically resized based on the golden ratio and remaining working area.
    """
    # Initialize the working area for placing images
    working_area = {
        "x": 0,
        "y": 0,
        "width": collage.width,
        "height": collage.height,
    }

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
            img = ImageOps.fit(img, (int(working_area["width"] / GOLDEN_RATIO), working_area["height"]),
                               method=Image.Resampling.LANCZOS)
            # Adjust position and update working area
            if horizontal_order == "right-to-left":
                horizontal_order = "left-to-right"
                working_area["x"] += img.width + padding
            else:
                x = x + working_area["width"] - img.width
                horizontal_order = "right-to-left"
            working_area["width"] -= img.width + padding
        else:  # Vertical split
            img = ImageOps.fit(img, (working_area["width"], int(working_area["height"] / GOLDEN_RATIO)),
                               method=Image.Resampling.LANCZOS)
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

    return collage


def grid_collage(images, collage, padding, randomization, centered):
    """
    Create a grid-based collage.

    Parameters:
        images (list): List of image file paths to include in the collage.
        collage (PIL.Image): Blank canvas to place the images.
        padding (int): Space between images and canvas edges.
        randomization (bool): Randomize image placement and order.
        centered (bool): Whether to center the grid if the canvas is not square.
    """
    images_num = len(images)
    if randomization:
        random.shuffle(images)
    canvas_width, canvas_height = collage.size
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

    return collage


def lane_collage(images, collage, padding, randomization, centered, orientation="horizontal"):
    """
    Create a lane-based collage.

    Parameters:
        images (list): List of image file paths to include in the collage.
        collage (PIL.Image): Blank canvas to place the images.
        padding (int): Space between images and canvas edges.
        randomization (bool): Randomize image placement and order.
        centered (bool): Whether to center the grid if the canvas is not square.
        orientation (str): Orientation of the grid: "horizontal" or "vertical".
    """
    canvas_width, canvas_height = collage.size

    images_num = len(images)

    if randomization:
        random.shuffle(images)

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

    return collage


def auto_layout(images, collage, padding, randomization, centered):
    """
    Create an auto layout.

    Args:
        images (list): List of image file paths to include in the collage.
        collage (PIL.Image): Blank canvas to place the images.
        padding (int): Space between images and canvas edges.
        randomization (bool): Randomize image placement and order.
        centered (bool): Whether to center the grid if the canvas is not square (default: False).
    """
    canvas_width, canvas_height = collage.size
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
        return grid_collage(images, collage, padding, randomization, centered)

    elif horizontal_rectangles == images_num:
        return lane_collage(images, collage, padding, randomization, centered, orientation="horizontal")

    elif vertical_rectangles == images_num:
        return lane_collage(images, collage, padding, randomization, centered, orientation="vertical")

    else:
        canvas_area = canvas_width * canvas_height
        scaling_factor = math.sqrt(canvas_area / total_area)
        rows = 0
        cols = 0
        aspect_sum_diff = abs(aspect_ratio_sum_width - aspect_ratio_sum_height)
        return golden_ratio_collage(images, collage, padding, randomization)


if __name__ == "__main__":
    st.set_page_config(
        page_title='Photo Collage Maker',
        page_icon="🧊",
        layout="centered",
    )
    st.title("Photo Collage Maker")
    st.markdown(
        f"""
             <style>
                 .stApp {{
                     background-color: #fefae0;
                     background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='152' height='152' viewBox='0 0 152 152'%3E%3Cg fill-rule='evenodd'%3E%3Cg id='temple' fill='%23283618' fill-opacity='0.1'%3E%3Cpath d='M152 150v2H0v-2h28v-8H8v-20H0v-2h8V80h42v20h20v42H30v8h90v-8H80v-42h20V80h42v40h8V30h-8v40h-42V50H80V8h40V0h2v8h20v20h8V0h2v150zm-2 0v-28h-8v20h-20v8h28zM82 30v18h18V30H82zm20 18h20v20h18V30h-20V10H82v18h20v20zm0 2v18h18V50h-18zm20-22h18V10h-18v18zm-54 92v-18H50v18h18zm-20-18H28V82H10v38h20v20h38v-18H48v-20zm0-2V82H30v18h18zm-20 22H10v18h18v-18zm54 0v18h38v-20h20V82h-18v20h-20v20H82zm18-20H82v18h18v-18zm2-2h18V82h-18v18zm20 40v-18h18v18h-18zM30 0h-2v8H8v20H0v2h8v40h42V50h20V8H30V0zm20 48h18V30H50v18zm18-20H48v20H28v20H10V30h20V10h38v18zM30 50h18v18H30V50zm-2-40H10v18h18V10z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");                 
                 }}
             </style>
        """,
        unsafe_allow_html=True
    )

    # Define default session state values
    default_values = {
        "images": None,
        "platform": None,
        "background": None,
        "layout": None,
        "randomization": False,
        "centering": False,
        "padding": MIN_PADDING,
        "collage": None,
    }

    # Initialize session state
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


    def set_active_platform(active_platform):
        st.session_state.platform = active_platform


    def set_active_images(active_images):
        st.session_state.images = active_images


    def set_active_background(category, active_background):
        if category is None and active_background is None:
            st.session_state.background = None
        else:
            st.session_state.background = {
                "category": category,
                "value": active_background
            }


    def set_active_layout(active_layout):
        st.session_state.layout = active_layout


    def handle_create_collage_button_click():
        # Initialize the canvas (background image or color)
        new_collage = None
        if st.session_state.background["category"] == "image":
            new_collage = Image.open(st.session_state.background["value"])
        else:
            new_collage = Image.new("RGB", SOCIAL_MEDIA_IMAGE_SIZES[st.session_state.platform],
                                    st.session_state.background["value"])

        match st.session_state.layout:
            case "golden_ratio":
                new_collage = golden_ratio_collage(st.session_state.images, new_collage, st.session_state.padding,
                                                   st.session_state.randomization)
            case "grid":
                new_collage = grid_collage(st.session_state.images, new_collage, st.session_state.padding,
                                           st.session_state.randomization, st.session_state.centering)
            case "strip":
                new_collage = lane_collage(st.session_state.images, new_collage, st.session_state.padding,
                                           st.session_state.randomization, st.session_state.centering,
                                           orientation="vertical")
            case "stack":
                new_collage = lane_collage(st.session_state.images, new_collage, st.session_state.padding,
                                           st.session_state.randomization, st.session_state.centering,
                                           orientation="horizontal")
            case "auto":
                new_collage = auto_layout(st.session_state.images, new_collage, st.session_state.padding,
                                          st.session_state.randomization, st.session_state.centering)

        st.session_state.collage = new_collage


    st.header("Step 1. Upload images")

    uploaded_files = st.file_uploader("Choose images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if uploaded_files:
        images = [Image.open(file) for file in uploaded_files]
        st.write(f"Selected {len(images)} images")

        if len(images) < MIN_IMAGES:
            st.warning(f"Please select at least {MIN_IMAGES} images for a collage")
        elif len(images) > MAX_IMAGES:
            st.warning(f"Please select at most {MAX_IMAGES} images for a collage")
        else:
            st.success("Images uploaded successfully!")
            show_images_toggle = st.toggle("Show images")
            if show_images_toggle:
                st.image(images, use_container_width=True)
            set_active_images(uploaded_files)

    if st.session_state.images is not None:
        st.header("Step 2. Customize size")
        st.subheader("Select appropriate media size")

        if st.session_state.platform is None:
            # Render buttons dynamically
            for platform, size in SOCIAL_MEDIA_IMAGE_SIZES.items():

                # Extract the base name (e.g., "Instagram" from "Instagram Feed Square")
                platform_base = platform.split()[0]
                icon_url = SOCIAL_MEDIA_ICONS.get(platform_base, None)

                # Display the button with an icon and label
                col1, col2 = st.columns([0.2, 0.8])  # For icon and label alignment
                with col1:
                    if icon_url:
                        st.image(icon_url, width=30)
                    else:
                        st.write("")  # Placeholder for missing icons
                with col2:
                    st.button(label=f"{platform}: {size[0]}x{size[1]}", key=platform, help=platform,
                              use_container_width=True, args=(platform,), on_click=set_active_platform)

        else:
            # Display active platform info
            platform_base = st.session_state.platform.split()[0]
            icon_url = SOCIAL_MEDIA_ICONS.get(platform_base, None)

            # Display the button with an icon and label
            col1, col2 = st.columns([0.2, 0.8])  # For icon and label alignment
            with col1:
                if icon_url:
                    st.image(icon_url, width=30)
                else:
                    st.write("")  # Placeholder for missing icons
            with col2:
                platform = st.session_state.platform
                st.write(
                    f"Selected: {platform} {SOCIAL_MEDIA_IMAGE_SIZES[platform][0]}x{SOCIAL_MEDIA_IMAGE_SIZES[platform][1]}")

            st.button('Re-select size', args=(None,), on_click=set_active_platform, help="Re-select size",
                      use_container_width=True, icon=":material/photo_size_select_actual:")

            st.header("Step 3. Customize background")
            st.subheader("Choose color or image")

            if st.session_state.background is None:
                with st.container(border=True):
                    column1, column2 = st.columns([1, 1])
                    with column1:
                        color_image_radio = st.radio(
                            "Background color or image",
                            ["color", "image"],
                            captions=[
                                "Solid color",
                                "Image",
                            ],
                        )
                    with column2:
                        if color_image_radio == "color":
                            bg_color = st.color_picker("Pick A Color", None)
                            if bg_color:
                                st.write(f"Selected color: {bg_color}")
                                st.button("Set background color", on_click=set_active_background,
                                          args=("color", bg_color),
                                          use_container_width=True, icon=":material/water_drop:")
                        else:
                            bg_file = st.file_uploader("Choose image for background", type=["jpg", "jpeg", "png"],
                                                       accept_multiple_files=False)
                            if bg_file:
                                bg_img = Image.open(bg_file)
                                st.image(bg_img, caption="Selected image", use_container_width=True)
                                st.button("Set background image", on_click=set_active_background,
                                          args=("image", bg_file),
                                          use_container_width=True, icon=":material/image:")
            else:
                bg_category = st.session_state.background["category"]
                bg_value = st.session_state.background["value"]

                if bg_category == "color":
                    st.write(f"Selected color: {bg_value}")
                else:
                    st.image(bg_value, caption="Selected image", use_container_width=True)

                st.button("Re-select background", use_container_width=True, on_click=set_active_background,
                          args=(None, None), icon=":material/format_paint:", help="Re-select background")

                st.header("Step 4. Customize arrangement of images")
                st.subheader("Choose layout")

                if st.session_state.layout is None:
                    layout_options = ["grid", "strip", "stack", "golden_ratio", "auto"]
                    layout_icons = ["grid_on", "table_rows", "view_column", "grid_goldenratio", "auto_awesome"]

                    with st.container(border=True):
                        columns = st.columns(len(layout_options))  # Create dynamic columns

                        for col, layout, icon in zip(columns, layout_options, layout_icons):
                            with col:
                                st.button(layout.replace("_", " "), use_container_width=True,
                                          on_click=set_active_layout, args=(layout,), icon=f":material/{icon}:")

                else:
                    st.write(f"Selected layout: {st.session_state.layout}")
                    st.button("Re-select layout", use_container_width=True, on_click=set_active_layout,
                              args=(None,), icon=":material/grid_off:", help="Re-select layout")

                    st.header("Step 5. Final settings")
                    st.subheader("Set up padding, centering, and randomization")
                    with st.container(border=True):
                        column1, column2 = st.columns([1, 1])
                        with column1:
                            st.number_input("Padding", min_value=MIN_PADDING, max_value=MAX_PADDING, key='padding')
                        with column2:
                            st.checkbox("Randomize image order", key='randomization')
                            st.checkbox("Center images (if possible)", key="centering")
                        st.button("Create collage", use_container_width=True,
                                  on_click=handle_create_collage_button_click, icon=":material/auto_awesome_mosaic:")

                    if st.session_state.collage is not None:
                        st.header("Step 6. Collage preview")
                        st.image(np.array(st.session_state.collage), caption="Collage Preview",
                                 use_container_width=True)
                        # Convert the image to binary format
                        image_bytes = io.BytesIO()
                        st.session_state.collage.save(image_bytes, format="PNG")  # Save as PNG or change to "JPEG"
                        image_bytes.seek(0)  # Move cursor to the beginning

                        # Create a download button
                        st.download_button(
                            label="Download Image",
                            data=image_bytes,
                            file_name=f"{str(uuid.uuid4())}-{st.session_state.layout}-collage.png",
                            mime="image/png",
                            use_container_width=True,
                            icon=":material/download:"
                        )

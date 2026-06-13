
"""Profile page component."""

import reflex as rx
from ..state.profile import ProfileState


def profile_header() -> rx.Component:
    """Profile header with cover photo and profile picture."""
    return rx.box(
        # Cover photo area
        rx.box(
            height="200px",
            width="100%",
            background="linear-gradient(135deg, #1DA1F2 0%, #14171A 100%)",
            border_radius="0",
        ),
        # Profile picture
        rx.box(
            rx.cond(
                ProfileState.profile_photo != "",
                rx.image(
                    src=ProfileState.profile_photo,
                    width="150px",
                    height="150px",
                    border_radius="50%",
                    border="4px solid white",
                    object_fit="cover",
                ),
                rx.box(
                    rx.icon("user", size=50, color="#657786"),
                    width="150px",
                    height="150px",
                    border_radius="50%",
                    border="4px solid white",
                    background="#E1E8ED",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
            ),
            position="absolute",
            top="140px",
            left="20px",
        ),
        position="relative",
        margin_bottom="60px",
    )


def edit_profile_form() -> rx.Component:
    """Form to edit profile information."""
    return rx.box(
        rx.vstack(
            rx.heading("Edit Profile", size="6", color="#14171A", margin_bottom="20px"),
            
            # Profile photo upload
            rx.vstack(
                rx.text("Profile Photo", font_weight="bold", color="#14171A"),
                rx.upload(
                    rx.vstack(
                        rx.button(
                            "Select Profile Photo",
                            color="white",
                            bg="#1DA1F2",
                            _hover={"bg": "#1A91DA"},
                            border_radius="20px",
                        ),
                        rx.text(
                            "Drag and drop or click to upload",
                            font_size="14px",
                            color="#657786",
                        ),
                    ),
                    id="profile_photo_upload",
                    border="2px dashed #E1E8ED",
                    padding="20px",
                    border_radius="10px",
                ),
                rx.button(
                    "Upload Photo",
                    on_click=ProfileState.handle_upload(
                        rx.upload_files(upload_id="profile_photo_upload")
                    ),
                    color="white",
                    bg="#1DA1F2",
                    _hover={"bg": "#1A91DA"},
                    border_radius="20px",
                ),
                width="100%",
                spacing="2",
            ),
            
            # Display name
            rx.vstack(
                rx.text("Display Name", font_weight="bold", color="#14171A"),
                rx.input(
                    placeholder="Your display name",
                    value=ProfileState.display_name,
                    on_change=ProfileState.set_display_name,
                    width="100%",
                    border_color="#E1E8ED",
                    _focus={"border_color": "#1DA1F2"},
                ),
                width="100%",
                spacing="2",
            ),
            
            # Bio
            rx.vstack(
                rx.text("Bio", font_weight="bold", color="#14171A"),
                rx.text_area(
                    placeholder="Tell us about yourself",
                    value=ProfileState.bio,
                    on_change=ProfileState.set_bio,
                    width="100%",
                    height="100px",
                    border_color="#E1E8ED",
                    _focus={"border_color": "#1DA1F2"},
                ),
                width="100%",
                spacing="2",
            ),
            
            # Location
            rx.vstack(
                rx.text("Location", font_weight="bold", color="#14171A"),
                rx.input(
                    placeholder="Where are you located?",
                    value=ProfileState.location,
                    on_change=ProfileState.set_location,
                    width="100%",
                    border_color="#E1E8ED",
                    _focus={"border_color": "#1DA1F2"},
                ),
                width="100%",
                spacing="2",
            ),
            
            # Website
            rx.vstack(
                rx.text("Website", font_weight="bold", color="#14171A"),
                rx.input(
                    placeholder="https://yourwebsite.com",
                    value=ProfileState.website,
                    on_change=ProfileState.set_website,
                    width="100%",
                    border_color="#E1E8ED",
                    _focus={"border_color": "#1DA1F2"},
                ),
                width="100%",
                spacing="2",
            ),
            
            # Action buttons
            rx.hstack(
                rx.button(
                    "Save Changes",
                    on_click=ProfileState.update_profile,
                    color="white",
                    bg="#1DA1F2",
                    _hover={"bg": "#1A91DA"},
                    border_radius="20px",
                    padding="10px 24px",
                ),
                rx.button(
                    "Cancel",
                    on_click=ProfileState.cancel_edit,
                    color="#14171A",
                    bg="white",
                    border="1px solid #E1E8ED",
                    _hover={"bg": "#F7F9FA"},
                    border_radius="20px",
                    padding="10px 24px",
                ),
                spacing="3",
                justify="flex-end",
                width="100%",
            ),
            
            spacing="4",
            width="100%",
        ),
        padding="20px",
        background="white",
        border_radius="16px",
        border="1px solid #E1E8ED",
        box_shadow="0 2px 8px rgba(0, 0, 0, 0.1)",
    )


def profile_info() -> rx.Component:
    """Display profile information."""
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.cond(
                    ProfileState.display_name != "",
                    rx.heading(ProfileState.display_name, size="7", color="#14171A"),
                    rx.heading(ProfileState.username, size="7", color="#14171A"),
                ),
                rx.text(f"@{ProfileState.username}", color="#657786", font_size="16px"),
                align_items="flex-start",
                spacing="1",
            ),
            rx.spacer(),
            rx.button(
                "Edit Profile",
                on_click=ProfileState.toggle_edit_mode,
                color="white",
                bg="#1DA1F2",
                _hover={"bg": "#1A91DA"},
                border_radius="20px",
                padding="8px 20px",
                font_weight="bold",
            ),
            width="100%",
            align_items="center",
        ),
        
        rx.cond(
            ProfileState.bio != "",
            rx.text(ProfileState.bio, color="#14171A", font_size="15px", margin_top="12px"),
        ),
        
        rx.vstack(
            rx.cond(
                ProfileState.location != "",
                rx.hstack(
                    rx.icon("map-pin", size=18, color="#657786"),
                    rx.text(ProfileState.location, color="#657786", font_size="15px"),
                    spacing="2",
                ),
            ),
            rx.cond(
                ProfileState.website != "",
                rx.hstack(
                    rx.icon("link", size=18, color="#657786"),
                    rx.link(
                        ProfileState.website,
                        href=ProfileState.website,
                        color="#1DA1F2",
                        font_size="15px",
                        _hover={"text_decoration": "underline"},
                    ),
                    spacing="2",
                ),
            ),
            spacing="2",
            margin_top="12px",
            align_items="flex-start",
        ),
        
        padding="20px",
        width="100%",
        align_items="flex-start",
        spacing="2",
    )


def profile_page() -> rx.Component:
    """Main profile page."""
    return rx.box(
        rx.vstack(
            profile_header(),
            
            rx.box(
                rx.cond(
                    ProfileState.is_editing,
                    edit_profile_form(),
                    profile_info(),
                ),
                width="100%",
                max_width="600px",
                margin="0 auto",
            ),
            
            width="100%",
            spacing="0",
        ),
        padding="0",
        width="100%",
        background="#F7F9FA",
        min_height="100vh",
        on_mount=ProfileState.load_profile_data,
    )

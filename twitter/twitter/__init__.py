"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

# ...existing imports...
from .components.profile import profile_page

# ...existing code...

# Create app instance and add pages
app = rx.App()

# ...existing page routes...

# Add profile page route
app.add_page(profile_page, route="/profile", title="Profile")

# ...existing code...
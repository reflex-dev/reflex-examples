"""Profile editing state."""

import reflex as rx
from sqlmodel import select

from ..db_model import User
from .base import State


class ProfileState(State):
    """State for profile editing."""

    # Form fields
    display_name: str = ""
    bio: str = ""
    location: str = ""
    website: str = ""
    profile_photo: str = ""
    
    # UI state
    is_editing: bool = False
    upload_progress: int = 0

    def load_profile_data(self):
        """Load the current user's profile data."""
        if self.logged_in:
            with rx.session() as session:
                user = session.exec(
                    select(User).where(User.username == self.username)
                ).first()
                if user:
                    self.display_name = user.display_name
                    self.bio = user.bio
                    self.location = user.location
                    self.website = user.website
                    self.profile_photo = user.profile_photo

    def toggle_edit_mode(self):
        """Toggle edit mode for profile."""
        if not self.is_editing:
            self.load_profile_data()
        self.is_editing = not self.is_editing

    def update_profile(self):
        """Update the user's profile information."""
        if not self.logged_in:
            return

        with rx.session() as session:
            user = session.exec(
                select(User).where(User.username == self.username)
            ).first()
            if user:
                user.display_name = self.display_name
                user.bio = self.bio
                user.location = self.location
                user.website = self.website
                if self.profile_photo:
                    user.profile_photo = self.profile_photo
                session.add(user)
                session.commit()
        
        self.is_editing = False
        return rx.toast.success("Profile updated successfully!")

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle profile photo upload."""
        for file in files:
            upload_data = await file.read()
            outfile = f"./uploaded_files/{file.filename}"
            
            # Save the file
            with open(outfile, "wb") as file_object:
                file_object.write(upload_data)
            
            # Set the profile photo path
            self.profile_photo = f"/uploaded_files/{file.filename}"
            self.upload_progress = 100

    def cancel_edit(self):
        """Cancel editing and reset form."""
        self.is_editing = False
        self.display_name = ""
        self.bio = ""
        self.location = ""
        self.website = ""
        self.upload_progress = 0

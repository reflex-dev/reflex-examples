# PySocial - Twitter Clone with Reflex

A fully functional Twitter clone built with Reflex, featuring user authentication, tweets, profiles, and social interactions.

## 🚀 Features

### Core Functionality
- **User Authentication**: Sign up, login, and logout
- **Tweet Management**: Create, edit, and delete tweets
- **User Profiles**: Customizable profiles with photos and information
- **Social Features**: Follow/unfollow users and view followers
- **Search**: Search for tweets and users
- **Like System**: Like and unlike tweets (database ready)

### Recent Updates & Enhancements

#### 1. Enhanced UI with Twitter Color Scheme
- **Twitter Blue** (#1DA1F2) for primary actions and branding
- **Dark Gray** (#14171A) for primary text
- **Light Gray** (#657786) for secondary text
- **Border Color** (#E1E8ED) matching Twitter's design
- Beautiful gradient backgrounds and modern shadows
- Smooth hover effects and transitions

#### 2. Tweet CRUD Operations
- ✅ **Create**: Post new tweets with a clean composer interface
- ✅ **Read**: View tweets in a feed with author information
- ✅ **Update**: Edit your own tweets inline with a pencil icon
- ✅ **Delete**: Remove your tweets with a trash icon
- Auto-clear tweet input after posting
- Only tweet authors can edit/delete their own tweets

#### 3. Profile Management System
- **Profile Photos**: Upload and display profile pictures
- **Editable Fields**:
  - Display Name (different from username)
  - Bio (tell us about yourself)
  - Location
  - Website
- **Profile Header**: Gradient cover photo with profile picture overlay
- **Edit Mode**: Toggle between view and edit modes
- **Default Avatar**: User icon for accounts without photos

#### 4. Like/Favorite System (Database Layer)
- `Like` table implemented for tracking tweet likes
- Composite primary key (tweet_id + username)
- Ready for frontend integration

## 📁 Project Structure

```
twitter/
├── db_model.py          # Database models (User, Tweet, Follows, Like)
├── state/
│   ├── base.py          # Base state with authentication
│   ├── home.py          # Home feed state with tweet CRUD
│   └── profile.py       # Profile editing state
├── components/
│   ├── profile.py       # Profile page components
│   └── tweet.py         # Tweet display components
├── pages/
│   └── home.py          # Home page with feed
├── layouts/
│   └── auth.py          # Authentication layout
└── __init__.py          # App initialization and routes
```

## 🗄️ Database Schema

### User Table
- `username`: Primary identifier
- `password`: Hashed password
- `profile_photo`: URL or path to profile image
- `bio`: User biography
- `display_name`: Display name (can differ from username)
- `location`: User location
- `website`: User website URL

### Tweet Table
- `id`: Auto-generated primary key
- `content`: Tweet text
- `created_at`: Timestamp
- `author`: Username of tweet creator

### Follows Table (Many-to-Many)
- `follower_username`: User who follows
- `followed_username`: User being followed

### Like Table (Many-to-Many)
- `tweet_id`: ID of liked tweet
- `username`: User who liked the tweet

## 🎨 UI/UX Features

### Authentication Page
- Gradient background (Twitter Blue to Dark)
- Clean white card with rounded corners
- Modern shadows and spacing
- Responsive design

### Home Feed
- Tweet composer with character count
- Real-time tweet feed
- Edit mode with inline editing
- Delete confirmation
- Twitter-style avatars and layouts

### Profile Page
- Cover photo with gradient
- Circular profile picture
- Editable profile information
- Drag-and-drop photo upload
- Save/Cancel actions with feedback

## 🛠️ Setup Instructions

1. **Install dependencies**:
   ```bash
   pip install reflex
   ```

2. **Create upload directory**:
   ```bash
   mkdir -p uploaded_files
   ```

3. **Initialize database**:
   ```bash
   reflex db makemigrations
   reflex db migrate
   ```

4. **Run the application**:
   ```bash
   reflex run
   ```

5. **Access the app**:
   - Open your browser to `http://localhost:3000`
   - Sign up for a new account
   - Start tweeting!

## 📝 Usage

### Posting Tweets
1. Type your message in the composer
2. Click "Tweet" button
3. Tweet appears in feed and input clears automatically

### Editing Tweets
1. Find your tweet in the feed
2. Click the pencil icon
3. Edit the content inline
4. Click "Save" or "Cancel"

### Deleting Tweets
1. Find your tweet in the feed
2. Click the trash icon
3. Tweet is removed immediately

### Editing Profile
1. Navigate to `/profile`
2. Click "Edit Profile" button
3. Upload a photo or update your information
4. Click "Save Changes"

## 🎯 Future Enhancements

- [ ] Implement like button UI and counter
- [ ] Add retweet functionality
- [ ] Implement direct messaging
- [ ] Add notifications system
- [ ] Media upload for tweets
- [ ] Hashtag support
- [ ] Trending topics
- [ ] User mentions (@username)
- [ ] Tweet replies/threads

## 🎨 Color Palette

- **Primary Blue**: `#1DA1F2` (Zima Blue)
- **Primary Blue Hover**: `#1A91DA`
- **Dark Text**: `#14171A`
- **Secondary Text**: `#657786`
- **Border**: `#E1E8ED`
- **Background**: `#F7F9FA`
- **White**: `#FFFFFF`
- **Error Red**: `#E0245E`

## 📋 Changelog - What Was Changed

### 🎨 UI Enhancements (`layouts/auth.py`)
**Before**: Basic auth layout with generic styling
**After**: Twitter-themed authentication page
- Added Zima Blue (#1DA1F2) color scheme throughout
- Implemented gradient background (Twitter Blue to Dark)
- Enhanced heading styles with proper colors and sizing
- Improved box shadows and border radius for modern look
- Added hover effects on links with color transitions
- Updated spacing and padding for better visual hierarchy

### 🗄️ Database Model Extensions (`db_model.py`)
**Added to User Model**:
```python
profile_photo: str = ""      # URL or path to profile photo
bio: str = ""                # User bio/description
display_name: str = ""       # Display name (different from username)
location: str = ""           # User location
website: str = ""            # User website
```

**New Like Table**:
```python
class Like(rx.Model, table=True):
    tweet_id: int = Field(primary_key=True)
    username: str = Field(primary_key=True)
```
- Enables like/favorite functionality
- Composite primary key prevents duplicate likes
- Ready for frontend integration

### ✏️ Tweet CRUD Operations (`state/home.py`)
**Modified `post_tweet()` method**:
- Added `self.tweet = ""` to clear input after posting
- Ensures clean UI experience after tweeting

**Added New Methods**:
```python
delete_tweet(tweet_id: int)              # Delete a tweet
start_edit_tweet(tweet_id, content)      # Enter edit mode
cancel_edit_tweet()                      # Cancel editing
save_edit_tweet(tweet_id)                # Save edited tweet
```

**Added State Variables**:
```python
editing_tweet_id: int = -1               # Track which tweet is being edited
edit_tweet_content: str = ""             # Store edit content
```

### 🏠 Home Page Improvements (`pages/home.py`)
**Updated `composer()` function**:
- Changed from `on_blur` to `on_change` with `value` binding
- Added `value=HomeState.tweet` for proper state binding
- Added `disabled=HomeState.tweet == ""` to prevent empty tweets
- Enhanced button styling with `color_scheme="blue"`

**Enhanced `tweet()` display function**:
- Added conditional rendering for edit/view modes
- **View Mode Features**:
  - Edit button (pencil icon) for tweet authors
  - Delete button (trash icon) for tweet authors
  - Buttons only visible to tweet owner
  - Icon buttons with hover effects
- **Edit Mode Features**:
  - Inline text area for editing
  - Save/Cancel action buttons
  - Color-coded buttons (blue for save, outline for cancel)

### 👤 Profile Management System (New Files)

**Created `state/profile.py`**:
- `ProfileState` class with profile management logic
- Form fields: display_name, bio, location, website, profile_photo
- UI state: is_editing, upload_progress
- Methods:
  - `load_profile_data()`: Load current user's profile
  - `toggle_edit_mode()`: Switch between view and edit
  - `update_profile()`: Save profile changes to database
  - `handle_upload()`: Process profile photo uploads
  - `cancel_edit()`: Discard changes

**Created `components/profile.py`**:
- `profile_header()`: Cover photo with gradient + profile picture
- `edit_profile_form()`: Complete profile editing interface
  - Profile photo upload with drag-and-drop
  - Display name input
  - Bio text area
  - Location input
  - Website input
  - Save/Cancel buttons
- `profile_info()`: Display profile information
  - Shows display name or username
  - Displays bio, location, website with icons
  - Edit Profile button
- `profile_page()`: Main profile page layout

**Updated `__init__.py`**:
- Added import for `profile_page`
- Added route: `app.add_page(profile_page, route="/profile", title="Profile")`

**Updated `components/__init__.py`**:
- Added export: `from .profile import profile_page`

### 🎨 Design System Applied
All components now follow Twitter's official design language:
- **Buttons**: Rounded (border-radius: 20px) with Twitter Blue
- **Inputs**: Light borders (#E1E8ED) with blue focus states
- **Cards**: White backgrounds with subtle shadows
- **Spacing**: Consistent padding and margins
- **Typography**: Bold headings in dark gray, secondary text in light gray
- **Icons**: Size-consistent with proper colors and hover states
- **Hover Effects**: Smooth transitions on interactive elements

### 📂 New Directory Structure
```
uploaded_files/          # Created for profile photo storage
```

### 🔄 Breaking Changes
None - All changes are backward compatible with existing data

### ⚠️ Migration Required
After pulling these changes, run:
```bash
reflex db makemigrations
reflex db migrate
```

This will add the new fields to User table and create the Like table.

## 🤝 Contributing

Feel free to fork this project and add your own features!

## 📄 License

This is a demo project for learning Reflex framework.

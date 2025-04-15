# LightUpLives - Crowdfunding Web App

## Overview
LightUpLives is a web-based crowdfunding platform that enables individuals and organizations to raise funds for projects, causes, and ventures in Egypt. The platform connects fundraisers with donors, providing a secure and user-friendly environment to support initiatives that make a difference.

## Features

### 1. Authentication System
- **User Registration:**
  - First name, Last name, Email, Password, Confirm Password
  - Mobile phone (validated for Egyptian numbers)
  - Profile Picture
  - Email activation (users must activate their accounts via email within 24 hours before they can log in)
- **Login System:**
  - Login via email and password (after activation)
  - Login via Facebook
- **Password Management:**
  - Forgot password functionality with email reset link
  - Password change within profile settings
- **User Profile:**
  - View profile, projects, and donations
  - Edit personal data (except email)
  - Add optional information (Birthdate, Facebook profile, Country)
  - Delete account with confirmation and password verification

### 2. Projects Management
- **Project Creation:**
  - Title, Details, Category (admin-defined), Multiple images
  - Funding goal (e.g., 250,000 EGP), Tags, Start/End time
- **User Interactions:**
  - View and donate to projects
  - Comment on projects with reply functionality
  - Report inappropriate projects or comments
  - Rate projects using a 5-star rating system
- **Project Page Features:**
  - Overall project rating
  - Image slider for project pictures
  - Related projects based on tags
  - Progress bar showing funding percentage
  - Comment section with nested replies
- **Project Control:**
  - Project creator can cancel the project if donations are below 25% of the target

### 3. Homepage
- **Project Showcases:**
  - Latest projects with horizontal scrolling
  - Featured projects (admin-selected)
  - Category-based project browsing
- **UI Features:**
  - Dark mode support
  - Responsive design for all device sizes
  - Interactive UI elements
- **Search Functionality:**
  - Search projects by title or tag

### 4. Admin Features
- **Content Moderation:**
  - Manage user-reported content
  - Approve or delete reported comments
  - Review and handle project reports
- **Featured Content:**
  - Select projects to be featured on the homepage
- **Category Management:**
  - Create and manage project categories

## Technologies Used
- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, Bootstrap 5, JavaScript
- **Database:** PostgreSQL
- **Authentication:** Django Authentication, OAuth (for Facebook login)
- **Email Service:** Django Email backend (for email verification and password resets)
- **UI Enhancements:** Font Awesome icons, Custom CSS animations
- **Form Handling:** Django Forms with client-side validation

## Installation
To set up the project locally:

1. Clone the repository:
   ```sh
   git clone git@github.com:Ahmed-Awwad99/LightUpLives.git
   ```
2. Navigate to the project directory:
   ```sh
   cd LightUpLives
   ```
3. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
4. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
5. Set up the environment variables (.env file) with necessary keys.
6. Apply database migrations:
   ```sh
   python manage.py migrate
   ```
7. Start the development server:
   ```sh
   python manage.py runserver
   ```

## Usage
- Users can register, activate their accounts, and log in
- Users can create, view, and donate to projects
- Users can interact via comments, replies, reports, and ratings
- Users can switch between light and dark modes
- Admins can manage categories, featured projects, and reported content

## Contribution
We welcome contributions! To contribute:
1. Fork the repository
2. Create a feature branch
3. Commit changes and push to your branch
4. Open a pull request

## Contributors
- [Ahmed Awwad](https://github.com/Ahmed-Awwad99)  
- [Istabrak Mohamed](https://github.com/istabrak001)  
- [Mohamed Sallam](https://github.com/mu-sallam)
- [Salma Elsallal](https://github.com/SALMASALLAL) 
- [Salma Tamer](https://github.com/salmaali15)   

## License
This project is open-source and licensed under the MIT License.

## Completed Features
- [x] Develop project creation and management functionality
- [x] Implement core authentication system
- [x] Set up donation transactions
- [x] Build project commenting and reporting system
- [x] Implement comment reply functionality
- [x] Create admin panel for managing categories and featured projects
- [x] Implement dark mode toggle
- [x] Add star rating system for projects
- [x] Implement account deletion functionality
- [ ] Add login with Facebook integration

---
© 2025 Light Up Lives. All rights reserved.
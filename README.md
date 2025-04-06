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
  - Bonus: Login via Facebook
- **Password Management:**
  - Bonus: Forgot password functionality with email reset link
- **User Profile:**
  - View profile, projects, and donations
  - Edit personal data (except email)
  - Add optional information (Birthdate, Facebook profile, Country)
  - Delete account with confirmation (Bonus: Require password for deletion)

### 2. Projects Management
- Users can create and manage fundraising campaigns with:
  - Title, Details, Category (admin-defined), Multiple images
  - Funding goal (e.g., 250,000 EGP), Tags, Start/End time
- Users can:
  - View and donate to projects
  - Comment on projects (Bonus: Comment replies)
  - Report inappropriate projects or comments
  - Rate projects
- Project page includes:
  - Overall project rating
  - Image slider for project pictures
  - Related projects based on tags
- Project creator can cancel the project if donations are below 25% of the target

### 3. Homepage
- Slider showcasing the top 5 highest-rated active projects
- List of latest 5 projects
- List of 5 featured projects (selected by admin)
- Category-based project browsing
- Search bar for searching projects by title or tag

## Technologies Used
- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, Bootstrap, JavaScript
- **Database:** PostgreSQL
- **Authentication:** Django Authentication, OAuth (for Facebook login)
- **Email Service:** Django Email backend (for email verification and password resets)

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
- Users can register, activate their accounts, and log in.
- Users can create, view, and donate to projects.
- Users can interact via comments, reports, and ratings.
- Admins can manage categories and featured projects.

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

## Roadmap
- [ ] Develop project creation and management functionality
- [ ] Implement core authentication system
- [ ] Set up donation transactions
- [ ] Build project commenting and reporting system
- [ ] Admin panel for managing categories and featured projects
- [ ] Implement bonus features like Facebook login and comment replies

---
### Notes
This README will be updated as we progress with the development of the project. Stay tuned!
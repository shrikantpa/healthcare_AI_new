# Aayura Frontend - Login & Signup System

## Overview
Complete frontend authentication system for the Aayura Malaria Outbreak Forecasting Platform with modern UI/UX design.

## Features

### 1. Login Screen
- Username and password input fields
- Error messages for invalid credentials
- Loading spinner during authentication
- Link to signup page
- Responsive design
- Enter key submission support

### 2. Signup Screen
- First name and last name fields
- Deputed state dropdown (pulled from backend API)
- Deputed location dropdown (district - filtered by state)
- Username field
- Password field with validation (min 6 characters)
- Confirm password field with real-time matching indicator
- Validation for all fields
- Success modal with redirect to login
- Error handling with specific messages

### 3. Dashboard
- User welcome message
- Profile information display
- Logout functionality
- Session management via localStorage

## File Structure

```
frontend/
├── index.html          # Login page
├── signup.html         # Signup page
├── dashboard.html      # User dashboard
├── styles.css          # Unified styling for all pages
└── auth.js             # Authentication logic and API calls
```

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **HTTP Requests**: Fetch API
- **Storage**: localStorage for session management
- **Styling**: CSS Grid, Flexbox, CSS Variables
- **Responsive**: Mobile-first design

## API Integration

### Backend Endpoints Used

1. **Login**
   - Endpoint: `POST /login`
   - Body: `{ username, password }`
   - Response: `{ user_id, username, role }`

2. **Signup**
   - Endpoint: `POST /signup`
   - Body: `{ first_name, last_name, username, password, district, state }`
   - Response: User details with created_at timestamp

3. **Get Locations**
   - Endpoint: `GET /locations`
   - Response: Array of `{ state, district }`

## Component Details

### Login Page (index.html)
- Company branding with "Aayura" header
- Clean, minimal form design
- Real-time error messaging
- Loading state management
- Redirect to signup for new users
- Auto-redirect to dashboard on success

### Signup Page (signup.html)
- Multi-step form layout
- Cascading dropdowns (State → District)
- Live password matching validation
- Form validation before submission
- Success modal on registration
- Link back to login

### Dashboard (dashboard.html)
- Personalized greeting
- User profile display
- Session management
- Logout functionality

### Styling (styles.css)
- CSS Variables for theming
- Mobile-responsive breakpoints
- Smooth animations and transitions
- Consistent button and form styling
- Modal and overlay components
- Loading spinner animation

### Authentication Logic (auth.js)
- Form initialization
- API communication
- Session management (localStorage)
- Input validation
- Error/success message handling
- Location data loading and filtering
- Dynamic dropdown population

## Validation Rules

### Login
- Username: Required, non-empty
- Password: Required, non-empty

### Signup
- First Name: Required, non-empty
- Last Name: Required, non-empty
- State: Must be selected from dropdown
- District: Must be selected from dropdown (filtered by state)
- Username: Required, unique, non-empty
- Password: Required, minimum 6 characters
- Confirm Password: Must match password exactly

## Error Handling

1. **Network Errors**: Display connection error message
2. **Invalid Credentials**: Show "Invalid credentials" on login
3. **Duplicate Username**: Show "Username already exists"
4. **Invalid Location**: Show "Location not found" message
5. **Validation Errors**: Real-time field validation messages

## Security Features

- Passwords sent to backend (backend handles hashing)
- Session stored in localStorage with username
- Form validation on client and server
- CORS enabled for localhost development
- Password confirmation field
- Location verification against backend

## Browser Compatibility

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile browsers: Fully responsive

## Responsive Design Breakpoints

- **Desktop**: 1200px and above
- **Tablet**: 768px to 1199px
- **Mobile**: Below 768px
- **Small Mobile**: Below 400px

## CSS Variables (Theming)

```css
--primary-color: #2c5f8d (Aayura Blue)
--secondary-color: #1abc9c (Teal)
--success-color: #27ae60 (Green)
--error-color: #e74c3c (Red)
--light-bg: #ecf0f1 (Light Gray)
--dark-text: #2c3e50 (Dark Gray)
```

## Form Features

### Real-time Validation
- Password matching indicator
- Username availability checking (via API)
- Field-level error messages
- Visual feedback on validation

### Accessibility
- Proper label associations
- Keyboard navigation support
- Enter key submission
- Clear error messages
- Focus indicators on form elements

## User Flow

### Login Flow
1. User navigates to index.html
2. Enters username and password
3. Clicks Login button (or presses Enter)
4. API validates credentials
5. On success: Redirect to dashboard.html
6. On error: Display error message

### Signup Flow
1. User clicks "Register here" link
2. Navigates to signup.html
3. Fills in personal details
4. Selects state from dropdown
5. Selects district from dropdown (filtered)
6. Enters username
7. Enters password twice with confirmation
8. Clicks Sign Up button
9. API validates location and creates user
10. On success: Shows success modal → Link to login
11. On error: Display specific error message

## Local Storage Schema

```javascript
// After successful login
localStorage.setItem('user', JSON.stringify({
    user_id: number,
    username: string,
    role: string,
    first_name: string,
    last_name: string,
    district: string,
    state: string,
    created_at: string
}));

localStorage.setItem('token', username);
```

## Running the Frontend

### With Backend Server

1. Start backend server:
   ```bash
   cd backend
   python main.py
   ```

2. Serve frontend (option 1 - Python):
   ```bash
   cd frontend
   python -m http.server 8001
   ```

3. Serve frontend (option 2 - Node):
   ```bash
   cd frontend
   npx http-server -p 8001
   ```

4. Open browser to `http://localhost:8001`

### Environment Configuration

The frontend is configured to connect to:
- Backend API: `http://localhost:8000`

To change the backend URL, edit `auth.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000'; // Change this line
```

## Features in Action

### Dropdown Cascading
1. User selects state from first dropdown
2. JavaScript filters locations by state
3. District dropdown auto-populates with matching districts
4. User selects district
5. Validation ensures both selections are made

### Password Validation
1. User types password in first field
2. User types in confirm password field
3. JavaScript compares both fields in real-time
4. Green checkmark shows if match
5. Red error if mismatch
6. Form prevents submission if no match

### Location Verification
1. Form attempts signup
2. Backend queries location table
3. If location found: User created in users table
4. If not found: Error message displayed
5. User cannot create account with invalid location

## Future Enhancements

- Two-factor authentication
- Profile edit page
- Password reset functionality
- Email verification
- Social login (Google, GitHub)
- Dark mode toggle
- Language selection
- Remember me functionality
- Session timeout handling
- User activity logging

## Notes

- All error messages are user-friendly and specific
- Loading states prevent duplicate submissions
- Forms auto-reset after successful submission
- Success modal provides clear call-to-action
- Mobile optimization tested on various screen sizes
- Animations enhance user experience without impact on performance

## Troubleshooting

### Backend Connection Issues
- Ensure backend is running on port 8000
- Check CORS is enabled
- Verify API_BASE_URL in auth.js

### Signup Dropdown Empty
- Backend /locations endpoint may not be responding
- Check browser console for errors
- Verify location table has data

### Passwords Don't Match
- Check keyboard layout
- Ensure Caps Lock is off
- Confirm both passwords are identical

### Session Lost After Refresh
- Check browser localStorage (F12 → Application tab)
- Verify user data was saved correctly
- Check for localStorage quota issues
